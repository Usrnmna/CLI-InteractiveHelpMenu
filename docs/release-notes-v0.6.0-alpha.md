## v0.6.0-alpha — Reading command help across terminal sizes

Use **Alt-H** on a pending Bash command to open the menu. **Shift+D** cycles through Simple, Detailed and Expanded in either layout, keeping the selected option and filter. Section headings, option spellings and key hints use distinct styling. Related value forms share explanations. For example, rsync’s bandwidth units are grouped separately from special inputs.

- **Narrow terminals.** Set `export CLI_HELP_NARROW_MENU=1` for Categories → Options → Details at 60–79 columns. Use **→** to open the next screen and **←** to return. The split view resumes at 80 columns. The default split layout also works at the 60×16 minimum.
- **Long explanations.** Press **Space** to page through overflowing Details and wrap to the beginning. When the terminal resizes, the menu rewraps the explanation and keeps the reading position at the same phrase where possible. Compact headers give the command path and level key priority. If a wrapped prompt leaves a duplicate row after returning to Bash, **Ctrl-L** redraws it and preserves the edit.
- **Clipped summaries.** The highlighted summary pauses for two seconds, then scrolls horizontally if it needs more room. The option name and neighboring rows stay in place. Press **m** to toggle motion for the open menu.
- **APT and Bash help.** APT option explanations use the matching Noble and Resolute documentation. For example, Detailed explains how simulation computes a plan with locking disabled. Expanded decodes the simulated dpkg actions and the effect of configuration permissions. Bash builtin help focuses on the selected option.
- **Five recorded workflows.** The documentation follows a simulated Graphviz install, a timed Bash prompt, a Git worktree listing, an rsync rate limit and navigation through 92 FFmpeg codec parameters. Each includes multiple selections and all three detail levels. Resize captures document how searches, paging, selection and the return to Bash behave.

For Linux x86_64, download the installer and its matching checksum into the same directory. The menu requires Bash 4.4+, Python 3.10+ with curses, a UTF-8 terminal and at least 60×16 cells.

```bash
sha256sum -c cli-interactive-help-v0.6.0-alpha-linux-x86_64.run.checksum &&
bash cli-interactive-help-v0.6.0-alpha-linux-x86_64.run --verify &&
bash cli-interactive-help-v0.6.0-alpha-linux-x86_64.run install --prefix "$HOME/apps/cli-help" --no-rc &&
source "$HOME/apps/cli-help/bash/interactive-help.bash"
```

The Linux tarball includes the compiled launcher and runtime. The standalone launcher needs the adjacent extracted runtime. The source archive includes the code, tests, documentation and demonstrations.
