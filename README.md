# Triple Balance - the phone edition

An interactive text-based adventure created with Twine. It explores the dilemma of creating a circular smartphone economy, while at the same time keeping phone users happy and not exhausting a given budget.

[Play online](https://imaginary.github.io/math4sustainability-R-strategies-dilemmas/)

## Development

Main file is `tripleBalance.twee`. You can use the Twine graphical editor to inspect, modify, or and export it as `index.html` for testing and deployment. You can also use a text editor or IDE for development.

Edit `tripleBalance.twee` directly and record changes in [change-log.md](change-log.md).
Git tracks future revisions; historical `tbN.twee` snapshots are kept in `archive/`.

You will need a local server for testing locally (for instance `python3 -m http.server`).

This game uses a custom internationalization setup (see `twine-i18n-macro-api-cpb.md`).

To count gameplay paths and regenerate final-score statistics, run
`python3 analysis/count_paths.py`. See [analysis/README.md](analysis/README.md)
for the counting rules, histogram outputs and optional individual path export.

## Translations

The main game's translation files are in `i18n/`. Use `i18n/en.json` as the
source; `examples/i18n/` contains separate dictionaries for the demonstration.

### Add a language

1. Copy `i18n/en.json` to a file named after the language code, such as
   `i18n/fr.json`, `i18n/es.json` or `i18n/it.json`. Translate the string values,
   keeping all key names and nested sections unchanged. Keep interpolation
   placeholders such as `{{score}}`, `{{round}}` and `{{total}}` exactly as written.
   Use valid JSON: double-quoted strings, escaped inner quotes and no trailing
   commas or backticks. For inline emphasis, retain only the supported `<b>`,
   `<strong>` and `<span class="policy">`, `<span class="tech">` or
   `<span class="event">` markup. Keep passage names and link destinations in
   the story unchanged.

2. In `tripleBalance.twee`, find the `StoryScript` passage and the `const languages`
   array in the Chapbook i18next integration. Add an entry for each new language,
   using its own name as the selector label:

   ```javascript
   const languages = [
     { code: "en", label: "English" },
     { code: "de", label: "Deutsch" },
     { code: "fr", label: "Français" },
     { code: "es", label: "Español" },
     { code: "it", label: "Italiano" },
   ];
   ```

   Add only languages for which you have created dictionaries. If editing in
   Twine, make this change in **Story → JavaScript**. This array controls both
   the selector and i18next's supported languages; no other JavaScript changes
   are needed for these language codes. The loader automatically requests
   `i18n/<code>.json`, and English remains the fallback for missing entries.
   The current loader uses base language codes (`load: "languageOnly"`).

   The main game's JavaScript is embedded in `tripleBalance.twee` and its HTML
   export. The standalone `twine-i18n-chapbook.js` serves the demonstration;
   changing that file does not enable a language in the main game.

3. Publish the updated story from Twine as `index.html`, and keep the editable
   `tripleBalance.twee` source in sync with changes made in Twine. Include the new
   dictionary when sharing or deploying the project. Adding JSON alone does not
   update the language selector in an existing HTML export.

4. From the project root, run `python3 -m http.server 8000` and open
   `http://localhost:8000/`. Select the new language and check passage text,
   navigation, resource descriptions, headers, footers and ending messages.
   Check that longer text fits and placeholders display their values. Switching
   languages should preserve resources, score and the current random event.
   The browser remembers the selected language between reloads. Internet access
   is required to load the i18next libraries from the CDN.

See the [Chapbook insert API](twine-i18n-macro-api-cpb.md) for translation syntax
and rich-text rules. The graph's labels are currently embedded in an image and
need separate localization; adding a dictionary does not translate them.

## Credits

© 2026 Imaginary gGmbH

Gameplay and implementation by Bianca Violet, illustrations by Ariel Kahtan.

This work is part of the Erasmus+ project Math4Sustainability and co-funded by the European Union. Views and opinions expressed are however those of the author(s) only and do not necessarily reflect those of the European Union or the European Education and Culture Executive Agency (EACEA). Neither the European Union nor EACEA can be held responsible for them. Project number 2024-1-DE03-KA220-SCH-000246047.

## License

This work is licensed under the Creative Commons Attribution-ShareAlike 4.0 International License.
