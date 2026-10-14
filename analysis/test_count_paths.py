"""Small independent fixtures for branching, failure rules and aggregation."""
import tempfile
import unittest
import csv
from collections import Counter
from pathlib import Path

from count_paths import ModelError, Story, analyze, expression, export_paths

SCORE_SCRIPT = """:: StoryScript [script]
engine.state.setLookup('score', get =>
    2.5 * (get('circle') ?? 0) + 1.5 * (get('happy') ?? 0) + (get('money') ?? 0)
  );
"""


def fixture(root, body):
    source = Path(root)/'fixture.twee'
    source.write_text(':: StoryData\n{"start":"Start"}\n'+body+'\n'+SCORE_SCRIPT+
                      '\n:: End1\nDone\n:: Game over\nLost\n:: Game over2\nLost\n')
    return source


class CountingTests(unittest.TestCase):
    def test_distinct_choices_merge_without_losing_multiplicity(self):
        body = ''':: Start
circle: 0
happy: 5
money: 5
tech: 0
--
[[A]] [[B]]
:: A
circle: circle + 1
--
[[Roll]]
:: B
circle: circle + 1
--
[[Roll]]
:: Roll
randomEvent: Math.floor(Math.random() * 4) + 1
--
[if randomEvent == 1]
[[End1]]
[if randomEvent > 1]
[[End1]]
'''
        with tempfile.TemporaryDirectory() as root:
            story = Story(fixture(root, body)); terminal, _, _ = analyze(story)
            self.assertEqual(sum(terminal.values()), 8)
            self.assertEqual(len(terminal), 1)
            self.assertEqual(story.score((1,5,5,0,0)), 15)
            output = Path(root)/'paths.csv'
            export_paths(story,output)
            with output.open() as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows),8)
            self.assertEqual({r['score'] for r in rows},{'15'})

    def test_override_priority_clamp_and_hidden_rolls(self):
        body = ''':: Start
circle: 1
happy: 1
money: 1
tech: 0
--
[[Lose]]
:: Lose
circle: Math.max(0, circle - 2)
happy: happy - 1
money: money - 1
randomEvent: Math.floor(Math.random() * 4) + 1
--
[if randomEvent == 1]
{translated link: "common.continue", to: '[[End1]]', role: "continue"}
[if randomEvent > 1]
{translated link: "common.continue", to: '[[End1]]', role: "continue"}
[continue]
{game over override}
'''
        with tempfile.TemporaryDirectory() as root:
            path = fixture(root,body)
            for hidden, expected in ((False,1),(True,4)):
                terminal, _, _ = analyze(Story(path,hidden))
                self.assertEqual(terminal,Counter({('happiness_game_over',0,0,0,0):expected}))

    def test_budget_override_and_continue_resets_false_condition(self):
        body = ''':: Start
circle: 0
happy: 2
money: 0
tech: 0
--
[if happy < 0]
[[MissingButInvisible]]
[continue]
{translated link: "common.continue", to: '[[End1]]', role: "continue"}
{game over override}
'''
        # The static graph intentionally also validates hidden destinations.
        body = body.replace('MissingButInvisible','End1')
        with tempfile.TemporaryDirectory() as root:
            terminal, _, _ = analyze(Story(fixture(root,body)))
            self.assertEqual(terminal,Counter({('budget_game_over',0,2,0,0):1}))

    def test_cycles_are_rejected(self):
        body = ':: Start\n[[Loop]]\n:: Loop\n[[Loop]]\n'
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaisesRegex(ModelError,'cycle'):
                analyze(Story(fixture(root,body)))

    def test_unsupported_gameplay_expression_is_rejected(self):
        with self.assertRaises(ModelError):
            expression('Math.random()', {'money':5})


if __name__ == '__main__':
    unittest.main()
