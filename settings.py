import json
import os

def read_settings():
    if os.path.exists('settings.json'):
        fh = open('settings.json')
        settings = json.load(fh)
        fh.close()
        return settings
    else:
        return {}

def write_settings(settings):
    fh = open('settings.json', 'w')
    json.dump(settings, fh, indent=2)
    fh.close()

def get_setting(key):
    settings = read_settings()
    if key in settings.keys():
        return settings[key]
    else:
        return ''

def set_setting(key, value):
    settings = read_settings()
    settings[key] = value
    write_settings(settings)
