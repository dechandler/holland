%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:           holland-delphini
Version:        1.0
Release:        1%{?dist}
Summary:        MySQL Cluster backup plugin for Holland

Group:          Development/Languages
License:        GPLv2
URL:            https://github.com/abg/holland-delphini
Source0:        holland-delphini-1.0.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch
BuildRequires:  python-devel

%description
Delphini is a plugin for the Holland backup framework to generate backups of a MySQL cluster.

%prep
%setup -q


%build
%{__python} setup.py build


%install
rm -rf %{buildroot}
%{__python} setup.py install -O1 --skip-build --root %{buildroot}


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%doc README.rst
%{python_sitelib}/*


%changelog
