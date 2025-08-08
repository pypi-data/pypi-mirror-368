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
import logging
import struct
from typing import TYPE_CHECKING, Dict, List, Optional

from tikka.domains.entities.identity import Certification, Identity, IdentityStatus
from tikka.interfaces.adapters.network.connection import NetworkConnectionError
from tikka.interfaces.adapters.network.node.identities import (
    NodeIdentitiesException,
    NodeIdentitiesInterface,
)
from tikka.libs.keypair import Keypair, KeypairType

if TYPE_CHECKING:
    from tikka.adapters.network.node.node import NetworkNode


class NodeIdentities(NodeIdentitiesInterface):
    """
    NodeIdentities class
    """

    status_map = {
        "Unconfirmed": IdentityStatus.UNCONFIRMED,
        "Unvalidated": IdentityStatus.UNVALIDATED,
        "Member": IdentityStatus.MEMBER,
        "NotMember": IdentityStatus.NOT_MEMBER,
        "Revoked": IdentityStatus.REVOKED,
    }

    def __init__(self, node: "NetworkNode") -> None:
        """
        Use NetworkNodeInterface to request/send smiths information

        :param node: NetworkNodeInterface instance
        :return:
        """
        self.node = node

    def get_identity_index(self, address: str) -> Optional[int]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodeIdentitiesInterface.get_identity_index.__doc__
        )
        if (
            not self.node.connection.is_connected()
            or self.node.connection.client is None
        ):
            raise NodeIdentitiesException(NetworkConnectionError())

        try:
            result = self.node.connection.client.query(
                "Identity", "IdentityIndexOf", [address]
            )
        except Exception as exception:
            logging.exception(exception)
            raise NodeIdentitiesException(exception)

        return result

    def get_identity_indice(self, addresses: List[str]) -> List[Optional[int]]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodeIdentitiesInterface.get_identity_indice.__doc__
        )
        if (
            not self.node.connection.is_connected()
            or self.node.connection.client is None
        ):
            raise NodeIdentitiesException(NetworkConnectionError())

        storage_functions = []
        for address in addresses:
            storage_functions.append(("Identity", "IdentityIndexOf", [address]))

        try:
            multi_result = self.node.connection.client.query_multi(storage_functions)
        except Exception as exception:
            logging.exception(exception)
            raise NodeIdentitiesException(exception)

        return multi_result

    def get_identity(self, address: str) -> Optional[Identity]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodeIdentitiesInterface.get_identity.__doc__
        )
        if (
            not self.node.connection.is_connected()
            or self.node.connection.client is None
        ):
            raise NodeIdentitiesException(NetworkConnectionError())

        try:
            index = self.node.connection.client.query(
                "Identity", "IdentityIndexOf", [address]
            )
        except Exception as exception:
            logging.exception(exception)
            raise NodeIdentitiesException(exception)

        if index is None:
            return None

        return self.get_identity_by_index(index)

    def get_identity_by_index(self, index: int) -> Optional[Identity]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodeIdentitiesInterface.get_identity_by_index.__doc__
        )
        if (
            not self.node.connection.is_connected()
            or self.node.connection.client is None
        ):
            raise NodeIdentitiesException(NetworkConnectionError())

        try:
            result = self.node.connection.client.query(
                "Identity", "Identities", [index]
            )
        except Exception as exception:
            logging.exception(exception)
            raise NodeIdentitiesException(exception)

        if result is None:
            return None

        old_address = result["old_owner_key"]
        if old_address is not None:
            old_address = old_address[0]

        # fixme: store next_creatable_on and removable_on as datetime in entity and DB
        return Identity(
            index=index,
            name=None,
            next_creatable_on=result["next_creatable_identity_on"],
            removable_on=int(result["next_scheduled"]),
            status=self.status_map[result["status"]],
            address=result["owner_key"],
            old_address=old_address,
            first_eligible_ud=result["data"]["first_eligible_ud"],
        )

    def get_identities(self, addresses: List[str]) -> Dict[str, Optional[Identity]]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodeIdentitiesInterface.get_identities.__doc__
        )
        if (
            not self.node.connection.is_connected()
            or self.node.connection.client is None
        ):
            raise NodeIdentitiesException(NetworkConnectionError())

        identity_indice = self.get_identity_indice(addresses)
        index_by_address = dict(zip(addresses, identity_indice))
        filtered_indice = [index for index in identity_indice if index is not None]
        identity_by_index = self.get_identities_by_index(list(set(filtered_indice)))

        identity_by_address = {}
        for address, index in index_by_address.items():
            if index is not None:
                identity_by_address[address] = identity_by_index[index]
            else:
                identity_by_address[address] = None

        return identity_by_address

    def get_identities_by_index(
        self, identity_indice: List[int]
    ) -> Dict[int, Optional[Identity]]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodeIdentitiesInterface.get_identities_by_index.__doc__
        )
        if (
            not self.node.connection.is_connected()
            or self.node.connection.client is None
        ):
            raise NodeIdentitiesException(NetworkConnectionError())

        storage_functions = []
        for identity_index in identity_indice:
            storage_functions.append(("Identity", "Identities", [identity_index]))

        try:
            multi_result = self.node.connection.client.query_multi(storage_functions)
        except Exception as exception:
            logging.exception(exception)
            raise NodeIdentitiesException(exception)

        # def: {
        #   Composite: {
        #     fields: [
        #       {
        #         name: data
        #         # type: 268
        #         typeName: IdtyData
        #         docs: []
        #       }
        #       {
        #         name: next_creatable_identity_on
        #         # type: 4
        #         typeName: BlockNumber
        #         docs: []
        #       }
        #       {
        #         name: old_owner_key
        #         # type: 269
        #         typeName: Option<(AccountId, BlockNumber)>
        #         docs: []
        #       }
        #       {
        #         name: owner_key
        #         # type: 0
        #         typeName: AccountId
        #         docs: []
        #       }
        #       {
        #         name: next_scheduled
        #         # type: 4
        #         typeName: BlockNumber
        #         docs: []
        #       }
        #       {
        #         name: status
        #         # type: 271
        #         typeName: IdtyStatus
        #         docs: []
        #       }
        #     ]
        #   }
        # }

        identities: Dict[int, Optional[Identity]] = {}
        for index, value_obj in enumerate(multi_result):
            if value_obj is not None:
                old_address_value = value_obj["old_owner_key"]
                old_address = None
                if old_address_value is not None:
                    if isinstance(old_address_value, tuple):
                        old_address = old_address_value[0]
                    else:
                        old_address = old_address_value

                identities[identity_indice[index]] = Identity(
                    index=identity_indice[index],
                    name=None,
                    next_creatable_on=value_obj["next_creatable_identity_on"],
                    removable_on=int(value_obj["next_scheduled"]),
                    status=self.status_map[value_obj["status"]],
                    address=value_obj["owner_key"],
                    old_address=old_address,
                    first_eligible_ud=value_obj["data"]["first_eligible_ud"],
                )
            else:
                identities[identity_indice[index]] = None

        return identities

    def change_owner_key(self, old_keypair: Keypair, new_keypair: Keypair) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodeIdentitiesInterface.change_owner_key.__doc__
        )
        if (
            not self.node.connection.is_connected()
            or self.node.connection.client is None
        ):
            raise NodeIdentitiesException(NetworkConnectionError())

        identity_index = self.get_identity_index(old_keypair.ss58_address)
        if identity_index is None:
            raise NodeIdentitiesException("No identity found for origin account")

        # message to sign
        prefix_bytes = b"icok"
        genesis_hash_str = self.node.connection.client.get_block_hash(0)
        assert genesis_hash_str is not None
        genesis_hash_bytes = bytearray.fromhex(genesis_hash_str[2:])
        identity_index_bytes = struct.pack("<I", identity_index)
        identity_pubkey_bytes = old_keypair.public_key
        message_bytes = (
            prefix_bytes
            + genesis_hash_bytes
            + identity_index_bytes
            + identity_pubkey_bytes
        )

        # message signed by the new owner
        signature_bytes = new_keypair.sign(message_bytes)

        # newKey: AccountId32, newKeySig: SpRuntimeMultiSignature
        crypto_label = (
            "Sr25519" if new_keypair.crypto_type == KeypairType.SR25519 else "Ed25519"
        )
        params = {
            "new_key": new_keypair.ss58_address,
            "new_key_sig": {crypto_label: signature_bytes},
        }
        try:
            # create raw call (extrinsic)
            call = self.node.connection.client.compose_call(
                call_module="Identity",
                call_function="change_owner_key",
                call_params=params,
            )
        except Exception as exception:
            logging.exception(exception)
            raise NodeIdentitiesException(exception)

        try:
            # create extrinsic signed by current owner
            extrinsic = self.node.connection.client.create_signed_extrinsic(
                call=call, keypair=old_keypair
            )
        except Exception as exception:
            logging.exception(exception)
            raise NodeIdentitiesException(exception)

        try:
            receipt = self.node.connection.client.submit_extrinsic(
                extrinsic, wait_for_inclusion=True
            )
        except Exception as exception:
            logging.exception(exception)
            raise NodeIdentitiesException(exception)

        logging.debug(
            "Extrinsic '%s' sent and included in block '%s'",
            receipt.extrinsic_hash,
            receipt.block_hash,
        )

        self.node.connection.client.process_events(receipt)

        if not receipt.is_success:
            logging.error(receipt.error_message)
            message = (
                receipt.error_message.docs[0]
                if receipt.error_message
                else "identities.change_owner_key error"
            )
            raise NodeIdentitiesException(message)

    def certs_by_receiver(
        self, receiver_address: str, receiver_identity_index: int
    ) -> List[Certification]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodeIdentitiesInterface.certs_by_receiver.__doc__
        )
        if (
            not self.node.connection.is_connected()
            or self.node.connection.client is None
        ):
            raise NodeIdentitiesException(NetworkConnectionError())

        try:
            result = self.node.connection.client.query(
                "Certification", "CertsByReceiver", [receiver_identity_index]
            )
        except Exception as exception:
            logging.exception(exception)
            raise NodeIdentitiesException(exception)

        storage_functions = []
        for issuer_identity_index, cert_expire_on_block in result:
            storage_functions.append(
                ("Identity", "Identities", [issuer_identity_index])
            )

        multi_result = self.node.connection.client.query_multi(storage_functions)

        certifications = []
        for index, value_obj in enumerate(multi_result):
            certifications.append(
                Certification(
                    issuer_identity_index=result[index][0],
                    issuer_address=value_obj["owner_key"],
                    receiver_identity_index=receiver_identity_index,
                    receiver_address=receiver_address,
                    expire_on_block=result[index][1],
                )
            )

        return certifications

    def claim_uds(self, keypair: Keypair) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodeIdentitiesInterface.claim_uds.__doc__
        )
        if (
            not self.node.connection.is_connected()
            or self.node.connection.client is None
        ):
            raise NodeIdentitiesException(NetworkConnectionError())

        try:
            # create raw call (extrinsic)
            call = self.node.connection.client.compose_call(
                call_module="UniversalDividend",
                call_function="claim_uds",
            )
        except Exception as exception:
            logging.exception(exception)
            raise NodeIdentitiesException(exception)

        try:
            # create extrinsic signed by current owner
            extrinsic = self.node.connection.client.create_signed_extrinsic(
                call=call, keypair=keypair
            )
        except Exception as exception:
            logging.exception(exception)
            raise NodeIdentitiesException(exception)

        try:
            receipt = self.node.connection.client.submit_extrinsic(
                extrinsic, wait_for_inclusion=True
            )
        except Exception as exception:
            logging.exception(exception)
            raise NodeIdentitiesException(exception)

        logging.debug(
            "Extrinsic '%s' sent and included in block '%s'",
            receipt.extrinsic_hash,
            receipt.block_hash,
        )

        self.node.connection.client.process_events(receipt)

        if not receipt.is_success:
            logging.error(receipt.error_message)
            message = (
                receipt.error_message.docs[0]
                if receipt.error_message
                else "identities.claim_uds error"
            )
            raise NodeIdentitiesException(message)
