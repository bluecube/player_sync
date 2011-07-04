#!/usr/bin/python3

import os
import os.path
import stat
import errno
import shutil
import logging
import argparse

class Synchronizer:
    def __init__(self, paths, source, dest):
        self._paths = dict(map(
            lambda x: (os.path.relpath(os.path.abspath(os.path.normpath(x.strip())), source), 0),
            paths))
        self._source = source
        self._dest = dest
        
    def negative_sync(self):
        """
        Delete files that aren't in the playlist.
        """
        for (root, dirs, files) in os.walk(self._dest, topdown=False, followlinks=True):
            for f in files:
                filename = os.path.join(root, f)
                
                if os.path.relpath(filename, self._dest) not in self._paths:
                    logging.debug('Removing file "{0}".'.format(filename))
                    os.unlink(filename)

            if not len(os.listdir(root)):
                logging.debug('Removing directory "{0}".'.format(root))
                os.rmdir(root)
        
    def positive_sync(self):
        """
        Ensure that all files in the playlist are on the target path.
        """
        for relpath in sorted(self._paths.keys()):
            source = os.path.join(self._source, relpath)
            dest = os.path.join(self._dest, relpath)
            self._positive_sync_one(source, dest, relpath)

    def _positive_sync_one(self, source, dest, relpath):
        source_stat = os.stat(source)

        if not stat.S_ISREG(source_stat.st_mode):
            logging.warning('"{0}" is not a regular file.'.format(relpath))
            return
            
        try:
            dest_stat = os.stat(dest)
        except OSError as e:
            dest_stat = False
    
        if dest_stat and \
            dest_stat.st_size == source_stat.st_size and \
            dest_stat.st_mtime >= source_stat.st_mtime:
            logging.debug('Skipping "{0}".'.format(relpath))
            return

        logging.debug('Copying "{0}".'.format(relpath))

        try:
            os.makedirs(os.path.split(dest)[0])
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        shutil.copyfile(source, dest)


def main():
    parser = argparse.ArgumentParser(description='Synchronize a directory with a playlist.')
    parser.add_argument('--source', required=True,
        help='Source directory with the music.')
    parser.add_argument('--dest', required=True,
        help='Target directory.')
    parser.add_argument('--playlist', required=True, type=argparse.FileType(),
        help='Playlist specifying which files from source should appear in dest.')
    parser.add_argument('--no-delete', action='store_true',
        help="Don't delete files that shouldn't be in the playlist.")
    parser.add_argument('--silent', action='store_const', const=logging.INFO,
        default=logging.DEBUG, help="Don't write too much.")
    args = parser.parse_args()

    logging.basicConfig(level=args.silent, format='%(asctime)s %(message)s', datefmt='%x %X')

    logging.info('Loading playlist.')

    sync = Synchronizer(args.playlist, args.source, args.dest)

    if not args.no_delete:
        logging.info('Deleting unwanted files.')
        sync.negative_sync()

    logging.info('Copying files')
    sync.positive_sync()

    logging.info('Done.')


if __name__ == '__main__':
    main()
