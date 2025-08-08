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
from datetime import datetime
from typing import Dict, List, Optional

from tikka.domains.entities.smith import Smith, SmithStatus
from tikka.interfaces.adapters.network.indexer.identities import (
    IndexerIdentitiesInterface,
)
from tikka.interfaces.adapters.network.node.node import NetworkNodeInterface
from tikka.interfaces.adapters.repository.identities import (
    IdentitiesRepositoryInterface,
)
from tikka.interfaces.adapters.repository.smiths import SmithsRepositoryInterface
from tikka.libs.keypair import Keypair


class Smiths:

    """
    Smiths domain class
    """

    def __init__(
        self,
        repository: SmithsRepositoryInterface,
        identities_repository: IdentitiesRepositoryInterface,
        network_node: NetworkNodeInterface,
        indexer_identities: IndexerIdentitiesInterface,
    ):
        """
        Init Smiths domain

        :param repository: SmithsRepositoryInterface instance
        :param identities_repository: IdentitiesRepositoryInterface instance
        :param network_node: NetworkNodeInterface instance
        """
        self.repository = repository
        self.identities_repository = identities_repository
        self.network_node = network_node
        self.indexer_identities = indexer_identities

    @staticmethod
    def create(
        identity_index: int,
        expire_on: Optional[datetime] = None,
        status: SmithStatus = SmithStatus.INVITED,
    ):
        """
        Return a Smith instance from params

        :param identity_index: Identity index number in blockchain
        :param expire_on: Smith status expiration timestamp
        :param status: Smith status
        :return:
        """
        return Smith(
            identity_index=identity_index,
            expire_on=expire_on,
            status=status,
        )

    def add(self, smith: Smith):
        """
        Add smith in repository

        :param smith: Smith instance
        :return:
        """
        self.repository.add(smith)

    def update(self, smith: Smith):
        """
        Update smith in repository

        :param smith: Smith instance
        :return:
        """
        self.repository.update(smith)

    def get(self, identity_index: int) -> Optional[Smith]:
        """
        Get Smith instance from Identity index

        :param identity_index: Identity index
        :return:
        """
        return self.repository.get(identity_index)

    def delete(self, identity_index: int) -> None:
        """
        Delete smith in repository

        :param identity_index: Identity index to delete
        :return:
        """
        self.repository.delete(identity_index)

    def delete_all(self) -> None:
        """
        Delete all smiths in repository

        :return:
        """
        self.repository.delete_all()

    def exists(self, identity_index: int) -> bool:
        """
        Return True if smith exists in repository

        :param identity_index: Identity index to check
        :return:
        """
        return self.repository.exists(identity_index)

    def list(self) -> List[Smith]:
        """
        Return list of all smiths in repository

        :return:
        """
        return self.repository.list()

    def network_invite_member(self, keypair: Keypair, identity_index: int) -> None:
        """
        Request a smith membership for the Keypair account with node session_keys

        :param keypair: Owner Keypair
        :param identity_index: Identity index of member to invite to be smith
        :return:
        """
        return self.network_node.smiths.invite(keypair, identity_index)

    def network_accept_invitation(self, keypair: Keypair) -> None:
        """
        Invited Keypair account smith invitation acceptance

        :param keypair: Owner Keypair
        :return:
        """
        self.network_node.smiths.accept_invitation(keypair)

    def network_certify(self, keypair: Keypair, identity_index: int) -> None:
        """
        Certify an identity to be smith with the Keypair account

        :param keypair: Owner Keypair
        :param identity_index: Identity index of member to invite to be smith
        :return:
        """
        self.network_node.smiths.certify(keypair, identity_index)

    def network_get_smith(self, identity_index: int) -> Optional[Smith]:
        """
        Get smith for identity index from network if any

        :param identity_index: Identity index
        :return:
        """
        return self.network_node.smiths.get_smith(identity_index)

    def network_update_smith(self, identity_index: int) -> Optional[Smith]:
        """
        Get smith for identity index from network if any

        :param identity_index: Identity index
        :return:
        """
        smith = self.network_node.smiths.get_smith(identity_index)
        if smith is not None:
            if self.exists(identity_index) is True:
                self.update(smith)
            else:
                self.add(smith)
        else:
            self.delete(identity_index)

        return smith

    def network_update_smiths(self, identity_indice: List[int]) -> None:
        """
        Update DB with Smith instances from network from identity_indice list

        :param identity_indice: Identity indice list
        :return:
        """
        smiths = self.network_node.smiths.get_smiths(identity_indice)
        for index, smith in enumerate(smiths):
            if smith is None:
                self.repository.delete(identity_indice[index])
                continue
            if self.exists(smith.identity_index) is True:
                self.update(smith)
            else:
                self.add(smith)

    def network_get_smiths(
        self, identity_indice: List[int]
    ) -> Dict[int, Optional[Smith]]:
        """
        Get Smith instances from network from identity_indice list

        :param identity_indice: Identity indice list
        :return:
        """
        smiths: Dict[int, Optional[Smith]] = {}
        for index, smith in enumerate(
            self.network_node.smiths.get_smiths(identity_indice)
        ):
            smiths[identity_indice[index]] = smith
        return smiths
