import argparse
from aiassistcli.ai_generate import AIGenerator
from aiassistcli.check_update import check_update, remove_old_config_once
from aiassistcli.config import configure, list_models, switch_model
from .history import handle_history
from .run_prompt import run_prompt
from aiassistcli import __version__



def main():
    parser = argparse.ArgumentParser(prog="ai", description="AI assistant CLI tool")
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show version"
    )
    subparsers = parser.add_subparsers(dest="command")

    # ai configure
    subparsers.add_parser("configure", help="Configure your AI API key")

    # ai models (group)
    models_parser = subparsers.add_parser("models", help="Manage AI models")
    models_subparsers = models_parser.add_subparsers(dest="models_command")
    models_subparsers.add_parser("list", help="List available models")
    models_subparsers.add_parser("switch", help="Set default model interactively")


    # ai history
    history_parser = subparsers.add_parser("history", help="Show command history")
    history_parser.add_argument("--search", help="Filter by keyword")
    history_parser.add_argument("action", nargs="?", choices=["clear"], help="Clear history")

    # ai <prompt>
    ask_parser = subparsers.add_parser("ask", help="Ask AI a question")
    ask_parser.add_argument("prompt", nargs=argparse.REMAINDER, help="Ask a question to the AI")
    ask_parser.add_argument("--refine", action="store_true", help="Refine the prompt before sending")

    args = parser.parse_args()

    if args.command == "configure":
        configure()

    elif args.command == "models":
        if args.models_command == "list":
            list_models()
        elif args.models_command == "switch":
            switch_model()
        else:
            models_parser.print_help()

    elif args.command == "history":
        handle_history(args)

    elif args.command == "ask":
        gen = AIGenerator()
        prompt = " ".join(args.prompt)
        final_prompt = prompt

        if args.refine:
            refined = gen.refine_prompt(prompt)
            final_prompt = refined

        run_prompt(final_prompt)
            
    else:
        parser.print_help()

    if args.command is not None:
        check_update()
        remove_old_config_once()


if __name__ == "__main__":
    main()
