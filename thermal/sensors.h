// SPDX-License-Identifier: Apache-2.0
#pragma once
#include <array>
#include <cmath>
#include <filesystem>
#include <fstream>
#include <optional>
#include <string>
#include <vector>

namespace fire {
struct Sensor {
    std::string name, zone;
    int type;
    std::array<float, 7> hot;
};
// Existing device thermal_info_config.json thresholds, not newly tuned limits.
// GPU/NPU aliases of the CPU sensor are deliberately not advertised.
inline const std::vector<Sensor> sensors = {
    {"CPU", "mtktscpu", 0, {NAN, NAN, NAN, 85, 90, 100, 117}},
    {"mtktsbattery", "mtktsbattery", 2, {NAN, NAN, NAN, 50, 55, 59, 60}},
    {"mtktsAP", "mtktsAP", 3, {NAN, NAN, NAN, 50, 70, 80, 90}},
    {"mtktsbtsmdpa", "mtktsbtsmdpa", 5, {NAN, NAN, NAN, 68, 90, 100, 110}},
};
inline std::string readText(const std::filesystem::path& path) {
    std::ifstream input(path);
    std::string value;
    std::getline(input, value);
    return value;
}
inline std::optional<long long> readInteger(const std::filesystem::path& path) {
    std::ifstream input(path);
    long long value;
    std::string extra;
    if (!(input >> value) || (input >> extra)) return std::nullopt;
    return value;
}
inline std::optional<float> temperature(const std::filesystem::path& path) {
    const auto raw = readInteger(path);
    // Reject driver sentinel -127000 and corrupt values; never report fake zero.
    if (!raw || *raw < -40000 || *raw > 150000) return std::nullopt;
    return static_cast<float>(*raw) / 1000.f;
}
inline int severity(float value, const std::array<float, 7>& hot) {
    int result = 0;
    for (int i = 1; i < 7; ++i)
        if (std::isfinite(hot[i]) && value >= hot[i]) result = i;
    return result;
}
inline std::filesystem::path findZone(const std::filesystem::path& root,
                                      const std::string& name) {
    std::error_code ec;
    for (const auto& entry : std::filesystem::directory_iterator(root, ec)) {
        if (entry.path().filename().string().rfind("thermal_zone", 0) != 0) continue;
        if (readText(entry.path() / "type") == name) return entry.path();
    }
    return {};
}
}  // namespace fire
