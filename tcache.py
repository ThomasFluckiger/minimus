#!/usr/bin/env python3
"""cache controller class for use by minimus, but trying to be fairly generic"""
import os
import sys
import logging
import hashlib
import tkinter.filedialog
import xdg
import tconfig as cc


class CacheController():
    """ class for making a cache of salted file hashes and reading and writing them to a file"""
    def __init__(self, app_name,  the_salt):
        self._current_cache = set()
        self._cache_file = app_name + ".cache"
        self._cache_path = os.path.join(xdg.xdg_data_home() ,  self._cache_file)
        self._hash_salt = the_salt
        loaded_cache = self.load_cache()
        print(len(loaded_cache))
        if len(loaded_cache) == 0:
            self.create_cache()
            self.load_cache()
        print(self._current_cache)

    def load_cache(self):
        """open the cache file and load any contents as set, return False on failure"""
        try:
            with open(self._cache_path, 'r+') as minimus_cache:
                cache_contents = minimus_cache.read()
                if not cache_contents:
                    logging.info('Played song cache is empty')
                    return set()
                if len(cache_contents) == 1:
                    logging.info('Played song cache has a single song, which breaks splitlines()')
                    return cache_contents
                if len(cache_contents) > 1:
                    logging.info('Played song cache has multiple songs, which is the common path')

                    _cache_list = cache_contents.splitlines()
                    _curr_cache = set(_cache_list)
                    _cache_size = len(_curr_cache)
                    _logline = "cache loaded from file contains " + str(_cache_size) + "songs"
                    logging.info(_logline)
                    self._current_cache = _curr_cache
                    return _curr_cache
        except IOError:
            logging.error('IOERROR: Played songs cache does not exist')
            self.create_cache()
            return set()
        return set() #you should never hit this case, but pylint insists

    def create_cache(self):
        """create an empty cache file """
        if os.path.isfile(self._cache_path):
            logging.info('Cache is already a file,')

        if not os.path.isfile(self._cache_path):
            try:
                open(self._cache_path, 'a').close()
            except IOError:
                print("unable to create new cache file, this is fatal")
                sys.exit(0)
        try:
            open(self._cache_path,  'a+') #not sure if theres a simpler way to create a file.
            return None
        except IOError:
            logging.error('IOERROR: attempting to create cache failed,  this is fatal')
            sys.exit(1)

    def get_checksum(self, _filename):
        """get a checksum for the file passed as an argument, salt it, and return the hash"""
        logging.info('Entered function in CacheController: get_checksum(self,_filename)')
        md5_hash = hashlib.md5()
        file = open(_filename, "rb")
        fcontent = file.read()
        md5_hash.update(fcontent)
        encoded_salt = self._hash_salt.encode('utf-8')
        md5_hash.update(encoded_salt)
        _checksum = md5_hash.hexdigest()
        return _checksum

    def update_cache(self, _filename):
        """takes a file, salts, hashes and appends it to the cache file if it doesn't exist"""
        _hash = self.get_checksum(_filename)
        print(_hash)
#        print(self._current_cache)
        if not _hash in self._current_cache:
            print("hash is not in current_cache")
            self._current_cache.update(_hash)
            try:
                with open(self._cache_path, 'a+') as minimus_cache:
                    minimus_cache.write(_hash)
                    minimus_cache.write('\n')
                return True
            except IOError:
                logging.error("IOError exception: unable to append to cache file. exiting.")
                sys.exit(0)
        else:
            print("That hash already exists")
            return False

def main():
    """the main function of CacheController, for testing"""
    the_config = cc.ConfigController("minimus", {})
    the_dict = the_config.get()
    the_cache = CacheController("minimus",  the_dict['salt'])
    _dir = tkinter.filedialog.askdirectory()
    _file_count = 0
    if len(_dir) > 0:
        os.chdir(_dir)
        _file_list = os.listdir(_dir)
        cwd_pth = os.getcwd()
        for _file in _file_list:
            _file_path = os.path.join(cwd_pth,  _file)
            added = the_cache.update_cache(_file_path)
            if added:
                print("Cache updated")
            if not added:
                print("hash exists in cache")
            print(_file_path)
            _file_count += 1
    print(_file_count)
    sys.exit(0)

if __name__ == "__main__":
    main()
