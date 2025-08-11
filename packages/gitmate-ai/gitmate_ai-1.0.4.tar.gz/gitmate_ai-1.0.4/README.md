
# 🧠 GitMate — AI Git Terminal Assistant

GitMate is a terminal-based assistant powered by **LangChain + your choice of LLM (Gemini, OpenAI, Claude)**.  
It helps you execute Git and shell commands interactively, detects common errors like merge conflicts or fatal errors, and offers AI-powered help — right inside your terminal.

---

## ⚙️ Features

- 💬 Talk to the AI with `@bot your question`
- 🧠 Pick your preferred model: OpenAI GPT-4o, Gemini 2.0, or Claude 3
- 🤖 Auto-detect Git errors and offer intelligent help
- 💾 Logs the entire terminal session
- ⚡ Fully automated mode with CLI flags (`--model`, `--api-key`)

---

## 🚀 Quickstart

### 1. Install

```bash
pip install gitmate-ai
````

### 2. Run Interactively

```bash
gitmate
```

You'll be prompted to select an LLM model and enter your API key.

---

## 🔧 Command-Line Arguments

| Flag        | Description                              | Example            |
| ----------- | ---------------------------------------- | ------------------ |
| `--model`   | Select LLM: `openai`, `gemini`, `claude` | `--model gemini`   |
| `--api-key` | Provide your API key                     | `--api-key sk-...` |

Skip all prompts:

```bash
gitmate --model claude --api-key YOUR_KEY
```

---

## 🤖 Usage Examples

### Ask the bot directly:

```bash
@bot how do I revert the last commit?
```

### Handle errors interactively:

If GitMate detects an error (like a merge conflict), it will ask:

```
🚨 I noticed a merge conflict. Do you want help resolving it?
```

---

## 📓 Session Logs

All terminal activity is logged automatically as:

```
git_session_YYYYMMDD_HHMMSS.log
```

Useful for reviewing your Git workflow or debugging sessions.

---

## 🧩 Future Ideas

* `--command` flag: Run a single Git command with AI help and exit
* Task Performer Agent
* Markdown output formatting
* Live Git watch mode for auto-analysis
* API key manager / config file support
---

## 🛡️ Disclaimer

This tool runs Git and shell commands using Python’s `subprocess`.
Always review AI suggestions before executing potentially destructive commands.

---

## 👨‍💻 Author

Built by [Tejas Raundal](https://github.com/TejasRaundal)

---

## 📄 License

MIT License
