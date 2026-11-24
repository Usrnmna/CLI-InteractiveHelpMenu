# Extended discovery audit

The [discovery matrix](../tests/fixtures/help/matrix.json) lists 51 Extended paths, beginning with `vlc`. Their own fixed documentation supplies 3,711 selectable spellings across the editions below. Each row counts a literal option spelling or selectable keyword once per route. An alias can have a different operand requirement from its long form. The linked source notes reconcile individual spellings, operand counts, scope and release differences.

The source edition identifies the reply served to discovery. The [combined terminal verification](next-extended-discovery-verification.md) identifies the Ubuntu and Python versions that displayed it. [Historical fixture provenance](../tests/fixtures/help/README.md) distinguishes complete captures, excerpts and synthetic format examples.

| Path in matrix order | Fixed documentation and identity requests | Source edition | Expected and observed spellings | Menu disposition | Source notes |
| --- | --- | --- | ---: | --- | --- |
| `vlc` | `vlc --help` · `man vlc` | 3.0.23-1 | 239 | Selectable | [Media and utilities](discovery-media-utilities.md) |
| `rclone copy` | `rclone copy --help` | 1.60.1+dfsg-4ubuntu3.2 | 3 | Selectable | [Media and utilities](discovery-media-utilities.md) |
| `restic backup` | `restic backup --help` | 0.18.1-3ubuntu1 | 65 | Selectable | [Media and utilities](discovery-media-utilities.md) |
| `borg create` | `borg help create` | 1.4.4-3 | 75 | Selectable | [Media and utilities](discovery-media-utilities.md) |
| `7z` | `7z -h` | 26.00+dfsg-1 | 26 | Selectable | [Media and utilities](discovery-media-utilities.md) |
| `7zz` | `7zz -h` | 26.00+dfsg-1 | 26 | Selectable | [Media and utilities](discovery-media-utilities.md) |
| `magick` | `magick -help` | 8:7.1.2.18+dfsg1-1 | 259 | Selectable | [Media and utilities](discovery-media-utilities.md) |
| `convert` | `convert -help` | 8:7.1.2.18+dfsg1-1 | 260 | Selectable | [Media and utilities](discovery-media-utilities.md) |
| `yt-dlp` | `yt-dlp --help` · `man yt-dlp` | 2026.03.17-1 | 360 | Selectable | [Media and utilities](discovery-media-utilities.md) |
| `rclone` | `rclone help flags` | 1.60.1+dfsg-4ubuntu3.2 | 654 | Selectable | [Media and utilities](discovery-media-utilities.md) |
| `rclone sync` | `rclone sync --help` | 1.60.1+dfsg-4ubuntu3.2 | 3 | Selectable | [Media and utilities](discovery-media-utilities.md) |
| `systemctl status` | `systemctl --help` · `man systemctl` | systemd 255 (255.4-1ubuntu8.18) | 33 | Selectable | [System tools](discovery-extended-tools.md) |
| `systemctl list-units` | `systemctl --help` · `man systemctl` | systemd 255 (255.4-1ubuntu8.18) | 34 | Selectable | [System tools](discovery-extended-tools.md) |
| `systemctl show` | `systemctl --help` · `man systemctl` | systemd 255 (255.4-1ubuntu8.18) | 37 | Selectable | [System tools](discovery-extended-tools.md) |
| `journalctl` | `journalctl --help` · `man journalctl` | systemd 255 (255.4-1ubuntu8.18) | 88 | Selectable | [System tools](discovery-extended-tools.md) |
| `ssh` | `man ssh` | OpenSSH_9.6p1 Ubuntu-3ubuntu13.20, OpenSSL 3.0.13 30 Jan 2024 | 45 | Selectable | [System tools](discovery-extended-tools.md) |
| `scp` | `man scp` | OpenSSH_9.6p1 Ubuntu-3ubuntu13.20, OpenSSL 3.0.13 30 Jan 2024 | 23 | Selectable | [System tools](discovery-extended-tools.md) |
| `sftp` | `man sftp` | OpenSSH_9.6p1 Ubuntu-3ubuntu13.20, OpenSSL 3.0.13 30 Jan 2024 | 25 | Selectable | [System tools](discovery-extended-tools.md) |
| `ip address` | `ip address help` · `man ip-address` | ip utility, iproute2-6.1.0, libbpf 1.3.0 | 8 | Selectable | [System tools](discovery-extended-tools.md) |
| `ip link` | `ip link help` · `man ip-link` | ip utility, iproute2-6.1.0, libbpf 1.3.0 | 0 | Usage-only diagnostic | [System tools](discovery-extended-tools.md) |
| `ip route` | `ip route help` · `man ip-route` | ip utility, iproute2-6.1.0, libbpf 1.3.0 | 0 | Usage-only diagnostic | [System tools](discovery-extended-tools.md) |
| `ss` | `ss --help` · `man ss` | ip utility, iproute2-6.1.0, libbpf 1.3.0 | 78 | Selectable | [System tools](discovery-extended-tools.md) |
| `openssl s_client` | `openssl s_client -help` · `man openssl-s_client` | OpenSSL 3.0.13 30 Jan 2024 (Library: OpenSSL 3.0.13 30 Jan 2024) | 181 | Selectable | [System tools](discovery-extended-tools.md) |
| `openssl x509` | `openssl x509 -help` · `man openssl-x509` | OpenSSL 3.0.13 30 Jan 2024 (Library: OpenSSL 3.0.13 30 Jan 2024) | 73 | Selectable | [System tools](discovery-extended-tools.md) |
| `openssl dgst` | `openssl dgst -help` · `man openssl-dgst` | OpenSSL 3.0.13 30 Jan 2024 (Library: OpenSSL 3.0.13 30 Jan 2024) | 28 | Selectable | [System tools](discovery-extended-tools.md) |
| `podman run` | `podman run --help` · `man podman-run` | podman version 4.9.3 | 156 | Selectable | [System tools](discovery-extended-tools.md) |
| `podman build` | `podman build --help` · `man podman-build` | podman version 4.9.3 | 106 | Selectable | [System tools](discovery-extended-tools.md) |
| `podman exec` | `podman exec --help` · `man podman-exec` | podman version 4.9.3 | 18 | Selectable | [System tools](discovery-extended-tools.md) |
| `podman logs` | `podman logs --help` · `man podman-logs` | podman version 4.9.3 | 12 | Selectable | [System tools](discovery-extended-tools.md) |
| `psql` | `psql --help` · `man psql` | psql (PostgreSQL) 16.15 (Ubuntu 16.15-0ubuntu0.24.04.1) | 69 | Selectable | [System tools](discovery-extended-tools.md) |
| `yq eval` | `yq --version` · `yq eval --help` | yq (https://github.com/mikefarah/yq/) version v4.54.1 | 64 | Selectable | [System tools](discovery-extended-tools.md) |
| `fd` | `fd --help` | fdfind 9.0.0 | 82 | Selectable | [System tools](discovery-extended-tools.md) |
| `fdfind` | `fdfind --help` · `man fdfind` | fdfind 9.0.0 | 84 | Selectable | [System tools](discovery-extended-tools.md) |
| `fzf` | `fzf --help` · `man fzf` | 0.44.1 (debian) | 81 | Selectable | [System tools](discovery-extended-tools.md) |
| `ansible-playbook` | `ansible-playbook --help` · `man ansible-playbook` | ansible-core 2.22.0 help; Ubuntu 2.20.1-1 manual | 61 | Selectable | [Cloud and embedded](discovery-cloud-tools.md) |
| `az account show` | `az account show --help` | azure-cli                         2.91.0 | 12 | Selectable | [Cloud and embedded](discovery-cloud-tools.md) |
| `az vm list` | `az vm list --help` | azure-cli                         2.91.0 | 14 | Selectable | [Cloud and embedded](discovery-cloud-tools.md) |
| `az storage blob list` | `az storage blob list --help` | azure-cli                         2.91.0 | 24 | Selectable | [Cloud and embedded](discovery-cloud-tools.md) |
| `gcloud config list` | `gcloud config list --help` | Google Cloud SDK 590.0.1 | 19 | Selectable | [Cloud and embedded](discovery-cloud-tools.md) |
| `gcloud compute instances list` | `gcloud compute instances list --help` | Google Cloud SDK 590.0.1 | 23 | Selectable | [Cloud and embedded](discovery-cloud-tools.md) |
| `gcloud storage ls` | `gcloud storage ls --help` | Google Cloud SDK 590.0.1 | 40 | Selectable | [Cloud and embedded](discovery-cloud-tools.md) |
| `pio run` | `pio run --help` | PlatformIO Core 6.2.0 | 24 | Selectable | [Cloud and embedded](discovery-cloud-tools.md) |
| `pio device monitor` | `pio device monitor --help` | PlatformIO Core 6.2.0 | 25 | Selectable | [Cloud and embedded](discovery-cloud-tools.md) |
| `platformio run` | `platformio run --help` | PlatformIO Core 6.2.0 | 24 | Selectable | [Cloud and embedded](discovery-cloud-tools.md) |
| `platformio device monitor` | `platformio device monitor --help` | PlatformIO Core 6.2.0 | 25 | Selectable | [Cloud and embedded](discovery-cloud-tools.md) |
| `esptool write-flash` | `esptool --help` · `esptool write-flash --help` | esptool 5.6.0 | 26 | Selectable | [Cloud and embedded](discovery-cloud-tools.md) |
| `esptool.py write_flash` | `esptool.py --help` · `esptool.py write_flash --help` | esptool 4.12.0 | 23 | Selectable | [Cloud and embedded](discovery-cloud-tools.md) |
| `arduino-cli compile` | `arduino-cli compile --help` | arduino-cli  Version: 1.5.1 Commit: 01f3d4f2b Date: 2026-06-05T10:22:17Z | 50 | Selectable | [Cloud and embedded](discovery-cloud-tools.md) |
| `esptool.py write-flash` | `esptool.py --help` · `esptool.py write-flash --help` | esptool 5.6.0 | 26 | Selectable | [Cloud and embedded](discovery-cloud-tools.md) |
| `7z x` | Root only · `7z -h` | 26.00+dfsg-1 | 0 | Direct discovery rejected. Cached `7z` displays 26 root spellings. | [Media and utilities](discovery-media-utilities.md) |
| `7zz x` | Root only · `7zz -h` | 26.00+dfsg-1 | 0 | Direct discovery rejected. Cached `7zz` displays 26 root spellings. | [Media and utilities](discovery-media-utilities.md) |

## Interpretation

Of the 51 paths, 47 supply their own selectable rows. The `ip link` and `ip route` requests provide usage grammar and no standalone selectable declarations. Direct discovery for `7z x` and `7zz x` is disabled by the existing route policy. With both profile sources empty, those lines can browse their respective root documentation. These two checks add 52 root row visits beyond the tier’s own spellings. [System sources and alternate editions](discovery-extended-tools.md) · [Media and archive request boundaries](discovery-media-utilities.md)
