#!/usr/bin/env python3
"""Tests for stage.py (run: python3 scripts/stage_test.py)."""
import pathlib
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
STAGE = HERE / "stage.py"

MANIFEST = """\
name = "{name}"
description = "d"
license = "MIT OR Apache-2.0"
version = "{mver}"
abi = "0.1"
min_proxy = "0.1.0"

[limits]
max_memory_bytes = 16777216
call_timeout_ms = 20
"""
CARGO = '[package]\nname = "{name}"\nversion = "{cver}"\n'


def make(root, name="my-sniffer", mver="0.1.0", cver="0.1.0", wasm=True, dirname=None):
    d = root / "sniffers" / (dirname or name)
    d.mkdir(parents=True)
    (d / "manifest.toml").write_text(MANIFEST.format(name=name, mver=mver))
    (d / "Cargo.toml").write_text(CARGO.format(name=name, cver=cver))
    if wasm:
        out = root / "target/wasm32-unknown-unknown/release"
        out.mkdir(parents=True, exist_ok=True)
        (out / (name.replace("-", "_") + ".wasm")).write_bytes(b"\0asm")


def run(root, *args):
    return subprocess.run(
        [sys.executable, str(STAGE), "--root", str(root), *args],
        capture_output=True, text=True,
    )


class StageTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_stages_manifest_and_wasm_under_the_sniffer_name(self):
        make(self.root)
        r = run(self.root)
        self.assertEqual(r.returncode, 0, r.stderr)
        d = self.root / "dist/my-sniffer"
        self.assertEqual((d / "my-sniffer.wasm").read_bytes(), b"\0asm")
        self.assertTrue((d / "manifest.toml").exists())

    def test_version_mismatch_between_manifest_and_cargo_fails(self):
        make(self.root, mver="0.2.0", cver="0.1.0")
        r = run(self.root)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("my-sniffer", r.stderr)
        self.assertIn("version", r.stderr)

    def test_manifest_name_must_match_the_directory(self):
        make(self.root, name="other", dirname="my-sniffer")
        r = run(self.root)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("directory", r.stderr)

    def test_missing_wasm_fails_and_names_the_sniffer(self):
        make(self.root, wasm=False)
        r = run(self.root)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("my-sniffer", r.stderr)
        self.assertIn("wasm", r.stderr)

    def test_reports_every_failure_not_just_the_first(self):
        make(self.root, name="aaa", wasm=False)
        make(self.root, name="bbb", wasm=False)
        r = run(self.root)
        self.assertIn("aaa", r.stderr)
        self.assertIn("bbb", r.stderr)

    def test_names_limit_the_set(self):
        make(self.root, name="aaa")
        make(self.root, name="bbb", wasm=False)
        r = run(self.root, "aaa")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse((self.root / "dist/bbb").exists())

    def test_unknown_name_fails(self):
        make(self.root)
        self.assertNotEqual(run(self.root, "nope").returncode, 0)


if __name__ == "__main__":
    unittest.main()
