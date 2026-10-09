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

## tb4 — reusable effect rows

Source: `tb3.twee` → [tb4.twee](tb4.twee). StoryTitle is **tb4**, with a new IFID.

Replaced all 102 policy, technology and event-outcome effect rows with the
`effect row` insert from `tribalance3.twee`. Only that insert and its supporting
icon maps, HTML escaping and metric-image helper were copied. Other components
from the reference were not added. The extension targets Chapbook 2.3.1.

### Insert syntax

```text
{effect row: "circularity", trend: "down", text: "less ability to recycle old smartphones and materials", first: true}

{effect row: "budget", trend: "down", text: "the operation was paid from the city budget"}
```

| Argument/property | Values and behavior |
| --- | --- |
| First argument | `circularity`, `happiness` or `budget` selects the metric icon. |
| `trend` | `up`, `down` or `unchanged` selects the direction icon. |
| `text` | Plain-text explanation; HTML characters are escaped. |
| `first` | Optional boolean; `true` adds the existing 12px first-row top margin. |

The insert is a presentation component: it does not change indicator values.
Gameplay effects remain in each passage's vars section. Unsupported metrics
or trends produce an insert error.

The component emits `effect-row`, `effect-icons` and `effect-text` markup.
Its CSS shares the existing indicator grid rules, retains left-aligned
descriptions within tag-driven layouts, and uses the reference's consistent
25px icons with a 5px vertical offset. This replaces the previous mix of 3px and
5px offsets within effect rows and removes repeated spacer entities and trailing
line-break markup.

The three introductory status rows and three ending summary rows still use
their existing markup. They display current values and are separate from this
effect component. Source length decreased from 3,329 to 2,370 lines.

### Validation

- Original source, tb1–tb3 and `tribalance3.twee` remain unchanged.
- Passage headings, tags, positions, vars sections, conditions and explicit
  links match tb3.
- Chrome checks passed for all 87 passage layouts and actual round-to-policy
  navigation. Rendered text, icon sources, passage links and gameplay values
  match tb3 across 86 passages under deterministic sample conditions; the
  introduction's asynchronous translations are checked on initial loading.
- Story JavaScript passes the syntax check.

## tb5 — balanced markup and CSS title typography

Source: `tb4.twee` → [tb5.twee](tb5.twee). StoryTitle is **tb5**, with a new IFID.

- Corrected the mismatched div/span closing tags in `End1` and
  `NewTech1`–`NewTech3`.
- Removed the redundant, unclosed outer centering div in `RECYCLE BONUS`.
- Replaced the malformed right-alignment wrappers in `End3` with one balanced
  `score-details-link` block. Its font size and alignment are defined in CSS.
- Standardized the nine technology-result titles on `passage-title`.
- Replaced 57 title `<b>` elements with class-based title typography, and four
  ending-label `<b>` elements with `game-over-label` spans. Event and ending
  titles retain inline placement where they sit beside illustrations or labels.
- Moved the header title's font size and bolding from inline styling into the
  `header-title` CSS class.
- Renamed the score assessment wrapper to `ending-assessment`, separating its
  role from navigation styling.
- Reduced runs of excessive blank lines in passage content, preserving the
  vars sections. Existing prose emphasis remains unchanged.
- Removed 58 redundant trailing or navigation-spacer `<br>` tags in a follow-up
  edit to this same snapshot. Breaks that separate content within a paragraph,
  such as the event label/title and header title/subtitle, remain. A source
  comparison confirms this edit changes only break tags and whitespace.

### Validation

- All 87 story passages have balanced div/span markup.
- Chrome comparisons confirmed preserved rendered text, links, icon sources
  and gameplay values across 86 passages under deterministic sample conditions;
  the introduction's translations were checked on initial loading separately.
- CSS checks confirmed bold title and ending-label styling without nested
  `<b>` elements. Passage layouts and actual round-to-policy navigation passed.
- Passage metadata, explicit links, conditions, gameplay vars and all 102
  effect-row inserts are unchanged. The only vars-section markup change is the
  header title's CSS class.
- `original.twee` and tb1–tb4 remain untouched.

## tb6 — reusable status and summary rows

Source: `tb5.twee` → [tb6.twee](tb6.twee). StoryTitle is **tb6**, with a new IFID.
The existing tag colors and all other story metadata are preserved.

The three introductory rows in `Start4` now use `status row`:

```text
{status row: "circularity", value: 0, text: "The circularity index is zero, so your current economy is not circular at all. It cannot get worse.", first: true}
```

The ending rows in `End2` use paired summary inserts. The existing conditions,
explanations and Markdown emphasis remain directly in that passage:

```text
{summary row: "circularity", value: circle, first: true}
[if circle < 4]
Your choices did not really improve the **circularity** of the economy.
[continue]
…remaining conditions and explanations…
{end summary row}
```

Each `summary row` must have a matching `end summary row`. The opening insert
creates the metric/value column and opens the explanation column; the closing
insert closes both. Keep conditional modifiers inside the explanation area,
and reset them with `[continue]` before closing the row.

Both components share the `effect row` metric-icon helper. Supported metrics
are `circularity`, `happiness` and `budget`. `value` is displayed as escaped
text; `first: true` adds the existing first-row spacing. `status row` also
accepts a plain-text `text` explanation. Neither component changes game state.

Status rows reuse the effect-row grid. Summary rows retain their 80px metric
column, centered vertical alignment and existing line spacing. Icons use the
shared 25px sizing and 5px offset already used by effect rows.

### Validation

- Browser comparison passes for all passage layouts and preserves rendered
  text, links, icons and gameplay values relative to tb5.
- Twenty-one summary threshold scenarios preserve conditional explanations
  and Markdown emphasis; each renders three complete summary grids.
- All conditions and explicit passage links remain unchanged.
- Story JavaScript passes its syntax check. Earlier snapshots and the existing
  translation implementation remain untouched.

## tb7 — optional Game Over navigation override

Source: `tb6.twee` → [tb7.twee](tb7.twee). StoryTitle is **tb7**, with a new IFID.

Follow-up cleanup in this same snapshot removed 37 redundant `[continue]`
statements: 27 in unconditional navigation blocks and 10 immediately before
another `[if]`. Resets remain before override markers following conditional
routes and before summary-row closing inserts. Navigation, override and summary
threshold checks passed again after this cleanup.

Normal routes remain standard Twine links. An optional insert requests an
end-condition override after Chapbook displays the passage:

```text
<div class="passage-navigation">
[[Continue->Round4]]

{game over override}
</div>
```

For conditional routes, place the marker after a `[continue]` reset so it renders
regardless of which branch is selected:

```text
<div class="passage-navigation">
[if randomEvent == 1]
[[Continue->Event1.1]]

[if randomEvent == 2]
[[Continue->Event1.2]]

[if randomEvent == 3]
[[Continue->Event1.3]]

[if randomEvent > 3]
[[Continue->Round2]]

[continue]
{game over override}
</div>
```

The hidden marker is handled on `body-content-change`. It changes the `to`
attribute of rendered links labeled **Continue** inside the marker's enclosing
`passage-navigation` block:

1. `happy <= 0` routes to `Game over`.
2. Otherwise, `money <= 0` routes to `Game over2`.
3. Otherwise, the normal destination is retained.

Restart, Credits, links outside that navigation block, and header/footer links
are unaffected. The handler retains each link's original destination for repeat
invocations. It reads state without changing scores, randomness or history;
clicking the resulting link uses native Chapbook navigation.

Added markers to 48 passages: 18 event outcomes, 18 policy results, nine
technology results and three research investments. Removed explicit Game Over
links and their repeated conditions. Normal branch conditions now depend only
on event selection or research availability, allowing a Continue link to render
before the override applies.

All normal route arrows remain discoverable in Twine. Game Over destinations
exist only in the shared handler and are intentionally hidden from the graph.

### Deliberate behavior changes

Depletion checks now consistently include negative values. This replaces the
previous zero-only budget checks and the zero-only happiness checks in three
policies. Technology results also check budget, and research investments use
the shared override. Happiness failure takes precedence when both indicators
are depleted.

### Validation

- Browser comparisons preserve normal-state text, links, icons and gameplay
  values across the story, including the summary threshold checks.
- 2,304 override scenarios cover all 48 marked passages, both research branches,
  four event values, normal/zero/negative indicators, simultaneous depletion,
  link scope, repeat invocation and unchanged state.
- Actual Continue clicks reach both Game Over passages.
- Earlier files, passage names/tags/positions, gameplay vars, all normal route
  links, unrelated passages and translation code remain unchanged.
- Story JavaScript passes its syntax check.

## tb8 — Shared headers and footers controlled by UI modes

Created `tb8.twee` from `tb7.twee`, with StoryTitle `tb8` and a new IFID.
Preserved passage names, tags, graph positions, body content and gameplay logic.
Previous story versions and `original.twee` remain unchanged.

### Mode defaults

| Passage tag | Default `ui.mode` | Footer |
| --- | --- | --- |
| `intro`, `explanation` | `intro` | Skip explanations |
| `round` | `round` | Indicators and round number |
| `policy`, `event`, `outcome`, `technology` | `gameplay` | Indicators |
| `ending` | `results` | Restart and Credits |

`game-over` is an explicit mode for the two Game Over passages, with Restart
and Credits and no indicators. Gameplay and round modes also show Restart in
the header. Every mode shares the story identity and language selector.
The `prose` tag continues to control body styling independently of UI modes.

Removed repeated `config.header.*` and `config.footer.*` assignments from
passages. The shared renderer replaces all six slots after Chapbook renders
each passage, so controls and indicators cannot leak from earlier passages.
It does not change gameplay state or trigger another passage render.

### Passage settings

Settings live in the passage's vars section, before `--`. Each setting must be
a JSON literal: use double quotes for strings, numbers for rounds, and
`true`/`false` for switches. The renderer reads the current passage's settings
fresh; it does not use inherited `ui.*` state from earlier passages.

```text
ui.mode: "gameplay"
ui.status: true
ui.skip: false
ui.headerRight: "[[Restart|Start]]"
ui.footerCenter: "[[Credits->End.Credits]]"
--
Passage content here.
```

Supported overrides:

- `ui.mode`: `intro`, `gameplay`, `round`, `results`, or `game-over`.
- `ui.round`: number from 1 to 6; required for round mode.
- `ui.status`: show or hide the three indicators.
- `ui.skip`: show or hide Skip explanations; it occupies the right footer slot.
- `ui.headerRight`: replace the right header controls.
- `ui.footerLeft`, `ui.footerCenter`, `ui.footerRight`: replace a footer slot.
  These explicit slot overrides take precedence over mode defaults.

Control strings support ordinary Twine links and Chapbook inserts. An empty
string clears a slot. Shared CSS controls identity, indicator and control
spacing without inline styles or nonbreaking-space padding.

### Story exceptions

Start4 shows the introductory indicator preview without Skip explanations.
Start5 and Start6 use gameplay mode. Round1–Round6 declare their round numbers.
End1–End3 retain their indicator displays and individual control choices.
The credits and score passages retain their explicit controls and score label.
Other results and Game Over pages have no inherited indicators; this removes
the accidental circularity display in End4 and End5.

Translation implementation remains deferred. Existing translation code and
header/skip translation hooks are preserved.

### Validation

- 99 browser transitions cover all 87 passages, mode defaults and overrides,
  cross-mode resets, round numbers, indicators, ending controls, score label,
  language selector and shared styling.
- Browser regression comparisons check passage layouts, content, links, icons,
  gameplay values, actual navigation and 21 summary threshold scenarios.
- Story JavaScript passes its syntax check; prior story files are hash-verified
  unchanged.

## tb9 — Passage illustration and layout cleanup

Created `tb9.twee` from the current `tb8.twee`, with StoryTitle `tb9` and a new
IFID. Original and previous story files remain unchanged.

### Presentation changes

- Replaced every remaining passage-body inline style with shared CSS classes:
  welcome/research/policy illustrations, score chart, explanation icons and
  links, Game Over icons, and the credits funding notice.
- Kept existing image heights and relative offsets. Illustration variants use
  the shared `story-illustration` class with an explicit modifier.
- Replaced nonbreaking-space padding in Start3 and Start5 with wrapping image
  and choice groups, using CSS gaps.
- Removed five redundant `text-center` wrappers from End1, NewTech1–NewTech3
  and Tech, plus the unused CSS rule. Their passage tags already center content;
  none of these wrappers contained conditional modifiers. Navigation and
  conditional wrappers remain intact.
- Escaped the apostrophe in Tech's `people&#39;s` to retain its displayed wording
  when removing the wrapper enables Chapbook's smart punctuation processing.
- Omitted the credits notice's invalid unitless `padding:0.1` declaration, which
  browsers already ignored.

### Shared UI rendering correction

The current tb8 snapshot's `display-change` listener could run after Chapbook
had consumed the header/footer payload, leaving default controls on screen.
In tb9, the shared UI renderer listens for `body-content-change` and commits
all six slots in a microtask after Chapbook finishes updating them. This also
handles passage transitions without changing config variables or game state.
The modes, tag defaults and per-passage override settings are unchanged.

### Validation

Browser comparisons cover all 87 passage layouts and preserve displayed body
text, links, image sources and computed sizes/offsets, gameplay values, actual
navigation and 21 summary threshold scenarios. Start's existing translation is
checked on initial load. Prior story hashes, passage headers (including graph
positions), vars, conditional modifiers, link expressions and translation code
are unchanged. JavaScript passes its syntax check. No inline styles remain in
the story source.
The shared UI additionally passes 99 browser transitions covering all 87
passages, mode defaults/overrides, resets, round numbers, indicators, ending
controls, score labels and the language selector.

## Follow-up — Score initialization on alternate ending routes

Before refactoring ending conditions/scoring, remind the user to fix this:
End4 and End6 can be reached through End.Credits without visiting End3.
The `final` variable is calculated only in End3, so it can be undefined in
End4 and End6 on that route. Ensure the score is available regardless of the
entry route. Recorded for later; no gameplay fix applied yet.

## tb10 — Derived score and native assessment flow

Created `tb10.twee` from the latest `tb9.twee`, preserving its corrected
LIMIT ONLINE FOOTPRINT name/link and updated passage positions. StoryTitle is
`tb10`, with a new IFID. Earlier versions and the original remain untouched.

### Score calculation

Renamed the derived variable from `final` to `score` throughout tb10.

The formula lives once in StoryScript, registered as the native Chapbook
`engine.state.setLookup('score', ...)` lookup:

```javascript
2.5 * (get('circle') ?? 0) + 1.5 * (get('happy') ?? 0) + (get('money') ?? 0)
```

A lookup calculates on every read, so `score`, `{score}` and expressions using
it always see the current resources. It requires no dependency-update listener
or stored score copy. Missing resources before initialization contribute zero.
Removed the End3 vars assignment. End4 and End6 now work through Credits without
visiting End3, and restarting or restoring resources cannot expose a stale
stored score. This resolves the score-initialization follow-up recorded above.

### End3 assessment

No custom flow-control extensions were added. Chapbook 2.3.1's native `[if]`
modifiers start independent text blocks; a new `[if]` replaces the previous
condition rather than nesting inside it. `[continue]` starts an unmodified
block. A div does not close a modifier.

End3 uses explicit, mutually exclusive native `[if]` ranges, so writers can
edit the score boundaries directly beside each assessment. No intermediate
classification variable or custom `else if` modifier is needed. For example:

```text
[if score > 32.5 && score <= 50]
```

A `[continue]` explicitly ends assessment formatting before the separate
restart-link condition.

| Condition | Assessment |
| --- | --- |
| `score > 50` | High score |
| `score > 32.5 && score <= 50` | Outstanding |
| `score > 28.5 && score <= 32.5` | Good |
| `score > 22.5 && score <= 28.5` | Average |
| `score > 14.5 && score <= 22.5` | Poor |
| `score > 2 && score <= 14.5` | Barely survived |
| `score <= 2` | No assessment, preserving existing behavior |

The resource formula produces half-unit scores, and all old assessment choices
on that grid remain unchanged. Score wording, gameplay effects, random events,
normal links, translations and primary resources were not changed.

### Validation

- Browser comparison of 141 scores from -10 through 60, in steps of 0.5,
  preserves End3 text, icons and links.
- Score reads update immediately after each resource changes; restored stale
  score data cannot override the formula. Restart and the Credits → End4 →
  End5 → End6 route display the correct score.
- Browser passage/gameplay comparisons and summary scenarios check the rest
  of the story, using a consistent reference score for the old implementation.
- Story JavaScript passes its syntax check; prior story hashes and all passage
  headings, tags, positions and normal link expressions are unchanged.

## tb11 — Simplified random-event selection

Created `tb11.twee` from the latest `tb10.twee`, with StoryTitle `tb11` and a
new IFID. Replaced all nine randomEvent assignments with:

```text
randomEvent: Math.floor(Math.random() * 4) + 1
```

The browser supplies the pseudorandom stream. Each affected passage draws once
in its vars section and stores the result, so all conditions inspect the same
roll. Outcomes 1–3 select their existing events; outcome 4 keeps the existing
no-event route. No custom random helper, seed setting or Date.now adjustment
was added. Repeated individual outcomes are valid and remain possible.

### Validation

- 108 browser comparisons against tb10 cover all nine passages, all four rolls,
  and normal/low-happiness/low-budget states. Displayed text, destinations,
  primary resources and score match for each controlled roll.
- With the browser's unmodified Math.random, 100,000 draws produced counts
  24,920 / 24,737 / 24,948 / 25,395 for outcomes 1 / 2 / 3 / 4. Every draw was an
  integer in range; the sample was consistent with an approximately uniform
  distribution.
- Twelve Start restarts, each followed by visits to all nine rolling passages,
  produced twelve distinct nine-roll sequences. Eight page reloads produced
  eight distinct twenty-roll sequences. These checks show that tested runs did
  not repeat an identical sequence; they do not establish true randomness or
  prohibit chance repetitions.
- Only the nine formulas, StoryTitle and IFID changed from tb10. Earlier story
  files are hash-verified unchanged; passage tags/positions, gameplay effects,
  scoring, translations and link expressions remain intact. Story JavaScript
  passes its syntax check.

## tb12 — Small copy corrections and unused CSS cleanup

Created `tb12.twee` from `tb11.twee`, with StoryTitle `tb12` and a new IFID.
Original and earlier story versions remain untouched.

### Changes

- Corrected `avarage` to `average` in the End3 assessment.
- Corrected `ecnomy` to `economy` in the two explanation links.
- Closed the missing outer parenthesis in Round6's digital minimalism description.
- Changed the two Game Over footer labels from `End.Credits` to `Credits`,
  keeping `End.Credits` as the destination.
- Removed unused selector entries for `no-wrap`, `full-width`, `tight-lines`,
  `indicator-row`, `indicator-row-summary` and `indicator-row-first`.
  Shared rules and their declarations remain for the active classes.

### Validation

Verified that the removed class names are absent from passage markup and
StoryScript. CSS declarations and active selectors are unchanged. Passage
names, tags, graph positions, scripts, resource effects, score logic, random
selection and link destinations are unchanged. Previous story hashes are
unchanged. Translation integration has not started.

## Deferred improvements from the tb11 assessment

These proposals are recorded for later; they were not implemented in tb12.
Translation is the next planned iteration.

### Score presentation and playthrough statistics

- Display the numeric score in every End3 assessment, including the top band.
  Remove `of 50`: the current reachable maximum is 53 (circularity 16,
  happiness 8, budget 1). Rename the above-50 assessment so it does not imply
  every score above 50 is the maximum. Keep the current formula and explicit
  mutually exclusive ranges unless a deliberate design change is agreed.
- Define what counts as a playthrough. Current model enumeration yields
  3,597,500 successful routes and 4,054,180 terminal routes including failures,
  counting distinct decision/event sequences, stopping at Game Over and
  excluding restarts. The current End6 value, 3,824,020, does not match this
  definition.
- Generate the displayed count and score graph from the same gameplay model.
  Distinguish route counts from probabilities: routes need not be equally
  likely. Recalculate after balancing, since balance changes may alter survival
  and maximum scores.

### Technology, policy and event balance

- Give equal-cost technologies distinct strengths or situational advantages.
  Triple-Diamond Glass dominates Magnetic Break-Apart and Low-Orbit Signal
  Mesh; Regenerative Port Matrix dominates Smart Bins and Self-Destruct;
  Modular Smartphone dominates Smart-Shattering. The battery offers a budget
  benefit, but only at the end of the game, limiting its strategic usefulness.
- Review dominated policies with identical subsequent routes: Mobile Detox Day
  over Return Deposit; School Repair Café over One-Phone Law; Sustainable
  Devices Act over Don't Phone and Drive; Closed-Loop Law over Limit Online
  Footprint.
- Review dominated event responses: promoting minimalism over encouraging
  spending, and circular recession support over purchase support at equal cost.
  Decide whether these choices deliberately teach consequences or should offer
  competing benefits.
- Clarify that policies staying in effect currently means their resource changes
  remain in the totals. They do not create recurring effects or change later
  events; implementing such interactions would be a separate gameplay change.

### Presentation, accessibility and content

- Add accessible names for indicator values and trend directions. Decide which
  illustrations are decorative and which need meaningful alternative text.
  Use semantic headings for passage titles.
- Check the fixed-height score graph and shared header/footer layout on narrow
  screens, including aspect ratio and wrapping.
- Review the cyan/yellow/magenta category highlighting while retaining explicit
  category labels.
- Explain that the score weights are the game's simplified model, rather than
  an objective measure of good policy.

### Maintainability and translation-related cleanup

- Replace the Game Over handler's dependence on the visible English label
  `Continue` with an explicit navigation role before translating those labels.
- Retire the abandoned translation loader and its repeated timers during the
  separate migration to the new Chapbook internationalization mechanism.
- Make link/asset validation and gameplay enumeration reusable project tools,
  so future edits can verify routes, score bounds and statistics.
- Keep resource assignments, native score conditions and normal destination
  links in the passages: they remain readable for beginner writers and useful
  in the graphical Twine editor.
