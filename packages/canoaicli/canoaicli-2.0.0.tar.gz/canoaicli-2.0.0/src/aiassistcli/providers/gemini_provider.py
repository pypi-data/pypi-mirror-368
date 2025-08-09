import sys
from aiassistcli.ai_prompt import build_prompt
import google.generativeai as genai
from .base import AIProvider
from rich.console import Console

console = Console()

class GeminiProvider(AIProvider):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        genai.configure(api_key=api_key)

    def generate(self, model: str, prompt: str, refine: bool = False):
        try:
            model = genai.GenerativeModel(model)
            final_prompt = prompt if refine else build_prompt(prompt)
            response = model.generate_content(final_prompt)
            return response.text.strip()
     
        except Exception as e:
            console.print(
                "[red]Something is wrong with your API key. Check that your key is correct, has the right permissions, "
                "and that you haven’t exceeded your usage quota.[/red]"
            )
            sys.exit(1)
    
    def explain_command(self, model: str, command: str) -> str:
        prompt = f"""
        Generate the same CLI command as: {command}
        Add brief inline comments to each line explaining what it does.
        Only output the command with the comments, no extra explanation.
        """
        return self.generate(model, prompt)
    
    def refine_prompt(self, model: str, prompt: str,) -> str:
        """Send the prompt to the language model for refinement."""
        console = Console()
        refine_instruction = (
            "Please improve the following prompt without changing its intent or purpose. "
            "Make it clearer, more concise, and more precise, while preserving its original meaning."
            "Please rephrase it as a single clear sentence, without any additional explanation."
            "The refined prompt helps generate commands for shells like Bash, Zsh, CMD, PowerShell, Docker CLI, etc."
        )
        full_prompt = f"{refine_instruction}\n\nPrompt original:\n{prompt}"
        
        refined = self.generate(model, full_prompt, refine=True)
        console.print(f"✨ [bold cyan]Improved prompt[/bold cyan]: [white]{refined}[/white]")
        return refined
        