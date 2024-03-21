%{!?sources_gpg: %{!?dlrn:%global sources_gpg 1} }
%global sources_gpg_sign 0x2ef3fe0ec2b075ab7458b5f8b702b20b13df2318
%{?!_licensedir:%global license %%doc}
%{!?upstream_version: %global upstream_version %{version}}
# we are excluding some BRs from automatic generator
%global excluded_brs doc8 bandit pre-commit hacking flake8-import-order
# Exclude sphinx from BRs if docs are disabled
%if ! 0%{?with_doc}
%global excluded_brs %{excluded_brs} sphinx openstackdocstheme
%endif

%global with_doc 1
%global sname ironic-python-agent

Name:       openstack-ironic-python-agent
Summary:    A python agent for provisioning and deprovisioning bare metal servers
Version:    9.11.0
Release:    1%{?dist}
License:    Apache-2.0
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

%if 0%{?sources_gpg} == 1
# Required for tarball sources verification
BuildRequires:  /usr/bin/gpgv2
%endif

BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros
BuildRequires:  systemd
BuildRequires: openstack-macros
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

Requires: python3-systemd

%description -n python3-ironic-python-agent
Python library for ironic python agent.

%package -n python3-ironic-python-agent-tests
Summary:    Python library for the ironic python agent - Tests.
Requires: python3-ironic-python-agent = %{version}-%{release}

Requires: python3-testtools
Requires: python3-oslotest
Requires: python3-stestr

%description -n python3-ironic-python-agent-tests
Tests for Python library for ironic python agent.

%if 0%{?with_doc}
%package -n python-ironic-python-agent-doc
Summary:    Documentation for ironic python agent.
%description -n python-ironic-python-agent-doc
Documentation for ironic python agent.
%endif

%prep
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
%{gpgverify}  --keyring=%{SOURCE102} --signature=%{SOURCE101} --data=%{SOURCE0}
%endif
%autosetup -v -p 1 -n ironic-python-agent-%{upstream_version} -S git


sed -i /^[[:space:]]*-c{env:.*_CONSTRAINTS_FILE.*/d tox.ini
sed -i "s/^deps = -c{env:.*_CONSTRAINTS_FILE.*/deps =/" tox.ini
sed -i /^minversion.*/d tox.ini
sed -i /^requires.*virtualenv.*/d tox.ini

# Exclude some bad-known BRs
for pkg in %{excluded_brs}; do
  for reqfile in doc/requirements.txt test-requirements.txt; do
    if [ -f $reqfile ]; then
      sed -i /^${pkg}.*/d $reqfile
    fi
  done
done

# Automatic BR generation
%generate_buildrequires
%if 0%{?with_doc}
  %pyproject_buildrequires -t -e %{default_toxenv},docs
%else
  %pyproject_buildrequires -t -e %{default_toxenv}
%endif

%build
%pyproject_wheel

%install
%pyproject_install

%if 0%{?with_doc}
%tox -e docs
# Remove build docs leftovers
rm -rf doc/build/html/.{doctrees,buildinfo}
%endif

# install systemd scripts
mkdir -p %{buildroot}%{_unitdir}
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_unitdir}

# Install distribution config
install -p -D -m 640 %{SOURCE2} %{buildroot}/%{_sysconfdir}/ironic-python-agent/ironic-python-agent-dist.conf

%check
%tox -e %{default_toxenv}

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
%exclude %{python3_sitelib}/ironic_python_agent/tests
%{python3_sitelib}/ironic_python_agent*.dist-info

%files -n python3-ironic-python-agent-tests
%license LICENSE
%{python3_sitelib}/ironic_python_agent/tests

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
* Thu Mar 21 2024 RDO <dev@lists.rdoproject.org> 9.11.0-1
- Update to 9.11.0

* Thu Mar 21 2024 RDO <dev@lists.rdoproject.org> 9.10.0-1
- Update to 9.10.0

