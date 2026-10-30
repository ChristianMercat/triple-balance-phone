# How many ways can you play Triple Balance?

One playthrough is one journey from the start to an ending. Change a decision,
get a different random event, or choose another response, and you follow a
different path—even if you finish with the same score.

At each policy round, you choose **one of three policies**. At an event slot,
either nothing happens or one of three events occurs. Each event offers two
responses. That gives **1 + 3 × 2 = 7 possible routes** through an event slot.
For example, a policy choice followed by an event slot gives **3 × 7 = 21**
combinations, provided Game Over does not interrupt them.

Research adds more branches. At the start, you pay for zero, one, two or three
technologies. Each technology you paid for later gives you three choices:

| Technologies paid for | Possible technology-choice sequences |
| ---: | ---: |
| 0 | 1: no technology choices |
| 1 | 3 |
| 2 | 3 × 3 = 9 |
| 3 | 3 × 3 × 3 = 27 |

Across all four investment options, that is **1 + 3 + 9 + 27 = 40** sequences.
With six policy rounds and three event slots, we could write down
**3⁶ × 7³ × 40 = 10,001,880 full plans** if we ignored Game Over.

But the game stops when happiness or money falls to zero or below. Choices after that
point do not count: many full plans share the same early ending. A computer
follows every branch and stops counting that path at its ending:

| Ending | Number of playthroughs |
| --- | ---: |
| Finish all six rounds | 3,597,500 |
| Game Over | 456,680 |
| **Total** | **4,054,180** |

That is over four million different journeys! These are **possible paths, not
probabilities**: the numbers do not tell us how often real players will win.
We do not count restarts or visits to explanation and credits pages as additional branches.

[Explore the decision diagram](decision_tree_proposal.svg).
