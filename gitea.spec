Name:           gitea
Version:        1.26.4
Release:        2%{?dist}
Summary:        Gitea is a painless self-hosted Git service.

License:        MIT
URL:            https://gitea.io
Source0:        https://github.com/go-gitea/gitea/releases/download/v%{version}/%{name}-src-%{version}.tar.gz
Source1:	    gitea.service
Source2:        gitea.ini

BuildRequires:	golang >= 1.21
BuildRequires:	make
BuildRequires:	systemd-rpm-macros

%if 0%{?suse_version}
%global shadow_pkg shadow
%else
%global shadow_pkg shadow-utils
%endif

Requires: git
Requires(pre):	%{shadow_pkg}
%{?systemd_requires}


# Temporary solution while waiting for golang and go-bindata to be built in cbs.centos.org
ExclusiveArch: x86_64 aarch64

%description
Gitea is a painless self-hosted Git service, built in GO

%prep
%setup -q

%build
cd ../
mkdir -p src/code.gitea.io
cp -rav %{name}-%{version}/ src/code.gitea.io/gitea/
export GOPATH=$(pwd)
cd src/code.gitea.io/gitea/
git init
rm -f $GOPATH/go.mod
TAGS="bindata sqlite" make generate build

%install
mkdir -p %{buildroot}/%{_sharedstatedir}/gitea
mkdir -p %{buildroot}/%{_sysconfdir}/gitea
mkdir -p %{buildroot}/%{_unitdir}
#install custom/conf/app.ini.sample %{buildroot}/%{_sysconfdir}/gitea/gitea.ini
install -m 755 ../src/code.gitea.io/gitea/gitea %{buildroot}/%{_sharedstatedir}/gitea/gitea
install -m 644 %{SOURCE1} %{buildroot}/%{_unitdir}/gitea.service
install -m 644 %{SOURCE2} %{buildroot}/%{_sysconfdir}/gitea/gitea.ini

%files
%license LICENSE
%attr (755,gitea,gitea) %{_sharedstatedir}/gitea
%attr(755,gitea,gitea) %{_sharedstatedir}/gitea/gitea
%attr(0640,gitea,gitea) %config(noreplace) %{_sysconfdir}/gitea/gitea.ini
%{_unitdir}/gitea.service

%pre
getent group gitea > /dev/null || groupadd -r gitea
getent passwd gitea > /dev/null || \
	useradd -m -g gitea -s /bin/bash \
	-c "Gitea git account" gitea

%post
%systemd_post gitea.service

%preun
%systemd_preun gitea.service

%postun
%systemd_postun_with_restart gitea.service

%changelog
* Sat Nov 21 2026 CasjaysDev <rpm-devel@casjaysdev.pro> - 1.26.4-2
- Drop the unused directory Source3 (rpm sources must be files)

* Sat Jul 05 2026 CasjaysDev <rpm-devel@casjaysdev.pro> - 1.26.4-1
- Multi-distro: guard Requires(pre) shadow-utils/shadow via %%{?suse_version}
  (openSUSE/SLES use "shadow", RHEL/Fedora use "shadow-utils")
- Verified ExclusiveArch: x86_64 aarch64 already correct, no BuildArch:
  noarch present; no EL7-missing macros in use; no other dep name
  divergences apply (golang, make, git, systemd-rpm-macros identical
  across all target distros)

* Sat Jul 04 2026 CasjaysDev <rpm-devel@casjaysdev.pro> - 1.26.4-1
- Version: 1.26.0 → 1.26.4 (latest)
- Source0: fix tarball name gitea-VERSION → gitea-src-VERSION (GitHub release asset); verified 302→200
- Add Requires(pre): shadow-utils; systemd-rpm-macros; %%{?systemd_requires}
- Add %%preun/%%postun systemd scriptlets; %%license LICENSE

* Fri May 22 2026 CasjaysDev <rpm-devel@casjaysdev.pro> - 1.26.0-1
- Fix spec violations: use %{buildroot}, %global for constants

* Fri Apr 24 2026 CasjaysDev <rpm-devel@casjaysdev.pro> - 1.26.0-1
- Update to 1.26.0
- Modernize spec for EL10

* Mon Jun 04 2018 Fabian Arrotin <fabian.arrotin@arrfab.net> 1.4.1-1
- bumped to new release 1.4.1
- reflected change for default app.ini

* Mon Feb 26 2018 Fabian Arrotin <fabian.arrotin@arrfab.net> 1.3.3-1
- bumped to new release 1.3.3

* Thu Feb 8 2018 Fabian Arrotin <fabian.arrotin@arrfab.net> 1.3.2-1
- initial spec
