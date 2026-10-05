# Triple Balance refactoring versions

`original.twee` is the unchanged reference source. Each `tbN.twee` is a complete
story snapshot with `tbN` as its StoryTitle and a distinct IFID, so versions can
be imported into Twine as separate stories. Passage names, positions and explicit
links are preserved for comparison in the graphical editor.

## tb1 — shared CSS classes

Source: `original.twee` → [tb1.twee](tb1.twee).

Replaced 683 inline style attributes across 13 repeated patterns with shared
classes in `StoryStylesheet`. This includes attributes inside header/footer
configuration strings.

| Classes | Purpose |
| --- | --- |
| `text-center` | Center passage content and navigation blocks. |
| `no-wrap` | Keep indicator icons and values together. |
| `full-width` | Fill the available row width. |
| `tight-lines` | Preserve the ending summary's line spacing. |
| `indicator-row` | Shared two-column indicator layout. |
| `indicator-row-first` | Add the existing first-row top spacing. |
| `indicator-row-summary` | Use the ending summary's wider icon column and alignment. |
| `indicator-icon` | Shared 25px indicator icon sizing and positioning. |
| `indicator-icon-offset-3` | Preserve the existing 3px vertical offset where used. |
| `score-icon` | Shared 50px ending score icons. |
| `balance-illustration` | Shared 103px illustrations in the introduction. |
| `story-illustration` | Shared 150px illustrations with the existing left offset. |

The stylesheet scopes these classes to `#page`. Twenty-three inline style
attributes remain for more specialized layouts and images.

### Comparison in Twine

Import `original.twee` and `tb1.twee` as separate stories. The new story appears
as **tb1** and retains the same passage graph and layout. Compare the indicator
rows, introduction, ending summary, score icons and header/footer. Inspect
`StoryStylesheet` to see the shared rules, and individual passages to see the
shorter markup.

### Validation

- Reversing the class replacements, stylesheet additions, title and IFID changes
  reproduces `original.twee` exactly. Narrative text, gameplay instructions and
  the existing translation implementation are unchanged.
- All passage headings, graphical positions and explicit passage links match
  the reference source.
- Chrome computed-style comparisons matched across all 87 story passages and
  the header/footer, checking 670 rendered occurrences under a fixed sample
  game state. Other conditional branches are covered by the exact source
  comparison rather than exhaustive playthroughs.

This version changes presentation organization only; it does not correct
existing markup, wording or gameplay behavior.

## tb2 — passage-type tags

Source: `tb1.twee` → [tb2.twee](tb2.twee).

Added one type tag to each of the 87 story passages. StoryTitle is **tb2**,
with a distinct IFID for importing as a separate story in Twine.

| Tag | Passages | Count |
| --- | --- | --- |
| `intro` | `Start`, `Start2`–`Start6` | 6 |
| `explanation` | `explanation.economy`, `explanation.happy` | 2 |
| `round` | `Round1`–`Round6` | 6 |
| `policy` | The named policy results offered by the six rounds | 18 |
| `event` | `Event1.1`–`Event3.3` | 9 |
| `outcome` | The 18 numbered event results, such as `1.1Fire` | 18 |
| `ending` | `End1`–`End6`, `End.Credits`, `Game over`, `Game over2` | 9 |
| `technology` | `Tech`, `Tech1`–`Tech3`, the six `NewTech*` passages and nine named technology results | 19 |

For example:

```twee
:: Start2 [intro] {"position":"925,50","size":"100,100"}
```

`StoryScript` and `StoryStylesheet` keep their existing `script` and `stylesheet`
tags. `StoryTitle` and `StoryData` remain untagged metadata passages.

Import `tb2.twee` into Twine and inspect the tags on each passage. These tags
classify passages; tag-driven CSS layouts have not yet been implemented.

Validation: removing the new type tags and reversing the title/IFID changes
reproduces `tb1.twee` exactly. Passage names, positions, explicit links, content,
styles and gameplay logic are unchanged. `original.twee` and `tb1.twee` remain
untouched.

## tb3 — connect tags to layouts

Source: `tb2.twee` → [tb3.twee](tb3.twee). StoryTitle is **tb3**, with a new IFID.

`StoryScript` now listens for Chapbook's `body-content-change` event, reads the
displayed passage's tags, and applies its layout class to `#page article`.
Classes are replaced on each display, so a previous passage's layout cannot
carry over. The integration reads metadata only; it does not modify story state
or render passages again.

| Passage tag | Article class | Default alignment |
| --- | --- | --- |
| `intro` | `passage-intro` | Center |
| `explanation` | `passage-explanation` | Left |
| `round` | `passage-round` | Center |
| `policy` | `passage-policy` | Left, with centered title and navigation |
| `event` | `passage-event` | Center |
| `outcome` | `passage-outcome` | Left, with centered title and navigation |
| `ending` | `passage-ending` | Center |
| `technology` | `passage-technology` | Center |
| `prose` (additional tag) | `passage-prose` | Left; overrides the type default |

The `prose` tag is assigned to `Start2`, `Start4`, `End.Credits`, `End2`, `End4`,
`End5`, and `NewTech1a`–`NewTech3a`. It supports reading-heavy passages without
hard-coding their names in JavaScript. All indicator rows retain left alignment.
Header/footer styling is outside these passage layouts.

Nineteen complete centering wrappers were removed. Remaining title and
navigation blocks use `passage-title` and `passage-navigation` where possible.
Some wrappers remain, including `Tech`, where removal would change Markdown
punctuation processing. Structural indicator-row divs remain necessary for the
grid layout.

Round choices now use the shared centered layout. Reading-heavy variants retain
left-aligned prose and centered navigation. Layout classes use the `passage-`
prefix so tags such as `policy` and `event` do not accidentally apply the colored
inline highlight styles to the whole passage.

### Edit and compare in Twine

Import `tb3.twee`. Change a passage's type tag to choose its layout, or add
`prose` for left-aligned reading text. Edit the tag-driven layout section in
`StoryStylesheet` to change a type's defaults. Explicit passage links and map
positions are preserved.

### Validation

- Original source and earlier snapshots remain unchanged.
- Passage names, positions, explicit links and gameplay vars sections match tb2.
- Chrome checks cover layout assignment and alignment across all 87 passages,
  including prose overrides, indicator rows and navigation blocks.
- With deterministic random values and a fixed sample state, rendered text,
  links, images and gameplay values match tb2 for 86 passages. The introduction's
  asynchronous translation content is checked on initial loading separately.
- Clicking an actual round choice switches the layout to `passage-policy`.
