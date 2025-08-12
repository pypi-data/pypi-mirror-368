import sys
sys.path.append('./mapper')
import map_module
import json

class mapper:
    """
    Class for mapping and transforming JSON dictionaries.
    
    This class allows flattening nested dictionaries and mapping fields
    according to a specific configuration. It's useful for transforming data
    between different formats or structures.
    
    Attributes:
        sep (str): Separator used to concatenate nested keys. Default: "|"
        parent_key (str): Optional parent key to prefix all keys. Default: ""
    
    Example:
        >>> mapper_instance = mapper(sep=".", parent_key="data")
        >>> result = mapper_instance.map_dic(input_data, "config.json", "trigger_name")
    """
    
    def __init__(self, sep:str = "|", parent_key: str = "") -> None:
        """
        Initialize the mapper instance.
        
        Args:
            sep (str, optional): Separator for nested keys. Default: "|"
            parent_key (str, optional): Parent key to prefix all keys. Default: ""
        """
        self.sep = sep
        self.parent_key = parent_key
        pass
    
    def _flatten_dict(self, input_dict: dict) -> dict:
        """
        Flatten a nested dictionary into a simple key dictionary.
        
        Args:
            input_dict (dict): Input dictionary to be flattened
            
        Returns:
            dict: Flattened dictionary with concatenated keys using separator
            
        Raises:
            Exception: If input dictionary is empty or None
            
        Example:
            >>> input_data = {"a": {"b": {"c": 1}}}
            >>> result = mapper_instance._flatten_dict(input_data)
            >>> # Result: {"a|b|c": 1}
        """
        if not input_dict or input_dict == None:
            raise Exception("Empty dict")
        result_dict = map_module.flatten_map(input_dict, self.parent_key, self.sep)

        return result_dict
    
    def _mapping_fields(self, input_fields: dict, flatten_fields: dict) -> dict:
        """
        Map input fields to flattened fields using configuration.
        
        Args:
            input_fields (dict): Mapping configuration dictionary
            flatten_fields (dict): Flattened dictionary with input data
            
        Returns:
            dict: Dictionary with mapped fields according to configuration
            
        Raises:
            Exception: If input_fields or flatten_fields are empty or None
            
        Example:
            >>> config = {"nome": "name", "idade": "age"}
            >>> flat_data = {"name": "João", "age": 30}
            >>> result = mapper_instance._mapping_fields(config, flat_data)
            >>> # Result: {"nome": "João", "idade": 30}
        """
        if not input_fields or input_fields == None:
            raise Exception("Empty mapping fields")

        if not flatten_fields or flatten_fields == None:
            raise Exception("Empty flatten_fields")

        mapped_dict = map_module.mapping_fields(input_fields, flatten_fields, self.sep)
        return mapped_dict
    
    def map_dic(self, input_dict: dict, config_path: str, trigger: str = None) -> dict:
        """
        Map an input dictionary using file configuration.
        
        This is the main method that combines flattening and field mapping.
        First flattens the input dictionary, then loads the configuration
        from the specified file and applies the mapping.
        
        Args:
            input_dict (dict): Input dictionary to be mapped
            config_path (str): Path to the JSON configuration file
            trigger (str, optional): Specific key in configuration to use. Default: None
            
        Returns:
            dict: Dictionary with mapped data according to configuration
            
        Raises:
            Exception: If input_dict or config_path are empty or None
            FileNotFoundError: If configuration file is not found
            json.JSONDecodeError: If configuration file is not valid JSON
            
        Example:
            >>> input_data = {"user": {"name": "João", "age": 30}}
            >>> result = mapper_instance.map_dic(input_data, "mapping_config.json", "user_mapping")
        """
        if not input_dict or input_dict == None:
            raise Exception("Empty input dict")

        if not config_path or config_path == None:
            raise Exception("Empty config path")

        flatten_fields = self._flatten_dict(input_dict)

        with open(config_path, "r", encoding="utf-8") as file:
            config_json = json.loads(file.read())

        if trigger != None:
            config_json = config_json.get(trigger)

        mapped_dict = self._mapping_fields(config_json, flatten_fields)

        return mapped_dict
        

