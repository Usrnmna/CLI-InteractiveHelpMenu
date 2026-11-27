"""APT command and argument declarations from the Ubuntu 2.8.4 and 3.2.1 sources.

Grouped verbs share exactly the same option spellings and operand arities.
A trailing equals sign marks a required argument in these tables.
Source files and edition checks are listed in the Ubuntu coverage audit.
"""

NOBLE = {
    "apt": (
        ("@ help",
         "--config-file= --help --option= --quiet --silent --version -c= -h -o= -q -v"),
        ("list",
         "--all-versions --config-file= --help --installed --manual-installed --option= --quiet --silent "
         "--upgradable --upgradeable --verbose --version --with-source= -a -c= -h -i -o= -q -u -v"),
        ("search",
         "--allow-change-held-packages --allow-downgrades --allow-remove-essential --allow-unauthenticated "
         "--assume-no --assume-yes --config-file= --default-release= --download --download-only "
         "--fix-missing --fix-policy --force-yes --full --generate --help --ignore-hold --ignore-missing "
         "--install-recommends --install-suggests --mark-auto --names-only --only-source --only-upgrade "
         "--option= --pkg-cache= --print-uris --quiet --remove --show-upgraded --silent --snapshot= "
         "--src-cache= --target-release= --trivial-only --upgrade --version --with-source= --yes -S= -c= "
         "-d -f -g -h -m -n -o= -p= -q -s= -t= -u -v -y"),
        ("show info",
         "--all-versions --config-file= --full --help --option= --quiet --silent --version --with-source= "
         "-a -c= -f -h -o= -q -v"),
        ("install reinstall remove autoremove autopurge purge full-upgrade dist-upgrade",
         "--allow-change-held-packages --allow-downgrades --allow-remove-essential --allow-unauthenticated "
         "--assume-no --assume-yes --auto-remove --autoremove --config-file= --default-release= --download "
         "--download-only --dry-run --fix-broken --fix-missing --fix-policy --force-yes --help "
         "--ignore-hold --ignore-missing --install-recommends --install-suggests --just-print --mark-auto "
         "--no-act --only-source --only-upgrade --option= --planner= --print-uris --purge --quiet --recon "
         "--reinstall --remove --show-progress --show-upgraded --silent --simulate --snapshot= --solver= "
         "--target-release= --trivial-only --update --upgrade --verbose-versions --version --with-source= "
         "--yes -S= -U -V -c= -d -f -h -m -o= -q -s -t= -u -v -y"),
        ("auto-remove clean distclean dist-clean autoclean auto-clean",
         "--allow-change-held-packages --allow-downgrades --allow-remove-essential --allow-unauthenticated "
         "--assume-no --assume-yes --config-file= --default-release= --download --download-only --dry-run "
         "--fix-missing --fix-policy --force-yes --help --ignore-hold --ignore-missing "
         "--install-recommends --install-suggests --just-print --mark-auto --no-act --only-source "
         "--only-upgrade --option= --print-uris --quiet --recon --remove --show-upgraded --silent "
         "--simulate --snapshot= --target-release= --trivial-only --upgrade --version --with-source= --yes "
         "-S= -c= -d -h -m -o= -q -s -t= -u -v -y"),
        ("update",
         "--allow-change-held-packages --allow-downgrades --allow-insecure-repositories "
         "--allow-releaseinfo-change --allow-releaseinfo-change-codename "
         "--allow-releaseinfo-change-defaultpin --allow-releaseinfo-change-label "
         "--allow-releaseinfo-change-origin --allow-releaseinfo-change-suite "
         "--allow-releaseinfo-change-version --allow-remove-essential --allow-unauthenticated "
         "--allow-weak-repositories --assume-no --assume-yes --config-file= --default-release= --download "
         "--download-only --error-on= --fix-missing --fix-policy --force-yes --help --ignore-hold "
         "--ignore-missing --install-recommends --install-suggests --list-cleanup --mark-auto "
         "--only-source --only-upgrade --option= --print-uris --quiet --remove --show-upgraded --silent "
         "--snapshot= --target-release= --trivial-only --upgrade --version --with-source= --yes -S= -c= -d "
         "-e= -h -m -o= -q -t= -u -v -y"),
        ("upgrade",
         "--allow-change-held-packages --allow-downgrades --allow-remove-essential --allow-unauthenticated "
         "--assume-no --assume-yes --auto-remove --autoremove --config-file= --default-release= --download "
         "--download-only --dry-run --fix-broken --fix-missing --fix-policy --force-yes --help "
         "--ignore-hold --ignore-missing --install-recommends --install-suggests --just-print --mark-auto "
         "--new-pkgs --no-act --only-source --only-upgrade --option= --planner= --print-uris --purge "
         "--quiet --recon --reinstall --remove --show-progress --show-upgraded --silent --simulate "
         "--snapshot= --solver= --target-release= --trivial-only --update --upgrade --verbose-versions "
         "--version --with-source= --yes -S= -U -V -c= -d -f -h -m -o= -q -s -t= -u -v -y"),
        ("edit-sources download changelog",
         "--allow-change-held-packages --allow-downgrades --allow-remove-essential --allow-unauthenticated "
         "--assume-no --assume-yes --config-file= --default-release= --download --download-only "
         "--fix-missing --fix-policy --force-yes --help --ignore-hold --ignore-missing "
         "--install-recommends --install-suggests --mark-auto --only-source --only-upgrade --option= "
         "--print-uris --quiet --remove --show-upgraded --silent --snapshot= --target-release= "
         "--trivial-only --upgrade --version --with-source= --yes -S= -c= -d -h -m -o= -q -t= -u -v -y"),
        ("satisfy",
         "--allow-change-held-packages --allow-downgrades --allow-remove-essential --allow-unauthenticated "
         "--assume-no --assume-yes --build-profiles= --config-file= --default-release= --download "
         "--download-only --dry-run --fix-broken --fix-missing --fix-policy --force-yes --help "
         "--host-architecture= --ignore-hold --ignore-missing --install-recommends --install-suggests "
         "--just-print --mark-auto --no-act --only-source --only-upgrade --option= --print-uris --purge "
         "--quiet --recon --remove --show-upgraded --silent --simulate --snapshot= --solver= "
         "--target-release= --trivial-only --upgrade --version --with-source= --yes -P= -S= -a= -c= -d -f "
         "-h -m -o= -q -s -t= -u -v -y"),
        ("showsrc policy",
         "--allow-change-held-packages --allow-downgrades --allow-remove-essential --allow-unauthenticated "
         "--assume-no --assume-yes --config-file= --default-release= --download --download-only "
         "--fix-missing --fix-policy --force-yes --generate --help --ignore-hold --ignore-missing "
         "--install-recommends --install-suggests --mark-auto --only-source --only-upgrade --option= "
         "--pkg-cache= --print-uris --quiet --remove --show-upgraded --silent --snapshot= --src-cache= "
         "--target-release= --trivial-only --upgrade --version --with-source= --yes -S= -c= -d -g -h -m "
         "-o= -p= -q -s= -t= -u -v -y"),
        ("depends rdepends",
         "--allow-change-held-packages --allow-downgrades --allow-remove-essential --allow-unauthenticated "
         "--assume-no --assume-yes --breaks --config-file= --conflicts --default-release= --depends "
         "--download --download-only --enhances --fix-missing --fix-policy --force-yes --generate --help "
         "--ignore-hold --ignore-missing --implicit --important --install-recommends --install-suggests "
         "--installed --mark-auto --only-source --only-upgrade --option= --pkg-cache= --pre-depends "
         "--print-uris --quiet --recommends --recurse --remove --replaces --show-upgraded --silent "
         "--snapshot= --src-cache= --suggests --target-release= --trivial-only --upgrade --version "
         "--with-source= --yes -S= -c= -d -g -h -i -m -o= -p= -q -s= -t= -u -v -y"),
        ("build-dep",
         "--allow-change-held-packages --allow-downgrades --allow-remove-essential --allow-unauthenticated "
         "--arch-only --assume-no --assume-yes --build-profiles= --config-file= --default-release= "
         "--download --download-only --dry-run --fix-broken --fix-missing --fix-policy --force-yes --help "
         "--host-architecture= --ignore-hold --ignore-missing --indep-only --install-recommends "
         "--install-suggests --just-print --mark-auto --no-act --only-source --only-upgrade --option= "
         "--print-uris --purge --quiet --recon --remove --show-upgraded --silent --simulate --snapshot= "
         "--solver= --target-release= --trivial-only --upgrade --version --with-source= --yes -P= -S= -a= "
         "-c= -d -f -h -m -o= -q -s -t= -u -v -y"),
        ("source",
         "--allow-change-held-packages --allow-downgrades --allow-remove-essential --allow-unauthenticated "
         "--assume-no --assume-yes --build --build-profiles= --compile --config-file= --debian-only "
         "--default-release= --diff-only --download --download-only --dry-run --dsc-only --fix-missing "
         "--fix-policy --force-yes --help --host-architecture= --ignore-hold --ignore-missing "
         "--install-recommends --install-suggests --just-print --mark-auto --no-act --only-source "
         "--only-upgrade --option= --print-uris --quiet --recon --remove --show-upgraded --silent "
         "--simulate --snapshot= --tar-only --target-release= --trivial-only --upgrade --version "
         "--with-source= --yes -P= -S= -a= -b -c= -d -h -m -o= -q -s -t= -u -v -y"),
    ),
    "apt-cache": (
        ("@ dotty xvcg help",
         "--config-file= --help --option= --quiet --silent --version -c= -h -o= -q -v"),
        ("gencaches showpkg stats dump dumpavail showauto policy madison",
         "--config-file= --default-release= --generate --help --option= --pkg-cache= --quiet --silent "
         "--snapshot= --src-cache= --target-release= --version --with-source= -S= -c= -g -h -o= -p= -q -s= "
         "-t= -v"),
        ("showsrc",
         "--config-file= --default-release= --generate --help --only-source --option= --pkg-cache= --quiet "
         "--silent --snapshot= --src-cache= --target-release= --version --with-source= -S= -c= -g -h -o= "
         "-p= -q -s= -t= -v"),
        ("unmet",
         "--config-file= --default-release= --generate --help --important --option= --pkg-cache= --quiet "
         "--silent --snapshot= --src-cache= --target-release= --version --with-source= -S= -c= -g -h -i "
         "-o= -p= -q -s= -t= -v"),
        ("search",
         "--config-file= --default-release= --full --generate --help --names-only --option= --pkg-cache= "
         "--quiet --silent --snapshot= --src-cache= --target-release= --version --with-source= -S= -c= -f "
         "-g -h -n -o= -p= -q -s= -t= -v"),
        ("depends rdepends",
         "--breaks --config-file= --conflicts --default-release= --depends --enhances --generate --help "
         "--implicit --important --installed --option= --pkg-cache= --pre-depends --quiet --recommends "
         "--recurse --replaces --silent --snapshot= --src-cache= --suggests --target-release= --version "
         "--with-source= -S= -c= -g -h -i -o= -p= -q -s= -t= -v"),
        ("show",
         "--all-versions --config-file= --default-release= --generate --help --option= --pkg-cache= "
         "--quiet --silent --snapshot= --src-cache= --target-release= --version --with-source= -S= -a -c= "
         "-g -h -o= -p= -q -s= -t= -v"),
        ("pkgnames",
         "--all-names --config-file= --default-release= --generate --help --option= --pkg-cache= --quiet "
         "--silent --snapshot= --src-cache= --target-release= --version --with-source= -S= -c= -g -h -o= "
         "-p= -q -s= -t= -v"),
    ),
    "apt-get": (
        ("@ help",
         "--config-file= --help --option= --quiet --silent --version -c= -h -o= -q -v"),
        ("update",
         "--allow-change-held-packages --allow-downgrades --allow-insecure-repositories "
         "--allow-releaseinfo-change --allow-releaseinfo-change-codename "
         "--allow-releaseinfo-change-defaultpin --allow-releaseinfo-change-label "
         "--allow-releaseinfo-change-origin --allow-releaseinfo-change-suite "
         "--allow-releaseinfo-change-version --allow-remove-essential --allow-unauthenticated "
         "--allow-weak-repositories --assume-no --assume-yes --config-file= --default-release= --download "
         "--download-only --error-on= --fix-missing --fix-policy --force-yes --help --ignore-hold "
         "--ignore-missing --install-recommends --install-suggests --list-cleanup --mark-auto "
         "--only-source --only-upgrade --option= --print-uris --quiet --remove --show-upgraded --silent "
         "--snapshot= --target-release= --trivial-only --upgrade --version --with-source= --yes -S= -c= -d "
         "-e= -h -m -o= -q -t= -u -v -y"),
        ("upgrade",
         "--allow-change-held-packages --allow-downgrades --allow-remove-essential --allow-unauthenticated "
         "--assume-no --assume-yes --auto-remove --autoremove --config-file= --default-release= --download "
         "--download-only --dry-run --fix-broken --fix-missing --fix-policy --force-yes --help "
         "--ignore-hold --ignore-missing --install-recommends --install-suggests --just-print --mark-auto "
         "--new-pkgs --no-act --only-source --only-upgrade --option= --planner= --print-uris --purge "
         "--quiet --recon --reinstall --remove --show-progress --show-upgraded --silent --simulate "
         "--snapshot= --solver= --target-release= --trivial-only --update --upgrade --verbose-versions "
         "--version --with-source= --yes -S= -U -V -c= -d -f -h -m -o= -q -s -t= -u -v -y"),
        ("install reinstall remove purge autoremove autopurge dist-upgrade full-upgrade dselect-upgrade",
         "--allow-change-held-packages --allow-downgrades --allow-remove-essential --allow-unauthenticated "
         "--assume-no --assume-yes --auto-remove --autoremove --config-file= --default-release= --download "
         "--download-only --dry-run --fix-broken --fix-missing --fix-policy --force-yes --help "
         "--ignore-hold --ignore-missing --install-recommends --install-suggests --just-print --mark-auto "
         "--no-act --only-source --only-upgrade --option= --planner= --print-uris --purge --quiet --recon "
         "--reinstall --remove --show-progress --show-upgraded --silent --simulate --snapshot= --solver= "
         "--target-release= --trivial-only --update --upgrade --verbose-versions --version --with-source= "
         "--yes -S= -U -V -c= -d -f -h -m -o= -q -s -t= -u -v -y"),
        ("auto-remove clean autoclean auto-clean distclean dist-clean check",
         "--allow-change-held-packages --allow-downgrades --allow-remove-essential --allow-unauthenticated "
         "--assume-no --assume-yes --config-file= --default-release= --download --download-only --dry-run "
         "--fix-missing --fix-policy --force-yes --help --ignore-hold --ignore-missing "
         "--install-recommends --install-suggests --just-print --mark-auto --no-act --only-source "
         "--only-upgrade --option= --print-uris --quiet --recon --remove --show-upgraded --silent "
         "--simulate --snapshot= --target-release= --trivial-only --upgrade --version --with-source= --yes "
         "-S= -c= -d -h -m -o= -q -s -t= -u -v -y"),
        ("markauto unmarkauto download changelog",
         "--allow-change-held-packages --allow-downgrades --allow-remove-essential --allow-unauthenticated "
         "--assume-no --assume-yes --config-file= --default-release= --download --download-only "
         "--fix-missing --fix-policy --force-yes --help --ignore-hold --ignore-missing "
         "--install-recommends --install-suggests --mark-auto --only-source --only-upgrade --option= "
         "--print-uris --quiet --remove --show-upgraded --silent --snapshot= --target-release= "
         "--trivial-only --upgrade --version --with-source= --yes -S= -c= -d -h -m -o= -q -t= -u -v -y"),
        ("build-dep",
         "--allow-change-held-packages --allow-downgrades --allow-remove-essential --allow-unauthenticated "
         "--arch-only --assume-no --assume-yes --build-profiles= --config-file= --default-release= "
         "--download --download-only --dry-run --fix-broken --fix-missing --fix-policy --force-yes --help "
         "--host-architecture= --ignore-hold --ignore-missing --indep-only --install-recommends "
         "--install-suggests --just-print --mark-auto --no-act --only-source --only-upgrade --option= "
         "--print-uris --purge --quiet --recon --remove --show-upgraded --silent --simulate --snapshot= "
         "--solver= --target-release= --trivial-only --upgrade --version --with-source= --yes -P= -S= -a= "
         "-c= -d -f -h -m -o= -q -s -t= -u -v -y"),
        ("satisfy",
         "--allow-change-held-packages --allow-downgrades --allow-remove-essential --allow-unauthenticated "
         "--assume-no --assume-yes --build-profiles= --config-file= --default-release= --download "
         "--download-only --dry-run --fix-broken --fix-missing --fix-policy --force-yes --help "
         "--host-architecture= --ignore-hold --ignore-missing --install-recommends --install-suggests "
         "--just-print --mark-auto --no-act --only-source --only-upgrade --option= --print-uris --purge "
         "--quiet --recon --remove --show-upgraded --silent --simulate --snapshot= --solver= "
         "--target-release= --trivial-only --upgrade --version --with-source= --yes -P= -S= -a= -c= -d -f "
         "-h -m -o= -q -s -t= -u -v -y"),
        ("source",
         "--allow-change-held-packages --allow-downgrades --allow-remove-essential --allow-unauthenticated "
         "--assume-no --assume-yes --build --build-profiles= --compile --config-file= --debian-only "
         "--default-release= --diff-only --download --download-only --dry-run --dsc-only --fix-missing "
         "--fix-policy --force-yes --help --host-architecture= --ignore-hold --ignore-missing "
         "--install-recommends --install-suggests --just-print --mark-auto --no-act --only-source "
         "--only-upgrade --option= --print-uris --quiet --recon --remove --show-upgraded --silent "
         "--simulate --snapshot= --tar-only --target-release= --trivial-only --upgrade --version "
         "--with-source= --yes -P= -S= -a= -b -c= -d -h -m -o= -q -s -t= -u -v -y"),
        ("indextargets",
         "--allow-change-held-packages --allow-downgrades --allow-remove-essential --allow-unauthenticated "
         "--assume-no --assume-yes --config-file= --default-release= --download --download-only "
         "--fix-missing --fix-policy --force-yes --format= --help --ignore-hold --ignore-missing "
         "--install-recommends --install-suggests --mark-auto --only-source --only-upgrade --option= "
         "--print-uris --quiet --release-info --remove --show-upgraded --silent --snapshot= "
         "--target-release= --trivial-only --upgrade --version --with-source= --yes -S= -c= -d -h -m -o= "
         "-q -t= -u -v -y"),
    ),
    "apt-config": (
        ("@ shell help",
         "--config-file= --help --option= --quiet --silent --version -c= -h -o= -q -v"),
        ("dump",
         "--config-file= --empty --format= --help --option= --quiet --silent --version -c= -h -o= -q -v"),
    ),
    "apt-mark": (
        ("@ help",
         "--config-file= --help --option= --quiet --silent --version -c= -h -o= -q -v"),
        ("auto manual hold unhold",
         "--config-file= --dry-run --file= --help --just-print --no-act --option= --quiet --recon --silent "
         "--simulate --version --with-source= -c= -f= -h -o= -q -s -v"),
        ("minimize-manual",
         "--assume-no --assume-yes --config-file= --dry-run --file= --help --just-print --no-act --option= "
         "--quiet --recon --silent --simulate --version --with-source= --yes -c= -f= -h -o= -q -s -v -y"),
        ("install remove deinstall purge",
         "--config-file= --dry-run --help --just-print --no-act --option= --quiet --recon --silent "
         "--simulate --version --with-source= -c= -h -o= -q -s -v"),
        ("showauto showmanual showhold showholds showheld",
         "--config-file= --file= --help --option= --quiet --silent --version --with-source= -c= -f= -h -o= "
         "-q -v"),
        ("showinstall showinstalls showdeinstall showdeinstalls showremove showremoves showpurge showpurges",
         "--config-file= --help --option= --quiet --silent --version --with-source= -c= -h -o= -q -v"),
        ("markauto unmarkauto",
         "--config-file= --dry-run --file= --help --just-print --no-act --option= --quiet --recon --silent "
         "--simulate --verbose --version --with-source= -c= -f= -h -o= -q -s -v"),
    ),
}

RESOLUTE = {
    "apt": (
        ("@ help",
         "--audit --cli-version= --color --config-file= --help --option= --quiet --silent --version -c= -h "
         "-o= -q -v"),
        ("list",
         "--all-versions --audit --cli-version= --color --config-file= --default-release= --help "
         "--installed --manual-installed --option= --quiet --silent --snapshot= --target-release= "
         "--upgradable --upgradeable --verbose --version --with-source= -S= -a -c= -h -i -o= -q -t= -u -v"),
        ("search",
         "--allow-change-held-packages --allow-downgrades --allow-remove-essential --allow-unauthenticated "
         "--assume-no --assume-yes --audit --cli-version= --color --config-file= --default-release= "
         "--download --download-only --fix-missing --fix-policy --force-yes --full --generate --help "
         "--ignore-hold --ignore-missing --install-recommends --install-suggests --mark-auto --names-only "
         "--only-source --only-upgrade --option= --pkg-cache= --print-uris --quiet --remove "
         "--show-upgraded --silent --snapshot= --src-cache= --target-release= --trivial-only --upgrade "
         "--version --with-source= --yes -S= -c= -d -f -g -h -m -n -o= -p= -q -s= -t= -u -v -y"),
        ("show info",
         "--all-versions --audit --cli-version= --color --config-file= --full --help --option= --quiet "
         "--silent --snapshot= --version --with-source= -S= -a -c= -f -h -o= -q -v"),
        ("install reinstall remove autoremove autopurge purge full-upgrade dist-upgrade",
         "--allow-change-held-packages --allow-downgrades --allow-remove-essential --allow-unauthenticated "
         "--assume-no --assume-yes --audit --auto-remove --autoremove --cli-version= --color --comment= "
         "--config-file= --default-release= --download --download-only --dry-run --fix-broken "
         "--fix-missing --fix-policy --force-yes --help --ignore-hold --ignore-missing "
         "--install-recommends --install-suggests --just-print --list-columns --mark-auto --no-act "
         "--only-source --only-upgrade --option= --planner= --print-uris --purge --quiet --recon "
         "--reinstall --remove --show-progress --show-upgraded --silent --simulate --snapshot= --solver= "
         "--strict-pinning --target-release= --trivial-only --update --upgrade --verbose-versions "
         "--version --with-source= --yes -S= -U -V -c= -d -f -h -m -o= -q -s -t= -u -v -y"),
        ("auto-remove clean distclean dist-clean autoclean auto-clean",
         "--allow-change-held-packages --allow-downgrades --allow-remove-essential --allow-unauthenticated "
         "--assume-no --assume-yes --audit --cli-version= --color --config-file= --default-release= "
         "--download --download-only --dry-run --fix-missing --fix-policy --force-yes --help --ignore-hold "
         "--ignore-missing --install-recommends --install-suggests --just-print --mark-auto --no-act "
         "--only-source --only-upgrade --option= --print-uris --quiet --recon --remove --show-upgraded "
         "--silent --simulate --snapshot= --target-release= --trivial-only --upgrade --version "
         "--with-source= --yes -S= -c= -d -h -m -o= -q -s -t= -u -v -y"),
        ("update",
         "--allow-change-held-packages --allow-downgrades --allow-insecure-repositories "
         "--allow-releaseinfo-change --allow-releaseinfo-change-codename "
         "--allow-releaseinfo-change-defaultpin --allow-releaseinfo-change-label "
         "--allow-releaseinfo-change-origin --allow-releaseinfo-change-suite "
         "--allow-releaseinfo-change-version --allow-remove-essential --allow-unauthenticated "
         "--allow-weak-repositories --assume-no --assume-yes --audit --cli-version= --color --config-file= "
         "--default-release= --download --download-only --error-on= --fix-missing --fix-policy --force-yes "
         "--help --ignore-hold --ignore-missing --install-recommends --install-suggests --list-cleanup "
         "--mark-auto --only-source --only-upgrade --option= --print-uris --quiet --remove --show-upgraded "
         "--silent --snapshot= --target-release= --trivial-only --upgrade --version --with-source= --yes "
         "-S= -c= -d -e= -h -m -o= -q -t= -u -v -y"),
        ("upgrade",
         "--allow-change-held-packages --allow-downgrades --allow-remove-essential --allow-unauthenticated "
         "--assume-no --assume-yes --audit --auto-remove --autoremove --cli-version= --color --comment= "
         "--config-file= --default-release= --download --download-only --dry-run --fix-broken "
         "--fix-missing --fix-policy --force-yes --help --ignore-hold --ignore-missing "
         "--install-recommends --install-suggests --just-print --list-columns --mark-auto --new-pkgs "
         "--no-act --only-source --only-upgrade --option= --planner= --print-uris --purge --quiet --recon "
         "--reinstall --remove --show-progress --show-upgraded --silent --simulate --snapshot= --solver= "
         "--strict-pinning --target-release= --trivial-only --update --upgrade --verbose-versions "
         "--version --with-source= --yes -S= -U -V -c= -d -f -h -m -o= -q -s -t= -u -v -y"),
        ("history-list history-info history-redo history-undo history-rollback edit-sources modernize-sources why why-not download changelog",
         "--allow-change-held-packages --allow-downgrades --allow-remove-essential --allow-unauthenticated "
         "--assume-no --assume-yes --audit --cli-version= --color --config-file= --default-release= "
         "--download --download-only --fix-missing --fix-policy --force-yes --help --ignore-hold "
         "--ignore-missing --install-recommends --install-suggests --mark-auto --only-source "
         "--only-upgrade --option= --print-uris --quiet --remove --show-upgraded --silent --snapshot= "
         "--target-release= --trivial-only --upgrade --version --with-source= --yes -S= -c= -d -h -m -o= "
         "-q -t= -u -v -y"),
        ("satisfy",
         "--allow-change-held-packages --allow-downgrades --allow-remove-essential --allow-unauthenticated "
         "--assume-no --assume-yes --audit --build-profiles= --cli-version= --color --config-file= "
         "--default-release= --download --download-only --dry-run --fix-broken --fix-missing --fix-policy "
         "--force-yes --help --host-architecture= --ignore-hold --ignore-missing --install-recommends "
         "--install-suggests --just-print --mark-auto --no-act --only-source --only-upgrade --option= "
         "--print-uris --purge --quiet --recon --remove --show-upgraded --silent --simulate --snapshot= "
         "--solver= --strict-pinning --target-release= --trivial-only --upgrade --version --with-source= "
         "--yes -P= -S= -a= -c= -d -f -h -m -o= -q -s -t= -u -v -y"),
        ("showsrc policy",
         "--allow-change-held-packages --allow-downgrades --allow-remove-essential --allow-unauthenticated "
         "--assume-no --assume-yes --audit --cli-version= --color --config-file= --default-release= "
         "--download --download-only --fix-missing --fix-policy --force-yes --generate --help "
         "--ignore-hold --ignore-missing --install-recommends --install-suggests --mark-auto --only-source "
         "--only-upgrade --option= --pkg-cache= --print-uris --quiet --remove --show-upgraded --silent "
         "--snapshot= --src-cache= --target-release= --trivial-only --upgrade --version --with-source= "
         "--yes -S= -c= -d -g -h -m -o= -p= -q -s= -t= -u -v -y"),
        ("depends rdepends",
         "--allow-change-held-packages --allow-downgrades --allow-remove-essential --allow-unauthenticated "
         "--assume-no --assume-yes --audit --breaks --cli-version= --color --config-file= --conflicts "
         "--default-release= --depends --download --download-only --enhances --fix-missing --fix-policy "
         "--force-yes --generate --help --ignore-hold --ignore-missing --implicit --important "
         "--install-recommends --install-suggests --installed --mark-auto --only-source --only-upgrade "
         "--option= --pkg-cache= --pre-depends --print-uris --quiet --recommends --recurse --remove "
         "--replaces --show-upgraded --silent --snapshot= --src-cache= --suggests --target-release= "
         "--trivial-only --upgrade --version --with-source= --yes -S= -c= -d -g -h -i -m -o= -p= -q -s= "
         "-t= -u -v -y"),
        ("build-dep",
         "--allow-change-held-packages --allow-downgrades --allow-remove-essential --allow-unauthenticated "
         "--arch-only --assume-no --assume-yes --audit --build-profiles= --cli-version= --color "
         "--config-file= --default-release= --download --download-only --dry-run --fix-broken "
         "--fix-missing --fix-policy --force-yes --help --host-architecture= --ignore-hold "
         "--ignore-missing --indep-only --install-recommends --install-suggests --just-print --mark-auto "
         "--no-act --only-source --only-upgrade --option= --print-uris --purge --quiet --recon --remove "
         "--show-upgraded --silent --simulate --snapshot= --solver= --strict-pinning --target-release= "
         "--trivial-only --upgrade --version --with-source= --yes -P= -S= -a= -c= -d -f -h -m -o= -q -s "
         "-t= -u -v -y"),
        ("source",
         "--allow-change-held-packages --allow-downgrades --allow-remove-essential --allow-unauthenticated "
         "--assume-no --assume-yes --audit --build --build-profiles= --cli-version= --color --compile "
         "--config-file= --debian-only --default-release= --diff-only --download --download-only --dry-run "
         "--dsc-only --fix-missing --fix-policy --force-yes --help --host-architecture= --ignore-hold "
         "--ignore-missing --install-recommends --install-suggests --just-print --mark-auto --no-act "
         "--only-source --only-upgrade --option= --print-uris --quiet --recon --remove --show-upgraded "
         "--silent --simulate --snapshot= --tar-only --target-release= --trivial-only --upgrade --version "
         "--with-source= --yes -P= -S= -a= -b -c= -d -h -m -o= -q -s -t= -u -v -y"),
    ),
    "apt-cache": (
        ("@ dotty xvcg help",
         "--audit --cli-version= --color --config-file= --help --option= --quiet --silent --version -c= -h "
         "-o= -q -v"),
        ("gencaches showpkg stats dump dumpavail showauto policy madison",
         "--audit --cli-version= --color --config-file= --default-release= --generate --help --option= "
         "--pkg-cache= --quiet --silent --snapshot= --src-cache= --target-release= --version "
         "--with-source= -S= -c= -g -h -o= -p= -q -s= -t= -v"),
        ("showsrc",
         "--audit --cli-version= --color --config-file= --default-release= --generate --help --only-source "
         "--option= --pkg-cache= --quiet --silent --snapshot= --src-cache= --target-release= --version "
         "--with-source= -S= -c= -g -h -o= -p= -q -s= -t= -v"),
        ("unmet",
         "--audit --cli-version= --color --config-file= --default-release= --generate --help --important "
         "--option= --pkg-cache= --quiet --silent --snapshot= --src-cache= --target-release= --version "
         "--with-source= -S= -c= -g -h -i -o= -p= -q -s= -t= -v"),
        ("search",
         "--audit --cli-version= --color --config-file= --default-release= --full --generate --help "
         "--names-only --option= --pkg-cache= --quiet --silent --snapshot= --src-cache= --target-release= "
         "--version --with-source= -S= -c= -f -g -h -n -o= -p= -q -s= -t= -v"),
        ("depends rdepends",
         "--audit --breaks --cli-version= --color --config-file= --conflicts --default-release= --depends "
         "--enhances --generate --help --implicit --important --installed --option= --pkg-cache= "
         "--pre-depends --quiet --recommends --recurse --replaces --silent --snapshot= --src-cache= "
         "--suggests --target-release= --version --with-source= -S= -c= -g -h -i -o= -p= -q -s= -t= -v"),
        ("show",
         "--all-versions --audit --cli-version= --color --config-file= --default-release= --generate "
         "--help --option= --pkg-cache= --quiet --silent --snapshot= --src-cache= --target-release= "
         "--version --with-source= -S= -a -c= -g -h -o= -p= -q -s= -t= -v"),
        ("pkgnames",
         "--all-names --audit --cli-version= --color --config-file= --default-release= --generate --help "
         "--option= --pkg-cache= --quiet --silent --snapshot= --src-cache= --target-release= --version "
         "--with-source= -S= -c= -g -h -o= -p= -q -s= -t= -v"),
    ),
    "apt-get": (
        ("@ help",
         "--audit --cli-version= --color --config-file= --help --option= --quiet --silent --version -c= -h "
         "-o= -q -v"),
        ("update",
         "--allow-change-held-packages --allow-downgrades --allow-insecure-repositories "
         "--allow-releaseinfo-change --allow-releaseinfo-change-codename "
         "--allow-releaseinfo-change-defaultpin --allow-releaseinfo-change-label "
         "--allow-releaseinfo-change-origin --allow-releaseinfo-change-suite "
         "--allow-releaseinfo-change-version --allow-remove-essential --allow-unauthenticated "
         "--allow-weak-repositories --assume-no --assume-yes --audit --cli-version= --color --config-file= "
         "--default-release= --download --download-only --error-on= --fix-missing --fix-policy --force-yes "
         "--help --ignore-hold --ignore-missing --install-recommends --install-suggests --list-cleanup "
         "--mark-auto --only-source --only-upgrade --option= --print-uris --quiet --remove --show-upgraded "
         "--silent --snapshot= --target-release= --trivial-only --upgrade --version --with-source= --yes "
         "-S= -c= -d -e= -h -m -o= -q -t= -u -v -y"),
        ("upgrade",
         "--allow-change-held-packages --allow-downgrades --allow-remove-essential --allow-unauthenticated "
         "--assume-no --assume-yes --audit --auto-remove --autoremove --cli-version= --color --comment= "
         "--config-file= --default-release= --download --download-only --dry-run --fix-broken "
         "--fix-missing --fix-policy --force-yes --help --ignore-hold --ignore-missing "
         "--install-recommends --install-suggests --just-print --list-columns --mark-auto --new-pkgs "
         "--no-act --only-source --only-upgrade --option= --planner= --print-uris --purge --quiet --recon "
         "--reinstall --remove --show-progress --show-upgraded --silent --simulate --snapshot= --solver= "
         "--strict-pinning --target-release= --trivial-only --update --upgrade --verbose-versions "
         "--version --with-source= --yes -S= -U -V -c= -d -f -h -m -o= -q -s -t= -u -v -y"),
        ("install reinstall remove purge autoremove autopurge dist-upgrade full-upgrade dselect-upgrade",
         "--allow-change-held-packages --allow-downgrades --allow-remove-essential --allow-unauthenticated "
         "--assume-no --assume-yes --audit --auto-remove --autoremove --cli-version= --color --comment= "
         "--config-file= --default-release= --download --download-only --dry-run --fix-broken "
         "--fix-missing --fix-policy --force-yes --help --ignore-hold --ignore-missing "
         "--install-recommends --install-suggests --just-print --list-columns --mark-auto --no-act "
         "--only-source --only-upgrade --option= --planner= --print-uris --purge --quiet --recon "
         "--reinstall --remove --show-progress --show-upgraded --silent --simulate --snapshot= --solver= "
         "--strict-pinning --target-release= --trivial-only --update --upgrade --verbose-versions "
         "--version --with-source= --yes -S= -U -V -c= -d -f -h -m -o= -q -s -t= -u -v -y"),
        ("auto-remove clean autoclean auto-clean distclean dist-clean check",
         "--allow-change-held-packages --allow-downgrades --allow-remove-essential --allow-unauthenticated "
         "--assume-no --assume-yes --audit --cli-version= --color --config-file= --default-release= "
         "--download --download-only --dry-run --fix-missing --fix-policy --force-yes --help --ignore-hold "
         "--ignore-missing --install-recommends --install-suggests --just-print --mark-auto --no-act "
         "--only-source --only-upgrade --option= --print-uris --quiet --recon --remove --show-upgraded "
         "--silent --simulate --snapshot= --target-release= --trivial-only --upgrade --version "
         "--with-source= --yes -S= -c= -d -h -m -o= -q -s -t= -u -v -y"),
        ("markauto unmarkauto download changelog",
         "--allow-change-held-packages --allow-downgrades --allow-remove-essential --allow-unauthenticated "
         "--assume-no --assume-yes --audit --cli-version= --color --config-file= --default-release= "
         "--download --download-only --fix-missing --fix-policy --force-yes --help --ignore-hold "
         "--ignore-missing --install-recommends --install-suggests --mark-auto --only-source "
         "--only-upgrade --option= --print-uris --quiet --remove --show-upgraded --silent --snapshot= "
         "--target-release= --trivial-only --upgrade --version --with-source= --yes -S= -c= -d -h -m -o= "
         "-q -t= -u -v -y"),
        ("build-dep",
         "--allow-change-held-packages --allow-downgrades --allow-remove-essential --allow-unauthenticated "
         "--arch-only --assume-no --assume-yes --audit --build-profiles= --cli-version= --color "
         "--config-file= --default-release= --download --download-only --dry-run --fix-broken "
         "--fix-missing --fix-policy --force-yes --help --host-architecture= --ignore-hold "
         "--ignore-missing --indep-only --install-recommends --install-suggests --just-print --mark-auto "
         "--no-act --only-source --only-upgrade --option= --print-uris --purge --quiet --recon --remove "
         "--show-upgraded --silent --simulate --snapshot= --solver= --strict-pinning --target-release= "
         "--trivial-only --upgrade --version --with-source= --yes -P= -S= -a= -c= -d -f -h -m -o= -q -s "
         "-t= -u -v -y"),
        ("satisfy",
         "--allow-change-held-packages --allow-downgrades --allow-remove-essential --allow-unauthenticated "
         "--assume-no --assume-yes --audit --build-profiles= --cli-version= --color --config-file= "
         "--default-release= --download --download-only --dry-run --fix-broken --fix-missing --fix-policy "
         "--force-yes --help --host-architecture= --ignore-hold --ignore-missing --install-recommends "
         "--install-suggests --just-print --mark-auto --no-act --only-source --only-upgrade --option= "
         "--print-uris --purge --quiet --recon --remove --show-upgraded --silent --simulate --snapshot= "
         "--solver= --strict-pinning --target-release= --trivial-only --upgrade --version --with-source= "
         "--yes -P= -S= -a= -c= -d -f -h -m -o= -q -s -t= -u -v -y"),
        ("source",
         "--allow-change-held-packages --allow-downgrades --allow-remove-essential --allow-unauthenticated "
         "--assume-no --assume-yes --audit --build --build-profiles= --cli-version= --color --compile "
         "--config-file= --debian-only --default-release= --diff-only --download --download-only --dry-run "
         "--dsc-only --fix-missing --fix-policy --force-yes --help --host-architecture= --ignore-hold "
         "--ignore-missing --install-recommends --install-suggests --just-print --mark-auto --no-act "
         "--only-source --only-upgrade --option= --print-uris --quiet --recon --remove --show-upgraded "
         "--silent --simulate --snapshot= --tar-only --target-release= --trivial-only --upgrade --version "
         "--with-source= --yes -P= -S= -a= -b -c= -d -h -m -o= -q -s -t= -u -v -y"),
        ("indextargets",
         "--allow-change-held-packages --allow-downgrades --allow-remove-essential --allow-unauthenticated "
         "--assume-no --assume-yes --audit --cli-version= --color --config-file= --default-release= "
         "--download --download-only --fix-missing --fix-policy --force-yes --format= --help --ignore-hold "
         "--ignore-missing --install-recommends --install-suggests --mark-auto --only-source "
         "--only-upgrade --option= --print-uris --quiet --release-info --remove --show-upgraded --silent "
         "--snapshot= --target-release= --trivial-only --upgrade --version --with-source= --yes -S= -c= -d "
         "-h -m -o= -q -t= -u -v -y"),
    ),
    "apt-config": (
        ("@ shell help",
         "--audit --cli-version= --color --config-file= --help --option= --quiet --silent --version -c= -h "
         "-o= -q -v"),
        ("dump",
         "--audit --cli-version= --color --config-file= --empty --format= --help --option= --quiet "
         "--silent --version -c= -h -o= -q -v"),
    ),
    "apt-mark": (
        ("@ help",
         "--audit --cli-version= --color --config-file= --help --option= --quiet --silent --version -c= -h "
         "-o= -q -v"),
        ("auto manual hold unhold",
         "--audit --cli-version= --color --config-file= --dry-run --file= --help --just-print --no-act "
         "--option= --quiet --recon --silent --simulate --version --with-source= -c= -f= -h -o= -q -s -v"),
        ("minimize-manual",
         "--assume-no --assume-yes --audit --cli-version= --color --config-file= --dry-run --file= --help "
         "--just-print --no-act --option= --quiet --recon --silent --simulate --version --with-source= "
         "--yes -c= -f= -h -o= -q -s -v -y"),
        ("install remove deinstall purge",
         "--audit --cli-version= --color --config-file= --dry-run --help --just-print --no-act --option= "
         "--quiet --recon --silent --simulate --version --with-source= -c= -h -o= -q -s -v"),
        ("showauto showmanual showhold showholds showheld",
         "--audit --cli-version= --color --config-file= --file= --help --option= --quiet --silent "
         "--version --with-source= -c= -f= -h -o= -q -v"),
        ("showinstall showinstalls showdeinstall showdeinstalls showremove showremoves showpurge showpurges",
         "--audit --cli-version= --color --config-file= --help --option= --quiet --silent --version "
         "--with-source= -c= -h -o= -q -v"),
        ("markauto unmarkauto",
         "--audit --cli-version= --color --config-file= --dry-run --file= --help --just-print --no-act "
         "--option= --quiet --recon --silent --simulate --verbose --version --with-source= -c= -f= -h -o= "
         "-q -s -v"),
    ),
}


# Wording from the shipped APT manual and fixed help.
VERB_HELP = {
    'auto': 'Mark the given packages as automatically installed',
    'autoclean': 'Erase old downloaded archive files',
    'autoremove': 'Remove automatically all unused packages',
    'build-dep': 'Configure build-dependencies for source packages',
    'changelog': 'Download and display the changelog for the given package',
    'check': 'Verify that there are no broken dependencies',
    'clean': 'Erase downloaded archive files',
    'depends': 'Show raw dependency information for a package',
    'dist-upgrade': 'Distribution upgrade, see apt-get(8)',
    'download': 'Download the binary package into the current directory',
    'dselect-upgrade': 'Follow dselect selections',
    'dump': 'show the active configuration setting',
    'edit-sources': 'edit the source information file',
    'full-upgrade': 'upgrade the system by removing/installing/upgrading packages',
    'history-info': 'show info on specific transactions',
    'history-list': 'show list of history',
    'history-redo': 'redo transactions',
    'history-rollback': 'rollback transactions',
    'history-undo': 'undo transactions',
    'hold': 'Mark a package as held back',
    'install': 'Install new packages (pkg is libc6 not libc6.deb)',
    'list': 'list packages based on package names',
    'manual': 'Mark the given packages as manually installed',
    'minimize-manual': 'Mark all dependencies of meta packages as automatically installed.',
    'modernize-sources': 'modernize .list files to .sources files',
    'pkgnames': 'List the names of all packages in the system',
    'policy': 'Show policy settings',
    'purge': 'Remove packages and config files',
    'rdepends': 'Show reverse dependency information for a package',
    'reinstall': 'Reinstall packages (pkg is libc6 not libc6.deb)',
    'remove': 'Remove packages',
    'satisfy': 'Satisfy dependency strings',
    'search': 'Search the package list for a regex pattern',
    'shell': 'get configuration values via shell evaluation',
    'show': 'Show a readable record for the package',
    'showauto': 'Print the list of automatically installed packages',
    'showhold': 'Print the list of packages on hold',
    'showmanual': 'Print the list of manually installed packages',
    'showsrc': 'Show source records',
    'source': 'Download source archives',
    'unhold': 'Unset a package set as held back',
    'update': 'Retrieve new lists of packages',
    'upgrade': 'Perform an upgrade',
    'why': 'produce a reason trace for the current state of the package',
    'why-not': 'produce a reason trace for the current state of the package',
}
