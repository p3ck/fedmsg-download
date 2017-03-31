# This file is part of fedmsg-downloader.
# Copyright (C) 2012 Red Hat, Inc.
#
# fedmsg-downloader is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# fedmsg-downloader is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with fedmsg; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#
# Authors:  Bill Peck <bpeck@redhat.com>
#
import fedmsg
import re
import os
from fedmsg.consumers import FedmsgConsumer
from fedmsg_download.download import Downloader
from threading import Thread
from Queue import Queue

import logging
log = logging.getLogger(__name__)

def download_thread(queue):
    while True:
        download = queue.get()
        try:
            download.sync_it_down()
        except Exception, e:
            log.critical(e)
        queue.task_done()

class RsyncConsumer(FedmsgConsumer):
    topic = "org.fedoraproject.*"
    config_key = 'fedmsg-download.consumer.enabled'
    rsync_queue = Queue()

    def __init__(self, hub):
        settings = hub.config.get('download')
        self.local_path = settings.get('local_path')
        self.rsync_base = settings.get('rsync_base')
        self.compose_dirs = settings.get('compose_dirs')
        self.rsync_opts = settings.get('rsync_opts')
        self.delete_old = settings.get('delete_old')
        self.req_compose = settings.get('req_compose', True)
        self.ignore_name = settings.get('ignore_name', False)
        self.import_command = settings.get('import_command')
        self.regex_topic = re.compile(settings.get('filter_topic', ''))
        if not self.local_path:
            raise Exception('local_path not configured!')

        worker = Thread(target=download_thread, args=(self.rsync_queue,))
        worker.setDaemon(True)
        worker.start()

        super(RsyncConsumer, self).__init__(hub)

    def consume(self, msg):
        """ Look for topic messages that match the config
            branched.rsync.complete
            rawhide.rsync.complete
        """
        topic, body = msg.get('topic'), msg.get('body')
        log.debug('topic=%s' % topic)
        if self.regex_topic.search(topic) and 'msg' in body:
            branch = body['msg'].get('branch', None)
            log.info("Rsync Complete for branch: %s" % branch)
            if branch and self.compose_dirs:
                # sync it down...
                for compose_dir in self.compose_dirs:
                    rsync_base = "%s/%s" % (self.rsync_base,
                                            self.compose_dirs[compose_dir])
                    local_path = "%s/%s" % (self.local_path,
                                            compose_dir)
                    try:
                        download = Downloader(os.path.join(rsync_base, branch),
                                              branch,
                                              self.req_compose,
                                              self.ignore_name,
                                              local_path,
                                              self.rsync_opts,
                                              self.delete_old,
                                              self.import_command)
                    except Exception, e:
                        log.critical(e)
                        return 1
                    self.rsync_queue.put(download)
