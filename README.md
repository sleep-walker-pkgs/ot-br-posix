# OpenThread Border Router RPM Packaging (openSUSE)

Native RPM packaging source for [OpenThread Border Router](https://github.com/openthread/ot-br-posix)
(OTBR), built via git-based OBS (`scmsync`) and replacing a Docker container deployment.

## Contents

- **`ot-br-posix.spec`** — RPM spec. Builds `otbr-agent` (border router daemon + REST API) and
  `otbr-web` (setup UI) from a vendored, pinned source tree.
- **`ot-br-posix-2026.08.0.tar.gz`** — source tarball for the pinned upstream tag `v2026.08.0`,
  with the `third_party/openthread` submodule (and ITS nested `third_party/mbedtls` +
  `framework` submodules) spliced in at the exact commits `v2026.08.0` pins, since a plain
  GitHub release tarball / `git archive` does not include submodule content. `third_party/
  cpp-httplib` is vendored too, but at a NEWER release (v0.53.1) than ot-br-posix's own pin —
  see `SECURITY_AUDIT_REPORT.md`'s addendum for why. `cJSON` is NOT vendored; the package uses
  the system `cJSON`/`cJSON-devel`.
- **`SECURITY_AUDIT_REPORT.md`** — security audit of the pinned tree (GitHub Security
  Advisories + CVE search for all four upstream repos, plus a manual pattern-based review of
  the vendored `openthread` submodule, which has no automated CVE-scanning tool for its
  C/CMake dependency graph the way Go/Rust/npm projects do).
- **`ot-br-posix-agent.default`, `ot-br-posix-web.default`** — `/etc/default/otbr-{agent,web}`
  environment files (installed as `%config(noreplace)`), pre-filled to match the RCP
  device/interface configuration the Docker deployment on `doom` used
  (`OT_RCP_DEVICE=spinel+hdlc+uart:///dev/ttyUSB0...`, `OT_INFRA_IF=enp0s31f6`,
  `OT_THREAD_IF=wpan0`) — edit these to match your actual hardware.

## Why no dedicated service user

Unlike a typical bridge/daemon package, `otbr-agent` manages kernel network interfaces, NAT64
translation, and firewall/routing rules for the Thread mesh — the same privilege level the
Docker image it replaces required (`--privileged`, `--network=host`,
`NET_ADMIN`/`NET_RAW`/`SYS_ADMIN`). The systemd units therefore run as root rather than under
a `DynamicUser`/dedicated unprivileged account.

## Building

Via OBS (scmsync-linked, see `home:sleep_walker:openthread/ot-br-posix` on
build.opensuse.org):

```bash
osc co home:sleep_walker:openthread ot-br-posix
cd ot-br-posix
osc build
```

Or directly with `rpmbuild` (needs `cJSON-devel cmake dbus-1-devel gcc-c++ git jsoncpp-devel
libavahi-devel libstdc++-devel ninja pkgconfig(libcjson) pkgconfig(libsystemd) readline-devel
systemd-rpm-macros` installed):

```bash
rpmbuild -bb ot-br-posix.spec
```

**Known gotcha**: openSUSE's `%cmake` macro forces `BUILD_SHARED_LIBS=ON`, which breaks
OpenThread's `openthread-ftd <-> tcplp-ftd` mutual dependency (CMake only permits cyclic
dependencies between STATIC libraries) — the spec explicitly re-forces
`-DBUILD_SHARED_LIBS=OFF` after the macro. `-DOTBR_DBUS=OFF` is also required unless
`protobuf-devel` is added as a BuildRequires (the Docker deployment being replaced didn't use
D-Bus either — its process list has no `--dbus` argument).

## Integration

Package meta's `<scmsync>` element points at this repo pinned to an exact commit SHA (not a
floating branch), per this project's OBS git-workflow convention — after pushing a fix, the
OBS package meta needs to be re-pointed at the new commit SHA and `runservice`-forced to pick
it up; a plain `git push` alone does not trigger a resync.

## License

Upstream ot-br-posix, openthread, cpp-httplib and cJSON are each under their own licenses
(see `LICENSE` inside the source tarball) — this repository's own spec/unit/audit files are
public domain / CC0 equivalent, matching the sibling `sleep-walker-matrix-bridges` packaging
repos.

## References

- [OpenThread Border Router Documentation](https://openthread.io/guides/border-router)
- [OBS Documentation](https://build.opensuse.org/)
