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

from tikka.adapters.network.indexer.indexer import NetworkIndexer
from tikka.domains.config import Config
from tikka.domains.currencies import Currencies
from tikka.domains.entities.constants import (
    INDEXERS_CURRENT_ENTRY_POINT_URL_PREFERENCES_KEY,
)
from tikka.domains.entities.events import IndexersEvent
from tikka.domains.entities.indexer import Indexer
from tikka.domains.events import EventDispatcher
from tikka.domains.preferences import Preferences
from tikka.interfaces.adapters.network.indexer.indexer import NetworkIndexerInterface
from tikka.interfaces.adapters.repository.indexers import IndexersRepositoryInterface


class Indexers:
    """
    Indexers domain class
    """

    CONFIG_INDEXERS_ENDPOINTS_KEYWORD = "squid"
    CONFIG_ONLINE_ENDPOINTS_KEYWORD = "online"

    def __init__(
        self,
        repository: IndexersRepositoryInterface,
        preferences: Preferences,
        network_indexer: NetworkIndexerInterface,
        config: Config,
        currencies: Currencies,
        event_dispatcher: EventDispatcher,
    ):
        """
        Init Indexers domain instance

        :param repository: EntryPointsRepositoryInterface instance
        :param preferences: Preferences domain instance
        :param network_indexer: Network adapter instance for handling indexers
        :param config: Config instance
        :param currencies: Currencies instance
        :param event_dispatcher: EventDispatcher instance
        """
        self.repository = repository
        self.preferences = preferences
        self.network_indexer = network_indexer
        self.config = config
        self.currencies = currencies
        self.event_dispatcher = event_dispatcher
        self._current_url = self.currencies.get_entry_point_urls()[
            self.CONFIG_INDEXERS_ENDPOINTS_KEYWORD
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
        for url in currency_endpoints[self.CONFIG_INDEXERS_ENDPOINTS_KEYWORD]:
            if url not in repository_urls:
                self.repository.add(Indexer(url))

        self._current_url = self.repository.list(0, 1)[0].url

        current_url_in_preferences = self.preferences.get(
            INDEXERS_CURRENT_ENTRY_POINT_URL_PREFERENCES_KEY
        )
        if (
            current_url_in_preferences is None
            or current_url_in_preferences not in self.repository.get_urls()
        ):
            self.preferences.set(
                INDEXERS_CURRENT_ENTRY_POINT_URL_PREFERENCES_KEY, self.get_current_url()
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
            online_url = currency_endpoints[self.CONFIG_ONLINE_ENDPOINTS_KEYWORD]
            try:
                with request.urlopen(online_url) as file:
                    online_endpoints = json.load(file)
            except JSONDecodeError as exception:
                logging.warning("error loading endpoints from %s", online_url)
                logging.exception(exception)
                online_endpoints = None

            if online_endpoints is not None:
                repository_urls = self.repository.get_urls()
                for url in online_endpoints[self.CONFIG_INDEXERS_ENDPOINTS_KEYWORD]:
                    if url not in repository_urls:
                        self.repository.add(Indexer(url))

    def network_fetch_current_indexer(self) -> None:
        """
        Update indexer from network

        :return:
        """
        current_indexer = self.repository.get(self.get_current_url())
        network_indexer = self.network_indexer.get()
        if network_indexer is None:
            return None

        if current_indexer is not None:
            # update only changing properties
            current_indexer.block = network_indexer.block

            self.repository.update(current_indexer)

        return None

    @staticmethod
    def network_test_and_get_indexer(url: str) -> Optional[Indexer]:
        """
        Try to open connection on url and return indexer if successful

        Then close connection

        :param url: Entry point url
        :return:
        """
        indexer = None

        network_indexer = NetworkIndexer()
        network_indexer.connection.connect(Indexer(url))
        if network_indexer.connection.is_connected():
            indexer = network_indexer.get()
        network_indexer.connection.disconnect()

        return indexer

    def set_current_url_randomly(self):
        """
        Shuffle indexers list randomly and connect to first available indexer

        :return:
        """
        indices = list(range(1, self.count()))
        random.shuffle(indices)
        for index in indices:
            url = self.list()[index].url
            # never choose localhost randomly...
            if "localhost" not in url:
                self.set_current_url(self.list()[index].url)
                if self.network_indexer.connection.is_connected():
                    break

    def add(self, indexer: Indexer) -> None:
        """
        Add indexer in repository

        :param indexer: Indexer instance
        :return:
        """
        self.repository.add(indexer)

        self.event_dispatcher.dispatch_event(
            IndexersEvent(IndexersEvent.EVENT_TYPE_LIST_CHANGED)
        )

    def get(self, url: str) -> Optional[Indexer]:
        """
        Get Indexer instance by url

        :param url: Url
        :return:
        """
        return self.repository.get(url)

    def update(self, indexer: Indexer) -> None:
        """
        Update indexer in repository

        :param indexer: Indexer instance
        :return:
        """
        self.repository.update(indexer)

        self.event_dispatcher.dispatch_event(
            IndexersEvent(IndexersEvent.EVENT_TYPE_LIST_CHANGED)
        )

    def list(self) -> List[Indexer]:
        """
        Return all Indexers from repository

        :return:
        """
        return self.repository.list()

    def count(self) -> int:
        """
        Return total indexers count

        :return:
        """
        return self.repository.count()

    def delete(self, url: str) -> None:
        """
        Delete Indexer by url

        :param url: Indexer url
        :return:
        """
        # do not delete default entry points from config
        if (
            url
            in self.currencies.get_entry_point_urls()[
                self.CONFIG_INDEXERS_ENDPOINTS_KEYWORD
            ]
        ):
            return

        self.repository.delete(url)
        # switch current entry point to first in list
        self.set_current_url(self.repository.list(0, 1)[0].url)
        # set new entry point in preferences
        self.preferences.set(
            INDEXERS_CURRENT_ENTRY_POINT_URL_PREFERENCES_KEY, self.get_current_url()
        )

        self.event_dispatcher.dispatch_event(
            IndexersEvent(IndexersEvent.EVENT_TYPE_LIST_CHANGED)
        )

    def delete_all(self) -> None:
        """
        Delete all Indexers in repository

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
            INDEXERS_CURRENT_ENTRY_POINT_URL_PREFERENCES_KEY,
            self._current_url,
        )
        # switch current connection
        self.network_indexer.connection.disconnect()
        indexer = self.get(self._current_url)
        if indexer is not None:
            self.network_indexer.connection.connect(indexer)
