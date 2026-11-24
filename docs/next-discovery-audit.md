# Next discovery audit

The [discovery matrix](../tests/fixtures/help/matrix.json) lists 65 Next paths, beginning with `gcc`. Their own fixed documentation supplies 3,399 selectable spellings across the editions below. Each row counts a literal option spelling or selectable keyword once per route. An alias can have a different operand requirement from its long form. The linked source notes reconcile individual spellings, operand counts, scope and release differences.

The source edition identifies the reply served to discovery. The [combined terminal verification](next-extended-discovery-verification.md) identifies the Ubuntu and Python versions that displayed it. [Historical fixture provenance](../tests/fixtures/help/README.md) distinguishes complete captures, excerpts and synthetic format examples.

| Path in matrix order | Fixed documentation and identity requests | Source edition | Expected and observed spellings | Menu disposition | Source notes |
| --- | --- | --- | ---: | --- | --- |
| `gcc` | `gcc --help` · `man gcc` | Ubuntu GCC 15.2.0-16ubuntu1 | 37 | Selectable | [Developer tools](discovery-next-tools.md) |
| `gh pr list` | `gh help pr list` | 2.46.0-4 | 29 | Selectable | [Cloud and embedded](discovery-cloud-tools.md) |
| `gh repo clone` | `gh help repo clone` | 2.46.0-4 | 3 | Selectable | [Cloud and embedded](discovery-cloud-tools.md) |
| `kubectl get` | `kubectl help get` | v1.35.10 | 31 | Selectable | [Cloud and embedded](discovery-cloud-tools.md) |
| `kubectl config view` | `kubectl help config view` | v1.35.10 | 9 | Selectable | [Cloud and embedded](discovery-cloud-tools.md) |
| `helm install` | `helm help install` | v4.3.1 | 72 | Selectable | [Cloud and embedded](discovery-cloud-tools.md) |
| `aws s3 cp` | `aws s3 cp help` | AWS CLI 1.46.1 | 52 | Selectable | [Cloud and embedded](discovery-cloud-tools.md) |
| `aws ec2 describe-instances` | `aws ec2 describe-instances help` | AWS CLI 1.46.1 | 26 | Selectable | [Cloud and embedded](discovery-cloud-tools.md) |
| `terraform plan` | `terraform plan -help` | v1.16.6 | 17 | Selectable | [Cloud and embedded](discovery-cloud-tools.md) |
| `terraform apply` | `terraform apply -help` | v1.16.6 | 14 | Selectable | [Cloud and embedded](discovery-cloud-tools.md) |
| `tofu plan` | `tofu plan -help` | v1.13.1 | 27 | Selectable | [Cloud and embedded](discovery-cloud-tools.md) |
| `tofu apply` | `tofu apply -help` | v1.13.1 | 26 | Selectable | [Cloud and embedded](discovery-cloud-tools.md) |
| `cargo build` | `cargo build --help` | Ubuntu cargo-1.93 1.93.1+dfsg-0ubuntu6 | 47 | Selectable | [Developer tools](discovery-next-tools.md) |
| `cmake` | `cmake --help` · `man cmake` | Ubuntu CMake 4.2.3-2ubuntu2 | 88 | Selectable | [Developer tools](discovery-next-tools.md) |
| `ninja` | `ninja --help` · `man ninja` | Ubuntu ninja-build 1.13.2-1 | 13 | Selectable | [Developer tools](discovery-next-tools.md) |
| `clang` | `clang --help` · `man clang` | Ubuntu clang-21 1:21.1.8-6ubuntu1 | 1,201 | Selectable | [Developer tools](discovery-next-tools.md) |
| `gh pr view` | `gh help pr view` | 2.46.0-4 | 12 | Selectable | [Cloud and embedded](discovery-cloud-tools.md) |
| `gh pr create` | `gh help pr create` | 2.46.0-4 | 36 | Selectable | [Cloud and embedded](discovery-cloud-tools.md) |
| `cargo test` | `cargo test --help` | Ubuntu cargo-1.93 1.93.1+dfsg-0ubuntu6 | 48 | Selectable | [Developer tools](discovery-next-tools.md) |
| `kubectl describe` | `kubectl help describe` | v1.35.10 | 12 | Selectable | [Cloud and embedded](discovery-cloud-tools.md) |
| `kubectl logs` | `kubectl help logs` | v1.35.10 | 20 | Selectable | [Cloud and embedded](discovery-cloud-tools.md) |
| `helm upgrade` | `helm help upgrade` | v4.3.1 | 75 | Selectable | [Cloud and embedded](discovery-cloud-tools.md) |
| `aws s3 sync` | `aws s3 sync help` | AWS CLI 1.46.1 | 53 | Selectable | [Cloud and embedded](discovery-cloud-tools.md) |
| `pytest` | `pytest --help --noconftest` | pytest 9.0.2-4 | 112 | Selectable | [Developer tools](discovery-next-tools.md) |
| `ruff check` | `ruff check --help` | ruff 0.14.1 | 47 | Selectable | [Developer tools](discovery-next-tools.md) |
| `ruff format` | `ruff format --help` | ruff 0.14.1 | 26 | Selectable | [Developer tools](discovery-next-tools.md) |
| `uv sync` | `uv help sync` | uv 0.13.1 (x86_64-unknown-linux-gnu) | 90 | Selectable | [Developer tools](discovery-next-tools.md) |
| `uv add` | `uv help add` | uv 0.13.1 (x86_64-unknown-linux-gnu) | 92 | Selectable | [Developer tools](discovery-next-tools.md) |
| `uv lock` | `uv help lock` | uv 0.13.1 (x86_64-unknown-linux-gnu) | 64 | Selectable | [Developer tools](discovery-next-tools.md) |
| `uv venv` | `uv help venv` | uv 0.13.1 (x86_64-unknown-linux-gnu) | 47 | Selectable | [Developer tools](discovery-next-tools.md) |
| `uv tool install` | `uv help tool install` | uv 0.13.1 (x86_64-unknown-linux-gnu) | 80 | Selectable | [Developer tools](discovery-next-tools.md) |
| `go build` | `go help build` | go version go1.27.3 linux/amd64 | 33 | Selectable | [Developer tools](discovery-next-tools.md) |
| `go test` | `go help test` | go version go1.27.3 linux/amd64 | 5 | Selectable | [Developer tools](discovery-next-tools.md) |
| `go run` | `go help run` | go version go1.27.3 linux/amd64 | 1 | Selectable | [Developer tools](discovery-next-tools.md) |
| `go mod tidy` | `go help mod tidy` | go version go1.27.3 linux/amd64 | 6 | Selectable | [Developer tools](discovery-next-tools.md) |
| `dotnet build` | `dotnet build --help` | 10.0.402 | 29 | Selectable | [Developer tools](discovery-next-tools.md) |
| `dotnet test` | `dotnet test --help` | 10.0.402 | 43 | Selectable | [Developer tools](discovery-next-tools.md) |
| `dotnet run` | `dotnet run --help` | 10.0.402 | 31 | Selectable | [Developer tools](discovery-next-tools.md) |
| `dotnet publish` | `dotnet publish --help` | 10.0.402 | 29 | Selectable | [Developer tools](discovery-next-tools.md) |
| `dotnet restore` | `dotnet restore --help` | 10.0.402 | 30 | Selectable | [Developer tools](discovery-next-tools.md) |
| `yarn install` | `yarn --version` · `yarn install --help` | 4.9.4 | 8 | Selectable | [Developer tools](discovery-next-tools.md) |
| `yarn add` | `yarn --version` · `yarn add --help` | 4.9.4 | 20 | Selectable | [Developer tools](discovery-next-tools.md) |
| `yarn run` | `yarn --version` · `yarn run -h=1` | 4.9.4 | 7 | Selectable | [Developer tools](discovery-next-tools.md) |
| `bun run` | `bun run --help` | 1.4.4 | 109 | Selectable | [Developer tools](discovery-next-tools.md) |
| `git stash` | `man git-stash` | git version 2.43.0 | 29 | Selectable | [Developer tools](discovery-next-tools.md) |
| `git stash push` | `man git-stash` | git version 2.43.0 | 18 | Selectable | [Developer tools](discovery-next-tools.md) |
| `git stash pop` | `man git-stash` | git version 2.43.0 | 3 | Selectable | [Developer tools](discovery-next-tools.md) |
| `git stash apply` | `man git-stash` | git version 2.43.0 | 3 | Selectable | [Developer tools](discovery-next-tools.md) |
| `git stash list` | `man git-log` | git version 2.43.0 | 185 | Selectable | [Developer tools](discovery-next-tools.md) |
| `git stash show` | `man git-diff` | git version 2.43.0 | 99 | Selectable | [Developer tools](discovery-next-tools.md) |
| `git worktree` | `man git-worktree` | git version 2.43.0 | 8 | Selectable | [Developer tools](discovery-next-tools.md) |
| `git worktree add` | `man git-worktree` | git version 2.43.0 | 17 | Selectable | [Developer tools](discovery-next-tools.md) |
| `git worktree list` | `man git-worktree` | git version 2.43.0 | 5 | Selectable | [Developer tools](discovery-next-tools.md) |
| `git worktree remove` | `man git-worktree` | git version 2.43.0 | 2 | Selectable | [Developer tools](discovery-next-tools.md) |
| `git worktree prune` | `man git-worktree` | git version 2.43.0 | 5 | Selectable | [Developer tools](discovery-next-tools.md) |
| `kubectl apply` | `kubectl help apply` | v1.35.10 | 29 | Selectable | [Cloud and embedded](discovery-cloud-tools.md) |
| `kubectl delete` | `kubectl help delete` | v1.35.10 | 25 | Selectable | [Cloud and embedded](discovery-cloud-tools.md) |
| `kubectl exec` | `kubectl help exec` | v1.35.10 | 11 | Selectable | [Cloud and embedded](discovery-cloud-tools.md) |
| `kubectl port-forward` | `kubectl help port-forward` | v1.35.10 | 2 | Selectable | [Cloud and embedded](discovery-cloud-tools.md) |
| `gh issue list` | `gh help issue list` | 2.46.0-4 | 26 | Selectable | [Cloud and embedded](discovery-cloud-tools.md) |
| `gh issue view` | `gh help issue view` | 2.46.0-4 | 12 | Selectable | [Cloud and embedded](discovery-cloud-tools.md) |
| `gh run list` | `gh help run list` | 2.46.0-4 | 23 | Selectable | [Cloud and embedded](discovery-cloud-tools.md) |
| `gh run view` | `gh help run view` | 2.46.0-4 | 19 | Selectable | [Cloud and embedded](discovery-cloud-tools.md) |
| `gh workflow list` | `gh help workflow list` | 2.46.0-4 | 12 | Selectable | [Cloud and embedded](discovery-cloud-tools.md) |
| `gh workflow view` | `gh help workflow view` | 2.46.0-4 | 9 | Selectable | [Cloud and embedded](discovery-cloud-tools.md) |

## Interpretation

All 65 routes supply selectable rows. GCC retains its 37 fixed-help spellings when its formatted manual exceeds the existing per-request byte limit. CMake and Ninja stop at their child-mode selectors. Git applies each manual section to the requested stash or worktree operation. The AWS S3 check covers both bracketed synopsis and definition text. [Developer sources and exclusions](discovery-next-tools.md) · [Cloud sources and editions](discovery-cloud-tools.md)
