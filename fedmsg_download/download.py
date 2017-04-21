import os, os.path
import sys
from optparse import OptionParser
import logging
import ConfigParser
import tempfile
import shutil
import datetime
import time
from subprocess import Popen, PIPE
import select

log = logging.getLogger(__name__)

def _mkdir(newdir):
    """works the way a good mkdir should :)
        - already exists, silently complete
        - regular file in the way, raise an exception
        - parent directory(ies) does not exist, make them as well
    """
    if os.path.isdir(newdir):
        pass
    elif os.path.isfile(newdir):
        raise OSError("a file with the same name as the desired " \
                      "dir, '%s', already exists." % newdir)
    else:
        head, tail = os.path.split(newdir)
        if head and not os.path.isdir(head):
            _mkdir(head)
        #print "_mkdir %s" % repr(newdir)
        if tail:
            os.mkdir(newdir)

def run_command(commandline):
    command = commandline.split()
    proc = Popen(command, stdout=PIPE, stderr=PIPE)
    input = [proc.stdout, proc.stderr]
    running = 1
    while running:
        inputready, outputready, exceptready = select.select(input,[],[],5)
        for s in inputready:
            for line in s:
               if s == proc.stderr:
                   log.error("run_command: %s" %  line)
               else:
                   log.info("run_command: %s" %  line)
        if proc.poll() is not None:
            break
    return proc.returncode

class DownloadException(Exception):

   def __init__(self, value, *args):
       self.value = value % args

   def __str__(self):
       return repr(self.value)


class DX(DownloadException):
   pass


class Downloader(object):
    def __init__(self, rsync_url=None, branch=None,
                 req_compose=True, ignore_name=False,
                 local_dir=None, rsync_opts=None,
                 delete_old=False, compose_dir=None,
                 command=None):
        self.rsync = RSync(rsync_url)
        self.branch = branch
        self.parser = CParser()
        self.req_compose = req_compose
        self.ignore_name = ignore_name
        self.local_dir = local_dir
        self.rsync_opts = rsync_opts
        self.delete_old = delete_old
        self.compose_dir = compose_dir
        self.command = command
        try:
            tmp_file = tempfile.mktemp()
            self.rsync.get(self.parser.infofile, tmp_file)
            self.parser.parse(tmp_file)
        except DX, e:
            if self.req_compose:
                raise
            else:
                pass
        finally:
            if os.path.isfile(tmp_file):
                os.unlink(tmp_file)

    def sync_it_down(self):
        product_name = "%s-%s" % ( self.branch, str(datetime.date.today()))
        if not self.ignore_name:
            product_name = self.parser.get('product','name', product_name)

        # Default options
        opts = '--archive --verbose --delete'
        # Add in rsync_opts
        if self.rsync_opts:
            opts = '%s %s' % (opts, self.rsync_opts)
        # read 'latest' symlink from local_dir
        latest = os.path.realpath('%s/latest-%s' % (self.local_dir, self.branch))
        # Add in link-dest if symlink points to valid dir
        if os.path.isdir(latest):
            opts = opts + ' --link-dest=%s' % latest

        local_path = os.path.join(self.local_dir, product_name)
        # compare local and remote
        if os.path.realpath(local_path) == latest:
            log.info('Already have %s' % local_path)
            return 0

        # Create dir if needed
        _mkdir(local_path)

        # Get it.
        log.info("Downloading: %s"  % product_name)
        self.rsync.get('', local_path, opts)

        # update symlink to newly downloaded
        if os.path.exists(os.path.join(self.local_dir,'latest-%s' % self.branch)):
            os.unlink(os.path.join(self.local_dir,'latest-%s' % self.branch))
        os.symlink(product_name, '%s/latest-%s' % (self.local_dir, self.branch))

        # If delete_old is set remove previous tree
        if os.path.isdir(latest) and self.delete_old:
            # The variable latest actually holds the old dir
            shutil.rmtree('%s' % latest)

        # If command is not None then run it with product_name
        if self.command:
            rel_path = "%s/%s" % (self.compose_dir, product_name)
            commandline = self.command % dict(tree = rel_path)
            log.debug(commandline)
            rc = run_command(commandline)
            if rc != 0:
                raise DX('Unable to run command %s' % commandline)
        return 0


class RSync(object):
    def __init__(self, rsync_url):
        self.rsync_url = rsync_url
        self.cmd = "rsync"

    def get(self, remote_filename, local_filename, opts=''):
        """Use rsync to get a remote file"""
        remote_path = os.path.join(self.rsync_url, remote_filename)
        commandline = "%s %s %s %s" % (self.cmd,
                                       opts,
                                       remote_path,
                                       local_filename)
        log.debug(commandline)
        # Try the rsync twice to get around horrible
        # issues on server where files sometimes go away
        for x in range(0,5):
            loop = 0
            while loop < 1800:
                loop += 1
                rc = run_command(commandline)
                # rsync rc 5  : Error starting client-server protocol
                # This usually is because the server is too busy
                if rc != 5:
                    break
                else:
                    time.sleep(2)
            if rc == 0:
                break
            log.debug("Retry: %s" % x)
        if rc != 0:
            raise DX('RC:%s Unable to rsync %s -> %s' %
                    (rc, remote_path, local_filename))
        return rc


class Parser(object):
    def __init__(self, rsync_url=None):
        self.parser = None

    def get(self, section, key, default=None):
        if self.parser:
            try:
                default = self.parser.get(section, key)
            except (ConfigParser.NoSectionError, ConfigParser.NoOptionError), e:
                if default is None:
                    raise
        return default

    def parse(self, filename):
        try:
            self.parser = ConfigParser.ConfigParser()
            self.parser.read(filename)
        except ConfigParser.MissingSectionHeaderError, e:
            raise DX('%s/%s is not parsable: %s' % (filename,
                                                    self.infofile,
                                                    e))
        return True


class CParser(Parser):
    infofile = '.composeinfo'
