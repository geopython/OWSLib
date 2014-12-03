#
# spec file for package OWSLib (0.7.2)
#
# Copyright (c) 2011 Angelos Tzotsos <tzotsos@opensuse.org>
#
# This file and all modifications and additions to the pycsw
# package are under the same license as the package itself.

%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}

%define pyname owslib

Name:           python-%{pyname}
Version:        0.7.2
Release:        0
Summary:        Python interface to OGC Web Services
License:        BSD
Url:            http://geopython.github.com/OWSLib/
Group:          Productivity/Scientific/Other
Source0:        %{pyname}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildArch:      noarch
BuildRequires:  python-devel 
BuildRequires:  python-setuptools
BuildRequires:  fdupes
Requires:	python
Requires:       python-dateutil python-pytz

%description
OWSLib is a Python package for client programming with Open Geospatial Consortium (OGC) web service (hence OWS) interface standards, and their related content models.

%prep
%setup -q -n %{pyname}-%{version}

%build
%{__python} setup.py build

%install
rm -rf %{buildroot}

python setup.py install --prefix=%{_prefix} --root=%{buildroot} \
                                            --record-rpm=INSTALLED_FILES

%fdupes -s %{buildroot}

%clean
rm -rf %{buildroot}

%files -f INSTALLED_FILES
%defattr(-,root,root,-)

%changelog
