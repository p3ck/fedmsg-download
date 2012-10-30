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

import logging
log = logging.getLogger("moksha.hub")


class RsyncConsumer(FedmsgConsumer):
    topic = "org.fedoraproject.*"
    config_key = 'fedmsg-download.consumer.enabled'

    def __init__(self, hub):
        self.hub = hub
        self.DBSession = None

        settings = hub.config.get('download')
        self.local_path = settings.get('local_path')
        self.rsync_base = settings.get('rsync_base')
        self.rsync_opts = settings.get('rsync_opts')
        self.delete_old = settings.get('delete_old')
        self.import_command = settings.get('import_command')
        self.regex_topic = re.compile(settings.get('filter_topic', ''))
        if not self.local_path:
            raise Exception('local_path not configured!')

        return super(RsyncConsumer, self).__init__(hub)

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
            if branch:
                # sync it down...
                try:
                    download = Downloader(os.path.join(self.rsync_base, branch), branch)
                except Exception, e:
                    log.critical(e)
                    return 1
                return download.sync_it_down(self.local_path,
                                             self.rsync_opts,
                                             self.delete_old,
                                             self.import_command)
