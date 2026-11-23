# Git stash and worktree direct option inventory

The declarations below cover implicit push, three explicit stash operations and all five worktree menus. Each row groups spellings with one effect on the listed paths. `N` denotes Noble Git 2.43.0, `R` Resolute Git 2.53.0 and `U` upstream Git 2.56.0. The upstream site records no manual change for 2.56.1. Ubuntu publishes the manuals in git-man 1:2.43.0-1ubuntu7.4 and 1:2.53.0-1ubuntu1.1. [Upstream stash](https://git-scm.com/docs/git-stash/2.56.0) · [Noble stash](https://manpages.ubuntu.com/manpages/noble/man1/git-stash.1.html) · [Resolute stash](https://manpages.ubuntu.com/manpages/resolute/man1/git-stash.1.html) · [Upstream worktree](https://git-scm.com/docs/git-worktree/2.56.0) · [Noble worktree](https://manpages.ubuntu.com/manpages/noble/man1/git-worktree.1.html) · [Resolute worktree](https://manpages.ubuntu.com/manpages/resolute/man1/git-worktree.1.html)

## Direct declarations

The spelling column gives the literal menu insertion (trailing separators omitted). All positive long options with a required value accept both `--option=value` and `--option value`. Short options with a required value accept both joined and separate operands. Every listed negation is a switch. Git also accepts unambiguous option abbreviations. These context-dependent prefixes do not define additional options. The `keyword` entries select a child operation. See the ownership notes below for their subsequent operands.

| Path(s) | Selectable spelling(s) | Operand | Releases |
| --- | --- | --- | --- |
| `stash`, `stash push`, `stash apply`, `stash pop`, `worktree`, `worktree add`, `worktree list`, `worktree prune`, `worktree remove` | `-h` | none | NRU |
| `stash`, `stash push` | `-p`, `--patch` | none | NRU |
| `stash`, `stash push` | `-S`, `--staged` | none | NRU |
| `stash`, `stash push` | `-k`, `--keep-index` | none | NRU |
| `stash`, `stash push` | `--no-keep-index` | none | NRU |
| `stash`, `stash push` | `-u`, `--include-untracked` | none | NRU |
| `stash`, `stash push` | `-a`, `--all` | none | NRU |
| `stash`, `stash push` | `--no-include-untracked` | none | NRU |
| `stash`, `stash push` | `-m`, `--message` | MESSAGE | NRU |
| `stash`, `stash push`, `stash apply`, `stash pop`, `worktree add` | `-q`, `--quiet` | none | NRU |
| `stash`, `stash push` | `--pathspec-from-file` | FILE | NRU |
| `stash`, `stash push` | `--pathspec-file-nul` | none | NRU |
| `stash`, `stash push` | `-U`, `--unified=` | LINES | RU |
| `stash`, `stash push` | `--inter-hunk-context=` | LINES | RU |
| `stash`, `stash push` | `--auto-advance` | none | U, parser |
| `stash`, `stash push` | `--no-auto-advance` | none | U, parser |
| `stash` | `push` | keyword | NRU |
| `stash` | `apply` | keyword | NRU |
| `stash` | `pop` | keyword | NRU |
| `stash` | `list` | keyword | NRU |
| `stash` | `show` | keyword | NRU |
| `stash` | `branch` | keyword | NRU |
| `stash` | `clear` | keyword | NRU |
| `stash` | `drop` | keyword | NRU |
| `stash` | `create` | keyword | NRU |
| `stash` | `store` | keyword | NRU |
| `stash` | `save` | keyword | NRU, deprecated |
| `stash` | `export` | keyword | RU |
| `stash` | `import` | keyword | RU |
| `stash apply`, `stash pop` | `--index` | none | NRU |
| `stash apply`, `stash pop` | `--no-index` | none | NRU, parser |
| `stash apply` | `--label-ours=` | LABEL | U |
| `stash apply` | `--label-theirs=` | LABEL | U |
| `stash apply` | `--label-base=` | LABEL | U |
| `worktree` | `add` | keyword | NRU |
| `worktree` | `list` | keyword | NRU |
| `worktree` | `remove` | keyword | NRU |
| `worktree` | `prune` | keyword | NRU |
| `worktree` | `lock` | keyword | NRU |
| `worktree` | `unlock` | keyword | NRU |
| `worktree` | `move` | keyword | NRU |
| `worktree` | `repair` | keyword | NRU |
| `worktree add`, `worktree remove` | `-f`, `--force` | none | NRU |
| `worktree add` | `-d`, `--detach` | none | NRU |
| `worktree add` | `-b` | BRANCH | NRU |
| `worktree add` | `-B` | BRANCH | NRU |
| `worktree add` | `--checkout` | none | NRU |
| `worktree add` | `--no-checkout` | none | NRU |
| `worktree add` | `--lock` | none | NRU |
| `worktree add` | `--reason` | REASON | NRU |
| `worktree add` | `--orphan` | none | NRU |
| `worktree add` | `--track` | none | NRU |
| `worktree add` | `--no-track` | none | NRU |
| `worktree add` | `--guess-remote` | none | NRU |
| `worktree add` | `--no-guess-remote` | none | NRU |
| `worktree add` | `--relative-paths` | none | RU |
| `worktree add` | `--no-relative-paths` | none | RU |
| `worktree list` | `--porcelain` | none | NRU |
| `worktree list` | `-z` | none | NRU |
| `worktree list`, `worktree prune` | `-v`, `--verbose` | none | NRU |
| `worktree list`, `worktree prune` | `--expire` | TIME | NRU |
| `worktree list`, `worktree prune` | `--no-expire` | none | NRU, parser |
| `worktree prune` | `-n`, `--dry-run` | none | NRU |

## Ownership and parser distinctions

- Implicit push takes flags at the stash root. The portable spelling for pathspecs is `git stash -- PATH...`. With explicit push the separator is optional unless a path begins with a dash. Resolute also accepts a path immediately after `-p` or `--patch`. Noble rejects both forms. Its implementation tests the first argument for `-p` after the dispatcher has prepended the word `push`. A subcommand keyword precedes its options. Dedicated children open their own profiles. Other recognized keywords describe their operands in the root Details and have no bundled child menu.
- `drop [-q] [STASH]`, `branch BRANCH [STASH]`, `clear`, `create [MESSAGE]`, `store [-q] [-m MESSAGE] COMMIT` and deprecated `save [FLAGS] [MESSAGE...]` are separate operations. Save joins remaining words into a message and takes no pathspec. Export's mutually exclusive `--print` and `--to-ref REF` belong after `export`. Import takes the export-chain tip commit and appends stashes. Git globals such as `-C` precede the operation. The pathspec separator and stash references are operand grammar.
- The tagged stash push parser requires one integer for each context option. Bare `-U` is an error here even though the common diff documentation describes it as a patch synonym. A value of -1 leaves Git's default in place. Smaller values are rejected. The upstream-only patch navigation toggle appears in the parser despite its omission from the stash options section. `--label-ours`, `--label-theirs` and `--label-base` each take one string on upstream apply. Pop has no such options. [Noble stash parser](https://raw.githubusercontent.com/git/git/v2.43.0/builtin/stash.c) · [Resolute stash parser](https://raw.githubusercontent.com/git/git/v2.53.0/builtin/stash.c) · [Upstream stash parser](https://raw.githubusercontent.com/git/git/v2.56.0/builtin/stash.c) · [Shared diff documentation](https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/diff-context-options.adoc) · [Interactive hunk navigation](https://raw.githubusercontent.com/git/git/v2.56.0/add-patch.c)
- `worktree lock [--reason STRING] WORKTREE`, `unlock WORKTREE`, `move [-f] WORKTREE NEW-PATH` and `repair [PATH...]` own their operands. Move and repair also accept relative-path controls on Resolute and upstream. A unique path suffix can identify an existing worktree. Only add and remove among the four bundled leaf profiles take force. The second force matters for locked worktrees.
- Worktree add forwards the bare tracking switch to branch creation. Its parser disallows a value even though git-branch accepts attached tracking modes. For an omitted start point, both Ubuntu parsers fall back to HEAD when remote guessing cannot select a unique match. Upstream reports unresolved ambiguity as an error. A matching `checkout.defaultRemote` can resolve the ambiguity. With an explicit branch argument, a matching local branch takes precedence. [Noble worktree parser](https://raw.githubusercontent.com/git/git/v2.43.0/builtin/worktree.c) · [Resolute worktree parser](https://raw.githubusercontent.com/git/git/v2.53.0/builtin/worktree.c) · [Upstream worktree parser](https://raw.githubusercontent.com/git/git/v2.56.0/builtin/worktree.c)
- Git's generic option parser accepts reset spellings which cancel an earlier setting. These are searchable on the owning option. Push accepts `--no-patch`, `--no-staged`, `--no-all`, `--no-message`, `--no-pathspec-from-file` and `--no-pathspec-file-nul`. All direct quiet flags accept `--no-quiet`. The upstream label switches each accept a no-value `--no-label-...` reset. Worktree add accepts `--no-detach`, `--no-orphan`, `--no-lock` and `--no-reason`. Force, verbose, porcelain and dry-run accept corresponding resets. `--no-expire` is selectable because it sets the cutoff to `never` even without a preceding option. Short-only options have no generated long names. Diff-context switches explicitly disallow negation. Completion plumbing belongs to the shell. Built-in help aliases and the root manual viewer are distinguished below. [Generic parser](https://raw.githubusercontent.com/git/git/v2.53.0/parse-options.c) · [Expiry callback](https://raw.githubusercontent.com/git/git/v2.53.0/parse-options-cb.c) · [Option declarations](https://raw.githubusercontent.com/git/git/v2.53.0/parse-options.h)

- All nine direct paths accept `--help-all` as full built-in usage. On the seven direct leaf paths `--help` also means built-in usage. At either root, Git dispatches `--help` to the manual viewer before the stash/worktree parser sees it. The `-h` Details identify these alternatives. These aliases account for 16 additional path-specific built-in usage spellings across the nine menus. The two root manual-viewer invocations are Git-wide actions. [Git dispatch](https://raw.githubusercontent.com/git/git/v2.53.0/git.c) · [Built-in help parser](https://raw.githubusercontent.com/git/git/v2.53.0/parse-options.c)

## Counts

A path-specific effect groups equivalent aliases, such as `-q` and `--quiet`. Positive and negative selections with different outcomes count separately. Parser-generated resets documented in Details add searchable spellings without duplicating the row. The first-pass spellings remain individually selectable.

| Path | Original rows | Added rows | Final rows | Distinct selectable effects | Additional reset spellings in Details |
| --- | ---: | ---: | ---: | ---: | ---: |
| Stash root | 17 | 20 | 37 | 29 | 7 |
| Stash push | 17 | 7 | 24 | 16 | 7 |
| Stash apply | 3 | 5 | 8 | 7 | 4 |
| Stash pop | 3 | 2 | 5 | 4 | 1 |
| Worktree root | 5 | 4 | 9 | 9 | 0 |
| Worktree add | 11 | 9 | 20 | 17 | 6 |
| Worktree list | 4 | 3 | 7 | 6 | 2 |
| Worktree prune | 5 | 2 | 7 | 5 | 2 |
| Worktree remove | 2 | 1 | 3 | 2 | 1 |
| Total | 67 | 53 | 120 | 95 | 30 |

## Packaged Git observations

The [direct fixture regression](../tests/test_git_stash_worktree_packaged.py) runs Git in newly initialized repositories with private configuration, local fixture identities, empty templates, disabled hooks and no remotes. The observations below come from the Ubuntu packages. The separate terminal evidence concerns the help menu.

| Check | Observable result |
| --- | --- |
| Patch context | Git 2.43 rejected context switches with status 129. Git 2.53 rejected missing values with 129 and positive context without patch mode with 128. Both the attached and separate forms of one line of context displayed and saved the chosen interior change. At zero context the same client displayed the hunk, then returned 1 with a patch application error when the hunk was selected. A value of -1 preserved normal noninteractive push. |
| Implicit push | Both clients refused a bare `git stash tracked`. With `-- tracked`, both saved the selected modification. Git 2.43 rejected implicit `-p tracked` and `--patch tracked` with 128. Git 2.53 accepted both. Following `-u` with `--no-include-untracked` left the loose file in place. |
| Index restoration and conflicts | With `stash.index=true`, applying a staged edit restored the staging state on 2.53. On 2.43 the same setting left it unstaged. Explicit `--no-index` left it unstaged on both. A conflicting pop returned 1, left unmerged index stages and retained the saved object as the tip of refs/stash. Both clients rejected all three conflict-label options on apply and pop with 129. |
| Export and import | Git 2.43 rejected both operations. On 2.53, exporting one saved entry via `--print` and via `--to-ref` produced the same chain tip. Importing that chain after clearing the fixture stash restored the original object ID. |
| Worktree tracking and relative links | Both clients rejected `--track=direct` and `--track=inherit` with 129. Bare `--track -b topic PATH main` set the upstream merge ref to refs/heads/main. Explicit orphan creation produced an empty index and unborn HEAD. On 2.53, `--relative-paths` wrote a relative gitdir target and enabled extensions.relativeWorktrees. The absolute override produced an absolute target even with relative paths configured. Git 2.43 rejected the relative switch with 129. |
| Expiry and locks | List annotated a missing path as prunable without deleting the registration. `--no-expire` suppressed the annotation and prevented prune from removing it. Prune with `--expire now` removed it. Porcelain with -z ended every attribute with NUL and separated worktrees with a second NUL. Removing a locked fixture failed with one force and succeeded with two. |
| File selection | Both packages kept an indexed edit ready to commit under `--keep-index -u`, stored it in the stash index parent and preserved an ignored file. `--all --no-keep-index` saved and removed the ignored file and rolled back the index. A NUL-terminated filename containing a newline selected only that file, leaving an unrelated edit in place. A subsequent staged-only save also preserved that unrelated edit. |
| Branch creation and reset | On both packages, `add -b topic PATH` refused an existing branch and preserved its old object ID. `add -B topic PATH` reset it to the current HEAD and checked out that same commit in the linked worktree. |
| Help ownership | With the helper search path empty, both root `--help` invocations returned 128 and diagnosed an unavailable manual viewer. Root `--help-all` and all nine leaf `--help` and `--help-all` invocations matched their release-specific `-h` capture byte for byte on stdout, with status 129 and empty stderr. |
