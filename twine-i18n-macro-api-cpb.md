# Twine / Chapbook i18n Insert API

This document describes the custom internationalization inserts provided by
`twine-i18n-chapbook.js`: `{translate text}`, `{language selector}` and
`{translated link}`.

## Overview

The integration uses:

- **Chapbook 2.3.1** (the version used by the template).
- **i18next 25** and **i18next-http-backend 4**, loaded from jsDelivr.
- One JSON translation file per language under `i18n/`.

```text
story/
├── i18n-test-cpb.html
└── i18n/
    ├── en.json
    └── pl.json
```

Translation files load from `i18n/{{lng}}.json`. English is the initial and
fallback language. Serve the template over HTTP so the browser can fetch JSON;
internet access is required for the CDN libraries.

Import `i18n-test-cpb.html` into Twine to edit the complete template. If importing
`i18n-test-cpb.twee` instead, select Chapbook 2.3.1 and copy
`twine-i18n-chapbook.js` into **Story → JavaScript**. See the
[template guide](twine-i18n-chapbook-api.md) for local preview and rebuilding.

## `{translate text}`

Translates a key using i18next.

### Syntax

```text
{translate text: "key"}
```

With interpolation or pluralization:

```text
{translate text: "inventory", name: playerName, count: apples}
```

Properties after the key are passed to i18next as options. Supply each option
as a named property, such as `name: playerName` or `count: apples`.

### Basic example

Translation file:

```json
{
  "hello": "Hello world!"
}
```

Passage:

```text
{translate text: "hello"}
```

Output:

```text
Hello world!
```

### Interpolation

Translation:

```json
{
  "greeting": "Hello, {{name}}!"
}
```

Passage:

```text
playerName: "Anna"
--
{translate text: "greeting", name: playerName}
```

Output:

```text
Hello, Anna!
```

### Pluralization

English:

```json
{
  "inventory_one": "{{name}}, you have {{count}} apple.",
  "inventory_other": "{{name}}, you have {{count}} apples."
}
```

Polish:

```json
{
  "inventory_one": "{{name}}, masz {{count}} jabłko.",
  "inventory_few": "{{name}}, masz {{count}} jabłka.",
  "inventory_many": "{{name}}, masz {{count}} jabłek.",
  "inventory_other": "{{name}}, masz {{count}} jabłka."
}
```

Passage:

```text
playerName: "Anna"
apples: 22
--
{translate text: "inventory", name: playerName, count: apples}
```

i18next selects a plural category using the numeric `count` property. English
displays `Anna, you have 22 apples.`; Polish displays `Anna, masz 22 jabłka.`

### Text rendering and fallback

Translations and interpolated values are assigned through `textContent`.
HTML, Markdown and Chapbook instructions inside translations are displayed as
plain text rather than executed. Apply formatting in the passage:

```text
# {translate text: "greeting", name: playerName}
```

Missing keys fall back to English. A key missing in both languages displays
the key itself. Before initialization finishes, inserts also display their keys.

Dotted keys are literal keys because the Chapbook integration configures
`keySeparator: false`:

```json
{
  "dialog.warning": "Please choose carefully."
}
```

Use `{translate text: "dialog.warning"}` with this flat JSON structure.

Interpolation values are captured when the insert renders. Changing language
retranslates using those captured values; it does not reevaluate story variables.

## `{language selector}`

Displays a labeled dropdown containing the supported languages.

### Syntax

```text
{language selector}
```

### Language switching

Selecting a language:

1. Disables the selectors while resources load.
2. Initializes an i18next candidate for the chosen language, reusing downloaded
   translation resources.
3. Makes that candidate active only after loading succeeds.
4. Updates all connected translation elements and language selectors, including
   those in the header and footer.
5. Updates the document's `lang` attribute.

Language changes update translated text in place, preserving scores, random
outcomes and passage history. Vars sections and passage JavaScript are not
executed again. Language selection is kept outside Chapbook story state and
resets to English on page reload.

If initialization fails, the selector offers **Retry**. If a language download
fails, the previous language remains active and the player can attempt selection
again. Loading/error messages and the `Language` / `Retry` labels are currently
English.

### Configuring languages

Edit the `languages` array at the top of `twine-i18n-chapbook.js`:

```javascript
const languages = [
  { code: "en", label: "English" },
  { code: "pl", label: "Polski" },
  { code: "de", label: "Deutsch" },
];
```

Labels are endonyms and are not translated. Supply `i18n/de.json` when adding
German, including all keys needed by the story or allowing English fallback.

### Header and footer

The selector and translation inserts can also be used in Chapbook configuration:

```text
playerName: "Anna"
config.header.center: '{translate text: "greeting", name: playerName}'
config.footer.center: '{language selector}'
--
{translate text: "greeting", name: playerName}
```

## `{translated link}`

Creates a translated link to an existing passage.

### Syntax

```text
{translated link: "translationKey", to: '[[Passage]]'}
```

Recommended form:

```text
{translated link: "translationKey", to: '[[editor-label|Passage]]'}
```

**Use single quotes around the `to` argument.** Chapbook converts standard
`[[...]]` links to HTML before evaluating custom insert arguments. The generated
HTML contains double quotes, so double quotes around this argument would break
its expression.

The standard link notation preserves discoverable passage connections for the
Twine story map. Its label is for editing; the runtime label comes from i18next.
These destination forms are supported:

```text
{translated link: "next", to: '[[Second]]'}
{translated link: "next", to: '[[next|Second]]'}
{translated link: "next", to: '[[next->Second]]'}
{translated link: "next", to: '[[Second<-next]]'}
```

A bare destination such as `to: "Second"` is not accepted by this implementation.

### Example

English translation:

```json
{
  "next": "Continue"
}
```

Polish translation:

```json
{
  "next": "Dalej"
}
```

Passage:

```text
{translated link: "next", to: '[[next|Second]]'}
```

The player sees `Continue` in English or `Dalej` in Polish. Both links lead to
the passage named `Second`.

Additional properties are passed to i18next for the label:

```text
{translated link: "greeting", to: '[[greet|Second]]', name: playerName}
```

### Navigation behavior

The insert renders Chapbook's native `passage-link` element, with keyboard
activation and normal passage navigation. Clicking it adds the destination to
Chapbook's passage trail. A missing destination produces an insert error.

## Translation file example

`i18n/en.json`:

```json
{
  "greeting": "Hello, {{name}}!",
  "inventory_one": "{{name}}, you have {{count}} apple.",
  "inventory_other": "{{name}}, you have {{count}} apples.",
  "next": "Continue",
  "back": "Go back"
}
```

`i18n/pl.json`:

```json
{
  "greeting": "Cześć, {{name}}!",
  "inventory_one": "{{name}}, masz {{count}} jabłko.",
  "inventory_few": "{{name}}, masz {{count}} jabłka.",
  "inventory_many": "{{name}}, masz {{count}} jabłek.",
  "inventory_other": "{{name}}, masz {{count}} jabłka.",
  "next": "Dalej",
  "back": "Wróć"
}
```

These are illustrative translation values; the existing demo files have their
own labels.

## Complete passage example

With the integration installed in Story JavaScript and an existing `Second`
passage:

```text
playerName: "Anna"
apples: 22
--
# {translate text: "greeting", name: playerName}

{translate text: "inventory", name: playerName, count: apples}

{translated link: "next", to: '[[next|Second]]'}

---

{language selector}
```

The `--` separates the Chapbook vars section from passage content. The `---`
inside the content is a Markdown horizontal rule.

## Conventions

- Keep story logic and passage names language-independent.
- Use stable semantic translation keys such as `inventory`, `next` and
  `dialog.warning` in flat JSON dictionaries.
- Use one passage per story location rather than separate language passages.
- Use numeric `count` values for pluralization.
- Pass interpolation options as named insert properties.
- Keep language labels as endonyms.
- Use single-quoted standard links in `{translated link}` for passage-map
  connections.
- Keep translations as plain text; put formatting and executable logic in the
  story.
- Keep gameplay effects tied to gameplay actions, rather than language changes.

## Browser diagnostics

`window.ChapbookI18n.ready` settles after the initial loading attempt, including
an unsuccessful attempt; it is not a success flag.
`window.ChapbookI18n.changeLanguage("pl")` runs the same language switch as the
selector. Calls made while loading or before successful initialization are ignored;
an unsupported language code rejects the returned promise.
