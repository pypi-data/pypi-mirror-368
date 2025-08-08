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

import gettext
import json
import logging
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from tikka.adapters.network.network import Network
from tikka.adapters.repository.repository import Repository
from tikka.domains.accounts import Accounts
from tikka.domains.amounts import Amounts
from tikka.domains.authorities import Authorities
from tikka.domains.categories import Categories
from tikka.domains.config import Config
from tikka.domains.connections import Connections
from tikka.domains.currencies import Currencies
from tikka.domains.entities.account import Account
from tikka.domains.entities.category import Category
from tikka.domains.entities.constants import DATABASE_FILE_EXTENSION, LOCALES_PATH
from tikka.domains.entities.events import CurrencyEvent
from tikka.domains.entities.indexer import Indexer
from tikka.domains.entities.node import Node
from tikka.domains.entities.password import Password
from tikka.domains.entities.wallet import Wallet
from tikka.domains.events import EventDispatcher
from tikka.domains.identities import Identities
from tikka.domains.indexers import Indexers
from tikka.domains.nodes import Nodes
from tikka.domains.passwords import Passwords
from tikka.domains.preferences import Preferences
from tikka.domains.smiths import Smiths
from tikka.domains.technical_committee import TechnicalCommittee
from tikka.domains.transfers import Transfers
from tikka.domains.vaults import Vaults
from tikka.domains.wallets import Wallets
from tikka.interfaces.adapters.network.node.currency import NodeCurrencyException


class Application:
    """
    Application class
    """

    def __init__(self, data_path: Path):
        """
        Init application

        :param data_path: Path instance of application data folder
        """

        # set data path
        self.data_path = data_path

        # dependency injection
        # init event dispatcher
        self.event_dispatcher = EventDispatcher()

        # repository adapter
        self.repository = Repository(str(self.data_path))

        # init config domain
        self.config = Config(self.repository.config)

        # if supported currencies has changed and config use an unknown currency...
        if (
            self.config.get(Config.CURRENCY_KEY)
            not in self.repository.currencies.code_names()
        ):
            # set current currency to first currency by default
            self.config.set(
                Config.CURRENCY_KEY, self.repository.currencies.code_names()[0]
            )

        # database adapter
        currency_db_file_uri = (
            self.data_path.expanduser()
            .joinpath(self.config.get(Config.CURRENCY_KEY) + DATABASE_FILE_EXTENSION)
            .as_uri()
        )
        self.repository.db_client.connect(currency_db_file_uri)

        # network adapter
        self.network = Network()

        # init translation
        self.translator = self.init_i18n()

        # init domains
        self.connections = Connections(self.network, self.event_dispatcher)
        self.preferences = Preferences(self.repository.preferences)
        self.currencies = Currencies(
            self.repository.currencies,
            self.repository.currency,
            self.network.node.currency,
            self.config.get(Config.CURRENCY_KEY),
        )
        self.passwords = Passwords(self.repository.passwords)
        self.wallets = Wallets(self.repository.wallets, self.currencies)
        self.transfers = Transfers(
            self.wallets,
            self.repository.transfers,
            self.currencies,
            self.network.node.transfers,
            self.network.indexer.transfers,
            self.event_dispatcher,
        )
        self.identities = Identities(
            self.repository.identities,
            self.network.node.identities,
            self.network.indexer.identities,
        )
        self.accounts = Accounts(
            self.repository.accounts,
            self.network.node.accounts,
            self.network.indexer.accounts,
            self.passwords,
            self.wallets,
            self.transfers,
            self.repository.v1_file_wallets,
            self.currencies,
            self.event_dispatcher,
        )
        self.amounts = Amounts(self.currencies, self.translator)
        self.nodes = Nodes(
            self.repository.nodes,
            self.preferences,
            self.network.node,
            self.config,
            self.currencies,
            self.event_dispatcher,
        )
        self.indexers = Indexers(
            self.repository.indexers,
            self.preferences,
            self.network.indexer,
            self.config,
            self.currencies,
            self.event_dispatcher,
        )
        self.smiths = Smiths(
            self.repository.smiths,
            self.repository.identities,
            self.network.node,
            self.network.indexer.identities,
        )
        self.authorities = Authorities(
            self.repository.authorities,
            self.network.node.authorities,
            self.nodes,
            self.smiths,
        )
        self.categories = Categories(
            self.repository.categories, self.accounts, self.event_dispatcher
        )
        self.technical_committee = TechnicalCommittee(
            self.repository,
            self.network,
            self.event_dispatcher,
        )
        self.vaults = Vaults(
            self.network.node.accounts,
            self.accounts,
            self.currencies,
        )

        # if currency properties required for amount display not populated...
        if self.currencies.get_current().members_count is None:
            try:
                # fetch currency properties from network
                self.currencies.network_update_properties()
            except NodeCurrencyException:
                self.currencies.get_current().members_count = 1

    def init_i18n(self) -> Any:
        """
        Init translator from configured language

        :return:
        """
        # define translator for configurated language
        translator = gettext.translation(
            "application",
            str(LOCALES_PATH),
            languages=[self.config.get(Config.LANGUAGE_KEY)],
        )
        # init translator
        translator.install()

        return translator

    def select_currency(self, code_name: str):
        """
        Change currency

        :return:
        """
        if self.config is None:
            raise NoConfigError

        # dispatch event EVENT_TYPE_PRE_CHANGE
        event = CurrencyEvent(CurrencyEvent.EVENT_TYPE_PRE_CHANGE, code_name)
        self.event_dispatcher.dispatch_event(event)

        self.config.set(Config.CURRENCY_KEY, code_name)

        if self.repository.db_client is not None:
            self.repository.db_client.disconnect()

        # init database connection
        currency_db_file_uri = (
            self.data_path.expanduser()
            .joinpath(code_name + DATABASE_FILE_EXTENSION)
            .as_uri()
        )
        self.repository.db_client.connect(currency_db_file_uri)

        self.currencies.set_current(code_name)

        # init domains with new repository adapter
        self.nodes.init_repository()
        self.indexers.init_repository()

        # get current entry point for new network connection
        current_node = self.nodes.get(self.nodes.get_current_url())
        if current_node is not None:
            # disconnect previous node connection
            self.connections.node.disconnect()
            # connect to node
            self.connections.node.connect(current_node)

        # get current entry point for new network connection
        current_indexer = self.indexers.get(self.indexers.get_current_url())
        if current_indexer is not None:
            # disconnect previous indexer connection
            self.connections.indexer.disconnect()
            # connect to indexer
            self.connections.indexer.connect(current_indexer)

        try:
            # fetch currency properties from network
            self.currencies.network_update_properties()
        except NodeCurrencyException:
            self.currencies.get_current().members_count = 1

        # dispatch event EVENT_TYPE_CHANGED
        event = CurrencyEvent(
            CurrencyEvent.EVENT_TYPE_CHANGED, self.currencies.get_current().code_name
        )
        self.event_dispatcher.dispatch_event(event)

    def select_language(self, language: str):
        """
        Select GUI language

        :param language: Code of language (ex: "en_US", "fr_FR")
        :return:
        """
        if self.config is None:
            raise NoConfigError

        self.config.set(Config.LANGUAGE_KEY, language)
        self.translator = self.init_i18n()

    def save_data(self, filepath: str) -> None:
        """
        Save user data on disk as json file

        :param filepath: Filepath to save data into
        :return:
        """
        categories = []
        for category in self.categories.list_all():
            category_dict = asdict(category)
            category_dict = serialize_dict(category_dict)
            categories.append(category_dict)

        accounts = []
        for account in self.accounts.get_list():
            account_dict = asdict(account)
            account_dict = serialize_dict(account_dict)
            accounts.append(account_dict)

        wallets = []
        for wallet in self.wallets.list():
            wallets.append(asdict(wallet))

        passwords = []
        for password in self.passwords.list():
            passwords.append(asdict(password))

        nodes = []
        for node in self.nodes.list():
            nodes.append(asdict(node))

        indexers = []
        for indexer in self.indexers.list():
            indexers.append(asdict(indexer))

        data = {
            "categories": categories,
            "accounts": accounts,
            "wallets": wallets,
            "passwords": passwords,
            "nodes": nodes,
            "indexers": indexers,
        }
        with open(filepath, "w") as file:
            json.dump(data, file, indent=4)

        logging.debug("Repository data successfully saved in %s", filepath)

    def load_data(self, filepath: str) -> None:
        """
        Load backup data json from disk

        :param filepath: Path of json file
        :return:
        """
        logging.debug("Delete all data in repository...")
        self.categories.delete_all()
        self.accounts.delete_all()
        self.wallets.delete_all()
        self.passwords.delete_all()
        self.identities.delete_all()
        self.smiths.delete_all()
        self.authorities.delete_all()

        self.nodes.delete_all()
        self.nodes.init_repository()
        self.indexers.delete_all()
        self.indexers.init_repository()

        logging.debug("Open json file...")
        with open(filepath, "r") as file:
            data = json.load(file)

        logging.debug("process user data...")
        for category_dict in data["categories"]:
            category_dict["id"] = UUID(hex=category_dict["id"])
            self.categories.repository.add(Category(**category_dict))

        for account_dict in data["accounts"]:
            account_dict["category_id"] = (
                UUID(hex=account_dict["category_id"])
                if account_dict["category_id"] is not None
                else None
            )
            self.accounts.repository.add(Account(**account_dict))

        for wallet_dict in data["wallets"]:
            self.wallets.repository.add(Wallet(**wallet_dict))

        for password_dict in data["passwords"]:
            self.passwords.repository.add(Password(**password_dict))

        for node_dict in data["nodes"]:
            self.nodes.repository.add(Node(**node_dict))

        for indexer_dict in data["indexers"]:
            self.indexers.repository.add(Indexer(**indexer_dict))

        logging.debug("User data successfully loaded")

        # load currency servers in repository
        self.nodes.init_repository()
        self.indexers.init_repository()

    def close(self):
        """
        Quit application and close what needs to be closed

        :return:
        """
        # disconnect all connections
        self.connections.disconnect_all()
        # close DB client
        self.repository.db_client.disconnect()


def serialize_dict(data: dict) -> dict:
    """
    Return the data dict with serialized values for json export

    :param data: Data to serialize
    :return:
    """
    serialized_data = {}
    for key, value in data.items():
        if isinstance(value, UUID):
            value = value.hex
        elif isinstance(value, datetime):
            value = value.isoformat()
        serialized_data[key] = value

    return serialized_data


class NoDatabaseError(Exception):
    pass


class NoConfigError(Exception):
    pass
