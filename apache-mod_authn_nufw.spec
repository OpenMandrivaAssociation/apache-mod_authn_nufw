#Module-Specific definitions
%define mod_name mod_authn_nufw
%define mod_conf A61_%{mod_name}.conf
%define mod_so %{mod_name}.so

Summary:	A Single Sign On Authentication module for Apache
Name:		apache-%{mod_name}
Version:	2.2.2
Release:	%mkrel 6
Group:		System/Servers
License:	GPL
URL:		http://www.inl.fr/mod-auth-nufw.html
Source0:	http://www.inl.fr/download/mod_auth_nufw-%{version}.tar.bz2
Source1:	%{mod_conf}.bz2
Patch0:		mod_auth_nufw-2.0-aprfix.diff
Patch2:		mod_auth_nufw-2.2.2-apache22.diff
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.0.54
Requires(pre):	apache >= 2.0.54
Requires:	apache-conf >= 2.0.54
Requires:	apache >= 2.0.54
BuildRequires:  apache-devel >= 2.0.54
BuildRequires:  openldap-devel
BuildRequires: 	mysql-devel
BuildRequires:	file
BuildRequires:	autoconf2.5
BuildRequires:	automake
BuildRequires:	libtool
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
This module allow for a totally transparent, and strict, identification of
users. It uses Nufw as backend, performs SQL requests on the Nufw-fed SQL
tables, and optionnaly resolves numeric userids through a LDAP directory. It
also features LDAP basic caching features. This module is probably of no use
if not used with Nufw, as it lays on a database constantly up-to-date with
users network activity.

%prep

%setup -q -n mod_auth_nufw-%{version}
%patch0 -p0
%patch2 -p0

find . -type d -perm 0700 -exec chmod 755 {} \;
find . -type d -perm 0555 -exec chmod 755 {} \;
find . -type f -perm 0555 -exec chmod 755 {} \;
find . -type f -perm 0444 -exec chmod 644 {} \;

for i in `find . -type d -name CVS` `find . -type d -name .svn` `find . -type f -name .cvs\*` `find . -type f -name .#\*`; do
    if [ -e "$i" ]; then rm -r $i; fi >&/dev/null
done

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

# determine the correct apr-config file
if [ -x %{_bindir}/apr-config ]; then
	APR="%{_bindir}/apr-config"
    else
	APR="%{_bindir}/apr-1-config"
fi
perl -pi -e "s|apr-config|$APR|g" Makefile.in

# apache220 fix
mv mod_auth_nufw.c mod_authn_nufw.c

%build

libtoolize --copy --force; aclocal; autoconf

%configure2_5x --localstatedir=/var/lib \
    --with-apache22 \
    --with-mysql \
    APXS=%{_sbindir}/apxs

%make

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -d %{buildroot}%{_libdir}/apache-extramodules
install -d %{buildroot}%{_sysconfdir}/httpd/modules.d

install -m0755 %{mod_so} %{buildroot}%{_libdir}/apache-extramodules/
bzcat %{SOURCE1} > %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}

%post
if [ -f /var/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f /var/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
    fi
fi

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc NOTICE PLANS README doc/*
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/%{mod_so}
