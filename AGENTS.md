# AGENTS.md

Guidance for any AI coding agent working in this repository, following the [agents.md](https://agents.md) convention. Humans: see [`CONTRIBUTING.md`](CONTRIBUTING.md).

## What this repo is

The official **sniffers** for [wayhouse](https://github.com/wayhouse-proxy/wayhouse): small WASM modules that peek at the first bytes of a connection or datagram and return a routing hint. It is also the registry the wayhouse admin UI installs them from (`index.json`). Sniffers are not *plugins* (those live in [`wayhouse-proxy/plugins`](https://github.com/wayhouse-proxy/plugins)). The ABI crate (`wayhouse-sniffer-abi`) and the registry generator/validator (`wayhouse-registry-gen`) live in the wayhouse repository; the format is documented in its `docs/sniffers.md`.

## Layout

```
Cargo.toml                workspace; members = sniffers/*; pins wayhouse-sniffer-abi by git rev
rust-toolchain.toml       pinned toolchain
sniffers/<name>/          one crate per sniffer: Cargo.toml, manifest.toml, src/lib.rs
scripts/stage.py          checks manifests against crates, stages built modules in dist/
scripts/stage_test.py     tests for stage.py
index.json                the registry index; written by the release workflow, never by hand
.github/workflows/        ci.yml (checks, ci-ok gate), release.yml (manual release)
.github/actions/registry-gen/  builds the registry tool from the pinned wayhouse rev
```

`sniffers/a2s` is the smallest sniffer; copy it when adding one.

## Commands

Run these before every push (CI runs the same, plus the real registry validator):

```sh
python3 scripts/stage_test.py
cargo fmt --all
cargo clippy --locked --workspace --all-targets -- -D warnings
cargo test --locked --workspace
cargo build --locked --release --target wasm32-unknown-unknown --workspace   # needs the wasm32-unknown-unknown target
python3 scripts/stage.py
```

## Rules

- **Never skip, disable or weaken a test or CI check** to get green. Fix the cause.
- **Crate name == directory name == manifest `name`.** The manifest `version` equals the crate `version`; the manifest `abi` is the `major.minor` that `wayhouse-sniffer-abi` declares. `stage.py` and the registry validator enforce this.
- **Published versions are immutable.** Any behaviour change needs a version bump in both `Cargo.toml` and `manifest.toml`. Do not edit `index.json` by hand and do not touch existing releases or tags.
- **ABI bumps:** the `wayhouse-sniffer-abi` `rev` in the root `Cargo.toml` is the single place to bump; rebuild and re-test every sniffer, because the host requires an exact ABI minor match while the major is 0.
- **No imports, at most 8 MiB, no WASI.** Core WebAssembly only.
- **Tests required** and native (`cargo test`): no network, no clock. Cover the recognised packet, near misses, truncated input and hostile input. Sniffers must be bounded and linear in the input.
- **Do not edit `CODE_OF_CONDUCT.md`** or the licence files unless asked. Releases are cut by a maintainer through the **Release** workflow; contributors and agents do not tag.

## Git and PRs

- Work on a branch, never directly on `main`.
- PR titles are conventional commits (`feat(quic): ...`, `fix: ...`, `docs: ...`); the PR title becomes the squash commit message.
- `main` is protected by a merge queue: once CI is green, queue with `gh pr merge <N> --squash --auto`. The required check is `ci-ok`.
- Docs-only PRs need no extra review once CI is green; code PRs get a human review.
