%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?pyver: %global pyver %(%{__python} -c "import sys ; print sys.version[:3]")}

%global modname fedmsg_download

# Got Systemd?
%if 0%{?fedora} >= 18 || 0%{?rhel} >= 7
%global with_systemd 1
%else
%global with_systemd 0
%endif

Name:           fedmsg-download
Version:        0.1.21
Release:        1%{?dist}
Summary:        Fedora Infrastructure real-time messaging consumer for downloads
Group:          Applications/Internet
License:        LGPLv2+
URL:            http://github.com/p3ck/%{name}
Source0:        http://github.com/p3ck/%{name}/tarball/%{name}-%{version}#/%{name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  python-devel
BuildRequires:  python-setuptools
BuildRequires:  fedmsg >= 0.4.0
Requires:       fedmsg >= 0.4.0
Requires:	pexpect
Requires:	python-setuptools

%if 0%{?rhel}%{?fedora} <= 6
BuildRequires:  python-ordereddict
BuildRequires:  python-argparse
Requires:       python-ordereddict
Requires:       python-argparse
%endif

%if %{with_systemd}
BuildRequires:          systemd-units
Requires(post):         systemd
Requires(pre):          systemd
Requires(postun):       systemd
%else
Requires(post): chkconfig
Requires(preun): chkconfig
# This is for /sbin/service
Requires(preun): initscripts
Requires(postun): initscripts
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

%if %{with_systemd}
%{__mkdir_p} %{buildroot}%{_unitdir}
%{__install} init.d/fedmsg-download.service %{buildroot}%{_unitdir}/%{name}.service
%else
%{__mkdir_p} %{buildroot}%{_sysconfdir}/init.d
%{__install} init.d/fedmsg-download.init %{buildroot}%{_sysconfdir}/init.d/%{name}
%endif


%post
%if %{with_systemd}
%systemd_post %{name}
%endif

%preun
%if %{with_systemd}
%systemd_preun  %{name}
%endif

%postun
%if %{with_systemd}
%systemd_postun_with_restart %{name}
%endif

%files
%doc LICENSE
%{_bindir}/%{name}
%if %{with_systemd}
%attr(0644, root, root)%{_unitdir}/%{name}.service
%else
%attr(0755, root, root)%{_sysconfdir}/init.d/%{name}
%endif

%{python_sitelib}/%{modname}/
%{python_sitelib}/%{modname}-%{version}-py%{pyver}.egg-info/

%config(noreplace) %{_sysconfdir}/fedmsg.d


%changelog
* Mon Apr 24 2017 Bill Peck <bpeck@redhat.com> 0.1.21-1
- Add retry logic to the rsync beyond simply checking for max user connections.
  (bpeck@redhat.com)
- Report return code if it fails (bpeck@redhat.com)

* Thu Apr 06 2017 Bill Peck <bpeck@redhat.com> 0.1.20-1
- Fix path passed to import command. (bpeck@redhat.com)

* Mon Apr 03 2017 Bill Peck <bpeck@redhat.com> 0.1.19-1
- Forgot to import time module (bpeck@redhat.com)

* Mon Apr 03 2017 Bill Peck <bpeck@redhat.com> 0.1.18-1
- Update to support pulling Secondary arches (bpeck@redhat.com)

* Wed May 11 2016 Bill Peck <bpeck@redhat.com> 0.1.17-1
- wrap download method in try/except block. (bpeck@redhat.com)

* Wed May 11 2016 Bill Peck <bpeck@redhat.com> 0.1.16-1
- use double quotes is easier to handle in ansible (bpeck@redhat.com)

* Fri May 06 2016 Bill Peck <bpeck@redhat.com> 0.1.15-1
- do the main downloading in a seperate thread (bpeck@redhat.com)
- change logging for run command (bpeck@redhat.com)
- switch to using subprocess.  deal with output as its generated since keeping
  the entire rsync log may be quite large (bpeck@redhat.com)

* Mon Apr 04 2016 Bill Peck <bpeck@redhat.com> 0.1.14-1
- allow more flexibility when dealing with broken .composeinfo files.
  (bpeck@redhat.com)
- include last 10 lines of rsync commands (bpeck@redhat.com)

* Wed Mar 30 2016 Bill Peck <bpeck@redhat.com> 0.1.13-1
- paperbag release (bpeck@redhat.com)

* Wed Mar 30 2016 Bill Peck <bpeck@redhat.com> 0.1.12-1
- update for systemd (bpeck@redhat.com)

* Fri Mar 27 2015 Bill Peck <bpeck@redhat.com> 0.1.11-3
- Update spec file for newer fedora (bpeck@redhat.com)

* Tue Oct 28 2014 Bill Peck <bpeck@redhat.com> 0.1.11-2
- Accidentally left debug level logging as the default (bpeck@redhat.com)

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
