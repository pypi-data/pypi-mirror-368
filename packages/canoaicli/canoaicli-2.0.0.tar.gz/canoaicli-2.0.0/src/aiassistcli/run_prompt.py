import subprocess
import sys
from aiassistcli.ai_generate import AIGenerator
from aiassistcli.config import copy_command, custom_style, load_config
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
import questionary
from .history import save_history

def run_prompt(prompt: str) -> None:

    console = Console()
    gen = AIGenerator()
    default_model = load_config().get("default_model")
    if default_model is None:
        console.print("[bold red] No default model configured. Run 'ai configure' first.[bold red]")
        sys.exit(1)
    provider = default_model["provider"]
    conversation = []
    
    console.print(f"[bold cyan]🧠 Query:[/bold cyan] {prompt}")
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[grey] Processing...[/grey]"),
            transient=True
        ) as progress:
            progress.add_task("thinking", total=None)
            command = gen.generate(prompt)
        
        # add the initial prompt and generated command to the conversation history
        conversation.append({"question": prompt, "answer": command})
        
    except Exception as e:
        console.print(f"[red] Error:[/red] {e}")
        sys.exit(1)

    console.print(f"\n[bold green]✨ {provider} suggests:[/bold green]")
    console.print(f"[green bold] {command}[/green bold]\n")

    while True:
        choice = questionary.select(
                "What do you want to do?",
                choices=[
                    "1. Execute",
                    "2. Modify command",
                    "3. Show command with explanation",
                    "4. Revise command",
                    "5. Copy to clipboard",
                    "6. Exit",
                ],
                style=custom_style
                ).ask()
            
        if choice.startswith("1"):
                is_confirmed = questionary.confirm("Are you sure you want to execute this command?").ask()
                if is_confirmed:
                    # console.print("[cyan] Executing...[/cyan]\n")
                    subprocess.run(command, shell=True)
                    save_history(prompt, command, action="run")
                # else:
                #     console.print("[red]🚫 Command cancelled.[/red]")
                conversation.clear()
                break
                

        elif choice.startswith("2"):
                new_cmd = questionary.text("📝 Modify the command:", default=command ).ask()
                
                if new_cmd:
                    is_confirmed = questionary.confirm("Are you sure you want to execute this command?").ask()
                    if is_confirmed:
                        # console.print("[cyan] Executing...[/cyan]\n")
                        subprocess.run(new_cmd, shell=True)
                        save_history(prompt, new_cmd, action="run")
                    # else : 
                    #     console.print("[red]🚫 Command cancelled.[/red]")
                conversation.clear()
                break
                    
        elif choice.startswith("3"):
                try:
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[grey] Explaining command...[/grey]"),
                        transient=True
                    ) as progress:
                        progress.add_task("explaining", total=None)
                        explanation = gen.explain_command(command)
                except Exception as e:
                    console.print(f"[red]Gemini Error:[/red] {e}")
                    sys.exit(1)

                console.print(f"[green bold] {explanation}[/green bold]\n")
                save_history(prompt, command, action="explain")
                conversation.clear()
                break
        elif choice.startswith("4"):
             while True:
                extra = questionary.text("Add more instructions for revision (leave empty to finish):").ask()
                if not extra.strip():
                    break

                context_text = ""
                for turn in conversation:
                    context_text += f"User: {turn['question']}\nAssistant: {turn['answer']}\n"
                context_text += f"User: {extra}\nAssistant:"

                revise_prompt = (
                    "You are an assistant that generates correct terminal commands.\n\n"
                    "Here is the previous conversation between user and assistant:\n"
                    f"{context_text}\n\n"
                    "Revise the last assistant command strictly following the new user instructions.\n"
                    "Return only the corrected/updated command, no explanation, no extra text."
                )

                with Progress(
                    SpinnerColumn(),
                    TextColumn("[grey bold] Revising...[/grey bold]"),
                    transient=True
                ) as progress:
                    progress.add_task("revise", total=None)
                    revised_cmd = gen.generate(revise_prompt)

                console.print("\n[bold green]✨ Revised command:[/bold green]")
                console.print(f"[bold green] {revised_cmd}[/ bold green]\n")

                # Add the new question/answer to the conversational context
                conversation.append({"question": extra, "answer": revised_cmd})

                save_history(prompt, revised_cmd, action="revise")
                command = revised_cmd

        elif choice.startswith("5"):
            copy_command(command)
            conversation.clear()
            break

        else:
                # console.print("[red]🚫 Command cancelled.[/red]")
                save_history(prompt, command, action="cancel")
                conversation.clear()
                break