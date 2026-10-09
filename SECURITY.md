# Security policy

## Reporting a vulnerability

Please do not open a public issue for a security problem. Report it privately through a
[GitHub security advisory](https://github.com/wayhouse-proxy/sniffers/security/advisories/new)
on this repository. Include what you found, how to reproduce it, and which version or commit is affected.

In scope: a sniffer in this repository that misparses hostile input (crash, hang, excessive memory), a release or index that does not match its sources, and flaws in the CI or release tooling here. Flaws in the host that runs the modules belong in the [wayhouse](https://github.com/wayhouse-proxy/wayhouse/security/advisories/new) repository.

## Supported versions

wayhouse is pre-1.0 and under active development. Fixes land on `main` and ship in the next release; older releases are not patched.
