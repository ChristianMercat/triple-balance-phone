#!/usr/bin/env python3
"""Export the complete, unmerged gameplay decision tree as SVG.

Uses count_paths.Story for every transition and early ending. Straight-through
narrative passages are folded into edges; no choice or visible random branch is
omitted. SVG definitions are reused as drawing templates, but each occurrence
is a separate drawn subtree, never a joining edge.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from functools import lru_cache
from html import escape
import hashlib
import json
from pathlib import Path
import textwrap

from count_paths import ROOT, Story, TERMINALS, analyze


@dataclass
class Node:
    number: int
    name: str
    state: tuple
    children: list
    counts: tuple
    expanded_nodes: int
    depth: int

    @property
    def leaves(self):
        return sum(self.counts)


class Tree:
    def __init__(self, story):
        self.story = story
        story.order()  # Reject cycles using the same gameplay scope as analysis.
        self.nodes = []

    @lru_cache(maxsize=None)
    def resolve(self, name, state):
        folded = []
        while name not in TERMINALS:
            branches = self.story.branches(name, state)
            if len(branches) != 1:
                break
            folded.append(name)
            name, state, _ = branches[0]
        return name, state, tuple(folded)

    @lru_cache(maxsize=None)
    def build(self, name, state):
        children = []
        if name in TERMINALS:
            index = list(TERMINALS).index(name)
            counts = tuple(int(i == index) for i in range(3))
        else:
            for target, after, roll in self.story.branches(name, state):
                dest, final, folded = self.resolve(target, after)
                child = self.build(dest, final)
                # A roll suppressed by immediate Game Over is not a visible
                # random outcome, matching the main analyzer's default rule.
                label = target if roll is None or target in TERMINALS else f'Roll {roll}: {target}'
                children.append((child, label, folded))
            if len(children) < 2:
                raise ValueError(f'Unfolded non-decision node: {name}')
            counts = tuple(sum(child.counts[i] for child,_,_ in children) for i in range(3))
        node = Node(len(self.nodes),name,state,children,counts,
                    1 + sum(child.expanded_nodes for child,_,_ in children),
                    0 if not children else 1 + max(child.depth for child,_,_ in children))
        self.nodes.append(node)
        return node

    def root(self):
        name,state,folded = self.resolve(self.story.start,(0,0,0,0,0))
        return self.build(name,state),folded


def label_lines(value,width):
    return textwrap.wrap(value,width=width,break_long_words=True,break_on_hyphens=False) or ['']


def write_svg(tree, root, output):
    # Coordinates intentionally retain enough space for individual labels.
    # With millions of leaves this is a very tall vector canvas, not a poster.
    spacing, column = 60, 600
    width = (root.depth+1)*column+300
    height = root.leaves*spacing+220
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('w',encoding='utf-8') as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title description">\n')
        f.write('<title id="title">Triple Balance — full gameplay decision tree</title>\n')
        f.write(f'<desc id="description">Complete decision tree with {root.leaves:,} distinct endings. Every gameplay choice and visible random outcome branches. Paths stop at their first Game Over or at End1. No branches rejoin. Straight-through passages are included in edge tooltips. Repeated SVG use elements draw separate copies of their templates; they do not merge paths. This enormous canvas requires a capable vector viewer and deep zoom.</desc>\n')
        f.write('<style>text{font-family:Arial,Helvetica,sans-serif;font-size:13px;fill:#172b42}.edge{fill:none;stroke:#94a3b8;stroke-width:1}.choice{font-size:12px;fill:#475569}</style>\n<defs>\n')
        for node in tree.nodes:
            span=node.leaves*spacing;middle=span/2
            f.write(f'<g id="t{node.number}">\n')
            tip=f'{node.name}; before-entry state: circle={node.state[0]}, happiness={node.state[1]}, money={node.state[2]}, remaining technologies={node.state[3]}; {node.leaves:,} terminal paths'
            f.write(f'<title>{escape(tip)}</title>\n')
            offset=0
            for child,choice,folded in node.children:
                assert child.number<node.number, 'SVG definition reference would cycle'
                child_y=offset+child.leaves*spacing/2
                f.write(f'<path class="edge" d="M0 {middle:g} H245 V{child_y:g} H{column}"><title>{escape(choice+"; straight-through passages: "+" → ".join(folded))}</title></path>\n')
                lines=label_lines(choice,48)
                for i,line in enumerate(lines):
                    f.write(f'<text class="choice" x="270" y="{child_y-8+i*14:g}">{escape(line)}</text>\n')
                f.write(f'<use xlink:href="#t{child.number}" transform="translate({column} {offset})"/>\n')
                offset+=child.leaves*spacing
            if node.name in TERMINALS:
                color='#18754a' if node.name=='End1' else '#b42336'
                lines=[('SUCCESS' if node.name=='End1' else TERMINALS[node.name].replace('_',' ').upper()),
                       f'Score {tree.story.score(node.state):g} | C {node.state[0]} / H {node.state[1]} / M {node.state[2]}']
            else:
                color='#8a6415' if any(k=='randomEvent' for k,_ in tree.story.passages[node.name].assignments) else '#246291'
                lines=label_lines(node.name,31)
            f.write(f'<circle cx="0" cy="{middle:g}" r="3" fill="{color}"/>\n')
            for i,line in enumerate(lines):
                f.write(f'<text x="12" y="{middle-(len(lines)-1)*7+i*14:g}" style="fill:{color}">{escape(line)}</text>\n')
            f.write('</g>\n')
        f.write('</defs>\n')
        f.write('<text x="30" y="35" font-size="24">Triple Balance — complete decision tree (no merged paths)</text>\n')
        f.write(f'<text x="30" y="65">{root.leaves:,} endings: {root.counts[0]:,} successful, {root.counts[1]:,} happiness failures, {root.counts[2]:,} budget failures.</text>\n')
        f.write('<text x="30" y="90">Read left to right. Each drawn copy is a separate path. Zoom deeply in a vector editor; this is not a page-sized diagram.</text>\n')
        f.write('<text x="30" y="115">Start → introductory passages → Start5 (research decision). Hover an edge for the straight-through passage names.</text>\n')
        f.write(f'<use xlink:href="#t{root.number}" transform="translate(40 170)"/>\n</svg>\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,default=ROOT/'tripleBalance.twee')
    parser.add_argument('--output',type=Path,default=ROOT/'educational_material/en/decision_tree_full.svg')
    args=parser.parse_args()
    story=Story(args.source)
    tree=Tree(story);root,folded=tree.root()
    print(f'Computed {len(tree.nodes):,} drawing templates; {root.expanded_nodes:,} distinct drawn nodes and {root.leaves:,} endings.',flush=True)
    # Verify all terminal state counts and scores against the independent
    # forward traversal in the main analysis, not only the total leaf count.
    terminal,_,_=analyze(story)
    weights={root.number:1}
    actual={}
    for node in reversed(tree.nodes):
        multiplicity=weights.get(node.number,0)
        if node.name in TERMINALS:
            key=(TERMINALS[node.name],*node.state[:4])
            actual[key]=actual.get(key,0)+multiplicity
        for child,_,_ in node.children:
            weights[child.number]=weights.get(child.number,0)+multiplicity
    assert dict(terminal)==actual,'Terminal states disagree with analysis'
    write_svg(tree,root,args.output)
    source_name=str(args.source.resolve().relative_to(ROOT)) if args.source.resolve().is_relative_to(ROOT) else str(args.source)
    metadata={
        'source':source_name,'source_sha256':hashlib.sha256(args.source.read_bytes()).hexdigest(),
        'definition':'Same early endings and visible random outcomes as analysis/count_paths.py; no narrative-only branches, restarts or informational detours.',
        'endings':dict(zip(TERMINALS.values(),root.counts)),
        'leaves':root.leaves,'drawn_nodes':root.expanded_nodes,'drawn_edges':root.expanded_nodes-1,
        'maximum_branch_depth':root.depth,'svg_drawing_templates':len(tree.nodes),
        'straight_through_start':list(folded),
        'terminal_state_and_score_counts_match_analysis':True,
        'note':'SVG templates are instanced independently: the rendered structure is a tree, not a graph with joining edges.'}
    args.output.with_suffix('.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print(f'Written {args.output} ({args.output.stat().st_size/1024/1024:.1f} MiB).',flush=True)


if __name__=='__main__':main()
