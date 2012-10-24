%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?pyver: %global pyver %(%{__python} -c "import sys ; print sys.version[:3]")}

%global modname fedmsg-download

Name:           fedmsg-download
Version:        0.1.1
Release:        1%{?dist}
Summary:        Fedora Infrastructure real-time messaging consumer for downloads
Group:          Applications/Internet
License:        LGPLv2+
URL:            http://github.com/bpeck/fedmsg-download
Source0:        http://pypi.python.org/packages/source/f/%{modname}/%{modname}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  python-devel
BuildRequires:  python-setuptools-devel
BuildRequires:  fedmsg
Requires:       fedmsg

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
%setup -q -n %{modname}-%{version}

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
%{__install} init.d/fedmsg-download.init %{buildroot}%{_sysconfdir}/init.d/fedmsg-download


%post
/sbin/chkconfig --add fedmsg-download

%preun
if [ $1 -eq 0 ]; then
    /sbin/service fedmsg-download stop >/dev/null 2>&1
    /sbin/chkconfig --del fedmsg-download
fi

%files
%doc LICENSE
%{_bindir}/fedmsg-downloader
%{_sysconfdir}/init.d/fedmsg-download

%attr(755, %{modname}, %{modname}) %dir %{_var}/log/%{modname}
%attr(755, %{modname}, %{modname}) %dir %{_var}/run/%{modname}

%{python_sitelib}/%{modname}/
%{python_sitelib}/%{modname}-%{version}-py%{pyver}.egg-info/

%config(noreplace) %{_sysconfdir}/fedmsg.d


%changelog
* Wed Oct 24 2012 Bill Peck <bpeck@redhat.com> 0.1.1-1
- new package built with tito

* Wed Oct 24 2012 Bill Peck <bpeck@redhat.com> - 0.1.0-1
- Initial packaging.
