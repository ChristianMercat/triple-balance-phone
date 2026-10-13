"""Build the isolated demo using the project's existing Chapbook 2.3.1 runtime."""
from pathlib import Path
import html
import json
import re

root = Path(__file__).resolve().parent
source = (root / "i18n-test-cpb.twee").read_text()
sections = re.split(r"^:: ", source, flags=re.MULTILINE)[1:]
passages = []
positions = {}
for section in sections:
    heading, body = section.split("\n", 1)
    name = heading.split(" {")[0]
    if " {" in heading:
        positions[name] = json.loads(heading[len(name) + 1:])
    passages.append((name, body.strip()))
metadata = json.loads(dict(passages)["StoryData"])
title = dict(passages)["StoryTitle"]

# The published story provides the engine shell only, never its passages or script.
runtime = (root / "index.html").read_text()
shell = runtime[:runtime.index('<tw-storydata name=')]
if 'format="Chapbook" format-version="2.3.1"' not in runtime[runtime.index('<tw-storydata name='):][:500]:
    raise ValueError("Expected the existing Chapbook 2.3.1 runtime")
shell = re.sub(r"<title>.*?</title>", f"<title>{html.escape(title)}</title>", shell, count=1)
story = (f'<tw-storydata name="{html.escape(title, quote=True)}" startnode="1" '
         f'creator="Twine" creator-version="2.12.0" format="Chapbook" '
         f'format-version="2.3.1" ifid="{metadata["ifid"]}" options="" hidden>')
script = (root / "twine-i18n-chapbook.js").read_text()
if "</script" in script.lower():
    raise ValueError("Story JavaScript must not contain a closing script tag")
story += f'<script role="script" id="twine-user-script" type="text/twine-javascript">{script}</script>'
story += '<style role="stylesheet" id="twine-user-stylesheet" type="text/twine-css"></style>'
for pid, (name, body) in enumerate((p for p in passages if p[0] not in ("StoryTitle", "StoryData")), 1):
    layout = positions.get(name, {})
    story += (f'<tw-passagedata pid="{pid}" name="{html.escape(name, quote=True)}" tags="" '
              f'position="{html.escape(layout.get("position", "0,0"), quote=True)}" '
              f'size="{html.escape(layout.get("size", "100,100"), quote=True)}">'
              f'{html.escape(body)}</tw-passagedata>')
story += '</tw-storydata></html>'
(root / "i18n-test-cpb.html").write_text(shell + story)
print("Built i18n-test-cpb.html")
