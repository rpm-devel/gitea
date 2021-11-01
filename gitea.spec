Name:           gitea
Version:        1.15.6
Release:        1%{?dist}
Summary:        Gitea is a painless self-hosted Git service.

License:        MIT
URL:            https://gitea.io
Source0:        https://github.com/go-gitea/gitea/archive/v%{version}.tar.gz
Source1:	    gitea.service
Source2:        gitea.ini
Source3:        themes

BuildRequires:	golang >= 1.8
BuildRequires:	go-bindata
BuildRequires:	make

Requires: git

# Temporary solution while waiting for golang and go-bindata to be built in cbs.centos.org
ExclusiveArch: i686 x86_64

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
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/%{_sharedstatedir}/gitea
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/gitea
mkdir -p $RPM_BUILD_ROOT/%{_unitdir}
#install custom/conf/app.ini.sample $RPM_BUILD_ROOT/%{_sysconfdir}/gitea/gitea.ini
install -m 755 ../src/code.gitea.io/gitea/gitea $RPM_BUILD_ROOT/%{_sharedstatedir}/gitea/gitea
install -m 644 %{SOURCE1} $RPM_BUILD_ROOT/%{_unitdir}/gitea.service
install -m 644 %{SOURCE2} $RPM_BUILD_ROOT/%{_sysconfdir}/gitea/gitea.ini

%files
%defattr(0644,gitea,gitea,0755)
%doc LICENSE
%attr (755,gitea,gitea) %{_sharedstatedir}/gitea
%attr(755,gitea,gitea) %{_sharedstatedir}/gitea/gitea
%attr(0640,gitea,gitea) %config(noreplace) %{_sysconfdir}/gitea/gitea.ini
%{_unitdir}/gitea.service

%clean
rm -rf $RPM_BUILD_ROOT

%pre
getent group gitea > /dev/null || groupadd -r gitea
getent passwd gitea > /dev/null || \
	useradd -m -g gitea -s /bin/bash \
	-c "Gitea git account" gitea

%post
%systemd_post gitea.service

%changelog
* Mon Jun 04 2018 Fabian Arrotin <fabian.arrotin@arrfab.net> 1.4.1-1
- bumped to new release 1.4.1
- reflected change for default app.ini

* Mon Feb 26 2018 Fabian Arrotin <fabian.arrotin@arrfab.net> 1.3.3-1
- bumped to new release 1.3.3

* Thu Feb 8 2018 Fabian Arrotin <fabian.arrotin@arrfab.net> 1.3.2-1
- initial spec
