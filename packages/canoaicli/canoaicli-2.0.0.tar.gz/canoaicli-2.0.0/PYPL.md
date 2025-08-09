# 🧠 Canoaicli – AI Commands in Your Terminal

**Canoaicli** is a smart and minimalist CLI tool powered by Google Gemini. It transforms plain English instructions into terminal commands (bash, git, docker, etc.) – instantly.

## ⚡️ Quick Start

### ✅ Prerequisites

- Python ≥ 3.9
- A Gemini API key ([Get it here](https://makersuite.google.com/app/apikey))

### 📦 Installation

Install directly from PyPI:

```bash
pip install canoaicli
```

### 🔐 Configure Gemini API

Before using, run:

```bash
ai configure
```

Enter your Gemini API key when prompted. It will be saved securely on your system.

## 💡 Example Usage

Transform any plain English question into ready-to-run commands:

```bash
ai ask "<your question>"
```

Examples:

```bash
ai ask "how to list all docker containers"
ai ask "delete all git branches except main"
ai ask "create a new virtual environment in python"
```

The tool will instantly generate and display the appropriate command(s).

## ✨ Refine Your Prompt

Use the `--refine` flag to improve the clarity of your prompt before sending it to the AI.

It rewrites your question in a clearer and more precise way, without changing its meaning. This helps the AI better understand your intent and provide more accurate responses.

**Example:**

```bash
ai ask --refine "find files that contain error"
```

## 🕘 View Command History

Canoaicli keeps track of your previous prompts and responses.

```bash
ai history
```

Search your history:

```bash
ai history --search <keyword>
```

Clear the history:

```bash
ai history clear
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

- ✔️ Natural language → bash, git, docker, etc.
- 🧠 Powered by Gemini AI
- 🎨 Rich & interactive terminal UI
- 🔐 Secure API key configuration
- 📜 Local history with search
- 🧩 Easy to extend and customize

## 🤖 Ideal For

- Developers tired of googling shell commands
- Beginners looking to learn by example
- Productivity-focused engineers and power users

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

## 📄 License

Licensed under the [MIT License](https://github.com/carellihoula/AssistantIACLI/blob/master/LICENSE).
