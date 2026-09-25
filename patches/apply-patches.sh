#!/bin/bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
repo="$root/hardware/interfaces"
patch="$root/device/xiaomi/fire/patches/hardware_interfaces/0001-sensors-drop-unsupported-moisture-intrusion.patch"

if git -C "$repo" apply --check "$patch"; then
    git -C "$repo" apply "$patch"
    echo "Applied fire sensors patch"
elif git -C "$repo" apply --reverse --check "$patch"; then
    echo "Fire sensors patch already applied"
else
    echo "ERROR: patch does not match hardware/interfaces" >&2
    exit 1
fi
