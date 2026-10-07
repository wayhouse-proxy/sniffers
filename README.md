# wayhouse sniffers

Official WASM sniffer modules for [wayhouse](https://github.com/wayhouse-proxy/wayhouse), and the
registry the wayhouse admin UI installs them from.

A **sniffer** is a small WebAssembly module that peeks at the first bytes of a connection or
datagram and returns a routing hint (a hostname or a tag) so a `sniffer` route can steer the
traffic. The proxy has no game-protocol code of its own; it lives here. (Sniffers are not
*plugins*: plugins are integrations with other systems and live in
[`wayhouse-proxy/plugins`](https://github.com/wayhouse-proxy/plugins).)

## Sniffers

| Sniffer | Recognises | Hint |
| ------- | ---------- | ---- |
| [`a2s`](sniffers/a2s) | Source-engine A2S query packets (CS:GO, TF2, Garry's Mod, Rust, ...) | key `a2s` |
| [`minecraft`](sniffers/minecraft) | Minecraft (>= 1.7) handshake; strips a Forge `\0FML\0` suffix | host (virtual host) |
| [`quic`](sniffers/quic) | QUIC Initial (v1, v2, drafts 29 to 34); decrypts it to read the TLS SNI | key `quic`, host when readable |
| [`wireguard`](sniffers/wireguard) | WireGuard handshake initiation | key `wireguard` |
| [`openvpn`](sniffers/openvpn) | OpenVPN client hard reset (a weak signal: list it after stronger sniffers) | key `openvpn` |
| [`raknet`](sniffers/raknet) | RakNet offline handshake (Minecraft Bedrock and other RakNet games) | key `raknet` |
| [`teamspeak3`](sniffers/teamspeak3) | TeamSpeak 3 `TS3INIT1` client init | key `teamspeak3` |
| [`regex_firstbytes`](sniffers/regex_firstbytes) | Your own literal hex/ASCII patterns, set in `settings.sniffers.modules[].config` | key from config |

**Handshake-only sniffers.** `quic`, `wireguard`, `openvpn`, `raknet` and `teamspeak3` recognise only a
flow's first datagram, so a session evicted by `idle_timeout_sec` cannot be routed again by them. See
the "Handshake-only sniffers" note in the wayhouse configuration guide (`docs/05-configuration.md`).

## Installing

- **From the admin UI.** The wayhouse UI lists this registry (its `index.json` on `main`) on the Sniffers
  page and installs a chosen version on every proxy: it downloads the module, checks size and sha256
  from the index (and the minisign signature when one is published), validates it, and only then
  uploads it. Registries other than this one are installed from at your own risk.
- **By hand.** Download `<name>.wasm` from a [release](https://github.com/wayhouse-proxy/sniffers/releases)
  and upload it through the admin API or UI, or drop it into `settings.sniffers.dir`.

Trust model in short: this repository only holds reviewed sniffers; every download is checked against
the index; signatures are optional for now and an unsigned module is shown as unsigned. The format and
checks are documented in [`docs/sniffers.md`](https://github.com/wayhouse-proxy/wayhouse/blob/main/docs/sniffers.md)
in the wayhouse repository.

## Layout

```
sniffers/<name>/          one crate per sniffer
  Cargo.toml              crate name == directory name; version == manifest version
  manifest.toml           what the registry shows and checks (see docs/sniffers.md)
  src/lib.rs
scripts/stage.py          checks manifests against crates and stages built modules in dist/
index.json                the registry index, written by the release workflow
```

Every sniffer depends on `wayhouse-sniffer-abi` from the wayhouse repository, pinned to an exact
commit in the root `Cargo.toml` (`[workspace.dependencies]`). That crate adds the `wayhouse.abi`
custom section the host checks: while the ABI major is 0 the host requires an exact minor match, so a
sniffer built for ABI 0.1 does not load on a proxy that speaks 0.2 and needs a rebuilt version.

## Develop

```sh
cargo test --workspace                                              # native unit tests
cargo build --release --target wasm32-unknown-unknown --workspace  # needs the wasm32 target
python3 scripts/stage.py                                            # manifest checks, writes dist/
```

CI additionally runs `cargo fmt`, `clippy -D warnings`, and the real registry validator
(`wayhouse-registry-gen`, built from the same wayhouse commit as the ABI crate) over the staged modules.

## Releasing

Run the **Release** workflow from the Actions tab on `main` (one sniffer, or `all`). For every sniffer
whose `<name>-v<version>` release does not exist yet it builds the module, signs it when the
`MINISIGN_SECRET_KEY` / `MINISIGN_PASSWORD` secrets are set, creates the release, and commits the
refreshed `index.json` to `main`. Published versions are immutable: existing releases are never
touched, and the index generator refuses a changed sha256 for a version it already lists. To ship a
change, bump `version` in both the sniffer's `Cargo.toml` and `manifest.toml`. If a run dies after a release is created but before its `.minisig` is attached, delete that release and its tag and run again (a rerun treats an existing release as published).

## License

MIT OR Apache-2.0, see [LICENSE-MIT](LICENSE-MIT) and [LICENSE-APACHE](LICENSE-APACHE).
