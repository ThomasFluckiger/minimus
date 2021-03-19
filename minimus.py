#!/usr/bin/env python3
""" a minimal music player module and GUI using libvlc for playback"""
import math
import sys
import os
import tkinter
import tkinter.filedialog #why do I need this?
import random
import time
import logging
import vlc
import magic
import notify2
import eyed3
import tconfig
import tcache


def close_app():
    """exit to the system, no errors, no logs"""
    sys.exit(0)

def show_notification(header, body, note_type = 0):
    '''Show a notification, either using notify as default or not '''
    logging.info('Entered function: show_notification()')

    if note_type == 0:
        note = notify2.Notification(header, body)
        note.show()
    elif note_type ==1:
        print(str(header))
        print(str(body))

class Song():
    """ a class to deal with song data for use by the playlistmanager"""
    def __init__(self, fname):
        self.filename = fname
        self.artist = ""
        self.album = ""
        self.title = ""

    def add_tags(self):
        '''Add tags using the filename defined in init'''
        logging.info('Entered function in Song: add_tags(self)')
        taggy = eyed3.load(self.filename)
        sartist = taggy.tag.artist
        salbum = taggy.tag.album
        strack = taggy.tag.title
        self.artist = sartist
        self.album = salbum
        self.title = strack

    def get_full_path(self):
        '''return the filename associated with the song object'''
        logging.info('Entered function in Song: get_full_path(self)')

        return self.filename

    def info(self):
        '''print the info from the song'''
        logging.info("Entered function in Song: info(self)")
#        print("file:", self.filename, "\n")
#        print("checksum", self.chksm, "\n")
#        print("Artist:", self.artist, " Album: ",  self.album, "\n",  "Track: ",  self.title)
        return self.artist,  self.album,  self.title



class PlayListManager():
    '''a playlist manager class to wrap libvlc '''
    def __init__(self, config, the_cache):
        self.current_song = None
        self._cache = the_cache
        self.songs = []
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.current_volume = vlc.libvlc_audio_get_volume(self.player)
        self._current_cache = the_cache.load_cache()
        self._config_dict = config.get()
        self.md5_salt = self._config_dict['salt']
        self.lib_path = self._config_dict['path']
        print(self._cache)
        try:
            os.chdir(self.lib_path)
        except FileNotFoundError:
            print("can't open path in config")
            sys.exit()


    def add_song(self, _filename):
        '''take a file and import it to the songs list if it is a song'''
        logging.info('Entered function in PlayListManager: add_song(self, _filename)')

#     to begin, hopefully the default path for most files with tags read by eyed3 using magic'''
        _magic_tag = magic.from_file(_filename)
        if "Audio file with ID3" in _magic_tag:
            this_song = Song(_filename)
            this_song.add_tags()
            self.songs.append(this_song)
            return self.songs

#      unfortunately magic is imperfect and some mpeg audio with tags go unrecognized this way
        _mime = magic.from_file(_filename, mime=True)
#        print(_mime)
        if _mime == "audio/mpeg":
            this_song = Song(_filename)
            this_song.add_tags()
            self.songs.append(this_song)
            return self.songs

        if _mime =="image/jpeg":
            print("ignoring album art")
            return 0
        if _mime =="inode/x-empty":
            print("An Empty file? delete this crap!")
            return 0

#apparently some mp3s return application octet-streams as mime this is a test stub
        if _mime ==  "application/octet-stream":
            print("Yay, an unidentifiable octet-stream that may or may not be audio")
            print("trying to add minus tags")
            print("_magic_tag: ",  _magic_tag)
            this_song = Song(_filename)
            self.songs.append(this_song)
            return self.songs

        print(_filename," has unrecognized mimetype,", _mime,", skipping")
        return 0

    def play_random(self):
        '''return and remove a random song object from the playlist to be played'''
        logging.info('Entered function in PlayListManager: play_random(self)')

        songs_in_list = len(self.songs)
#        print("playlist contains", songs_in_list, "songs.")
        if songs_in_list > 1:
            song_pick = random.randint(0, songs_in_list-1)
#            print("I chose track #", song_pick)
            pick = self.songs.pop(song_pick)
            self.play(pick)
        else:
            show_notification("Nothing to play", "random function has nothing to do")


    def play_next(self):
        '''pop the next song off the playlist add it to played songs
         ironically, this doesn't actually play it, and needs to be renamed
         It uses the new play function to reuse the code with shuffle option'''
        logging.info('Entered function in PlayListManager: play_next(self)')

        songs_remaining = len(self.songs) -1
        show_notification("songs remaining: ", str(songs_remaining), 1)

        if songs_remaining > 0:
            trak = self.songs.pop(0)
            self.play(trak)
        else:
            show_notification("Nothing to play", "nothing to do")


    def play(self, sobj):
        '''play a track from a song object'''
        logging.info('Entered function in PlayListManager: play(self)')
        _file_name = sobj.filename
        self.player.stop()
        fresh = self._cache.update_cache(_file_name)
        if fresh:
            print("This is where we actually do the dirty work")
            self.current_song = sobj
            file_to_play = sobj.filename
            media = self.instance.media_new(file_to_play)
            self.player.set_media(media)
            self.player.play()
            header = sobj.artist
            body = sobj.album + "\n"+sobj.title
            show_notification(header, body, 0)
        else:
            show_notification("Skipping","You already heard that one", 0)
            self.play_random()

    def current_notify(self):
        """display the curront song information using show_notification"""
        logging.info('Entered function in PlayListManager: current_notify(self)')

        line2 = self.current_song.album + "\n" + self.current_song.title
        show_notification(self.current_song.artist,  line2)

    def mute_volume(self):
        """ toggle the player mute function """
        logging.info('Entered function in PlayListManager: mute_volume(self)')
        vlc.libvlc_audio_toggle_mute(self.player)

    def play_pause(self):
        """ toggle pause with libvlc"""
        logging.info('Entered function in PlayListManager: play_pause(self)')
        vlc.libvlc_media_player_pause(self.player)

    def pause_media(self):
        '''toggle pause on player object directly'''
        logging.info('Entered function in PlayListManager: pause_media(self)')
        self.player.pause()

    def resume_media(self):
        '''tell the player object to play'''
        logging.info('Entered function in PlayListManager: resume_media(self)')
        self.player.play()

    def set_volume(self, volume):
        '''set the volume to a specified level no sanity checks'''
        logging.info('Entered function in PlayListManager: set_volume(self)')
        vlc.libvlc_audio_set_volume(self.player,  volume)

    def get_volume(self):
        '''return the volume and show a notification'''
        logging.info('Entered function in PlayListManager: get_volume(self)')
        vol_ = vlc.libvlc_audio_get_volume(self.player)
        show_notification("Volume", vol_)
        return vol_

    def volume_up(self, prcnt = 10):
        '''pump up the volume 10% by default'''
        logging.info('Entered function in PlayListManager: volume_up(self,prcnt=10)')
        self.current_volume = vlc.libvlc_audio_get_volume(self.player)
        self.current_volume = self.current_volume + prcnt
        if self.current_volume >100:
            self.current_volume = 100
        vlc.libvlc_audio_set_volume(self.player,  self.current_volume)
        show_notification("Volume", str(self.current_volume))

    def volume_down(self,  prcnt = 10):
        """turn the volume down 10% by default"""
        logging.info('Entered function in PlayListManager: volume_down(self,prcnt=10)')
        self.current_volume = vlc.libvlc_audio_get_volume(self.player)
        self.current_volume = self.current_volume - prcnt
        if self.current_volume <0:
            self.current_volume = 0
        vlc.libvlc_audio_set_volume(self.player,  self.current_volume)
        show_notification("Volume", str(self.current_volume))

    def playback_status(self):
        """ return the track length and current position"""
        logging.info('Entered function in PlayListManager: playback_status(self)')
        track_length = vlc.libvlc_media_player_get_length(self.player)
        current_position = vlc.libvlc_media_player_get_position(self.player)
        return track_length, current_position

    def is_playing(self):
        '''returns current status of the media player'''
        logging.info('Entered function in PlayListManager: is_playing(self)')
        play_status = vlc.libvlc_media_player_get_state(self.player)
        return str(play_status)

    def get_track_info(self):
        """returns _artist, _album, and _track for use in updating the GUI"""
        _artist,  _album, _track = self.current_song.info()
        return _artist,  _album,  _track

class MainWindow(tkinter.Frame):
    '''The MainWindow class for a simple tkinter GUI with only a single frame'''
    def __init__(self, the_cache, master=None):
        super().__init__(master)
        self.master = master
#        self.current_cache ={0 }
        self.shuffle = tkinter.IntVar()
        self.app_name = "minimus"
        self.default_dict = {}
#        self.default_dict['path']= '/media/merlin/threepos/music'
#        self.default_dict['salt']= uuid.uuid4().hex
        self.configuration_dict = tconfig.ConfigController(self.app_name,  self.default_dict)
        #this may be different from self.default_dict if the
        #configuration exists, this is intentional if slightly dumb way to not nuke salts
        #and also allows empty dicts to be passed if the app_name.config exists already
        print(self.configuration_dict)
        self.play_list = PlayListManager(self.configuration_dict, the_cache)
        self.create_widgets()
        self.pack()

    def on_checkbox(self):
        '''MainWindow checkbox callback'''
        logging.info('Entered callback function in MainWindow: on_checkbox(self)')

        check_status = self.shuffle.get()
        _logline = 'self.shuffle.get(): ' + str(check_status)
        logging.debug(_logline)

#        if check_status == 0:
#            print("Not shuffling")
#        if check_status ==1:
#            print("everyday I'm shufflin")
#        print(check_status)
        return check_status

    def create_widgets(self):
        '''create the widgets in the window'''
        logging.info('Entered function in MainWindow: create_widgets(self)')

        self.ok_button = tkinter.Button(self)
        self.ok_button["text"] = "Break Things"
        self.ok_button["command"] = self.on_ok_button
        self.ok_button.pack(side="left")
#        self.ok_button.grid(column=1, row=0)


        self.load_button = tkinter.Button(self)
        self.load_button["text"] = "Load"
        self.load_button["command"] = self.on_load_button
        self.load_button.pack(side = "top")
#        self.load_button.pack(column=2, row=0)

        self.play_button = tkinter.Button(self)
        self.play_button["text"] = "Play Next"
        self.play_button["command"] = self.on_play_button
        self.play_button.pack(side = "right")

        self.mute_button = tkinter.Button(self)
        self.mute_button["text"] = "Mute"
        self.mute_button["command"] = self.on_mute_button
        self.mute_button.pack(side = "right")

        self.pause_button = tkinter.Button(self)
        self.pause_button["text"] = "Play/Pause"
        self.pause_button["command"] = self.on_play_pause
        self.pause_button.pack(side = "right")

        self.volume_up_button = tkinter.Button(self)
        self.volume_up_button["text"]="Vol +"
        self.volume_up_button["command"] = self.on_vol_up
        self.volume_up_button.pack(side = "top")

        self.volume_down_button = tkinter.Button(self)
        self.volume_down_button["text"]="Vol -"
        self.volume_down_button["command"] = self.on_vol_down
        self.volume_down_button.pack(side = "top")

        self.quit_button = tkinter.Button(self)
        self.quit_button["text"]="Quit"
        self.quit_button["command"]= close_app
        self.quit_button.pack(side = "right")

        self.shuffle_radio = tkinter.Checkbutton(self, text="Shuffle", variable = self.shuffle)
        self.shuffle_radio["command"]= self.on_checkbox
        self.shuffle_radio.pack(side = "right")


        self.label_artist = tkinter.Label(self, text="Artist")
        self.label_artist.pack(side = "left")
#        self.label_artist.pack(column=5, row=0)

        self.label_album = tkinter.Label(self, text="Album")
#        self.label_album.pack(column=6, row=0)
        self.label_album.pack(side = "left")

        self.label_track = tkinter.Label(self, text="Track")
        self.label_track.pack(side = "left")
#        self.label_track.pack(column=7, row=0)

        self.label_status = tkinter.Label(self, text="Status")
        self.label_status.after(1000,  self.update_label())
        self.label_status.pack(side = "bottom")
#        self.label_status.pack(column=8, row=0)

    def update_label(self):
        '''upate various bits using .after to update using a GUI label to trigger'''
        logging.info('Entered function in MainWindow: update_label(self)')

        play_status_ = self.play_list.is_playing()
        #defaults for first starting UI
        status_msg_ = ""
        _artist = ""
        _album = ""
        _track = ""

        if play_status_ == "State.Ended":
#            print("Playback Stopped")
            status_msg_ = "Ended"
            logging.info("Current Song Ended")
            self.on_play_button()


        if  play_status_ == "State.Playing":
            traklen,  playpos = self.play_list.playback_status()
            _p = playpos*100
            progress_ = math.trunc(_p)
            formatted_length_ = time.strftime('%H:%M:%S', time.gmtime(traklen/1000))
            _song_length = str(formatted_length_)
            _song_progress = str(progress_)
            status_msg_ = "Playing "+ _song_progress + "%/" + _song_length
            _artist, _album,  _track = self.play_list.get_track_info()

        if play_status_ == "State.NothingSpecial":
            status_msg_ = "Initialized"
        elif play_status_ == "State.Paused":
            status_msg_ = "Paused"


        self.label_artist["text"] = "Artist: " + _artist
        self.label_album["text"] = "Album: " + _album
        self.label_track["text"] = "Track: " +  _track

        self.label_status["text"] = status_msg_
        self.label_status.after(1000,  self.update_label)

    def on_ok_button(self):
        '''ok button callback'''
        logging.info('Entered callback function in MainWindow: on_ok_button(self)')

        show_notification("Stop!", "Please don't push this button again")
        self.play_list.play_next()
        self.play_list.current_notify()
#        self.play_list.print_list()

    def on_load_button(self):
        '''load button notify and callback'''
        logging.info('Entered callback function in MainWindow: on_load_button(self)')
        load_files = tkinter.filedialog.askdirectory()
#        print(load_files)
#      if the user selects dumb files, do nothing gracefully
        #and count files actually added
        cnt = 0
        if len(load_files) > 0:
            os.chdir(load_files)
    #        self.status = "Loading"
            dfiles = os.listdir(load_files)
            pth = os.getcwd()
            for fname in dfiles:
                full_path_ = os.path.join(pth,  fname)
                add_success = self.play_list.add_song(full_path_)
                if add_success:
                    cnt = cnt + 1
        nt_ = "Added "+str(cnt)+" songs successfully"
        show_notification("Playlist", nt_)
        return cnt

    def on_play_button(self):
        """play button callback notify is in play_next"""
        logging.info('Entered callback function in MainWindow: on_play_button(self)')
        shuffle_status =  self.on_checkbox()
#        print(shuffle_status)
        if shuffle_status == 0:
            self.play_list.play_next()
        if shuffle_status == 1:
#            print("Playing random track")
            self.play_list.play_random()

    def on_mute_button(self):
        '''mute button notify and callback'''
        logging.info('Entered callback function in MainWindow: on_mute_button(self)')
        note = notify2.Notification("Mute", "Toggled")
        note.show()
        self.play_list.mute_volume()

    def on_play_pause(self):
        '''toggle notify and playback and pause callback'''
        logging.info('Entered callback function in MainWindow: on_play_pause(self)')
        note = notify2.Notification("Playback", "Toggled")
        note.show()
        self.play_list.play_pause()

    def on_vol_up(self):
        '''vol up callback'''
        logging.info('Entered callback function in MainWindow: on_vol_up(self)')
        self.play_list.volume_up()

    def on_vol_down(self):
        '''vol down callback'''
        logging.info('Entered function: on_vol_down(self)')
        self.play_list.volume_down()


def main():
    ''' The main function of the music player'''
    logging.info('Entered function: main()')
    app_name = "minimus"
 #   default_dict = {'path':default_path, 'salt', new_salt}
    the_config = tconfig.ConfigController(app_name, {})
    config_dict = the_config.get()
    the_cache = tcache.CacheController(app_name, config_dict['salt'])


    notify2.init('minimus')
    #'''It is a GUI so make an app window'''
    minimus_window = MainWindow(the_cache)
    #''' Here's our last chance to do stuff before the GUI Mainloop!'''
    minimus_window.mainloop()
    #'''When the app window closes we exit'''
    sys.exit(0)

if __name__ == "__main__":
    main()
