# Macros for py2/py3 compatibility
%if 0%{?fedora} || 0%{?rhel} > 7
%global pyver %{python3_pkgversion}
%else
%global pyver 2
%endif
%global pyver_bin python%{pyver}
%global pyver_sitelib %python%{pyver}_sitelib
%global pyver_install %py%{pyver}_install
%global pyver_build %py%{pyver}_build
# End of macros for py2/py3 compatibility
%{?!_licensedir:%global license %%doc}
%{!?upstream_version: %global upstream_version %{version}}

%global with_doc 1
%global sname ironic-python-agent

Name:       openstack-ironic-python-agent
Summary:    A python agent for provisioning and deprovisioning bare metal servers
Version:    XXX
Release:    XXX
License:    ASL 2.0
URL:        https://github.com/openstack/ironic-python-agent

Source0:    https://tarballs.openstack.org/%{sname}/%{sname}-%{upstream_version}.tar.gz
Source1:    openstack-ironic-python-agent.service
Source2:    ironic-python-agent-dist.conf

BuildArch:  noarch
BuildRequires:  python%{pyver}-setuptools
BuildRequires:  python%{pyver}-pbr
BuildRequires:  python%{pyver}-devel
BuildRequires:  systemd
# These packages are required for running unit tests
BuildRequires: python%{pyver}-eventlet
BuildRequires: python%{pyver}-ironic-lib
BuildRequires: python%{pyver}-iso8601
BuildRequires: python%{pyver}-mock
BuildRequires: python%{pyver}-oslo-config
BuildRequires: python%{pyver}-oslo-concurrency
BuildRequires: python%{pyver}-oslo-log
BuildRequires: python%{pyver}-oslo-serialization
BuildRequires: python%{pyver}-oslo-service
BuildRequires: python%{pyver}-oslo-utils
BuildRequires: python%{pyver}-oslotest
BuildRequires: python%{pyver}-pecan
BuildRequires: python%{pyver}-psutil
BuildRequires: python%{pyver}-requests
BuildRequires: python%{pyver}-six
BuildRequires: python%{pyver}-stevedore
BuildRequires: python%{pyver}-wsme
BuildRequires: openstack-macros
BuildRequires: python%{pyver}-stestr
# Handle python2 exception
%if %{pyver} == 2
BuildRequires: python-netifaces
BuildRequires: python-pint
BuildRequires: python-pyudev
BuildRequires: python-rtslib
%else
BuildRequires: python%{pyver}-netifaces
BuildRequires: python%{pyver}-pint
BuildRequires: python%{pyver}-pyudev
BuildRequires: python%{pyver}-rtslib
%endif

Requires: python%{pyver}-ironic-python-agent = %{version}-%{release}
%{?systemd_requires}

%description
An agent for controlling and deploying Ironic controlled bare metal nodes.

The ironic-python-agent works with the agent driver in Ironic to provision the
node. Starting with ironic-python-agent running on a ramdisk on the
unprovisioned node, Ironic makes API calls to ironic-python-agent to provision
the machine. This allows for greater control and flexibility of the entire
deployment process.

The ironic-python-agent may also be used with the original Ironic pxe drivers
as of the Kilo OpenStack release.

%package -n python%{pyver}-ironic-python-agent
Summary:    Python library for the ironic python agent.
%{?python_provide:%python_provide python%{pyver}-ironic-python-agent}

Requires: python%{pyver}-pbr
Requires: python%{pyver}-eventlet
Requires: python%{pyver}-ironic-lib >= 2.16.0
Requires: python%{pyver}-iso8601
Requires: python%{pyver}-netaddr >= 0.7.18
Requires: python%{pyver}-oslo-config >= 2:5.2.0
Requires: python%{pyver}-oslo-concurrency >= 3.26.0
Requires: python%{pyver}-oslo-log >= 3.36.0
Requires: python%{pyver}-oslo-serialization >= 2.18.0
Requires: python%{pyver}-oslo-service >= 1.24.0
Requires: python%{pyver}-oslo-utils >= 3.33.0
Requires: python%{pyver}-pecan
Requires: python%{pyver}-psutil
Requires: python%{pyver}-requests
Requires: python%{pyver}-six
Requires: python%{pyver}-stevedore >= 1.20.0
Requires: python%{pyver}-wsme
# Handle python2 exception
%if %{pyver} == 2
Requires: python-netifaces
Requires: python-pint
Requires: python-pyudev
Requires: python-rtslib
Requires: systemd-python
%else
Requires: python%{pyver}-netifaces
Requires: python%{pyver}-pint
Requires: python%{pyver}-pyudev
Requires: python%{pyver}-rtslib
Requires: python%{pyver}-systemd
%endif

%if 0%{?rhel} > 7
# RHEL8 requires a network-scripts package for ifcfg backwards compatibility
Requires:   network-scripts
%endif

%description -n python%{pyver}-ironic-python-agent
Python library for ironic python agent.

%if 0%{?with_doc}
%package -n python-ironic-python-agent-doc
Summary:    Documentation for ironic python agent.
BuildRequires: python%{pyver}-sphinx
BuildRequires: python%{pyver}-sphinxcontrib-httpdomain
BuildRequires: python%{pyver}-sphinxcontrib-pecanwsme
BuildRequires: python%{pyver}-openstackdocstheme

%description -n python-ironic-python-agent-doc
Documentation for ironic python agent.
%endif

%prep
%autosetup -v -p 1 -n ironic-python-agent-%{upstream_version}

# Remove the requirements file so that pbr hooks don't add it
# to distutils requires_dist config
%py_req_cleanup

%build
%{pyver_build}

%install
%{pyver_install}

%if 0%{?with_doc}
export PYTHONPATH=.
sphinx-build-%{pyver} -b html -d doc/build/doctrees doc/source doc/build/html
# Remove build docs leftovers
rm -rf doc/build/html/.{doctrees,buildinfo}
%endif

# install systemd scripts
mkdir -p %{buildroot}%{_unitdir}
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_unitdir}

# Install distribution config
install -p -D -m 640 %{SOURCE2} %{buildroot}/%{_sysconfdir}/ironic-python-agent/ironic-python-agent-dist.conf

%check

export PYTHON=%{pyver_bin}
stestr-%{pyver} --test-path ironic_python_agent/tests/unit run

%files
%doc README.rst
%license LICENSE
%config(noreplace) %attr(-,root,root) %{_sysconfdir}/ironic-python-agent
%{_bindir}/ironic-python-agent
%{_unitdir}/openstack-ironic-python-agent.service

%files -n python%{pyver}-ironic-python-agent
%license LICENSE
%{pyver_sitelib}/ironic_python_agent
%{pyver_sitelib}/ironic_python_agent*.egg-info

%if 0%{?with_doc}
%files -n python-ironic-python-agent-doc
%doc doc/build/html
%license LICENSE
%endif

%post
%systemd_post openstack-ironic-python-agent.service

%preun
%systemd_preun openstack-ironic-python-agent.service

%postun
%systemd_postun_with_restart openstack-ironic-python-agent.service

%changelog
# REMOVEME: error caused by commit http://git.openstack.org/cgit/openstack/ironic-python-agent/commit/?id=e33744ac2d28d23e1e7951c50deaf07806665023
