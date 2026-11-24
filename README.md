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
