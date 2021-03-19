#!/usr/bin/env python3
"""utility functions and classes for minimus"""
import sys
import logging
import tkinter.filedialog
import os
import notify2

def read_dir(_dir_path):
    """prompt to open a dir and return all files with a tkinter dialog"""
    logging.info('Entered function open_files in tutil.py, prompting for directory')
    _file_list = []
    _load_files = tkinter.filedialog.askdirectory()
    _cnt = 0
    if len(_load_files) > 0:
        os.chdir(_load_files)
        _dfiles = os.listdir(_load_files)
        _pth = os.getcwd()
        for _fname in _dfiles:
            _file_path = os.path.join(_pth,  _fname)
            _cnt = _cnt + 1
            _file_list.append(_file_path)
    nt_ = "Added "+str(_cnt)+" songs successfully"
    show_notification("Playlist", nt_)
    return _file_list


def close_app():
    """exit to the system, no errors, no logs"""
    sys.exit(0)


notify2.init('minimus')

def show_notification(header, body, note_type = 0):
    '''Show a notification, either using notify as default or not '''
    logging.info('Entered function: show_notification()')
    if note_type == 0:
        note = notify2.Notification(header, body)
        note.show()
    elif note_type ==1:
        print(str(header))
        print(str(body))

def main():
    """main function to test utility classes and functions"""
    show_notification("Notificatin","tested",0)
    os.chdir("/media/merlin/threepos")

    the_files = read_dir("/media/merlin/threepos")
    print(the_files)
    close_app()

if __name__ == "__main__":
    main()
