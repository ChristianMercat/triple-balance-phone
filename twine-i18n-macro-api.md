# Twine / SugarCube i18n Macro API

This document describes the custom internationalization macros provided by the project's SugarCube Story JavaScript.

## Overview

The integration uses:

- **SugarCube 2**
- **i18next**
- **i18next-http-backend**
- One JSON translation file per language, stored under `i18n/`

Example project structure:

```text
story/
├── index.html
└── i18n/
    ├── en.json
    └── pl.json
```

Translation files are loaded with:

```text
i18n/{{lng}}.json
```

For example:

```text
i18n/en.json
i18n/pl.json
```

---

## `<<t>>`

Translates a key using i18next.

### Syntax

```twine
<<t "key">>
```

With interpolation/pluralization options:

```twine
<<t "key" `OPTIONS_OBJECT`>>
```

> **Important:** when passing an object expression directly to the macro, wrap it in SugarCube backticks so that it is evaluated as a single argument.

### Basic example

Translation file:

```json
{
  "hello": "Hello world!"
}
```

Passage:

```twine
<<t "hello">>
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

```twine
<<set $playerName = "Anna">>

<<t "greeting" `{ name: $playerName }`>>
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

```twine
<<set $playerName = "Anna">>
<<set $apples = 22>>

<<t "inventory" `{ name: $playerName, count: $apples }`>>
```

i18next treats `count` specially and selects the correct plural category for the active language.

Possible English output:

```text
Anna, you have 22 apples.
```

Possible Polish output:

```text
Anna, masz 22 jabłka.
```

### Using a temporary options object

For larger parameter sets, a temporary SugarCube variable may be easier to read:

```twine
<<set _params = {
    name: $playerName,
    count: $apples
}>>

<<t "inventory" _params>>
```

---

## `<<languageSelector>>`

Displays a dropdown menu containing the supported languages.

### Syntax

```twine
<<languageSelector>>
```

Example result:

```text
English ▼
Polski
```

Selecting a language:

1. calls `i18next.changeLanguage(...)`;
2. loads the corresponding `i18n/<language>.json` file when needed;
3. rerenders the current SugarCube passage.

The rerender does **not** create a new story-history entry.

### Configuring languages

Languages are configured in Story JavaScript:

```javascript
setup.languages = [
    { code: "en", label: "English" },
    { code: "pl", label: "Polski" }
];
```

Labels are intentionally written as **endonyms** and are not translated.

To add German:

```javascript
setup.languages = [
    { code: "en", label: "English" },
    { code: "pl", label: "Polski" },
    { code: "de", label: "Deutsch" }
];
```

Then add:

```text
i18n/de.json
```

---

## `<<tlink>>`

Creates a translated link to another passage.

### Syntax

```twine
<<tlink "translationKey" [[Passage]]>>
```

Recommended form:

```twine
<<tlink "translationKey" [[editor-label|Passage]]>>
```

The `[[...]]` syntax is important because it allows the **Twine editor to detect the passage connection and draw an arrow in the story map**.

The visible link text at runtime comes from i18next, not from the label inside `[[...]]`.

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

```twine
<<tlink "next" [[next|Second]]>>
```

In English the player sees:

```text
Continue
```

In Polish:

```text
Dalej
```

The destination in both cases is the passage named:

```text
Second
```

Twine also sees the standard link:

```twine
[[next|Second]]
```

and can therefore display the connection in the passage map.

### Navigation behavior

`<<tlink>>` uses SugarCube passage navigation and creates a normal new history moment, so Back/Undo-style story navigation continues to work.

---

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

---

## Complete passage example

```twine
<<set $playerName = "Anna">>
<<set $apples = 22>>

# <<t "greeting" `{ name: $playerName }`>>

<<t "inventory" `{ name: $playerName, count: $apples }`>>

<<tlink "next" [[next|Second]]>

---

<<languageSelector>>
```

---

## Conventions

Recommended project conventions:

- Keep story logic and passage names language-independent.
- Use stable semantic translation keys such as `inventory`, `next`, and `dialog.warning`.
- Do not create separate passages such as `Start_en` and `Start_pl`.
- Use `count` for values that should trigger i18next pluralization.
- Use backticks around inline object expressions passed to `<<t>>`.
- Keep language-selector labels as endonyms: `English`, `Polski`, `Deutsch`, etc.
- Use standard `[[...]]` link syntax inside `<<tlink>>` so Twine can display passage-map connections.
- Keep translation files as plain JSON; do not put SugarCube macros or executable HTML into translated strings.
