# ansible-playbook manual coverage

The [bundled playbook menu](../profiles/ansible-playbook.json) contains 61 selectable spellings for 38 effects. The original 21 rows retain their order and literal insertions. The 40 added rows include the remaining aliases, connection options, credential sources, execution controls and help switches. Each of the 23 alias spellings beyond the first spelling per effect has its own row.

## Sources and inventory

| Reference | Release and use |
| --- | --- |
| [Upstream CLI manual](https://docs.ansible.com/projects/ansible/latest/cli/ansible-playbook.html) and [release parser](https://github.com/ansible/ansible/blob/v2.22.0/lib/ansible/cli/playbook.py) | The playbook parser selects its own sets of [shared option declarations](https://github.com/ansible/ansible/blob/v2.22.0/lib/ansible/cli/arguments/option_helpers.py). Installed ansible-core 2.22.0 fixed help provides argument counts for the exact command. |
| [Ubuntu 24.04 ansible-playbook(1)](https://manpages.ubuntu.com/manpages/noble/man1/ansible-playbook.1.html) | ansible-core 2.16.3-0ubuntu2. Matched the option headings and synopsis against the [2.16.3 declarations](https://github.com/ansible/ansible/blob/v2.16.3/lib/ansible/cli/arguments/option_helpers.py). |
| [Ubuntu 26.04 ansible-playbook(1)](https://manpages.ubuntu.com/manpages/resolute/man1/ansible-playbook.1.html) | ansible-core 2.20.1-1. Matched the option headings and synopsis against the [2.20.1 declarations](https://github.com/ansible/ansible/blob/v2.20.1/lib/ansible/cli/arguments/option_helpers.py). |
| [Historical native help](../tests/fixtures/help/followup-systems/ansible-playbook.txt) and [capture manifest](../tests/fixtures/help/followup-systems/manifest.json) | ansible-core 2.21.5 on Ubuntu 24.04 under WSL. The original [short specimen](../tests/fixtures/help/ansible-playbook.txt) is a documentation excerpt. |

The [inventory](../tests/fixtures/operations-manual/ansible-playbook.txt) groups aliases by effect and records required operand counts. It was derived from installed fixed help and matched to both Ubuntu manuals before comparison with the profile. Several Ubuntu option headings omit the operand placeholder, including the inventory and Vault password file headings. The synopsis and parser require an operand in each case. All three reviewed releases have the same spelling set. Noble describes the deprecation of `--inventory-file` in the manual. The newer parser still accepts it and directs users to `-i` or `--inventory`.

One or more playbook paths are positional inputs. The menu accepts options around playbook paths and preserves quoting. Play keywords, configuration keys, host pattern operators, Vault identity syntax and options belonging only to other Ansible commands are outside the selectable option inventory.

## Original rows and material changes

| Original spellings | Disposition and resulting guidance |
| --- | --- |
| `-i`, `--inventory` | Incomplete. Repeat for multiple sources. A non-path inline host list needs a comma, including the trailing comma for a single host. The inventory plugin interprets the source. [host_list implementation](https://github.com/ansible/ansible/blob/v2.22.0/lib/ansible/plugins/inventory/host_list.py) |
| `-l`, `--limit` | Incomplete. Apply a pattern to the play's existing host selection. Quote shell metacharacters or supply `@file`. The existing detailed subscript grammar remains searchable. [Inventory pattern evaluation](https://github.com/ansible/ansible/blob/v2.22.0/lib/ansible/inventory/manager.py) |
| `-e`, `--extra-vars` | Incomplete. Repeat key/value strings or pass a JSON/YAML mapping or `@file`. The mapping form preserves typed values. [Variables guide](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_variables.html) |
| `-C`, `--check`; `-D`, `--diff` | Inaccurate blanket prediction and incomplete diff guidance. Modules must support each mode. A task with `check_mode: false` can still make changes under `--check`. Diff alone applies tasks and can show sensitive content. [Check and diff modes](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_checkmode.html) |
| `--tags`, `--skip-tags` | Incomplete. Tag lists accept commas and repeated options. The `always` tag and an explicit skip affect selection. [Tag selection](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_tags.html) |
| `--list-hosts`, `--list-tasks`, `--syntax-check` | Incomplete. Match hosts, enumerate known tasks or validate what loads at parse time, respectively. Listing omits tasks that a dynamic include only reveals at runtime. [Static and dynamic reuse](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_reuse.html) |
| `--user`, `--private-key`, `--become`, `--become-user` | Summaries sufficient, Details incomplete. Distinguish the connection identity, controller-side key, escalation switch and target user. Selecting a target user or password prompt alone does not enable escalation. [Privilege escalation guide](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_privilege_escalation.html) |
| `--forks` | Redundant numeric detail in the original summary. Retain the built-in five-process default and the minimum of one in Details and the structured contract. |
| `--vault-password-file` | Incomplete. Accepts a file or an executable password script and can repeat. The Vault password, connection password and become password have separate sources and prompts. [Vault password sources](https://docs.ansible.com/projects/ansible/latest/vault_guide/vault_managing_passwords.html) |

The new rows also distinguish restarting at a named task, prompting before individual tasks, forcing notified handlers after failure, and clearing facts for inventory hosts before limiting the play. The SSH argument options each identify which of the three subprocesses receives the string. [Playbook flags and their scope](https://docs.ansible.com/projects/ansible/latest/cli/ansible-playbook.html)

## Verification

A disposable environment with networking disabled and a private home ran `ansible-playbook --help` from ansible-core 2.22.0. A separate parser-only check accepted two inventory sources, `--check` and two playbook paths in order. No playbook was executed. The [focused tests](../tests/test_operations_manual_inventories.py) compare the independently recorded spelling and arity of every option with the bundled menu and the historical native capture. The [combined verification report](remaining-bundled-verification.md) records the rendered checks and full offline suites.
