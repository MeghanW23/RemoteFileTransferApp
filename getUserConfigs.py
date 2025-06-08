import json 
import settings

global config 

with open(settings.user_config_file, 'r') as fp:
    config: dict = json.load(fp)

def edit_user_configs(key: str, new_value: any): 
    with open(settings.user_config_file, 'r') as fp:
        config: dict = json.load(fp)

    config[key] = new_value

    with open(settings.user_config_file, 'w') as fp:
        json.dump(config, fp=fp)
    
    with open(settings.user_config_file, 'r') as fp:
        config: dict = json.load(fp)
