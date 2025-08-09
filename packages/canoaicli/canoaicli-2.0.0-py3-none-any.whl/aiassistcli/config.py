from pathlib import Path
import json
import questionary
from rich.console import Console
import pyperclip

CONFIG_DIR = Path.home() / ".ai-assist"
CONFIG_PATH = CONFIG_DIR / "config.json"

SUPPORTED_MODELS = {
    "openai": ["gpt-4.1-mini", "gpt-4o-mini", "gpt-4o"], # , "gpt-4o-mini"
    # "anthropic": ["claude-sonnet-4", "claude-sonnet-4",],
    "deepseek": ["deepseek-chat"],
    "gemini": ["gemini-2.0-flash", "gemini-2.5-flash"],
}

DEFAULT_PROVIDER = "gemini"
DEFAULT_MODEL = "gemini-2.0-flash"

# Custom style for questionary
custom_style = questionary.Style([
   ('qmark', 'fg:#673ab7 bold'),        
    ('question', 'bold'),               
    ('answer', 'fg:#f44336 bold'),      
    ('pointer', 'fg:#673ab7 bold'),     
    ('highlighted', 'fg:#673ab7 bold'), 
    ('selected', 'fg:#cc5454'),         
    ('separator', 'fg:#cc5454'),        
    ('instruction', ''),               
    ('text', ''),                      
    ('disabled', 'fg:#858585 italic')
])

console = Console()

def save_config(config: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, indent=2))

def load_config() -> dict:
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text())
    return {}

def configure():
    choice = questionary.select(
        "Select configuration mode:",
        choices=[
            "1. Use default (Gemini Flash)",
            "2. Choose another provider/model",
        ],
        style=custom_style
    ).ask()

    config = load_config()

    if choice.startswith("1"):
        # Cas 1 : default Gemini Flash
        api_key = questionary.password("🔐 Enter your Gemini API key:", style=custom_style).ask()

        if not api_key:
            console.print("[red bold] No API key entered. Aborting.[/red bold]")
            return

        config["default_model"] = {
            "provider": DEFAULT_PROVIDER,
            "model": DEFAULT_MODEL,
        }
        config.setdefault("providers", {})[DEFAULT_PROVIDER] = {"api_key": api_key}
        save_config(config)

        console.print(
            f"[white bold]Active model: [/white bold] [green bold]{DEFAULT_PROVIDER}/{DEFAULT_MODEL}[/green bold]"
             " - You can now use: [bold cyan]ai ask <your prompt>[/bold cyan]"
        )


    else:
        provider = questionary.select(
            "Select provider:", choices=list(SUPPORTED_MODELS.keys()), style=custom_style
        ).ask()

        model = questionary.select(
            "Select model:", choices=SUPPORTED_MODELS[provider], style=custom_style
        ).ask()

        api_key = questionary.password(f"🔐 Enter your API key for {provider}:", style=custom_style).ask()
        if not api_key:
            console.print("[red bold]No API key entered.[/red bold]")
            return

        config["default_model"] = {"provider": provider, "model": model}
        config.setdefault("providers", {})[provider] = {"api_key": api_key}
        save_config(config)

        console.print(
            f"[white bold]Active model: [/white bold][green]{provider}/{model}[/green]"
            " - You can now use: [bold cyan]ai ask <your prompt>[/bold cyan]"
        )

def list_models():
    console.print("\n[bold cyan]Available models[/bold cyan]:")
    for provider, models in SUPPORTED_MODELS.items():
        for model in models:
            console.print(f" - {provider}/{model}")
    config = load_config()
    default_model = config.get("default_model")
    if default_model:
        console.print(
            f"\n[green bold]✔ Default: {default_model['provider']}/{default_model['model']}[/green bold]"
        )
    else:
        console.print("\n[green bold]✔ Default: [/green bold][red bold]No default model configured. Run 'ai configure' first[/red bold]")
    
def switch_model():
    """Sets the default model in the configuration."""
    try:
        models_available = []
        for provider, models in SUPPORTED_MODELS.items():
            for model in models:
                # console.print(f" - {provider}/{model}")
                models_available.append(f"{provider}/{model}")
        # return models_available
        choice = questionary.select(
                "Select a model",
                choices=models_available,
                style=custom_style
                ).ask()
        # choice = f"{choice.split('/')[0]}/{choice.split('/')[2]}" if len(choice.split('/')) == 3 and choice.split('/')[0] == choice.split('/')[1] else choice
        
        provider, model = choice.split('/')
    except ValueError:
        console.print(f"[red]Invalid model format. Use 'provider/model' (e.g., 'openai/gpt-4o').[/red]")
        return

    if provider not in SUPPORTED_MODELS or model not in SUPPORTED_MODELS[provider]:
        console.print(f"[red bold]Model '{model}' is not supported.[/red bold]")
        console.print("Use 'ai models list' to see available models.")
        return

    config = load_config()

    if not config.get("providers", {}).get(provider, {}).get("api_key"):
        console.print(f"[yellow bold]API key for '{provider}' is not configured.[/yellow bold]")
        api_key = questionary.password(f"🔐 Enter your API key for {provider}:", style=custom_style).ask()
        if not api_key:
            console.print("[red bold]No API key entered. Aborting.[/red bold]")
            return
        config.setdefault("providers", {})[provider] = {"api_key": api_key}

    config["default_model"] = {"provider": provider, "model": model}
    save_config(config)
    console.print(f"[green bold]✔ Default model set to: {provider}/{model}[/green bold]")

def copy_command(command: str):
    pyperclip.copy(command)