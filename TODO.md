# Pending tasks

Baseline: `tripleBalance.twee` and its English dictionary, following tb24. This list
consolidates unimplemented follow-ups from `change-log.md` and the project reviews.
Balance changes and repository cleanup proposals still require decisions;
listing them here does not implement them.

## Score presentation

- [ ] Remove or correct the misleading “of 50” wording in the endings. The
      current reachable maximum is **53** (circularity 16, happiness 8, budget 1).
- [ ] Display the numeric score in every End3 assessment, including the top band.
- [ ] Revise the above-50 assessment so it does not imply that every score above
      50 is the maximum. Preserve the current formula and explicit, mutually
      exclusive score ranges unless a gameplay change is agreed.
- [ ] Explain that the score weights are a simplified model for this game,
      rather than an objective measure of good policy.

## Playthrough statistics and graph

- [ ] Agree on the definition of a playthrough before replacing the current
      End6 count of **3,824,020**. The previous model enumeration counted distinct
      decision/event sequences, stopped at Game Over and excluded restarts:
      **3,597,500 successful routes** and **4,054,180 terminal routes**, including
      failures. Revalidate these figures against the current story.
- [ ] Generate the displayed count and score distribution graph from the same
      gameplay model. Recalculate the counts, score bounds and graph after balancing.
- [ ] Distinguish route counts from probabilities: different routes need not
      be equally likely.
- [ ] Localize the graph labels “score” and “Number of playthroughs”, currently
      embedded in `images/graph.webp`. Decide between localized image variants and
      a generated graph with translated labels.

## Gameplay and balance

- [ ] Review equal-cost technologies that currently offer strictly better
      resource effects than alternatives. Give them distinct strengths or
      situational advantages if meaningful trade-offs are the design goal:
      Triple-Diamond Glass over Magnetic Break-Apart and Low-Orbit Signal Mesh;
      Regenerative Port Matrix over Smart Bins and Self-Destruct; Modular Smartphone
      over Smart-Shattering.
- [ ] Review the battery technology's budget benefit: it arrives at the end,
      limiting its strategic usefulness.
- [ ] Review dominated policies with identical subsequent routes: Mobile Detox
      Day over Return Deposit; School Repair Café over One-Phone Law; Sustainable
      Devices Act over Don't Phone and Drive; Closed-Loop Law over Limit Online
      Footprint.
- [ ] Review dominated event responses: promoting minimalism over encouraging
      spending, and circular recession support over purchase support at equal cost.
      Decide whether these deliberately teach consequences or should offer
      competing benefits.
- [ ] Clarify what “policies stay in effect” means: currently their resource
      changes remain in the totals, with no recurring effects or influence on later
      events. Treat recurring effects or policy/event interactions as a separate
      gameplay design decision.

## Accessibility and presentation

- [ ] Add localized accessible names for resource indicators and trend
      directions; their icons currently have empty alternative text.
- [ ] Review illustrations individually: meaningful images need alternative
      text, while decorative images should be marked accordingly. Provide an
      accessible description or equivalent data for the score graph.
- [ ] Use semantic headings for passage titles, preserving the existing CSS.
- [ ] Check the score graph on narrow screens, especially its fixed height and
      aspect ratio. Check shared header/footer wrapping with longer translations.
- [ ] Review cyan/yellow/magenta category highlighting for readability and
      contrast, retaining explicit category labels.
- [ ] Replace the visible “Language” label with a translation icon. Retain a
      localized accessible name and normal keyboard operation.

## Translation

- [x] Generate a complete German dictionary mirroring English: all 312 entries
      are translated, with matching nested keys, placeholders and inline markup.
- [ ] Have a German-speaking collaborator review wording and terminology.
- [ ] Review the complete German story in context, including interpolation,
      inline emphasis, navigation labels and layout with longer text.
- [ ] Review passage naming when translation work makes it useful. Event names
      have already been made descriptive; renaming other passages remains deferred.
- [ ] Review the seven English keys unused by tb24: `greeting`, `inventory_one`,
      `inventory_other`, `next`, `second`, `start.intro` and `start.title`. Check older
      stories and demo dependencies before removing them or separating demo data.
      Language endonyms, emergency bootstrap UI messages and developer diagnostics
      are intentional literals, rather than missing passage translations.

## Maintainability and validation

- [x] Add reusable gameplay path and score analysis in `analysis/`, with grouped
      results, optional individual path export and a final-score histogram.
- [ ] Turn link/asset validation and dictionary-key checks into reusable project
      tools so collaborators can verify edits.
- [ ] Document how to build or export the current story reproducibly; the
      existing Python builder builds only the isolated Chapbook demonstration.
- [ ] Keep resource assignments, native score conditions and graph-readable
      destination links in passages so beginner writers can understand and edit them.

## Repository cleanup for collaborators

- [ ] Agree on the active source/export names and archive layout. Preserve
      `original.twee` and the sequential Twee versions for comparison.
- [ ] Remove the unreferenced assets `images/government.png`, `images/tech1.png`,
      `images/tech2.png`, `images/tech3.png` and `images/very-bad.png`.
- [ ] Group the Chapbook demonstration, its JavaScript, builder, documentation
      and Polish dictionary together; update paths if they move.
- [ ] Deliberately update the published `index.html`: it still contains the
      original story and also supplies the engine shell for the demo builder.
      Update that dependency before removing or relocating it.
- [ ] Update README instructions for the active story, graphical Twine editing,
      local HTTP preview, build/export workflow, dictionary organization and German
      translation status. Check documentation links after cleanup.

Already completed tasks, including the derived `score` lookup, alternate ending
route fix, native score conditions, random-event formula, translation-independent
Game Over navigation and migration of ordinary player-facing English text, are
not pending and should not be redone.
