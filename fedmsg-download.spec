%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?pyver: %global pyver %(%{__python} -c "import sys ; print sys.version[:3]")}

%global modname fedmsg_download

Name:           fedmsg-download
Version:        0.1.11
Release:        1%{?dist}
Summary:        Fedora Infrastructure real-time messaging consumer for downloads
Group:          Applications/Internet
License:        LGPLv2+
URL:            http://github.com/p3ck/%{name}
Source0:        http://github.com/p3ck/%{name}/tarball/%{name}-%{version}#/%{name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  python-devel
BuildRequires:  python-setuptools-devel
BuildRequires:  fedmsg >= 0.4.0
Requires:       fedmsg >= 0.4.0
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

%{python_sitelib}/%{modname}/
%{python_sitelib}/%{modname}-%{version}-py%{pyver}.egg-info/

%config(noreplace) %{_sysconfdir}/fedmsg.d


%changelog
* Tue Oct 28 2014 Bill Peck <bpeck@redhat.com> 0.1.11-1
- make it easier to set logging to DEBUG level (bpeck@redhat.com)
- allow rsyncing composes only if they have a valid .composeinfo file
  (bpeck@redhat.com)

* Wed Sep 17 2014 Bill Peck <bpeck@redhat.com> 0.1.10-1
- fix for locking in init script (bpeck@redhat.com)

* Wed Feb 20 2013 Bill Peck <bpeck@redhat.com> 0.1.9-1
- Update command syntax to newer fedmsg. Fix download.py to support downloading
  rawhide without .composeinfo (bpeck@redhat.com)
- update Requires to specify newer fedmsg.  fix setup.py url and authors.
  (bpeck@redhat.com)
- Update fedmsg_download/consumer.py (rbean@redhat.com)

* Tue Oct 30 2012 Bill Peck <bpeck@redhat.com> 0.1.8-1
- I will get this to work. :-) (bpeck@redhat.com)

* Tue Oct 30 2012 Bill Peck <bpeck@redhat.com> 0.1.7-1
- last time trying to get github url to work. :-( (bpeck@redhat.com)
- one last update to work with github's urls (bpeck@redhat.com)

* Tue Oct 30 2012 Bill Peck <bpeck@redhat.com> 0.1.6-1
- Updated source locations to github. (bpeck@redhat.com)

* Tue Oct 30 2012 Bill Peck <bpeck@redhat.com> 0.1.5-1
- clean up log and run dirs. (bpeck@redhat.com)

* Tue Oct 30 2012 Bill Peck <bpeck@redhat.com> 0.1.4-1
- updated topic filtering. (bpeck@redhat.com)

* Wed Oct 24 2012 Bill Peck <bpeck@redhat.com> 0.1.3-1
- new package built with tito

* Wed Oct 24 2012 Bill Peck <bpeck@redhat.com> - 0.1.0-1
- Initial packaging.
