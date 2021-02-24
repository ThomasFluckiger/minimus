minimus is a minimalistic music player and art project
It is written in Python utilizing libvlc for playback of media


It is designed to allow playback of a particular track only once.
This is accomplished by taking and salting a hash and cache file.

minimus utilizes libvlc for playback, eyed3 to read tags, and notify2
for notifications

hashlib, tkinter, and magic are core components. 

As this project was a learning excercise the code quality roughly
matches when it was written. a full featured media player, it is not.

Some fairly core changes need to happen, as the early core parts were 
written when I had much less experience and things need to be more decoupled.

v0.1, and push to github represent that minimus while far from polished, 
has succeeded in the minimal artistic aims in creating it, being that it is complete
enough to load files, tries to get some tags, and not play it if the hash exists.

