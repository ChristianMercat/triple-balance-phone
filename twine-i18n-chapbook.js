/* Copy into Twine → Story → JavaScript (Chapbook 2.3.1 or later). */
engine.extend("2.3.1", () => {
  const languages = [
    { code: "en", label: "English" },
    { code: "pl", label: "Polski" },
  ];
  const texts = new Set();
  const selectors = new Set();
  let translator;
  let ready = false;
  let busy = true;
  let errorMessage = "";
  let initialization;

  function escapeAttribute(value) {
    return String(value).replace(/[&<>"']/g, character => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
    })[character]);
  }

  function refresh() {
    texts.forEach(element => element.update());
    selectors.forEach(element => element.update());
    if (ready) document.documentElement.lang = translator.resolvedLanguage || translator.language;
  }

  function loadScript(url, globalName) {
    if (window[globalName]) return Promise.resolve();
    return new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = url;
      script.onload = () => window[globalName]
        ? resolve()
        : reject(new Error(`Missing library: ${globalName}`));
      script.onerror = () => {
        script.remove();
        reject(new Error(`Could not load ${url}`));
      };
      document.head.appendChild(script);
    });
  }

  function initialize() {
    if (initialization) return initialization;
    busy = true;
    errorMessage = "";
    refresh();
    initialization = (async () => {
      try {
        await loadScript("https://cdn.jsdelivr.net/npm/i18next@25/dist/umd/i18next.min.js", "i18next");
        await loadScript("https://cdn.jsdelivr.net/npm/i18next-http-backend@4/i18nextHttpBackend.min.js", "i18nextHttpBackend");
        translator = await createTranslator("en");
        ready = true;
      } catch (error) {
        errorMessage = "Could not load translations. Check your connection and retry.";
        console.error("Chapbook i18n initialization failed:", error);
      } finally {
        busy = false;
        refresh();
      }
    })();
    return initialization;
  }

  async function createTranslator(language, resources) {
    const instance = window.i18next.createInstance();
    instance.use(window.i18nextHttpBackend);
    await new Promise((resolve, reject) => instance.init({
      lng: language,
      fallbackLng: "en",
      supportedLngs: languages.map(item => item.code),
      load: "languageOnly",
      keySeparator: false,
      // Reuse downloaded JSON, but isolate a failed attempt from the active instance.
      resources: resources ? JSON.parse(JSON.stringify(resources)) : undefined,
      partialBundledLanguages: true,
      interpolation: { escapeValue: false }, // Output is assigned via textContent.
      backend: { loadPath: "i18n/{{lng}}.json" },
    }, error => error ? reject(error) : resolve()));
    return instance;
  }

  async function changeLanguage(code) {
    if (!ready || busy) return;
    if (!languages.some(language => language.code === code)) {
      throw new Error(`Unsupported language: ${code}`);
    }
    busy = true;
    errorMessage = "";
    refresh();
    try {
      // Commit only after loading succeeds. A fresh candidate also permits retrying
      // downloads that i18next's backend has previously marked as failed.
      translator = await createTranslator(code, translator.store.data);
    } catch (error) {
      errorMessage = "Could not load this language. Your previous language is still active.";
      console.error("Chapbook language change failed:", error);
    } finally {
      busy = false;
      // Update only text nodes and controls. Never rerender a passage or change state.
      refresh();
    }
  }

  class TranslatedText extends HTMLElement {
    connectedCallback() {
      texts.add(this);
      this.update();
    }
    disconnectedCallback() { texts.delete(this); }
    update() {
      const key = this.getAttribute("key");
      const options = JSON.parse(this.getAttribute("options") || "{}");
      this.textContent = ready ? translator.t(key, options) : key;
    }
  }

  class LanguageSelector extends HTMLElement {
    connectedCallback() {
      if (!this.select) {
        const label = document.createElement("label");
        label.appendChild(document.createTextNode("Language "));
        this.select = document.createElement("select");
        languages.forEach(language => {
          const option = document.createElement("option");
          option.value = language.code;
          option.textContent = language.label;
          this.select.appendChild(option);
        });
        this.select.addEventListener("change", () => changeLanguage(this.select.value));
        label.appendChild(this.select);
        this.status = document.createElement("span");
        this.status.setAttribute("role", "status");
        this.retry = document.createElement("button");
        this.retry.type = "button";
        this.retry.textContent = "Retry";
        this.retry.addEventListener("click", () => {
          initialization = undefined;
          initialize();
        });
        this.append(label, this.status, this.retry);
      }
      selectors.add(this);
      this.update();
    }
    disconnectedCallback() { selectors.delete(this); }
    update() {
      this.select.disabled = busy || !ready;
      this.select.value = ready ? translator.resolvedLanguage || translator.language : "en";
      this.status.textContent = busy ? " Loading…" : errorMessage ? ` ${errorMessage}` : "";
      this.retry.hidden = ready || busy || !errorMessage;
    }
  }

  customElements.define("chapbook-translated-text", TranslatedText);
  customElements.define("chapbook-language-selector", LanguageSelector);

  function translatedText(key, options) {
    if (typeof key !== "string" || !key) throw new Error("Translation key required");
    return `<chapbook-translated-text key="${escapeAttribute(key)}" options="${escapeAttribute(JSON.stringify(options))}"></chapbook-translated-text>`;
  }

  engine.template.inserts.add({
    match: /^translate\s+text$/i,
    render: (key, options) => translatedText(key, options),
  });
  engine.template.inserts.add({
    match: /^language\s+selector$/i,
    render: () => "<chapbook-language-selector></chapbook-language-selector>",
  });
  engine.template.inserts.add({
    match: /^translated\s+link$/i,
    render(key, { to, ...options }) {
      // Standard link notation inside a quoted argument keeps Twine map arrows.
      // Chapbook expands [[links]] before evaluating custom insert arguments.
      // Single quotes around the argument preserve the generated double-quoted HTML.
      const template = document.createElement("template");
      template.innerHTML = typeof to === "string" ? to : "";
      const link = template.content.firstElementChild;
      if (link?.tagName !== "PASSAGE-LINK" || template.content.childNodes.length !== 1) {
        throw new Error("Use to: '[[editor-label|Passage]]'");
      }
      const passage = link.getAttribute("to");
      if (!engine.story.passageNamed(passage)) throw new Error(`Unknown passage: ${passage}`);
      return `<passage-link class="link" to="${escapeAttribute(passage)}">${translatedText(key, options)}</passage-link>`;
    },
  });

  // Useful for diagnostics; language is deliberately kept outside story state.
  window.ChapbookI18n = { languages, changeLanguage, ready: initialize() };
});
