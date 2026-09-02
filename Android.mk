#
# Copyright (C) 2026 The LineageOS Project
#
# SPDX-License-Identifier: Apache-2.0
#

LOCAL_PATH := $(call my-dir)

ifeq ($(TARGET_DEVICE),fire)
ifeq ($(FIRE_KERNEL_VERSION),6.6)

FIRE_KERNEL_6_6_PLATFORM_ABS := $(abspath $(FIRE_KERNEL_6_6_PLATFORM))
FIRE_KERNEL_6_6_SOURCE_ABS := $(abspath $(FIRE_KERNEL_6_6_SOURCE))
FIRE_KERNEL_6_6_PREBUILT_DIR_ABS := $(abspath $(FIRE_KERNEL_6_6_PREBUILT_DIR))
FIRE_KERNEL_6_6_OUT_DIR ?= $(FIRE_KERNEL_6_6_PLATFORM_ABS)/out
FIRE_KERNEL_6_6_STAMP := $(FIRE_KERNEL_6_6_PREBUILT_DIR_ABS)/.fire-kernel-6.6.stamp

ifeq ($(FIRE_KERNEL_BUILD_TYPE),source)
.PHONY: fire-kernel-6.6
fire-kernel-6.6: $(FIRE_KERNEL_6_6_STAMP)

$(FIRE_KERNEL_6_6_STAMP): FORCE
	$(hide) mkdir -p $(dir $@)
	$(hide) cd $(FIRE_KERNEL_6_6_PLATFORM_ABS) && \
		PROJECT=$(FIRE_KERNEL_6_6_PROJECT) \
		MODE=$(FIRE_KERNEL_6_6_MODE) \
		OUT_DIR=$(FIRE_KERNEL_6_6_OUT_DIR) \
		./$(FIRE_KERNEL_6_6_MODULES_DIR)/build.sh
	$(hide) cd $(FIRE_KERNEL_6_6_SOURCE_ABS) && \
		PROJECT=$(FIRE_KERNEL_6_6_PROJECT) \
		MODE=$(FIRE_KERNEL_6_6_MODE) \
		KERNEL_ROOT=$(FIRE_KERNEL_6_6_PLATFORM_ABS) \
		OUT_DIR=$(FIRE_KERNEL_6_6_OUT_DIR) \
		ROM_ARTIFACTS_DIR=$(FIRE_KERNEL_6_6_PREBUILT_DIR_ABS) \
		SKIP_AK3=1 \
		./scripts/package_fire_ak3.sh
	$(hide) touch $@

$(TARGET_PREBUILT_KERNEL) $(BOARD_PREBUILT_DTBOIMAGE) $(FIRE_KERNEL_6_6_PREBUILT_DTB) $(FIRE_KERNEL_6_6_PREBUILT_VENDOR_BOOT): $(FIRE_KERNEL_6_6_STAMP)
endif

# HOS2 uses the stock partitioned module contract (vendor_boot/vendor_dlkm/
# system_dlkm/odm_dlkm). Do not copy the kernel dist module universe into
# /vendor/lib/modules; the stock module payload is integrated separately.

endif
endif
