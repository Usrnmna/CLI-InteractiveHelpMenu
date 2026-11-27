"""Reviewed option guidance for the APT 2.8 and 3.2 declarations in apt_editions.

The five edition-matched manuals and the sources for command-specific exceptions
are listed in the Ubuntu coverage audit. Lookup never adds a selectable spelling.
"""


# Each record gives the list summary, operational guidance and a further qualification.
TOPICS = {
    "--all-names": (
        "Include every name known to the cache",
        "For pkgnames, include virtual package names and names referenced by missing dependencies.",
        "Configuration: APT::Cache::AllNames.",
    ),
    "--all-versions": (
        "Show all available package records",
        "For show, include a record for each available version. Disabling all versions restricts output to the installation candidate.",
        "Configuration: APT::Cache::AllVersions.",
    ),
    "--allow-change-held-packages": (
        "Allow unattended changes to held packages",
        "APT can continue without confirmation when the plan changes a package marked on hold. Review the planned changes before applying them.",
        "Configuration: APT::Get::allow-change-held-packages.",
    ),
    "--allow-downgrades": (
        "Allow unattended package downgrades",
        "APT can continue without confirmation when the plan selects an older version. A downgrade can damage the installation.",
        "Configuration: APT::Get::allow-downgrades.",
    ),
    "--allow-insecure-repositories": (
        "Accept unverifiable repository data on update",
        "Permit index downloads when a source lacks sufficient authentication. Ordinarily update fails without a valid signature.",
        "Configuration: Acquire::AllowInsecureRepositories. See apt-secure(8) for repository authentication.",
    ),
    "--allow-releaseinfo-change": (
        "Accept changed repository release information",
        "An update can stop if a repository changes its identity or release metadata. This switch accepts the change for the update.",
        "Field-specific variants limit permission to one field. Configuration: Acquire::AllowReleaseInfoChange.",
    ),
    "--allow-remove-essential": (
        "Allow unattended removal of essential packages",
        "APT can continue without confirmation when the plan removes an essential package. This can leave the system unusable.",
        "Configuration: APT::Get::allow-remove-essential.",
    ),
    "--allow-unauthenticated": (
        "Allow packages that cannot be authenticated",
        "Suppress the authentication prompt for this invocation. Package authenticity must be established separately.",
        "The manual recommends considering a source-specific Trusted setting before a global override. Configuration: APT::Get::AllowUnauthenticated.",
    ),
    "--allow-weak-repositories": (
        "Allow weak repository authentication on update",
        "The source provides security information, but APT considers its cryptography too weak. This exception is disabled by default.",
        "Configuration: Acquire::AllowWeakRepositories in apt.conf(5).",
    ),
    "--arch-only": (
        "Process architecture-dependent build dependencies",
        "With build-dep, restrict dependency processing to the architecture-dependent build.",
        "Configuration: APT::Get::Arch-Only.",
    ),
    "--assume-no": (
        "Answer no to prompts",
        "APT supplies a negative response when an operation asks for confirmation.",
        "Configuration: APT::Get::Assume-No.",
    ),
    "--audit": (
        "Show audit and notice messages",
        "Notice messages remain visible when quiet output is enabled.",
        "Progress output still follows the quiet setting. Configuration: APT::Audit.",
    ),
    "--autoremove": (
        "Remove unused automatic dependencies",
        "During install or remove, also remove automatic packages no longer required by manually installed packages.",
        "Review the removal list. Configuration: APT::Get::AutomaticRemove.",
    ),
    "--build-profiles": (
        "Activate build profiles",
        "Supply one profile or a comma-separated list for source compilation and build-dependency resolution.",
        "No profiles are active by default. Configuration: APT::Build-Profiles.",
    ),
    "--cli-version": (
        "Select CLI compatibility behavior",
        "Use MAJOR.MINOR, or just MAJOR for its latest supported minor level.",
        "APT 3.2 also calls this feature level 2.12, 1.22 and 0.32 in the corresponding tracks. Configuration: APT::Version.",
    ),
    "--color": (
        "Enable colored output",
        "APT normally uses color on supported interactive terminals. Environment controls include NO_COLOR and APT_NO_COLOR.",
        "Configuration: APT::Color and its scope in apt.conf(5).",
    ),
    "--comment": (
        "Attach a comment to the transaction history",
        "The supplied text goes in the Comment field of APT's history.log. Quote a multiword comment as one argument.",
        "Configuration: APT::History::Comment.",
    ),
    "--compile": (
        "Build the downloaded source package",
        "With source, compile the retrieved sources to produce binary packages. The host architecture can be selected separately.",
        "Configuration: APT::Get::Compile.",
    ),
    "--config-file": (
        "Read additional APT configuration",
        "APT reads its default configuration before the file supplied with -c.",
        "To load a file before the defaults, set APT_CONFIG. Files use apt.conf(5) syntax.",
    ),
    "--diff-only": (
        "Fetch only the Debian changes archive",
        "With source, retrieve the Debian changes component of the source package.",
        "Configuration: APT::Get::Diff-Only.",
    ),
    "--download": (
        "Allow fetching missing package archives",
        "Enable archive retrieval when APT::Get::Download has been disabled. The opposite switch is --no-download.",
        "To retrieve archives without installing them, use --download-only.",
    ),
    "--download-only": (
        "Download packages without installing them",
        "Retrieve the package archives for the planned operation. APT leaves them packed and skips installation.",
        "Configuration: APT::Get::Download-Only.",
    ),
    "--dsc-only": (
        "Fetch only the source description file",
        "With source, retrieve the .dsc control file without requesting the source tar archives.",
        "Configuration: APT::Get::Dsc-Only.",
    ),
    "--empty": (
        "Include empty configuration values",
        "The dump command includes empty values by default. Use --no-empty to omit them.",
        "Configuration: APT::Config::Dump::EmptyValue.",
    ),
    "--error-on": (
        "Fail update on any error",
        "Supply the mode any to make even a transient index retrieval failure fail the update.",
        "Example: apt-get update --error-on=any.",
    ),
    "--file": (
        "Select an alternative package state file",
        "Read and write automatic installation marks in this file. The default is extended_states under Dir::State.",
        "Configuration: Dir::State::extended_states.",
    ),
    "--fix-broken": (
        "Repair broken package dependencies",
        "With install or remove, omit package names to let APT find a repair. If names are supplied, they must resolve the whole problem.",
        "Combining this option with --fix-missing can fail. Configuration: APT::Get::Fix-Broken.",
    ),
    "--fix-missing": (
        "Hold back packages that cannot be retrieved",
        "A failed download or integrity check can hold back even a package explicitly requested for installation.",
        "Combining this option with --fix-broken can fail. Configuration: APT::Get::Fix-Missing.",
    ),
    "--fix-policy": (
        "Repair policy-broken dependencies",
        "Enable broken-dependency repair and mark policy-broken packages for installation with important dependencies included.",
        "Configuration: APT::Get::Fix-Policy-Broken.",
    ),
    "--force-yes": (
        "Force confirmation of potentially harmful actions",
        "This deprecated switch can bypass safeguards and leave the system unusable.",
        "APT documents narrower switches for downgrades, unauthenticated packages, held-package changes and essential-package removal.",
    ),
    "--full": (
        "Show complete search records",
        "Print the full package record for each search match in place of the short listing.",
        "Configuration: APT::Cache::ShowFull.",
    ),
    "--generate": (
        "Regenerate the package cache as needed",
        "Automatic generation is enabled by default. Use --no-generate to inspect the existing cache as it stands.",
        "Configuration: APT::Cache::Generate.",
    ),
    "--help": (
        "Show command usage",
        "Read the program's usage synopsis with -h or --help. A package name is unnecessary.",
        "The synopsis distinguishes commands from options and their operands.",
    ),
    "--host-architecture": (
        "Select the architecture to build for",
        "Set the target for source --compile and for satisfying cross-build dependencies.",
        "If unset, the host architecture matches the build architecture. Configuration: APT::Get::Host-Architecture.",
    ),
    "--ignore-hold": (
        "Override package holds",
        "Allow APT to change a held package during this operation, including during a distribution upgrade.",
        "Configuration: APT::Ignore-Hold.",
    ),
    "--implicit": (
        "Include implicit dependencies and conflicts",
        "Dependency listings normally show relationships written in the metadata. A conflict can also imply a conflict with the same package of another architecture.",
        "Configuration: APT::Cache::ShowImplicit.",
    ),
    "--important": (
        "Show only important dependency relationships",
        "For depends and unmet, limit the display to Depends and Pre-Depends relationships.",
        "Configuration: APT::Cache::Important.",
    ),
    "--indep-only": (
        "Process architecture-independent build dependencies",
        "With build-dep, restrict dependency processing to the architecture-independent build.",
        "Configuration: APT::Get::Indep-Only.",
    ),
    "--install-recommends": (
        "Include recommended dependencies",
        "Treat Recommends as dependencies during installation, including when local configuration normally omits them.",
        "Configuration: APT::Install-Recommends.",
    ),
    "--install-suggests": (
        "Include suggested dependencies",
        "Treat Suggests as dependencies when calculating the installation plan.",
        "Configuration: APT::Install-Suggests.",
    ),
    "--installed": (
        "Restrict dependency output to installed packages",
        "In depends and rdepends, exclude packages that have no installed version.",
        "Configuration: APT::Cache::Installed.",
    ),
    "--list-cleanup": (
        "Clean obsolete package indexes",
        "APT normally erases obsolete files from /var/lib/apt/lists as it manages the package lists.",
        "Use --no-list-cleanup to retain those files when frequently switching sources. Configuration: APT::Get::List-Cleanup.",
    ),
    "--list-columns": (
        "Arrange package lists in columns",
        "Display the package list in an ls-style layout. Use --no-list-columns for output without columns.",
        "Configuration: APT::Get::List-Columns.",
    ),
    "--manual-installed": (
        "List manually installed packages",
        "Filter apt list to packages marked as manually installed. APT distinguishes these from dependencies it installed automatically.",
        "Configuration: APT::Cmd::Manual-Installed.",
    ),
    "--mark-auto": (
        "Mark newly installed packages as automatic",
        "After a successful installation, new packages are marked as dependencies. They can become eligible for autoremove when manual packages no longer need them.",
        "Configuration: APT::Get::Mark-Auto.",
    ),
    "--names-only": (
        "Search package names and provided names",
        "Restrict search to names. A match that occurs only in a long description is excluded.",
        "Configuration: APT::Cache::NamesOnly.",
    ),
    "--new-pkgs": (
        "Allow new dependencies during upgrade",
        "An installed package can be upgraded when it needs additional packages. This upgrade mode still disallows removals.",
        "Configuration: APT::Get::Upgrade-Allow-New.",
    ),
    "--no-download": (
        "Use previously downloaded archives",
        "Combine with --ignore-missing to restrict installation to .deb files already available locally.",
        "Configuration: disables APT::Get::Download.",
    ),
    "--no-install-recommends": (
        "Omit recommended dependencies",
        "APT leaves Recommends out of dependency selection for installation. Required dependencies still apply.",
        "Configuration: disables APT::Install-Recommends.",
    ),
    "--no-remove": (
        "Abort if the plan removes a package",
        "APT stops immediately, without a confirmation prompt, when the computed plan includes a removal.",
        "Configuration: disables APT::Get::Remove.",
    ),
    "--no-upgrade": (
        "Keep already installed requested packages at their versions",
        "With install, skip upgrades of named packages that are already installed. New packages can still be requested.",
        "Configuration: disables APT::Get::Upgrade.",
    ),
    "--only-source": (
        "Interpret operands as source package names",
        "For source and build-dep, APT skips binary-to-source name lookup. Supply the source package name itself.",
        "Configuration: APT::Get::Only-Source.",
    ),
    "--only-upgrade": (
        "Upgrade only already installed packages",
        "With install, ignore requests for packages that have no installed version.",
        "Configuration: APT::Get::Only-Upgrade.",
    ),
    "--option": (
        "Set an APT configuration item",
        "Pass one assignment per option, for example -o APT::Get::Assume-No=true.",
        "Repeat -o or --option to set multiple configuration items for this invocation.",
    ),
    "--pkg-cache": (
        "Select the binary package cache file",
        "Use this file for the primary package cache shared by cache operations.",
        "Configuration: Dir::Cache::pkgcache.",
    ),
    "--planner": (
        "Choose an installation planner",
        "The planner orders package installation, configuration and removal after dependency resolution.",
        "Configuration: APT::Planner. Dir::Bin::Planners controls external planner lookup.",
    ),
    "--print-uris": (
        "Print archive locations instead of fetching files",
        "Package records give the URI, destination filename, size and expected MD5. The remote and destination names can differ.",
        "With update, size and MD5 are omitted and the caller must decompress compressed indexes.",
    ),
    "--purge": (
        "Also delete package configuration on removal",
        "A planned purge is marked with an asterisk. Using remove --purge requests the purge operation.",
        "Package purge leaves files in users' home directories alone. Configuration: APT::Get::Purge.",
    ),
    "--quiet": (
        "Reduce progress output",
        "Omit progress indicators for log output. Repeating -q increases quietness up to level 2.",
        "Use -q=LEVEL to override the configured quiet level.",
    ),
    "--recurse": (
        "Follow dependencies recursively",
        "With depends or rdepends, print each reachable package once, including packages beyond the first dependency level.",
        "Configuration: APT::Cache::RecurseDepends.",
    ),
    "--reinstall": (
        "Reinstall an already installed package",
        "APT can unpack and install a package again even when its installed version is already the newest available.",
        "Configuration: APT::Get::ReInstall.",
    ),
    "--release-info": (
        "Include downloaded release information",
        "For indextargets, the default view lists downloaded targets with their release fields. --no-release-info also lists targets that have not been downloaded.",
        "Without release information, the reported filename may refer to an index that does not exist locally.",
    ),
    "--remove": (
        "Permit removals in the computed plan",
        "Allow a transaction to include package removals. --no-remove makes APT abort if removal would be necessary.",
        "Configuration: APT::Get::Remove.",
    ),
    "--show-progress": (
        "Show package installation progress",
        "Display terminal progress during installation, upgrades and removals.",
        "APT documents its machine-readable progress stream separately in README.progress-reporting.",
    ),
    "--show-upgraded": (
        "List packages scheduled for upgrade",
        "Include the package names in the upgrade report. --no-show-upgraded suppresses that list.",
        "Configuration: APT::Get::Show-Upgraded.",
    ),
    "--snapshot": (
        "Choose an archive snapshot",
        "The source entry must enable snapshots. Supply a UTC timestamp such as 20220102T030405Z.",
        "Configuration: APT::Snapshot. The Snapshot field is documented in sources.list(5).",
    ),
    "--solver": (
        "Choose a dependency solver",
        "Supply a solver name. The packaged solver protocol documents internal and the lookup directory for external solvers.",
        "Configuration: APT::Solver. Dir::Bin::Solvers controls external solver lookup.",
    ),
    "--src-cache": (
        "Select the source cache file",
        "gencaches saves parsed remote package metadata here to avoid reparsing all indexes when rebuilding the primary cache.",
        "Configuration: Dir::Cache::srcpkgcache.",
    ),
    "--strict-pinning": (
        "Require the solver to respect pinning",
        "Ask the solver to adhere strictly to package pinning. The external solver protocol distinguishes strict policy from allowing deviations.",
        "Configuration: APT::Solver::Strict-Pinning.",
    ),
    "--tar-only": (
        "Fetch only the source tar archive",
        "With source, request the tar component of the source package.",
        "Configuration: APT::Get::Tar-Only.",
    ),
    "--target-release": (
        "Prefer a target distribution",
        "The selected release receives a default pin priority of 990. Specific package pins still take precedence.",
        "Use a release identifier such as a codename or suite. Configuration: APT::Default-Release.",
    ),
    "--trivial-only": (
        "Accept only trivial operations",
        "Answer no when APT would need confirmation to proceed. This is useful when a command should stop at such a prompt.",
        "Configuration: APT::Get::Trivial-Only.",
    ),
    "--update": (
        "Refresh indexes before the package operation",
        "Run update before the requested installation, removal or upgrade. This can fetch indexes for a selected snapshot.",
        "Each phase acquires its own locks. A successful update does not guarantee that installation can acquire its lock.",
    ),
    "--upgradable": (
        "List installed packages with available upgrades",
        "Filter the package-name patterns supplied to apt list to show packages that can be upgraded.",
        "Configuration: APT::Cmd::Upgradable.",
    ),
    "--upgrade": (
        "Allow upgrades of requested installed packages",
        "With install, enable upgrading a named package that already has an installed version. --no-upgrade overrides this behavior.",
        "Configuration: APT::Get::Upgrade.",
    ),
    "--verbose-versions": (
        "Show full package versions",
        "Include version numbers for packages being installed or upgraded.",
        "Configuration: APT::Get::Show-Versions.",
    ),
    "--version": (
        "Print the APT program version",
        "Use --version on the program itself to identify the installed APT release.",
        "The version describes the APT tool. Use a package query to inspect versions of other packages.",
    ),
    "--with-source": (
        "Add a local package metadata source",
        "Repeat the option for multiple files. APT recognizes supported .deb, .dsc, .changes, Packages and Sources files by name.",
        "Packages and Sources indexes may be compressed. APT treats these sources as trusted.",
    ),
    "--yes": (
        "Answer yes to prompts",
        "Run noninteractively. APT can still abort on held-package changes, unauthenticated packages or essential-package removal.",
        "Configuration: APT::Get::Assume-Yes.",
    ),
    "cache-only-source": (
        "Look up source records by source package name",
        "showsrc ordinarily accepts a binary package name and looks up its source. Restrict the match to source package names.",
        "Configuration: APT::Cache::Only-Source.",
    ),
    "config-format": (
        "Format each configuration entry",
        "Use %f for the full key, %t for its last name component and %v for its value. Uppercase field codes encode special characters.",
        "Use %n for a newline, %N for a tab and %% for a literal percent.",
    ),
    "index-format": (
        "Format each index target",
        "Supply a template using uppercase field names wrapped in $(), for example '$(FILENAME)'. Change field-name hyphens to underscores.",
        "Without a template, indextargets prints deb822 records. Remaining arguments can filter records by their fields.",
    ),
    "list-all-versions": (
        "List all available package versions",
        "Display the versions matching the package-name patterns, including available versions beyond the candidate.",
        "Configuration: APT::Cmd::All-Versions.",
    ),
    "list-installed": (
        "List installed packages",
        "Limit apt list results to packages with an installed version. Package-name globs further narrow the listing.",
        "Configuration: APT::Cmd::Installed.",
    ),
    "list-verbose": (
        "Include package summaries in the list",
        "Add the short package description to apt list output for each matching package.",
        "Configuration: APT::Cmd::List-Include-Summary.",
    ),
    "mark-no": (
        "Decline changes to automatic marks",
        "For minimize-manual, decline the prompt before the new automatic marks are saved.",
        "Configuration: APT::Get::Assume-No.",
    ),
    "mark-simulate": (
        "Preview package mark or selection changes",
        "Compute the requested changes without saving automatic marks or dpkg selections.",
        "Configuration: APT::Mark::Simulate.",
    ),
    "mark-verbose": (
        "Report individual changes to automatic marks",
        "The legacy markauto and unmarkauto commands print the changed package name and the new automatic flag, 1 or 0.",
        "Configuration: APT::MarkAuto::Verbose.",
    ),
    "mark-yes": (
        "Confirm changes to automatic marks",
        "For minimize-manual, accept the prompt before saving dependency mark changes.",
        "Configuration: APT::Get::Assume-Yes.",
    ),
    "quiet-two": (
        "Select quiet level 2",
        "Suppress progress output at the highest documented quiet level. The equivalent numeric form is -q=2.",
        "Configuration: quiet.",
    ),
    "show-full": (
        "Include additional package record fields",
        "With apt show or info, retain fields normally hidden from the interactive record, such as Filename and package hashes.",
        "Configuration: APT::Cache::ShowFull.",
    ),
}


# Resolve overloaded short forms only against declarations present on this route.
# APT registers command-specific switches before the common -v/--version.
ALIASES = {
    "-P": ("--build-profiles",), "-S": ("--snapshot",), "-U": ("--update",),
    "-V": ("--verbose-versions",), "-a": ("--all-versions", "--host-architecture"),
    "-b": ("--compile",), "-c": ("--config-file",), "-d": ("--download-only",),
    "-e": ("--error-on",), "-f": ("--full", "--file", "--fix-broken"),
    "-g": ("--generate",), "-h": ("--help",), "-i": ("--important", "--installed"),
    "-m": ("--fix-missing",), "-n": ("--names-only",), "-o": ("--option",),
    "-p": ("--pkg-cache",), "-q": ("--quiet",), "-s": ("--src-cache", "--simulate"),
    "-t": ("--target-release",), "-u": ("--upgradable", "--show-upgraded"),
    "-v": ("--verbose", "--version"), "-y": ("--yes",),
}
LONG_ALIASES = {
    "--silent": "--quiet", "--default-release": "--target-release", "--assume-yes": "--yes",
    "--auto-remove": "--autoremove", "--debian-only": "--diff-only", "--build": "--compile",
    "--ignore-missing": "--fix-missing", "--upgradeable": "--upgradable",
    "--dry-run": "--simulate", "--just-print": "--simulate", "--no-act": "--simulate",
    "--recon": "--simulate", "-qq": "quiet-two",
}
RELATIONS = {
    "--pre-depends": "Pre-Depends", "--depends": "Depends", "--recommends": "Recommends",
    "--suggests": "Suggests", "--replaces": "Replaces", "--breaks": "Breaks",
    "--conflicts": "Conflicts", "--enhances": "Enhances",
}
LIST_TOPICS = {"--installed": "list-installed", "--all-versions": "list-all-versions",
               "--verbose": "list-verbose"}
MARK_TOPICS = {"--simulate": "mark-simulate", "--yes": "mark-yes", "--assume-no": "mark-no",
               "--verbose": "mark-verbose"}


def option_guidance(program, verb, flag, declarations):
    """Return display prose for an already-declared flag, resolving its owner and polarity."""
    key = LONG_ALIASES.get(flag, flag)
    if flag in ALIASES:
        key = next(name for name in ALIASES[flag] if name in declarations)
    if key in RELATIONS:
        relation = RELATIONS[key]
        return (f"Include {relation} relationships",
                f"Behavior: Show the {relation} relationships in depends or rdepends output.\n"
                f"Notes: Use --no-{flag[2:]} to omit this relationship from the listing.")
    if key.startswith("--allow-releaseinfo-change-"):
        field = key.removeprefix("--allow-releaseinfo-change-")
        return (f"Accept a change to the repository {field} field",
                f"Behavior: Allow update to accept a changed {field} value in repository release information.\n"
                "Notes: Other changed fields still require their own permission or confirmation.")
    if program == "apt-mark":
        key = MARK_TOPICS.get(key, key)
    elif program == "apt" and verb == "list":
        key = LIST_TOPICS.get(key, key)
    if key == "--format":
        key = "config-format" if program == "apt-config" else "index-format"
    elif key == "--full" and verb in {"show", "info"}:
        key = "show-full"
    elif key == "--only-source" and verb == "showsrc":
        key = "cache-only-source"
    summary, behavior, extra = TOPICS[key]
    if key in {"quiet-two", "--quiet"} and program in {"apt", "apt-get"} and "--yes" in declarations:
        behavior = "Quiet level 2 (-qq) implies yes to prompts. Use a no-action mode such as --simulate when previewing changes."
    if not extra.startswith(("Example: ", "Configuration: ")):
        extra = "Notes: " + extra
    return summary, "Behavior: " + behavior + "\n" + extra
