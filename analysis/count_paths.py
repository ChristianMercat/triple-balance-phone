#!/usr/bin/env python3
"""Count Triple Balance gameplay paths from its Chapbook Twee source.

Standard library only. This is a restricted interpreter for the constructs used
by this story, not a general Chapbook or JavaScript interpreter. Unsupported
reachable assignments/modifiers fail rather than silently changing the model.
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import re
from collections import Counter, deque
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VARIABLES = ("circle", "happy", "money", "tech", "randomEvent")
TERMINALS = {"End1": "success", "Game over": "happiness_game_over",
             "Game over2": "budget_game_over"}
EXCLUDED = {"explanation.economy", "explanation.happy", "End.Credits"}
RANDOM = "Math.floor(Math.random() * 4) + 1"


class ModelError(ValueError):
    pass


def expression(text: str, state: dict[str, int]) -> int | float | bool:
    """Evaluate a small, explicit subset without eval or executing story code."""
    text = text.replace("Math.max", "max").replace("Math.min", "min")
    text = text.replace("&&", " and ").replace("||", " or ")
    tree = ast.parse(text, mode="eval")

    def visit(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float, bool):
            return node.value
        if isinstance(node, ast.Name) and node.id in state:
            return state[node.id]
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
            value = visit(node.operand)
            return -value if isinstance(node.op, ast.USub) else value
        if isinstance(node, ast.BinOp):
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Add): return left + right
            if isinstance(node.op, ast.Sub): return left - right
            if isinstance(node.op, ast.Mult): return left * right
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in ("max", "min") and not node.keywords:
                return {"max": max, "min": min}[node.func.id]([visit(a) for a in node.args])
        if isinstance(node, ast.BoolOp):
            values = [bool(visit(v)) for v in node.values]
            if isinstance(node.op, ast.And): return all(values)
            if isinstance(node.op, ast.Or): return any(values)
        if isinstance(node, ast.Compare):
            left = visit(node.left)
            for op, comparator in zip(node.ops, node.comparators):
                right = visit(comparator)
                if isinstance(op, ast.Eq): ok = left == right
                elif isinstance(op, ast.NotEq): ok = left != right
                elif isinstance(op, ast.Lt): ok = left < right
                elif isinstance(op, ast.LtE): ok = left <= right
                elif isinstance(op, ast.Gt): ok = left > right
                elif isinstance(op, ast.GtE): ok = left >= right
                else: raise ModelError(f"Unsupported comparison: {text}")
                if not ok: return False
                left = right
            return True
        raise ModelError(f"Unsupported expression: {text}")

    return visit(tree.body)


@dataclass
class Passage:
    assignments: list[tuple[str, str]]
    body: str


def destination(link: str) -> str:
    if "->" in link: return link.rsplit("->", 1)[1]
    if "<-" in link: return link.split("<-", 1)[0]
    return link.rsplit("|", 1)[-1]


class Story:
    def __init__(self, path: Path, count_hidden_rolls: bool = False):
        self.source = path.read_text(encoding="utf-8")
        self.count_hidden_rolls = count_hidden_rolls
        self.passages = {}
        sections = {}
        for section in re.split(r"^:: ", self.source, flags=re.MULTILINE)[1:]:
            heading, body = section.split("\n", 1)
            name = re.split(r" \[| \{", heading)[0].strip()
            if name in sections: raise ModelError(f"Duplicate passage: {name}")
            sections[name] = body
        self.start = json.loads(sections["StoryData"])["start"]
        # Read the actual lookup formula, not a second hardcoded score formula.
        lookup = re.search(r"setLookup\('score',\s*get\s*=>\s*(.*?)\n\s*\);",
                           sections["StoryScript"], re.DOTALL)
        if not lookup: raise ModelError("Cannot find the score lookup")
        self.score_formula = re.sub(r"\(get\('([A-Za-z]+)'\)\s*\?\?\s*0\)",
                                    r"\1", lookup.group(1)).strip()
        expression(self.score_formula, dict.fromkeys(VARIABLES, 0))
        for name, body in sections.items():
            if name.startswith("Story"): continue
            assignments = []
            split = re.split(r"^--\s*$", body, maxsplit=1, flags=re.MULTILINE)
            if len(split) == 2:
                vars_text, body = split
                for line in vars_text.splitlines():
                    line = line.strip()
                    if not line: continue
                    match = re.fullmatch(r"([\w.]+):\s*(.+)", line)
                    if not match: raise ModelError(f"Unsupported vars line in {name}: {line}")
                    key, value = match.groups()
                    if key.startswith("ui."): continue
                    if key not in VARIABLES:
                        raise ModelError(f"Unknown gameplay variable in {name}: {key}")
                    assignments.append((key, value))
            self.passages[name] = Passage(assignments, body)
        for name in TERMINALS:
            if name not in self.passages: raise ModelError(f"Missing terminal: {name}")

    def score(self, state):
        return expression(self.score_formula, dict(zip(VARIABLES, state)))

    def links(self, name, state=None):
        """Native [if] replaces the preceding condition; [continue] resets it."""
        visible = True
        links = []
        override = False
        for line in self.passages[name].body.splitlines():
            modifier = re.fullmatch(r"\s*\[(if\s+.+|continue)\]\s*", line)
            if modifier:
                text = modifier.group(1)
                visible = (True if state is None or text == "continue"
                           else bool(expression(text[3:], dict(zip(VARIABLES, state)))))
                continue
            # Fail explicitly if a future flow modifier is added to this model.
            if re.fullmatch(r"\s*\[[A-Za-z][^\[\]]*\]\s*", line):
                raise ModelError(f"Unsupported modifier in {name}: {line}")
            if not visible: continue
            if "{game over override}" in line: override = True
            for link in re.findall(r"\[\[(.*?)\]\]", line):
                target = destination(link)
                if target in EXCLUDED or target == self.start: continue
                if target not in self.passages:
                    raise ModelError(f"Missing destination in {name}: {target}")
                is_continue = bool(re.search(r'role:\s*[\"\x27]continue[\"\x27]', line))
                links.append((target, is_continue))
        if state is not None and override:
            values = dict(zip(VARIABLES, state))
            target = ("Game over" if values["happy"] <= 0 else
                      "Game over2" if values["money"] <= 0 else None)
            if target:
                links = [(target if continuation else dest, continuation)
                         for dest, continuation in links]
        return links

    def branches(self, name, before):
        states = [(dict(zip(VARIABLES, before)), None)]
        for key, value in self.passages[name].assignments:
            if value == RANDOM and key == "randomEvent":
                states = [(dict(s, randomEvent=roll), roll)
                          for s, _ in states for roll in range(1, 5)]
            else:
                for s, _ in states:
                    result = expression(value, s)
                    if type(result) is not int:
                        raise ModelError(f"Noninteger resource in {name}: {key} = {result}")
                    s[key] = result
        branches = []
        seen_failures = set()
        for values, roll in states:
            state = tuple(values[v] for v in VARIABLES)
            links = self.links(name, state)
            if not links: raise ModelError(f"No gameplay exit from {name} with {state}")
            for dest, _ in links:
                # A roll hidden by Game Over does not create a new visible route.
                if dest in TERMINALS and dest != "End1" and roll is not None:
                    failure = (dest, state[:4])
                    if not self.count_hidden_rolls and failure in seen_failures: continue
                    seen_failures.add(failure)
                branches.append((dest, state, roll))
        return branches

    def order(self):
        graph = {}
        todo = [self.start]
        while todo:
            name = todo.pop()
            if name in graph: continue
            graph[name] = set() if name in TERMINALS else {d for d, _ in self.links(name)}
            if name not in TERMINALS and "{game over override}" in self.passages[name].body:
                graph[name].update(("Game over", "Game over2"))
            todo.extend(graph[name] - graph.keys())
        indegree = Counter({n: 0 for n in graph})
        for targets in graph.values():
            indegree.update(targets)
        queue = deque(n for n in graph if indegree[n] == 0)
        ordered = []
        while queue:
            name = queue.popleft(); ordered.append(name)
            for dest in sorted(graph[name]):
                indegree[dest] -= 1
                if indegree[dest] == 0: queue.append(dest)
        if len(ordered) != len(graph):
            raise ModelError("Gameplay graph contains a cycle; counting needs an explicit loop rule")
        return ordered


def analyze(story):
    """Propagate integer route multiplicities through equivalent states."""
    frontier = {story.start: Counter({(0, 0, 0, 0, 0): 1})}
    witnesses = {(story.start, (0, 0, 0, 0, 0)): [story.start]}
    terminal = Counter()
    examples = {}
    visited = 0
    for name in story.order():
        states = frontier.pop(name, Counter())
        for state, count in states.items():
            visited += 1
            path = witnesses.pop((name, state))
            if name in TERMINALS:
                key = (TERMINALS[name], *state[:4])
                terminal[key] += count
                examples.setdefault(key, path)
                continue
            for dest, after, roll in story.branches(name, state):
                frontier.setdefault(dest, Counter())[after] += count
                suffix = ([f"randomEvent={roll}"] if roll is not None else []) + [dest]
                witnesses.setdefault((dest, after), path + suffix)
    if frontier:
        raise ModelError(f"Unprocessed destinations: {sorted(frontier)}")
    return terminal, examples, visited


def histogram_svg(histogram):
    """Standalone SVG with stable hooks for the game's translated score overlay."""
    lo, hi = min(histogram), max(histogram)
    scores = [lo + i * 0.5 for i in range(int((hi-lo)*2)+1)]
    peak = max(histogram.values())
    left, top, width, height = 100, 50, 900, 360
    baseline = top + height
    step = width / len(scores)
    bars = []
    for i, score in enumerate(scores):
        count = histogram.get(score, 0); h = height * count / peak
        if not count:
            continue  # Keep physical spacing but do not emit empty rectangles.
        bars.append(f'<rect data-score="{score:g}" data-paths="{count}" '
                    f'x="{left+i*step:.4f}" y="{baseline-h:.4f}" '
                    f'width="{step:.4f}" height="{h:.4f}" fill="#3678a8">'
                    f'<title data-chart-text="binLabel">Score {score:g}: {count:,} successful playthroughs.</title></rect>')
    labels = []
    for i in range(5):
        y = baseline - i*height/4; count = round(peak*i/4)
        labels.append(f'<text data-chart-number="{count}" x="90" y="{y+6}" text-anchor="end">{count:,}</text>')
    for i, score in enumerate(scores):
        if i == 0 or i == len(scores)-1 or score % 5 == 0:
            labels.append(f'<text data-chart-number="{score:g}" data-score-tick="" '
                          f'x="{left+(i+0.5)*step:.4f}" y="{baseline+25}" '
                          f'text-anchor="middle">{score:g}</text>')
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="1060" height="530" '
            'viewBox="0 0 1060 530" role="img" aria-labelledby="score-chart-title score-chart-description">'
            '<title id="score-chart-title" data-chart-text="title">Successful playthroughs by final score</title>'
            '<desc id="score-chart-description" data-chart-text="description">'
            'Number of successful playthroughs at each final score. Counts are not probabilities.</desc>'
            '<rect width="1060" height="530" fill="white"/>'
            '<g font-family="sans-serif" font-size="18" fill="#222">'
            '<text data-chart-text="title" x="550" y="28" font-size="21" text-anchor="middle">'
            'Successful playthroughs by final score</text>'
            + ''.join(bars+labels)
            + f'<path d="M{left} {top} V{baseline} H{left+width}" fill="none" stroke="#222"/>'
            '<text data-chart-text="scoreAxis" x="550" y="510" text-anchor="middle">Final score</text>'
            '<text data-chart-text="pathsAxis" transform="translate(24 230) rotate(-90)" '
            'text-anchor="middle">Number of successful playthroughs</text>'
            '<g data-score-marker=""></g>'
            '</g></svg>\n')


def distribution_lookup(histogram):
    """Only attainable successful scores; integer cumulative path counts."""
    scores = sorted(score for score, count in histogram.items() if count > 0)
    if not scores:
        raise ModelError("Cannot generate a distribution without successful paths")
    cumulative = []
    total = 0
    for score in scores:
        total += histogram[score]
        cumulative.append(total)
    return {"population": "successful_paths", "totalPaths": total,
            "scores": scores, "cumulativeCounts": cumulative}


def update_story_distribution(source, lookup):
    """Replace only the explicitly marked generated data in StoryScript."""
    text = source.read_text(encoding="utf-8")
    pattern = r"(?m)^  // BEGIN GENERATED SCORE DISTRIBUTION\n.*?^  // END GENERATED SCORE DISTRIBUTION"
    replacement = ("  // BEGIN GENERATED SCORE DISTRIBUTION\n"
                   + "  const distribution = " + json.dumps(lookup, separators=(',', ':')) + ";\n"
                   + "  // END GENERATED SCORE DISTRIBUTION")
    if len(re.findall(pattern, text, flags=re.DOTALL)) != 1:
        raise ModelError("Expected exactly one generated score-distribution block in the story")
    updated = re.sub(pattern, lambda _: replacement, text, flags=re.DOTALL)
    if updated != text:
        source.write_text(updated, encoding="utf-8")


def write_results(story, terminal, examples, visited, source, output, update_story=False):
    output.mkdir(parents=True, exist_ok=True)
    histograms = {kind: Counter() for kind in TERMINALS.values()}
    for (kind, circle, happy, money, tech), count in terminal.items():
        score = story.score((circle, happy, money, tech, 0))
        if score*2 != int(score*2):
            raise ModelError("SVG currently requires half-unit scores; update its binning")
        histograms[kind][score] += count
    all_scores = sum(histograms.values(), Counter())
    lookup = distribution_lookup(histograms['success'])
    if update_story:
        update_story_distribution(source, lookup)
    (output/"score-distribution.json").write_text(
        json.dumps(lookup, separators=(',', ':'))+'\n', encoding="utf-8")
    summaries = {}
    for kind, hist in {**histograms, "all_terminal": all_scores}.items():
        if not hist: summaries[kind] = {"paths": 0}; continue
        summaries[kind] = {"paths": sum(hist.values()), "minimum_score": min(hist),
                           "maximum_score": max(hist)}
        if kind != "all_terminal":
            for label, score in (("minimum", min(hist)), ("maximum", max(hist))):
                key = next(k for k in terminal if k[0] == kind and
                           story.score((*k[1:], 0)) == score)
                summaries[kind][label+"_example"] = {
                    "resources": dict(zip(VARIABLES[:4], key[1:])), "path": examples[key]}
    source_name = str(source.resolve().relative_to(ROOT)) if source.resolve().is_relative_to(ROOT) else str(source)
    report = {"source": source_name, "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
              "score_formula": story.score_formula, "count_hidden_rolls": story.count_hidden_rolls,
              "definition": "Distinct gameplay choices and visible random outcomes; stop at End1 or Game Over; exclude explanatory detours, UI controls, credits and restarts.",
              "histogram_definition": "Exact final-score bins; successful and failed paths reported separately. Counts are not probabilities.",
              "processed_passage_states": visited, "results": summaries}
    (output/"summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding="utf-8")
    with (output/"terminal-states.csv").open('w', newline='', encoding="utf-8") as f:
        writer = csv.writer(f); writer.writerow(['ending', 'circle', 'happy', 'money', 'tech', 'score', 'paths'])
        for key, count in sorted(terminal.items()):
            writer.writerow([*key, f'{story.score((*key[1:],0)):g}', count])
    with (output/"score-histogram.csv").open('w', newline='', encoding="utf-8") as f:
        writer = csv.writer(f); writer.writerow(['score', *histograms, 'all_terminal'])
        lo, hi = min(all_scores), max(all_scores)
        for i in range(int((hi-lo)*2)+1):
            score = lo+i*0.5
            writer.writerow([f'{score:g}', *(h.get(score,0) for h in histograms.values()), all_scores.get(score,0)])
    if histograms['success']:
        svg = histogram_svg(histograms['success'])
        (output/"score-histogram.svg").write_text(svg, encoding="utf-8")
        if update_story:
            image = source.parent / "images" / "score-histogram.svg"
            image.parent.mkdir(parents=True, exist_ok=True)
            image.write_text(svg, encoding="utf-8")
    return summaries


def export_paths(story, filename):
    """Optional large CSV: one row per path instead of grouped multiplicities."""
    with filename.open('w', newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(['ending','circle','happy','money','tech','score','path'])
        def walk(name, state, path):
            if name in TERMINALS:
                writer.writerow([TERMINALS[name], *state[:4], f'{story.score(state):g}', json.dumps(path,ensure_ascii=False)])
                return
            for dest, after, roll in story.branches(name,state):
                suffix = ([f'randomEvent={roll}'] if roll is not None else [])+[dest]
                walk(dest,after,path+suffix)
        walk(story.start,(0,0,0,0,0),[story.start])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT/'tripleBalance.twee')
    parser.add_argument('--output', type=Path, default=ROOT/'analysis'/'results')
    parser.add_argument('--count-hidden-rolls', action='store_true', help='Count each random draw even when Game Over suppresses its event')
    parser.add_argument('--paths', type=Path, help='Also write every individual path to this CSV (millions of rows)')
    parser.add_argument('--update-story', action='store_true', help='Also refresh embedded distribution data and images/score-histogram.svg; does not update index.html')
    args = parser.parse_args()
    try:
        story = Story(args.source, args.count_hidden_rolls)
        terminal, examples, visited = analyze(story)
        summaries = write_results(story,terminal,examples,visited,args.source,args.output,args.update_story)
        if args.paths:
            args.paths.parent.mkdir(parents=True,exist_ok=True)
            export_paths(story,args.paths)
    except (ModelError, SyntaxError, KeyError, ValueError) as error:
        parser.exit(1,f'Analysis failed: {error}\n')
    for kind, result in summaries.items():
        print(f"{kind}: {result['paths']:,} paths; score {result.get('minimum_score')}–{result.get('maximum_score')}")
    print(f'Results: {args.output}')


if __name__ == '__main__':
    main()
