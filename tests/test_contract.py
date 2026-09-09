from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOCKET = "data-goblin.fileblade/blade"
HOST_ID = "data-goblin.fileblade"
BUILTIN_OPEN = re.compile(r"(?<![.\w])open\(")

def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")

def manifest_contract() -> None:
    manifest = json.loads(read("manifest.json"))
    assert manifest["schemaVersion"] == 1
    assert manifest["id"] == "data-goblin.fileblade-hooks"
    for key in ("name", "version", "author", "description", "license"):
        assert isinstance(manifest[key], str) and manifest[key], key
    assert manifest["kinds"] == ["service"]
    assert (ROOT / manifest["entryPoints"]["service"]).is_file()
    modules = manifest["extensions"][SOCKET]
    assert isinstance(modules, list) and len(modules) == 1
    module = modules[0]
    assert module["hostContract"] == 3
    assert module["id"] == "hooks" and module["singleton"] is True
    assert (ROOT / module["entry"]).is_file()
    helper = manifest["extensions"]["data-goblin.fileblade/helper"][0]
    assert helper["id"] == "inventory" and helper["entry"] == "bin/agent-hooksctl"
    assert helper["read"] == ["list", "recovery-list"]
    assert helper["write"] == ["apply", "remove-prepared", "restore", "label", "prepare-remove", "discard"]

def qml_contract() -> None:
    module = read("blades/Module.qml")
    lines = module.splitlines()
    for index, line in enumerate(lines):
        if line.strip().startswith("Text {"):
            window = lines[index + 1:index + 12]
            assert any("textFormat: Text.PlainText" in entry for entry in window), f"line {index + 1}"
    for shared in ("PaneView", "PaneHeader", "PaneSearchField", "ArtifactTree"):
        assert f'context.ui.url("{shared}")' in module, shared
    assert "inventory ? inventory.anchorPath" in module
    assert "inventory ? inventory.projectArguments" in module
    assert "function entryPath(entry)" in module
    for option in ("caseSensitive", "regex"):
        assert f'item.{option} = module.{option}' in module
        assert f'item.{option} = Qt.binding(function() {{ return module.{option} }})' in module
    assert "item.optionsToggled.connect" in module
    assert "item.showOptions = true" in module
    assert "item.editPathFor = function(entry) { return module.entryPath(entry) }" in module
    assert "item.fileActionsFor = function(entry) { return false }" in module
    assert "if (entry.path) return String(entry.path)" in module
    assert "var path = entryPath(entry)" in module
    assert "entry.source && entry.source.path ? String(entry.source.path)" in module
    assert "readonly property var items: inventory ? inventory.items" in module
    for shared in ("busy", "truncated", "applying", "loadError", "applyError", "watchError"):
        assert f"inventory.{shared}" in module, shared
    for duplicate in ("boundedRows", "boundedMetrics", "scanProcess", "applyProcess", "rescanTimer"):
        assert duplicate not in module, duplicate
    assert "syntaxKeys" not in module
    assert "property var context: null" in module and "required property" not in module
    assert 'context.metrics.options(["off", "agents", "status", "type", "updated", "created", "summary"])' in module
    assert 'label: "Tokens' not in module and 'kind: "number"' not in module
    assert "readonly property var view: viewLoader.item" in module
    assert 'setSource(module.context.ui.url("ArtifactBin"), { service: module.files })' in module
    assert 'item.module = "hooks"\n      item.context = Qt.binding(function() { return module.context })' in module
    assert "item.helperRoute = Qt.binding(" in module
    assert "item.removalArguments = function(entry)" in module
    assert "binProcess" not in module and "binCallback" not in module
    assert "bin.item.mergeRows(items, binned, function(entry) { return [module.agentGroup(entry), module.eventGroup(entry)] })" in module
    assert "position: Math.max(0, allRows().indexOf(entry))" in module
    assert "groups: [agentGroup(entry), eventGroup(entry)]" in module
    assert "metrics: entry.metrics" in module
    assert 'item.defaultMetric = "agents"' in module and "item.options = module.metricOptions" in module
    assert "item.view = Qt.binding(function() { return module.view })" in module
    assert "item.installedAgents = Qt.binding(" in module and "files.installedAgents" in module
    assert "item.appliedAgents = function(entry) { return module.appliedAgents(entry) }" in module
    assert "entry.appliedAgents" in module and "item.specialMetricValue" in module
    assert "item.filterRequested.connect" in module and "header.item.openFilter()" in module
    assert "item.agentToggled.connect" in module and "item.agentsAllRequested.connect(function(entry, on) { module.applyAll(entry, on) })" in module
    assert '["--project", anchorPath, "--id", String(entry.id), "--state", state, "--json"]' in module
    assert 'inventory.mutate("apply", command)' in module
    assert 'command.push("--agent", String(agents[i]))' in module
    assert '"Applying…"' in module and "readonly property string status: statusText()" in module
    assert "item.status = Qt.binding(function() { return module.status })" in module
    assert module.count('"Applying…"') == 1 and "(capped)" in module
    assert "function applyAll(entry, on)" in module and "!on && agentId !== own" in module
    for removed in ("metricKey", "setMetric", "restoreMetric", "metricChosen", "metricAllowed",
                    'context.state.set("metric"', "item.leafBadge"):
        assert removed not in module, removed
    assert ".some(" not in module and "for (var " in module
    assert "DESC" not in module and "showDescriptions" not in module
    assert "item.tabIndex = Qt.binding(function() { return module.context.tabIndex })" in module
    assert "item.reservedLeft" in module and "item.reservedRight" in module
    assert "context.collapsed === true" in module and "context.bladeOpen !== false" in module
    assert "Component.onDestruction: if (attachedProvider) attachedProvider.detach(attachedContext)" in module
    assert "onActiveChanged: syncProvider()" in module and "onProviderChanged: syncProvider()" in module
    assert "active: module.active" in module
    assert "height: item && item.visible ? Style.space(32) : 0" in module
    assert "item.context = Qt.binding(function() { return module.context })" in module
    assert "property bool truncated" in module and "(capped)" in module
    assert "KeyPlan.moduleAction(event.key, event.modifiers, Qt)" in module
    assert 'action === "rescan"' in module and 'action === "name"' in module
    assert module.count("Keys.onPressed") == 1
    for owned in ("Qt.Key_PageDown", "Qt.Key_PageUp", "Qt.Key_Home", "Qt.Key_End",
                  "Qt.Key_Tab", "Qt.Key_Backtab", "Qt.Key_G", "Qt.Key_Z"):
        assert owned not in module, owned
    for removed in ("pageBy", "jumpTo", "runSupplementary", "trust"):
        assert removed not in module, removed
    service = read("Service.qml")
    assert "property var shell: null" in service and "required property" not in service
    assert 'context.ui.url("ArtifactInventory")' in service
    provider = (ROOT / "Provider.qml").read_text(encoding="utf-8")
    assert 'maximumItems: 1000, scanArguments: ["--watch"]' in provider
    assert 'observers: Qt.binding(function() { return provider.observers })' in provider

def keyplan_contract() -> None:
    plan = read("blades/KeyPlan.js")
    assert plan.lstrip().startswith(".pragma library")
    for name in ("isTabCycle", "moduleAction"):
        assert f"function {name}(" in plan, name
    for removed in ("supplementaryAction", "hostAction", "coverage", "PAGE_ROWS"):
        assert removed not in plan, removed
    assert "Qt." not in plan and "import " not in plan
    for chord in ("Key_Tab", "Key_Backtab", "Key_PageUp", "Key_PageDown",
                  "Key_BracketLeft", "Key_BracketRight"):
        assert chord in plan, chord
    returned = {value for value in re.findall(r'return "([^"]*)"', plan) if value}
    assert returned == {"rescan", "name"}, returned

def helper_contract() -> None:
    helper = ROOT / "bin" / "agent-hooksctl"
    assert helper.is_file() and helper.stat().st_mode & 0o111
    for source in sorted((ROOT / "agent_hooks").glob("*.py")):
        text = source.read_text(encoding="utf-8")
        for forbidden in ("subprocess", "socket", "urllib", "eval(", "exec(", "os.system", "__import__"):
            assert forbidden not in text, f"{source.name}: {forbidden}"
        assert not BUILTIN_OPEN.search(text), f"{source.name} uses builtin open()"
        assert ".write_text(" not in text and ".write_bytes(" not in text
        if source.name not in ("apply.py", "recovery.py"):
            for writer in ("os.replace", "os.rename", "os.write(", "O_WRONLY", "O_CREAT", "os.unlink", "mkdir("):
                assert writer not in text, f"{source.name}: {writer}"
    recovering = read("agent_hooks/recovery.py")
    for required in ("O_EXCL", "O_NOFOLLOW", "0o600", "0o700", "MAX_RECORD_BYTES", "RESTORED_LIFETIME_SECONDS", "MAX_SCANNED_RECORDS", "MAX_STORE_BYTES", "O_NONBLOCK", "dir_fd=parent"):
        assert required in recovering, required
    applying = read("agent_hooks/apply.py")
    for required in ("def write_atomic(", "Snapshot.read(path, MAX_FILE_BYTES)", "snapshot.write(payload)", "json.dumps(document, indent=2",
                     "not strict JSON", "from .events import mapped_event", "WRITER_AGENTS",
                     "CODE_HOSTED_AGENTS"):
        assert required in applying, required
    mapping = read("agent_hooks/events.py")
    for required in ("def mapped_event(", "def canonical(", "CANONICAL_EVENTS", '"antigravity": "Stop"',
                     '"copilot-cli": "agentStop"', '"copilot-cli": "preCompact"'):
        assert required in mapping, required
    assert "strip_comments" not in applying and "allow_comments=True" in applying
    command_line = read("agent_hooks/cli.py")
    for flag in ('"--id"', '"--agent", action="append", required=True', 'choices=("on", "off")', '"--json"'):
        assert flag in command_line, flag
    assert "from . import apply" in command_line and command_line.index("def run_apply") < command_line.index("from . import apply")
    assert 'restoring.add_argument("--record-id", required=True)' in command_line
    assert 'restoring.add_argument("--payload-stdin", action="store_true")' in command_line
    assert 'add_argument("--payload")' not in command_line
    adapters = read("agent_hooks/adapters.py")
    for invented in ("trusted_hash", "hooks.state", "codex_trust", "orphan_trust", "antigravity-cli",
                     "requirements.toml"):
        assert invented not in adapters, invented
    for documented in ("policy.d", "installed-plugins", "_direct",
                       '("hooks", "hooks.json")',
                       ".config.toml", "profile-unselected"):
        assert documented in adapters, documented
    assert "COPILOT_PASCAL_ALIASES" in adapters and "COPILOT_KNOWN" in adapters
    assert "policyOwnerUid" in adapters
    discovery_source = read("agent_hooks/discovery.py")
    assert 'etc_root: str = "/etc"' in discovery_source
    assert "policy_owner_uid: int = 0" in discovery_source
    safeio = read("agent_hooks/safeio.py")
    assert "def secure_metadata(" in safeio and "S_IWGRP | stat.S_IWOTH" in safeio
    assert "MAX_STDOUT_BYTES = 1024 * 1024" in safeio and "def fit_payload(" in safeio
    assert "O_NOFOLLOW" in safeio and "O_NONBLOCK" in safeio
    assert "MAX_FILE_BYTES" in safeio and "MAX_JSON_DEPTH" in safeio
    assert "MAX_TRAVERSAL_DEPTH" in safeio and "MAX_ITEMS_PER_SOURCE" in safeio
    assert "entry.is_symlink()" in safeio
    assert "def artifact_metrics(" in safeio and "def creation_time(" in safeio
    assert "countable = len(encoded) <= MAX_FILE_BYTES" in safeio
    assert "metadata = target.lstat()" in safeio

def docs_contract() -> None:
    readme = " ".join(read("docs/agent-written/README.md").split())
    assert "Omarchy Fileblade" in readme and HOST_ID in readme
    assert "fileblade-hooks" in readme
    assert "installed and enabled first" in readme
    assert "redact" in readme.lower()
    assert "hook payload" in readme.lower() and "source config" in readme.lower()
    for documented in ("agent-hooksctl apply", "--state on|off", "agentStop",
                       "timeoutSec", "hooks/hooks.json", "strict JSON", "Left click",
                       "Right click", "since", "until", "min", "max", "appliedAgents", "list writes nothing"):
        assert documented in readme, documented
    assert (ROOT / "LICENSE").is_file()

def main() -> None:
    manifest_contract()
    qml_contract()
    keyplan_contract()
    helper_contract()
    docs_contract()
    print("contract tests: ok (5 groups)")

if __name__ == "__main__":
    main()
