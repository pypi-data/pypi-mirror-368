from pathlib import Path
from datetime import datetime
import json
from typing import Literal, Optional
from rich.table import Table
from rich.console import Console

HISTORY_PATH = Path.home() / ".ai-assist" / "history.json"
console = Console()

def save_history(query: str, command: str, action: Literal["run", "explain", "cancel"]) -> None:
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    history = []

    if HISTORY_PATH.exists():
        try:
            history = json.loads(HISTORY_PATH.read_text())
        except Exception:
            pass

    history.append({
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "command": command,
        "action": action,
    })

    HISTORY_PATH.write_text(json.dumps(history[-100:], indent=2)) 

def show_history(search: Optional[str] = None) -> None:
    if not HISTORY_PATH.exists():
        console.print("[yellow bold]No history found.[/yellow bold]")
        return

    try:
        history = json.loads(HISTORY_PATH.read_text())
    except Exception as e:
        console.print(f"[red bold]Failed to read history: {e}[/red bold]")
        return

    if search:
        history = [h for h in history if search.lower() in h["query"].lower() or search.lower() in h["command"].lower()]
        if not history:
            console.print(f"[red bold]No results found for:[/red bold] '{search}'")
            return

    entries = history
   
    table = Table(show_lines=True)
    table.add_column("Time", style="cyan", no_wrap=True)
    table.add_column("Query", style="magenta")
    table.add_column("Command", style="green")
    table.add_column("Action", style="yellow")

    for entry in reversed(entries):
        table.add_row(entry["timestamp"], entry["query"], entry["command"], entry["action"])

    with console.pager():
        console.print(table)

def clear_history() -> None:
    if HISTORY_PATH.exists():
        HISTORY_PATH.unlink()
        console.print("[green bold]History cleared.[/green bold]")
    else:
        console.print("[yellow bold]No history to clear.[/yellow bold]")
    return

def handle_history(args):
    if args.action == "clear":
        clear_history()
        return

    show_history(search=args.search)
