%{?!_licensedir:%global license %%doc}
%{!?upstream_version: %global upstream_version %{version}}

%global sname ironic-python-agent

Name:       openstack-ironic-python-agent
Summary:    A python agent for provisioning and deprovisioning bare metal servers
Version:    3.3.3
Release:    1%{?dist}
License:    ASL 2.0
URL:        https://github.com/openstack/ironic-python-agent

Source0:    https://tarballs.openstack.org/%{sname}/%{sname}-%{upstream_version}.tar.gz
Source1:    openstack-ironic-python-agent.service
Source2:    ironic-python-agent-dist.conf

BuildArch:  noarch
BuildRequires:  python2-setuptools
BuildRequires:  python2-pbr
BuildRequires:  python2-devel
BuildRequires:  systemd
# These packages are required for running unit tests
BuildRequires: python2-eventlet
BuildRequires: python-ironic-lib
BuildRequires: python2-iso8601
BuildRequires: python2-mock
BuildRequires: python-netifaces
BuildRequires: python2-oslo-config
BuildRequires: python2-oslo-concurrency
BuildRequires: python2-oslo-log
BuildRequires: python2-oslo-serialization
BuildRequires: python2-oslo-service
BuildRequires: python2-oslo-utils
BuildRequires: python2-oslotest
BuildRequires: python2-pecan
BuildRequires: python-pint
BuildRequires: python2-psutil
BuildRequires: python-pyudev
BuildRequires: python2-requests
BuildRequires: python-rtslib
BuildRequires: python2-six
BuildRequires: python2-stevedore
BuildRequires: python-wsme
BuildRequires: openstack-macros
# In Fedora, the ostestr binary is in the python3 subpackage, so using binary as BR
BuildRequires: /usr/bin/ostestr

Requires: python-ironic-python-agent = %{upstream_version}
%{?systemd_requires}

# TODO(trown) when the following packages are available, package for py3:
# python3-eventlet
# python3-oslo-concurrency
# python3-oslo-log
# python3-oslo-serialization
# python3-oslo-service
# python3-oslo-utils
# python3-pecan
# python3-pint
# python3-wsme

%description
An agent for controlling and deploying Ironic controlled bare metal nodes.

The ironic-python-agent works with the agent driver in Ironic to provision the
node. Starting with ironic-python-agent running on a ramdisk on the
unprovisioned node, Ironic makes API calls to ironic-python-agent to provision
the machine. This allows for greater control and flexibility of the entire
deployment process.

The ironic-python-agent may also be used with the original Ironic pxe drivers
as of the Kilo OpenStack release.

%package -n python2-ironic-python-agent
Summary:    Python library for the ironic python agent.
%{?python_provide:%python_provide python2-ironic-python-agent}
# python_provide does not exist in CBS Cloud buildroot
Provides:   python-ironic-python-agent = %{upstream_version}

Requires: python2-pbr
Requires: python2-eventlet
Requires: python-ironic-lib >= 2.14.0
Requires: python2-iso8601
Requires: python-netifaces
Requires: python2-netaddr >= 0.7.18
Requires: python2-oslo-config >= 2:5.2.0
Requires: python2-oslo-concurrency >= 3.26.0
Requires: python2-oslo-log >= 3.36.0
Requires: python2-oslo-serialization >= 2.18.0
Requires: python2-oslo-service >= 1.24.0
Requires: python2-oslo-utils >= 3.33.0
Requires: python2-pecan
Requires: python-pint
Requires: python2-psutil
Requires: python-pyudev
Requires: python2-requests
Requires: python-rtslib
Requires: python2-six
Requires: python2-stevedore >= 1.20.0
Requires: python-wsme
Requires: systemd-python

%description -n python2-ironic-python-agent
Python library for ironic python agent.

%package -n python2-ironic-python-agent-doc
Summary:    Documentation for ironic python agent.
%{?python_provide:%python_provide python2-ironic-python-agent-doc}
# python_provide does not exist in CBS Cloud buildroot
Provides:   python-ironic-python-agent-doc = %{upstream_version}

%description -n python2-ironic-python-agent-doc
Documentation for ironic python agent.

%prep
%autosetup -v -p 1 -n ironic-python-agent-%{upstream_version}

# Remove the requirements file so that pbr hooks don't add it
# to distutils requires_dist config
%py_req_cleanup

%build
%{__python2} setup.py build

%install
%{__python2} setup.py install -O1 --skip-build --root=%{buildroot}

# TODO(trown) build the docs as below once we either remove the upstream
# requirement on python-sphinxcontrib-pecanwsme, or it exists in rawhide.
# For now, we will just include the raw restructured text.
# pushd doc
# sphinx-build -b html -d build/doctrees  source build/html
# popd

# install systemd scripts
mkdir -p %{buildroot}%{_unitdir}
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_unitdir}

# Install distribution config
install -p -D -m 640 %{SOURCE2} %{buildroot}/%{_sysconfdir}/ironic-python-agent/ironic-python-agent-dist.conf

%check
ostestr --path ironic_python_agent/tests/unit

%files
%doc README.rst
%license LICENSE
%config(noreplace) %attr(-,root,root) %{_sysconfdir}/ironic-python-agent
%{_bindir}/ironic-python-agent
%{_unitdir}/openstack-ironic-python-agent.service

%files -n python2-ironic-python-agent
%license LICENSE
%{python2_sitelib}/ironic_python_agent
%{python2_sitelib}/ironic_python_agent*.egg-info

%files -n python2-ironic-python-agent-doc
%doc doc/source
%license LICENSE

%post
%systemd_post openstack-ironic-python-agent.service

%preun
%systemd_preun openstack-ironic-python-agent.service

%postun
%systemd_postun_with_restart openstack-ironic-python-agent.service

%changelog
* Fri Feb 07 2020 RDO <dev@lists.rdoproject.org> 3.3.3-1
- Update to 3.3.3

* Thu Jun 06 2019 RDO <dev@lists.rdoproject.org> 3.3.2-1
- Update to 3.3.2

* Tue Dec 18 2018 RDO <dev@lists.rdoproject.org> 3.3.1-1
- Update to 3.3.1

* Mon Aug 20 2018 RDO <dev@lists.rdoproject.org> 3.3.0-1
- Update to 3.3.0

