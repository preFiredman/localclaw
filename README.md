# LocalClaw 🦞

> Your AI assistant that never leaves your machine. 100% local, 100% private.

LocalClaw is a privacy-first personal AI assistant inspired by OpenClaw. It runs entirely on your local machine with zero external API calls.

## ✨ Features

- 🔒 **100% Private** - All data stays on your machine
- 🤖 **Local LLM** - Powered by Ollama, runs on your GPU
- 🧠 **Long-term Memory** - Vector-based memory with ChromaDB
- 🛠️ **File & System Tools** - Read, write, execute locally
- 💻 **Beautiful TUI** - Terminal UI with Rich

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
git clone https://github.com/YOUR_USERNAME/localclaw.git
cd localclaw
pip install -r requirements.txt
```

### Run

```bash
python -m localclaw
```

## ⚙️ Configuration

Edit `config.yaml`:

```yaml
model:
  name: "qwen2.5:7b"
  base_url: "http://localhost:11434/v1"

memory:
  db_path: "./memory_db"

workspace:
  path: "./workspace"
```

## 🛠️ Tools

- `read_file` - Read any file in workspace
- `write_file` - Write files
- `exec` - Execute shell commands
- `memory_search` - Search long-term memory
- `memory_save` - Save to long-term memory

## 📁 Project Structure

```
localclaw/
├── localclaw/          # Main package
│   ├── agent.py        # Core agent logic
│   ├── memory.py       # Vector memory
│   ├── tools.py        # Tool implementations
│   └── config.py       # Configuration
├── config.yaml         # User config
├── requirements.txt
└── README.md
```

## 🎯 Roadmap

- [x] Basic agent loop
- [ ] File system tools
- [ ] Memory system
- [ ] Beautiful TUI
- [ ] Multi-model support
- [ ] Voice input/output

## 📝 License

MIT

## 🙏 Credits

Inspired by [OpenClaw](https://github.com/openclaw/openclaw) and [PicoClaw](https://github.com/sipeed/picoclaw)
