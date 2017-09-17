%{?!_licensedir:%global license %%doc}
%{!?upstream_version: %global upstream_version %{version}}

%global sname ironic-python-agent

Name:       openstack-ironic-python-agent
Summary:    A python agent for provisioning and deprovisioning bare metal servers
Version:    XXX
Release:    XXX
License:    ASL 2.0
URL:        https://github.com/openstack/ironic-python-agent

Source0:    https://tarballs.openstack.org/%{sname}/%{sname}-%{upstream_version}.tar.gz
Source1:    openstack-ironic-python-agent.service

BuildArch:  noarch
BuildRequires:  python-setuptools
BuildRequires:  python-pbr
BuildRequires:  python2-devel
BuildRequires:  systemd
# These packages are required for running unit tests
BuildRequires: python-eventlet
BuildRequires: python-ironic-lib
BuildRequires: python-iso8601
BuildRequires: python-mock
BuildRequires: python-netifaces
BuildRequires: python-oslo-config
BuildRequires: python-oslo-concurrency
BuildRequires: python-oslo-log
BuildRequires: python-oslo-serialization
BuildRequires: python-oslo-service
BuildRequires: python-oslo-utils
BuildRequires: python-oslotest
BuildRequires: python-os-testr
BuildRequires: python-pecan
BuildRequires: python-pint
BuildRequires: python-psutil
BuildRequires: python-pyudev
BuildRequires: python-requests
BuildRequires: python-rtslib
BuildRequires: python-six
BuildRequires: python-stevedore
BuildRequires: python-wsme
BuildRequires: openstack-macros

Requires: python-ironic-python-agent = %{upstream_version}
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

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

Requires: python-pbr
Requires: python-eventlet
Requires: python-ironic-lib >= 2.5.0
Requires: python-iso8601
Requires: python-netifaces
Requires: python-netaddr >= 0.7.13
Requires: python-oslo-config >= 2:4.0.0
Requires: python-oslo-concurrency >= 3.8.0
Requires: python-oslo-log >= 3.22.0
Requires: python-oslo-serialization >= 1.10.0
Requires: python-oslo-service >= 1.10.0
Requires: python-oslo-utils >= 3.20.0
Requires: python-pecan
Requires: python-pint
Requires: python-psutil
Requires: python-pyudev
Requires: python-requests
Requires: python-rtslib
Requires: python-six
Requires: python-stevedore >= 1.20.0
Requires: python-wsme

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

install -p -D -m 644 etc/ironic_python_agent/ironic_python_agent.conf.sample %{buildroot}/%{_sysconfdir}/ironic-python-agent/agent.conf

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
