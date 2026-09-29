"""Scout: a free, local daily project-idea finder.

Setup:
  1. Install Ollama (https://ollama.com) and run:  ollama pull llama3.2
  2. pip install ddgs requests
  3. python scout.py
Ideas are saved to ideas-YYYY-MM-DD.md next to this script.
"""
import datetime
import json
import pathlib

import requests
from ddgs import DDGS

# ---- edit these ----
INTERESTS = [
    "machine learning",
    "brain-computer interfaces / neurotech",
]
N_IDEAS = 5
MODEL = "llama3.2"  # any model you've pulled with Ollama
# --------------------

OLLAMA_URL = "http://localhost:11434/api/chat"


def search(query, n=5):
    try:
        with DDGS() as d:
            return list(d.text(query, max_results=n))
    except Exception as e:
        print(f"search failed for {query!r}: {e}")
        return []


def ask_model(prompt):
    r = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "stream": False,
            "format": "json",
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=600,
    )
    r.raise_for_status()
    return json.loads(r.json()["message"]["content"])


def main():
    # 1. Gather inspiration from the web
    snippets = []
    for topic in INTERESTS:
        for r in search(f"{topic} project ideas github", 5):
            snippets.append(f"- {r.get('title', '')}: {r.get('body', '')}")

    # 2. Ask the local model for ideas
    prompt = f"""You are Scout. Using the search snippets below only as inspiration,
propose {N_IDEAS} project ideas a solo CS student could build in 2 to 4 weeks.
Prefer a specific twist on an existing idea over something generic.
My interests: {', '.join(INTERESTS)}.

Return JSON only, in this shape:
{{"ideas": [{{"title": "", "pitch": "one sentence", "difficulty": "easy|medium|hard", "search_query": "short query to check if this already exists"}}]}}

Snippets:
{chr(10).join(snippets)}"""
    ideas = ask_model(prompt).get("ideas", [])

    # 3. Check each idea for existing work and write the report
    today = datetime.date.today().isoformat()
    lines = [f"# Scout ideas for {today}", ""]
    for i, idea in enumerate(ideas, 1):
        lines.append(f"## {i}. {idea.get('title', 'Untitled')}")
        lines.append(f"{idea.get('pitch', '')}  ")
        lines.append(f"Difficulty: {idea.get('difficulty', '?')}")
        lines.append("")
        lines.append("Closest existing work:")
        for r in search(f"{idea.get('search_query', idea.get('title', ''))} github", 3):
            lines.append(f"- [{r.get('title', 'link')}]({r.get('href', '')})")
        lines.append("")

    out = pathlib.Path(__file__).parent / f"ideas-{today}.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {len(ideas)} ideas to {out}")


if __name__ == "__main__":
    main()