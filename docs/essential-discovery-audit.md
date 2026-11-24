# Essential discovery route inventory

Counts measure distinct selectable spellings, including short aliases. The first column of counts uses the original WSL capture where available and the installed workflow capture otherwise. The Noble and Resolute/vendor columns use the larger independently reconciled inputs. Where both distribution packages produce identical output, or a vendor release supplies the reference, the family audit identifies the exact source and version. A zero is an observed empty result. [Matrix in maintained order](../tests/fixtures/help/matrix.json) · [Fixture provenance](../tests/fixtures/help/README.md) · [Results and reproduction](essential-discovery-verification.md)

Across the 46 routes, the historical inputs account for 597 selectable rows and the complete Resolute or vendor inputs account for 3,541. These totals count each spelling once per command path. Root npm contributes zero to both totals. Its fixed sources provide usage and command names and the shell reports that it found no option declarations. An additional Noble count appears where the audit has a separate complete capture for that route. The other rows identify their Noble evidence in the family audit.

| Command | Historical | Additional Noble case | Complete Resolute or vendor case | Sources, requests and disposition |
| --- | ---: | --- | ---: | --- |
| `ffmpeg` | 4 | 174 | 176 | [media](essential-media.md) |
| `npm` | 0 | See family audit | 0 | [packages](essential-packages.md) |
| `pip` | 2 | 30 | 29 | [packages](essential-packages.md) |
| `git commit` | 4 | 58 | 61 | [git-docker](essential-git-docker.md) |
| `git log` | 4 | 211 | 212 | [git-docker](essential-git-docker.md) |
| `git diff` | 3 | 111 | 112 | [git-docker](essential-git-docker.md) |
| `curl` | 5 | See family audit | 332 | [utilities](essential-utilities.md) |
| `wget` | 6 | See family audit | 210 | [utilities](essential-utilities.md) |
| `rsync` | 4 | See family audit | 233 | [utilities](essential-utilities.md) |
| `docker run` | 5 | See family audit | 118 | [git-docker](essential-git-docker.md) |
| `docker image ls` | 5 | See family audit | 10 | [git-docker](essential-git-docker.md) |
| `docker compose up` | 5 | See family audit | 35 | [git-docker](essential-git-docker.md) |
| `pip install` | 5 | 80 | 81 | [packages](essential-packages.md) |
| `pip download` | 4 | 59 | 60 | [packages](essential-packages.md) |
| `pip3 install` | 5 | 80 | 81 | [packages](essential-packages.md) |
| `uv pip install` | 5 | See family audit | 95 | [packages](essential-packages.md) |
| `uv run` | 4 | See family audit | 96 | [packages](essential-packages.md) |
| `npm install` | 25 | See family audit | 34 | [packages](essential-packages.md) |
| `npm run` | 7 | See family audit | 9 | [packages](essential-packages.md) |
| `pnpm install` | 4 | See family audit | 60 | [packages](essential-packages.md) |
| `jq` | 7 | See family audit | 47 | [utilities](essential-utilities.md) |
| `rg` | 5 | See family audit | 189 | [utilities](essential-utilities.md) |
| `ffprobe` | 3 | 471 | 496 | [media](essential-media.md) |
| `docker compose logs` | 6 | See family audit | 12 | [git-docker](essential-git-docker.md) |
| `docker compose exec` | 10 | See family audit | 13 | [git-docker](essential-git-docker.md) |
| `git status` | 7 | 21 | 21 | [git-docker](essential-git-docker.md) |
| `git show` | 3 | 122 | 123 | [git-docker](essential-git-docker.md) |
| `git fetch` | 5 | 62 | 63 | [git-docker](essential-git-docker.md) |
| `git switch` | 6 | 25 | 25 | [git-docker](essential-git-docker.md) |
| `docker compose ps` | 11 | See family audit | 11 | [git-docker](essential-git-docker.md) |
| `docker compose config` | 22 | See family audit | 22 | [git-docker](essential-git-docker.md) |
| `docker compose build` | 16 | See family audit | 16 | [git-docker](essential-git-docker.md) |
| `docker compose pull` | 7 | See family audit | 7 | [git-docker](essential-git-docker.md) |
| `docker compose down` | 7 | See family audit | 7 | [git-docker](essential-git-docker.md) |
| `docker compose run` | 36 | See family audit | 36 | [git-docker](essential-git-docker.md) |
| `cp` | 50 | See family audit | 51 | [utilities](essential-utilities.md) |
| `mv` | 25 | See family audit | 26 | [utilities](essential-utilities.md) |
| `rm` | 17 | See family audit | 17 | [utilities](essential-utilities.md) |
| `sort` | 52 | See family audit | 53 | [utilities](essential-utilities.md) |
| `head` | 13 | See family audit | 15 | [utilities](essential-utilities.md) |
| `tail` | 21 | See family audit | 25 | [utilities](essential-utilities.md) |
| `du` | 44 | See family audit | 48 | [utilities](essential-utilities.md) |
| `df` | 28 | See family audit | 28 | [utilities](essential-utilities.md) |
| `sed` | 26 | See family audit | 26 | [utilities](essential-utilities.md) |
| `gzip` | 36 | See family audit | 40 | [utilities](essential-utilities.md) |
| `xz` | 28 | See family audit | 80 | [utilities](essential-utilities.md) |
