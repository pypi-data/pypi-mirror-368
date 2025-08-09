import sys
from aiassistcli.ai_prompt import build_prompt
from openai import OpenAI, AuthenticationError, RateLimitError
from rich.console import Console
from .base import AIProvider

console = Console()

class OpenAICompatibleProvider(AIProvider):
    def __init__(self, api_key: str, base_url: str):
        super().__init__(api_key)
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def generate(self, model: str, prompt: str, refine: bool = False) -> str:
        try:
            final_prompt = prompt if refine else build_prompt(prompt)
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user", 
                        "content": f"{final_prompt}"
                    }
                ],
            )
            return response.choices[0].message.content
        except AuthenticationError:
            console.print("[red]Invalid API key. Please reconfigure with ai configure.[red]")
            sys.exit(1)
        # except RateLimitError:
        #     print(f"You exceeded your {model} quota. Check your plan/billing.")
        #     sys.exit(1)
        except Exception as e:
            console.print(
                "[red]Something is wrong with your API key. Check that your key is correct, has the right permissions," 
                "and that you haven’t exceeded your usage quota.[red]"
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