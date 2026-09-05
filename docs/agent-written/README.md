# Omarchy Agent Hooks

An inventory of the hooks your coding agents are configured to run, grouped by
agent and event, with an agents strip that copies one hook into another
agent's user hook file. It shows that a hook exists, where it is configured,
which event it fires on, whether it is enabled, and which agents carry the
same command on the equivalent event. It never shows what the hook actually
runs, and it never runs it.

Private plugin. The eventual repository name is `fileblade-hooks`.

## Required dependency and Install order

**Omarchy Fileblade (`data-goblin.fileblade`) must be installed and enabled first.**

Requires Omarchy 4.0.2 or later, core FileBlade and Python 3.11+. Follow the direct GitHub installation
and removal instructions in the [root README](../../README.md), then select
Hooks in a FileBlade module slot. No marketplace listing is required.

The contribution uses `extensions["data-goblin.fileblade/blade"]` with
`hostContract: 2`. Its service supplies the missing-host prompt and provider
lifecycle. With FileBlade unavailable, the shared guard offers to install or
enable the host. It does not install anything without an explicit action.
Inventories reuse FileBlade's shared services; see the
[host contract](https://github.com/data-goblin/fileblade/blob/main/EXTENSIONS.md).
Removing the extension preserves host layout/view state, recoverable bins and
previous changes to the user's files or agent configuration.

## Zero execution

This plugin never runs a configured hook, never opens a network connection, and
never reads a credential store. The helper imports no `subprocess`, `socket`,
or `urllib`, and uses no `eval`, `exec`, or `__import__`. It uses Linux `statx`
through libc only to read creation timestamps. A sentinel test installs a
`sys.addaudithook` and asserts that a full `list` raises no process, exec,
network, write, or destructive filesystem audit event, even with the `apply`
module already imported.

## What is redacted

Hook payloads are treated as secret material. The inventory carries only safe
metadata:

```yaml
kept:      agent, source file path, scope, support status, event name,
           type (command/http/prompt), field names present, matcher shape
           (none/literal/pattern), timeout seconds, env variable count,
           conditional flag, an 8 character digest of the primary payload
           (command, bash, powershell, url, or prompt, first present),
           payload byte length, appliedAgents, and a label: the hook's own
           statusMessage, name, or description value when one is set,
           otherwise the basename of the script when the command is a path
           (`~/.claude/hooks/guard.sh` shows as `guard.sh`, `bun test`
           shows nothing), and always overridden by a name the user gave
           the hook in FileBlade's own store (labelSource says which)
never emitted:
           command strings, bash or powershell bodies, arguments, URLs,
           headers, environment keys or values, prompts, working directories,
           filesystem operands, tokens
```

Fixtures embed canary tokens, env values, URLs, header values, and file
operands; a test asserts none of them appear anywhere in the output, and that
each row's summary carries exactly the ten safe keys.

## The column control

The right column of the header is a `MetricPicker` shared with Fileblade. It is
one control with three gestures:

```yaml
Left click:   sorts by the current metric. Numbers and dates start descending,
              text starts ascending; a second click flips, a third clears
Right click:  menu. Radio list of metrics, Sort ascending, Sort descending,
              Clear sort, Filter…, Clear filter. Enter, Space, or Menu on the
              focused control opens the same menu
Filter…:      popup. Date metrics take since and until (ISO prefix, 7d/3w/2m/1y,
              today, yesterday, presets 7d 30d 90d 1y); number metrics take min
              and max (plain, 1.5k, 2m). The filter runs before grouping and the
              trigger shows a filter glyph while one is active. f in the tree
              opens the popup, s toggles the sort
```

Metrics and their kinds, as declared in `blades/Module.qml`:

```yaml
agents (default):   agents strip per row, see below
status, type:       text; status is enabled/disabled/unknown event/code, type is
                    command/http/prompt/script/unknown
updated, created:   date, from the source config file
summary:            text, the same detail string the row already shows
```

Metric, sort, and filter are remembered per slot through the host's
`context.state` (`metric`, `sort`, `filter`), owned by a `PaneView` the module
loads through `context.ui.url("PaneView")` and exposes as `view`, which the host
`BladeSlot` reads for the tab bar.

## The agents strip

With the `agents` metric each hook row ends in one mark per installed agent
(Claude Code, Codex, GitHub Copilot CLI, Antigravity, OpenCode, Pi,
as detected by the host's `files.installedAgents`), lit in brand colour when
that agent carries the hook and grey otherwise, plus a robot glyph for all.

A hook row belongs to one agent and one file. The lit set is the backend field
`appliedAgents`: every agent that has a row whose payload digest matches and
whose event maps to the same canonical event (table below). Two agents with
the same `curl …` under `PreToolUse`/`BeforeTool` therefore light each other's
marks, even when neither copy was made by this plugin. A row without a digest
(code-hosted locations) lights only its own agent.

```yaml
click a grey mark:    agent-hooksctl apply … --agent <id> --state on
click a lit mark:     … --state off, refused for the row's own agent
click the robot:      every installed agent on; when every installed agent is
                      already lit, every one off except the row's own agent
while it runs:        the status reads Applying… (in the header, or in the tab
                      bar when the slot is tabbed and the header is hidden)
when a target fails:  the header shows the payload's message (agent: reason,
                      one per failed target) until the next refresh; the other
                      targets in the same click still apply
```

OpenCode and Pi marks are present when those agents are installed but every
apply to them is refused: their hooks live in code and there is no hook file
to write.

## apply

```
agent-hooksctl apply --project <dir> --id <row id> --agent <agent id|all> [--agent <id> ...] --state on|off --json
-> { "ok": true, "schemaVersion": 1, "project": ..., "results": [ { "agent", "ok", "changed", "message", "touched": [paths] } ] }
```

`--id` is a row id from `list` for the same `--project`. `all` expands to the
five writable agents; with `--state off` it skips the row's own agent. The
top-level `ok` is the AND of every per-agent `ok` and false when `results` is
empty; `message` joins the failures as `agent: message` separated by `; ` and
is empty when everything succeeded. The exit status is 0 when `ok` is true and
1 otherwise. Per-agent outcomes keep their own `ok`, `changed`, `message`, and
`touched`, so a partial success still names what was written.

### label

```
agent-hooksctl label --digest <8 hex> --text "<name>" --json
-> { "ok": true, "schemaVersion": 1, "digest", "label", "changed", "message", "touched": [path] }
```

Names live in FileBlade's own file, `$XDG_CONFIG_HOME/omarchy/fileblade/hooks/labels.json`
(default `~/.config/omarchy/fileblade/hooks/labels.json`), keyed by the payload
digest, so a name follows the same command into every agent it is copied to
and never touches an agent's configuration. An empty text removes the name.
Names are single-line, at most 80 characters, at most 512 of them; the file is
written atomically like every other target. `list` reads the store on every
scan and reports such rows with `labelSource: user`.

### Event mapping

Source events are mapped to the target agent's documented name through this
table. A blank cell means the target has no equivalent and the apply is
refused for that agent. Events outside the table (Antigravity `PreInvocation`,
`PostInvocation`; Copilot `errorOccurred`, `userPromptTransformed`; the
Claude-only remainder) map only to the same agent.

```yaml
canonical            claude-code         codex              copilot-cli          antigravity
SessionStart:        SessionStart        SessionStart       sessionStart         -
SessionEnd:          SessionEnd          SessionEnd         sessionEnd           -
UserPromptSubmit:    UserPromptSubmit    UserPromptSubmit   userPromptSubmitted  -
PreToolUse:          PreToolUse          PreToolUse         preToolUse           PreToolUse
PostToolUse:         PostToolUse         PostToolUse        postToolUse          PostToolUse
PostToolUseFailure:  PostToolUseFailure  -                  postToolUseFailure   -
PermissionRequest:   PermissionRequest   PermissionRequest  permissionRequest    -
Notification:        Notification        -                  notification         -
Stop:                Stop                Stop               agentStop            Stop
SubagentStart:       SubagentStart       SubagentStart      subagentStart        -
SubagentStop:        SubagentStop        SubagentStop       subagentStop         -
PreCompact:          PreCompact          PreCompact         preCompact           -
PostCompact:         PostCompact         PostCompact        -                    -
```

Copilot's documented PascalCase aliases (`PreToolUse`, `Stop`, …) are
normalised to the camelCase name before mapping, so an aliased Copilot row and
a camelCase one share a canonical event.

### What on writes

`on` reads the source hook from its own file (JSON, JSONC, or Codex TOML), keeps
its command, matcher, timeout, and `if` where the target supports them, and
appends one entry to the target agent's user-scope hook file under the mapped
event. Only `type: command` hooks travel; http and prompt hooks are refused.

```yaml
claude-code:  ~/.claude/settings.json
              hooks.<Event>: [{ matcher?, hooks: [{ type, command, timeout?, if? }] }]
              timeout in seconds, if kept
codex:        $CODEX_HOME or ~/.codex/hooks.json
              hooks.<Event>: [{ matcher?, hooks: [{ type, command, timeout? }] }]
              timeout in seconds
copilot-cli:  $COPILOT_HOME or ~/.copilot/hooks/hooks.json, version 1
              hooks.<event>: [{ type, bash, timeoutSec? }]
              flat entries as documented; the format has no matcher or if, so
              they are dropped. Any other file under ~/.copilot/hooks/ is read by
              list but never written
antigravity:  ~/.gemini/config/hooks.json
              hook-<digest>: { <Event>: [{ matcher?, hooks: [{ type, command, timeout? }] }] }
              one named group per copied hook so enabled can be set per copy;
              timeout in seconds
```

`on` is idempotent: when the mapped event already holds an entry with the same
digest the result is `ok: true, changed: false` and nothing is written.

### What off writes

`off` removes, under the mapped event of the target file above, every entry
whose primary payload digest matches the source row. Emptied groups, emptied
event arrays, and emptied Antigravity hook groups are dropped. Entries in
other files (a Copilot `guard.json`, a project settings file, a plugin) are
never touched, so a mark can stay lit after `off` when another file still
carries the command; the row detail names the source file.

### Refusals

```yaml
target is not a regular file:      symlink, FIFO, directory
target is not strict JSON:         comments, trailing commas, a non-object
                                   root; nothing is rewritten and the file is
                                   left byte for byte
target hooks is not an object:     or an event value is not an array
copilot version is not 1:          the file is left alone
no event equivalent:               see the table
row is the target agent, off:      the row's own agent keeps its hook
row is code-hosted:                opencode and pi directories describe no hook
row is not a command hook:         http and prompt hooks
row changed since it was listed:   the digest no longer matches; refresh
```

### How it writes

The document is serialised with two-space indentation and a trailing newline
to a temporary file beside the target (`O_CREAT | O_EXCL`), fsynced, given the
target's existing mode (0644 for a new file), and renamed over the target.
Missing parent directories are created. Files are read with the same
`O_NOFOLLOW`, regular-file, and 256 KiB bounds as `list`.

## Agents covered

```yaml
documented hook mechanisms (parsed into event rows):
  claude-code:  /etc/claude-code/managed-settings.json, ~/.claude/settings.json,
                project .claude/settings.json and .claude/settings.local.json,
                and plugin hooks/hooks.json in the plugin cache
                33 documented events
  codex:        $CODEX_HOME or ~/.codex/hooks.json and config.toml, plus project
                .codex/hooks.json and .codex/config.toml, reading both the
                hooks.json form and the inline [hooks] table
                11 documented events; rows are badged feature-off unless
                [features] hooks (or the deprecated codex_hooks) is true
                profiles $CODEX_HOME/NAME.config.toml, selected only with
                         --profile NAME, so rows are listed with scope profile,
                         enabled null, and badged profile-unselected. They are
                         never counted as active, and never carry the base
                         config's feature-off badge, which describes only the
                         active user, project, and hooks.json rows
  copilot-cli:  policy   /etc/github-copilot/policy.d/*.json, alphabetical,
                         accepted only as a regular no-follow file owned by
                         root and neither group- nor world-writable
                files    $COPILOT_HOME or ~/.copilot/hooks/*.json and
                         repository .github/hooks/*.json
                settings ~/.copilot/settings.json, .github/copilot/settings.json
                         and settings.local.json, .claude/settings.json and
                         .claude/settings.local.json
                plugins  ~/.copilot/installed-plugins/MARKETPLACE/PLUGIN and
                         ~/.copilot/installed-plugins/_direct/SOURCE-ID, whose
                         hooks live in hooks.json or hooks/hooks.json
                14 camelCase events plus 12 documented VS Code compatible
                PascalCase aliases, badged vscode-alias with canonicalEvent
  antigravity:  ~/.gemini/config/hooks.json and workspace .agents/hooks.json,
                always under the real home. Each top-level key is a hook group
                name; its event arrays hold either documented
                { matcher, hooks: [...] } groups or bare entries. The group's
                enabled flag is the default for its entries and the group name
                is emitted as group. 5 documented events

code-hosted (listed as locations only, never inspected):
  opencode:     ~/.config/opencode/plugins, .opencode/plugins, and the plugin
                array in opencode.json
  pi:           ~/.pi/agent/extensions, .pi/extensions, and the extensions and
                packages arrays in settings.json
```

For OpenCode and Pi the hooks live inside JavaScript or TypeScript, so their
behaviour cannot be known without executing or interpreting code. Those rows
report the location and a file count, are badged `not-inspected`, and carry no
event. Nothing is imported, evaluated, or inferred.

### Version gates and disableAllHooks

```yaml
version: 1 required:  policy files, and standalone hook files under
                      ~/.copilot/hooks and .github/hooks. A file whose version
                      is anything else is rejected whole
version not required: inline hooks blocks in settings files, which use the
                      settings schema and document no version key
disableAllHooks:
  in a standalone hook file:  disables only that file's own rows
  in user settings:           disables only that file's own inline rows
  in repository settings:     disables every non-policy Copilot row from files,
                              settings, and plugins, badged repository-disabled
  policy rows:                never disabled, badged policy
```

### Environment overrides

```yaml
CODEX_HOME, COPILOT_HOME, XDG_CONFIG_HOME: as documented by each agent
```

### Precedence and enable state

```yaml
copilot plugin enable:   null, badged enable-state-undocumented, for the same
                         reason: the plugin reference documents the commands but
                         not the on-disk state
codex profile rows:      enabled null, badged profile-unselected. Which profile
                         a session runs under is a --profile argument, not a
                         file, so no scan can know it. [features] hooks in the
                         base config says nothing about a profile run, so
                         feature-off is never applied to a profile row
```

Codex `requirements.toml` and any managed or system Codex hook path are not
implemented: the config reference documents neither, and this plugin does not
guess a location.

Locations that an agent does not document are not guessed. A `.cursor/hooks.json`
on disk produces nothing, a `hooks.json` under an Antigravity CLI plugin
directory produces nothing because no Antigravity document describes that path,
and an event name outside an agent's documented set is still listed but marked
`unknown event` rather than silently normalized. Codex publishes no hook trust
or hash-pinning mechanism, so this plugin reports none; a test fails if the
words `trusted_hash` or `hooks.state` reappear in the adapters.

## Bounds

Files are opened with `O_NOFOLLOW` and `O_NONBLOCK` and must pass an `fstat`
regular-file check, so a symlinked config, FIFO, or device node is skipped
rather than followed or blocked on. Reads stop at 256 KiB per file, JSON and
TOML deeper than 12 levels are rejected, directory traversal is capped at 5
levels and 256 entries with symlinked directories skipped, and a scan stops at
128 sources and 600 rows, reporting `truncated`.

## Keys

Fileblade's shared `ArtifactTree` and `BladeSlot` own every navigation key, so
this pane behaves like every other Fileblade pane. This module adds one binding
and consumes nothing else.

```yaml
n:                         name the hook; Enter saves, Escape cancels   this module
j / k, Down / Up:          move                          ArtifactTree
h / l, Left / Right:       collapse or expand a branch   ArtifactTree
g / G:                     first row, last row           ArtifactTree
Home / End:                first row, last row           ArtifactTree
Ctrl+D / Ctrl+U:           half page                     ArtifactTree
PageDown / PageUp:         page                          ArtifactTree
/:                         search, Escape leaves it      ArtifactTree
f:                         open the filter popup         ArtifactTree
s:                         toggle sort on the metric     ArtifactTree
Enter, o:                  open the config file          ArtifactTree
r:                         reveal in the file tree       ArtifactTree
Escape:                    back out, return focus        ArtifactTree
Tab / Shift+Tab:           move between slots            ArtifactTree
Ctrl+Tab / Ctrl+Shift+Tab: cycle slot tabs               BladeSlot
Ctrl+PageDown / Ctrl+PageUp, Ctrl+] / Ctrl+[             BladeSlot
Alt+Z:                     collapse the slot             host
Shift+R:                   rescan                        this module
```

`blades/KeyPlan.js` handles `Shift+R` to rescan and `n` to name a hook.
Tree navigation and slot tab cycling remain host-owned.

## Lifecycle

Views observe the provider's shared inventory while open and expanded. The host
owns scanning, watches, cancellation and output bounds, and releases work when
no view observes it. Explicit apply/remove/restore operations use host mutation
services and durable recovery records, then refresh the shared inventory.
The helper reports capped output through its `truncated` field.

## State

The inventory command list writes nothing and never runs hooks. Explicit `apply` changes
agent configuration, `label` stores the user's display name, and
prepare/remove/restore support host-managed recovery. View settings and recovery
records remain with FileBlade after uninstall; prior agent changes remain too.

## Validation

```bash
LC_ALL=C omarchy plugin validate .
qmllint blades/Module.qml blades/KeyPlan.js Service.qml tests/tst_keyplan.qml
./tests/run
find . -path ./.git -prune -o -type l -print
git diff --check
```

## License

MIT. See `LICENSE`.

## Search syntax

The filter field is Fileblade's shared `PaneSearchField` with the FILES search
syntax: bare words match anywhere (case-insensitive), `"quoted text"` matches
exactly, `-word` excludes, `name:x` matches the row label only, and the
field keys shown in the placeholder (`agent, event, scope, type`) take exact comma-separated
values, negatable with a leading `-` (`event:PreToolUse -agent:codex`). Unknown keys are searched as
plain text.
