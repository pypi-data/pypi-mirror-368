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

import abc
from typing import TYPE_CHECKING

from tikka.interfaces.adapters.repository.technical_committee_members import (
    TechnicalCommitteeMembersRepositoryInterface,
)
from tikka.interfaces.adapters.repository.technical_committee_proposals import (
    TechnicalCommitteeProposalsRepositoryInterface,
)

if TYPE_CHECKING:
    from tikka.interfaces.adapters.repository.accounts import (
        AccountsRepositoryInterface,
    )
    from tikka.interfaces.adapters.repository.authorities import (
        AuthoritiesRepositoryInterface,
    )
    from tikka.interfaces.adapters.repository.categories import (
        CategoriesRepositoryInterface,
    )
    from tikka.interfaces.adapters.repository.config import ConfigRepositoryInterface
    from tikka.interfaces.adapters.repository.currencies import (
        CurrenciesRepositoryInterface,
    )
    from tikka.interfaces.adapters.repository.currency import (
        CurrencyRepositoryInterface,
    )
    from tikka.interfaces.adapters.repository.db_client import DBClientInterface
    from tikka.interfaces.adapters.repository.file_wallets import (
        V1FileWalletsRepositoryInterface,
    )
    from tikka.interfaces.adapters.repository.identities import (
        IdentitiesRepositoryInterface,
    )
    from tikka.interfaces.adapters.repository.indexers import (
        IndexersRepositoryInterface,
    )
    from tikka.interfaces.adapters.repository.nodes import NodesRepositoryInterface
    from tikka.interfaces.adapters.repository.passwords import (
        PasswordsRepositoryInterface,
    )
    from tikka.interfaces.adapters.repository.preferences import (
        PreferencesRepositoryInterface,
    )
    from tikka.interfaces.adapters.repository.smiths import SmithsRepositoryInterface
    from tikka.interfaces.adapters.repository.transfers import (
        TransfersRepositoryInterface,
    )
    from tikka.interfaces.adapters.repository.wallets import WalletsRepositoryInterface


class RepositoryInterface(abc.ABC):
    """
    RepositoryInterface class
    """

    @property
    def db_client(self) -> DBClientInterface:
        """
        Return ConfigRepositoryInterface instance

        :return:
        """
        raise NotImplementedError

    @property
    def config(self) -> ConfigRepositoryInterface:
        """
        Return ConfigRepositoryInterface instance

        :return:
        """
        raise NotImplementedError

    @property
    def currencies(self) -> CurrenciesRepositoryInterface:
        """
        Return CurrenciesRepositoryInterface instance

        :return:
        """
        raise NotImplementedError

    @property
    def v1_file_wallets(self) -> V1FileWalletsRepositoryInterface:
        """
        Return V1FileWalletsRepositoryInterface instance

        :return:
        """
        raise NotImplementedError

    @property
    def accounts(self) -> AccountsRepositoryInterface:
        """
        Return AccountsRepositoryInterface instance

        :return:
        """
        raise NotImplementedError

    @property
    def authorities(self) -> AuthoritiesRepositoryInterface:
        """
        Return AuthoritiesRepositoryInterface instance

        :return:
        """
        raise NotImplementedError

    @property
    def categories(self) -> CategoriesRepositoryInterface:
        """
        Return CategoriesRepositoryInterface instance

        :return:
        """
        raise NotImplementedError

    @property
    def currency(self) -> CurrencyRepositoryInterface:
        """
        Return CurrencyRepositoryInterface instance

        :return:
        """
        raise NotImplementedError

    @property
    def identities(self) -> IdentitiesRepositoryInterface:
        """
        Return IdentitiesRepositoryInterface instance

        :return:
        """
        raise NotImplementedError

    @property
    def indexers(self) -> IndexersRepositoryInterface:
        """
        Return IndexersRepositoryInterface instance

        :return:
        """
        raise NotImplementedError

    @property
    def nodes(self) -> NodesRepositoryInterface:
        """
        Return NodesRepositoryInterface instance

        :return:
        """
        raise NotImplementedError

    @property
    def passwords(self) -> PasswordsRepositoryInterface:
        """
        Return PasswordsRepositoryInterface instance

        :return:
        """
        raise NotImplementedError

    @property
    def preferences(self) -> PreferencesRepositoryInterface:
        """
        Return PreferencesRepositoryInterface instance

        :return:
        """
        raise NotImplementedError

    @property
    def smiths(self) -> SmithsRepositoryInterface:
        """
        Return SmithsRepositoryInterface instance

        :return:
        """
        raise NotImplementedError

    @property
    def transfers(self) -> TransfersRepositoryInterface:
        """
        Return TransfersRepositoryInterface instance

        :return:
        """
        raise NotImplementedError

    @property
    def wallets(self) -> WalletsRepositoryInterface:
        """
        Return WalletsRepositoryInterface instance

        :return:
        """
        raise NotImplementedError

    @property
    def technical_committee_members(
        self,
    ) -> TechnicalCommitteeMembersRepositoryInterface:
        """
        Return TechnicalCommitteeMembersRepositoryInterface instance

        :return:
        """
        raise NotImplementedError

    @property
    def technical_committee_proposals(
        self,
    ) -> TechnicalCommitteeProposalsRepositoryInterface:
        """
        Return TechnicalCommitteeProposalsRepositoryInterface instance

        :return:
        """
        raise NotImplementedError
