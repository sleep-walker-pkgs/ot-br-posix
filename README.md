# OpenThread Border Router RPM Packaging (openSUSE)

This repository contains the native RPM packaging source for OpenThread Border Router on openSUSE systems.

## Contents

This repository is the source for OBS (Open Build Service) scmsync integration and includes:

- **Spec File** (`ot-br.spec`): RPM package specification defining build dependencies, build steps, and package layout
- **Systemd Units**: Service definitions for running the Border Router as a system daemon
  - `ot-br.service`: Main Border Router service unit
- **Sysusers Configuration**: User and group definitions for secure service isolation
  - `ot-br.sysusers`: Declarative user/group setup via systemd-sysusers
- **Tmpfiles Configuration**: Temporary file and directory management
  - `ot-br.tmpfiles`: Runtime directory and state management via systemd-tmpfiles
- **Audit Report**: Security and build audit documentation

## Building

This package is built via OBS (Open Build Service) with scmsync integration. To build locally:

```bash
osc co home:sleep-walker-pkgs:branches:openSUSE:Factory ot-br-posix
cd ot-br-posix
osc build
```

Or using rpmbuild directly:

```bash
rpmbuild -ba ot-br.spec
```

## Integration

This repository is linked to OBS via git scmsync. Commits to the main branch automatically trigger package rebuilds in OBS.

## License

See LICENSE file for licensing details.

## References

- [OpenThread Border Router Documentation](https://openthread.io/guides/border-router)
- [OBS Documentation](https://build.opensuse.org/)
- [RPM Packaging Guide](https://rpm-software-management.github.io/)
