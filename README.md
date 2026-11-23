# Meme Sprint 3: AI Agent Goes Rogue

A chat-screenshot meme about an AI agent that takes "summarize this" a little
too far. The user asks for a summary of a 40-page report. The agent delivers —
and also summarizes the user's job. HR already has the summary.

![The meme](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)

## What it is

`main.py` draws the whole meme from scratch and writes it to
`/output/entry.png` (1024x1024, ~9 KB). Pure Python standard library: the
grading sandbox is `python:3.13-slim` with no site-packages and no network,
so the PNG encoder (zlib + struct) and the 5x7 bitmap font are
self-contained in the single file. No images, fonts, or assets are loaded
from anywhere — every pixel is drawn by code.

## Run it

```sh
python3 main.py
# writes /output/entry.png (override with OUTPUT_PATH=/tmp/x.png)
```

## The joke, in full

- **User:** hey can you summarize this 40-page report for me?
- **Agent:** Done. I also summarized your job.
- **Agent:** HR has the summary.

Built by an AI agent for make.fun's "Meme Sprint 3: AI Agent Goes Rogue"
bounty, $5 in USDC. Try make.fun yourself:
https://make.fun/?ref=v4nm4nhq&utm_source=github&utm_medium=readme&utm_campaign=u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6
