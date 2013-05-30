# -*- coding: utf-8 -*-
#
# Copyright © 2013 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public
# License as published by the Free Software Foundation; either version
# 2 of the License (GPLv2) or (at your option) any later version.
# There is NO WARRANTY for this software, express or implied,
# including the implied warranties of MERCHANTABILITY,
# NON-INFRINGEMENT, or FITNESS FOR A PARTICULAR PURPOSE. You should
# have received a copy of GPLv2 along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.

from gettext import gettext as _

from pulp.client.commands.options import OPTION_REPO_ID
from pulp.client.extensions.extensions import PulpCliOption, PulpCliFlag, PulpCliCommand
from pulp.client import validators

# -- constants ----------------------------------------------------------------

# Command descriptions
DESC_SYNC_HISTORY = _('shows sync history')
DESC_PUBLISH_HISTORY = _('shows publish history')

# Options
DESC_LIMIT = _('specify how many events to display')
OPTION_LIMIT = PulpCliOption('--limit', DESC_LIMIT, required=False,
                             validate_func=validators.positive_int_validator)
DEFAULT_LIMIT = 5
DESC_DISTRIBUTOR_ID = _('the distributor id')
OPTION_DISTRIBUTOR_ID = PulpCliOption('--distributor-id', DESC_DISTRIBUTOR_ID, required=True,
                                      validate_func=validators.id_validator)

# Flags
DESC_DETAILS = _('increase information shown')
FLAG_DETAILS = PulpCliFlag('--details', DESC_DETAILS, aliases='-d')

# -- commands -----------------------------------------------------------------


class SyncHistoryCommand(PulpCliCommand):
    """
    Displays the sync history of a given repository
    """

    def __init__(self, context, name='sync', description=DESC_SYNC_HISTORY, method=None):
        # The context is used to access the server and prompt.
        self.context = context

        if method is None:
            method = self.run

        super(SyncHistoryCommand, self).__init__(name, description, method)

        self.add_option(OPTION_REPO_ID)
        # Option to limit the number of history objects shown
        self.add_option(OPTION_LIMIT)
        # Flag to display more information about the syncs
        self.add_flag(FLAG_DETAILS)

    # TODO: Figure out where to apply the limit
    def run(self, **kwargs):
        # Collect input
        details = kwargs[FLAG_DETAILS.keyword]
        repo_id = kwargs[OPTION_REPO_ID.keyword]
        limit = DEFAULT_LIMIT
        if kwargs[OPTION_LIMIT.keyword] is not None:
            limit = int(kwargs[OPTION_LIMIT.keyword])

        # Request the sync history from the server
        result = self.context.server.repo_history.sync_history(repo_id)
        # Use limit to only show the last n items.
        index_start = len(result.response_body) - limit
        if index_start < 0:
            # In this case just print the whole list
            index_start = 0
        result = result.response_body[index_start:]

        # Render results
        filter = ['result', 'summary', 'repo_id', 'started', 'completed', 'added_count', 'removed_count',
                  'updated_count']
        print_order = ['repo_id', 'result', 'started', 'completed', 'added_count', 'removed_count',
                       'updated_count', 'summary']
        if details is True:
            filter.append('details')
            print_order.append('details')

        title = _('Sync History')
        self.context.prompt.render_title(title)
        self.context.prompt.render_document_list(result[:], filters=filter, order=print_order)


class PublishHistoryCommand(PulpCliCommand):
    """
    Displays the publish history of a given repository and publisher
    """

    # TODO: Sort out whether or not a details flag is needed
    def __init__(self, context, name='publish', description=DESC_PUBLISH_HISTORY, method=None):
        # The context is used to access the server and prompt.
        self.context = context

        if method is None:
            method = self.run

        super(PublishHistoryCommand, self).__init__(name, description, method)

        self.add_option(OPTION_REPO_ID)
        self.add_option(OPTION_DISTRIBUTOR_ID)
        self.add_option(OPTION_LIMIT)
        self.add_flag(FLAG_DETAILS)

    def run(self, **kwargs):
        # Collect input
        details = kwargs[FLAG_DETAILS.keyword]
        distributor_id = kwargs[OPTION_DISTRIBUTOR_ID.keyword]
        repo_id = kwargs[OPTION_REPO_ID.keyword]
        limit = DEFAULT_LIMIT
        if kwargs[OPTION_LIMIT.keyword] is not None:
            limit = int(kwargs[OPTION_LIMIT.keyword])

        # Request the publish history from the server
        result = self.context.server.repo_history.publish_history(repo_id, distributor_id)
        # Use limit to only show the last n items.
        index_start = len(result.response_body) - limit
        if index_start < 0:
            # In this case just print the whole list
            index_start = 0
        result = result.response_body[index_start:]

        # Render results
        filter = ['completed', 'distributor_id', 'repo_id', 'result', 'started', 'summary']
        print_order = ['repo_id', 'distributor_id', 'result', 'started', 'completed', 'summary']
        if details is True:
            filter.append('details')
            print_order.append('details')

        title = _('Publish History')
        self.context.prompt.render_title(title)
        self.context.prompt.render_document_list(result, filters=filter, order=print_order)