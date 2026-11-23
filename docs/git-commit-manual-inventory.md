# Git commit manual inventory

The inventory follows DESCRIPTION, OPTIONS, DATE FORMATS and HOOKS in the upstream and Ubuntu commit manuals. The upstream manual was last revised in 2.55.0 and lists no changes through 2.56.1. Noble ships git-man 1:2.43.0-1ubuntu7.4 and Resolute ships 1:2.53.0-1ubuntu1.1. The tagged commit implementation distinguishes similarly named status and diff options. [Upstream commit](https://git-scm.com/docs/git-commit/2.55.0) · [Noble commit](https://manpages.ubuntu.com/manpages/noble/man1/git-commit.1.html) · [Resolute commit](https://manpages.ubuntu.com/manpages/resolute/man1/git-commit.1.html) · [Noble implementation](https://raw.githubusercontent.com/git/git/v2.43.0/builtin/commit.c) · [Resolute implementation](https://raw.githubusercontent.com/git/git/v2.53.0/builtin/commit.c) · [Upstream implementation](https://raw.githubusercontent.com/git/git/v2.56.0/builtin/commit.c)

## Selectable inventory

Each spelling in a row is separately selectable. Required short operands accept joined and separate forms. Required long operands accept equals and separate forms. Optional short operands must be attached directly. Optional long operands must be attached with an equals sign. The literal menu spelling retains any trailing equals sign shown below. “All” covers both Ubuntu packages and the pinned upstream release. The final rows identify options and resets exposed by the packaged parser. [Noble fixed usage](../tests/fixtures/git-commit-log/noble-usage.json) · [Resolute fixed usage](../tests/fixtures/git-commit-log/resolute-usage.json)

| Literal spellings | Operand | Releases | Effect |
| --- | --- | --- | --- |
| `-a`, `--all` | none | All | Stage tracked modifications and deletions in addition to the existing index. |
| `-p`, `--patch` | none | All | Select additional hunks to commit. |
| `--interactive` | none | All | Use interactive staging before committing the resulting index. |
| `-U`, `--unified=` | LINES | Resolute/upstream | Set context around each interactive hunk. |
| `--inter-hunk-context=` | LINES | Resolute/upstream | Join nearby interactive hunks. |
| `-C`, `--reuse-message=` | COMMIT | All | Reuse a commit's message, author and author date. |
| `-c`, `--reedit-message=` | COMMIT | All | Reuse the same message and author information and open the editor. |
| `--fixup=` | TARGET | All | Prepare a content or message correction for autosquash. |
| `--squash=` | COMMIT | All | Prepare a combined-message autosquash commit. |
| `--reset-author` | none | All | Assign authorship to the committer and renew the author date. |
| `--short` | none | All | Preview in short status format. |
| `--branch` | none | All | Include branch and tracking information in status output. |
| `--porcelain` | none | All | Preview using the stable machine-readable status format. |
| `--long` | none | All | Preview using the detailed human-readable status format. |
| `-z`, `--null` | none | All | Terminate status entries with NUL and emit verbatim path names. |
| `-F`, `--file` | FILE | All | Read a commit message from a file or standard input. |
| `--author=` | AUTHOR | All | Override the author identity or select an existing author by pattern. |
| `--date=` | DATE | All | Override the author timestamp. |
| `-m`, `--message` | MESSAGE | All | Supply a message paragraph. |
| `-t`, `--template=` | FILE | All | Start the message editor with a template file. |
| `-s`, `--signoff` | none | All | Append the committer's Signed-off-by trailer. |
| `--no-signoff` | none | All | Cancel an earlier signoff. |
| `--trailer=` | TRAILER | All | Add a configured trailer to the message. |
| `-n`, `--no-verify` | none | All | Skip the pre-commit and commit-msg hooks. |
| `--verify` | none | All | Re-enable those hooks after a bypass. |
| `--allow-empty` | none | All | Permit committing the same tree as the sole parent. |
| `--allow-empty-message` | none | All | Permit an empty log message. |
| `--cleanup=` | MODE | All | Select message cleanup rules. |
| `-e`, `--edit` | none | All | Open the message editor. |
| `--no-edit` | none | All | Use the prepared message without opening the editor. |
| `--amend` | none | All | Replace the current tip commit. |
| `--no-post-rewrite` | none | All | Skip the post-rewrite hook during amendment. |
| `-i`, `--include` | none | All | Stage selected tracked paths and include previous staging. |
| `-o`, `--only` | none | All | Commit the working-tree content of selected paths and retain unrelated staging. |
| `--pathspec-from-file=` | FILE | All | Read the path selection from a file or standard input. |
| `--pathspec-file-nul` | none | All | Split the pathspec file on NUL bytes. |
| `-u`, `--untracked-files=` | optional MODE | All | Choose how untracked names appear in status. |
| `-v`, `--verbose` | none | All | Show the proposed diff in the editor. |
| `-q`, `--quiet` | none | All | Suppress the success summary. |
| `--dry-run` | none | All | Preview the selected content without creating a commit. |
| `--status` | none | All | Include status information in the editor template. |
| `--no-status` | none | All | Omit status information from the editor template. |
| `-S`, `--gpg-sign=` | optional KEY | All | Cryptographically sign the commit. |
| `--no-gpg-sign` | none | All | Disable signing for this commit. |
| `--ahead-behind` | none | All, fixed help | Compute full ahead/behind counts for upstream tracking information. |
| `--no-ahead-behind` | none | All, parser | Skip computing detailed ahead/behind counts. |
| `--post-rewrite` | none | All, parser | Restore the post-rewrite hook after a bypass. |
| `-h` | none | All, parser | Show built-in usage. |
| `--help` | none | All, Git dispatch | Open the manual for this command. |
| `--help-all` | none | All, parser | Show built-in usage including hidden option descriptions. |
| `--no-message` | none | All, parser | Clear earlier message paragraphs. |
| `--no-file` | none | All, parser | Cancel the message file selection. |
| `--no-author` | none | All, parser | Cancel the author identity override. |
| `--no-date` | none | All, parser | Cancel the author date override. |
| `--no-reuse-message` | none | All, parser | Cancel reuse of a commit message. |
| `--no-reedit-message` | none | All, parser | Cancel editing of a reused message. |
| `--no-fixup` | none | All, parser | Cancel the autosquash correction request. |
| `--no-squash` | none | All, parser | Cancel the squash title request. |
| `--no-reset-author` | none | All, parser | Cancel the authorship reset. |
| `--no-template` | none | All, parser | Clear the selected message template. |
| `--no-cleanup` | none | All, parser | Cancel the cleanup mode override. |
| `--no-all` | none | All, parser | Cancel automatic staging of tracked files. |
| `--no-include` | none | All, parser | Cancel explicit inclusion of paths. |
| `--no-interactive` | none | All, parser | Cancel interactive staging. |
| `--no-patch` | none | All, parser | Cancel interactive hunk selection. |
| `--no-only` | none | All, parser | Cancel explicit path-only selection. |
| `--no-dry-run` | none | All, parser | Cancel an explicit preview request. |
| `--no-short`, `--no-long`, `--no-porcelain` | none | All, parser | Clear the selected status format. |
| `--no-branch` | none | All, parser | Omit the optional short-status branch header. |
| `--no-null` | none | All, parser | Cancel NUL-terminated status output. |
| `--no-amend` | none | All, parser | Cancel tip replacement. |
| `--no-untracked-files` | none | All, parser | Clear the untracked display override. |
| `--no-pathspec-from-file` | none | All, parser | Cancel the pathspec input source. |
| `--no-pathspec-file-nul` | none | All, parser | Restore line-delimited pathspec input. |
| `--no-verbose` | none | All, parser | Omit the verbose editor diff. |
| `--no-quiet` | none | All, parser | Restore the commit success summary. |
| `--no-allow-empty` | none | All, parser | Restore the unchanged-tree check. |
| `--no-allow-empty-message` | none | All, parser | Restore the empty-message check. |

## Coverage and ownership

The nine original rows have 89 additions, giving 98 selectable spellings for 78 effects. Each short alias has its own row. The three status-format negations clear the same selection. Each positive toggle, negative toggle and source reset counts separately when it changes an outcome. The original separate-operand insertions for `--message` and `--file` and their Git 2.48 contracts remain intact. The original discovery specimen contains three representative declarations. Its provenance and bytes remain independent of the packaged help captures. [Discovery specimen](../tests/fixtures/help/git-commit.txt) · [Fixture provenance](../tests/fixtures/help/README.md)

- `--` separates commit options from pathspec operands. A pathspec, including a dash-prefixed name after the separator, does not define a menu option. Similarly, `amend:` and `reword:` qualify the operand of `--fixup`. A trailer token, signing key, date and cleanup mode are values. Global options such as `git --literal-pathspecs commit` precede the command. After `commit`, `-C` reuses a message and `-c` re-edits one.
- The commit parser exposes tracking-count switches and option resets in its fixed usage. `--help-all` also shows the two hidden empty-commit controls and their negations. A negated value-taking option takes no operand. The parser rejects `--no-trailer`. A top-level `git commit --help` dispatches to the manual viewer, while `-h` and `--help-all` select built-in help. [Option parser](https://raw.githubusercontent.com/git/git/v2.53.0/parse-options.c) · [Option definitions](https://raw.githubusercontent.com/git/git/v2.53.0/parse-options.h) · [Git help dispatch](https://raw.githubusercontent.com/git/git/v2.53.0/git.c)
- The commit parser requires a count with `-U`, although the upstream manual's shared diff description calls bare `-U` a patch alias. A nonnegative value for either patch context requires `--interactive` or `--patch`. The internal default sentinel is -1. Noble lacks both context options. Resolute accepts them. Both clients reject `--porcelain=v2` and `--long -z`. The `--porcelain` version selector belongs to status. The shared manual heading for `--verify` and `--no-verify` describes the bypass. Only `-n` and `--no-verify` bypass the two hooks. [Commit parser](https://raw.githubusercontent.com/git/git/v2.53.0/builtin/commit.c) · [Upstream option definitions](https://raw.githubusercontent.com/git/git/v2.56.0/parse-options.h)
- Reading pathspecs from a NUL-delimited file disables line splitting and quote decoding. Git still interprets pathspec magic. The file is incompatible with additional command-line pathspecs, interactive selection and `--all`. [Pathspec file parser](https://raw.githubusercontent.com/git/git/v2.53.0/pathspec.c)
- The release-specific `prepare_index` implementation checks whether each `--include` pathspec matched a tracked path on Resolute and upstream. Noble omits the match check. The staged snapshot can therefore enter a commit despite a mistyped name. [Noble commit selection](https://raw.githubusercontent.com/git/git/v2.43.0/builtin/commit.c) · [Resolute commit selection](https://raw.githubusercontent.com/git/git/v2.53.0/builtin/commit.c)

Common short combinations such as `-am "message"` and `-vv` remain browsable. For a cluster ending in an optional short operand, split the options when continuing to edit in the menu. For example, write `-a -uall` for Git’s `-auall`, or `-v -SKEY` for `-vSKEY`. [Insertion and argument checks](../tests/test_git_commit_inventory.py)

## Packaged observations

The commands below ran in new offline sandbox repositories with private configuration, local fixture identities and no remotes. Each row describes the observable result separately from the manuals.

| Fixture and command | Git 2.43.0 on Noble | Git 2.53.0 on Resolute |
| --- | --- | --- |
| An existing staged blob plus `git commit --include -m x -- absent` | Status 0. HEAD and the index contained the staged blob. Naming an existing untracked path produced the same result. | Status 128. Git reported an unmatched path, kept the old HEAD blob and retained the new blob in the index. The untracked-path case also returned 128. |
| Only an unstaged tracked modification, `git commit --short -uyes`, `-utrue` or `-ufalse` | All three returned 128 for an invalid mode. | All three parsed and displayed the tracked modification. Status 1 indicated that the index had no committable change. |
| `git commit --short -u all` in a repository without a path named all | Status 1 and an unmatched path error. | Status 1 and an unmatched path error. The next word is a pathspec on both releases. |
| `git commit --short -U` | Status 129, unknown switch. | Status 129, missing count. |
| `git commit --short --unified=0` and `--unified=-2` | Both returned 129, unknown option. | Both returned 128. A nonnegative override needs interactive selection and -2 is below the allowed range. |
| `git commit --short --porcelain=v2`, `--short --no-trailer`, and `--long -z` | Statuses 129, 129 and 128, respectively. | Identical statuses. The errors identify a valueless switch, an unknown negation and incompatible formats. |

The [family verification record](git-commit-log-manual-coverage.md) distinguishes the packaged behavior checks from the Bash/tmux menu runs and full suites.
