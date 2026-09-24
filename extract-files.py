#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils python3
#
# SPDX-FileCopyrightText: 2026 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

from extract_utils.file import File
from extract_utils.fixups_blob import (
    BlobFixupCtx,
    blob_fixup,
    blob_fixups_user_type,
)
from extract_utils.fixups_lib import (
    lib_fixup_remove,
    lib_fixups,
    lib_fixups_user_type,
)
from extract_utils.main import (
    ExtractUtils,
    ExtractUtilsModule,
)
from extract_utils.tools import (
    llvm_objdump_path,
)
from extract_utils.utils import (
    run_cmd,
)

from pathlib import Path
import sys


def prune_manifest(manifest: Path, source: Path) -> None:
    """Keep only blob entries that physically exist in the supplied dump."""
    original = manifest.read_text().splitlines(keepends=True)
    kept: list[str] = []
    removed = 0

    for line in original:
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            kept.append(line)
            continue

        # The source path is before an optional destination (:) or attributes (;).
        source_path = (
            stripped.lstrip('-')
            .split(';', 1)[0]
            .split('|', 1)[0]
            .split(':', 1)[0]
        )
        if (source / source_path).exists():
            kept.append(line)
        else:
            removed += 1

    manifest.write_text(''.join(kept))
    print(f'Pruned {removed} missing entries from {manifest}')


def prune_manifests_from_args() -> None:
    if '--prune' not in sys.argv:
        return

    sys.argv.remove('--prune')
    source_arg = next((arg for arg in reversed(sys.argv[1:]) if not arg.startswith('-')), None)
    if source_arg is None:
        raise SystemExit('--prune requires a dump directory')

    source = Path(source_arg)
    if not source.is_dir():
        raise SystemExit(f'Not a dump directory: {source}')

    device_dir = Path(__file__).resolve().parent
    for manifest_name in ('proprietary-files.txt', 'proprietary-firmware.txt'):
        prune_manifest(device_dir / manifest_name, source)

def patch_pq_blob() -> None:
    """Apply the known HOS2 PQ crash workaround after extraction."""
    blob = (
        Path(__file__).resolve().parents[3]
        / 'vendor/xiaomi/fire/proprietary/vendor/lib64/hw'
        / 'vendor.mediatek.hardware.pq_aidl-impl.so'
    )
    if not blob.exists():
        print(f'PQ blob not extracted: {blob}')
        return

    offset = 359648
    raw = bytes.fromhex('ff 83 06 d1 e8 9b 00 fd')
    patched = bytes.fromhex('00 00 80 52 c0 03 5f d6')

    data = bytearray(blob.read_bytes())
    actual = bytes(data[offset:offset + len(raw)])

    if actual == raw:
        data[offset:offset + len(patched)] = patched
        blob.write_bytes(data)
        print('Applied PQ HAL crash workaround')
    elif actual == patched:
        print('PQ HAL crash workaround already applied')
    else:
        raise RuntimeError(
            f'Unexpected PQ bytes at {offset}: {actual.hex(" ")}'
        )


namespace_imports = [
	'device/xiaomi/fire',
	'hardware/mediatek',
	'hardware/xiaomi',
    'hardware/mediatek/libmtkperf_client',
]

def lib_fixup_vendor_suffix(lib: str, partition: str, *args, **kwargs):
    return f'{lib}_{partition}' if partition == 'vendor' else None

lib_fixups: lib_fixups_user_type = {
    **lib_fixups
}

blob_fixups: blob_fixups_user_type = {
    ('vendor/lib64/libaalservice.so', 'vendor/lib64/libcam.utils.sensorprovider.so'): blob_fixup()
        .replace_needed('libsensorndkbridge.so', 'android.hardware.sensors@1.0-convert-shared.so'),

    ('vendor/bin/mnld'): blob_fixup()
        .replace_needed('libsensorndkbridge.so', 'android.hardware.sensors@1.0-convert-shared.so'),

    (
        'vendor/lib/egl/libGLES_mali.so',
        'vendor/lib64/egl/libGLES_mali.so',
        'vendor/lib/hw/android.hardware.graphics.allocator-V2-mediatek.so',
        'vendor/lib64/hw/android.hardware.graphics.allocator-V2-mediatek.so',
        'vendor/lib/hw/mapper.mediatek.so',
        'vendor/lib64/hw/mapper.mediatek.so',
        'vendor/lib/libcodec2_fsr.so',
        'vendor/lib64/libcodec2_fsr.so',
        'vendor/lib/libgpud.so',
        'vendor/lib64/libgpud.so',
        'vendor/lib/libmtkcam_grallocutils.so',
        'vendor/lib64/libmtkcam_grallocutils.so',
        'vendor/lib/vendor.mediatek.hardware.pq_aidl-V2-ndk.so',
        'vendor/lib64/vendor.mediatek.hardware.pq_aidl-V2-ndk.so',
        'vendor/lib/vendor.mediatek.hardware.pq_aidl-V4-ndk.so',
        'vendor/lib64/vendor.mediatek.hardware.pq_aidl-V4-ndk.so',
        'vendor/lib64/libaimemc.so',
        'vendor/lib64/vendor.mediatek.hardware.camera.isphal-V1-ndk.so',
        'vendor/bin/hw/android.hardware.graphics.allocator-V2-service-mediatek'
    ): blob_fixup()
        .replace_needed('android.hardware.graphics.common-V5-ndk.so', 'android.hardware.graphics.common-V7-ndk.so'),

    # HOS2 PQ crashes in loadPqparamTable(), stalling HWC/SF at ~2 FPS.
    ('vendor/lib64/hw/vendor.mediatek.hardware.pq_aidl-impl.so'): blob_fixup()
        .binary_regex_replace(
            b'\xff\x83\x06\xd1\xe8\x9b\x00\xfd',
            b'\x00\x00\x80\x52\xc0\x03\x5f\xd6',
        ),

    ('vendor/bin/hw/android.hardware.audio.service-aidl.mediatek'): blob_fixup()
        .replace_needed('libaudio_aidl_conversion_common_ndk.so', 'libaudio_aidl_conversion_common_ndk_prebuilt.so'),
    
    (
        'vendor/lib/hw/audio.primary.mt6768.so',
        'vendor/lib64/hw/audio.primary.mt6768.so',
    ): blob_fixup()
        .replace_needed('libxml2.so', 'libxml2-vendor.so'),

    ('vendor/lib/hw/android.hardware.audio.effect.aidl-impl-mediatek.so', 'vendor/lib64/hw/android.hardware.audio.effect.aidl-impl-mediatek.so'): blob_fixup()
        .replace_needed('android.media.audio.common.types-V5-ndk.so', 'android.media.audio.common.types-V3-ndk.so')
        .replace_needed('libxml2.so', 'libxml2-vendor.so'),
    
    ('vendor/lib/android.hardware.audio.core-impl-mediatek.so', 'vendor/lib64/android.hardware.audio.core-impl-mediatek.so'): blob_fixup()
        .add_needed('libaudioutils_shim.so')
        .replace_needed('libaudio_aidl_conversion_common_ndk.so', 'libaudio_aidl_conversion_common_ndk_prebuilt.so'),
    
    ('vendor/lib/libaudio_aidl_conversion_common_ndk_prebuilt.so', 'vendor/lib64/libaudio_aidl_conversion_common_ndk_prebuilt.so'): blob_fixup()
        .replace_needed('android.media.audio.common.types-V5-ndk.so', 'android.media.audio.common.types-V3-ndk.so'),
    
    ('vendor/lib/hw/android.hardware.soundtrigger3-impl.so', 'vendor/lib64/hw/android.hardware.soundtrigger3-impl.so'): blob_fixup()
        .replace_needed('libaudio_aidl_conversion_common_ndk.so', 'libaudio_aidl_conversion_common_ndk_prebuilt.so'),

    ('vendor/lib/vendor.mediatek.hardware.pq_aidl-V7-ndk.so', 'vendor/lib64/vendor.mediatek.hardware.pq_aidl-V7-ndk.so'): blob_fixup()
        .replace_needed('android.hardware.graphics.common-V4-ndk.so', 'android.hardware.graphics.common-V7-ndk.so'),

    ('vendor/lib64/libmtkcam_hal_aidl_common.so'): blob_fixup()
        .replace_needed('android.hardware.camera.common-V2-ndk.so', 'android.hardware.camera.common-V1-ndk.so'),

    ('vendor/lib64/hw/hwcomposer.mtk_common.so'): blob_fixup()
        .add_needed('libprocessgroup_shim.so'),

    ('vendor/lib/libteei_daemon_vfs.so', 'vendor/lib64/libteei_daemon_vfs.so'): blob_fixup()
        .add_needed('liblog.so'),

    ('vendor/bin/hw/android.hardware.contexthub-service.tinysys'): blob_fixup()
        .replace_needed('android.hardware.contexthub-V3-ndk.so', 'android.hardware.contexthub-V4-ndk.so'),

    ('vendor/bin/hw/mtkfusionrild'): blob_fixup()
        .add_needed('libutils-v33.so'),

    ('vendor/lib/mt6781/libneuron_adapter_mgvi.so', 'vendor/lib64/mt6781/libneuron_adapter_mgvi.so'): blob_fixup()
        .add_needed('libz.so')
        .add_needed('liblog.so')
        .add_needed('libnativewindow.so')
        .clear_symbol_version('AHardwareBuffer_allocate')
        .clear_symbol_version('AHardwareBuffer_createFromHandle')
        .clear_symbol_version('AHardwareBuffer_describe')
        .clear_symbol_version('AHardwareBuffer_getNativeHandle')
        .clear_symbol_version('AHardwareBuffer_lock')
        .clear_symbol_version('AHardwareBuffer_release')
        .clear_symbol_version('AHardwareBuffer_unlock'),

    ('vendor/lib64/libalLDC.so', 'vendor/lib64/libalhLDC.so', 'vendor/lib64/libneuralnetworks_sl_driver_mtk_legacy_prebuilt.so'): blob_fixup()
        .clear_symbol_version('AHardwareBuffer_allocate')
        .clear_symbol_version('AHardwareBuffer_createFromHandle')
        .clear_symbol_version('AHardwareBuffer_describe')
        .clear_symbol_version('AHardwareBuffer_getNativeHandle')
        .clear_symbol_version('AHardwareBuffer_lock')
        .clear_symbol_version('AHardwareBuffer_release')
        .clear_symbol_version('AHardwareBuffer_unlock'),
}

module = ExtractUtilsModule(
    'fire',
    'xiaomi',
    blob_fixups=blob_fixups,
    lib_fixups=lib_fixups,
    namespace_imports=namespace_imports,
    add_firmware_proprietary_file=True,
)

if __name__ == '__main__':
    prune_manifests_from_args()
    utils = ExtractUtils.device(module)
    utils.run()
    patch_pq_blob()
