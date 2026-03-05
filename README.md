# LocalClaw 🦞

[![Tests](https://github.com/preFiredman/localclaw/actions/workflows/tests.yml/badge.svg)](https://github.com/preFiredman/localclaw/actions/workflows/tests.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> Your AI assistant that never leaves your machine. 100% local, 100% private.

LocalClaw is a privacy-first personal AI assistant inspired by OpenClaw. It runs entirely on your local machine with zero external API calls.

![TUI Screenshot](https://via.placeholder.com/800x400?text=TUI+Screenshot+Coming+Soon)

## ✨ Features

- 🔒 **100% Private** - All data stays on your machine
- 🤖 **Local LLM** - Powered by Ollama, runs on your GPU
- 🧠 **Long-term Memory** - Vector-based memory with ChromaDB
- 🛠️ **File & System Tools** - Read, write, execute locally
- 🖥️ **Beautiful TUI** - Terminal UI with file browser and chat interface
- 💻 **CLI Mode** - Simple command-line interface
- 🧪 **Well Tested** - Automated tests running daily

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- [Ollama](https://ollama.com/) installed
- NVIDIA GPU (optional but recommended)

### Install Ollama

```bash
# macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model (qwen2.5 is recommended for Chinese)
ollama pull qwen2.5:7b
```

### Install LocalClaw

```bash
git clone https://github.com/preFiredman/localclaw.git
cd localclaw
pip install -r requirements.txt
```

### Run

#### TUI Mode (Recommended)
```bash
python -m localclaw --tui
# or
python -m localclaw -t
```

#### CLI Mode
```bash
python -m localclaw
```

#### Single Message
```bash
python -m localclaw -m "What is the weather today?"
```

## 🖥️ TUI Interface

The TUI provides:
- 📁 **File Browser** - Navigate your workspace
- 💬 **Chat Interface** - Real-time streaming responses
- 🎨 **Syntax Highlighting** - Code blocks are beautifully rendered
- ⌨️ **Keyboard Shortcuts**:
  - `Ctrl+C` - Quit
  - `Ctrl+L` - Clear chat

## ⚙️ Configuration

Edit `config.yaml`:

```yaml
model:
  name: "qwen2.5:7b"
  base_url: "http://localhost:11434/v1"
  temperature: 0.7
  max_tokens: 4096

memory:
  db_path: "./memory_db"
  collection_name: "localclaw_memory"

workspace:
  path: "./workspace"
  restrict_to_workspace: true
```

## 🛠️ Tools

- `read_file` - Read any file in workspace
- `write_file` - Write files
- `list_dir` - List directory contents
- `exec` - Execute shell commands
- `memory_search` - Search long-term memory
- `memory_save` - Save to long-term memory

## 🧪 Testing

Run tests locally:

```bash
pytest tests/ -v
```

With coverage:

```bash
pytest tests/ --cov=localclaw --cov-report=html
```

## 📦 Building

Build standalone executable:

```bash
pip install pyinstaller
pyinstaller --onefile --name localclaw localclaw/__main__.py
```

## 📁 Project Structure

```
localclaw/
├── localclaw/          # Main package
│   ├── __init__.py     # Version info
│   ├── __main__.py     # Entry point
│   ├── agent.py        # Core agent logic
│   ├── config.py       # Configuration
│   ├── memory.py       # Vector memory
│   ├── tools.py        # Tool implementations
│   └── tui.py          # TUI interface
├── tests/              # Test suite
│   └── test_localclaw.py
├── .github/workflows/  # CI/CD
│   ├── tests.yml       # Daily automated tests
│   └── release.yml     # Build releases
├── config.yaml         # User config
├── requirements.txt    # Dependencies
├── pytest.ini         # Test configuration
└── README.md          # This file
```

## 🎯 Roadmap

- [x] Basic agent loop
- [x] File system tools
- [x] Memory system
- [x] Beautiful TUI
- [x] Automated testing
- [x] GitHub Actions CI/CD
- [ ] ChromaDB vector search
- [ ] Web search tool (DuckDuckGo)
- [ ] Voice input/output
- [ ] Multi-model support
- [ ] Plugin system

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.

## 🙏 Credits

Inspired by [OpenClaw](https://github.com/openclaw/openclaw) and [PicoClaw](https://github.com/sipeed/picoclaw)

---

⭐ **Star this repo if you find it helpful!**
