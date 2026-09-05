<p align="center"><img src="assets/fileblade-extension-logo.svg" alt="FileBlade extension" width="640"></p>

---

**FileBlade Agent Hooks** shows the hooks your agents are configured to run in [FileBlade](https://github.com/data-goblin/fileblade), which gives you IDE-like sidebars for Omarchy. 

<p align="center"><img src="assets/hooks-blade.png" alt="Agent Hooks blade" width="640"></p>

The purpose of this extension is to list every configured hook for your installed agents, by agent and event, with where it is configured and whether it is enabled. It never runs a hook and it redacts what a hook command does. It supports:
- Codex
- Claude Code
- OpenCode
- Pi
- Copilot CLI
- Antigravity

> [!NOTE]
> Please submit a PR if you want support for other agents.

Agent Hooks groups hooks by agent and event in a FileBlade filetree, for the project selected in the file tree. Hooks show up by their script name, or by the name you give them: press `n` on a hook to name it. The column control switches between status, type and date columns, and sorts or filters each group, so you can compare hook coverage across agents at a glance.

<p align="center"><img src="assets/hooks-columns.gif" alt="Switching the hooks column from status to last update and sorting it" width="640"></p>

## Installation / Quick-start

Until this extension appears in the Omarchy marketplace, install it directly
from GitHub. Requires Omarchy 4.0.2 or later, FileBlade and Python 3.11+. FileBlade includes its
bundled x86-64 Linux binary; no separate extension binary or build is needed.

1. [Install FileBlade](https://github.com/data-goblin/fileblade#installation--quick-start) first.

2. Install and enable this extension:

   ```bash
   OMARCHY_SHELL_IPC_TIMEOUT=10s omarchy plugin add https://github.com/data-goblin/fileblade-hooks.git --enable
   ```

3. Restart the shell after installation finishes:

   ```bash
   omarchy restart shell
   ```

4. Select Hooks in a FileBlade module slot.

To remove this extension:

```bash
omarchy plugin remove data-goblin.fileblade-hooks
omarchy restart shell
```

Removing the extension preserves your files, previous agent configuration
changes and FileBlade's saved state and recoverable bins.

This concise README is human-written to convey the simple intent and purpose of this extension. Full (agent-written) docs are in [docs/agent-written/README.md](docs/agent-written/README.md); design notes in [ARCHITECTURE.md](ARCHITECTURE.md). 

Building your own extension is covered in FileBlade's [EXTENSIONS.md](https://github.com/data-goblin/fileblade/blob/main/EXTENSIONS.md).

### FileBlade Repos

- [FileBlade core](https://github.com/data-goblin/fileblade)
- [Memory](https://github.com/data-goblin/fileblade-memory)
- [Skills](https://github.com/data-goblin/fileblade-skills)
- [MCP](https://github.com/data-goblin/fileblade-mcp)
- [Hooks](https://github.com/data-goblin/fileblade-hooks)

## License

MIT, see [LICENSE](LICENSE).
