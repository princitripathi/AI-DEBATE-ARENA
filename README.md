# ⚖️ AI Debate Arena

A multi-agent system where two LLM-powered debaters argue opposite sides of any topic, and a third, impartial AI judge scores the exchange and delivers a verdict.

Instead of a single agent answering a question, this project explores **structured multi-agent disagreement**: two agents with distinct personas argue back and forth over several rounds, responding directly to each other's points, before a separate judge agent evaluates both sides and produces a scored, synthesized conclusion.

## Why this project

Most "AI agent" demos are a single agent calling tools. This one is built around **agent-to-agent interaction and evaluation** — each debater keeps track of its own argument history, responds to its opponent's last point, and a dedicated judge model (with zero temperature, for consistency) scores both sides on a rubric rather than just picking a "winner" arbitrarily.

## How it works

```
Topic → [FOR Agent] ↔ [AGAINST Agent]  (N rounds, each responding to the other)
                 ↓
           [Judge Agent] → Score (out of 10 each) + strongest argument per side + verdict
```

- **Debater agents** (`nvidia/nemotron-3-nano-30b-a3b:free`) are each given a persona and expertise (e.g. "technology economist," "labor economist") to keep arguments grounded and distinct.
- **Judge agent** (`nvidia/nemotron-3-nano-30b-a3b:free`, temperature `0.2`) evaluates the full transcript and returns a structured verdict: winner, scores, strongest argument per side, and a balanced synthesis.
- Optional `--export` flag saves the whole debate + verdict as a clean Markdown transcript, so debates can be archived or shared.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# add your OPENROUTER_API_KEY to .env
```

## Usage

```bash
# Use the default topic
python agent.py

# Pick your own topic
python agent.py --topic "Remote work is better than office work"

# More rounds = deeper back-and-forth
python agent.py --topic "Cryptocurrency will replace fiat currency" --rounds 3

# Save the full debate as a Markdown file (transcripts/debate_<timestamp>.md)
python agent.py --topic "Universal basic income should be adopted" --rounds 2 --export
```

## Example output

```
⚖️  DEBATE: AI will eliminate more jobs than it creates
============================================================
🟢 FOR: Dr. Alex Chen (technology economist and AI researcher)
🔴 AGAINST: Prof. Sarah Martinez (labor economist and social policy expert)
🏛️  Rounds: 2
============================================================

--- Round 1 ---

🟢 Dr. Alex Chen (FOR):
[opening argument...]

🔴 Prof. Sarah Martinez (AGAINST):
[rebuttal + counter-argument...]

...

🏛️  JUDGE'S VERDICT
[scores, strongest arguments, balanced synthesis]
```

## Tech stack

- **Framework**: LangChain
- **Model**: nvidia/nemotron-3-nano-30b-a3b:free via OpenRouter
- **Language**: Python

## Ideas for extending this

- Swap the CLI for a Streamlit/Gradio UI so debates can be watched live, round by round
- Add a third "fact-checker" agent that flags unsupported claims mid-debate
- Let users vote on rounds and compare their picks to the judge's verdict
- Support local models via Ollama for a fully offline version

## License

MIT
