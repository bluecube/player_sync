#!/bin/sh

# Wrapper around synchronizer.py.
# Mounts my mp3 player, synchronizes from a MPD playlist and unmounts.

mount /mnt/player || exit
./synchronizer.py --source /big/music --dest /mnt/player/MUSIC --playlist /var/lib/mpd/playlists/Player.m3u "$@"
echo "Unmounting."
umount /mnt/player
