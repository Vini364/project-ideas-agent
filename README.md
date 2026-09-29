# Scout: Local Project Idea Generator

A free, local Python automation that researches your technical interests, generates tailored 2-to-4-week software project ideas using a local LLM, and surfaces existing GitHub repositories to help you evaluate prior work. 

All AI generation runs locally via Ollama, ensuring privacy and zero API costs.

## Prerequisites

* Python 3.x
* [Ollama](https://ollama.com/) installed and running locally

## Installation & Setup

1. **Pull the default local model:**
   ```bash
   ollama pull llama3.2
   ```

2. **Install the required Python packages:**
   ```bash
   pip install ddgs requests
   ```

3. **Download the script:** Save the provided code as `scout.py`.

## Configuration

Open `scout.py` and modify the variables at the top to match your goals:

```python
INTERESTS = [
    "machine learning",
    "brain-computer interfaces / neurotech",
]
N_IDEAS = 5
MODEL = "llama3.2"  # Must match a model you have pulled via Ollama
```

## Usage

Run the script from your terminal:

```bash
python scout.py
```

The script will take a few moments to search and generate, then output a file named `ideas-YYYY-MM-DD.md` in the same directory.

### Example Output File
```markdown
# Scout ideas for 2026-09-29

## 1. Neuro-Controlled Terminal Multiplexer
A tmux wrapper that uses consumer BCI hardware inputs to switch panes or execute macros based on concentration levels.  
Difficulty: hard

Closest existing work:
- [bci-tmux-integration](https://github.com/...)
- [mental-macros](https://github.com/...)
```

## Automating with Cron

If you want Scout to run automatically every morning, you can schedule it using cron. 

When setting up your crontab, you **must** use the absolute path to the Python environment where you installed `requests` and `ddgs` (especially if you use a version manager like pyenv), otherwise the job will fail silently.

Open your crontab (`crontab -e`) and add an entry like this to run it every day at 10:00 AM:

```bash
0 10 * * * cd /path/to/sc