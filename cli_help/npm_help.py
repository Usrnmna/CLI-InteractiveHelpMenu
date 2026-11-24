"""Explanations for syntax-only npm declarations from the npm 9.2.0 config definitions."""

# Only declarations actually supplied by fixed help can receive these notes.
# The short spellings are the aliases in npm's tagged config definitions.
ALIASES = {"-S": "--save", "-E": "--save-exact", "-g": "--global", "-w": "--workspace", "-ws": "--workspaces"}
EXPLANATIONS = {
    "--save": "Record installed dependencies in package.json.",
    "--no-save": "Install without recording dependencies in package.json.",
    "--save-prod": "Record the package in dependencies.",
    "--save-dev": "Record the package in devDependencies.",
    "--save-optional": "Record the package in optionalDependencies.",
    "--save-peer": "Record the package in peerDependencies.",
    "--save-bundle": "Include the saved dependency in bundleDependencies.",
    "--save-exact": "Record the exact installed version.",
    "--global": "Install into the global prefix.",
    "--install-strategy": "Choose how npm lays out packages in node_modules.",
    "--legacy-bundling": "Install dependencies in nested directories.",
    "--global-style": "Keep only direct dependencies at the top level.",
    "--omit": "Omit the selected dependency type from the installation on disk.",
    "--strict-peer-deps": "Fail installation on conflicting peer dependencies.",
    "--no-package-lock": "Ignore package-lock.json during installation.",
    "--foreground-scripts": "Run package build scripts in the foreground.",
    "--ignore-scripts": "Skip package lifecycle scripts during installation.",
    "--no-audit": "Skip sending the audit report to registries.",
    "--no-bin-links": "Skip creating executable links for package binaries.",
    "--no-fund": "Suppress the funding message after installation.",
    "--dry-run": "Report what npm would install without applying changes.",
    "--workspace": "Select a workspace by name or path.",
    "--workspaces": "Run in all configured workspaces.",
    "--include-workspace-root": "Include the root project in the workspace operation.",
    "--no-install-links": "Link local file dependencies instead of packing them.",
    "--if-present": "Skip a missing script without reporting an error.",
    "--script-shell": "Choose the shell used to run scripts.",
}
QUALIFICATIONS = {
    "--no-save": "This also prevents writes to package-lock.json.",
    "--save-bundle": "Peer dependencies cannot be bundled.",
    "--omit": "Omitted dependencies are still resolved and recorded in the lockfile. Repeat the option for multiple types.",
    "--strict-peer-deps": "The legacy-peer-deps setting bypasses peer dependency resolution.",
    "--no-package-lock": "This also prevents writing the lockfile during installation.",
    "--no-install-links": "This setting has no effect on workspaces.",
    "--if-present": "An existing script that fails still returns an error.",
    "--workspace": "Repeat the option to select additional workspaces. A parent directory selects its workspaces.",
    "--foreground-scripts": "Build scripts share standard input, output and error with npm.",
}


def explain_syntax_only_options(profile):
    """Enrich recognized npm option rows that still lack prose after merging.

    Preserve declarations, insertion, arity, and any local manual explanation.
    Attribute external wording to its release because a synopsis alone cannot
    identify the installed npm version.
    """
    if profile["command"] not in (["npm", "install"], ["npm", "run"]):
        return
    for category in profile["categories"]:
        for option in category["options"]:
            if option["summary"] != "Documented option" or "Syntax: [" not in option["detail"]:
                continue
            flag = ALIASES.get(option["flag"], option["flag"])
            summary = EXPLANATIONS.get(flag)
            if not summary:
                continue
            if flag == "--ignore-scripts" and profile["command"][1] == "run":
                summary = "Run the requested script without its pre- and post-scripts."
            explanation = QUALIFICATIONS.get(flag)
            option["summary"] = summary
            option["detail"] += "\n\n" + summary
            if explanation:
                option["detail"] += " " + explanation
            option["detail"] += "\nReference: npm 9.2.0 configuration. The local synopsis supplies the spelling and syntax."
