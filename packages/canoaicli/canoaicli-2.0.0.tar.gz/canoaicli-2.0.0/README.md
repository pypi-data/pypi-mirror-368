![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![PyPI - Version](https://img.shields.io/pypi/v/canoaicli)
[![ClickPy Stats](https://img.shields.io/badge/stats-ClickPy-blue?logo=python)](https://clickpy.clickhouse.com/dashboard/canoaicli)

# Canoaicli – AI in your terminal

**Canoaicli** is a minimalist and intelligent command-line tool. It lets you generate terminal commands from simple natural language instructions, powered by multiple AI providers such as **Google Gemini, OpenAI, Anthropic, and DeepSeek**.

## ⚡️ Quick Start

### ✅ Prerequisites

- **Python ≥ 3.9**
- **At least one API key** from your preferred provider:

  - [OpenAI API key](https://platform.openai.com/account/api-keys)
  - [Google Gemini API key](https://makersuite.google.com/app/apikey) _(Gemini-2.0-flash is free and set as the default model)_
  - [Anthropic API key](https://console.anthropic.com/account/keys)
  - [DeepSeek API key](https://platform.deepseek.com/)

## 🚀 Installation

Make sure you have **Python ≥ 3.9**, then install it easily from PyPI:

```bash
pip install canoaicli
```

## 🧠 Configuration

Before using the CLI, you need to configure your **API key** and select a model.

Run:

```bash
ai configure
```

You will be prompted to choose between two modes:

### 1. Use default (`gemini-2.0-flash`, Free)

The default configuration uses **Gemini Flash** (`gemini-2.0-flash`).
This model is **free to use** with your Gemini API key (within Google’s free tier limits).

➡️ Get your Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey).

```bash
? Select configuration mode:
❯ 1. Use default (gemini-2.0-flash, Free)
  2. Choose another provider/model

🔐 Enter your Gemini API key: ********************
✅ Active model: gemini/gemini-2.0-flash
```

### 2. Choose another provider/model (May require paid API key)

You can also select another provider (OpenAI, Anthropic, DeepSeek, Gemini Pro).

⚠️ In this case, you must provide **your own API key** for that provider.
Depending on the service and the model chosen, usage may require a **paid subscription**.

```bash
? Select configuration mode:
  1. Use default (gemini-2.0-flash, Free)
❯ 2. Choose another provider/model

? Select provider:
❯ openai
  anthropic
  deepseek
  gemini

? Select model:
❯ gpt-4o
  gpt-4o-mini

🔐 Enter your API key for openai: ********************
✅ Active model: openai/gpt-4o
```

Your configuration will be stored in:

```bash
~/.ai-assist/config.json
```

## 💡 Usage

Once installed and configured, use AI directly in your terminal:

```bash
ai ask <your prompt>
```

Examples:

```bash
ai ask "how to list all docker containers"
ai ask "delete all git branches except main"
ai ask "create a new virtual environment in python"

```

The tool will show you the appropriate shell commands, clearly and ready to be copied or run.

## ✨ Refine Your Prompt

Use the `--refine` flag to improve the clarity of your prompt before sending it to the AI.

It rewrites your question in a clearer and more precise way, without changing its meaning. This helps the AI better understand your intent and provide more accurate responses.

**Example:**

```bash
ai ask --refine "find files that contain error"
```

## ✨ Revise Command

Sometimes the AI-generated command is not exactly what you need.
With the Revise command option, you can provide additional instructions to modify the proposed command — without starting over.

**Example session:**

```bash
$ ai ask --refine "delete a git branch"

✨ Improved prompt: Generate the shell command to delete a Git branch.
🧠 Query: Generate the shell command to delete a Git branch.

💡 gemini suggests:
 git branch -d branch_name

? What do you want to do? (Use arrow keys)
   1. Execute
   2. Modify command
   3. Show command with explanation
 » 4. Revise command
   5. Copy to clipboard
   6. Exit
```

Choosing **Revise command (4)** lets you refine it step by step:

```bash
? Add more instructions for revision (leave empty to finish): force delete the branch

💡 Revised command:
 git branch -D branch_name
```

Another refinement:

```bash
? Add more instructions for revision (leave empty to finish): delete branch "feature-login"

💡 Revised command:
 git branch -D feature-login
```

Each new instruction updates the last command until you’re satisfied ✅.

## 📜 History

If you want to use the history feature, you can use the following command:

**This will show you the history of your commands.**

```bash
ai history
```

**You can also search for a specific command in the history:**

```bash
ai history --search <keyword>
```

**You can also clear the history:**

```bash
ai history clear
```

## 🔎 List Available Models

You can list all models available for your configured providers:

```bash
ai models list
```

Example output:

```
Available models:

 - openai/gpt-4o
 - openai/gpt-4o-mini
 - anthropic/claude-sonnet-4-20250514
 - anthropic/claude-opus-4-20250514
 - anthropic/claude-3-7-sonnet-20250219
 - deepseek/deepseek-chat
 - deepseek/deepseek-reasoner
 - gemini/gemini-2.0-flash
 - gemini/gemini-2.0-pro

✔ Default: gemini/gemini-2.0-flash
```

## 🧠 Select AI Model

You can switch between different AI models depending on your needs.

Each provider offers models optimized for speed, reasoning, or cost.

```bash
ai models switch
```

```bash
? Select model:
❯ openai/gpt-4o
  openai/gpt-4o-mini
  anthropic/claude-sonnet-4-20250514
  anthropic/claude-opus-4-20250514
  anthropic/claude-3-7-sonnet-20250219
  deepseek/deepseek-chat
  deepseek/deepseek-reasoner
  gemini/gemini-2.0-flash
  gemini/gemini-2.0-pro
```

## 📖 Help / CLI Options

View all available commands and options:

```bash
ai --help
```

or simply:

```bash
ai -h
```

## 🛠️ Features

- 🔑 **Multi‑provider support**
  Use Google Gemini, OpenAI, Anthropic, or DeepSeek with your own API key.

- ⚡ **Default free model (`gemini-2.0-flash`)**
  Start immediately with Gemini Flash, free via [Google AI Studio](https://makersuite.google.com/app/apikey).

- 📑 **List available models**
  Use `ai models-list` to see which models are available for each provider, and which one is currently active.

- 🧩 **Configurable & secure**
  Store and switch providers/models easily with `ai configure`.
  Your API keys are stored locally and securely.

- 💡 **Natural language to CLI commands**
  Generate `bash`, `git`, `docker`, or `system` commands from simple instructions.

- ✨ **Prompt refinement**
  Use `--refine` to automatically improve your input prompt for better accuracy.

- ✨ **Revise command**: refine and update suggested commands with new instructions.

- 📜 **Command history**
  View, search, and clear your history with `ai history`.

- 🎨 **Interactive interface**
  Built with [`rich`](https://github.com/Textualize/rich) and [`questionary`](https://github.com/tmbo/questionary) for a smooth user experience.

- 🔐 **Secure API key configuration**
  Keys are stored in `~/.ai-assist/config.json` with safe file permissions.

- 🚀 **Fast & extensible**
  Open source, modular design — easy to extend with new providers or features.

## 📦 Local development

To contribute to the project:

```bash
git clone https://github.com/carellihoula/AssistantIACLI.git
```

```bash
cd AssistantIACLI
```

```bash
pixi shell
```

```bash
pixi install
```

## 📃 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ✨ Demo video

_(coming soon)_ 🎥
