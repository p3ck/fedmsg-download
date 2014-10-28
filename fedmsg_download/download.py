import os, os.path
import sys
from optparse import OptionParser
import logging
import ConfigParser
import tempfile
import pexpect
import shutil
import datetime

log = logging.getLogger(__name__)

def run_command(commandline):
    if log.isEnabledFor(logging.DEBUG):
        logfile=sys.stdout
    else:
        logfile = None
    (command_output, exitstatus) = pexpect.run(commandline, withexitstatus=1,
                                       logfile=logfile, timeout=None)
    return command_output, exitstatus

class DownloadException(Exception):

   def __init__(self, value, *args):
       self.value = value % args

   def __str__(self):
       return repr(self.value)


class DX(DownloadException):
   pass


class Downloader(object):
    def __init__(self, rsync_url=None, branch=None, req_compose=True):
        self.rsync = RSync(rsync_url)
        self.branch = branch
        self.parser = CParser()
        self.req_compose = req_compose
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

    def sync_it_down(self, local_dir, rsync_opts, delete_old, command):
        today = str(datetime.date.today())
        product_name = self.parser.get('product','name', "%s-%s" %(self.branch, today))

        # Default options
        opts = '--archive --verbose --delete'
        # Add in rsync_opts
        if rsync_opts:
            opts = '%s %s' % (opts, rsync_opts)
        # read 'latest' symlink from local_dir
        latest = os.path.realpath('%s/latest-%s' % (local_dir, self.branch))
        # Add in link-dest if symlink points to valid dir
        if os.path.isdir(latest):
            opts = opts + ' --link-dest=%s' % latest

        local_path = os.path.join(local_dir, product_name)
        # compare local and remote
        if os.path.realpath(local_path) == latest:
            log.info('Already have %s' % local_path)
            return 0

        # Get it.
        log.info("Downloading: %s"  % product_name)
        self.rsync.get('', local_path, opts)

        # update symlink to newly downloaded
        if os.path.exists(os.path.join(local_dir,'latest-%s' % self.branch)):
            os.unlink(os.path.join(local_dir,'latest-%s' % self.branch))
        os.symlink(product_name, '%s/latest-%s' % (local_dir, self.branch))

        # If delete_old is set remove previous tree
        if os.path.isdir(latest) and delete_old:
            # The variable latest actually holds the old dir
            shutil.rmtree('%s' % latest)

        # If command is not None then run it with product_name
        if command:
            commandline = command % dict(tree = product_name)
            log.debug(commandline)
            stdout, rc = run_command(commandline)
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
        stdout, rc = run_command(commandline)
        if rc != 0:
            raise DX('Unable to rsync %s -> %s' % (remote_path, local_filename))
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
