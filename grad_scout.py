"""Grad Scout: finds Master's and PhD programs/labs that match your interests.

Same setup as scout.py (Ollama + `pip install ddgs requests`).
Run it weekly, not daily: programs and deadlines don't change that fast.
Output: grad-programs-YYYY-MM-DD.md next to this script.

IMPORTANT: a small local model can misread snippets. Treat every result as a
lead and confirm deadlines and requirements on the official program page.
"""
import datetime
import json
import pathlib

import requests
from ddgs import DDGS

# ---- edit these ----
DEGREES = ["PhD"]
INTERESTS = [
    "machine learning",
    "brain-computer interfaces neural engineering",
    "artificial intelligence", 
    "neurocomputation"
]
ENTRY_TERM = "Fall 2027"
MODEL = "llama3.2"
# --------------------

OLLAMA_URL = "http://localhost:11434/api/chat"


def search(query, n=8):
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
            "options": {"num_ctx": 8192, "num_predict": 1200, "temperature": 0.2},
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=180,
    )
    r.raise_for_status()
    return json.loads(r.json()["message"]["content"])


def main():
    today = datetime.date.today().isoformat()
    lines = [f"# Grad program leads for {today} ({ENTRY_TERM} entry)", ""]
    seen_urls = set()

    for degree in DEGREES:
        for interest in INTERESTS:
            print(f"Searching: {degree} / {interest}", flush=True)
            results = search(f"{degree} program {interest} admissions {ENTRY_TERM}")
            valid_urls = {r.get("href") for r in results}
            snippets = "\n".join(
                f"[{i}] {r.get('title', '')} | {r.get('href', '')} | {r.get('body', '')}"
                for i, r in enumerate(results)
            )
            prompt = f"""You are helping a student find {degree} programs in: {interest}.
Using ONLY the search results below, list programs or labs that look relevant.
Do not invent anything. If a deadline or requirement is not in the snippet,
write "check the page" for it. The url must be copied exactly from the results.

Return JSON only:
{{"programs": [{{"school": "", "program": "", "why_relevant": "one sentence", "deadline": "", "url": ""}}]}}

Results:
{snippets}"""
            print("  Waiting on model...", flush=True)
            try:
                programs = ask_model(prompt).get("programs", [])
            except Exception as e:
                print(f"model call failed: {e}")
                continue

            lines.append(f"## {degree}: {interest}")
            lines.append("")
            kept = 0
            for p in programs:
                url = p.get("url", "")
                # Drop anything whose link wasn't actually in the search results
                if url not in valid_urls or url in seen_urls:
                    continue
                seen_urls.add(url)
                kept += 1
                lines.append(f"### {p.get('school', '?')}: {p.get('program', '?')}")
                lines.append(f"{p.get('why_relevant', '')}  ")
                lines.append(f"Deadline (unverified): {p.get('deadline', 'check the page')}  ")
                lines.append(f"[Program page]({url})")
                lines.append("")
            if not kept:
                lines.append("_No usable leads this run._")
                lines.append("")

    out = pathlib.Path(__file__).parent / f"grad-programs-{today}.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved to {out}")


if __name__ == "__main__":
    main()