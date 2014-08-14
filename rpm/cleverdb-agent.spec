%if ! (0%{?rhel} >= 6 || 0%{?fedora} > 12)
%global with_python26 1
%define pybasever 2.6
%define __python_ver 26
%define __python %{_bindir}/python%{?pybasever}
%endif

%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%{!?pythonpath: %global pythonpath %(%{__python} -c "import os, sys; print(os.pathsep.join(x for x in sys.path if x))")}


Name: cleverdb-agent
Version: 0.2.17
Release: 1%{?dist}
Summary: CleverDB user agent

Group:   System Environment/Daemons
License: MIT
URL:     http://cleverdb.io/
Source0: %{name}-%{version}.tar.gz
Source1: %{name}.init.sh
Source2: %{name}.service
Source3: ports.conf

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch: noarch

%if 0%{?with_python26}
BuildRequires: python26-devel
BuildRequires: python26-setuptools
Requires: python26-setuptools
%else

BuildRequires: python-devel
BuildRequires: python-setuptools
Requires: python-setuptools
%endif

%if ! (0%{?rhel} >= 7 || 0%{?fedora} >= 15)

Requires(post): chkconfig
Requires(preun): chkconfig
Requires(preun): initscripts
Requires(postun): initscripts

%else

%if 0%{?systemd_preun:1}

Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units

%endif

BuildRequires: systemd-units

%endif

%description
Cleverdb agent

%prep
%setup -c

%build


%install
rm -rf $RPM_BUILD_ROOT
cd $RPM_BUILD_DIR/%{name}-%{version}/%{name}-%{version}
%{__python} setup.py install -O1 --root $RPM_BUILD_ROOT

%if ! (0%{?rhel} >= 7 || 0%{?fedora} >= 15)
mkdir -p $RPM_BUILD_ROOT%{_initrddir}
install -p %{SOURCE1} $RPM_BUILD_ROOT%{_initrddir}/cleverdb-agent
%else
mkdir -p $RPM_BUILD_ROOT%{_unitdir}
install -p -m 0644 %{SOURCE2} $RPM_BUILD_ROOT%{_unitdir}/
%endif

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/cleverdb-agent/
install -p -m 0640 %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/cleverdb-agent/ports.conf

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
# %doc $RPM_BUILD_DIR/%{name}-%{version}/%{name}-%{version}/LICENSE
%{python_sitelib}/cleverdb/*
%{python_sitelib}/cleverdb_agent-%{version}-py?.?.egg-info
%{python_sitelib}/cleverdb_agent-%{version}-py?.?-nspkg.pth
%{_bindir}/cleverdb-agent
%{_bindir}/cleverdb-upload
%if ! (0%{?rhel} >= 7 || 0%{?fedora} >= 15)
%attr(0755, root, root) %{_initrddir}/cleverdb-agent
%else
%{_unitdir}/cleverdb-agent.service
%endif

%config(noreplace) %{_sysconfdir}/cleverdb-agent/ports.conf


# less than RHEL 8 / Fedora 16
# not sure if RHEL 7 will use systemd yet
%if ! (0%{?rhel} >= 7 || 0%{?fedora} >= 15)

%preun -n cleverdb-agent
  if [ $1 -eq 0 ] ; then
      /sbin/service cleverdb-agent stop >/dev/null 2>&1
      /sbin/chkconfig --del cleverdb-agent
  fi

%post -n cleverdb-agent
  /sbin/chkconfig --add cleverdb-agent

%postun -n cleverdb-agent
  if [ "$1" -ge "1" ] ; then
      /sbin/service cleverdb-agent condrestart >/dev/null 2>&1 || :
  fi
%else

%preun -n cleverdb-agent
%if 0%{?systemd_preun:1}
  %systemd_preun cleverdb-agent.service
%else
  if [ $1 -eq 0 ] ; then
    # Package removal, not upgrade
    /bin/systemctl --no-reload disable cleverdb-agent.service > /dev/null 2>&1 || :
    /bin/systemctl stop cleverdb-agent.service > /dev/null 2>&1 || :

  fi
%endif

%post -n cleverdb-agent
%if 0%{?systemd_post:1}
  %systemd_post cleverdb-agent.service
%else
  /bin/systemctl daemon-reload &>/dev/null || :
%endif

%postun -n cleverdb-agent
%if 0%{?systemd_post:1}
  %systemd_postun cleverdb-agent.service
%else
  /bin/systemctl daemon-reload &>/dev/null
  [ $1 -gt 0 ] && /bin/systemctl try-restart cleverdb-agent.service &>/dev/null || :
%endif

%endif

%changelog
* Wed Aug 15 2014 Alexander V. Nikolaev <avn@labs.sendgrid.com> - 0.2.15
- Initial package
