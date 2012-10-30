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
# Authors:  Ralph Bean <rbean@redhat.com>, Bill Peck <bpeck@redhat.com>
#
config = dict(
    download=
        dict(
            # You must configure local_path in order for this to work!
            # This is where the downloads will be mirrored to.
            local_path=None,
            rsync_opts='--exclude debug --exclude source',
            #import_command='beaker-import http://FQDN/distros/Fedora/development/\%(tree)s',
            rsync_base='rsync://dl.fedoraproject.org/fedora-linux-development',
            delete_old=True,
            # The following topics will trigger an rsync
            # If you only want branched then use
            # filter_topics='compose\.branched\.rsync\.complete'
            filter_topic='compose\..*\.rsync\.complete',
        ),
)
