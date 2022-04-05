Name:           ppp
Version:        2.4.9
Release:        2
Summary:        The Point-to-Point Protocol

License:        BSD and LGPLv2+ and GPLv2+ and Public Domain
URL:            https://ppp.samba.org/
Source0:        https://download.samba.org/pub/ppp/%{name}-%{version}.tar.gz
Source1:        ppp-watch.tar.xz
Source2:        ip-down
Source3:        ip-down.ipv6to4
Source4:        ip-up
Source5:        ip-up.ipv6to4
Source6:        ipv6-down
Source7:        ipv6-up
Source8:        ifup-ppp
Source9:        ifdown-ppp
Source10:       ppp-pam.conf
Source11:       ppp-logrotate.conf
Source12:       ppp-tmpfiles.conf

BuildRequires:  gcc glib2-devel libpcap-devel openssl-devel pam-devel systemd systemd-devel
Requires:       libpcap >= 14:0.8.3-6 glibc >= 2.0.6 systemd /etc/pam.d/system-auth network-scripts
Supplements:    (network-scripts)
Requires(pre):  /usr/bin/getent
Requires(pre):  /usr/sbin/groupadd
Provides:       network-scripts-ppp
Obsoletes:      network-scripts-ppp

Patch0001:      backport-ppp-2.4.9-config.patch
Patch0002:      backport-0004-doc-add-configuration-samples.patch
Patch0003:      backport-ppp-2.4.9-build-sys-don-t-hardcode-LIBDIR-but-set-it-according.patch
Patch0004:      backport-0006-scritps-use-change_resolv_conf-function.patch
Patch0005:      backport-0011-build-sys-don-t-put-connect-errors-log-to-etc-ppp.patch
Patch0006:      backport-ppp-2.4.8-pppd-we-don-t-want-to-accidentally-leak-fds.patch
Patch0007:      backport-ppp-2.4.9-everywhere-O_CLOEXEC-harder.patch
Patch0008:      backport-0014-everywhere-use-SOCK_CLOEXEC-when-creating-socket.patch
Patch0009:      backport-0015-pppd-move-pppd-database-to-var-run-ppp.patch
Patch0010:      backport-0016-rp-pppoe-add-manpage-for-pppoe-discovery.patch
Patch0011:      backport-0018-scritps-fix-ip-up.local-sample.patch
Patch0012:      backport-0020-pppd-put-lock-files-in-var-lock-ppp.patch
Patch0013:      backport-0023-build-sys-install-rp-pppoe-plugin-files-with-standar.patch
Patch0014:      backport-0024-build-sys-install-pppoatm-plugin-files-with-standard.patch
Patch0015:      backport-ppp-2.4.8-pppd-install-pppd-binary-using-standard-perms-755.patch
Patch0016:      backport-ppp-2.4.9-configure-cflags-allow-commas.patch
%ifarch riscv64 
Patch0017:      backport-0027-Set-LIBDIR-for-RISCV.patch
%endif

%description
The Point-to-Point Protocol (PPP) provides a standard way to establish
a network connection over a serial link.  At present, this package
supports IP and IPV6 and the protocols layered above them, such as TCP
and UDP.  The Linux port of this package also has support for IPX.

%package        devel
Summary:        Development environment for %{name}
Requires:       %{name} = %{version}-%{release}

%description    devel
The %{name}-devel package contains libraries and header files for
building plugins for the %{name}.

%package_help

%prep
%setup -qn %{name}-%{version}
%autopatch -p1
tar -xvJf %{SOURCE1}
mkdir ppp
mkdir network-scripts
cp %{SOURCE2} ppp
cp %{SOURCE3} ppp
cp %{SOURCE4} ppp
cp %{SOURCE5} ppp
cp %{SOURCE6} ppp
cp %{SOURCE7} ppp
cp %{SOURCE8} network-scripts
cp %{SOURCE9} network-scripts

%build
%configure --cflags="$RPM_OPT_FLAGS -fPIC -Wall -fno-strict-aliasing"
%{make_build} LDFLAGS="%{?build_ldflags} -pie"
%{make_build} -C ppp-watch LDFLAGS="%{?build_ldflags} -pie"

%install
make install INSTROOT=$RPM_BUILD_ROOT install-etcppp 
find scripts -type f | xargs chmod a-x
make install ROOT=$RPM_BUILD_ROOT -C ppp-watch
mkdir -p %{buildroot}%{_sysconfdir}/ppp
mkdir -p %{buildroot}%{_sysconfdir}/sysconfig/network-scripts
mkdir -p %{buildroot}%{_localstatedir}/log/ppp
mkdir -p %{buildroot}%{_sysconfdir}/pam.d
mkdir -p %{buildroot}%{_sysconfdir}/logrotate.d
mkdir -p %{buildroot}%{_prefix}/lib/tmpfiles.d
for file in ppp/*; do
    install -p $file %{buildroot}%{_sysconfdir}/ppp/
done
for file in network-scripts/*; do
    install -p $file %{buildroot}%{_sysconfdir}/sysconfig/network-scripts
done

install -m 644 %{SOURCE10} %{buildroot}%{_sysconfdir}/pam.d/ppp
install -m 644 -p %{SOURCE11} %{buildroot}%{_sysconfdir}/logrotate.d/ppp
install -m 644 -p %{SOURCE12} %{buildroot}%{_prefix}/lib/tmpfiles.d/ppp.conf

#ghosts
mkdir -p %{buildroot}%{_rundir}/ppp
mkdir -p %{buildroot}%{_rundir}/lock/ppp

%pre
/usr/bin/getent group dip >/dev/null 2>&1 || /usr/sbin/groupadd -r -g 40 dip >/dev/null 2>&1 || :

%post
%tmpfiles_create ppp.conf
%files
%doc README scripts sample
%{_sysconfdir}/ppp/ip*
%{_sysconfdir}/sysconfig/network-scripts/if*-ppp
%config(noreplace) %{_sysconfdir}/%{name}/chap-secrets
%config(noreplace) %{_sysconfdir}/%{name}/eaptls-client
%config(noreplace) %{_sysconfdir}/%{name}/eaptls-server
%config(noreplace) %{_sysconfdir}/%{name}/options
%config(noreplace) %{_sysconfdir}/%{name}/pap-secrets
%config(noreplace) %{_sysconfdir}/pam.d/ppp
%config(noreplace) %{_sysconfdir}/logrotate.d/ppp
%{_prefix}/lib/tmpfiles.d/*.conf
%{_libdir}/pppd/%{version}/*.so
%{_sbindir}/chat
%{_sbindir}/ppp*
%ghost %dir %{_rundir}/ppp
%ghost %dir %{_rundir}/lock/ppp
%attr(700, root, root) %dir %{_localstatedir}/log/ppp

%files devel
%{_includedir}/pppd/*.h

%files help
%doc FAQ README.cbcp README.eap-tls README.linux README.MPPE
%doc README.MSCHAP80 README.MSCHAP81 README.pppoe README.pwfd PLUGINS
%{_mandir}/man8/*.8.gz

%changelog
* Thu Apr 7 2022 gym369 <gym487@163.com> - 2.4.9-2
- Upgrade Patch for RISC-V

* Mon Mar 28 2022 xihaochen <xihaochen@h-partners.com> - 2.4.9-1
- Type:requirement
- ID:NA
- SUG:NA
- DESC:update ppp version from 2.4.8 to 2.4.9

* Tue Dec 15 2020 xihaochen <xihaochen@huawei.com> - 2.4.8-3
- Type:requirement
- ID:NA
- SUG:NA
- DESC:remove sensitive words 

* Tue Nov 10 2020 whoisxxx <zhangxuzhou4@huawei.com> - 2.4.8-2
- Type: bugfix
- ID: NA
- SUG: NA
- DESC:Set LIBDIR for RISC-V

* Tue Jun 30 2020 yuboyun <yuboyun@huawei.com> - 2.4.8-1
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:update ppp version from 2.4.7 to 2.4.8

* Tue Mar 17 2020 chenzhen <chenzhen44@huawei.com> - 2.4.7-29
- Type:cves
- ID:CVE-2020-8597
- SUG:restart
- DESC:fix CVE-2020-8597

* Fri Dec 20 2019 openEuler Buildteam <buildteam@openeuler.org> - 2.4.7-28
- Type:cves
- ID:CVE-2015-3310
- SUG:restart
- DESC:fix CVE-2015-3310

* Sun Sep 15 2019 openEuler Buildteam <buildteam@openeuler.org> - 2.4.7-27
- Package Init

