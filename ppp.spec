Name:           ppp
Version:        2.4.7
Release:        28
Summary:        The Point-to-Point Protocol

License:        BSD and LGPLv2+ and GPLv2+ and Public Domain
URL:            https://ppp.samba.org/
Source0:        https://download.samba.org/pub/ppp/%{name}-%{version}.tar.gz
# Source1-12 are from fedora29
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

# Patch0001-Patch0028 are from Fedora29
Patch0001:      0001-build-sys-use-gcc-as-our-compiler-of-choice.patch
Patch0002:      0002-build-sys-enable-PAM-support.patch
Patch0003:      0003-build-sys-utilize-compiler-flags-handed-to-us-by-rpm.patch
Patch0004:      0004-doc-add-configuration-samples.patch
Patch0005:      0005-build-sys-don-t-hardcode-LIBDIR-but-set-it-according.patch
Patch0006:      0006-scritps-use-change_resolv_conf-function.patch
Patch0007:      0007-build-sys-don-t-strip-binaries-during-installation.patch
Patch0008:      0008-build-sys-use-prefix-usr-instead-of-usr-local.patch
Patch0009:      0009-pppd-introduce-ipv6-accept-remote.patch
Patch0010:      0010-build-sys-enable-CBCP.patch
Patch0011:      0011-build-sys-don-t-put-connect-errors-log-to-etc-ppp.patch
Patch0012:      0012-pppd-we-don-t-want-to-accidentally-leak-fds.patch
Patch0013:      0013-everywhere-O_CLOEXEC-harder.patch
Patch0014:      0014-everywhere-use-SOCK_CLOEXEC-when-creating-socket.patch
Patch0015:      0015-pppd-move-pppd-database-to-var-run-ppp.patch
Patch0016:      0016-rp-pppoe-add-manpage-for-pppoe-discovery.patch
Patch0018:      0018-scritps-fix-ip-up.local-sample.patch
Patch0019:      0019-sys-linux-rework-get_first_ethernet.patch
Patch0020:      0020-pppd-put-lock-files-in-var-lock-ppp.patch
Patch0021:      0021-build-sys-compile-pppol2tp-plugin-with-RPM_OPT_FLAGS.patch
Patch0022:      0022-build-sys-compile-pppol2tp-with-multilink-support.patch
Patch0023:      0023-build-sys-install-rp-pppoe-plugin-files-with-standar.patch
Patch0024:      0024-build-sys-install-pppoatm-plugin-files-with-standard.patch
Patch0025:      0025-pppd-install-pppd-binary-using-standard-perms-755.patch
Patch0026:      ppp-2.4.7-eaptls-mppe-1.101.patch
Patch0028:      0028-pppoe-include-netinet-in.h-before-linux-in.h.patch

Patch0029:      ppp-2.4.7-DES-openssl.patch
Patch0030:      ppp-2.4.7-honor-ldflags.patch
Patch6000:      ppp-CVE-2015-3310.patch

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
%autosetup -n %{name}-%{version} -p1
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
export RPM_OPT_FLAGS="$RPM_OPT_FLAGS -fPIC -Wall -fno-strict-aliasing" RPM_LD_FLAGS="$LDFLAGS"
%configure
make %{?_smp_mflags} LDFLAGS="%{?build_ldflags}"
make -C ppp-watch %{?_smp_mflags} LDFLAGS="%{?build_ldflags}"

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
%{_libdir}/pppd/2.4.7/*.so
%{_sbindir}/chat
%{_sbindir}/ppp*
%ghost %dir /run/ppp
%ghost %dir /run/lock/ppp
%attr(700, root, root) %dir %{_localstatedir}/log/ppp

%files devel
%{_includedir}/pppd/*.h

%files help
%doc FAQ README.cbcp README.eap-tls README.linux README.MPPE
%doc README.MSCHAP80 README.MSCHAP81 README.pppoe README.pwfd PLUGINS
%{_mandir}/man8/*.8.gz

%changelog
* Fri Dec 20 2019 openEuler Buildteam <buildteam@openeuler.org> - 2.4.7-28
- Type:cves
- ID:CVE-2015-3310
- SUG:restart
- DESC:fix CVE-2015-3310

* Sun Sep 15 2019 openEuler Buildteam <buildteam@openeuler.org> - 2.4.7-27
- Package Init

