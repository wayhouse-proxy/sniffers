## What and why

<!-- One or two sentences. Link the issue with "Closes #N" if there is one. -->

## Checklist

- [ ] PR title is a conventional commit (`feat(quic): ...`, `fix: ...`, `docs: ...`)
- [ ] `cargo fmt --all`, `cargo clippy --workspace --all-targets -- -D warnings` and `cargo test --workspace` pass
- [ ] New or changed sniffer: wasm build and `python3 scripts/stage.py` pass
- [ ] Behaviour change: `version` bumped in both `Cargo.toml` and `manifest.toml`
- [ ] Tests cover the recognised packet, near misses, truncated and hostile input
- [ ] README table updated if a sniffer was added
