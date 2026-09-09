# Hooks architecture

Hooks supplies redacted semantic rows to FileBlade's `ArtifactTree`. The tree
owns navigation, grouping, filtering, metrics and source-file actions. The bin
receives the same blade context, so tree and confirmation dialogs share key
release and repeat state. A hook row cannot rename or trash its whole source.

The provider service owns FileBlade's shared `ArtifactInventory`; visual panes
attach as observers. Discovery, metrics bounds, invalidation, helper transport
and ordinary apply actions use that runtime. The last pane closing stops reads
and watches; an accepted apply retains its original project and finishes without
the pane. The declared native helper supplies bounded watch plans for source
parents, nested directories and symlink targets. `list --watch` includes these
native directories for private host transport; normal listing omits them.

Row IDs bind the native source path, event, group/entry position and complete
definition, including extension fields. A stale row cannot select a replacement
definition. Discovery addresses up to 200 entries per group without collisions.

Copying between agents uses a portable command representation. Undo does not:
new recovery records preserve the original entry, group fields, named group and
position. Removing one duplicate leaves the others intact. Restore checks the
affected event's before/after fingerprints, preserves unrelated settings and
other events, and refuses a conflicting event or retargeted source symlink.
Old portable recovery records remain readable, but fields absent from those
records cannot be recovered.

Writes require strict JSON with unique object members. The shared native writer
compares the captured file identity and original bytes before publication. It
uses private staging, durable recovery intents and no-replace publication;
existing permission bits and source symlinks are preserved, and new files are
private. Intervening edits or replacement entries are refused.

`tests/run` covers discovery, redaction, copying, exact undo, stale identities,
conflicts, write failures, native paths through the core bin, keyboard contracts
and read-only helper imports. The live VM checks the shared confirmation path.

Removal and restore belong to the core backend, not the visual pane. The read
method `prepare-remove` captures exact recovery data; `remove-prepared` rechecks
that data before writing. Core validates and durably stores the complete bounded
record first. Closing a pane cannot abandon completion. Interrupted or uncertain
removal keeps the record, and idempotent restore removes it only after success.
The stored helper route also supports restore from global Trash without a pane.

A restore writes only where a recorded removal came from. Removal mints its own
recovery record under the user's state directory, private to the user, and
reports the identifier; `restore` accepts a payload only when it matches one of
those records, takes the destination from the record rather than from the
payload, and refuses any path that discovery does not know as a hook
configuration file for that agent, with every discovered source classified the
same way whether it arrives through the shared reader or an adapter of its own.
A payload naming an arbitrary file is refused without writing. The record also
carries the project, home and policy roots the removal was taken in, so a
restore reaches the same sources even when the caller passes none. Preparing and
then removing reuse one record, the record is durable before the source is
touched, and a full store refuses a new removal rather than evicting an unused
undo. A confirmed restore marks its record used, which frees its place while a
repeat restore still answers; used records are dropped after a week and unused
ones are kept for ten years, the widest bin retention the core allows. Sixty-four
unused removals is the limit. The earlier portable payload format, which carried its own
destination, is gone, so records prepared before this change cannot be replayed;
the removal itself is still listed in the core bin.

This file was written by an agent.

## Provider ownership and host availability

The blade contribution declares `provider: "Provider.qml"`. FileBlade creates
one nonvisual provider per enabled extension identity and shares it across its
views. It supplies `providerId`, the canonical absolute `providerRoot`, `files`,
and `inventoryComponentUrl` at construction. The provider exposes `inventory`,
`error`, `observers`, `viewCount`, `attach(context)`, `detach(context)`, and
`shutdown()`. Construction stays idle. Duplicate attachment is harmless, the
last detach suspends the shared inventory, and shutdown unloads it and refuses
late attachments. Existing inventory options and module contract 2 are preserved.

`Service.qml` resolves its directory from its own QML URL, even when the shell
strips the manifest's source directory. It lazily delegates to the same provider
only when an older FileBlade calls attach. The new host owns its provider directly,
so its companion Service never creates a second inventory. A legacy companion
without provider metadata still requires its actual old-shell service; a new
host on a restricted shell must request an extension update instead of loading
that old Service itself. Updating companions alone cannot repair an old core on
the restricted shell.

The missing-host card no longer inspects foreign registry entries.
`bin/fileblade-host-status` reads `omarchy plugin list --json`, validates unique
IDs and Boolean enabled states, then checks the enabled host with
`omarchy-shell data-goblin.fileblade status`. Each command has a two-second
deadline, 128 KiB stdout and 4 KiB stderr limits, and process-group cleanup.
Listings are limited to 512 rows; the helper returns only the four known companion
names and states. It reads no agent configuration and downloads nothing.

Missing, disabled, starting, ready, and unknown states stay distinct. Only a
confirmed disabled host offers the existing explicit Enable action. Starting
or failed checks never offer installation or enablement. The first enabled
companion in a successful listing owns the card. Polling backs off to 30 seconds,
and dismissal stops checks until the next shell start. This is presentation;
FileBlade's catalog separately controls permission to load providers and helpers.

The QML lifecycle and guard tests plus the standalone host-check tests are part
of `tests/run`. They cover cold creation, shared observers, last detach, terminal
shutdown, stripped manifests, both provider ownership paths, unavailable commands,
malformed authority, output limits and timeouts. User-visible expectation: an
enabled responding FileBlade produces no missing-host card on either shell API.
