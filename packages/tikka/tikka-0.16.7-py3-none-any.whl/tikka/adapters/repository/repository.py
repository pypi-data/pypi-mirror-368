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
from __future__ import annotations

from tikka.adapters.repository.accounts import DBAccountsRepository
from tikka.adapters.repository.authorities import DBAuthoritiesRepository
from tikka.adapters.repository.categories import DBCategoriesRepository
from tikka.adapters.repository.config import FileConfigRepository
from tikka.adapters.repository.currencies import FileCurrenciesRepository
from tikka.adapters.repository.currency import DBCurrencyRepository
from tikka.adapters.repository.file_db_client import FileDBClient
from tikka.adapters.repository.file_wallets import V1FileWalletsRepository
from tikka.adapters.repository.identities import DBIdentitiesRepository
from tikka.adapters.repository.indexers import DBIndexersRepository
from tikka.adapters.repository.nodes import DBNodesRepository
from tikka.adapters.repository.passwords import DBPasswordsRepository
from tikka.adapters.repository.preferences import DBPreferencesRepository
from tikka.adapters.repository.smiths import DBSmithsRepository
from tikka.adapters.repository.technical_committee_members import (
    DBTechnicalCommitteeMembersRepository,
)
from tikka.adapters.repository.technical_committee_proposals import (
    DBTechnicalCommitteeProposalsRepository,
)
from tikka.adapters.repository.transfers import DBTransfersRepository
from tikka.adapters.repository.wallets import DBWalletsRepository
from tikka.interfaces.adapters.repository.repository import RepositoryInterface
from tikka.interfaces.adapters.repository.technical_committee_proposals import (
    TechnicalCommitteeProposalsRepositoryInterface,
)


class Repository(RepositoryInterface):
    """
    Repository class
    """

    def __init__(self, data_path: str) -> None:
        """
        Init Repository instance
        """
        # dynamic user config file
        self._config = FileConfigRepository(data_path)
        # static application config file
        self._currencies = FileCurrenciesRepository()

        # handle V1 file wallets
        self._v1_file_wallets = V1FileWalletsRepository()

        # database
        self._db_client = FileDBClient()
        self._accounts = DBAccountsRepository(self._db_client)
        self._authorities = DBAuthoritiesRepository(self._db_client)
        self._categories = DBCategoriesRepository(self._db_client)
        self._currency = DBCurrencyRepository(self._db_client)
        self._identities = DBIdentitiesRepository(self._db_client)
        self._indexers = DBIndexersRepository(self._db_client)
        self._nodes = DBNodesRepository(self._db_client)
        self._passwords = DBPasswordsRepository(self._db_client)
        self._preferences = DBPreferencesRepository(self._db_client)
        self._smiths = DBSmithsRepository(self._db_client)
        self._transfers = DBTransfersRepository(self._db_client)
        self._wallets = DBWalletsRepository(self._db_client)
        self._technical_committee_members = DBTechnicalCommitteeMembersRepository(
            self._db_client
        )
        self._technical_committee_proposals = DBTechnicalCommitteeProposalsRepository(
            self._db_client
        )

    @property
    def db_client(self) -> FileDBClient:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            RepositoryInterface.db_client.__doc__
        )
        return self._db_client

    @property
    def config(self) -> FileConfigRepository:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            RepositoryInterface.config.__doc__
        )
        return self._config

    @property
    def currencies(self) -> FileCurrenciesRepository:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            RepositoryInterface.currencies.__doc__
        )
        return self._currencies

    @property
    def v1_file_wallets(self) -> V1FileWalletsRepository:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            RepositoryInterface.v1_file_wallets.__doc__
        )
        return self._v1_file_wallets

    @property
    def accounts(self) -> DBAccountsRepository:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            RepositoryInterface.accounts.__doc__
        )
        return self._accounts

    @property
    def authorities(self) -> DBAuthoritiesRepository:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            RepositoryInterface.authorities.__doc__
        )
        return self._authorities

    @property
    def categories(self) -> DBCategoriesRepository:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            RepositoryInterface.categories.__doc__
        )
        return self._categories

    @property
    def currency(self) -> DBCurrencyRepository:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            RepositoryInterface.currency.__doc__
        )
        return self._currency

    @property
    def identities(self) -> DBIdentitiesRepository:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            RepositoryInterface.identities.__doc__
        )
        return self._identities

    @property
    def indexers(self) -> DBIndexersRepository:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            RepositoryInterface.indexers.__doc__
        )
        return self._indexers

    @property
    def nodes(self) -> DBNodesRepository:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            RepositoryInterface.nodes.__doc__
        )
        return self._nodes

    @property
    def passwords(self) -> DBPasswordsRepository:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            RepositoryInterface.passwords.__doc__
        )
        return self._passwords

    @property
    def preferences(self) -> DBPreferencesRepository:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            RepositoryInterface.preferences.__doc__
        )
        return self._preferences

    @property
    def smiths(self) -> DBSmithsRepository:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            RepositoryInterface.smiths.__doc__
        )
        return self._smiths

    @property
    def transfers(self) -> DBTransfersRepository:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            RepositoryInterface.transfers.__doc__
        )
        return self._transfers

    @property
    def wallets(self) -> DBWalletsRepository:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            RepositoryInterface.wallets.__doc__
        )
        return self._wallets

    @property
    def technical_committee_members(
        self,
    ) -> DBTechnicalCommitteeMembersRepository:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            RepositoryInterface.technical_committee_members.__doc__
        )
        return self._technical_committee_members

    @property
    def technical_committee_proposals(
        self,
    ) -> TechnicalCommitteeProposalsRepositoryInterface:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            RepositoryInterface.technical_committee_proposals.__doc__
        )
        return self._technical_committee_proposals
