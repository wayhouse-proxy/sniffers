#!/usr/bin/env python3
"""Print the minisign trusted comment wayhouse requires on a sniffer signature.

`claim.py <manifest.toml> <name>.wasm` prints `wayhouse-v1 sniffer <name> <version> <abi> <sha256>`:
the signature names the artifact it covers, so it cannot be replayed under another name or
version (wayhouse#594). Pass the result to `minisign -S -t`.
"""
import hashlib
import pathlib
import sys
import tomllib


def claim(manifest_path, wasm_path):
    m = tomllib.loads(pathlib.Path(manifest_path).read_text())
    sha = hashlib.sha256(pathlib.Path(wasm_path).read_bytes()).hexdigest()
    return f"wayhouse-v1 sniffer {m['name']} {m['version']} {m['abi']} {sha}"


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    print(claim(*sys.argv[1:]))
