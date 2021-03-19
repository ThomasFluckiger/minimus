#!/usr/bin/env python3
"""config_controller is a wrapper to load toml configs"""
import os
import sys
import logging
import xdg
import toml

class ConfigController():
    """ConfigController: for when you have more than a single line config
        requires: toml, xdg, os
        
        takes a dict containing configuration and app_name as arguments.
        it uses xdg paths for files, and if the file exists it loads the file instead. 
        calling set_config with a different dict replaces the file
        passing an empty dict on an existing file returns the proper config
    """
    def __init__(self, app_name, config_dict):
        self._config_dict = config_dict
        self._app_name = app_name
        self._file_name = self._app_name + ".conf"
        self._config_file = os.path.join(xdg.xdg_config_home(),  self._file_name)

        if not os.path.isfile(self._config_file):
            self.write_config()
        self.read_file()

    def write_config(self):
        """write a config file """
        print("creating new toml conf file")
        print(self._file_name)
        print(self._config_dict)
        try:
            with open(self._config_file, 'w') as file:
                print("file should be open")
                toml_string = toml.dump(self._config_dict, file)
                print(toml_string)
        except IOError:
            logging.error('unable to create new config file, this is fatal')
            sys.exit(0)

    def set_config(self, new_dict):
        """replace self.config_dict, with a new_dict and flush to disk"""
        self._config_dict = new_dict
        self.write_config()

    def read_file(self):
        """read the configuration file"""
        try:
            with open(self._config_file, 'r') as file:
                self._config_dict = toml.load(file)
        except IOError:
            logging.error('unable to read config file, this is fatal')
            sys.exit()
        return self._config_dict

    def get(self):
        """return the config dict"""
#        print(self._config_dict)
        return self._config_dict


def main():
    """the main function, to test the config manager"""
    #config_path = os.path.join(xdg.xdg_config_home(),  "minimus.conf")

    config_dict = {'path': 'media/music', 'salt': 'ababababababababa'}
    app_name = "maximus"
    the_config = ConfigController(app_name, config_dict)
    print(the_config.get())
    sys.exit()

if __name__ == "__main__":
    main()
