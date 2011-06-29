import os
from boto import connect_s3
import zc.buildout
import setuptools.archive_util
import gzip
from sys import stdout



def unpack_gzfile(filename, extract_dir,
                  progress_filter=setuptools.archive_util.default_filter):
    """Unpack *.gz `filename` to `extract_dir`

    Raises ``UnrecognizedFormat`` if `filename` is not a gzip file (as
    determined by ``gzip.open()``).  See
    ``setuptools.archive_util.unpack_archive()`` for an explanation
    of the `progress_filter` argument.
    """
    try:
        gz_fd = gzip.open(filename, "r")
        with open(os.path.join(extract_dir,
                               os.path.basename(filename)[0:-3]), "w") as _fd:
            _fd.write(gz_fd.read())
        gz_fd.close()
    except IOError: #Ugh, gzip raised an IOERROR :(
        raise UnrecognizedFormat(
            "%s is not a compressed or uncompressed tar file" % (filename,))
    return True

DRIVERS = list(setuptools.archive_util.extraction_drivers) + [unpack_gzfile]

def _progress_callback(current, total):
    remain = 100 * float(total - current) / total
    done = 100 - remain
    # 60 Char len :
    nprog = int((current * 60) / float(total))
    if nprog:
        prog = "[" + (nprog - 1) * "=" + '>' + (60 - nprog) * ' ' + "]" + "%0.1f%%" % done
    else:
        prog = "[" + (60) * ' ' + "]" + "%s%%" % done

    msg = '%s\r' % prog if nprog != 60 else '%s\r\n' % prog
    stdout.write(msg)
    stdout.flush()

class Recipe(object):
    """
    This recipe is used by zc.buildout
    """

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options

        self.bucket = options.get('bucket_name', None)
        self.files = options.get('files', None)
        self.destination = options.get('destination', None)
        self.ec2_access_key = options.get('access_key',
                                          os.environ.get("EC2_ACCESS_KEY", None))
        self.ec2_secret_key = options.get('secret_key',
                                          os.environ.get("EC2_SECRET_KEY", None))

        self.on_install = options.get('on_install', True)
        self.on_update = options.get('on_update', False)

    def install(self):
        """installer"""
        if self.on_install:
            self._download(self.files)
        return tuple()

    def update(self):
        """updater"""
        if self.on_update:
            self._download(self.files)
        return tuple()

    def _download(self, files):
        """
        Download from bucket a list of files
        """
        if not self.ec2_access_key or not self.ec2_secret_key:
            raise zc.buildout.UserError("No EC2_CREDENTIALS Set")
        if not self.destination:
            raise zc.buildout.UserError("No Destination set")
        if not self.bucket:
            raise zc.buildout.UserError("No Bucket set")

        s3 = connect_s3(self.ec2_access_key, self.ec2_secret_key)
        bucket = s3.get_bucket(self.bucket)
        for key in bucket.get_all_keys():
            if key.name in files:
                if not os.path.isdir(self.destination):
                    os.mkdir(self.destination)
                file_name = os.path.join(self.destination, key.name)
                with open(file_name, 'w') as _f:
                    print "Downloading %s" % key.name
                    key.get_file(_f, cb=_progress_callback)
                setuptools.archive_util.unpack_archive(file_name,
                                                       self.destination,
                                                       drivers=DRIVERS)
