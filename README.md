# Djinn-Agent

Djinn-Agent is a lightweight, terminal-based tool designed for seamless interaction with Claude's cutting-edge computer-use capabilities. Tailored for developers who want to harness the full potential of Claude's functionality from the command line, Djinn-Agent provides an intuitive, efficient interface that integrates easily into your workflow.

## 🚀 Features

- **Direct CLI Access**: Interact with Claude directly from your terminal for a streamlined experience.
- **Claude's Computer Use Capabilities**: Leverages Claude’s unique ability to navigate, click, type, and more, simulating human-computer interaction for complex workflows.
- **Customizable for Development**: With simple setup and configuration options, you can easily tweak Djinn-Agent to fit your project's needs.
- **Seamless Integration**: Designed to integrate smoothly with Claude’s API, making advanced AI-powered actions straightforward.

## 🎥 Demo

Check out the [video demo](https://youtu.be/Yg10Ar-xkrc) to see Djinn-Agent in action, where it identifies the largest file in the current directory and generates a concise summary of its contents.

---

## 🛠️ Getting Started

### 1. Installation (For Users)

To get started, install Djinn-Agent via `pip`:

```bash
pip install djinn-agent
```

Once installed, you’ll need to set up an environment variable for authentication with Claude’s API:

```bash
export ANTHROPIC_API_KEY="your_api_key_here"
```

Now you can start using Djinn-Agent directly from your terminal with:

```bash
djinn-agent
```

### 2. Installation (For Developers)

If you’re looking to work on or extend Djinn-Agent, follow these steps:

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/sumleo/djinn-agent.git
   cd djinn-agent
   ```

2. **Run the Setup Script:**

   To set up your development environment, execute:

   ```bash
   ./setup.sh
   ```

3. **Set the API Key:**

   Add the `ANTHROPIC_API_KEY` environment variable:

   ```bash
   export ANTHROPIC_API_KEY="your_api_key_here"
   ```

4. **Start Djinn-Agent:**

   After setup, you’re ready to launch Djinn-Agent and begin development!

---

## 🧑‍💻 Credit

Special thanks to the [Anthropic Quickstarts repository](https://github.com/anthropics/anthropic-quickstarts/tree/main/computer-use-demo) for providing demo code that inspired and powered parts of Djinn-Agent.

---

> Djinn-Agent is your companion for effortlessly harnessing the power of Claude’s computer-use capabilities. Whether you're automating tasks, developing AI workflows, or exploring new applications, Djinn-Agent is here to make it simple and efficient.
