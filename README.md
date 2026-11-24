# Local Desk Portable

A native terminal for private, offline AI. The starter model runs on the device that opens it.

[Download Local Desk](https://github.com/jonaskuusela393-ctrl/local-desk-portable/releases/latest)

Pick the installer or USB ZIP for your operating system and processor. The release includes desktop builds for Linux, Windows, and macOS, an Android ARM64 build for Termux, and an unsigned iOS source project for Xcode. The starter model and runtime are already in each ZIP.

| Command | What it does |
| --- | --- |
| `/model` | Select a local GGUF. |
| `/room` | Host or join an invite-only text chat with other Local Desk users. |
| `/mcp tools desk` | List the bundled local tools. |
| `/mcp call desk system_info {}` | Ask the local MCP server which OS and processor you're using. |
| `/clear` | Clear the current assistant conversation. |

For an offline installation, copy the extracted folder over USB, open the matching launcher and choose a model the device can fit in memory. A group chat needs a reachable host and a private invitation. AI conversations work offline.

The release notes identify which targets were tested and give device-specific instructions.

## Project tools and messaging

| Task | Commands |
| --- | --- |
| Search past conversations and continue one | `/sessions search text`, `/resume latest`, `/new` |
| Edit several files, test and undo | `/batch app.py test_app.py -- describe the change`, `/diff`, `/apply`, `/test`, `/undo` |
| Ask about a local PDF or screenshot | `/attach "manual.pdf" question` |
| Choose, download or compare local GGUFs | `/models fit`, `/models get ID`, `/models compare ID ID -- question` |
| Exchange messages with other users | `/contacts join INVITE HANDLE`, `/contacts add HANDLE`, `/dm HANDLE message`, `/inbox` |
| Connect a tool server | `/mcp add NAME EXECUTABLE`, `/mcp discover NAME`, `/mcp enable NAME TOOL`, `/mcp ask NAME -- question`, `/mcp run` |

Desktop packages include the offline interpreter, llama.cpp and a small starter model. Model inference stays on the device. Online search, downloads, third-party tools and messaging use the services you select. Host a mailbox with `--mailbox ADDRESS:PORT` to retain deliveries for offline users. Anyone who operates the mailbox can read its stored messages.

Extract the ZIP and open its launcher, or use the installer for your system and CPU. A complete extracted desktop package can also be carried on USB. The bundled 360M model prioritizes a small download and can give wrong answers to simple questions. Android ARM64 uses Termux, with Python for the full CLI. The iPhone and iPad download is a native Xcode project for a signed device build. Its app supports document and image input, local project edits, JSON validation and HTTPS MCP tools. Isolated desktop project tests require a supported runner. Full visual inference requires a vision model.
