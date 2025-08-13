#include <any>
#include <array>
#include <cstdio>
#include <map>
#include <nlohmann/json.hpp>
#include <string>
#include <vector>

std::map<std::string, std::any> flatten_map(
    const std::map<std::string, std::any>& input_map,
    const std::string& parent_key = "",
    const std::string& sep = "|"
) {
    std::map<std::string, std::any> items;

    for (const auto& [key, value] : input_map) {
        std::string new_key = parent_key.empty() ? key : parent_key + sep + key;

        if (value.type() == typeid(std::string) ||
            value.type() == typeid(int) ||
            value.type() == typeid(long) ||
            value.type() == typeid(double) ||
            value.type() == typeid(float)) {
            items[new_key] = value;
        } else if (value.type() == typeid(std::map<std::string, std::any>)) {
            auto temp_map = std::any_cast<std::map<std::string, std::any>>(value);
            auto flattened = flatten_map(temp_map, new_key, sep);
            items.insert(flattened.begin(), flattened.end());
        } else if (value.type() == typeid(std::vector<std::any>)) {
            // Preserve arrays like Python version does
            items[new_key] = value;
        }
    }
    return items;
}