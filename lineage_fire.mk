#
# Copyright (C) 2026 The YgorBRxx Project
#
# SPDX-License-Identifier: Apache-2.0
#

# Inherit from those products. Most specific first.
$(call inherit-product, $(SRC_TARGET_DIR)/product/core_64_bit_only.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/full_base_telephony.mk)

# Inherit some common Lineage stuff.
$(call inherit-product, vendor/lineage/config/common_full_phone.mk)

# Inherit from generic device
$(call inherit-product, device/xiaomi/fire/device.mk)

# Include GApps. The path to the gapps blobs may be different, check the vendor/gapps/arm64/Android.mk file and adjust accordingly.
# $(call inherit-product, vendor/gapps/arm64/arm64-vendor.mk)

PRODUCT_DEVICE := fire
PRODUCT_NAME := lineage_fire
PRODUCT_BRAND := Redmi
PRODUCT_MODEL := 23053RN02Y
PRODUCT_MANUFACTURER := Xiaomi

PRODUCT_SYSTEM_NAME := fire_global
PRODUCT_SYSTEM_DEVICE := fire

PRODUCT_GMS_CLIENTID_BASE := android-xiaomi

PRODUCT_BUILD_PROP_OVERRIDES += \
    BuildDesc="missi-user 15 AP3A.240905.015.A2 OS2.0.209.0.VMXMIXM release-keys" \
    BuildFingerprint=Redmi/fire_global/fire:15/AP3A.240905.015.A2/OS2.0.209.0.VMXMIXM:user/release-keys \
    DeviceName=$(PRODUCT_SYSTEM_DEVICE) \
    DeviceProduct=$(PRODUCT_SYSTEM_NAME) \
    ProductModel=$(PRODUCT_SYSTEM_DEVICE) \
    DeviceProduct=$(PRODUCT_SYSTEM_NAME)
