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

%global service_user otbr
%global service_datadir %{_localstatedir}/lib/otbr
%global service_confdir %{_sysconfdir}/otbr
%global service_logdir %{_localstatedir}/log/otbr

Name:           ot-br-posix
Version:        2026.08.0
Release:        1
Summary:        OpenThread Border Router for POSIX-based systems
License:        BSD-3-Clause
Group:          System/Management
URL:            https://github.com/openthread/ot-br-posix
Source0:        https://github.com/openthread/ot-br-posix/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        %{name}.service
Source2:        %{name}.sysusers
Source3:        %{name}.tmpfiles
BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  git
BuildRequires:  libstdc++-devel
BuildRequires:  mbedtls-devel
BuildRequires:  sysuser-tools
BuildRequires:  cJSON-devel
BuildRequires:  cpp-httplib-devel
%sysusers_requires
%systemd_requires
Requires:       mbedtls
Requires:       cJSON
Requires:       cpp-httplib

%description
OpenThread Border Router (OTBR) is an open-source implementation of a Thread
Border Router for POSIX-based platforms. A Thread Border Router has two
functions: It stores settings and rights for the Thread network. It bridges
traffic between Thread and non-Thread networks.

This package provides a native systemd-managed daemon instead of the upstream
Docker container, running under a dedicated unprivileged system user with
configuration and persistent data kept in standard FHS locations.

%prep
%autosetup -n %{name}-%{version}

%build
%cmake \
  -DCMAKE_BUILD_TYPE=Release \
  -DOTBR_DBUS_INTERFACE_DIR=%{_datadir}/dbus-1/interfaces \
  -DOTBR_SYSTEMD_UNIT_DIR=%{_unitdir} \
  -DOTBR_SYSLOG_FACILITY_ID=LOG_LOCAL7 \
  -DOTBR_WEB_DATADIR=%{_datadir}/otbr-web

%cmake_build

%install
%cmake_install

install -D -m 0644 %{SOURCE1} %{buildroot}%{_unitdir}/%{name}.service
install -D -m 0644 %{SOURCE2} %{buildroot}%{_sysusersdir}/%{name}.conf
install -D -m 0644 %{SOURCE3} %{buildroot}%{_tmpfilesdir}/%{name}.conf
install -d -m 0750 %{buildroot}%{service_confdir}
install -d -m 0750 %{buildroot}%{service_datadir}
install -d -m 0750 %{buildroot}%{service_logdir}
%sysusers_generate_pre %{SOURCE2} %{service_user} %{name}.conf

%pre -f %{service_user}.pre
%service_add_pre %{name}.service

%post
%service_add_post %{name}.service
%tmpfiles_create %{_tmpfilesdir}/%{name}.conf

%preun
%service_del_preun %{name}.service

%postun
%service_del_postun %{name}.service

%files
%license LICENSE
%doc README.md
%{_sbindir}/otbr-agent
%{_sbindir}/otbr-web
%{_sbindir}/ot-ctl
%{_sbindir}/ot-extern-cp
%{_unitdir}/%{name}.service
%{_sysusersdir}/%{name}.conf
%{_tmpfilesdir}/%{name}.conf
%dir %attr(0750,%{service_user},%{service_user}) %{service_datadir}
%dir %attr(0750,%{service_user},%{service_user}) %{service_logdir}
%dir %attr(0750,%{service_user},%{service_user}) %{service_confdir}
%{_datadir}/otbr-web

%changelog
* Thu Sep 18 2026 Tomáš Čech <tcech@suse.com> - 2026.08.0-1
- Initial package of OpenThread Border Router (v2026.08.0)
- Provides otbr-agent and otbr-web as native systemd service
- Security audit completed: see SECURITY_AUDIT_REPORT.md in source repository
- Uses system-packaged cJSON and cpp-httplib libraries
- Openthread submodule vendored into source tarball
