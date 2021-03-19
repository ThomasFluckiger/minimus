            minimus is a minimalistic music player and art project


minimus is written in Python utilizing libvlc for playback of media,
and is licensed as GPL. I don't know what imported bits are licensed as.

It is designed to allow playback of a particular track only once.
This is accomplished by taking and salting a hash and cache file.

To be clear, it does not attempt any sort of DRM, simply deleting the cache
or changing the salt in the configuration file is sufficient.

It is an art project from a COVID-19 underemployed "Live Events Production Professional",
and a potential resume CV of sorts while I teach myself Python.

minimus utilizes libvlc for playback, eyed3 to read tags, and notify2
for notifications; hashlib, tkinter, and magic are core components. 


As this project was a learning excercise the code quality roughly
matches when it was written. Currently, things are being refactored to be more modular
to allow for easier maintenance and addition of features.

a full featured media player, it is not, nor is it really intended to be.

Some fairly core changes need to happen, as the early core parts were 
written when I had much less experience and things need to be more decoupled.

v0.1, and push to github represent that minimus while far from polished, 
has succeeded in the minimal artistic aims in creating it, being that it is complete
enough to load files, tries to get some tags, and not play it if the hash exists.

