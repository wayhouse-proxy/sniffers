import hashlib
import pathlib
import tempfile
import unittest

import claim


class T(unittest.TestCase):
    def test_claim_names_name_version_abi_and_hash(self):
        with tempfile.TemporaryDirectory() as t:
            t = pathlib.Path(t)
            (t / "manifest.toml").write_text('name = "demo"\nversion = "0.1.1"\nabi = "0.1"\n')
            wasm = b"\0asm"
            (t / "demo.wasm").write_bytes(wasm)
            want = f"wayhouse-v1 sniffer demo 0.1.1 0.1 {hashlib.sha256(wasm).hexdigest()}"
            self.assertEqual(claim.claim(t / "manifest.toml", t / "demo.wasm"), want)


if __name__ == "__main__":
    unittest.main()
