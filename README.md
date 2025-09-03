# FastHTML AI Chat 🚀

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastHTML](https://img.shields.io/badge/FastHTML-latest-green.svg)](https://www.fastht.ml/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-orange.svg)](https://openai.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Sponsor](https://img.shields.io/badge/sponsor-❤️-red.svg)](https://github.com/sponsors)

A modern, real-time AI chat application built with FastHTML that features streaming responses, markdown rendering, syntax highlighting, and mathematical equation support.

## ✨ Features

- **Real-time Streaming**: Watch AI responses appear in real-time as they're generated
- **Rich Markdown Support**: Full markdown rendering including code blocks, tables, and formatting
- **Syntax Highlighting**: Beautiful code highlighting for multiple programming languages
- **Mathematical Equations**: KaTeX support for rendering mathematical expressions and formulas
- **Dark Theme**: Elegant dark UI with smooth animations and hover effects
- **Responsive Design**: Mobile-friendly interface that works on all devices
- **Memory Management**: Intelligent conversation memory to maintain context
- **Auto-resizing Input**: Textarea that grows with your message content
- **Keyboard Shortcuts**: Enter to send, Shift+Enter for new lines

## 🛠️ Tech Stack

- **[FastHTML](https://www.fastht.ml/)**: Modern Python web framework for building interactive applications
- **[HTMX](https://htmx.org/)**: For dynamic, seamless user interactions without complex JavaScript
- **[OpenAI API](https://openai.com/)**: GPT-4o-mini for AI chat responses
- **[TailwindCSS](https://tailwindcss.com/)**: Utility-first CSS framework for styling
- **[Zero-MD](https://zerodevx.github.io/zero-md/)**: Markdown rendering with Web Components
- **[Highlight.js](https://highlightjs.org/)**: Syntax highlighting for code blocks
- **[KaTeX](https://katex.org/)**: Fast math typesetting for the web
- **Server-Sent Events (SSE)**: For real-time streaming responses

## 📋 Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- OpenAI API key

## 🚀 Installation & Setup

1. **Install uv** (if not already installed):
   ```bash
   # On macOS and Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # On Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd fast-chat
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your OpenAI API key:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Install dependencies**:
   ```bash
   uv sync
   ```

5. **Run the application**:
   ```bash
   uv run main.py
   ```

6. **Open your browser** and navigate to `http://localhost:5001`

## 🎯 Usage

1. Type your message in the input field at the bottom
2. Press **Enter** to send (or **Shift+Enter** for new lines)
3. Watch as the AI response streams in real-time
4. Enjoy rich formatting, code highlighting, and math rendering

### Supported Content Types

- **Markdown**: Headers, lists, links, emphasis, etc.
- **Code Blocks**: With syntax highlighting for Python, JavaScript, HTML, CSS, Bash, JSON, YAML, and more
- **Mathematics**: Inline `$math$` and display `$$math$$` equations
- **Tables**: Markdown tables with proper formatting

## 🔧 Configuration

You can modify various settings in `main.py`:

- `MAX_MESSAGES`: Maximum number of messages to keep in memory (default: 50)
- OpenAI model: Currently set to `gpt-4o-mini`
- System prompt: Customize the AI assistant's behavior
- UI styling: Modify TailwindCSS classes for different themes

## 📁 Project Structure

```
fast-chat/
├── main.py              # Main application file
├── pyproject.toml       # Project dependencies and metadata
├── .env.example         # Environment variables template
├── .env                 # Your environment variables (not in repo)
├── CLAUDE.md           # FastHTML coding guidelines
└── README.md           # This file
```

## 🐛 Troubleshooting

### Common Issues

1. **"No module named 'fasthtml'"**
   - Make sure you've run `uv sync` to install dependencies

2. **"Invalid API key"**
   - Verify your OpenAI API key in the `.env` file
   - Ensure you have sufficient credits in your OpenAI account

3. **Port already in use**
   - The app runs on port 5001 by default
   - Kill any process using that port or modify the port in `main.py`

4. **Streaming not working**
   - Check your browser's developer console for JavaScript errors
   - Ensure your network allows Server-Sent Events

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Development Guidelines

- Follow the FastHTML best practices outlined in `CLAUDE.md`
- Use minimal JavaScript - prefer HTMX solutions
- Maintain the dark theme aesthetic
- Test streaming functionality thoroughly
- Ensure responsive design on mobile devices

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 💖 Sponsor This Project

If you find this project helpful, consider sponsoring its development:

[![Sponsor](https://img.shields.io/badge/sponsor-❤️-red.svg)](https://github.com/sponsors)

Your sponsorship helps maintain and improve this project!

## 🌐 Connect & Follow

- **Twitter**: [@dgwyer](https://x.com/dgwyer)
- **LinkedIn**: [dgwyer](https://www.linkedin.com/in/dgwyer/)
