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
from fedmsg.commands import BaseCommand

from fedmsg_download.consumer import RsyncConsumer

class DownloadCommand(BaseCommand):
    """ Watch the compose topic for rsync.complete messages

    This is highly configurable by way of the :term:`download` config value.
    """

    name = "fedmsg-download"
    extra_args = [
        (['--verbose'], {
            'dest': 'verbose',
            'action': 'store_true',
            'default': False,
            'help': "Verbose logging.",
        }),
    ]
    daemonizable = True

    def run(self):
        # Do just like in fedmsg.commands.hub and mangle fedmsg-config.py to work
        # with moksha's expected configuration.
        moksha_options = dict(
            zmq_subscribe_endpoints=','.join(
                ','.join(bunch) for bunch in self.config['endpoints'].values()
            ),
        )
        self.config.update(moksha_options)

        self.config[RsyncConsumer.config_key] = True

        from moksha.hub import main
        main(options=self.config, consumers=[RsyncConsumer])

def download():
    command = DownloadCommand()
    command.execute()
