#
# spec file for package ot-br-posix
#
# Copyright (c) 2026 Tomáš Čech
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself unless
# otherwise agreed upon.
#

Name:           ot-br-posix
Version:        2026.08.0
Release:        1
Summary:        OpenThread Border Router for POSIX-based systems
License:        BSD-3-Clause
Group:          Productivity/Networking/Other
URL:            https://github.com/openthread/ot-br-posix
Source0:        %{name}-%{version}.tar.gz
Source1:        %{name}-agent.default
Source2:        %{name}-web.default
BuildRequires:  cJSON-devel
BuildRequires:  cmake
BuildRequires:  dbus-1-devel
BuildRequires:  gcc-c++
BuildRequires:  git
BuildRequires:  jsoncpp-devel
BuildRequires:  libavahi-devel
BuildRequires:  libstdc++-devel
BuildRequires:  ninja
BuildRequires:  pkgconfig(libcjson)
BuildRequires:  pkgconfig(libsystemd)
BuildRequires:  readline-devel
BuildRequires:  systemd-rpm-macros
Requires:       libcjson1
Requires:       libjsoncpp27
Requires:       iproute2
Requires:       ipset
%systemd_requires

%description
OpenThread Border Router (OTBR) is an open-source implementation of a Thread
Border Router for POSIX-based platforms. A Thread Border Router bridges a
low-power 802.15.4 Thread mesh network to the adjacent IP infrastructure
(Wi-Fi/Ethernet), and hosts the network's operational dataset, commissioner,
and NAT64/DNS64 translation.

This package builds otbr-agent (the border router daemon plus its REST API)
and otbr-web (the browser-based network setup UI) as native systemd services.
It statically links a vendored, version-pinned copy of the upstream
OpenThread protocol stack (third_party/openthread), with cpp-httplib
vendored at a current upstream release rather than the older version
ot-br-posix pins by default. cJSON, jsoncpp, systemd and avahi come from the
distribution.

Because the agent manages kernel network interfaces, NAT64 translation, and
firewall rules for the Thread mesh, it runs unconfined (root, host network
namespace) rather than under a dedicated service user -- the same privilege
level the container image it replaces required (--privileged,
--network=host, NET_ADMIN/NET_RAW/SYS_ADMIN capabilities).

%prep
%autosetup -n %{name}-%{version}

%build
# openSUSE's %%cmake macro forces BUILD_SHARED_LIBS=ON, but OpenThread's
# internal targets (openthread-ftd <-> tcplp-ftd) have a mutual dependency
# that CMake only permits between STATIC libraries -- override back to OFF.
%cmake \
  -DBUILD_SHARED_LIBS=OFF \
  -DBUILD_TESTING=OFF \
  -DOTBR_WEB=ON \
  -DOTBR_REST=ON \
  -DOTBR_DBUS=OFF \
  -DOTBR_SYSTEMD_UNIT_DIR=%{_unitdir} \
  -DOTBR_SYSLOG_FACILITY_ID=LOG_LOCAL7

%cmake_build

%install
%cmake_install

install -D -m 0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/default/otbr-agent
install -D -m 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/default/otbr-web
install -d -m 0755 %{buildroot}%{_localstatedir}/lib/thread

%pre
%service_add_pre otbr-agent.service otbr-web.service

%post
%service_add_post otbr-agent.service otbr-web.service

%preun
%service_del_preun otbr-agent.service otbr-web.service

%postun
%service_del_postun otbr-agent.service otbr-web.service

%files
%license LICENSE
%doc README.md
%{_sbindir}/otbr-agent
%{_sbindir}/otbr-web
%{_sbindir}/ot-ctl
%{_unitdir}/otbr-agent.service
%{_unitdir}/otbr-web.service
%config(noreplace) %{_sysconfdir}/default/otbr-agent
%config(noreplace) %{_sysconfdir}/default/otbr-web
%dir %{_datadir}/otbr-web
%{_datadir}/otbr-web/frontend
%dir %attr(0755,root,root) %{_localstatedir}/lib/thread

%changelog
* Fri Sep 18 2026 Tomáš Čech <tcech@suse.com> - 2026.08.0-1
- Initial package of OpenThread Border Router (ot-br-posix), replacing a
  Docker container deployment with a native systemd service.
- Vendors a pinned, version-matched copy of the upstream OpenThread protocol
  stack (third_party/openthread, including its own nested mbedtls submodule)
  since it is not available as a standalone distribution package.
- Vendors cpp-httplib at a current upstream release (v0.53.1) rather than
  the older version ot-br-posix's own submodule pin points at, closing a
  critical WebSocket use-after-free and three other CVEs identified during
  packaging's security audit (see SECURITY_AUDIT_REPORT.md in the source
  repository).
- Uses the distribution's cJSON rather than vendoring it.
- Vendors pre-built otbr-web frontend JavaScript/CSS assets, since the OBS
  build environment has no network access for a live npm install.
