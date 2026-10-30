# Review of the original decision diagram

The two pages of [decision_tree.pdf](decision_tree.pdf) show the correct sequence:
six policy rounds, event slots after policy rounds 1, 3 and 4, and technology
slots after policy rounds 2, 5 and 6. Each policy round has three options; an
event slot has one no-event route plus three events with two responses each.

The diagram needs three clarifications:

- **Technology slots depend on the initial investment.** Pay for one technology
  and you get a choice at the first slot only; pay for two and you get the first
  two slots; pay for three and you get all three. An eligible slot offers three
  technologies. “No technology” is an automatic skip for an unpaid slot, not a
  fourth option once you have paid. The numbered markers on page 1 suggest this
  dependency, but do not explain it; page 2 omits those markers.
- **Game Over cuts branches short.** If happiness or money falls to zero or below, the
  path ends before the next decision or event response. Ignoring this produces
  10,001,880 theoretical full plans, not the actual number of playthroughs.
- **It is a compressed schedule, not an unfolded tree.** A full tree would
  repeat the following stages separately after every branch. Rejoining lines
  saves space, but must not imply that earlier choices or resource differences
  have been forgotten.

The [SVG proposal](decision_tree_proposal.svg) keeps a compressed schedule, adds
explicit investment conditions and Game Over branches, and illustrates the
repeated branching patterns separately. A complete tree with millions of endings
would be impractical to read. Solid arrows show continuation; dashed red arrows
show possible early termination. Branches that rejoin in the drawing remain
separate paths when counting.

The figures use the main [Python analysis](../../analysis/README.md), not
`analysis2/`: 3,597,500 successful paths and 456,680 early endings, totalling
4,054,180. Different visible random outcomes count separately; a draw hidden by
an immediate Game Over does not create an extra visible path. No arbitrary
probabilities are assigned to player choices. The saved analysis source hash
was checked against the current `tripleBalance.twee`.

The original PDF is unchanged. For the shorter student-facing explanation, see
[How many ways can you play Triple Balance?](gameplay_paths.md).
