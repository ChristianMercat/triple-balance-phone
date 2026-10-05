# Chapbook i18n template

`i18n-test-cpb.html` is the runnable, Twine-importable Chapbook 2.3.1 template.
It ports the i18next integration from `i18n-test.html`; the original story and
SugarCube template are untouched. Both demos use the existing `i18n/en.json`
and `i18n/pl.json` files.

## Run and edit

Serve this folder over HTTP (opening the HTML as `file://` prevents reliable
JSON loading):

```sh
python3 -m http.server 8000
```

Open `http://localhost:8000/i18n-test-cpb.html`. Alternatively, import the HTML
into Twine to edit its passages and Story JavaScript. Publish the result beside
the `i18n/` directory. The libraries load from jsDelivr, so internet access is
required.

The editable sources are `i18n-test-cpb.twee` (passages) and
`twine-i18n-chapbook.js` (Story JavaScript). Rebuild the HTML with:

```sh
python3 build-i18n-test-cpb.py
```

The builder reuses only the Chapbook 2.3.1 engine shell already in `index.html`;
it replaces all story content, identity and Story JavaScript. It never writes
to `index.html` or `original.twee`. When importing the Twee passages directly,
also copy `twine-i18n-chapbook.js` into Story JavaScript and select Chapbook 2.3.1.

## Inserts

Chapbook custom inserts need multiword names. The SugarCube equivalents are:

| SugarCube | Chapbook |
| --- | --- |
| `<<t "key">>` | `{translate text: "key"}` |
| `<<t "inventory" ...>>` | `{translate text: "inventory", name: playerName, count: apples}` |
| `<<tlink "next" [[next\|Second]]>>` | `{translated link: "next", to: '[[next\|Second]]'}` |
| `<<languageSelector>>` | `{language selector}` |

### Translated text

```text
playerName: "Anna"
apples: 22
--
# {translate text: "greeting", name: playerName}

{translate text: "inventory", name: playerName, count: apples}
```

Properties are passed directly to i18next, including its special `count`
property. The existing English `inventory_one` / `inventory_other` and Polish
`inventory_one` / `inventory_few` / `inventory_many` / `inventory_other` keys
provide pluralization. Dotted keys such as `header.title` are literal JSON keys
(`keySeparator: false`).

Translations and interpolated values render as plain text. HTML, Markdown and
Chapbook instructions inside a translation are not executed. Put formatting
around the insert in the passage instead. Missing keys fall back to English;
keys absent from both languages display their key name.

### Translated links

```text
{translated link: "next", to: '[[editor label|Second]]'}
```

**Use single quotes around the standard link argument.** Chapbook expands
`[[...]]` links into HTML before evaluating insert arguments, and the generated
HTML uses double quotes. The destination comes from this standard link, so
Twine can discover the passage connection; the visible label comes from
i18next. `[[Second]]`, `[[label->Second]]`, and `[[Second<-label]]` also work.
The destination must exist. Navigation uses Chapbook's native `passage-link`
element, including keyboard support and normal passage history.

Additional properties support interpolation in link labels:

```text
{translated link: "greeting", to: '[[greet|Second]]', name: playerName}
```

### Language selector

```text
{language selector}
```

Configure the language list at the top of `twine-i18n-chapbook.js`, using
endonyms for labels, and supply `i18n/<code>.json` for each language. The default
and fallback language are English, as in the SugarCube template. Selection is
not persisted between page reloads.

The selector works in passages, headers and footers. All visible translation
elements and selectors update together, and the document's `lang` attribute
updates for assistive technology. Controls are disabled during loading to
prevent overlapping requests. Failed initialization offers Retry; a failed
language download retains the previous language and allows another attempt.
The selector's loading/error messages and the demo's diagnostic text are English.

## Game-state behavior

Language changes update text elements **without rerendering passages**. They do
not change Chapbook state or history, reapply vars sections, rerun JavaScript,
or reroll random events. Interpolation values are captured when an insert is
rendered; switching language preserves those values. A subsequent passage
render captures its current values again.

`Second` deducts one budget point and selects a random event on entry. Switch
languages there to verify that both diagnostic values remain unchanged.

For browser diagnostics, `window.ChapbookI18n.ready` is a promise that settles
after initialization has been attempted, and
`window.ChapbookI18n.changeLanguage("pl")` invokes the same switch as the selector.

The integration uses Chapbook's documented [custom insert API](https://klembot.github.io/chapbook/guide/en/advanced/adding-custom-inserts.html)
and native custom elements; it does not rely on timeout-based translation scans.
