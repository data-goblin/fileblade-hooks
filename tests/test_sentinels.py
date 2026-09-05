from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

import fixtures
from agent_hooks import discovery

EXECUTION_EVENTS = (
    "subprocess.Popen", "os.system", "os.exec", "os.posix_spawn", "os.fork", "os.spawn",
    "pty.spawn", "shutil.rmtree", "os.remove", "os.rename", "os.rmdir", "os.truncate",
)
NETWORK_EVENTS = ("socket.connect", "socket.getaddrinfo", "socket.bind", "urllib.Request", "ftplib.connect")
WRITE_EVENTS = ("os.mkdir", "os.chmod", "os.fchmod", "os.symlink", "os.link", "os.utime", "shutil.copyfile",
                "shutil.move", "tempfile.mkstemp")
FORBIDDEN_IMPORTS = ("subprocess", "socket", "urllib", "http.client", "ftplib", "asyncio", "requests")
CREDENTIAL_HINTS = ("credentials", ".netrc", "id_rsa", "token", "keyring", "secrets.json")

ETC = {"root": ""}

def scan(home: Path, project: Path) -> dict:
    import os
    return discovery.collect(str(project), str(home), environ={"HOME": str(home)},
                             etc_root=ETC["root"] or "/etc", policy_owner_uid=os.getuid())

def serialized(home: Path, project: Path) -> tuple[str, dict]:
    document = scan(home, project)
    return json.dumps(document, ensure_ascii=False), document

def write_flags(arguments: object) -> bool:
    import os
    flags = arguments[2] if isinstance(arguments, tuple) and len(arguments) > 2 else None
    if not isinstance(flags, int):
        return False
    return bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))

def test_no_execution_or_network_audit_events(home: Path, project: Path) -> None:
    observed: list[str] = []
    writes: list[str] = []

    def hook(event: str, arguments: object) -> None:
        if event.startswith(EXECUTION_EVENTS) or event.startswith(NETWORK_EVENTS):
            observed.append(event)
        if event.startswith(WRITE_EVENTS) or (event == "open" and write_flags(arguments)):
            writes.append(event)

    sys.addaudithook(hook)
    import agent_hooks.apply
    scan(home, project)
    assert observed == [], f"forbidden runtime events: {sorted(set(observed))}"
    assert writes == [], f"list must never write: {sorted(set(writes))}"

def test_list_never_imports_the_writer() -> None:
    import importlib
    for name in list(sys.modules):
        if name.startswith("agent_hooks"):
            del sys.modules[name]
    fresh = importlib.import_module("agent_hooks.cli")
    fresh.build_parser().parse_args(["list", "--json"])
    assert "agent_hooks.apply" not in sys.modules
    for name in ("discovery.py", "adapters.py", "events.py", "redaction.py", "safeio.py"):
        text = (ROOT / "agent_hooks" / name).read_text(encoding="utf-8")
        assert "import apply" not in text and ".apply import" not in text, name

def test_policy_and_plugin_rows_are_covered(home: Path, project: Path) -> None:
    document = scan(home, project)
    copilot = [row for row in document["items"] if row["agent"] == "copilot-cli"]
    scopes = {row["scope"] for row in copilot}
    assert {"policy", "plugin", "user", "project"} <= scopes, scopes

def test_no_forbidden_imports_in_package() -> None:
    for source in sorted((ROOT / "agent_hooks").glob("*.py")):
        text = source.read_text(encoding="utf-8")
        for module in FORBIDDEN_IMPORTS:
            assert f"import {module}" not in text, f"{source.name} imports {module}"
        assert "eval(" not in text and "exec(" not in text, source.name
        assert "__import__" not in text, source.name

def test_no_module_is_loaded_that_can_execute() -> None:
    for module in ("subprocess", "socket", "urllib.request", "http.client"):
        assert module not in sys.modules or module == "socket", module

def test_ctypes_is_limited_to_read_only_statx() -> None:
    for source in sorted((ROOT / "agent_hooks").glob("*.py")):
        text = source.read_text(encoding="utf-8")
        if "import ctypes" not in text:
            continue
        assert source.name == "safeio.py"
        assert ".statx" in text and "CDLL(None" in text
        for forbidden in ("dlopen", "dlsym", "system", "exec"):
            assert f".{forbidden}" not in text

def test_output_contains_no_canary_secret(home: Path, project: Path) -> None:
    text, _ = serialized(home, project)
    for canary in fixtures.CANARIES:
        assert canary not in text, f"leaked canary: {canary}"

def test_output_contains_no_command_shaped_strings(home: Path, project: Path) -> None:
    text, document = serialized(home, project)
    assert "curl " not in text and "echo " not in text
    assert "https://" not in text and "http://" not in text
    assert "Authorization" not in text
    for row in document["items"]:
        summary = row["summary"]
        for banned in ("command", "bash", "powershell", "url", "headers", "env", "prompt", "cwd"):
            assert banned not in summary, banned
        assert set(summary) == {
            "label", "labelSource", "type", "fields", "digest", "payloadBytes", "envCount", "matcher",
            "timeoutSeconds", "hasCondition",
        }
        assert "/" not in summary["label"] and len(summary["label"]) <= 80

def test_field_inventory_is_names_only(home: Path, project: Path) -> None:
    _, document = serialized(home, project)
    for row in document["items"]:
        for name in row["summary"]["fields"]:
            assert isinstance(name, str) and len(name) <= 40
            assert "/" not in name and " " not in name

def test_paths_are_config_locations_not_operands(home: Path, project: Path) -> None:
    _, document = serialized(home, project)
    for row in document["items"]:
        path = row["source"]["path"]
        assert fixtures.CANARY_PATH not in path
        for hint in CREDENTIAL_HINTS:
            assert hint not in path.lower(), f"credential-shaped source: {path}"

def test_digest_is_not_reversible_material(home: Path, project: Path) -> None:
    _, document = serialized(home, project)
    for row in document["items"]:
        digest = row["summary"]["digest"]
        assert digest == "" or re.fullmatch(r"[0-9a-f]{8}", digest), digest

def test_counts_only_for_code_hosted(home: Path, project: Path) -> None:
    _, document = serialized(home, project)
    for row in document["items"]:
        if row["supportStatus"] != "code-hosted":
            continue
        assert isinstance(row["entries"], int)
        assert row["summary"]["payloadBytes"] == 0

def main() -> None:
    with tempfile.TemporaryDirectory() as sandbox:
        home = Path(sandbox) / "home"
        project = Path(sandbox) / "work" / "repo"
        etc = Path(sandbox) / "etc"
        ETC["root"] = str(etc)
        fixtures.build_all(home, project, etc)
        checks = [
            test_policy_and_plugin_rows_are_covered,
            test_no_execution_or_network_audit_events,
            test_output_contains_no_canary_secret,
            test_output_contains_no_command_shaped_strings,
            test_field_inventory_is_names_only,
            test_paths_are_config_locations_not_operands,
            test_digest_is_not_reversible_material,
            test_counts_only_for_code_hosted,
        ]
        passed = 0
        for check in checks:
            check(home, project)
            passed += 1
    test_no_forbidden_imports_in_package()
    test_ctypes_is_limited_to_read_only_statx()
    test_no_module_is_loaded_that_can_execute()
    test_list_never_imports_the_writer()
    print(f"sentinel tests: ok ({passed + 4} checks)")

if __name__ == "__main__":
    main()
