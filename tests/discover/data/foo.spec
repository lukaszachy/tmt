Name: foo
Version: 0.1
Summary: Trying discover with applied patches
Release: 1
License: MIT
BuildArch: noarch
Source0: foo.tgz
Patch0: adding-test.patch

%description
Some tests are being added by patches, lets discover them correctly

%prep
%autosetup -n src

%install

%changelog
* Thu Jun 1 2023 Lukas Zachar <lzachar@redhat.com> 0.1-1
- Initial version
