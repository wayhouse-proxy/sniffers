#!/usr/bin/env python3
"""Stage built sniffers for publishing.

For every `sniffers/<name>/` (or just the names given) check that the manifest agrees
with the crate and copy `manifest.toml` plus the built wasm into `dist/<name>/`, the
layout `wayhouse-registry-gen generate` reads. Every problem is reported, not just the
first. Run after `cargo build --release --target wasm32-unknown-unknown --workspace`.
"""
import argparse
import pathlib
import shutil
import sys
import tomllib


def check(root, name):
    """Return (errors, manifest_path, wasm_path) for one sniffer."""
    src = root / "sniffers" / name
    errors = []
    manifest_path = src / "manifest.toml"
    wasm = root / "target/wasm32-unknown-unknown/release" / (name.replace("-", "_") + ".wasm")
    try:
        manifest = tomllib.loads(manifest_path.read_text())
        cargo = tomllib.loads((src / "Cargo.toml").read_text())["package"]
    except (OSError, tomllib.TOMLDecodeError, KeyError) as e:
        return [f"{name}: cannot read manifest.toml or Cargo.toml: {e}"], None, None
    if manifest.get("name") != name:
        errors.append(
            f"{name}: manifest name {manifest.get('name')!r} must equal the directory name"
        )
    if cargo.get("name") != name:
        errors.append(f"{name}: crate name {cargo.get('name')!r} must equal the directory name")
    if manifest.get("version") != cargo.get("version"):
        errors.append(
            f"{name}: manifest version {manifest.get('version')} "
            f"differs from the crate version {cargo.get('version')}"
        )
    if not wasm.is_file():
        errors.append(f"{name}: built wasm not found at {wasm.relative_to(root)}")
    return errors, manifest_path, wasm


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=pathlib.Path, default=pathlib.Path("."))
    ap.add_argument("--out", type=pathlib.Path, default=None, help="default: <root>/dist")
    ap.add_argument("names", nargs="*", help="sniffers to stage (default: all)")
    args = ap.parse_args()
    root = args.root.resolve()
    out = args.out or root / "dist"

    available = sorted(p.name for p in (root / "sniffers").iterdir() if p.is_dir())
    unknown = [n for n in args.names if n not in available]
    if unknown:
        print(f"unknown sniffer(s): {', '.join(unknown)}", file=sys.stderr)
        return 1
    names = args.names or available

    errors, staged = [], []
    for name in names:
        errs, manifest, wasm = check(root, name)
        errors += errs
        if not errs:
            staged.append((name, manifest, wasm))
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    for name, manifest, wasm in staged:
        d = out / name
        d.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(manifest, d / "manifest.toml")
        shutil.copyfile(wasm, d / f"{name}.wasm")
        print(f"staged {name} ({wasm.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
