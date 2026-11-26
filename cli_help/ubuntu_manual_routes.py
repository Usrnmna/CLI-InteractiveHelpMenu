"""Fixed manual-only lookup for Ubuntu inventory roots without a reviewed executable probe."""


MANUAL_ONLY = frozenset("""
. 3cpio : GET HEAD ModemManager NetworkManager POST VGAuthService Xwayland [ aa-enabled aa-exec
aa-features-abi aa-load aa-remove-unknown aa-status aa-teardown accessdb aconnect acpidbg
add-apt-repository add-shell addgnupghome addgroup addpart addr2line adduser agetty airscan-discover
alias alsa alsa-info alsabat alsabat-test alsactl alsaloop alsamixer alsatplg alsaucm amidi amixer
anacron ansible apache2ctl aplay aplaymidi aplaymidi2 apparmor_parser apparmor_status applygnupgdefaults
apport-bug apport-cli apport-collect apport-unpack appres appstreamcli apropos apt-add-repository
apt-cdrom apt-file aptd aptdcon aptitude ar arch arecord arecordmidi arecordmidi2 argdist-bpfcc aria2c
arm2hpdl arpd arptables arptables-nft arptables-nft-restore arptables-nft-save arptables-restore
arptables-save arptables-translate as aseqdump aseqnet aseqsend aspell aspell-autobuildhash
aspell-import atop automat-visualize3 avahi-daemon awk axfer b2sum badblocks baobab base32 base64
basename basenc bash bashbug bashreadline-bpfcc bashreadline.bt batcat bc bcache-super-show bdftopcf
bdftruncate bg bind bindsnoop-bpfcc biolatency-bpfcc biolatency-kp.bt biolatency.bt biolatpcts-bpfcc
biopattern-bpfcc biosdecode biosnoop-bpfcc biosnoop.bt biostacks.bt biotop-bpfcc bitesize-bpfcc
bitesize.bt bits blkdeactivate blkdiscard blkid blkpr blkzone blockdev bluemoon bluetooth-sendto
bluetoothctl bluetoothd boltctl bpflist-bpfcc bpftool bpftrace bpftrace-aotrt break bridge brltty
brltty-atb brltty-clip brltty-ctb brltty-hid brltty-ktb brltty-lscmds brltty-morse brltty-setup
brltty-trtxt brltty-ttb brltty-tune broadwayd browse btattach btmgmt btmon btop btrfs btrfs-convert
btrfs-find-root btrfs-image btrfs-map-logical btrfs-select-super btrfsck btrfsdist-bpfcc
btrfsslower-bpfcc btrfstune buildah builtin bunzip2 busctl busybox bwrap bzcat bzcmp bzdiff bzegrep
bzexe bzfgrep bzgrep bzip2 bzip2recover bzless bzmore c++filt c_rehash cache_check cache_dump
cache_metadata_size cache_repair cache_restore cache_writeback cachestat-bpfcc cachetop-bpfcc caddy
calibrate_ppa caller canberra-gtk-play cancel capable-bpfcc capable.bt capsh captoinfo cat catman cd
cd-create-profile cd-fix-profile cd-iccdump cd-it8 certbot cfdisk cftp3 cgdisk chacl chage chardet
chardetect chat chattr chcon chcpu check-language-support chfn chgpasswd chgrp chmem chmod choom chown
chpasswd chronyc chronyd chroot chrt chsh chvt cifsiostat ciptool ckbcomp ckeygen3 cksum clang++ clear
clear_console cloud-id cloud-init cloud-init-per cmp cobjnew-bpfcc codepage col colcrt coldreboot
colormgr colrm column comm command compactsnoop-bpfcc compare compgen complete compopt conch3 continue
corelist coresched coreutils cpan cpan5.40-x86_64-linux-gnu cpio cpp cpp-15 cpudist-bpfcc cpupower
cpuunclaimed-bpfcc cpuwalk.bt cracklib-check cracklib-format cracklib-packer cracklib-unpacker crash
create-cracklib-dict criticalstat-bpfcc cron crontab cryptdisks_start cryptdisks_stop cryptsetup csplit
ctest ctrlaltdel ctstat cups-browsed cupsaccept cupsctl cupsd cupsdisable cupsenable cupsfilter
cupsreject cupstestppd cut cvtsudoers.ws dash date dbslower-bpfcc dbstat-bpfcc dbus-cleanup-sockets
dbus-daemon dbus-monitor dbus-run-session dbus-send dbus-update-activation-environment dbus-uuidgen
dbxtool dc dcb dconf dcsnoop-bpfcc dcsnoop.bt dcstat-bpfcc dd ddstdecode deadlock-bpfcc deallocvt
deb-systemd-helper deb-systemd-invoke debconf debconf-apt-progress debconf-communicate debconf-copydb
debconf-escape debconf-set-selections debconf-show debian-distro-info debugfs declare deja-dup delgroup
delpart deluser delv depmod desktop-file-edit desktop-file-install desktop-file-validate
desktop-security-center devlink dh_bash-completion dh_installxmlcatalogs dh_perl_openssl dhcpcd diff
diff3 dig dir dircolors direnv dirmngr dirmngr-client dirname dirs dirtop-bpfcc disown distro-info dmesg
dmeventd dmidecode dmsetup dmstats dnsdomainname dnsmasq do-release-upgrade domainname dos2unix dosfsck
dosfslabel dpkg-divert dpkg-maintscript-helper dpkg-preconfigure dpkg-realpath dpkg-reconfigure
dpkg-split dpkg-statoverride dpkg-trigger dpll dracut dracut-catimages driverless driverless-fax
drsnoop-bpfcc dump.exfat dumpe2fs dumpkeys dvipdf e2freefrag e2fsck e2image e2label e2mmpstatus e2scrub
e2scrub_all e2undo e4crypt e4defrag eatmydata ebtables ebtables-nft ebtables-nft-restore
ebtables-nft-save ebtables-restore ebtables-save ebtables-translate ec2metadata echo ed editor editres
egrep eject elfedit enable enc2xs encguess enchant-2 enchant-lsmod-2 enosys env envsubst eps2eps eqn
era_check era_dump era_invalidate era_restore esc-m ethtool eutp eval ex exch exec execsnoop-bpfcc
execsnoop.bt exfat2img exfatlabel exiftool exit exitsnoop-bpfcc expand expect expiry export expr
ext4dist-bpfcc ext4slower-bpfcc eza f2fsslower-bpfcc factor fadvise fail2ban-client faillock fallocate
false fatlabel fc fc-cache fc-cat fc-conflist fc-list fc-match fc-pattern fc-query fc-scan fc-validate
fdisk fg fgconsole fgrep file file-roller file2brl filefrag filegone-bpfcc filelife-bpfcc
fileslower-bpfcc filetop-bpfcc finalrd fincore findfs findmnt firefox firefox.geckodriver
firmware-updater fish fixparts flock fmt fold fonttosfnt foo2ddst foo2ddst-wrapper foo2hbpl2
foo2hbpl2-wrapper foo2hiperc foo2hiperc-wrapper foo2hp foo2hp2600-wrapper foo2lava foo2lava-wrapper
foo2oak foo2oak-wrapper foo2qpdl foo2qpdl-wrapper foo2slx foo2slx-wrapper foo2xqx foo2xqx-wrapper
foo2zjs foo2zjs-icc2ps foo2zjs-pstops foo2zjs-wrapper foomatic-rip fprintd-delete fprintd-enroll
fprintd-list fprintd-verify free fsadm fsck fsck.btrfs fsck.cramfs fsck.exfat fsck.ext2 fsck.ext3
fsck.ext4 fsck.fat fsck.minix fsck.msdos fsck.vfat fsck.xfs fsfreeze fstab-decode fstrim ftp
funccount-bpfcc funcinterval-bpfcc funclatency-bpfcc funcslower-bpfcc funzip fuser fusermount
fusermount3 fwupdmgr fwupdtool g++ gamemode-simulate-game gamemoded gamemodelist gamemoderun
gamma4scanimage gapplication gatttool gawk gawkbug gcalccmd gcore gcr-viewer gcr-viewer-gtk4 gdb
gdb-add-index gdbtui gdbus gdctl gdisk gdk-pixbuf-csource gdk-pixbuf-pixdata gdm-config gdm3 geckodriver
gencat genl geqn getcap getconf getent getfacl gethostlatency-bpfcc gethostlatency.bt getkeycodes getopt
getopts getpcaps gettext gettext.sh getty getweb ghostscript ginstall-info gio gio-querymodules
gipddecode git-lfs git-receive-pack git-shell git-upload-archive git-upload-pack gjs gjs-console
glib-compile-schemas glycin-thumbnailer gnome-calculator gnome-calendar gnome-characters gnome-clocks
gnome-control-center gnome-disk-image-mounter gnome-disks gnome-extensions gnome-font-viewer gnome-help
gnome-keyring gnome-keyring-3 gnome-keyring-daemon gnome-language-selector gnome-logs
gnome-menus-blacklist gnome-service-client gnome-session gnome-session-inhibit gnome-session-quit
gnome-shell gnome-shell-extension-tool gnome-shell-test-tool gnome-text-editor gnome-thumbnail-font
gnome-www-browser gnu[ gnuarch gnub2sum gnubase32 gnubase64 gnubasename gnubasenc gnucat gnuchcon
gnuchgrp gnuchmod gnuchown gnuchroot gnucksum gnucomm gnucp gnucsplit gnucut gnudate gnudd gnudf gnudir
gnudircolors gnudirname gnudu gnuecho gnuenv gnuexpand gnuexpr gnufactor gnufalse gnufmt gnufold
gnugroups gnuhead gnuhostid gnuid gnuinstall gnujoin gnulink gnuln gnulogname gnuls gnumd5sum gnumkdir
gnumkfifo gnumknod gnumktemp gnumv gnunice gnunl gnunohup gnunproc gnunumfmt gnuod gnupaste gnupathchk
gnupinky gnupr gnuprintenv gnuprintf gnuptx gnupwd gnureadlink gnurealpath gnurm gnurmdir gnuruncon
gnuseq gnusha1sum gnusha224sum gnusha256sum gnusha384sum gnusha512sum gnushred gnushuf gnusleep gnusort
gnusplit gnustat gnustdbuf gnustty gnusum gnusync gnutac gnutail gnutee gnutest gnutimeout gnutouch
gnutr gnutrue gnutruncate gnutsort gnutty gnuuname gnuunexpand gnuuniq gnuunlink gnuusers gnuvdir gnuwc
gnuwho gnuwhoami gnuyes gofmt gp-archive gp-collect-app gp-display-html gp-display-src gp-display-text
gpasswd gpg gpg-agent gpg-connect-agent gpg-mail-tube gpg-wks-client gpgconf gpgparsemail gpgsm gpgsplit
gpgtar gpgv gpic gprof gprofng gprofng-archive gprofng-collect-app gprofng-display-html
gprofng-display-src gprofng-display-text gprofng-gmon gpu-manager grdctl gresource groff grog grops
grotty groupadd groupdel groupmod groups growpart grpck grpconv grpunconv grub-bios-setup grub-editenv
grub-file grub-fstest grub-glue-efi grub-install grub-kbdcomp grub-macbless grub-menulst2cfg
grub-mkconfig grub-mkdevicemap grub-mkfont grub-mkimage grub-mklayout grub-mknetdir grub-mkpasswd-pbkdf2
grub-mkrelpath grub-mkrescue grub-mkstandalone grub-mount grub-probe grub-reboot grub-render-label
grub-script-check grub-set-default grub-syslinux2cfg gs gsbj gsdj gsdj500 gsettings gslj gslp gsnd
gst-audio-thumbnailer gst-device-monitor-1.0 gst-discoverer-1.0 gst-inspect-1.0 gst-launch-1.0
gst-play-1.0 gst-stats-1.0 gst-tester-1.0 gst-typefind-1.0 gst-video-thumbnailer gstack
gstreamer-codec-install gtbl gted gtk-builder-tool gtk-encode-symbolic-svg gtk-launch gtk-query-settings
gtk-update-icon-cache gtk4-broadwayd gtk4-builder-tool gtk4-encode-symbolic-svg gtk4-image-tool
gtk4-launch gtk4-path-tool gtk4-query-settings gtk4-rendernode-tool gtk4-update-icon-cache gunzip gzexe
h2ph h2xs halt hardirqs-bpfcc hardlink hash hashsum hbpldecode hciattach hciconfig hcitool hd hdparm
heif-thumbnailer help helpztags hex2hcd hexdump hg hipercdecode history host hostid hostname hostnamectl
hp-align hp-check hp-clean hp-colorcal hp-config_usb_printer hp-doctor hp-firmware hp-info hp-levels
hp-logcapture hp-makeuri hp-pkservice hp-plugin hp-plugin-ubuntu hp-probe hp-query hp-scan hp-setup
hp-testpage hp-timedate htop hwclock hwctl hwe-support-status i386 ibus ibus-daemon ibus-setup
ibus-table-createdb iceauth iconv iconvconfig id identify iecset ijs_pxljr im-config im-launch
inetutils-telnet info infobrowser infocmp infotocap init inject-bpfcc inotifywait inotifywatch
inputattach insmod install install-info install-sgmlcatalog installkernel instmodsh integritysetup
intel-speed-select invoke-rc.d inxi ionice iostat iotop ip6tables ip6tables-apply ip6tables-legacy
ip6tables-legacy-restore ip6tables-legacy-save ip6tables-nft ip6tables-nft-restore ip6tables-nft-save
ip6tables-restore ip6tables-restore-translate ip6tables-save ip6tables-translate ipcmk ipcrm ipcs iperf3
ipod-read-sysinfo-extended ipod-time-sync ipp-usb ippevepcl ippeveprinter ippeveps ippfind ipptool
iptables iptables-apply iptables-legacy iptables-legacy-restore iptables-legacy-save iptables-nft
iptables-nft-restore iptables-nft-save iptables-restore iptables-restore-translate iptables-save
iptables-translate iptables-xml ischroot iscsi-iname iscsi_discovery iscsiadm iscsid iscsistart isosize
ispell-autobuildhash ispell-wrapper iucode-tool iucode_tool iw javacalls-bpfcc javaflow-bpfcc
javagc-bpfcc javaobjnew-bpfcc javastat-bpfcc javathreads-bpfcc jobs join jpgicc json-patch-jsondiff
json_pp jsondiff jsonpatch jsonpointer jsonschema kbd_mode kbdinfo kbdrate kbxutil kdump-config
kernel-install kexec kexec-load-kernel kill killall killall5 killsnoop-bpfcc killsnoop.bt
klockstat-bpfcc kmod kmodsign kpartx kvmexit-bpfcc l2ping l2test landscape-sysinfo laptop-detect
lavadecode ld ld.bfd ld.so ldapadd ldapcompare ldapdelete ldapexop ldapmodify ldapmodrdn ldappasswd
ldapsearch ldapurl ldapwhoami ldattach ldconfig ldd less lessecho lessfile lesskey lesspipe let lexgrog
lftp libnetcfg libreoffice link linkicc linux-boot-prober linux-check-removal linux-run-hooks
linux-update-symlinks linux-version linux32 linux64 listres llcstat-bpfcc ln lnstat loadkeys loads.bt
loadunimap local localc locale locale-check locale-gen localectl localedef localsearch lodraw loffice
lofromtemplate logger login loginctl logname logout logrotate logsave loimpress lomath look losetup
loupe loweb lowntfs-3g lowriter lp lpadmin lpc lpinfo lpmove lpoptions lpq lpr lprm lpstat lsattr
lsb_release lsblk lsclocks lscpu lsfd lshw lsinitramfs lsinitrd lsipc lsirq lslocks lslogins lsmem lsmod
lsns lsof lspci lspcmcia lspgpot lspower lsusb luit luksformat lvchange lvconvert lvcreate lvdisplay
lvextend lvm lvmconfig lvmdiskscan lvmdump lvmpolld lvmsadc lvmsar lvreduce lvremove lvrename lvresize
lvs lvscan lwp-download lwp-dump lwp-mirror lwp-request lxc lxd lz4 lzcat lzcmp lzdiff lzegrep lzfgrep
lzgrep lzless lzma lzmainfo lzmore m17n-db m2300w m2300w-wrapper m2400w mailmail3 make make-bcache
make-ssl-cert makedumpfile makedumpfile-R.pl mako-render man man-recode mandb manpath mapfile mapscrn
markdown-it mawk mbim-network mbimcli mcookie md5sum mdadm mdflush-bpfcc mdflush.bt mdig mdmon mediainfo
memhog memleak-bpfcc mesa-overlay-control.py mesa-screenshot-control.py meson micro
migrate-pubring-from-classic-gpg migratepages migspeed mimeopen mimetype min12xxw mk_modmap mkdir
mkdosfs mke2fs mkfifo mkfontdir mkfontscale mkfs mkfs.bfs mkfs.btrfs mkfs.cramfs mkfs.exfat mkfs.ext2
mkfs.ext3 mkfs.ext4 mkfs.fat mkfs.minix mkfs.msdos mkfs.ntfs mkfs.vfat mkfs.xfs mkhomedir_helper
mkinitramfs mklost+found mknod mkntfs mksquashfs mkswap mktemp mmcli modinfo modprobe mogrify mokutil
monitor-sensor more mosh mosquitto_pub mosquitto_sub mount mount.fuse mount.fuse3 mount.lowntfs-3g
mount.ntfs mount.ntfs-3g mountpoint mountsnoop-bpfcc mpathpersist mpris-proxy mpstat mptcpify-bpfcc mpv
mscompress msexpand mt mt-gnu mtr mtr-packet multipath multipathc multipathd mvn mysql
mysqld_qslower-bpfcc namei nano naptime.bt nautilus nautilus-autorun-software nautilus-sendto nawk nc
nc.openbsd ncdu needrestart neqn netaddr netcat netplan netqtop-bpfcc netshaper networkctl
networkd-dispatcher newgrp newusers nfnl_osf nfsdist-bpfcc nfsslower-bpfcc nft ngettext nginx
nhlt-dmic-info nice nisdomainname nl nm nm-connection-editor nm-online nmcli nmtui nmtui-connect
nmtui-edit nmtui-hostname node nodegc-bpfcc nodestat-bpfcc nohup nologin notify-send nproc npx nroff
nsenter nslookup nstat nsupdate ntfs-3g ntfs-3g.probe ntfscat ntfsclone ntfscluster ntfscmp ntfscp
ntfsdecrypt ntfsfallocate ntfsfix ntfsinfo ntfslabel ntfsls ntfsmove ntfsrecover ntfsresize ntfssecaudit
ntfstruncate ntfsundelete ntfsusermap ntfswipe numactl numasched-bpfcc numastat numfmt nvim nvme
oakdecode obexctl objcopy objdump od oem-getlogs offcputime-bpfcc offwaketime-bpfcc on_ac_power oomctl
oomkill-bpfcc oomkill.bt open opensnoop-bpfcc opensnoop.bt openvpn openvt opldecode optipng orca
orca-dm-wrapper os-prober osirrox overlayroot-chroot ownership p11-kit pager pam-auth-update
pam_extrausers_chkpwd pam_extrausers_update pam_getenv pam_namespace_helper pam_timestamp_check pandoc
paper paperconf paperconfig papers papers-previewer papers-thumbnailer parallel parted partprobe partx
passwd paste patch pathchk pbzip2 pccardctl pcilmr pdata_tools pdb3 pdb3.14 pdf2dsc pdf2ps pdfattach
pdfdetach pdffonts pdfimages pdfinfo pdfseparate pdfsig pdftocairo pdftohtml pdftoppm pdftops pdftotext
pdfunite peekfd perf perl perl5.40-x86_64-linux-gnu perl5.40.1 perlbug perlcalls-bpfcc perldoc
perlflow-bpfcc perli11ndoc perlivp perlstat-bpfcc perlthanks pf2afm pfbtopfa pgrep photorec
phpcalls-bpfcc phpflow-bpfcc phpstat-bpfcc pic pico piconv pidof pidpersec-bpfcc pidpersec.bt pidstat
pidwait pigz pinentry pinentry-curses pinentry-gnome3 pinentry-x11 ping ping4 ping6 pinky pipesz
pipewire pipewire-aes67 pipewire-avb pipewire-pulse pipx pivot_root pkaction pkcheck pkexec pkgcli pkill
pkttyagent pl2pm play pldd plocate plog plymouth plymouthd pmap pnm2ppa pod2html pod2man pod2text
pod2usage podchecker poff pon popd poweroff powerprofilesctl ppchcalls-bpfcc ppdc ppdhtml ppdi ppdmerge
ppdpo pphs pppd pppdump pppoe-discovery pppstats pptp pptpsetup pr precat preconv preunzip prezip
prezip-bin printafm printenv printer-profile printf prlimit pro profile-bpfcc prompting-client.echo
prompting-client.logging-level prompting-client.scripted prove prtstat ps ps2ascii ps2epsi ps2pdf
ps2pdf12 ps2pdf13 ps2pdf14 ps2pdfwr ps2ps ps2ps2 ps2txt psfaddtable psfgettable psfstriptable psfxtable
psicc pslog pstree pstree.x11 ptar ptardiff ptargrep ptx ptyxis pushd pv pvchange pvck pvcreate
pvdisplay pvmove pvremove pvresize pvs pvscan pw-cat pw-cli pw-config pw-container pw-dot pw-dsdplay
pw-dump pw-encplay pw-link pw-loopback pw-metadata pw-midi2play pw-midi2record pw-mididump pw-midiplay
pw-midirecord pw-mon pw-play pw-profiler pw-record pw-reserve pw-sysex pw-top pwck pwconv pwd pwdx
pwhistory_helper pwunconv py3clean py3compile py3versions pybabel pybabel-python3 pydoc3 pydoc3.14
pygettext3 pygettext3.14 pygmentize pyhtmlizer3 pyserial-miniterm pyserial-ports python3.14
pythoncalls-bpfcc pythonflow-bpfcc pythongc-bpfcc pythonstat-bpfcc pzstd qemu-img qemu-system-x86_64
qmi-firmware-update qmi-network qmicli qpdf qpdldecode quirks-handler ranlib rbash rctest rdma
rdmaucma-bpfcc read readahead-bpfcc readarray readelf readlink readonly readprofile realpath reboot rec
red redis-cli remmina remmina-file-wrapper remmina-gnome remove-default-ispell remove-default-wordlist
remove-shell rename rename.ul renice rescan-scsi-bus.sh reset reset-trace-bpfcc resize2fs resizecons
resizepart resolvconf resolvectl resources return rev rfcomm rfkill rgrep rhythmbox rhythmbox-client
rmdir rmmod rmt rmt-tar rnano routel rpcgen rrsync rsync-ssl rsyslogd rtacct rtcwake rtkitctl rtla rtmon
rtstat rubycalls-bpfcc rubyflow-bpfcc rubygc-bpfcc rubyobjnew-bpfcc rubystat-bpfcc run-parts
run-with-aspell run0 runcon runqlat-bpfcc runqlat.bt runqlen-bpfcc runqlen.bt runqslower-bpfcc runuser
rustc rview rvim rygel sadf sane-find-scanner saned sar sar.sysstat savelog sbattach sbkeysync sbsiglist
sbsign sbvarsign sbverify scalar scanimage scp-dbus-service screen screendump script scriptlive
scriptreplay scsi_logging_level scsi_mandat scsi_readcap scsi_ready scsi_satl scsi_start scsi_stop
scsi_temperature sdiff sdptool seahorse select-default-ispell select-default-iwrap
select-default-wordlist select-editor sensible-browser sensible-editor sensible-pager sensible-terminal
sensors seq service sessreg set setarch setcap setfacl setfont setkeycodes setleds setlogcons
setmetamode setpci setpriv setsid setterm setuids.bt setupcon setvesablank setvtrgb setxkbmap sfdisk sg
sg_bg_ctl sg_compare_and_write sg_copy_results sg_dd sg_decode_sense sg_emc_trespass sg_format
sg_get_config sg_get_elem_status sg_get_lba_status sg_ident sg_inq sg_logs sg_luns sg_map sg_map26
sg_modes sg_opcodes sg_persist sg_prevent sg_raw sg_rbuf sg_rdac sg_read sg_read_attr
sg_read_block_limits sg_read_buffer sg_read_long sg_readcap sg_reassign sg_referrals sg_rem_rest_elem
sg_rep_density sg_rep_pip sg_rep_zones sg_requests sg_reset sg_reset_wp sg_rmsn sg_rtpg sg_safte
sg_sanitize sg_sat_datetime sg_sat_identify sg_sat_phy_event sg_sat_read_gplog sg_sat_set_features
sg_scan sg_seek sg_senddiag sg_ses sg_ses_microcode sg_start sg_stpg sg_stream_ctl sg_sync sg_test_rwbuf
sg_timestamp sg_turs sg_unmap sg_verify sg_vpd sg_wr_mode sg_write_attr sg_write_buffer sg_write_long
sg_write_same sg_write_verify sg_write_x sg_xcopy sg_z_act_query sg_zone sgdisk sginfo sgm_dd sgp_dd sh
sha1sum sha224sum sha256sum sha3-224sum sha3-256sum sha3-384sum sha3-512sum sha384sum sha3sum sha512sum
shadowconfig shake128sum shake256sum shasum shellcheck shift shmsnoop-bpfcc shopt shotwell
showconsolefont showkey showrgb showtime shred shuf shutdown simple-scan size skill slabratetop-bpfcc
slabtop sleep slxdecode smartctl snap snap-store snap-store.show-updates snapctl snapfuse snapshot snice
socat soelim sofdsnoop-bpfcc soffice softirqs-bpfcc solisten-bpfcc sos source sox spa-acp-tool
spa-inspect spa-json-dump spa-monitor spa-resample spd-conf spd-say spdsend speaker-test
speech-dispatcher spice-vdagent spice-vdagentd splain split splitfont sqfscat sqfstar sqlite3 ssh-add
ssh-agent ssh-argv0 ssh-copy-id ssh-import-id ssh-import-id-gh ssh-import-id-lp ssh-keygen ssh-keyscan
sshd sshfs ssllatency.bt sslsniff-bpfcc sslsnoop.bt sss_ssh_authorizedkeys sss_ssh_knownhosts
sss_ssh_knownhostsproxy sssd stackcount-bpfcc starship start-stop-daemon stat static-sh statsnoop-bpfcc
statsnoop.bt stdbuf strace strace-log-merge streamzip strings strip stty su su-rs sudo sudo-rs sudo.ws
sudo_logsrvd sudo_sendlog.ws sudoedit sudoedit-rs sudoreplay.ws sulogin sum suspend svn swapin.bt
swaplabel swapoff swapon switch_root switcherooctl sync syncsnoop-bpfcc syncsnoop.bt syncthing
syscount-bpfcc syscount.bt sysctl sysprof sysprof-agent sysprof-cat sysprof-cli systemd-ac-power
systemd-analyze systemd-ask-password systemd-cat systemd-cgls systemd-cgtop systemd-confext
systemd-creds systemd-cryptenroll systemd-cryptsetup systemd-delta systemd-detect-virt systemd-escape
systemd-firstboot systemd-hwdb systemd-id128 systemd-inhibit systemd-machine-id-setup systemd-mount
systemd-mute-console systemd-notify systemd-path systemd-pty-forward systemd-run systemd-socket-activate
systemd-stdio-bridge systemd-sysext systemd-sysusers systemd-tmpfiles systemd-tty-ask-password-agent
systemd-umount systemd-vpick tabs tac tapestat tarcat taskset tbl tc tclcalls-bpfcc tclflow-bpfcc
tclobjnew-bpfcc tclsh tclsh8.6 tclstat-bpfcc tcpaccept-bpfcc tcpaccept.bt tcpcong-bpfcc tcpconnect-bpfcc
tcpconnect.bt tcpconnlat-bpfcc tcpdrop-bpfcc tcpdrop.bt tcpdump tcplife-bpfcc tcplife.bt
tcpretrans-bpfcc tcpretrans.bt tcprtt-bpfcc tcpstates-bpfcc tcpsubnet-bpfcc tcpsynbl-bpfcc tcpsynbl.bt
tcptop-bpfcc tcptracer-bpfcc tecla tee telnet tempfile tesseract test testdisk thermald thin_check
thin_delta thin_dump thin_ls thin_metadata_pack thin_metadata_size thin_metadata_unpack thin_migrate
thin_repair thin_restore thin_rmap thin_trim threadsnoop-bpfcc threadsnoop.bt thunderbird tic tificc tig
time timedatectl timeout times tinysparql tipc tkconch3 tload tmux tnftp toe top touch tplist-bpfcc tput
tr trace-bpfcc trace-cmd tracepath traceroute transicc transmission-gtk trap tree trial3 troff true
truncate trust tset tshark tsort tty ttysnoop-bpfcc tune.exfat tune2fs turbostat twist3 twistd3 type
typeset tzselect u-d-c-print-pci-ids ua ubuntu-advantage ubuntu-bug ubuntu-distro-info ubuntu-drivers
ubuntu-insights ubuntu-report ubuntu-security-status ucalls ucf ucfq ucfr uclampset ucs2any udevadm
udisksctl uflow ufw ugc ul ulimit umask umax_pp umount umount.udisks2 unalias uname unattended-upgrade
unattended-upgrades uncompress undump.bt unexpand unicode_start unicode_stop uniq unity-scope-loader
unix2dos unix_chkpwd unix_update unlink unlzma unminimize unmkinitramfs unopkg unpigz unrar unset
unshare unsquashfs unxz unzip unzipsfx unzstd uobjnew update-alternatives update-ca-certificates
update-catalog update-cracklib update-default-aspell update-default-ispell update-default-wordlist
update-desktop-database update-dictcommon-aspell update-dictcommon-hunspell update-fonts-alias
update-fonts-dir update-fonts-scale update-grub update-grub-gfxpayload update-grub2 update-gsfontmap
update-icon-caches update-ieee-data update-inetd update-info-dir update-initramfs update-locale
update-manager update-mime-database update-notifier update-passwd update-pciids update-rc.d
update-shells update-xmlcatalog upower uptime usb-creator-gtk usb-devices usb_modeswitch
usb_modeswitch_dispatcher usb_printerid usbhid-dump usbip usbipd usbmuxd usbreset user-session-migration
useradd userdel usermod users ustat uthreads uuidd uuidgen uuidparse valgrind validlocale varlinkctl
vcs-run vcstime vdir vdpa veritysetup vfscount-bpfcc vfscount.bt vfsstat-bpfcc vfsstat.bt vgcfgbackup
vgcfgrestore vgchange vgck vgconvert vgcreate vgdisplay vgexport vgextend vgimport vgimportclone vgmerge
vgmknodes vgreduce vgremove vgrename vgs vgscan vgsplit vi view viewres vigr vim vim.basic vim.tiny
vimdiff vimtutor vipw virsh virtiostat-bpfcc visudo visudo-rs visudo.ws vm-support vmcore-dmesg
vmhgfs-fuse vmstat vmtoolsd vmware-alias-import vmware-checkvm vmware-hgfsclient vmware-namespace-cmd
vmware-rpctool vmware-toolbox-cmd vmware-vgauth-cmd vmware-vmblock-fuse vmware-xferlogs vpddecode vstp w
wait waitpid wakeuptime-bpfcc wall watch watchgnupg wc wcurl wdctl wg wg-quick whatis whereis which
which.debianutils whiptail who whoami whois whoopsie whoopsie-preferences wipefs wireplumber
word-list-compress wpa_action wpa_cli wpa_passphrase wpa_supplicant wpctl wpexec wqlat-bpfcc
writeback.bt wsdd x-session-manager x-terminal-emulator x-www-browser x86_64 x86_64-linux-gnu-addr2line
x86_64-linux-gnu-ar x86_64-linux-gnu-as x86_64-linux-gnu-c++filt x86_64-linux-gnu-cpp
x86_64-linux-gnu-cpp-15 x86_64-linux-gnu-elfedit x86_64-linux-gnu-gprof x86_64-linux-gnu-ld
x86_64-linux-gnu-ld.bfd x86_64-linux-gnu-nm x86_64-linux-gnu-objcopy x86_64-linux-gnu-objdump
x86_64-linux-gnu-ranlib x86_64-linux-gnu-readelf x86_64-linux-gnu-size x86_64-linux-gnu-strings
x86_64-linux-gnu-strip x86_energy_perf_policy xargs xauth xbrlapi xcmsdb xdg-dbus-proxy xdg-desktop-icon
xdg-desktop-menu xdg-email xdg-icon-resource xdg-mime xdg-open xdg-screensaver xdg-settings
xdg-terminal-exec xdg-user-dir xdg-user-dirs-gtk-update xdg-user-dirs-update xdpyinfo xdriinfo xev xfd
xfontsel xfs_admin xfs_bmap xfs_copy xfs_db xfs_estimate xfs_freeze xfs_fsr xfs_growfs xfs_info xfs_io
xfs_logprint xfs_mdrestore xfs_metadump xfs_mkfile xfs_ncheck xfs_property xfs_protofile xfs_quota
xfs_repair xfs_rtcp xfs_scrub xfs_scrub_all xfs_spaceman xfsdist-bpfcc xfsdist.bt xfsslower-bpfcc xgamma
xhost xkbbell xkbcomp xkbevd xkbprint xkbvleds xkbwatch xkeystone xkill xlsatoms xlsclients xlsfonts
xmessage xmlstarlet xmodmap xorrecord xorriso xorrisofs xprop xqxdecode xrandr xrdb xrefresh xset
xsetmode xsetpointer xsetroot xstdcmap xsubpp xtables-legacy-multi xtables-monitor xtables-nft-multi
xvidtune xvinfo xwininfo xxd xzcat xzcmp xzdiff xzegrep xzfgrep xzgrep xzless xzmore yelp yes
ypdomainname zcat zcmp zdiff zdump zegrep zenity zerofree zfgrep zforce zfs zfsdist-bpfcc
zfsslower-bpfcc zgrep zic zip zipcloak zipdetails zipgrep zipinfo zipnote zipsplit zjsdecode zless zmore
znew zoxide zpool zramctl zsh zstd zstdcat zstdgrep zstdless zstdmt
""".split())
