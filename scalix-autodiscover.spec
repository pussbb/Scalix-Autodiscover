%define _topdir "./build"
Name:       scalix-autodiscover
Version:    0.0.2
Release:    1%{?dist}
Summary:    Autodiscover service
License:    Copyright 2014 Scalix, Inc. (www.scalix.com)
Source0:    ./
BuildArch:  noarch
Group:      Applications/Communications
Vendor:     Scalix Corporation
URL:        http://www.scalix.com
Packager:   Scalix Support <support@scalix.com>
Requires:   python-pip python-lxml

%description
The Autodiscover service minimizes user configuration
and deployment steps by providing clients access to email
and groupware server features.


%prep
%setup -q -n %{name}

%build

%install
rm -rf %{buildroot}
# _datadir is typically /usr/share/


%clean
rm -rf $RPM_BUILD_ROOT

%files


%changelog
