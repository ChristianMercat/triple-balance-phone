/**
 * This file must be copied manually into the Twine editor to load the Twine i18n integration.
 * Twine → Story → JavaScript
 */

/* ========================================
   Language configuration
   ======================================== */

setup.languages = [
  { code: "en", label: "English" },
  { code: "pl", label: "Polski" },
  // { code: "de", label: "Deutsch" },
  // { code: "fr", label: "Français" }
];

/* ========================================
   i18next initialization
   ======================================== */

const i18nLock = LoadScreen.lock();

importScripts(
  "https://cdn.jsdelivr.net/npm/i18next@25/dist/umd/i18next.min.js",
  "https://cdn.jsdelivr.net/npm/i18next-http-backend@4/i18nextHttpBackend.min.js",
)
  .then(function () {
    i18next.use(i18nextHttpBackend);

    return i18next.init({
      lng: "en",
      fallbackLng: "en",

      supportedLngs: setup.languages.map((language) => language.code),

      load: "languageOnly",

      backend: {
        loadPath: "i18n/{{lng}}.json",
      },
    });
  })
  .then(function () {
    console.log(
      "i18next initialized:",
      i18next.resolvedLanguage || i18next.language,
    );

    LoadScreen.unlock(i18nLock);
  })
  .catch(function (error) {
    console.error("Could not initialize i18next:", error);

    LoadScreen.unlock(i18nLock);
  });

/* ========================================
   <<t>>
   ======================================== */

Macro.add("t", {
  handler: function () {
    if (this.args.length === 0) {
      return this.error("translation key required");
    }

    const key = this.args[0];
    const options = this.args[1] || {};

    const translation = i18next.t(key, options);

    this.output.appendChild(document.createTextNode(translation));
  },
});

/* ========================================
   <<languageSelector>>
   ======================================== */

Macro.add("languageSelector", {
  handler: function () {
    const select = document.createElement("select");

    const currentLanguage = i18next.resolvedLanguage || i18next.language;

    setup.languages.forEach(function (language) {
      const option = document.createElement("option");

      option.value = language.code;

      option.textContent = language.label;

      option.selected = language.code === currentLanguage;

      select.appendChild(option);
    });

    select.addEventListener("change", function () {
      const previousLanguage = i18next.resolvedLanguage || i18next.language;

      i18next
        .changeLanguage(select.value)
        .then(function () {
          Engine.show();
        })
        .catch(function (error) {
          console.error("Could not change language:", error);

          select.value = previousLanguage;
        });
    });

    this.output.appendChild(select);
  },
});

/* ========================================
   <<tlink>>
   ======================================== */

Macro.add("tlink", {
  handler: function () {
    if (this.args.length < 2) {
      return this.error('usage: <<tlink "translationKey" [[Passage]]>>');
    }

    const key = this.args[0];
    const link = this.args[1];
    const passage = link.link;

    const element = document.createElement("a");

    element.href = "#";
    element.textContent = i18next.t(key);

    if (Story.has(passage)) {
      element.classList.add("link-internal");
    } else {
      element.classList.add("link-broken");
    }

    element.addEventListener("click", function (event) {
      event.preventDefault();

      if (Story.has(passage)) {
        Engine.play(passage);
      }
    });

    this.output.appendChild(element);
  },
});
