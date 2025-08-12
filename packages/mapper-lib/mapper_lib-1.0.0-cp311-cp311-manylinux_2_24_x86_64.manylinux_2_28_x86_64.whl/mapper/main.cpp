#include <any>
#include <cstdio>
#include <map>
#include <nlohmann/json.hpp>
#include <string>
#include <Python.h>

std::map<std::string, std::any> flatten_map(
    const std::map<std::string, std::any>& input_map,
    const std::string& parent_key = "",
    const std::string& sep = "|"
);

std::map<std::string, std::any> mapping_fields(
    const std::map<std::string, std::string>& input_fields,
    const std::map<std::string, std::any>& flatten_fields,
    const std::string& sep = "|"
);

std::map<std::string, std::any> map_dic(
    const std::map<std::string, std::any>& input_map,
    const std::map<std::string, std::string>& map_fields,
    const std::string& sep, 
    const std::string& parent_key
    ){   

    // Step 1: Flatten the data
    auto flattened_data = flatten_map(input_map, parent_key, sep);

    // Step 2: Apply mapping to reconstruct nested structure
    auto mapped_data = mapping_fields(map_fields, flattened_data, sep);

    return mapped_data;
}

// Helper function to convert Python dict to C++ map with memory optimization
std::map<std::string, std::any> py_dict_to_cpp_map(PyObject* py_dict) {
    std::map<std::string, std::any> cpp_map;
    
    if (!PyDict_Check(py_dict)) {
        return cpp_map;
    }
    
    // Note: std::map doesn't have reserve method, but we could use unordered_map for better performance
    // if memory allocation becomes a bottleneck
    
    PyObject *key, *value;
    Py_ssize_t pos = 0;
    
    while (PyDict_Next(py_dict, &pos, &key, &value)) {
        // Convert key to string
        PyObject* key_str = PyObject_Str(key);
        if (!key_str) continue;
        
        const char* key_cstr = PyUnicode_AsUTF8(key_str);
        if (!key_cstr) {
            Py_DECREF(key_str);
            continue;
        }
        
        std::string cpp_key(key_cstr);
        
        // Convert value based on type with move semantics
        if (PyUnicode_Check(value)) {
            const char* val_cstr = PyUnicode_AsUTF8(value);
            if (val_cstr) {
                cpp_map.emplace(std::move(cpp_key), std::string(val_cstr));
            }
        } else if (PyLong_Check(value)) {
            long val = PyLong_AsLong(value);
            cpp_map.emplace(std::move(cpp_key), val);
        } else if (PyFloat_Check(value)) {
            double val = PyFloat_AsDouble(value);
            cpp_map.emplace(std::move(cpp_key), val);
        } else if (PyDict_Check(value)) {
            // Recursive call for nested dictionaries
            auto nested_map = py_dict_to_cpp_map(value);
            cpp_map.emplace(std::move(cpp_key), std::move(nested_map));
        } else if (PyList_Check(value)) {
            // Handle lists/arrays with pre-allocation
            std::vector<std::any> vec;
            Py_ssize_t list_size = PyList_Size(value);
            if (list_size > 0) {
                vec.reserve(list_size);
            }
            
            for (Py_ssize_t i = 0; i < list_size; ++i) {
                PyObject* item = PyList_GetItem(value, i);
                if (PyUnicode_Check(item)) {
                    const char* item_cstr = PyUnicode_AsUTF8(item);
                    if (item_cstr) vec.emplace_back(std::string(item_cstr));
                } else if (PyLong_Check(item)) {
                    vec.emplace_back(PyLong_AsLong(item));
                } else if (PyFloat_Check(item)) {
                    vec.emplace_back(PyFloat_AsDouble(item));
                }
            }
            cpp_map.emplace(std::move(cpp_key), std::move(vec));
        }
    }
    
    return cpp_map;
}

// Helper function to convert C++ map to Python dict with memory optimization
PyObject* cpp_map_to_py_dict(const std::map<std::string, std::any>& cpp_map) {
    PyObject* py_dict = PyDict_New();
    if (!py_dict) return nullptr;
    
    // Pre-allocate dictionary size if possible
    PyDict_SetItem(py_dict, Py_None, Py_None); // Dummy item to trigger resize
    PyDict_DelItem(py_dict, Py_None);
    
    for (const auto& [key, value] : cpp_map) {
        PyObject* py_key = PyUnicode_FromString(key.c_str());
        if (!py_key) continue;
        
        PyObject* py_value = nullptr;
        
        if (value.type() == typeid(std::string)) {
            py_value = PyUnicode_FromString(std::any_cast<std::string>(value).c_str());
        } else if (value.type() == typeid(int)) {
            py_value = PyLong_FromLong(std::any_cast<int>(value));
        } else if (value.type() == typeid(long)) {
            py_value = PyLong_FromLong(std::any_cast<long>(value));
        } else if (value.type() == typeid(double)) {
            py_value = PyFloat_FromDouble(std::any_cast<double>(value));
        } else if (value.type() == typeid(float)) {
            py_value = PyFloat_FromDouble(std::any_cast<float>(value));
        } else if (value.type() == typeid(std::map<std::string, std::any>)) {
            py_value = cpp_map_to_py_dict(std::any_cast<const std::map<std::string, std::any>&>(value));
        } else if (value.type() == typeid(std::vector<std::any>)) {
            const auto& vec = std::any_cast<const std::vector<std::any>&>(value);
            py_value = PyList_New(vec.size());
            for (size_t i = 0; i < vec.size(); ++i) {
                PyObject* item = nullptr;
                if (vec[i].type() == typeid(std::string)) {
                    item = PyUnicode_FromString(std::any_cast<std::string>(vec[i]).c_str());
                } else if (vec[i].type() == typeid(int)) {
                    item = PyLong_FromLong(std::any_cast<int>(vec[i]));
                } else if (vec[i].type() == typeid(long)) {
                    item = PyLong_FromLong(std::any_cast<long>(vec[i]));
                } else if (vec[i].type() == typeid(double)) {
                    item = PyFloat_FromDouble(std::any_cast<double>(vec[i]));
                }
                if (item) PyList_SetItem(py_value, i, item);
            }
        }
        
        if (py_value) {
            PyDict_SetItem(py_dict, py_key, py_value);
            Py_DECREF(py_value);
        }
        Py_DECREF(py_key);
    }
    
    return py_dict;
}

// Helper function to convert Python dict of strings to C++ map<string, string> with optimization
std::map<std::string, std::string> py_dict_to_cpp_string_map(PyObject* py_dict) {
    std::map<std::string, std::string> cpp_map;
    
    if (!PyDict_Check(py_dict)) {
        return cpp_map;
    }
    
    // Note: std::map doesn't have reserve method, but we could use unordered_map for better performance
    // if memory allocation becomes a bottleneck
    
    PyObject *key, *value;
    Py_ssize_t pos = 0;
    
    while (PyDict_Next(py_dict, &pos, &key, &value)) {
        // Convert key to string
        PyObject* key_str = PyObject_Str(key);
        if (!key_str) continue;
        
        const char* key_cstr = PyUnicode_AsUTF8(key_str);
        if (!key_cstr) {
            Py_DECREF(key_str);
            continue;
        }
        
        std::string cpp_key(key_cstr);
        
        // Convert value to string
        if (PyUnicode_Check(value)) {
            const char* val_cstr = PyUnicode_AsUTF8(value);
            if (val_cstr) {
                cpp_map.emplace(std::move(cpp_key), std::string(val_cstr));
            }
        } else {
            // Convert other types to string
            PyObject* val_str = PyObject_Str(value);
            if (val_str) {
                const char* val_cstr = PyUnicode_AsUTF8(val_str);
                if (val_cstr) {
                    cpp_map.emplace(std::move(cpp_key), std::string(val_cstr));
                }
                Py_DECREF(val_str);
            }
        }
        Py_DECREF(key_str);
    }
    
    return cpp_map;
}

static PyObject* py_flatten_map(PyObject* self, PyObject* args) {
    PyObject* input_dict;
    const char* parent_key = "";
    const char* sep = "|";
    
    // Parse arguments: (dict, parent_key="", sep="|")
    if (!PyArg_ParseTuple(args, "O|ss", &input_dict, &parent_key, &sep)) {
        PyErr_SetString(PyExc_TypeError, "flatten_map() expects a dict and optional parent_key and sep strings");
        return nullptr;
    }
    
    // Check if input_dict is actually a dictionary
    if (!PyDict_Check(input_dict)) {
        PyErr_SetString(PyExc_TypeError, "First argument must be a dictionary");
        return nullptr;
    }
    
    try {
        // Convert Python dict to C++ map
        auto cpp_input_map = py_dict_to_cpp_map(input_dict);
        
        // Call the C++ flatten_map function
        auto flattened_result = flatten_map(cpp_input_map, std::string(parent_key), std::string(sep));
        
        // Convert result back to Python dict
        PyObject* result = cpp_map_to_py_dict(flattened_result);
        
        if (!result) {
            PyErr_SetString(PyExc_RuntimeError, "Failed to convert result to Python dictionary");
            return nullptr;
        }
        
        return result;
        
    } catch (const std::exception& e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return nullptr;
    }
}

static PyObject* py_mapping_fields(PyObject* self, PyObject* args) {
    PyObject* input_fields;
    PyObject* flatten_fields;
    const char* sep = "|";
    
    // Parse arguments: (input_fields_dict, flatten_fields_dict, sep="|")
    if (!PyArg_ParseTuple(args, "OO|s", &input_fields, &flatten_fields, &sep)) {
        PyErr_SetString(PyExc_TypeError, "mapping_fields() expects two dicts and optional sep string");
        return nullptr;
    }
    
    // Check if both arguments are dictionaries
    if (!PyDict_Check(input_fields) || !PyDict_Check(flatten_fields)) {
        PyErr_SetString(PyExc_TypeError, "Both arguments must be dictionaries");
        return nullptr;
    }
    
    try {
        // Convert Python dicts to C++ maps
        auto cpp_input_fields = py_dict_to_cpp_string_map(input_fields);
        auto cpp_flatten_fields = py_dict_to_cpp_map(flatten_fields);
        
        // Call the C++ mapping_fields function
        auto mapped_result = mapping_fields(cpp_input_fields, cpp_flatten_fields, std::string(sep));
        
        // Convert result back to Python dict
        PyObject* result = cpp_map_to_py_dict(mapped_result);
        
        if (!result) {
            PyErr_SetString(PyExc_RuntimeError, "Failed to convert result to Python dictionary");
            return nullptr;
        }
        
        return result;
        
    } catch (const std::exception& e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return nullptr;
    }
}

static PyObject* py_map_dict(PyObject* self, PyObject* args) {
    PyObject* input_map;
    PyObject* map_fields;
    const char* sep = "|";
    const char* parent_key = "";
    
    // Parse arguments: (input_map_dict, map_fields_dict, sep="|", parent_key="")
    if (!PyArg_ParseTuple(args, "OO|ss", &input_map, &map_fields, &sep, &parent_key)) {
        PyErr_SetString(PyExc_TypeError, "map_dic() expects two dicts and optional sep and parent_key strings");
        return nullptr;
    }
    
    // Check if both arguments are dictionaries
    if (!PyDict_Check(input_map) || !PyDict_Check(map_fields)) {
        PyErr_SetString(PyExc_TypeError, "Both arguments must be dictionaries");
        return nullptr;
    }
    
    try {
        // Convert Python dicts to C++ maps
        auto cpp_input_map = py_dict_to_cpp_map(input_map);
        auto cpp_map_fields = py_dict_to_cpp_string_map(map_fields);
        
        // Call the C++ map_dic function
        auto result_map = map_dic(cpp_input_map, cpp_map_fields, std::string(sep), std::string(parent_key));
        
        // Convert result back to Python dict
        PyObject* result = cpp_map_to_py_dict(result_map);
        
        if (!result) {
            PyErr_SetString(PyExc_RuntimeError, "Failed to convert result to Python dictionary");
            return nullptr;
        }
        
        return result;
        
    } catch (const std::exception& e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return nullptr;
    }
}

static PyMethodDef map_methods[] = {
    {"flatten_map", py_flatten_map, METH_VARARGS, "Achata o payload"},
    {"mapping_fields", py_mapping_fields, METH_VARARGS, "Mapeia o payload achatado"},
    {"map_dict", py_map_dict, METH_VARARGS, "Executa todo o processo de mapeamento"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef map_module = {
    PyModuleDef_HEAD_INIT,
    "map_module",         // m_name
    NULL,                 // m_doc
    -1,                   // m_size
    map_methods           // m_methods
};

PyMODINIT_FUNC PyInit_map_module(void) {
    return PyModule_Create(&map_module);
}
