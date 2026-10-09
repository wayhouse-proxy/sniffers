# Contributing a sniffer

Thanks for helping. A sniffer is one directory, `sniffers/<name>/`, with a crate and a manifest.

## Rules

- **Licence.** `MIT OR Apache-2.0`, like the rest of the repository.
- **Name.** Letters, digits, `-` and `_`. The directory, the crate (`[package] name`) and the
  manifest `name` are identical.
- **ABI.** Depend on `wayhouse-sniffer-abi` (`wayhouse-sniffer-abi = { workspace = true }`) and build
  with `crate-type = ["cdylib", "lib"]`. The manifest `abi` must be the `major.minor` that crate
  declares; the registry validator rejects a module whose `wayhouse.abi` section disagrees.
- **Manifest.** `name`, `description`, `license`, `version`, `abi`, `min_proxy`, `[limits]`
  (`max_memory_bytes`, `call_timeout_ms`), and optionally `config` (documentation of the per-module
  config string) and `homepage`. Unknown keys are an error. The crate `version` equals the manifest
  `version`; versions are independent SemVer per sniffer.
- **No imports.** The module is core WebAssembly with no WASI and no host imports, at most 8 MiB.
- **Tests required.** Unit tests run natively with `cargo test`. No network and no clock in tests.
  Cover the recognised packet, near misses, truncated input, and (if you parse) hostile input.
- **Bounded work.** The host enforces a wall-clock timeout and a memory cap per call. Keep the
  sniffer allocation-light and linear in the input.
- **Review.** Official sniffers are reviewed by a maintainer before merge: protocol claims are
  checked against the specification or captured traffic, and the code for anything surprising.

## Workflow

1. Copy an existing sniffer (`sniffers/a2s` is the smallest) and edit it.
2. `cargo fmt --all && cargo clippy --workspace --all-targets -- -D warnings && cargo test --workspace`
3. `cargo build --release --target wasm32-unknown-unknown --workspace && python3 scripts/stage.py`
4. Open a pull request. CI runs the same checks plus the real registry validator.

A maintainer cuts the release (see [Releasing](README.md#releasing)); contributors do not tag.

## External registries

You do not need to be merged here to share a sniffer: anyone can publish an `index.json` in the
same format (see `docs/sniffers.md` in the wayhouse repository) and users can add it by URL in the
admin UI. Registries other than the official one are installed from **at the user's own risk**, and
the UI says so on every install.

## Code of conduct

Be kind and constructive. The [Code of Conduct](CODE_OF_CONDUCT.md) applies to issues, pull requests and every other project space.
