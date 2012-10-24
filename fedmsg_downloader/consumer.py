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
from fedmsg.consumers import FedmsgConsumer

import logging
log = logging.getLogger("moksha.hub")


class RsyncConsumer(FedmsgConsumer):
    topic = "org.fedoraproject.compose"
    config_key = 'fedmsg-downloader.consumer.enabled'

    def __init__(self, hub):
        self.hub = hub
        self.DBSession = None

        settings = hub.config.get('download')
        self.regex_topic = re.compile(settings.get('filter_topic', ''))

        return super(RsyncConsumer, self).__init__(hub)

    def consume(self, msg):
        """ Look for topic messages that match the config
            branched.rsync.complete
            rawhide.rsync.complete
        """
        log.info("Duhhhh... got: %r" % msg)
        topic = msg['body']['topic']
        if self.regex_topic.search(topic):
            branch = msg['body']['msg'].get('branch', None)
            log.info("branch: %s" % branch)
            # sync it down...
