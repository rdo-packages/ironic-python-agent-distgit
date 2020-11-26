%{!?sources_gpg: %{!?dlrn:%global sources_gpg 1} }
%global sources_gpg_sign 0x5d2d1e4fb8d38e6af76c50d53d4fec30cf5ce3da
%{?!_licensedir:%global license %%doc}
%{!?upstream_version: %global upstream_version %{version}}

%global with_doc 1
%global sname ironic-python-agent

Name:       openstack-ironic-python-agent
Summary:    A python agent for provisioning and deprovisioning bare metal servers
Version:    6.4.2
Release:    1%{?dist}
License:    ASL 2.0
URL:        https://github.com/openstack/ironic-python-agent

Source0:    https://tarballs.openstack.org/%{sname}/%{sname}-%{upstream_version}.tar.gz
Source1:    openstack-ironic-python-agent.service
Source2:    ironic-python-agent-dist.conf
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
Source101:        https://tarballs.openstack.org/%{sname}/%{sname}-%{upstream_version}.tar.gz.asc
Source102:        https://releases.openstack.org/_static/%{sources_gpg_sign}.txt
%endif

BuildArch:  noarch

# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
BuildRequires:  /usr/bin/gpgv2
%endif
BuildRequires:  python3-setuptools
BuildRequires:  python3-pbr
BuildRequires:  python3-devel
BuildRequires:  systemd
# These packages are required for running unit tests
BuildRequires: python3-eventlet
BuildRequires: python3-ironic-lib
BuildRequires: python3-iso8601
BuildRequires: python3-mock
BuildRequires: python3-oslo-config
BuildRequires: python3-oslo-concurrency
BuildRequires: python3-oslo-log
BuildRequires: python3-oslo-serialization
BuildRequires: python3-oslo-service
BuildRequires: python3-oslo-utils
BuildRequires: python3-oslotest
BuildRequires: python3-pecan
BuildRequires: python3-psutil
BuildRequires: python3-requests
BuildRequires: python3-stevedore
BuildRequires: python3-werkzeug
BuildRequires: openstack-macros
BuildRequires: python3-stestr
BuildRequires: python3-netifaces
BuildRequires: python3-pint
BuildRequires: python3-pyudev
BuildRequires: python3-rtslib
BuildRequires: python3-tenacity

Requires: python3-ironic-python-agent = %{version}-%{release}
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

%package -n python3-ironic-python-agent
Summary:    Python library for the ironic python agent.
%{?python_provide:%python_provide python3-ironic-python-agent}

Requires: python3-eventlet >= 0.18.2
Requires: python3-ironic-lib >= 4.1.0
Requires: python3-netifaces >= 0.10.4
Requires: python3-oslo-concurrency >= 3.26.0
Requires: python3-oslo-config >= 2:5.2.0
Requires: python3-oslo-log >= 3.36.0
Requires: python3-oslo-serialization >= 2.18.0
Requires: python3-oslo-service >= 1.24.0
Requires: python3-oslo-utils >= 3.33.0
Requires: python3-pbr >= 2.0.0
Requires: python3-pint >= 0.5
Requires: python3-psutil >= 3.2.2
Requires: python3-pyudev >= 0.18
Requires: python3-requests >= 2.14.2
Requires: python3-rtslib >= 2.1.65
Requires: python3-stevedore >= 1.20.0
Requires: python3-systemd
Requires: python3-werkzeug >= 1.0.1
Requires: python3-tenacity >= 6.2.0

%if 0%{?rhel} > 7
# RHEL8 requires a network-scripts package for ifcfg backwards compatibility
Requires:   network-scripts
%endif

%description -n python3-ironic-python-agent
Python library for ironic python agent.

%if 0%{?with_doc}
%package -n python-ironic-python-agent-doc
Summary:    Documentation for ironic python agent.
BuildRequires: python3-sphinx
BuildRequires: python3-sphinxcontrib-apidoc
BuildRequires: python3-sphinxcontrib-httpdomain
BuildRequires: python3-sphinxcontrib-pecanwsme
BuildRequires: python3-openstackdocstheme

%description -n python-ironic-python-agent-doc
Documentation for ironic python agent.
%endif

%prep
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
%{gpgverify}  --keyring=%{SOURCE102} --signature=%{SOURCE101} --data=%{SOURCE0}
%endif
%autosetup -v -p 1 -n ironic-python-agent-%{upstream_version}

# Remove the requirements file so that pbr hooks don't add it
# to distutils requires_dist config
%py_req_cleanup

%build
%{py3_build}

%install
%{py3_install}

%if 0%{?with_doc}
export PBR_VERSION=%{version}
export PYTHONPATH=.
sphinx-build -b html -d doc/build/doctrees doc/source doc/build/html
# Remove build docs leftovers
rm -rf doc/build/html/.{doctrees,buildinfo}
%endif

# install systemd scripts
mkdir -p %{buildroot}%{_unitdir}
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_unitdir}

# Install distribution config
install -p -D -m 640 %{SOURCE2} %{buildroot}/%{_sysconfdir}/ironic-python-agent/ironic-python-agent-dist.conf

%check

export PYTHON=%{__python3}
stestr --test-path ironic_python_agent/tests/unit run

%files
%doc README.rst
%license LICENSE
%config(noreplace) %attr(-,root,root) %{_sysconfdir}/ironic-python-agent
%{_bindir}/ironic-python-agent
%{_bindir}/ironic-collect-introspection-data
%{_unitdir}/openstack-ironic-python-agent.service

%files -n python3-ironic-python-agent
%license LICENSE
%{python3_sitelib}/ironic_python_agent
%{python3_sitelib}/ironic_python_agent*.egg-info

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
* Thu Nov 26 2020 RDO <dev@lists.rdoproject.org> 6.4.2-1
- Update to 6.4.2

* Tue Oct 20 2020 Joel Capitao <jcapitao@redhat.com> 6.4.1-2
- Enable sources tarball validation using GPG signature.

* Mon Oct 12 2020 RDO <dev@lists.rdoproject.org> 6.4.1-1
- Update to 6.4.1

* Thu Oct 01 2020 RDO <dev@lists.rdoproject.org> 6.4.0-1
- Update to 6.4.0

* Wed Sep 30 2020 RDO <dev@lists.rdoproject.org> 6.3.0-1
- Update to 6.3.0

