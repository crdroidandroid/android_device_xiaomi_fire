#
# Copyright (C) 2026 The LineageOS Project
#
# SPDX-License-Identifier: Apache-2.0
#

# Inherit from those products. Most specific first.
$(call inherit-product, $(SRC_TARGET_DIR)/product/core_64_bit_only.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/full_base_telephony.mk)

# Inherit some common Lineage stuff.
$(call inherit-product, vendor/lineage/config/common_full_phone.mk)

# Inherit from generic device
$(call inherit-product, device/xiaomi/sea/device.mk)

# Include GApps. The path to the gapps blobs may be different, check the vendor/gapps/arm64/Android.mk file and adjust accordingly.
# $(call inherit-product, vendor/gapps/arm64/arm64-vendor.mk)

PRODUCT_DEVICE := sea
PRODUCT_NAME := lineage_sea
PRODUCT_BRAND := Redmi
PRODUCT_MODEL := sea
PRODUCT_MANUFACTURER := Xiaomi

PRODUCT_SYSTEM_NAME := sea_global
PRODUCT_SYSTEM_DEVICE := sea

PRODUCT_GMS_CLIENTID_BASE := android-xiaomi

PRODUCT_BUILD_PROP_OVERRIDES += \
    BuildDesc="missi-user 15 AP3A.240905.015.A2 OS2.0.212.0.VHZMIXM release-keys" \
    BuildFingerprint=Redmi/sea_global/sea:15/AP3A.240905.015.A2/OS2.0.212.0.VHZMIXM:user/release-keys \
    DeviceName=$(PRODUCT_SYSTEM_DEVICE) \
    DeviceProduct=$(PRODUCT_SYSTEM_NAME) \
    ProductModel=$(PRODUCT_SYSTEM_DEVICE) \
    DeviceProduct=$(PRODUCT_SYSTEM_NAME)
