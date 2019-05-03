%undefine _hardened_build

%global tarversion 2.02
%undefine _missing_build_ids_terminate_build
%global _configure_gnuconfig_hack 0

### begin grub.macros
# vim:filetype=spec
# Modules always contain just 32-bit code
%global _libdir %{_exec_prefix}/lib
%global _binaries_in_noarch_packages_terminate_build 0
#%%undefine _missing_build_ids_terminate_build
%{expand:%%{!?buildsubdir:%%global buildsubdir grub-%{tarversion}}}
%{expand:%%{!?_licensedir:%%global license %%%%doc}}

%global _configure ../configure

%if %{?_with_ccache: 1}%{?!_with_ccache: 0}
%global cc_equals CC=/usr/%{_lib}/ccache/gcc
%else
%global cc_equals %{nil}
%endif

%global cflags_sed						\\\
	sed							\\\
		-e 's/-O. //g'					\\\
		-e 's/-g /-g3 /g'				\\\
		-e 's/-fplugin=annobin //g'			\\\
		-e 's,-specs=/usr/lib/rpm/redhat/redhat-annobin-cc1 ,,g' \\\
		-e 's/-fstack-protector[[:alpha:]-]\\+//g'	\\\
		-e 's/-Wp,-D_FORTIFY_SOURCE=[[:digit:]]\\+//g'	\\\
		-e 's/--param=ssp-buffer-size=4//g'		\\\
		-e 's/-mregparm=3/-mregparm=4/g'		\\\
		-e 's/-fexceptions//g'				\\\
		-e 's/-fasynchronous-unwind-tables//g'		\\\
		-e 's/^/ -fno-strict-aliasing /'		\\\
		%{nil}

%global host_cflags %{expand:%%(echo %{optflags} | %{cflags_sed})}
%global target_cflags %{expand:%%(echo %{optflags} | %{cflags_sed})}

%global legacy_target_cflags					\\\
	%{expand:%%(echo %{target_cflags} | 			\\\
	%{cflags_sed}						\\\
		-e 's/-m64//g'					\\\
		-e 's/-mcpu=power[[:alnum:]]\\+/-mcpu=power6/g'	\\\
	)}
%global legacy_host_cflags					\\\
	%{expand:%%(echo %{host_cflags} | 			\\\
	%{cflags_sed}						\\\
		-e 's/-m64//g'					\\\
		-e 's/-mcpu=power[[:alnum:]]\\+/-mcpu=power6/g'	\\\
	)}

%global efi_host_cflags %{expand:%%(echo %{host_cflags})}
%global efi_target_cflags %{expand:%%(echo %{target_cflags})}

%global with_efi_arch 0
%global with_alt_efi_arch 0
%global with_legacy_arch 0
%global grubefiarch %{nil}
%global grublegacyarch %{nil}

# sparc is always compiled 64 bit
%ifarch %{sparc}
%global target_cpu_name sparc64
%global _target_platform %{target_cpu_name}-%{_vendor}-%{_target_os}%{?_gnu}
%global legacy_target_cpu_name %{_arch}
%global legacy_package_arch ieee1275
%global platform ieee1275
%endif
# ppc is always compiled 64 bit
%ifarch ppc ppc64 ppc64le
%global target_cpu_name %{_arch}
%global legacy_target_cpu_name powerpc
%global legacy_package_arch %{_arch}
%global legacy_grub_dir powerpc-ieee1275
%global _target_platform %{target_cpu_name}-%{_vendor}-%{_target_os}%{?_gnu}
%global platform ieee1275
%endif


%global efi_only aarch64 %{arm}
%global efi_arch x86_64 ia64 %{efi_only}
%ifarch %{efi_arch}
%global with_efi_arch 1
%else
%global with_efi_arch 0
%endif
%ifarch %{efi_only}
%global with_efi_only 1
%else
%global with_efi_only 0
%endif
%{!?with_efi_arch:%global without_efi_arch 0}
%{?with_efi_arch:%global without_efi_arch 1}
%{!?with_efi_only:%global without_efi_only 0}
%{?with_efi_only:%global without_efi_only 1}

### fixme
%ifarch aarch64 %{arm}
%global efi_modules " "
%else
%global efi_modules " backtrace chain usb usbserial_common usbserial_pl2303 usbserial_ftdi usbserial_usbdebug "
%endif

%ifarch aarch64 %{arm}
%global legacy_provides -l
%endif

%ifarch %{ix86}
%global efiarch ia32
%global target_cpu_name i386
%global grub_target_name i386-efi
%global package_arch efi-ia32

%global legacy_target_cpu_name i386
%global legacy_package_arch pc
%global platform pc
%endif

%ifarch x86_64
%global efiarch x64
%global target_cpu_name %{_arch}
%global grub_target_name %{_arch}-efi
%global package_arch efi-x64

%global legacy_target_cpu_name i386
%global legacy_package_arch pc
%global platform pc

%global alt_efi_arch ia32
%global alt_target_cpu_name i386
%global alt_grub_target_name i386-efi
%global alt_platform efi
%global alt_package_arch efi-ia32

%global alt_efi_host_cflags %{expand:%%(echo %{efi_host_cflags})}
%global alt_efi_target_cflags					\\\
	%{expand:%%(echo %{target_cflags} |			\\\
	%{cflags_sed}						\\\
		-e 's/-m64//g'					\\\
	)}
%endif

%ifarch aarch64
%global efiarch aa64
%global target_cpu_name aarch64
%global grub_target_name arm64-efi
%global package_arch efi-aa64
%endif

%ifarch %{arm}
%global efiarch arm
%global target_cpu_name arm
%global grub_target_name arm-efi
%global package_arch efi-arm
%global efi_target_cflags						\\\
	%{expand:%%(echo %{optflags} |					\\\
	%{cflags_sed}							\\\
		-e 's/-march=armv7-a[[:alnum:]+-]*/&+nofp/g'		\\\
		-e 's/-mfpu=[[:alnum:]-]\\+//g'				\\\
		-e 's/-mfloat-abi=[[:alpha:]]\\+/-mfloat-abi=soft/g'	\\\
	)}
%endif

%global _target_platform %{target_cpu_name}-%{_vendor}-%{_target_os}%{?_gnu}
%global _alt_target_platform %{alt_target_cpu_name}-%{_vendor}-%{_target_os}%{?_gnu}

%ifarch %{efi_arch}
%global with_efi_arch 1
%global grubefiname grub%{efiarch}.efi
%global grubeficdname gcd%{efiarch}.efi
%global grubefiarch %{target_cpu_name}-efi
%ifarch %{ix86}
%global with_efi_modules 0
%global without_efi_modules 1
%else
%global with_efi_modules 1
%global without_efi_modules 0
%endif
%endif

%if 0%{?alt_efi_arch:1}
%global with_alt_efi_arch 1
%global grubaltefiname grub%{alt_efi_arch}.efi
%global grubalteficdname gcd%{alt_efi_arch}.efi
%global grubaltefiarch %{alt_target_cpu_name}-efi
%endif

%ifnarch %{efi_only}
%global with_legacy_arch 1
%global grublegacyarch %{legacy_target_cpu_name}-%{platform}
%global moduledir %{legacy_target_cpu_name}-%{platform}
%endif

%global evr %{epoch}:%{version}-%{release}

%ifarch x86_64
%global with_efi_common 1
%global with_legacy_modules 0
%global with_legacy_common 0
%else
%global with_efi_common 0
%global with_legacy_common 1
%global with_legacy_modules 1
%endif

%define define_legacy_variant()						\
%{expand:%%package %%{1}}						\
Summary:	Bootloader with support for Linux, Multiboot, and more	\
Group:		System Environment/Base					\
Provides:	%{name} = %{evr}					\
Obsoletes:	%{name} < %{evr}					\
Requires:	%{name}-common = %{evr}					\
Requires:	%{name}-tools-minimal = %{evr}				\
Requires:	%{name}-%{1}-modules = %{evr}				\
Requires:	gettext which file					\
Requires:	%{name}-tools-extra = %{evr}				\
Requires:	%{name}-tools = %{evr}					\
Requires(pre):	dracut							\
Requires(post): dracut							\
%{expand:%%description %%{1}}						\
%{desc}									\
This subpackage provides support for %%{1} systems.			\
									\
%{expand:%%{?!buildsubdir:%%define buildsubdir grub-%%{1}-%{tarversion}}}\
%{expand:%%if 0%%{with_legacy_modules}					\
%%package %%{1}-modules							\
Summary:	Modules used to build custom grub images		\
Group:		System Environment/Base					\
BuildArch:	noarch							\
Requires:	%%{name}-common = %%{evr}				\
%%description %%{1}-modules						\
%%{desc}								\
This subpackage provides support for rebuilding your own grub.efi.	\
%%endif									\
}									\
									\
%{expand:%%{?!buildsubdir:%%define buildsubdir grub-%%{1}-%{tarversion}}}\
%{expand:%%package %%{1}-tools}						\
Summary:	Support tools for GRUB.					\
Group:		System Environment/Base					\
Requires:	gettext os-prober which file system-logos		\
Requires:	%{name}-common = %{evr}					\
Requires:	%{name}-tools-minimal = %{evr}				\
Requires:	os-prober >= 1.58-11					\
Requires:	gettext which file					\
									\
%{expand:%%description %%{1}-tools}					\
%{desc}									\
This subpackage provides tools for support of %%{1} platforms.		\
%{nil}

%define define_efi_variant(o)						\
%{expand:%%package %{1}}						\
Summary:	GRUB for EFI systems.					\
Group:		System Environment/Base					\
Requires:	efi-filesystem						\
Requires:	%{name}-common = %{evr}					\
Requires:	%{name}-tools-minimal >= %{evr}				\
Requires:	%{name}-tools-extra = %{evr}				\
Requires:	%{name}-tools = %{evr}					\
Provides:	%{name}-efi = %{evr}					\
%{?legacy_provides:Provides:	%{name} = %{evr}}			\
%{-o:Obsoletes:	%{name}-efi < %{evr}}					\
									\
%{expand:%%description %{1}}						\
%{desc}									\
This subpackage provides support for %{1} systems.			\
									\
%{expand:%%{?!buildsubdir:%%define buildsubdir grub-%{1}-%{tarversion}}}\
%{expand:%if 0%{?with_efi_modules}					\
%{expand:%%package %{1}-modules}					\
Summary:	Modules used to build custom grub.efi images		\
Group:		System Environment/Base					\
BuildArch:	noarch							\
Requires:	%{name}-common = %{evr}					\
Provides:	%{name}-efi-modules = %{evr}				\
Obsoletes:	%{name}-efi-modules < %{evr}				\
%{expand:%%description %{1}-modules}					\
%{desc}									\
This subpackage provides support for rebuilding your own grub.efi.	\
%endif}									\
									\
%{expand:%%package %{1}-cdboot}						\
Summary:	Files used to boot removeable media with EFI		\
Group:		System Environment/Base					\
Requires:	%{name}-common = %{evr}					\
Provides:	%{name}-efi-cdboot = %{evr}				\
%{expand:%%description %{1}-cdboot}					\
%{desc}									\
This subpackage provides optional components of grub used with removeable media on %{1} systems.\
%{nil}

%global do_common_setup()					\
%setup -q -n grub-%{tarversion}					\
rm -fv docs/*.info						\
cp %{SOURCE6} .gitignore					\
cp %{SOURCE8} ./grub-core/tests/strtoull_test.c			\
git init							\
echo '![[:digit:]][[:digit:]]_*.in' > util/grub.d/.gitignore	\
echo '!*.[[:digit:]]' > util/.gitignore				\
echo '!config.h' > include/grub/emu/.gitignore			\
git config user.email "%{name}-owner@fedoraproject.org"		\
git config user.name "Fedora Ninjas"				\
git config gc.auto 0						\
rm -f configure							\
git add .							\
git commit -a -q -m "%{tarversion} baseline."			\
git apply --index --whitespace=nowarn %{SOURCE3}		\
git commit -a -q -m "%{tarversion} master."			\
git am --whitespace=nowarn %%{patches} </dev/null		\
autoreconf -vi							\
git add .							\
git commit -a -q -m "autoreconf"				\
autoconf							\
PYTHON=python3 ./autogen.sh					\
%{nil}

%define do_efi_configure()					\
%configure							\\\
	%{cc_equals}						\\\
	HOST_CFLAGS="%{3} -I$(pwd)"				\\\
	HOST_CPPFLAGS="${CPPFLAGS} -I$(pwd)"			\\\
	TARGET_CFLAGS="%{2} -I$(pwd)"				\\\
	TARGET_CPPFLAGS="${CPPFLAGS} -I$(pwd)"			\\\
	TARGET_LDFLAGS=-static					\\\
	--with-platform=efi					\\\
	--with-utils=host					\\\
	--target=%{1}						\\\
	--with-grubdir=%{name}					\\\
	--program-transform-name=s,grub,%{name},		\\\
	--disable-grub-mount					\\\
	--disable-werror || ( cat config.log ; exit 1 )		\
git add .							\
git commit -m "After efi configure"				\
%{nil}

%define do_efi_build_modules()					\
make %{?_smp_mflags} ascii.h widthspec.h			\
make %{?_smp_mflags} -C grub-core				\
%{nil}

%define do_efi_build_all()					\
make %{?_smp_mflags}						\
%{nil}

%define do_efi_link_utils()					\
for x in grub-mkimage ; do					\\\
	ln ../grub-%{1}-%{tarversion}/${x} ./ ;			\\\
done								\
%{nil}

%ifarch x86_64 aarch64 %{arm}
%define mkimage()						\
%{4}./grub-mkimage -O %{1} -o %{2}.orig				\\\
	-p /EFI/%{efi_vendor} -d grub-core ${GRUB_MODULES}	\
%{4}./grub-mkimage -O %{1} -o %{3}.orig				\\\
	-p /EFI/BOOT -d grub-core ${GRUB_MODULES}		\
%{expand:%%{pesign -s -i %%{2}.orig -o %%{2} -a %%{5} -c %%{6} -n %%{7}}}	\
%{expand:%%{pesign -s -i %%{3}.orig -o %%{3} -a %%{5} -c %%{6} -n %%{7}}}	\
%{nil}
%else
%define mkimage()						\
%{4}./grub-mkimage -O %{1} -o %{2}				\\\
	-p /EFI/%{efi_vendor} -d grub-core ${GRUB_MODULES}	\
%{4}./grub-mkimage -O %{1} -o %{3}				\\\
	-p /EFI/BOOT -d grub-core ${GRUB_MODULES}		\
%{nil}
%endif

%define do_efi_build_images()					\
GRUB_MODULES="	all_video boot blscfg btrfs			\\\
		cat configfile					\\\
		echo efi_netfs efifwsetup efinet ext2		\\\
		fat font gfxmenu gfxterm gzio			\\\
		halt hfsplus http increment iso9660 jpeg	\\\
		loadenv loopback linux lvm lsefi lsefimmap	\\\
		mdraid09 mdraid1x minicmd net			\\\
		normal part_apple part_msdos part_gpt		\\\
		password_pbkdf2 png reboot			\\\
		search search_fs_uuid search_fs_file		\\\
		search_label serial sleep syslinuxcfg test tftp	\\\
		version video xfs"				\
GRUB_MODULES+=%{efi_modules}					\
%{expand:%%{mkimage %{1} %{2} %{3} %{4}}}			\
%{nil}

%define do_primary_efi_build()					\
cd grub-%{1}-%{tarversion}					\
%{expand:%%do_efi_configure %%{4} %%{5} %%{6}}			\
%do_efi_build_all						\
%{expand:%%do_efi_build_images %{grub_target_name} %{2} %{3} ./ } \
cd ..								\
%{nil}

%define do_alt_efi_build()					\
cd grub-%{1}-%{tarversion}					\
%{expand:%%do_efi_configure %%{4} %%{5} %%{6}}			\
%do_efi_build_modules						\
%{expand:%%do_efi_link_utils %{grubefiarch}}			\
%{expand:%%do_efi_build_images %{alt_grub_target_name} %{2} %{3} ../grub-%{grubefiarch}-%{tarversion}/ } \
cd ..								\
%{nil}

%define do_legacy_build()					\
cd grub-%{1}-%{tarversion}					\
%configure							\\\
	%{cc_equals}						\\\
	HOST_CFLAGS="%{legacy_host_cflags} -I$(pwd)"		\\\
	TARGET_CFLAGS="%{legacy_target_cflags} -I$(pwd)"	\\\
	TARGET_LDFLAGS=-static					\\\
	--with-platform=%{platform}				\\\
	--with-utils=host					\\\
	--target=%{_target_platform}				\\\
	--with-grubdir=%{name}					\\\
	--program-transform-name=s,grub,%{name},		\\\
	--disable-grub-mount					\\\
	--disable-werror || ( cat config.log ; exit 1 )		\
git add .							\
git commit -m "After legacy configure"					\
make %{?_smp_mflags}						\
cd ..								\
%{nil}

%define do_alt_efi_install()					\
cd grub-%{1}-%{tarversion}					\
install -d -m 755 $RPM_BUILD_ROOT/usr/lib/grub/%{grubaltefiarch}/ \
find . '(' -iname gdb_grub					\\\
	-o -iname kernel.exec					\\\
	-o -iname kernel.img					\\\
	-o -iname config.h					\\\
	-o -iname gmodule.pl					\\\
	-o -iname modinfo.sh					\\\
	-o -iname '*.lst'					\\\
	-o -iname '*.mod'					\\\
	')'							\\\
	-exec cp {} $RPM_BUILD_ROOT/usr/lib/grub/%{grubaltefiarch}/ \\\; \
find $RPM_BUILD_ROOT -type f -iname "*.mod*" -exec chmod a-x {} '\;'	\
install -m 700 %{2} $RPM_BUILD_ROOT%{efi_esp_dir}/%{2}	\
install -m 700 %{3} $RPM_BUILD_ROOT%{efi_esp_dir}/%{3} \
cd ..								\
%{nil}

%define do_efi_install()					\
cd grub-%{1}-%{tarversion}					\
make DESTDIR=$RPM_BUILD_ROOT install				\
if [ -f $RPM_BUILD_ROOT%{_infodir}/grub.info ]; then		\
	rm -f $RPM_BUILD_ROOT%{_infodir}/grub.info		\
fi								\
if [ -f $RPM_BUILD_ROOT%{_infodir}/grub-dev.info ]; then	\
	rm -f $RPM_BUILD_ROOT%{_infodir}/grub-dev.info		\
fi								\
find $RPM_BUILD_ROOT -iname "*.module" -exec chmod a-x {} '\;'	\
touch $RPM_BUILD_ROOT%{efi_esp_dir}/grub.cfg			\
ln -sf ..%{efi_esp_dir}/grub.cfg				\\\
	$RPM_BUILD_ROOT%{_sysconfdir}/%{name}-efi.cfg		\
install -m 700 %{2} $RPM_BUILD_ROOT%{efi_esp_dir}/%{2}		\
install -m 700 %{3} $RPM_BUILD_ROOT%{efi_esp_dir}/%{3}		\
install -D -m 700 unicode.pf2					\\\
	$RPM_BUILD_ROOT%{efi_esp_dir}/fonts/unicode.pf2		\
${RPM_BUILD_ROOT}/%{_bindir}/%{name}-editenv			\\\
	${RPM_BUILD_ROOT}%{efi_esp_dir}/grubenv create		\
ln -sf ../efi/EFI/%{efi_vendor}/grubenv				\\\
	$RPM_BUILD_ROOT/boot/grub2/grubenv			\
cd ..								\
%{nil}

%define do_legacy_install()					\
cd grub-%{1}-%{tarversion}					\
make DESTDIR=$RPM_BUILD_ROOT install				\
if [ -f $RPM_BUILD_ROOT%{_infodir}/grub.info ]; then		\
	rm -f $RPM_BUILD_ROOT%{_infodir}/grub.info		\
fi								\
if [ -f $RPM_BUILD_ROOT%{_infodir}/grub-dev.info ]; then	\
	rm -f $RPM_BUILD_ROOT%{_infodir}/grub-dev.info		\
fi								\
ln -s ../boot/%{name}/grub.cfg					\\\
	${RPM_BUILD_ROOT}%{_sysconfdir}/grub2.cfg		\
if [ -f $RPM_BUILD_ROOT/%{_libdir}/grub/%{1}/grub2.chrp ]; then \
	mv $RPM_BUILD_ROOT/%{_libdir}/grub/%{1}/grub2.chrp	\\\
	   $RPM_BUILD_ROOT/%{_libdir}/grub/%{1}/grub.chrp	\
fi								\
if [ %{3} -eq 0 ]; then						\
	${RPM_BUILD_ROOT}/%{_bindir}/%{name}-editenv		\\\
		${RPM_BUILD_ROOT}/boot/%{name}/grubenv create	\
fi								\
cd ..								\
%{nil}

%define do_common_install()					\
install -d -m 0755 						\\\
	$RPM_BUILD_ROOT%{_datarootdir}/locale/en\@quot		\\\
	$RPM_BUILD_ROOT%{_datarootdir}/locale/en		\\\
	$RPM_BUILD_ROOT%{_infodir}/				\
cp -a $RPM_BUILD_ROOT%{_datarootdir}/locale/en\@quot		\\\
	$RPM_BUILD_ROOT%{_datarootdir}/locale/en		\
cp docs/grub.info $RPM_BUILD_ROOT%{_infodir}/%{name}.info	\
cp docs/grub-dev.info						\\\
	$RPM_BUILD_ROOT%{_infodir}/%{name}-dev.info		\
install -d -m 0700 ${RPM_BUILD_ROOT}%{efi_esp_dir}/		\
install -d -m 0700 ${RPM_BUILD_ROOT}/boot/grub2/		\
install -d -m 0700 ${RPM_BUILD_ROOT}/boot/loader/entries	\
install -d -m 0700 ${RPM_BUILD_ROOT}/boot/%{name}/themes/system	\
install -d -m 0700 ${RPM_BUILD_ROOT}%{_sysconfdir}/default	\
install -d -m 0700 ${RPM_BUILD_ROOT}%{_sysconfdir}/sysconfig	\
touch ${RPM_BUILD_ROOT}%{_sysconfdir}/default/grub		\
ln -sf ../default/grub						\\\
	${RPM_BUILD_ROOT}%{_sysconfdir}/sysconfig/grub		\
touch ${RPM_BUILD_ROOT}/boot/%{name}/grub.cfg			\
%{nil}

%define define_legacy_variant_files()				\
%{expand:%%files %{1}}						\
%defattr(-,root,root,-)						\
%config(noreplace) %{_sysconfdir}/%{name}.cfg			\
%ghost %config(noreplace) /boot/%{name}/grub.cfg		\
%dir %attr(0700,root,root)/boot/loader/entries			\
								\
%{expand:%if 0%{?with_legacy_modules}				\
%{expand:%%files %{1}-modules}					\
%defattr(-,root,root)						\
%dir %{_libdir}/grub/%{2}/					\
%{_libdir}/grub/%{2}/*						\
%exclude %{_libdir}/grub/%{2}/*.module				\
%exclude %{_libdir}/grub/%{2}/{boot,boot_hybrid,cdboot,diskboot,lzma_decompress,pxeboot}.image \
%exclude %{_libdir}/grub/%{2}/*.o				\
%else								\
%%exclude %%{_libdir}/grub/%%{grublegacyarch}/*			\
%endif}								\
%{nil}

%define define_efi_variant_files()				\
%{expand:%%files %{1}}						\
%defattr(0700,root,root,-)					\
%config(noreplace) %{_sysconfdir}/%{name}-efi.cfg		\
%attr(0700,root,root)%{efi_esp_dir}/%{2}			\
%dir %attr(0700,root,root)%{efi_esp_dir}/fonts			\
%dir %attr(0700,root,root)/boot/loader/entries			\
%ghost %config(noreplace) %attr(0700,root,root)%{efi_esp_dir}/grub.cfg	\
%config(noreplace) /boot/grub2/grubenv					\
%ghost %config(noreplace) %attr(0700,root,root)%{efi_esp_dir}/grubenv	\
%{expand:%if 0%{?without_efi_modules}				\
%exclude %{_libdir}/grub/%{6}					\
%exclude %{_libdir}/grub/%{6}/*					\
%endif}								\
								\
%{expand:%if 0%{?with_efi_modules}				\
%{expand:%%files %{1}-modules}					\
%defattr(-,root,root,-)						\
%dir %{_libdir}/grub/%{6}/					\
%{_libdir}/grub/%{6}/*						\
%exclude %{_libdir}/grub/%{6}/*.module				\
%endif}								\
								\
%{expand:%%files %{1}-cdboot}					\
%defattr(0700,root,root,-)					\
%attr(0700,root,root)%{efi_esp_dir}/%{3}			\
%attr(0700,root,root)%{efi_esp_dir}/fonts			\
%{nil}
### end grub.macros

Name:		grub2
Epoch:		1
Version:	2.02
Release:	78%{?dist}
Summary:	Bootloader with support for Linux, Multiboot and more
License:	GPLv3+
URL:		http://www.gnu.org/software/grub/
Obsoletes:	grub < 1:0.98
Source0:	https://ftp.gnu.org/gnu/grub/grub-%{tarversion}.tar.xz
#Source0:	https://ftp.gnu.org/gnu/grub/grub-%%{tarversion}.tar.xz
Source1:	https://ftp.gnu.org/gnu/grub/grub-%{tarversion}.tar.xz.sig
Source3:	release-to-master.patch
Source4:	http://unifoundry.com/unifont-5.1.20080820.pcf.gz
Source5:	theme.tar.bz2
Source6:	gitignore
Source8:	strtoull_test.c
Source9:	20-grub.install
Source13:	99-grub-mkconfig.install

# generate with do-rebase
### begin grub.patches
Patch0001: 0001-Add-support-for-Linux-EFI-stub-loading.patch
Patch0002: 0002-Rework-linux-command.patch
Patch0003: 0003-Rework-linux16-command.patch
Patch0004: 0004-Add-secureboot-support-on-efi-chainloader.patch
Patch0005: 0005-Make-any-of-the-loaders-that-link-in-efi-mode-honor-.patch
Patch0006: 0006-Handle-multi-arch-64-on-32-boot-in-linuxefi-loader.patch
Patch0007: 0007-re-write-.gitignore.patch
Patch0008: 0008-IBM-client-architecture-CAS-reboot-support.patch
Patch0009: 0009-for-ppc-reset-console-display-attr-when-clear-screen.patch
Patch0010: 0010-Disable-GRUB-video-support-for-IBM-power-machines.patch
Patch0011: 0011-Honor-a-symlink-when-generating-configuration-by-gru.patch
Patch0012: 0012-Move-bash-completion-script-922997.patch
Patch0013: 0013-Update-to-minilzo-2.08.patch
Patch0014: 0014-Allow-fallback-to-include-entries-by-title-not-just-.patch
Patch0015: 0015-Add-GRUB_DISABLE_UUID.patch
Patch0016: 0016-Make-exit-take-a-return-code.patch
Patch0017: 0017-Mark-po-exclude.pot-as-binary-so-git-won-t-try-to-di.patch
Patch0018: 0018-Make-efi-machines-load-an-env-block-from-a-variable.patch
Patch0019: 0019-DHCP-client-ID-and-UUID-options-added.patch
Patch0020: 0020-trim-arp-packets-with-abnormal-size.patch
Patch0021: 0021-Fix-bad-test-on-GRUB_DISABLE_SUBMENU.patch
Patch0022: 0022-Add-support-for-UEFI-operating-systems-returned-by-o.patch
Patch0023: 0023-Migrate-PPC-from-Yaboot-to-Grub2.patch
Patch0024: 0024-Add-fw_path-variable-revised.patch
Patch0025: 0025-Pass-x-hex-hex-straight-through-unmolested.patch
Patch0026: 0026-Add-X-option-to-printf-functions.patch
Patch0027: 0027-Search-for-specific-config-file-for-netboot.patch
Patch0028: 0028-blscfg-add-blscfg-module-to-parse-Boot-Loader-Specif.patch
Patch0029: 0029-Add-devicetree-loading.patch
Patch0030: 0030-Don-t-write-messages-to-the-screen.patch
Patch0031: 0031-Don-t-print-GNU-GRUB-header.patch
Patch0032: 0032-Don-t-add-to-highlighted-row.patch
Patch0033: 0033-Message-string-cleanups.patch
Patch0034: 0034-Fix-border-spacing-now-that-we-aren-t-displaying-it.patch
Patch0035: 0035-Use-the-correct-indentation-for-the-term-help-text.patch
Patch0036: 0036-Indent-menu-entries.patch
Patch0037: 0037-Fix-margins.patch
Patch0038: 0038-Use-2-instead-of-1-for-our-right-hand-margin-so-line.patch
Patch0039: 0039-Enable-pager-by-default.-985860.patch
Patch0040: 0040-F10-doesn-t-work-on-serial-so-don-t-tell-the-user-to.patch
Patch0041: 0041-Don-t-say-GNU-Linux-in-generated-menus.patch
Patch0042: 0042-Don-t-draw-a-border-around-the-menu.patch
Patch0043: 0043-Use-the-standard-margin-for-the-timeout-string.patch
Patch0044: 0044-Add-.eh_frame-to-list-of-relocations-stripped.patch
Patch0045: 0045-Don-t-munge-raw-spaces-when-we-re-doing-our-cmdline-.patch
Patch0046: 0046-Don-t-require-a-password-to-boot-entries-generated-b.patch
Patch0047: 0047-Don-t-emit-Booting-.-message.patch
Patch0048: 0048-Replace-a-lot-of-man-pages-with-slightly-nicer-ones.patch
Patch0049: 0049-use-fw_path-prefix-when-fallback-searching-for-grub-.patch
Patch0050: 0050-Try-mac-guid-etc-before-grub.cfg-on-tftp-config-file.patch
Patch0051: 0051-Fix-convert-function-to-support-NVMe-devices.patch
Patch0052: 0052-reopen-SNP-protocol-for-exclusive-use-by-grub.patch
Patch0053: 0053-Revert-reopen-SNP-protocol-for-exclusive-use-by-grub.patch
Patch0054: 0054-Add-grub_util_readlink.patch
Patch0055: 0055-Make-editenv-chase-symlinks-including-those-across-d.patch
Patch0056: 0056-Generate-OS-and-CLASS-in-10_linux-from-etc-os-releas.patch
Patch0057: 0057-Minimize-the-sort-ordering-for-.debug-and-rescue-ker.patch
Patch0058: 0058-Try-prefix-if-fw_path-doesn-t-work.patch
Patch0059: 0059-Update-info-with-grub.cfg-netboot-selection-order-11.patch
Patch0060: 0060-Use-Distribution-Package-Sort-for-grub2-mkconfig-112.patch
Patch0061: 0061-Handle-rssd-storage-devices.patch
Patch0062: 0062-Make-grub2-mkconfig-construct-titles-that-look-like-.patch
Patch0063: 0063-Add-friendly-grub2-password-config-tool-985962.patch
Patch0064: 0064-Try-to-make-sure-configure.ac-and-grub-rpm-sort-play.patch
Patch0065: 0065-tcp-add-window-scaling-support.patch
Patch0066: 0066-efinet-add-filter-for-the-first-exclusive-reopen-of-.patch
Patch0067: 0067-Fix-security-issue-when-reading-username-and-passwor.patch
Patch0068: 0068-Warn-if-grub-password-will-not-be-read-1290803.patch
Patch0069: 0069-Clean-up-grub-setpassword-documentation-1290799.patch
Patch0070: 0070-Fix-locale-issue-in-grub-setpassword-1294243.patch
Patch0071: 0071-efiemu-Handle-persistent-RAM-and-unknown-possible-fu.patch
Patch0072: 0072-efiemu-Fix-compilation-failure.patch
Patch0073: 0073-Revert-reopen-SNP-protocol-for-exclusive-use-by-grub.patch
Patch0074: 0074-Add-a-url-parser.patch
Patch0075: 0075-efinet-and-bootp-add-support-for-dhcpv6.patch
Patch0076: 0076-Add-grub-get-kernel-settings-and-use-it-in-10_linux.patch
Patch0077: 0077-Normalize-slashes-in-tftp-paths.patch
Patch0078: 0078-Fix-malformed-tftp-packets.patch
Patch0079: 0079-bz1374141-fix-incorrect-mask-for-ppc64.patch
Patch0080: 0080-Make-grub_fatal-also-backtrace.patch
Patch0081: 0081-Make-grub-editenv-build-again.patch
Patch0082: 0082-Fix-up-some-man-pages-rpmdiff-noticed.patch
Patch0083: 0083-Make-exit-take-a-return-code.patch
Patch0084: 0084-arm64-make-sure-fdt-has-address-cells-and-size-cells.patch
Patch0085: 0085-Make-our-info-pages-say-grub2-where-appropriate.patch
Patch0086: 0086-print-more-debug-info-in-our-module-loader.patch
Patch0087: 0087-macos-just-build-chainloader-entries-don-t-try-any-x.patch
Patch0088: 0088-grub2-btrfs-Add-ability-to-boot-from-subvolumes.patch
Patch0089: 0089-export-btrfs_subvol-and-btrfs_subvolid.patch
Patch0090: 0090-grub2-btrfs-03-follow_default.patch
Patch0091: 0091-grub2-btrfs-04-grub2-install.patch
Patch0092: 0092-grub2-btrfs-05-grub2-mkconfig.patch
Patch0093: 0093-grub2-btrfs-06-subvol-mount.patch
Patch0094: 0094-No-more-Bootable-Snapshot-submenu-in-grub.cfg.patch
Patch0095: 0095-Fallback-to-old-subvol-name-scheme-to-support-old-sn.patch
Patch0096: 0096-Grub-not-working-correctly-with-btrfs-snapshots-bsc-.patch
Patch0097: 0097-Add-grub_efi_allocate_pool-and-grub_efi_free_pool-wr.patch
Patch0098: 0098-Use-grub_efi_.-memory-helpers-where-reasonable.patch
Patch0099: 0099-Add-PRIxGRUB_EFI_STATUS-and-use-it.patch
Patch0100: 0100-Don-t-use-dynamic-sized-arrays-since-we-don-t-build-.patch
Patch0101: 0101-don-t-ignore-const.patch
Patch0102: 0102-don-t-use-int-for-efi-status.patch
Patch0103: 0103-make-GRUB_MOD_INIT-declare-its-function-prototypes.patch
Patch0104: 0104-editenv-handle-relative-symlinks.patch
Patch0105: 0105-Make-libgrub.pp-depend-on-config-util.h.patch
Patch0106: 0106-Don-t-guess-boot-efi-as-HFS-on-ppc-machines-in-grub-.patch
Patch0107: 0107-20_linux_xen-load-xen-or-multiboot-2-modules-as-need.patch
Patch0108: 0108-Make-pmtimer-tsc-calibration-not-take-51-seconds-to-.patch
Patch0109: 0109-align-struct-efi_variable-better.patch
Patch0110: 0110-Add-quicksort-implementation.patch
Patch0111: 0111-Add-blscfg-command-support-to-parse-BootLoaderSpec-c.patch
Patch0112: 0112-Add-BLS-support-to-grub-mkconfig.patch
Patch0113: 0113-Remove-duplicated-grub_exit-definition-for-grub-emu-.patch
Patch0114: 0114-Don-t-attempt-to-backtrace-on-grub_abort-for-grub-em.patch
Patch0115: 0115-Enable-blscfg-command-for-the-emu-platform.patch
Patch0116: 0116-Add-linux-and-initrd-commands-for-grub-emu.patch
Patch0117: 0117-Fix-the-efidir-in-grub-setpassword.patch
Patch0118: 0118-Add-grub2-switch-to-blscfg.patch
Patch0119: 0119-Add-grub_debug_enabled.patch
Patch0120: 0120-make-better-backtraces.patch
Patch0121: 0121-normal-don-t-draw-our-startup-message-if-debug-is-se.patch
Patch0122: 0122-Work-around-some-minor-include-path-weirdnesses.patch
Patch0123: 0123-Make-it-possible-to-enabled-build-id-sha1.patch
Patch0124: 0124-Add-grub_qdprintf-grub_dprintf-without-the-file-line.patch
Patch0125: 0125-Make-a-gdb-dprintf-that-tells-us-load-addresses.patch
Patch0126: 0126-Only-attempt-to-scan-different-BLS-directories-on-EF.patch
Patch0127: 0127-Core-TPM-support.patch
Patch0128: 0128-Measure-kernel-initrd.patch
Patch0129: 0129-Add-BIOS-boot-measurement.patch
Patch0130: 0130-Measure-kernel-and-initrd-on-BIOS-systems.patch
Patch0131: 0131-Measure-the-kernel-commandline.patch
Patch0132: 0132-Measure-commands.patch
Patch0133: 0133-Measure-multiboot-images-and-modules.patch
Patch0134: 0134-Fix-boot-when-there-s-no-TPM.patch
Patch0135: 0135-Rework-TPM-measurements.patch
Patch0136: 0136-Fix-event-log-prefix.patch
Patch0137: 0137-Set-the-first-boot-menu-entry-as-default-when-using-.patch
Patch0138: 0138-tpm-fix-warnings-when-compiling-for-platforms-other-.patch
Patch0139: 0139-Make-TPM-errors-less-fatal.patch
Patch0140: 0140-blscfg-handle-multiple-initramfs-images.patch
Patch0141: 0141-BLS-Fix-grub2-switch-to-blscfg-on-non-EFI-machines.patch
Patch0142: 0142-BLS-Use-etcdefaultgrub-instead-of-etc.patch
Patch0143: 0143-Add-missing-options-to-grub2-switch-to-blscfg-man-pa.patch
Patch0144: 0144-Make-grub2-switch-to-blscfg-to-generate-debug-BLS-wh.patch
Patch0145: 0145-Make-grub2-switch-to-blscfg-to-generate-BLS-fragment.patch
Patch0146: 0146-Only-attempt-to-query-dev-mounted-in-boot-efi-as-boo.patch
Patch0147: 0147-Include-OSTree-path-when-searching-kernels-images-if.patch
Patch0148: 0148-Use-BLS-version-field-to-compare-entries-if-id-field.patch
Patch0149: 0149-Add-version-field-to-BLS-generated-by-grub2-switch-t.patch
Patch0150: 0150-Fixup-for-newer-compiler.patch
Patch0151: 0151-Don-t-attempt-to-export-the-start-and-_start-symbols.patch
Patch0152: 0152-Simplify-BLS-entry-key-val-pairs-lookup.patch
Patch0153: 0153-Add-relative-path-to-the-kernel-and-initrds-BLS-fiel.patch
Patch0154: 0154-Skip-leading-spaces-on-BLS-field-values.patch
Patch0155: 0155-Fixup-for-newer-compiler.patch
Patch0156: 0156-TPM-Fix-hash_log_extend_event-function-prototype.patch
Patch0157: 0157-TPM-Fix-compiler-warnings.patch
Patch0158: 0158-grub-switch-to-blscfg.in-get-rid-of-a-bunch-of-bashi.patch
Patch0159: 0159-grub-switch-to-blscfg.in-Better-boot-prefix-checking.patch
Patch0160: 0160-Use-boot-loader-entries-as-BLS-directory-path-also-o.patch
Patch0161: 0161-Use-BLS-fragment-filename-as-menu-entry-id-and-for-c.patch
Patch0162: 0162-Fix-grub-switch-to-blscfg-boot-prefix-handling.patch
Patch0163: 0163-Revert-trim-arp-packets-with-abnormal-size.patch
Patch0164: 0164-Use-xid-to-match-DHCP-replies.patch
Patch0165: 0165-Add-support-for-non-Ethernet-network-cards.patch
Patch0166: 0166-misc-fix-invalid-character-recongition-in-strto-l.patch
Patch0167: 0167-net-read-bracketed-ipv6-addrs-and-port-numbers.patch
Patch0168: 0168-net-read-bracketed-ipv6-addrs-and-port-numbers-pjone.patch
Patch0169: 0169-bootp-New-net_bootp6-command.patch
Patch0170: 0170-Put-back-our-code-to-add-a-local-route.patch
Patch0171: 0171-efinet-UEFI-IPv6-PXE-support.patch
Patch0172: 0172-grub.texi-Add-net_bootp6-doument.patch
Patch0173: 0173-bootp-Add-processing-DHCPACK-packet-from-HTTP-Boot.patch
Patch0174: 0174-efinet-Setting-network-from-UEFI-device-path.patch
Patch0175: 0175-efinet-Setting-DNS-server-from-UEFI-protocol.patch
Patch0176: 0176-Fix-one-more-coverity-complaint.patch
Patch0177: 0177-Fix-grub_net_hwaddr_to_str.patch
Patch0178: 0178-Support-UEFI-networking-protocols.patch
Patch0179: 0179-AUDIT-0-http-boot-tracker-bug.patch
Patch0180: 0180-grub-core-video-efi_gop.c-Add-support-for-BLT_ONLY-a.patch
Patch0181: 0181-efi-uga-use-64-bit-for-fb_base.patch
Patch0182: 0182-EFI-console-Do-not-set-text-mode-until-we-actually-n.patch
Patch0183: 0183-EFI-console-Add-grub_console_read_key_stroke-helper-.patch
Patch0184: 0184-EFI-console-Implement-getkeystatus-support.patch
Patch0185: 0185-Make-grub_getkeystatus-helper-funtion-available-ever.patch
Patch0186: 0186-Accept-ESC-F8-and-holding-SHIFT-as-user-interrupt-ke.patch
Patch0187: 0187-grub-editenv-Add-incr-command-to-increment-integer-v.patch
Patch0188: 0188-Add-auto-hide-menu-support.patch
Patch0189: 0189-Output-a-menu-entry-for-firmware-setup-on-UEFI-FastB.patch
Patch0190: 0190-Add-grub-set-bootflag-utility.patch
Patch0191: 0191-Fix-grub-setpassword-o-s-output-path.patch
Patch0192: 0192-Make-grub-set-password-be-named-like-all-the-other-g.patch
Patch0193: 0193-docs-Add-grub-boot-indeterminate.service-example.patch
Patch0194: 0194-00_menu_auto_hide-Use-a-timeout-of-60s-for-menu_show.patch
Patch0195: 0195-00_menu_auto_hide-Reduce-number-of-save_env-calls.patch
Patch0196: 0196-30_uefi-firmware-fix-use-with-sys-firmware-efi-efiva.patch
Patch0197: 0197-gentpl-add-disable-support.patch
Patch0198: 0198-gentpl-add-pc-firmware-type.patch
Patch0199: 0199-blscfg-remove-unused-typedef.patch
Patch0200: 0200-blscfg-don-t-dynamically-allocate-default_blsdir.patch
Patch0201: 0201-blscfg-sort-BLS-entries-by-version-field.patch
Patch0202: 0202-blscfg-remove-NULL-guards-around-grub_free.patch
Patch0203: 0203-blscfg-fix-filename-in-no-linux-key-error.patch
Patch0204: 0204-blscfg-don-t-leak-bls_entry.filename.patch
Patch0205: 0205-blscfg-fix-compilation-on-EFI-and-EMU.patch
Patch0206: 0206-Add-loadenv-to-blscfg-and-loadenv-source-file-list.patch
Patch0207: 0207-blscfg-Get-rid-of-the-linuxefi-linux16-linux-distinc.patch
Patch0208: 0208-grub-switch-to-blscfg-Only-fix-boot-prefix-for-non-g.patch
Patch0209: 0209-blscfg-Expand-the-BLS-options-field-instead-of-showi.patch
Patch0210: 0210-blscfg-Fallback-to-search-BLS-snippets-in-boot-loade.patch
Patch0211: 0211-blscfg-Don-t-attempt-to-sort-by-version-if-not-prese.patch
Patch0212: 0212-blscfg-remove-logic-to-read-the-grubenv-file-and-set.patch
Patch0213: 0213-Rename-00_menu_auto_hide.in-to-01_menu_auto_hide.in.patch
Patch0214: 0214-efinet-also-use-the-firmware-acceleration-for-http.patch
Patch0215: 0215-efi-http-Make-root_url-reflect-the-protocol-hostname.patch
Patch0216: 0216-Disable-multiboot-multiboot2-and-linux16-modules-on-.patch
Patch0217: 0217-Force-everything-to-use-python3.patch
Patch0218: 0218-Fix-an-8-year-old-typo.patch
Patch0219: 0219-autogen-don-t-run-autoreconf-in-the-topdir.patch
Patch0220: 0220-Make-it-so-we-can-tell-configure-which-cflags-utils-.patch
Patch0221: 0221-module-verifier-make-it-possible-to-run-checkers-on-.patch
Patch0222: 0222-grub-module-verifier-report-the-filename-or-modname-.patch
Patch0223: 0223-Make-efi_netfs-not-duplicate-symbols-from-efinet.patch
Patch0224: 0224-Rework-how-the-fdt-command-builds.patch
Patch0225: 0225-Disable-non-wordsize-allocations-on-arm.patch
Patch0226: 0226-strip-R-.note.gnu.property-at-more-places.patch
Patch0227: 0227-Prepend-prefix-when-HTTP-path-is-relative.patch
Patch0228: 0228-Make-linux_arm_kernel_header.hdr_offset-be-at-the-ri.patch
Patch0229: 0229-Mark-some-unused-stuff-unused.patch
Patch0230: 0230-Make-grub_error-more-verbose.patch
Patch0231: 0231-Make-reset-an-alias-for-the-reboot-command.patch
Patch0232: 0232-EFI-more-debug-output-on-GOP-and-UGA-probing.patch
Patch0233: 0233-Add-a-version-command.patch
Patch0234: 0234-Add-more-dprintf-and-nerf-dprintf-in-script.c.patch
Patch0235: 0235-arm-arm64-loader-Better-memory-allocation-and-error-.patch
Patch0236: 0236-Try-to-pick-better-locations-for-kernel-and-initrd.patch
Patch0237: 0237-Attempt-to-fix-up-all-the-places-Wsign-compare-error.patch
Patch0238: 0238-Don-t-use-Wno-sign-compare-Wno-conversion-Wno-error-.patch
Patch0239: 0239-grub-boot-success.timer-Add-a-few-Conditions-for-run.patch
Patch0240: 0240-x86-efi-Use-bounce-buffers-for-reading-to-addresses-.patch
Patch0241: 0241-x86-efi-Re-arrange-grub_cmd_linux-a-little-bit.patch
Patch0242: 0242-x86-efi-Make-our-own-allocator-for-kernel-stuff.patch
Patch0243: 0243-x86-efi-Allow-initrd-params-cmdline-allocations-abov.patch
Patch0244: 0244-docs-Stop-using-polkit-pkexec-for-grub-boot-success..patch
Patch0245: 0245-drop-TPM-support-for-legacy-BIOS.patch
Patch0246: 0246-Move-quicksort-function-from-kernel.exec-to-the-blsc.patch
Patch0247: 0247-Include-blscfg-module-for-powerpc-ieee1275.patch
Patch0248: 0248-grub-switch-to-blscfg-copy-blscfg-module-for-legacy-.patch
Patch0249: 0249-Fix-getroot.c-s-trampolines.patch
Patch0250: 0250-Do-not-allow-stack-trampolines-anywhere.patch
Patch0251: 0251-Reimplement-boot_counter.patch
Patch0252: 0252-blscfg-don-t-include-.conf-at-the-end-of-our-id.patch
Patch0253: 0253-grub-get-kernel-settings-expose-some-more-config-var.patch
Patch0254: 0254-Reimplement-boot_counter.patch
Patch0255: 0255-add-10_linux_bls-grub.d-snippet-to-generate-menu-ent.patch
Patch0256: 0256-Only-set-kernelopts-in-grubenv-if-it-wasn-t-set-befo.patch
Patch0257: 0257-blscfg-sort-everything-with-rpm-package-comparison.patch
Patch0258: 0258-10_linux_bls-use-grub2-rpm-sort-instead-of-ls-vr-to-.patch
Patch0259: 0259-don-t-set-saved_entry-on-grub2-mkconfig.patch
Patch0260: 0260-grub-switch-to-blscfg-use-debug-instead-of-debug-as-.patch
Patch0261: 0261-Make-blscfg-debug-messages-more-useful.patch
Patch0262: 0262-Make-grub_strtoul-end-pointer-have-the-right-constif.patch
Patch0263: 0263-Fix-menu-entry-selection-based-on-ID-and-title.patch
Patch0264: 0264-Add-comments-and-revert-logic-changes-in-01_fallback.patch
Patch0265: 0265-Remove-quotes-when-reading-ID-value-from-etc-os-rele.patch
Patch0266: 0266-blscfg-expand-grub_users-before-passing-to-grub_norm.patch
Patch0267: 0267-Make-the-menu-entry-users-option-argument-to-be-opti.patch
Patch0268: 0268-10_linux_bls-add-missing-menu-entries-options.patch
Patch0269: 0269-Fix-menu-entry-selection-based-on-title.patch
Patch0270: 0270-BLS-files-should-only-be-copied-by-grub-switch-to-bl.patch
Patch0271: 0271-Fix-get_entry_number-wrongly-dereferencing-the-tail-.patch
Patch0272: 0272-Make-grub2-mkconfig-to-honour-GRUB_CMDLINE_LINUX-in-.patch
Patch0273: 0273-Add-efi-export-env-and-efi-load-env-commands.patch
Patch0274: 0274-Make-it-possible-to-subtract-conditions-from-debug.patch
Patch0275: 0275-Export-all-variables-from-the-initial-context-when-c.patch
Patch0276: 0276-blscfg-store-the-BLS-entries-in-a-sorted-linked-list.patch
Patch0277: 0277-blscfg-add-more-options-to-blscfg-command-to-make-it.patch
Patch0278: 0278-blscfg-add-support-for-prepend-early-initrds-to-the-.patch
Patch0279: 0279-Fix-the-looking-up-grub.cfg-XXX-while-tftp-booting.patch
Patch0280: 0280-Try-to-set-fPIE-and-friends-on-libgnu.a.patch
Patch0281: 0281-Don-t-make-grub_strtoull-print-an-error-if-no-conver.patch
Patch0282: 0282-Set-blsdir-if-the-BLS-directory-path-isn-t-one-of-th.patch
Patch0283: 0283-Check-if-blsdir-exists-before-attempting-to-get-it-s.patch
Patch0284: 0284-blscfg-fallback-to-default_kernelopts-if-BLS-option-.patch
Patch0285: 0285-grub-switch-to-blscfg-copy-increment.mod-for-legacy-.patch
Patch0286: 0286-Only-set-blsdir-if-boot-loader-entries-is-in-a-btrfs.patch
Patch0287: 0287-blscfg-don-t-use-grub_list_t-and-the-GRUB_AS_LIST-ma.patch
Patch0288: 0288-10_linux_bls-don-t-add-users-option-to-generated-men.patch
Patch0289: 0289-grub.d-Split-out-boot-success-reset-from-menu-auto-h.patch
Patch0290: 0290-HTTP-boot-strncmp-returns-0-on-equal.patch
Patch0291: 0291-Add-10_reset_boot_success-to-Makefile.patch
### end grub.patches

BuildRequires:	gcc efi-srpm-macros
BuildRequires:	flex bison binutils python3
BuildRequires:	ncurses-devel xz-devel bzip2-devel
BuildRequires:	freetype-devel libusb-devel
BuildRequires:	rpm-devel
BuildRequires:	rpm-devel rpm-libs
BuildRequires:	autoconf automake autogen device-mapper-devel
BuildRequires:	freetype-devel gettext-devel git
BuildRequires:	texinfo
BuildRequires:	dejavu-sans-fonts
BuildRequires:	help2man
# For %%_userunitdir macro
BuildRequires:	systemd
%ifarch %{efi_arch}
BuildRequires:	pesign >= 0.99-8
%endif
%if %{?_with_ccache: 1}%{?!_with_ccache: 0}
BuildRequires:	ccache
%endif

ExcludeArch:	s390 s390x
Obsoletes:	%{name} <= %{evr}

%if 0%{with_legacy_arch}
Requires:	%{name}-%{legacy_package_arch} = %{evr}
%else
Requires:	%{name}-%{package_arch} = %{evr}
%endif

%global desc \
The GRand Unified Bootloader (GRUB) is a highly configurable and \
customizable bootloader with modular architecture.  It supports a rich \
variety of kernel formats, file systems, computer architectures and \
hardware devices.\
%{nil}

%description
%{desc}

%package common
Summary:	grub2 common layout
BuildArch:	noarch
Conflicts:	grubby < 8.40-18

%description common
This package provides some directories which are required by various grub2
subpackages.

%package tools
Summary:	Support tools for GRUB.
Obsoletes:	%{name}-tools < %{evr}
Requires:	%{name}-common = %{epoch}:%{version}-%{release}
Requires:	gettext os-prober which file
Requires(pre):	dracut
Requires(post):	dracut

%description tools
%{desc}
This subpackage provides tools for support of all platforms.

%ifarch x86_64
%package tools-efi
Summary:	Support tools for GRUB.
Requires:	gettext os-prober which file
Requires:	%{name}-common = %{epoch}:%{version}-%{release}
Obsoletes:	%{name}-tools < %{evr}

%description tools-efi
%{desc}
This subpackage provides tools for support of EFI platforms.
%endif

%package tools-minimal
Summary:	Support tools for GRUB.
Requires:	gettext
Requires:	%{name}-common = %{epoch}:%{version}-%{release}
Obsoletes:	%{name}-tools < %{evr}

%description tools-minimal
%{desc}
This subpackage provides tools for support of all platforms.

%package tools-extra
Summary:	Support tools for GRUB.
Requires:	gettext os-prober which file
Requires:	%{name}-tools-minimal = %{epoch}:%{version}-%{release}
Requires:	%{name}-common = %{epoch}:%{version}-%{release}
Obsoletes:	%{name}-tools < %{evr}

%description tools-extra
%{desc}
This subpackage provides tools for support of all platforms.

%if 0%{with_efi_arch}
%{expand:%define_efi_variant %%{package_arch} -o}
%endif
%if 0%{with_alt_efi_arch}
%{expand:%define_efi_variant %%{alt_package_arch}}
%endif
%if 0%{with_legacy_arch}
%{expand:%define_legacy_variant %%{legacy_package_arch}}
%endif

%prep
%do_common_setup
%if 0%{with_efi_arch}
mkdir grub-%{grubefiarch}-%{tarversion}
grep -A100000 '# stuff "make" creates' .gitignore > grub-%{grubefiarch}-%{tarversion}/.gitignore
cp %{SOURCE4} grub-%{grubefiarch}-%{tarversion}/unifont.pcf.gz
git add grub-%{grubefiarch}-%{tarversion}
%endif
%if 0%{with_alt_efi_arch}
mkdir grub-%{grubaltefiarch}-%{tarversion}
grep -A100000 '# stuff "make" creates' .gitignore > grub-%{grubaltefiarch}-%{tarversion}/.gitignore
cp %{SOURCE4} grub-%{grubaltefiarch}-%{tarversion}/unifont.pcf.gz
git add grub-%{grubaltefiarch}-%{tarversion}
%endif
%if 0%{with_legacy_arch}
mkdir grub-%{grublegacyarch}-%{tarversion}
grep -A100000 '# stuff "make" creates' .gitignore > grub-%{grublegacyarch}-%{tarversion}/.gitignore
cp %{SOURCE4} grub-%{grublegacyarch}-%{tarversion}/unifont.pcf.gz
git add grub-%{grublegacyarch}-%{tarversion}
%endif
git commit -m "After making subdirs"

%build
%if 0%{with_efi_arch}
%{expand:%do_primary_efi_build %%{grubefiarch} %%{grubefiname} %%{grubeficdname} %%{_target_platform} %%{efi_target_cflags} %%{efi_host_cflags}}
%endif
%if 0%{with_alt_efi_arch}
%{expand:%do_alt_efi_build %%{grubaltefiarch} %%{grubaltefiname} %%{grubalteficdname} %%{_alt_target_platform} %%{alt_efi_target_cflags} %%{alt_efi_host_cflags}}
%endif
%if 0%{with_legacy_arch}
%{expand:%do_legacy_build %%{grublegacyarch}}
%endif
makeinfo --info --no-split -I docs -o docs/grub-dev.info \
	docs/grub-dev.texi
makeinfo --info --no-split -I docs -o docs/grub.info \
	docs/grub.texi
makeinfo --html --no-split -I docs -o docs/grub-dev.html \
	docs/grub-dev.texi
makeinfo --html --no-split -I docs -o docs/grub.html \
	docs/grub.texi

%install
set -e
rm -fr $RPM_BUILD_ROOT

%do_common_install
%if 0%{with_efi_arch}
%{expand:%do_efi_install %%{grubefiarch} %%{grubefiname} %%{grubeficdname}}
%endif
%if 0%{with_alt_efi_arch}
%{expand:%do_alt_efi_install %%{grubaltefiarch} %%{grubaltefiname} %%{grubalteficdname}}
%endif
%if 0%{with_legacy_arch}
%{expand:%do_legacy_install %%{grublegacyarch} %%{alt_grub_target_name} 0%{with_efi_arch}}
%endif
rm -f $RPM_BUILD_ROOT%{_infodir}/dir
ln -s %{name}-set-password ${RPM_BUILD_ROOT}/%{_sbindir}/%{name}-setpassword
echo '.so man8/%{name}-set-password.8' > ${RPM_BUILD_ROOT}/%{_datadir}/man/man8/%{name}-setpassword.8
%ifnarch x86_64
rm -vf ${RPM_BUILD_ROOT}/%{_bindir}/%{name}-render-label
rm -vf ${RPM_BUILD_ROOT}/%{_sbindir}/%{name}-bios-setup
rm -vf ${RPM_BUILD_ROOT}/%{_sbindir}/%{name}-macbless
%endif

%find_lang grub

# Make selinux happy with exec stack binaries.
mkdir ${RPM_BUILD_ROOT}%{_sysconfdir}/prelink.conf.d/
cat << EOF > ${RPM_BUILD_ROOT}%{_sysconfdir}/prelink.conf.d/grub2.conf
# these have execstack, and break under selinux
-b /usr/bin/grub2-script-check
-b /usr/bin/grub2-mkrelpath
-b /usr/bin/grub2-fstest
-b /usr/sbin/grub2-bios-setup
-b /usr/sbin/grub2-probe
-b /usr/sbin/grub2-sparc64-setup
EOF

# Install kernel-install scripts
install -d -m 0755 %{buildroot}%{_prefix}/lib/kernel/install.d/
install -D -m 0755 -t %{buildroot}%{_prefix}/lib/kernel/install.d/ %{SOURCE9}
install -D -m 0755 -t %{buildroot}%{_prefix}/lib/kernel/install.d/ %{SOURCE13}
install -d -m 0755 %{buildroot}%{_sysconfdir}/kernel/install.d/
# Install systemd user service to set the boot_success flag
install -D -m 0755 -t %{buildroot}%{_userunitdir} \
	docs/grub-boot-success.{timer,service}
install -d -m 0755 %{buildroot}%{_userunitdir}/timers.target.wants
ln -s ../grub-boot-success.timer \
	%{buildroot}%{_userunitdir}/timers.target.wants
# Install systemd system-update unit to set boot_indeterminate for offline-upd
install -D -m 0755 -t %{buildroot}%{_unitdir} docs/grub-boot-indeterminate.service
install -d -m 0755 %{buildroot}%{_unitdir}/system-update.target.wants
ln -s ../grub-boot-indeterminate.service \
	%{buildroot}%{_unitdir}/system-update.target.wants

# Don't run debuginfo on all the grub modules and whatnot; it just
# rejects them, complains, and slows down extraction.
%global finddebugroot "%{_builddir}/%{?buildsubdir}/debug"

%global dip RPM_BUILD_ROOT=%{finddebugroot} %{__debug_install_post}
%define __debug_install_post (						\
	mkdir -p %{finddebugroot}/usr					\
	mv ${RPM_BUILD_ROOT}/usr/bin %{finddebugroot}/usr/bin		\
	mv ${RPM_BUILD_ROOT}/usr/sbin %{finddebugroot}/usr/sbin		\
	%{dip}								\
	install -m 0755 -d %{buildroot}/usr/lib/ %{buildroot}/usr/src/	\
	cp -al %{finddebugroot}/usr/lib/debug/				\\\
		%{buildroot}/usr/lib/debug/				\
	cp -al %{finddebugroot}/usr/src/debug/				\\\
		%{buildroot}/usr/src/debug/ )				\
	mv %{finddebugroot}/usr/bin %{buildroot}/usr/bin		\
	mv %{finddebugroot}/usr/sbin %{buildroot}/usr/sbin		\
	%{nil}

%undefine buildsubdir

%pre tools
if [ -f /boot/grub2/user.cfg ]; then
    if grep -q '^GRUB_PASSWORD=' /boot/grub2/user.cfg ; then
	sed -i 's/^GRUB_PASSWORD=/GRUB2_PASSWORD=/' /boot/grub2/user.cfg
    fi
elif [ -f %{efi_esp_dir}/user.cfg ]; then
    if grep -q '^GRUB_PASSWORD=' %{efi_esp_dir}/user.cfg ; then
	sed -i 's/^GRUB_PASSWORD=/GRUB2_PASSWORD=/' \
	    %{efi_esp_dir}/user.cfg
    fi
elif [ -f /etc/grub.d/01_users ] && \
	grep -q '^password_pbkdf2 root' /etc/grub.d/01_users ; then
    if [ -f %{efi_esp_dir}/grub.cfg ]; then
	# on EFI we don't get permissions on the file, but
	# the directory is protected.
	grep '^password_pbkdf2 root' /etc/grub.d/01_users | \
		sed 's/^password_pbkdf2 root \(.*\)$/GRUB2_PASSWORD=\1/' \
	    > %{efi_esp_dir}/user.cfg
    fi
    if [ -f /boot/grub2/grub.cfg ]; then
	install -m 0600 /dev/null /boot/grub2/user.cfg
	chmod 0600 /boot/grub2/user.cfg
	grep '^password_pbkdf2 root' /etc/grub.d/01_users | \
		sed 's/^password_pbkdf2 root \(.*\)$/GRUB2_PASSWORD=\1/' \
	    > /boot/grub2/user.cfg
    fi
fi

%posttrans tools

if [ -f /etc/default/grub ]; then
    ! grep -q '^GRUB_ENABLE_BLSCFG=false' /etc/default/grub && \
      /sbin/grub2-switch-to-blscfg --backup-suffix=.rpmsave &>/dev/null || :
fi

%triggerun -- grub2 < 1:1.99-4
# grub2 < 1.99-4 removed a number of essential files in postun. To fix upgrades
# from the affected grub2 packages, we first back up the files in triggerun and
# later restore them in triggerpostun.
# https://bugzilla.redhat.com/show_bug.cgi?id=735259

# Back up the files before uninstalling old grub2
mkdir -p /boot/grub2.tmp &&
mv -f /boot/grub2/*.mod \
      /boot/grub2/*.img \
      /boot/grub2/*.lst \
      /boot/grub2/device.map \
      /boot/grub2.tmp/ || :

%triggerpostun -- grub2 < 1:1.99-4
# ... and restore the files.
test ! -f /boot/grub2/device.map &&
test -d /boot/grub2.tmp &&
mv -f /boot/grub2.tmp/*.mod \
      /boot/grub2.tmp/*.img \
      /boot/grub2.tmp/*.lst \
      /boot/grub2.tmp/device.map \
      /boot/grub2/ &&
rm -r /boot/grub2.tmp/ || :

%files common -f grub.lang
%dir %{_libdir}/grub/
%dir %{_datarootdir}/grub/
%dir %{_datarootdir}/grub/themes/
%exclude %{_datarootdir}/grub/themes/*
%attr(0700,root,root) %dir %{_sysconfdir}/grub.d
%{_prefix}/lib/kernel/install.d/20-grub.install
%{_prefix}/lib/kernel/install.d/99-grub-mkconfig.install
%dir %{_datarootdir}/grub
%exclude %{_datarootdir}/grub/*
%dir /boot/%{name}
%dir /boot/%{name}/themes/
%dir /boot/%{name}/themes/system
%exclude /boot/%{name}/themes/system/*
%attr(0700,root,root) %dir /boot/grub2
%exclude /boot/grub2/*
%dir %attr(0700,root,root) %{efi_esp_dir}
%exclude %{efi_esp_dir}/*
%license COPYING
%ghost %config(noreplace) /boot/grub2/grubenv
%doc INSTALL
%doc NEWS
%doc README
%doc THANKS
%doc TODO
%doc docs/grub.html
%doc docs/grub-dev.html
%doc docs/font_char_metrics.png

%files tools-minimal
%{_sysconfdir}/prelink.conf.d/grub2.conf
%{_sbindir}/%{name}-get-kernel-settings
%attr(4755, root, root) %{_sbindir}/%{name}-set-bootflag
%{_sbindir}/%{name}-set-default
%{_sbindir}/%{name}-set*password
%{_bindir}/%{name}-editenv
%{_bindir}/%{name}-mkpasswd-pbkdf2

%{_datadir}/man/man3/%{name}-get-kernel-settings*
%{_datadir}/man/man8/%{name}-set-default*
%{_datadir}/man/man8/%{name}-set*password*
%{_datadir}/man/man1/%{name}-editenv*
%{_datadir}/man/man1/%{name}-mkpasswd-*

%ifarch x86_64
%files tools-efi
%{_sbindir}/%{name}-macbless
%{_bindir}/%{name}-render-label
%{_datadir}/man/man8/%{name}-macbless*
%{_datadir}/man/man1/%{name}-render-label*
%endif

%files tools
%attr(0644,root,root) %ghost %config(noreplace) %{_sysconfdir}/default/grub
%config %{_sysconfdir}/grub.d/??_*
%ifarch ppc64 ppc64le
%exclude %{_sysconfdir}/grub.d/10_linux
%else
%exclude %{_sysconfdir}/grub.d/10_linux_bls
%endif
%{_sysconfdir}/grub.d/README
%{_userunitdir}/grub-boot-success.timer
%{_userunitdir}/grub-boot-success.service
%{_userunitdir}/timers.target.wants
%{_unitdir}/grub-boot-indeterminate.service
%{_unitdir}/system-update.target.wants
%{_infodir}/%{name}*
%{_datarootdir}/grub/*
%{_sbindir}/%{name}-install
%exclude %{_datarootdir}/grub/themes
%exclude %{_datarootdir}/grub/*.h
%{_datarootdir}/bash-completion/completions/grub
%{_sbindir}/%{name}-mkconfig
%{_sbindir}/%{name}-switch-to-blscfg
%{_sbindir}/%{name}-probe
%{_sbindir}/%{name}-rpm-sort
%{_sbindir}/%{name}-reboot
%{_bindir}/%{name}-file
%{_bindir}/%{name}-menulst2cfg
%{_bindir}/%{name}-mkimage
%{_bindir}/%{name}-mkrelpath
%{_bindir}/%{name}-script-check
%{_datadir}/man/man?/*

# exclude man pages from tools-extra
%exclude %{_datadir}/man/man8/%{name}-sparc64-setup*
%exclude %{_datadir}/man/man8/%{name}-install*
%exclude %{_datadir}/man/man1/%{name}-fstest*
%exclude %{_datadir}/man/man1/%{name}-glue-efi*
%exclude %{_datadir}/man/man1/%{name}-kbdcomp*
%exclude %{_datadir}/man/man1/%{name}-mkfont*
%exclude %{_datadir}/man/man1/%{name}-mklayout*
%exclude %{_datadir}/man/man1/%{name}-mknetdir*
%exclude %{_datadir}/man/man1/%{name}-mkrescue*
%exclude %{_datadir}/man/man1/%{name}-mkstandalone*
%exclude %{_datadir}/man/man1/%{name}-syslinux2cfg*

# exclude man pages from tools-minimal
%exclude %{_datadir}/man/man3/%{name}-get-kernel-settings*
%exclude %{_datadir}/man/man8/%{name}-set-default*
%exclude %{_datadir}/man/man8/%{name}-set*password*
%exclude %{_datadir}/man/man1/%{name}-editenv*
%exclude %{_datadir}/man/man1/%{name}-mkpasswd-*
%exclude %{_datadir}/man/man8/%{name}-macbless*
%exclude %{_datadir}/man/man1/%{name}-render-label*

%if %{with_legacy_arch}
%{_sbindir}/%{name}-install
%ifarch x86_64
%{_sbindir}/%{name}-bios-setup
%else
%exclude %{_sbindir}/%{name}-bios-setup
%exclude %{_datadir}/man/man8/%{name}-bios-setup*
%endif
%ifarch %{sparc}
%{_sbindir}/%{name}-sparc64-setup
%else
%exclude %{_sbindir}/%{name}-sparc64-setup
%exclude %{_datadir}/man/man8/%{name}-sparc64-setup*
%endif
%ifarch %{sparc} ppc ppc64 ppc64le
%{_sbindir}/%{name}-ofpathname
%else
%exclude %{_sbindir}/%{name}-ofpathname
%exclude %{_datadir}/man/man8/%{name}-ofpathname*
%endif
%endif

%files tools-extra
%{_sbindir}/%{name}-sparc64-setup
%{_sbindir}/%{name}-ofpathname
%{_bindir}/%{name}-fstest
%{_bindir}/%{name}-glue-efi
%{_bindir}/%{name}-kbdcomp
%{_bindir}/%{name}-mkfont
%{_bindir}/%{name}-mklayout
%{_bindir}/%{name}-mknetdir
%ifnarch %{sparc}
%{_bindir}/%{name}-mkrescue
%endif
%{_bindir}/%{name}-mkstandalone
%{_bindir}/%{name}-syslinux2cfg
%{_sysconfdir}/sysconfig/grub
%{_datadir}/man/man8/%{name}-sparc64-setup*
%{_datadir}/man/man8/%{name}-install*
%{_datadir}/man/man1/%{name}-fstest*
%{_datadir}/man/man1/%{name}-glue-efi*
%{_datadir}/man/man1/%{name}-kbdcomp*
%{_datadir}/man/man1/%{name}-mkfont*
%{_datadir}/man/man1/%{name}-mklayout*
%{_datadir}/man/man1/%{name}-mknetdir*
%{_datadir}/man/man1/%{name}-mkrescue*
%{_datadir}/man/man1/%{name}-mkstandalone*
%{_datadir}/man/man8/%{name}-ofpathname*
%{_datadir}/man/man1/%{name}-syslinux2cfg*
%exclude %{_datarootdir}/grub/themes/starfield

%if 0%{with_efi_arch}
%{expand:%define_efi_variant_files %%{package_arch} %%{grubefiname} %%{grubeficdname} %%{grubefiarch} %%{target_cpu_name} %%{grub_target_name}}
%endif
%if 0%{with_alt_efi_arch}
%{expand:%define_efi_variant_files %%{alt_package_arch} %%{grubaltefiname} %%{grubalteficdname} %%{grubaltefiarch} %%{alt_target_cpu_name} %%{alt_grub_target_name}}
%endif
%if 0%{with_legacy_arch}
%{expand:%define_legacy_variant_files %%{legacy_package_arch} %%{grublegacyarch}}
%endif

%changelog
* Thu Apr 18 2019 Javier Martinez Canillas <javierm@redhat.com> - 2.02-78
- Add 10_reset_boot_success to Makefile
  Related: rhbz#1701003

* Thu Apr 18 2019 Javier Martinez Canillas <javierm@redhat.com> - 2.02-77
- grub.d: Split out boot success reset from menu auto hide script (lorbus)
  Resolves: rhbz#1701003
- HTTP boot: strncmp returns 0 on equal (stephen)

* Mon Apr 15 2019 Javier Martinez Canillas <javierm@redhat.com> - 2.02-76
- Execute grub2-switch-to-blscfg script in %%posttrans instead of %%post
  Resolves: rhbz#1652806

* Thu Mar 28 2019 Javier Martinez Canillas <javierm@redhat.com> - 2.02-75
- 10_linux_bls: don't add --users option to generated menu entries
  Resolves: rhbz#1693515

* Fri Mar 22 2019 Javier Martinez Canillas <javierm@redhat.com> 2.02-74
- Only set blsdir if /boot/loader/entries is in a btrfs or zfs partition
  Related: rhbz#1688453
- Fix some BLS snippets not being displayed in the GRUB menu
  Resolves: rhbz#1691232

* Tue Mar 12 2019 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 2.02-73
- Never remove boot loader configuration for other boot loaders from the ESP.
  This would render machines with sd-boot unbootable (#1648907).
- Do not mask systemd's kernel-install scriptlets.

* Mon Mar 11 2019 Javier Martinez Canillas <javierm@redhat.com> - 2.02-72
- Avoid grub2-efi package to overwrite existing /boot/grub2/grubenv file
  Resolves: rhbz#1687323
- Switch to BLS in tools package %%post scriptlet
  Resolves: rhbz#1652806

* Wed Feb 27 2019 Javier Martinez Canillas <javierm@redhat.com> - 2.02-71
- 20-grub-install: Replace, rather than overwrite, the existing kernel (pjones)
  Resolves: rhbz#1642402
- 99-grub-mkconfig: Don't update grubenv generating entries on ppc64le
  Related: rhbz#1637875
- blscfg: fallback to default_kernelopts if BLS option field isn't set
  Related: rhbz#1625124
- grub-switch-to-blscfg: copy increment.mod for legacy BIOS and ppc64
  Resolves: rhbz#1652806

* Fri Feb 15 2019 Javier Martinez Canillas <javierm@redhat.com> - 2.02-70
- Check if blsdir exists before attempting to get it's real path
  Resolves: rhbz#1677415

* Wed Feb 13 2019 Javier Martinez Canillas <javierm@redhat.com> - 2.02-69
- Don't make grub_strtoull() print an error if no conversion is performed
  Resolves: rhbz#1674512
- Set blsdir if the BLS directory path isn't one of the looked up by default
  Resolves: rhbz#1657240

* Mon Feb 04 2019 Javier Martinez Canillas <javierm@redhat.com> - 2.02-68
- Don't build the grub2-efi-ia32-* packages on i686 (pjones)
- Add efi-export-env and efi-load-env commands (pjones)
- Make it possible to subtract conditions from debug= (pjones)
- Try to set -fPIE and friends on libgnu.a (pjones)
- Add more options to blscfg command to make it more flexible
- Add support for prepend early initrds to the BLS entries
- Fix grub.cfg-XXX look up when booting over TFTP

* Fri Feb 01 2019 Fedora Release Engineering <releng@fedoraproject.org>
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Mon Dec 17 2018 Javier Martinez Canillas <javierm@redhat.com> - 2.02-66
- Don't exclude /etc/grub.d/01_fallback_counting anymore

* Tue Dec 11 2018 Javier Martinez Canillas <javierm@redhat.com> - 2.02-65
- BLS files should only be copied by grub-switch-to-blscfg if BLS isn't set
  Related: rhbz#1638117
- Fix get_entry_number() wrongly dereferencing the tail pointer
  Resolves: rhbz#1654936
- Make grub2-mkconfig to honour GRUB_CMDLINE_LINUX in /etc/default/grub
  Resolves: rhbz#1637875

* Fri Nov 30 2018 Javier Martinez Canillas <javierm@redhat.com> - 2.02-64
- Add comments and revert logic changes in 01_fallback_counting
- Remove quotes when reading ID value from /etc/os-release
  Related: rhbz#1650706
- blscfg: expand grub_users before passing to grub_normal_add_menu_entry()
  Resolves: rhbz#1650706
- Drop buggy downstream patch "efinet: retransmit if our device is busy"
  Resolves: rhbz#1649048
- Make the menu entry users option argument to be optional
  Related: rhbz#1652434
- 10_linux_bls: add missing menu entries options
  Resolves: rhbz#1652434
- Drop "Be more aggro about actually using the *configured* network device."
  Resolves: rhbz#1654388
- Fix menu entry selection based on title
  Resolves: rhbz#1654936

* Wed Nov 21 2018 Javier Martinez Canillas <javierm@redhat.com> - 2.02-63
- add 10_linux_bls grub.d snippet to generate menu entries from BLS files
  Resolves: rhbz#1636013
- Only set kernelopts in grubenv if it wasn't set before
  Resolves: rhbz#1636466
- kernel-install: Remove existing initramfs if it's older than the kernel (pjones)
  Resolves: rhbz#1638405
- Update the saved entry correctly after a kernel install (pjones)
  Resolves: rhbz#1638117
- blscfg: sort everything with rpm *package* comparison (pjones)
  Related: rhbz#1638103
- blscfg: Make 10_linux_bls sort the same way as well
  Related: rhbz#1638103
- don't set saved_entry on grub2-mkconfig
  Resolves: rhbz#1636466
- Fix menu entry selection based on ID and title (pjones)
  Resolves: rhbz#1640979
- Don't unconditionally set default entry when installing debug kernels
  Resolves: rhbz#1636346
- Remove installkernel-bls script
  Related: rhbz#1647721

* Thu Oct 04 2018 Peter Jones <pjones@redhat.com> - 2.02-62
- Exclude /etc/grub.d/01_fallback_counting until we work through some design
  questions.
  Resolves: rhbz#1614637

* Wed Oct 03 2018 Peter Jones <pjones@redhat.com> - 2.02-61
- Fix the fallback counting script even harder. Apparently, this wasn't
  tested well enough.
  Resolves: rhbz#1614637

* Tue Oct 02 2018 Peter Jones <pjones@redhat.com> - 2.02-60
- Fix grub.cfg boot counting snippet generation (lorbus)
  Resolves: rhbz#1614637
- Fix spurrious allocation error reporting on EFI boot
  Resolves: rhbz#1635319
- Stop doing TPM on BIOS *again*.  It just doesn't work.
  Related: rhbz#1579835
- Make blscfg module loadable on older grub2 i386-pc and powerpc-ieee1275
  builds
- Fix execstack cropping up in grub2-tools
- Ban stack trampolines with compiler flags.

* Tue Sep 25 2018 Hans de Goede <hdegoede@redhat.com> - 2.02-59
- Stop using pkexec for grub2-set-bootflag, it does not work under gdm
  instead make it suid root (it was written with this in mind)

* Tue Sep 25 2018 Peter Jones <pjones@redhat.com>
- Use bounce buffers for addresses above 4GB
- Allow initramfs, cmdline, and params >4GB, but not kernel

* Wed Sep 12 2018 Peter Jones <pjones@redhat.com> - 2.02-58
- Add 2 conditions to boot-success timer and service:
  - Don't run it for system users
  Resolves: rhbz#1592201
  - Don't run it when pkexec isn't available
  Resolves: rhbz#1619445
- Use -Wsign-compare -Wconversion -Wextra in the build.

* Tue Sep 11 2018 Peter Jones <pjones@redhat.com> - 2.02-57
- Limit grub_malloc() on x86_64 to < 31bit addresses, as some devices seem to
  have a colossally broken storage controller (or UEFI driver) that can't do
  DMA to higher memory addresses, but fails silently.
  Resolves: rhbz#1626844 (possibly really resolving it this time.)
- Also integrate Hans's attempt to fix the related error from -54, but do it
  the other way around: try the low addresses first and *then* the high one if
  the allocation fails.  This way we'll get low regions by default, and if
  kernel/initramfs don't fit anywhere, it'll try the higher addresses.
  Related: rhbz#1624532
- Coalesce all the intermediate debugging junk from -54/-55/-56.

* Tue Sep 11 2018 Peter Jones <pjones@redhat.com> - 2.02-56
- Don't mangle fw_path even harder.
  Resolves: rhbz#1626844
- Fix reboot being missing on some platforms, and make it alias to
  "reset" as well.
- More dprintf().

* Mon Sep 10 2018 Peter Jones <pjones@redhat.com> - 2.02-55
- Fix UEFI memory problem in a different way.
  Related: rhbz#1624532
- Don't mangle fw_path with a / unless we're on http
  Resolves: rhbz#1626844

* Fri Sep 07 2018 Kevin Fenzi <kevin@scrye.com> - 2.02-54
- Add patch from https://github.com/rhboot/grub2/pull/30 to fix uefi booting
  Resolves: rhbz#1624532

* Thu Aug 30 2018 Peter Jones <pjones@redhat.com> - 2.02-53
- Fix AArch64 machines with no RAM latched lower than 1GB 
  Resolves: rhbz#1615969
- Set http_path and http_url when HTTP booting
- Hopefully slightly better error reporting in some cases
- Better allocation of kernel+initramfs on x86_64 and aarch64
  Resolves: rhbz#1572126

* Mon Aug 20 2018 Peter Jones <pjones@redhat.com> - 2.02-52
- Update conflicts on grubby not to care about %%{?dist}

* Sun Aug 19 2018 Peter Jones <pjones@redhat.com> - 2.02-51
- Make it quieter.

* Thu Aug 16 2018 Peter Jones <pjones@redhat.com> - 2.02-50
- Fix arm32 off-by-one error on reading the PE header.

* Tue Aug 14 2018 Peter Jones <pjones@redhat.com> - 2.02-50
- Fix typo in /etc/grub.d/01_fallback_counting
  Resolves: rhbz#1614637

* Fri Aug 10 2018 Javier Martinez Canillas <javierm@redhat.com> - 2.02-50
- Add an installkernel script for BLS configurations

* Tue Aug 07 2018 Peter Jones <pjones@redhat.com> - 2.02-49
- Temporarily make -cdboot perms 0700 again.

* Fri Aug 03 2018 Peter Jones <pjones@redhat.com> - 2.02-48
- Kill .note.gnu.property with fire.
  Resolves: rhbz#1612339

* Thu Aug 02 2018 Peter Jones <pjones@redhat.com> - 2.02-47
- Enable armv7 EFI builds.  This was way harder than I expected.

* Tue Jul 17 2018 Peter Jones <pjones@redhat.com> - 2.02-46
- Fix some minor BLS issues
- Rework the FDT module linking to make aarch64 build and boot right

* Mon Jul 16 2018 pjones <pjones@redhat.com> - 2.02-45
- Rework SB patches and 10_linux.in changes even harder.
  Resolves: rhbz#1601578

* Mon Jul 16 2018 Hans de Goede <hdegoede@redhat.com> - 2.02-44
- Make the user session automatically set the boot_success grubenv flag
- Make offline-updates increment the boot_indeterminate grubenv variable

* Mon Jul 16 2018 pjones <pjones@redhat.com> - 2.02-43
- Rework SB patches and 10_linux.in changes

* Fri Jul 13 2018 Peter Jones <pjones@redhat.com> - 2.02-42
- Revert broken moduledir fix *again*.

* Thu Jul 12 2018 Peter Jones <pjones@redhat.com> - 2.02-41
- Fix our linuxefi/linux command reunion.

* Wed Jul 11 2018 Peter Jones <pjones@redhat.com> - 2.02-40
- Port several fixes from the F28 tree and a WIP tree.

* Mon Jul 09 2018 pjones <pjones@redhat.com> - 2.02-39
- Fix my fix of grub2-switch-to-blscfg (javierm and pjones)

* Mon Jul 02 2018 Javier Martinez Canillas <javierm@redhat.com> - 2.02-38
- Use BLS fragment filename as menu entry id and for sort criterion

* Tue Jun 26 2018 Javier Martinez Canillas <javierm@redhat.com>
- Cleanups and fixes for grub2-switch-to-blscfg (pjones)
- Use /boot/loader/entries as BLS dir also on EFI (javierm)

* Tue Jun 19 2018 Peter Jones <pjones@redhat.com> - 2.02-37
- Fix some TPM errors on 32-bit (hdegoede)
- More fixups to avoid compiler changes (pjones)
- Put lsmmap into the EFI builds (pjones)
  Related: rhbz#1572126
- Make 20-grub.install to exit if there is no machine ID set (javierm)
  Resolves: rhbz#1576573
- More fixes for BLS (javierm)
  Resolves: rhbz#1588184

* Wed May 16 2018 Peter Jones <pjones@redhat.com> - 2.02-37.fc29
- Fixups to work with gcc 8
- Experimental https boot support on UEFI
- XFS fixes for sparse inode support
  Resolves: rhbz#1575797

* Thu May 10 2018 Javier Martinez Canillas <javierm@redhat.com> - 2.02-36
- Use version field to sort BLS entries if id field isn't defined
- Add version field to BLS fragments generated by 20-grub.install

* Tue Apr 24 2018 Peter Jones <pjones@redhat.com> - 2.02-35
- A couple of fixes needed by Fedora Atomic - javierm

* Mon Apr 23 2018 Peter Jones <pjones@redhat.com> - 2.02-34
- Put the os-prober dep back in - we need to change test plans and criteria
  before it can go.
  Resolves: rhbz#1569411

* Wed Apr 11 2018 Peter Jones <pjones@redhat.com> - 2.02-33
- Work around some issues with older automake found in CentOS.
- Make multiple initramfs images work in BLS.

* Wed Apr 11 2018 Javier Martinez Canillas <javierm@redhat.com> - 2.02-32
- Make 20-grub.install to generate debug BLS when MAKEDEBUG is set.

* Fri Apr 06 2018 Peter Jones <pjones@redhat.com> - 2.02-31
- Pull in some TPM fixes I missed.

* Fri Apr 06 2018 Peter Jones <pjones@redhat.com> - 2.02-30
- Enable TPM measurements
- Set the default boot entry to the first entry when we're using BLS.

* Tue Apr 03 2018 Peter Jones <pjones@redhat.com> - 2.02-29
- Fix for BLS paths on BIOS / non-UEFI (javierm)

* Fri Mar 16 2018 Peter Jones <pjones@redhat.com> - 2.02-28
- Install kernel-install scripts. (javierm)
- Add grub2-switch-to-blscfg

* Tue Mar 06 2018 Peter Jones <pjones@redhat.com> - 2.02-27
- Build the blscfg module in on EFI builds.

* Wed Feb 28 2018 Peter Jones <pjones@redhat.com> - 2.02-26
- Try to fix things for new compiler madness.
  I really don't know why gcc decided __attribute__((packed)) on a "typedef
  struct" should imply __attribute__((align (1))) and that it should have a
  warning that it does so.  The obvious behavior would be to keep the alignment
  of the first element unless it's used in another object or type that /also/
  hask the packed attribute.  Why should it change the default alignment at
  all?
- Merge in the BLS patches Javier and I wrote.
- Attempt to fix pmtimer initialization failures to not be super duper slow.

* Fri Feb 09 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org>
- Escape macros in %%changelog

* Tue Jan 23 2018 Peter Jones <pjones@redhat.com> - 2.02-24
- Fix a merge error from 2.02-21 that affected kernel loading on Aarch64.
  Related: rhbz#1519311
  Related: rhbz#1506704
  Related: rhbz#1502312

* Fri Jan 19 2018 Peter Jones <pjones@redhat.com> - 2.02-23
- Only nerf annobin, not -fstack-crash-protection.
- Fix a conflict on /boot/efi directory permissions between -cdboot and the
  normal bootloader.

* Thu Jan 18 2018 Peter Jones <pjones@redhat.com> - 2.02-22
- Nerf some gcc 7.2.1-6 'features' that cause grub to crash on start.

* Thu Jan 18 2018 Peter Jones <pjones@redhat.com> - 2.02-21
- Fix grub2-efi-modules provides/obsoletes generation
  Resolves: rhbz#1506704
- *Also* build grub-efi-ia32{,-*,!-modules} packages for i686 builds
  Resolves: rhbz#1502312
- Make everything under /boot/efi be mode 0700, since that's what FAT will
  show anyway.

* Wed Jan 17 2018 Peter Jones <pjones@redhat.com> - 2.02-20
- Update to newer upstream for F28
- Pull in patches for Apollo Lake hardware
  Resolves: rhbz#1519311

* Tue Oct 24 2017 Peter Jones <pjones@redhat.com> - 2.02-19
- Handle xen module loading (somewhat) better
  Resolves: rhbz#1486002

* Wed Sep 20 2017 Peter Jones <pjones@redhat.com> - 2.02-18
- Make grub2-efi-aa64 provide grub2
  Resolves: rhbz#1491045

* Mon Sep 11 2017 Dennis Gilmore <dennis@ausil.us> - 2.02-17
- bump for Obsoletes again

* Wed Sep 06 2017 Peter Jones <pjones@redhat.com> - 2.02-16
- Fix Obsoletes on grub2-pc

* Wed Aug 30 2017 Petr Šabata <contyk@redhat.com> - 2.02-15
- Limit the pattern matching in do_alt_efi_install to files to
  unbreak module builds

* Fri Aug 25 2017 Peter Jones <pjones@redhat.com> - 2.02-14
- Revert the /usr/lib/.build-id/ change:
  https://fedoraproject.org/wiki/Changes/ParallelInstallableDebuginfo
  says (without any particularly convincing reasoning):
    The main build-id file should not be in the debuginfo file, but in the
    main package (this was always a problem since the package and debuginfo
    package installed might not match). If we want to make usr/lib/debug/ a
    network resource then we will need to move the symlink to another
    location (maybe /usr/lib/.build-id).
  So do it that way.  Of course it doesn't matter, because exclude gets
  ignored due to implementation details.

* Fri Aug 25 2017 Peter Jones <pjones@redhat.com> - 2.02-13
- Add some unconditional Provides:
  grub2-efi on grub2-efi-${arch}
  grub2-efi-cdboot on grub2-efi-${arch}-cdboot
  grub2 on all grub2-${arch} pacakges
- Something is somehow adding /usr/lib/.build-id/... to all the -tools
  subpackages, so exclude all that.

* Thu Aug 24 2017 Peter Jones <pjones@redhat.com> - 2.02-12
- Fix arm kernel command line allocation
  Resolves: rhbz#1484609
- Get rid of the temporary extra efi packages hack.

* Wed Aug 23 2017 Peter Jones <pjones@redhat.com> - 2.02-11
- Put grub2-mkimage in -tools, not -tools-extra.
- Fix i686 building
- Fix ppc HFS+ usage due to /boot/efi's presence.

* Fri Aug 18 2017 Peter Jones <pjones@redhat.com> - 2.02-10
- Add the .img files into grub2-pc-modules (and all legacy variants)

* Wed Aug 16 2017 Peter Jones <pjones@redhat.com> - 2.02-9
- Re-work for ia32-efi.

* Wed Aug 16 2017 pjones <pjones@redhat.com> - 2.02-8
- Rebased to newer upstream for fedora-27

* Tue Aug 15 2017 Peter Jones <pjones@redhat.com> - 2.02-7
- Rebuild again with new fixed rpm. (bug #1480407)

* Fri Aug 11 2017 Kevin Fenzi <kevin@scrye.com> - 2.02-6
- Rebuild again with new fixed rpm. (bug #1480407)

* Thu Aug 10 2017 Kevin Fenzi <kevin@scrye.com> - 2.02-5
- Rebuild for rpm soname bump again.

* Thu Aug 10 2017 Igor Gnatenko <ignatenko@redhat.com> - 2.02-4
- Rebuilt for RPM soname bump

* Thu Aug 03 2017 Peter Jones <pjones@redhat.com> - 2.02-3
- Rebuild so it gets SB signed correctly.
  Related: rhbz#1335533
- Enable lsefi

* Mon Jul 24 2017 Michael Cronenworth <mike@cchtml.com> - 2.02-2
- Fix symlink to work on both EFI and BIOS machines
  Resolves: rhbz#1335533

* Mon Jul 10 2017 Peter Jones <pjones@redhat.com> - 2.02-1
- Rebased to newer upstream for fedora-27

* Wed Feb 01 2017 Stephen Gallagher <sgallagh@redhat.com> - 2.02-0.39
- Add missing %%license macro
- Fix deps that should have moved to -tools but didn't.

* Thu Dec 08 2016 Peter Jones <pjones@redhat.com> - 2.02-0.38
- Fix regexp in power compile flags, and synchronize release number with
  other branches.

* Fri Dec 02 2016 pjones <pjones@redhat.com> - 1:2.02-0.37
- Rebased to newer upstream for fedora-26

* Thu Dec 01 2016 Peter Jones <pjones@redhat.com> - 2.02-0.36
- Update version to .36 because I already built an f25 one named 0.35

* Thu Dec 01 2016 pjones <pjones@redhat.com> - 1:2.02-0.35
- Rebased to newer upstream for fedora-26

* Thu Dec 01 2016 Peter Jones <pjones@redhat.com> - 2.02-0.34
- Fix power6 makefile bits for newer autoconf defaults.
- efi/chainloader: fix wrong sanity check in relocate_coff() (Laszlo Ersek)
  Resolves: rhbz#1347291

* Thu Aug 25 2016 Peter Jones <pjones@redhat.com> - 2.02-0.34
- Update to be newer than f24's branch.
- Add grub2-get-kernel-settings
  Related: rhbz#1226325

* Thu Apr 07 2016 pjones <pjones@redhat.com> - 1:2.02-0.30
- Revert 27e66193, which was replaced by upstream's 49426e9fd
  Resolves: rhbz#1251600

* Thu Apr 07 2016 Peter Jones <pjones@redhat.com> - 2.02-0.29
- Fix ppc64 build failure and rebase to newer f24 code.

* Tue Apr 05 2016 pjones <pjones@redhat.com> - 1:2.02-0.27
- Pull TPM updates from mjg59.
  Resolves: rhbz#1318067

* Tue Mar 08 2016 pjones <pjones@redhat.com> - 1:2.02-0.27
- Fix aarch64 build problem.

* Fri Mar 04 2016 Peter Jones <pjones@redhat.com> - 2.02-0.26
- Rebased to newer upstream (grub-2.02-beta3) for fedora-24

* Thu Dec 10 2015 Peter Jones <pjones@redhat.com> - 2.02-0.25
- Fix security issue when reading username and password
  Related: CVE-2015-8370
- Do a better job of handling GRUB2_PASSWORD
  Related: rhbz#1284370

* Fri Nov 20 2015 Peter Jones <pjones@redhat.com> - 2.02-0.24
- Rebuild without multiboot* modules in the EFI image.
  Related: rhbz#1264103

* Sat Sep 05 2015 Kalev Lember <klember@redhat.com> - 2.02-0.23
- Rebuilt for librpm soname bump

* Wed Aug 05 2015 Peter Jones <pjones@redhat.com> - 2.02-0.21
- Back out one of the debuginfo generation patches; it doesn't work right on
  aarch64 yet.
  Resolves: rhbz#1250197

* Mon Aug 03 2015 Peter Jones <pjones@redhat.com> - 2.02-0.20
- The previous fix was completely not right, so fix it a different way.
  Resolves: rhbz#1249668

* Fri Jul 31 2015 Peter Jones <pjones@redhat.com> - 2.02-0.19
- Fix grub2-mkconfig's sort to put kernels in the right order.
  Related: rhbz#1124074

* Thu Jul 30 2015 Peter Jones <pjones@redhat.com> - 2.02-0.18
- Fix a build failure on aarch64

* Wed Jul 22 2015 Peter Jones <pjones@redhat.com> - 2.02-0.17
- Don't build hardened (fixes FTBFS) (pbrobinson)
- Reconcile with the current upstream
- Fixes for gcc 5

* Tue Apr 28 2015 Peter Jones <pjones@redhat.com> - 2.02-0.16
- Make grub2-mkconfig produce the kernel titles we actually want.
  Resolves: rhbz#1215839

* Sat Feb 21 2015 Till Maas <opensource@till.name>
- Rebuilt for Fedora 23 Change
  https://fedoraproject.org/wiki/Changes/Harden_all_packages_with_position-independent_code

* Mon Jan 05 2015 Peter Jones <pjones@redhat.com> - 2.02-0.15
- Bump release to rebuild with Ralf Corsépius's fixes.

* Sun Jan 04 2015 Ralf Corsépius <corsepiu@fedoraproject.org> - 2.02-0.14
- Move grub2.info/grub2-dev.info install-info scriptlets into *-tools package.
- Use sub-shell in %%__debug_install_post (RHBZ#1168732).
- Cleanup grub2-starfield-theme packaging.

* Thu Dec 04 2014 Peter Jones <pjones@redhat.com> - 2.02-0.13
- Update minilzo to 2.08 for CVE-2014-4607
  Resolves: rhbz#1131793

* Thu Nov 13 2014 Peter Jones <pjones@redhat.com> - 2.02-0.12
- Make backtrace and usb conditional on !arm
- Make sure gcdaa64.efi is packaged.
  Resolves: rhbz#1163481

* Fri Nov 07 2014 Peter Jones <pjones@redhat.com> - 2.02-0.11
- fix a copy-paste error in patch 0154.
  Resolves: rhbz#964828

* Mon Oct 27 2014 Peter Jones <pjones@redhat.com> - 2.02-0.10
- Try to emit linux16/initrd16 and linuxefi/initrdefi when appropriate
  in 30_os-prober.
  Resolves: rhbz#1108296
- If $fw_path doesn't work to find the config file, try $prefix as well
  Resolves: rhbz#1148652

* Mon Sep 29 2014 Peter Jones <pjones@redhat.com> - 2.02-0.9
- Clean up the build a bit to make it faster
- Make grubenv work right on UEFI machines
  Related: rhbz#1119943
- Sort debug and rescue kernels later than normal ones
  Related: rhbz#1065360
- Allow "fallback" to include entries by title as well as number.
  Related: rhbz#1026084
- Fix a segfault on aarch64.
- Load arm with SB enabled if available.
- Add some serial port options to GRUB_MODULES.

* Tue Aug 19 2014 Peter Jones <pjones@redhat.com> - 2.02-0.8
- Add ppc64le support.
  Resolves: rhbz#1125540

* Thu Jul 24 2014 Peter Jones <pjones@redhat.com> - 2.02-0.7
- Enabled syslinuxcfg module.

* Wed Jul 02 2014 Peter Jones <pjones@redhat.com> - 2.02-0.6
- Re-merge RHEL 7 changes and ARM works in progress.

* Mon Jun 30 2014 Peter Jones <pjones@redhat.com> - 2.02-0.5
- Avoid munging raw spaces when we're escaping command line arguments.
  Resolves: rhbz#923374

* Tue Jun 24 2014 Peter Jones <pjones@redhat.com> - 2.02-0.4
- Update to latest upstream.

* Thu Mar 13 2014 Peter Jones <pjones@redhat.com> - 2.02-0.3
- Merge in RHEL 7 changes and ARM works in progress.

* Mon Jan 06 2014 Peter Jones <pjones@redhat.com> - 2.02-0.2
- Update to grub-2.02~beta2

* Sat Aug 10 2013 Peter Jones <pjones@redhat.com> - 2.00-25
- Last build failed because of a hardware error on the builder.

* Mon Aug 05 2013 Peter Jones <pjones@redhat.com> - 2.00-24
- Fix compiler flags to deal with -fstack-protector-strong

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:2.00-24
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Tue Jul 02 2013 Dennis Gilmore <dennis@ausil.us> - 2.00-23
- add epoch to obsoletes

* Fri Jun 21 2013 Peter Jones <pjones@redhat.com> - 2.00-22
- Fix linewrapping in edit menu.
  Resolves: rhbz #976643

* Thu Jun 20 2013 Peter Jones <pjones@redhat.com> - 2.00-21
- Fix obsoletes to pull in -starfield-theme subpackage when it should.

* Fri Jun 14 2013 Peter Jones <pjones@redhat.com> - 2.00-20
- Put the theme entirely ento the subpackage where it belongs (#974667)

* Wed Jun 12 2013 Peter Jones <pjones@redhat.com> - 2.00-19
- Rebase to upstream snapshot.
- Fix PPC build error (#967862)
- Fix crash on net_bootp command (#960624)
- Reset colors on ppc when appropriate (#908519)
- Left align "Loading..." messages (#908492)
- Fix probing of SAS disks on PPC (#953954)
- Add support for UEFI OSes returned by os-prober
- Disable "video" mode on PPC for now (#973205)
- Make grub fit better into the boot sequence, visually (#966719)

* Fri May 10 2013 Matthias Clasen <mclasen@redhat.com> - 2.00-18
- Move the starfield theme to a subpackage (#962004)
- Don't allow SSE or MMX on UEFI builds (#949761)

* Wed Apr 24 2013 Peter Jones <pjones@redhat.com> - 2.00-17.pj0
- Rebase to upstream snapshot.

* Thu Apr 04 2013 Peter Jones <pjones@redhat.com> - 2.00-17
- Fix booting from drives with 4k sectors on UEFI.
- Move bash completion to new location (#922997)
- Include lvm support for /boot (#906203)

* Thu Feb 14 2013 Peter Jones <pjones@redhat.com> - 2.00-16
- Allow the user to disable submenu generation
- (partially) support BLS-style configuration stanzas.

* Tue Feb 12 2013 Peter Jones <pjones@redhat.com> - 2.00-15.pj0
- Add various config file related changes.

* Thu Dec 20 2012 Dennis Gilmore <dennis@ausil.us> - 2.00-15
- bump nvr

* Mon Dec 17 2012 Karsten Hopp <karsten@redhat.com> 2.00-14
- add bootpath device to the device list (pfsmorigo, #886685)

* Tue Nov 27 2012 Peter Jones <pjones@redhat.com> - 2.00-13
- Add vlan tag support (pfsmorigo, #871563)
- Follow symlinks during PReP installation in grub2-install (pfsmorigo, #874234)
- Improve search paths for config files on network boot (pfsmorigo, #873406)

* Tue Oct 23 2012 Peter Jones <pjones@redhat.com> - 2.00-12
- Don't load modules when grub transitions to "normal" mode on UEFI.

* Mon Oct 22 2012 Peter Jones <pjones@redhat.com> - 2.00-11
- Rebuild with newer pesign so we'll get signed with the final signing keys.

* Thu Oct 18 2012 Peter Jones <pjones@redhat.com> - 2.00-10
- Various PPC fixes.
- Fix crash fetching from http (gustavold, #860834)
- Issue separate dns queries for ipv4 and ipv6 (gustavold, #860829)
- Support IBM CAS reboot (pfsmorigo, #859223)
- Include all modules in the core image on ppc (pfsmorigo, #866559)

* Mon Oct 01 2012 Peter Jones <pjones@redhat.com> - 1:2.00-9
- Work around bug with using "\x20" in linux command line.
  Related: rhbz#855849

* Thu Sep 20 2012 Peter Jones <pjones@redhat.com> - 2.00-8
- Don't error on insmod on UEFI/SB, but also don't do any insmodding.
- Increase device path size for ieee1275
  Resolves: rhbz#857936
- Make network booting work on ieee1275 machines.
  Resolves: rhbz#857936

* Wed Sep 05 2012 Matthew Garrett <mjg@redhat.com> - 2.00-7
- Add Apple partition map support for EFI

* Thu Aug 23 2012 David Cantrell <dcantrell@redhat.com> - 2.00-6
- Only require pesign on EFI architectures (#851215)

* Tue Aug 14 2012 Peter Jones <pjones@redhat.com> - 2.00-5
- Work around AHCI firmware bug in efidisk driver.
- Move to newer pesign macros
- Don't allow insmod if we're in secure-boot mode.

* Wed Aug 08 2012 Peter Jones <pjones@redhat.com>
- Split module lists for UEFI boot vs UEFI cd images.
- Add raid modules for UEFI image (related: #750794)
- Include a prelink whitelist for binaries that need execstack (#839813)
- Include fix efi memory map fix from upstream (#839363)

* Wed Aug 08 2012 Peter Jones <pjones@redhat.com> - 2.00-4
- Correct grub-mkimage invocation to use efidir RPM macro (jwb)
- Sign with test keys on UEFI systems.
- PPC - Handle device paths with commas correctly.
  Related: rhbz#828740

* Wed Jul 25 2012 Peter Jones <pjones@redhat.com> - 2.00-3
- Add some more code to support Secure Boot, and temporarily disable
  some other bits that don't work well enough yet.
  Resolves: rhbz#836695

* Wed Jul 11 2012 Matthew Garrett <mjg@redhat.com> - 2.00-2
- Set a prefix for the image - needed for installer work
- Provide the font in the EFI directory for the same reason

* Thu Jun 28 2012 Peter Jones <pjones@redhat.com> - 2.00-1
- Rebase to grub-2.00 release.

* Mon Jun 18 2012 Peter Jones <pjones@redhat.com> - 2.0-0.37.beta6
- Fix double-free in grub-probe.

* Wed Jun 06 2012 Peter Jones <pjones@redhat.com> - 2.0-0.36.beta6
- Build with patch19 applied.

* Wed Jun 06 2012 Peter Jones <pjones@redhat.com> - 2.0-0.35.beta6
- More ppc fixes.

* Wed Jun 06 2012 Peter Jones <pjones@redhat.com> - 2.0-0.34.beta6
- Add IBM PPC fixes.

* Mon Jun 04 2012 Peter Jones <pjones@redhat.com> - 2.0-0.33.beta6
- Update to beta6.
- Various fixes from mads.

* Fri May 25 2012 Peter Jones <pjones@redhat.com> - 2.0-0.32.beta5
- Revert builddep change for crt1.o; it breaks ppc build.

* Fri May 25 2012 Peter Jones <pjones@redhat.com> - 2.0-0.31.beta5
- Add fwsetup command (pjones)
- More ppc fixes (IBM)

* Tue May 22 2012 Peter Jones <pjones@redhat.com> - 2.0-0.30.beta5
- Fix the /other/ grub2-tools require to include epoch.

* Mon May 21 2012 Peter Jones <pjones@redhat.com> - 2.0-0.29.beta5
- Get rid of efi_uga and efi_gop, favoring all_video instead.

* Mon May 21 2012 Peter Jones <pjones@redhat.com> - 2.0-0.28.beta5
- Name grub.efi something that's arch-appropriate (kiilerix, pjones)
- use EFI/$SOMETHING_DISTRO_BASED/ not always EFI/redhat/grub2-efi/ .
- move common stuff to -tools (kiilerix)
- spec file cleanups (kiilerix)

* Mon May 14 2012 Peter Jones <pjones@redhat.com> - 2.0-0.27.beta5
- Fix module trampolining on ppc (benh)

* Thu May 10 2012 Peter Jones <pjones@redhat.com> - 2.0-0.27.beta5
- Fix license of theme (mizmo)
  Resolves: rhbz#820713
- Fix some PPC bootloader detection IBM problem
  Resolves: rhbz#820722

* Thu May 10 2012 Peter Jones <pjones@redhat.com> - 2.0-0.26.beta5
- Update to beta5.
- Update how efi building works (kiilerix)
- Fix theme support to bring in fonts correctly (kiilerix, pjones)

* Wed May 09 2012 Peter Jones <pjones@redhat.com> - 2.0-0.25.beta4
- Include theme support (mizmo)
- Include locale support (kiilerix)
- Include html docs (kiilerix)

* Thu Apr 26 2012 Peter Jones <pjones@redhat.com> - 2.0-0.24
- Various fixes from Mads Kiilerich

* Thu Apr 19 2012 Peter Jones <pjones@redhat.com> - 2.0-0.23
- Update to 2.00~beta4
- Make fonts work so we can do graphics reasonably

* Thu Mar 29 2012 David Aquilina <dwa@redhat.com> - 2.0-0.22
- Fix ieee1275 platform define for ppc

* Thu Mar 29 2012 Peter Jones <pjones@redhat.com> - 2.0-0.21
- Remove ppc excludearch lines (dwa)
- Update ppc terminfo patch (hamzy)

* Wed Mar 28 2012 Peter Jones <pjones@redhat.com> - 2.0-0.20
- Fix ppc64 vs ppc exclude according to what dwa tells me they need
- Fix version number to better match policy.

* Tue Mar 27 2012 Dan Horák <dan[at]danny.cz> - 1.99-19.2
- Add support for serial terminal consoles on PPC by Mark Hamzy

* Sun Mar 25 2012 Dan Horák <dan[at]danny.cz> - 1.99-19.1
- Use Fix-tests-of-zeroed-partition patch by Mark Hamzy

* Thu Mar 15 2012 Peter Jones <pjones@redhat.com> - 1.99-19
- Use --with-grubdir= on configure to make it behave like -17 did.

* Wed Mar 14 2012 Peter Jones <pjones@redhat.com> - 1.99-18
- Rebase from 1.99 to 2.00~beta2

* Wed Mar 07 2012 Peter Jones <pjones@redhat.com> - 1.99-17
- Update for newer autotools and gcc 4.7.0
  Related: rhbz#782144
- Add /etc/sysconfig/grub link to /etc/default/grub
  Resolves: rhbz#800152
- ExcludeArch s390*, which is not supported by this package.
  Resolves: rhbz#758333

* Fri Feb 17 2012 Orion Poplawski <orion@cora.nwra.com> - 1:1.99-16
- Build with -Os (bug 782144)

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:1.99-15
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Wed Dec 14 2011 Matthew Garrett <mjg@redhat.com> - 1.99-14
- fix up various grub2-efi issues

* Thu Dec 08 2011 Adam Williamson <awilliam@redhat.com> - 1.99-13
- fix hardwired call to grub-probe in 30_os-prober (rhbz#737203)

* Mon Nov 07 2011 Peter Jones <pjones@redhat.com> - 1.99-12
- Lots of .spec fixes from Mads Kiilerich:
  Remove comment about update-grub - it isn't run in any scriptlets
  patch info pages so they can be installed and removed correctly when renamed
  fix references to grub/grub2 renames in info pages (#743964)
  update README.Fedora (#734090)
  fix comments for the hack for upgrading from grub2 < 1.99-4
  fix sed syntax error preventing use of $RPM_OPT_FLAGS (#704820)
  make /etc/grub2*.cfg %%config(noreplace)
  make grub.cfg %%ghost - an empty file is of no use anyway
  create /etc/default/grub more like anaconda would create it (#678453)
  don't create rescue entries by default - grubby will not maintain them anyway
  set GRUB_SAVEDEFAULT=true so saved defaults works (rbhz#732058)
  grub2-efi should have its own bash completion
  don't set gfxpayload in efi mode - backport upstream r3402
- Handle dmraid better. Resolves: rhbz#742226

* Wed Oct 26 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:1.99-11
- Rebuilt for glibc bug#747377

* Wed Oct 19 2011 Adam Williamson <awilliam@redhat.com> - 1.99-10
- /etc/default/grub is explicitly intended for user customization, so
  mark it as config(noreplace)

* Tue Oct 11 2011 Peter Jones <pjones@redhat.com> - 1.99-9
- grub has an epoch, so we need that expressed in the obsolete as well.
  Today isn't my day.

* Tue Oct 11 2011 Peter Jones <pjones@redhat.com> - 1.99-8
- Fix my bad obsoletes syntax.

* Thu Oct 06 2011 Peter Jones <pjones@redhat.com> - 1.99-7
- Obsolete grub
  Resolves: rhbz#743381

* Wed Sep 14 2011 Peter Jones <pjones@redhat.com> - 1.99-6
- Use mv not cp to try to avoid moving disk blocks around for -5 fix
  Related: rhbz#735259
- handle initramfs on xen better (patch from Marko Ristola)
  Resolves: rhbz#728775

* Sat Sep 03 2011 Kalev Lember <kalevlember@gmail.com> - 1.99-5
- Fix upgrades from grub2 < 1.99-4 (#735259)

* Fri Sep 02 2011 Peter Jones <pjones@redhat.com> - 1.99-4
- Don't do sysadminny things in %%preun or %%post ever. (#735259)
- Actually include the changelog in this build (sorry about -3)

* Thu Sep 01 2011 Peter Jones <pjones@redhat.com> - 1.99-2
- Require os-prober (#678456) (patch from Elad Alfassa)
- Require which (#734959) (patch from Elad Alfassa)

* Thu Sep 01 2011 Peter Jones <pjones@redhat.com> - 1.99-1
- Update to grub-1.99 final.
- Fix crt1.o require on x86-64 (fix from Mads Kiilerich)
- Various CFLAGS fixes (from Mads Kiilerich)
  - -fexceptions and -m64
- Temporarily ignore translations (from Mads Kiilerich)

* Thu Jul 21 2011 Peter Jones <pjones@redhat.com> - 1.99-0.3
- Use /sbin not /usr/sbin .

* Thu Jun 23 2011 Peter Lemenkov <lemenkov@gmail.com> - 1:1.99-0.2
- Fixes for ppc and ppc64

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:1.98-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild
