#include <any>
#include <cstddef>
#include <string>
#include <map>
#include <sstream>
#include <vector>
#include <typeinfo>

std::map<std::string, std::any> mapping_fields(
    const std::map<std::string, std::string>& input_fields,
    const std::map<std::string, std::any>& flatten_fields,
    const std::string& sep
){

    std::map<std::string, std::any> result;

    // Process each mapping rule
    for(const auto& [input_key, flatten_key] : input_fields){
        // Get the value from flattened fields
        auto it = flatten_fields.find(flatten_key);
        if (it == flatten_fields.end()) {
            continue; // Skip if value not found
        }
        
        std::any value = it->second;
        
        // Split input key into parts if it contains separator
        if (input_key.find(sep) != std::string::npos) {
            // Create nested structure
            std::stringstream ss(input_key);
            std::string part;
            std::vector<std::string> key_parts;
            
            // Split by separator
            while (std::getline(ss, part, sep[0])) {
                key_parts.push_back(part);
            }
            
            // Navigate through the nested structure
            std::map<std::string, std::any>* current = &result;
            
            for (size_t i = 0; i < key_parts.size() - 1; ++i) {
                const std::string& part = key_parts[i];
                
                // Check if current level exists and is a map
                auto current_it = current->find(part);
                if (current_it == current->end()) {
                    // Create new nested map
                    (*current)[part] = std::map<std::string, std::any>{};
                } else if (current_it->second.type() != typeid(std::map<std::string, std::any>)) {
                    // If it's not a map, replace with a new map
                    (*current)[part] = std::map<std::string, std::any>{};
                }
                
                // Navigate to the next level
                current = &std::any_cast<std::map<std::string, std::any>&>((*current)[part]);
            }
            
            // Set the final value
            (*current)[key_parts.back()] = value;
        } else {
            // Direct mapping for non-nested keys
            result[input_key] = value;
        }
    }
    
    return result;
} 