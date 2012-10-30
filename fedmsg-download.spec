%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?pyver: %global pyver %(%{__python} -c "import sys ; print sys.version[:3]")}

%global modname fedmsg_download

Name:           fedmsg-download
Version:        0.1.3
Release:        1%{?dist}
Summary:        Fedora Infrastructure real-time messaging consumer for downloads
Group:          Applications/Internet
License:        LGPLv2+
URL:            http://github.com/bpeck/%{name}
Source0:        http://pypi.python.org/packages/source/f/%{name}/%{name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  python-devel
BuildRequires:  python-setuptools-devel
BuildRequires:  fedmsg
Requires:       fedmsg
Requires:	pexpect

%if %{?rhel}%{!?rhel:0} <= 6
BuildRequires:  python-ordereddict
BuildRequires:  python-argparse
Requires:       python-ordereddict
Requires:       python-argparse
%endif

%description
Download Consumer which downloads latest branched and rawhide builds when a message from 
fedmsg is received.


%prep
%setup -q -n %{name}-%{version}

%build
%{__python} setup.py build

%install
%{__python} setup.py install -O1 --skip-build \
    --install-data=%{_datadir} --root %{buildroot}

%{__mkdir_p} %{buildroot}%{_sysconfdir}/fedmsg.d/
%{__cp} fedmsg.d/*.py %{buildroot}%{_sysconfdir}/fedmsg.d/.

%{__mkdir_p} %{buildroot}/%{_var}/run/%{modname}
%{__mkdir_p} %{buildroot}/%{_var}/log/%{modname}

%{__mkdir_p} %{buildroot}%{_sysconfdir}/init.d
%{__install} init.d/fedmsg-download.init %{buildroot}%{_sysconfdir}/init.d/%{name}


%post
/sbin/chkconfig --add %{name}

%preun
if [ $1 -eq 0 ]; then
    /sbin/service %{name} stop >/dev/null 2>&1
    /sbin/chkconfig --del %{name}
fi

%files
%doc LICENSE
%{_bindir}/%{name}
%{_sysconfdir}/init.d/%{name}

%attr(755, fedmsg, fedmsg) %dir %{_var}/log/%{modname}
%attr(755, fedmsg, fedmsg) %dir %{_var}/run/%{modname}

%{python_sitelib}/%{modname}/
%{python_sitelib}/%{modname}-%{version}-py%{pyver}.egg-info/

%config(noreplace) %{_sysconfdir}/fedmsg.d


%changelog
* Wed Oct 24 2012 Bill Peck <bpeck@redhat.com> 0.1.3-1
- new package built with tito

* Wed Oct 24 2012 Bill Peck <bpeck@redhat.com> - 0.1.0-1
- Initial packaging.
