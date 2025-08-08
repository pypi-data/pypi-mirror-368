# Copyright 2021 Vincent Texier <vit@free.fr>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import json
import logging
import random
from json import JSONDecodeError
from typing import List, Optional
from urllib import request

from tikka.adapters.network.node.node import NetworkNode
from tikka.domains.config import Config
from tikka.domains.currencies import Currencies
from tikka.domains.entities.constants import (
    NODES_CURRENT_ENTRY_POINT_URL_PREFERENCES_KEY,
)
from tikka.domains.entities.events import NodesEvent
from tikka.domains.entities.node import Node
from tikka.domains.events import EventDispatcher
from tikka.domains.preferences import Preferences
from tikka.interfaces.adapters.network.node.node import NetworkNodeInterface
from tikka.interfaces.adapters.repository.nodes import NodesRepositoryInterface


class Nodes:
    """
    Nodes domain class
    """

    CONFIG_NODES_ENDPOINTS_KEYWORD = "rpc"
    CONFIG_ONLINE_ENDPOINTS_KEYWORD = "online"

    def __init__(
        self,
        repository: NodesRepositoryInterface,
        preferences: Preferences,
        network_node: NetworkNodeInterface,
        config: Config,
        currencies: Currencies,
        event_dispatcher: EventDispatcher,
    ):
        """
        Init Nodes domain instance

        :param repository: EntryPointsRepositoryInterface instance
        :param preferences: Preferences domain instance
        :param network_node: NetworkNodeInterface adapter instance for handling nodes
        :param config: Config instance
        :param currencies: Currencies instance
        :param event_dispatcher: EventDispatcher instance
        """
        self.repository = repository
        self.preferences = preferences
        self.network_node = network_node
        self.config = config
        self.currencies = currencies
        self.event_dispatcher = event_dispatcher
        self._current_url = self.currencies.get_entry_point_urls()[
            self.CONFIG_NODES_ENDPOINTS_KEYWORD
        ][0]

        self.init_repository()

    def init_repository(self):
        """
        Init repository with default entry points from config

        :return:
        """
        repository_urls = self.repository.get_urls()
        currency_endpoints = self.currencies.get_entry_point_urls()

        # init repository with current currency entry point urls
        for url in currency_endpoints[self.CONFIG_NODES_ENDPOINTS_KEYWORD]:
            if url not in repository_urls:
                self.repository.add(Node(url))

        self._current_url = self.repository.list(0, 1)[0].url

        current_url_in_preferences = self.preferences.get(
            NODES_CURRENT_ENTRY_POINT_URL_PREFERENCES_KEY
        )
        if (
            current_url_in_preferences is None
            or current_url_in_preferences not in self.repository.get_urls()
        ):
            self.preferences.set(
                NODES_CURRENT_ENTRY_POINT_URL_PREFERENCES_KEY, self.get_current_url()
            )
        else:
            self._current_url = current_url_in_preferences

    def network_fetch_endpoints(self):
        """
        Add Indexers in repository from online list of endpoints

        :return:
        """
        currency_endpoints = self.currencies.get_entry_point_urls()

        # fetch endpoints from online json file
        if currency_endpoints[self.CONFIG_ONLINE_ENDPOINTS_KEYWORD]:
            try:
                with request.urlopen(
                    currency_endpoints[self.CONFIG_ONLINE_ENDPOINTS_KEYWORD]
                ) as file:
                    online_endpoints = json.load(file)
            except JSONDecodeError as exception:
                logging.warning(
                    "error loading endpoints from %s",
                    currency_endpoints[self.CONFIG_ONLINE_ENDPOINTS_KEYWORD],
                )
                logging.exception(exception)
                online_endpoints = None

            if online_endpoints is not None:
                repository_urls = self.repository.get_urls()
                for url in online_endpoints[self.CONFIG_NODES_ENDPOINTS_KEYWORD]:
                    if url not in repository_urls:
                        self.repository.add(Node(url))

    def network_fetch_current_node(self) -> None:
        """
        Update node from network

        :return:
        """
        current_node = self.repository.get(self.get_current_url())
        network_node = self.network_node.get()
        if network_node is None:
            return None

        if current_node is not None:
            # update only changing properties
            current_node.block = network_node.block
            current_node.peer_id = network_node.peer_id
            current_node.software = network_node.software
            current_node.software_version = network_node.software_version
            current_node.epoch_index = network_node.epoch_index
            current_node.unsafe_api_exposed = network_node.unsafe_api_exposed

            self.repository.update(current_node)

        return None

    @staticmethod
    def network_get_node_adapter(url: str) -> Optional[NetworkNode]:
        """
        Try to open connection on url and return connected NetworkNode instance if successful

        :param url: Entry point url
        :return:
        """
        network_node = NetworkNode()
        network_node.connection.connect(Node(url))
        if network_node.connection.is_connected():
            return network_node

        return None

    def set_current_url_randomly(self):
        """
        Shuffle node list randomly and connect to first available node

        :return:
        """
        indices = list(range(1, self.count()))
        random.shuffle(indices)
        for index in indices:
            url = self.list()[index].url
            # never choose localhost randomly...
            if "localhost" not in url:
                self.set_current_url(self.list()[index].url)
                if self.network_node.connection.is_connected():
                    break

    def add(self, node: Node) -> None:
        """
        Add node in repository

        :param node: Node instance
        :return:
        """
        self.repository.add(node)

        self.event_dispatcher.dispatch_event(
            NodesEvent(NodesEvent.EVENT_TYPE_LIST_CHANGED)
        )

    def get(self, url: str) -> Optional[Node]:
        """
        Get Node instance by url

        :param url: Url
        :return:
        """
        return self.repository.get(url)

    def update(self, node: Node) -> None:
        """
        Update Node in repository

        :param node: Node instance
        :return:
        """
        self.repository.update(node)

        self.event_dispatcher.dispatch_event(
            NodesEvent(NodesEvent.EVENT_TYPE_LIST_CHANGED)
        )

    def list(self) -> List[Node]:
        """
        Return all Nodes from repository

        :return:
        """
        return self.repository.list()

    def count(self) -> int:
        """
        Return total node count

        :return:
        """
        return self.repository.count()

    def delete(self, url: str):
        """
        Delete Node by url

        :param url: Node url
        :return:
        """
        # do not delete default entry points from config
        if url in self.currencies.get_entry_point_urls()["rpc"]:
            return

        self.repository.delete(url)
        # switch current entry point to first in list
        self.set_current_url(self.repository.list(0, 1)[0].url)
        # set new entry point in preferences
        self.preferences.set(
            NODES_CURRENT_ENTRY_POINT_URL_PREFERENCES_KEY, self.get_current_url()
        )

        self.event_dispatcher.dispatch_event(
            NodesEvent(NodesEvent.EVENT_TYPE_LIST_CHANGED)
        )

    def delete_all(self) -> None:
        """
        Delete all nodes in repository

        :return:
        """
        self.repository.delete_all()

    def get_current_url(self) -> str:
        """
        Return current entry point url

        :return:
        """
        return self._current_url

    def set_current_url(self, url: str) -> None:
        """
        Set current entry point url

        :return:
        """
        self._current_url = url
        # update preference
        self.preferences.set(
            NODES_CURRENT_ENTRY_POINT_URL_PREFERENCES_KEY,
            self._current_url,
        )
        # switch current connection
        self.network_node.connection.disconnect()
        node = self.get(self._current_url)
        if node is not None:
            self.network_node.connection.connect(node)
