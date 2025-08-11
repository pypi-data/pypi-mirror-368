def main():
    import subprocess
    from datetime import datetime
    import os
    import re
    import argparse

    from rich.console import Console
    from rich.prompt import Prompt, Confirm
    from rich.text import Text

    from langchain_core.prompts import ChatPromptTemplate
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_openai import ChatOpenAI
    from langchain_anthropic import ChatAnthropic

    console = Console()

    # 🧠 Argument Parser
    parser = argparse.ArgumentParser(description="GitMate - AI Git Terminal Assistant")
    parser.add_argument("--model", type=str, choices=["openai", "gemini", "claude"], help="LLM model to use")
    parser.add_argument("--api-key", type=str, help="API key for the selected model")
    args = parser.parse_args()

    # 🌐 Select LLM Provider
    model_choice = args.model
    if not model_choice:
        console.print("\n🤖 [bold cyan]Welcome to GitMate! Choose your LLM model:[/]")
        console.print("1. [green]OpenAI (ChatGPT)[/]")
        console.print("2. [blue]Google Gemini[/]")
        console.print("3. [magenta]Anthropic Claude[/]")
        selected = Prompt.ask("Enter choice [1/2/3]", choices=["1", "2", "3"], default="2")
        model_choice = {"1": "openai", "2": "gemini", "3": "claude"}[selected]

    api_key = args.api_key  # default: None

    # 🔑 API Key + LLM Initialization
    if model_choice == "openai":
        if not api_key:
            api_key = Prompt.ask("🔑 [bold green]Enter your OpenAI API Key[/]").strip()
        os.environ["OPENAI_API_KEY"] = api_key
        llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
        provider_name = "OpenAI GPT-4o"

    elif model_choice == "gemini":
        if not api_key:
            api_key = Prompt.ask("🔑 [bold blue]Enter your Google Gemini API Key[/]").strip()
        os.environ["GOOGLE_API_KEY"] = api_key
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
        provider_name = "Google Gemini 2.0"

    elif model_choice == "claude":
        if not api_key:
            api_key = Prompt.ask("🔑 [bold magenta]Enter your Claude API Key[/]").strip()
        os.environ["ANTHROPIC_API_KEY"] = api_key
        llm = ChatAnthropic(model="claude-3-sonnet-20240229", temperature=0.3)
        provider_name = "Claude 3 Sonnet"

    else:
        console.print("[red]❌ Invalid model selection[/]")
        return

    LOG_FILE = f"git_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    console.print(f"\n🎯 [bold cyan]GitMate Terminal Started with {provider_name}[/]")
    console.print(f"💾 [green]Logging to:[/] {LOG_FILE}")
    console.print("📝 Type your commands. Type [yellow]`exit`[/] or [yellow]`quit`[/] to stop.")
    console.print("🤖 Type [magenta]`@bot your question`[/] to ask GitMate.\n")

    ERROR_PATTERNS = [
        (r"CONFLICT", "I noticed a merge conflict. Do you want help resolving it?"),
        (r"error:", "An error occurred. Do you want me to help debug it?"),
        (r"fatal:", "A fatal error happened. Want me to investigate?"),
    ]

    def invoke_bot(question, history):
        console.print("🤖 [yellow]Thinking...[/]")
        prompt = ChatPromptTemplate.from_template(
            """You are GitMate — a concise, helpful git assistant.

            Here is the git session log so far:
            {history}

            The user asked:
            {question}

            Reply directly to the user in a short, clear, and friendly way.
            - Use “you” instead of “the user”.
            - If possible, give one or two specific commands or steps.
            - Keep the answer under 100 words.
            - Always give safe commands unless user explicitly requests otherwise.
            - If more context is needed, briefly ask what they want to achieve."""
        )
        chain = prompt | llm
        answer = chain.invoke({"history": history, "question": question})
        response_text = answer.content.strip()
        console.print(f"\n🤖 [bold green]GitMate:[/] {response_text}\n")
        return response_text

    with open(LOG_FILE, "w", encoding="utf-8") as log:
        while True:
            try:
                cmd = Prompt.ask("[bold blue]>>>[/]").strip()
            except (EOFError, KeyboardInterrupt):
                console.print("\n👋 [bold red]Exiting.[/]")
                break

            if cmd.lower() in {"exit", "quit"}:
                break
            if not cmd:
                continue

            # BOT mode
            if cmd.startswith("@bot"):
                question = cmd.replace("@bot", "", 1).strip()
                with open(LOG_FILE, "r", encoding="utf-8") as lf:
                    history_lines = lf.readlines()
                recent_history = "".join(history_lines[-100:])

                log.write(f"\n>>> @bot {question}\n")
                log.flush()
                response_text = invoke_bot(question, recent_history)
                log.write(f"🤖 {response_text}\n")
                log.flush()
                continue

            # Normal shell command
            timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
            log.write(f"\n{timestamp} >>> {cmd}\n")
            log.flush()

            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

            detected_error = None
            for line in process.stdout:
                line_clean = line.rstrip()
                console.print(Text(line_clean, style="white"))
                log.write(line + "\n")
                log.flush()

                for pattern, msg in ERROR_PATTERNS:
                    if re.search(pattern, line_clean, re.IGNORECASE):
                        detected_error = (pattern, msg)
                        break
                if detected_error:
                    break

            process.wait()
            if process.returncode != 0:
                console.print(f"[red]⚠️ Command exited with code {process.returncode}[/]")

            if detected_error:
                _, suggestion_msg = detected_error
                console.print(f"\n🚨 [bold red]{suggestion_msg}[/]")
                wants_help = Confirm.ask("[cyan]Do you want GitMate to help?[/]")
                if wants_help:
                    with open(LOG_FILE, "r", encoding="utf-8") as lf:
                        history_lines = lf.readlines()
                    recent_history = "".join(history_lines[-100:])
                    response_text = invoke_bot(suggestion_msg, recent_history)
                    log.write(f"🤖 {response_text}\n")
                    log.flush()
                detected_error = None

    console.print(f"\n✅ [bold green]Session saved to {LOG_FILE}[/]")

if __name__ == "__main__":
    main()
