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
from typing import TYPE_CHECKING, Dict, List

from tikka.domains.entities.authorities import AuthorityStatus
from tikka.interfaces.adapters.network.connection import NetworkConnectionError
from tikka.interfaces.adapters.network.node.authorities import (
    NodeAuthoritiesException,
    NodeAuthoritiesInterface,
)
from tikka.libs.keypair import Keypair

if TYPE_CHECKING:
    from tikka.adapters.network.node.node import NetworkNode


class NodeAuthorities(NodeAuthoritiesInterface):
    """
    NodeAuthorities class
    """

    def __init__(self, node: "NetworkNode") -> None:
        """
        Use NetworkNodeInterface to request/send smiths information

        :param node: NetworkNodeInterface instance
        :return:
        """
        self.node = node

    def rotate_keys(self) -> str:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodeAuthoritiesInterface.rotate_keys.__doc__
        )
        if (
            not self.node.connection.is_connected()
            or self.node.connection.client is None
        ):
            raise NodeAuthoritiesException(NetworkConnectionError())

        try:
            result = self.node.connection.client.rpc_request("author_rotateKeys", [])
        except Exception as exception:
            logging.exception(exception)
            if len(exception.args) > 0 and isinstance(exception.args[0], dict):
                exception = exception.args[0]["message"]
            raise NodeAuthoritiesException(exception)

        if result is None:
            raise NodeAuthoritiesException("No result from author_rotateKeys")

        return result.get("result")  # type: ignore

    def has_session_keys(self, session_keys: str) -> bool:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodeAuthoritiesInterface.has_session_keys.__doc__
        )
        if (
            not self.node.connection.is_connected()
            or self.node.connection.client is None
        ):
            raise NodeAuthoritiesException(NetworkConnectionError())

        try:
            result = self.node.connection.client.rpc_request(
                "author_hasSessionKeys", [session_keys]
            ).get("result")
        except Exception as exception:
            logging.exception(exception)
            raise NodeAuthoritiesException(exception)

        return result  # type: ignore

    def publish_session_keys(self, keypair: Keypair, session_keys: str) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodeAuthoritiesInterface.publish_session_keys.__doc__
        )
        if (
            not self.node.connection.is_connected()
            or self.node.connection.client is None
        ):
            raise NodeAuthoritiesException(NetworkConnectionError())

        session_keys_bytearray = bytearray.fromhex(session_keys[2:])
        params = {
            "keys": {
                "grandpa": f"0x{session_keys_bytearray[0:32].hex()}",
                "babe": f"0x{session_keys_bytearray[32:64].hex()}",
                "im_online": f"0x{session_keys_bytearray[64:96].hex()}",
                "authority_discovery": f"0x{session_keys_bytearray[96:128].hex()}",
            }
        }

        try:
            call = self.node.connection.client.compose_call(
                call_module="AuthorityMembers",
                call_function="set_session_keys",
                call_params=params,
            )
        except Exception as exception:
            logging.exception(exception)
            raise NodeAuthoritiesException(exception)

        try:
            extrinsic = self.node.connection.client.create_signed_extrinsic(
                call=call, keypair=keypair
            )
        except Exception as exception:
            logging.exception(exception)
            raise NodeAuthoritiesException(exception)

        try:
            # fixme: code stuck infinitely if no blocks are created on blockchain
            #       should have a timeout option
            receipt = self.node.connection.client.submit_extrinsic(
                extrinsic, wait_for_inclusion=True
            )
        except Exception as exception:
            logging.exception(exception)
            raise NodeAuthoritiesException(exception)

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
                else "authorities.publish_session_keys error"
            )
            raise NodeAuthoritiesException(message)

    def go_online(self, keypair: Keypair) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodeAuthoritiesInterface.go_online.__doc__
        )
        if (
            not self.node.connection.is_connected()
            or self.node.connection.client is None
        ):
            raise NodeAuthoritiesException(NetworkConnectionError())

        try:
            call = self.node.connection.client.compose_call(
                call_module="AuthorityMembers",
                call_function="go_online",
                call_params=None,
            )
        except Exception as exception:
            logging.exception(exception)
            raise NodeAuthoritiesException(exception)

        try:
            extrinsic = self.node.connection.client.create_signed_extrinsic(
                call=call, keypair=keypair
            )
        except Exception as exception:
            logging.exception(exception)
            raise NodeAuthoritiesException(exception)

        try:
            # fixme: code stuck infinitely if no blocks are created on blockchain
            #       should have a timeout option
            receipt = self.node.connection.client.submit_extrinsic(
                extrinsic, wait_for_inclusion=True
            )
        except Exception as exception:
            logging.exception(exception)
            raise NodeAuthoritiesException(exception)

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
                else "authorities.go_online error"
            )
            raise NodeAuthoritiesException(message)

    def go_offline(self, keypair: Keypair) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodeAuthoritiesInterface.go_offline.__doc__
        )
        if (
            not self.node.connection.is_connected()
            or self.node.connection.client is None
        ):
            raise NodeAuthoritiesException(NetworkConnectionError())

        try:
            call = self.node.connection.client.compose_call(
                call_module="AuthorityMembers",
                call_function="go_offline",
                call_params=None,
            )
        except Exception as exception:
            logging.exception(exception)
            raise NodeAuthoritiesException(exception)

        try:
            extrinsic = self.node.connection.client.create_signed_extrinsic(
                call=call, keypair=keypair
            )
        except Exception as exception:
            logging.exception(exception)
            raise NodeAuthoritiesException(exception)

        try:
            # fixme: code stuck infinitely if no blocks are created on blockchain
            #       should have a timeout option
            receipt = self.node.connection.client.submit_extrinsic(
                extrinsic, wait_for_inclusion=True
            )
        except Exception as exception:
            logging.exception(exception)
            raise NodeAuthoritiesException(exception)

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
                else "authorities.go_offline error"
            )
            raise NodeAuthoritiesException(message)

    def get_status(self, identity_index: int) -> AuthorityStatus:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodeAuthoritiesInterface.get_status.__doc__
        )
        if (
            not self.node.connection.is_connected()
            or self.node.connection.client is None
        ):
            raise NodeAuthoritiesException(NetworkConnectionError())

        status = AuthorityStatus.OFFLINE
        storage_functions: list = [
            ("AuthorityMembers", "OnlineAuthorities", []),
            ("AuthorityMembers", "IncomingAuthorities", []),
            ("AuthorityMembers", "OutgoingAuthorities", []),
        ]
        try:
            multi_result = self.node.connection.client.query_multi(storage_functions)
        except Exception as exception:
            logging.exception(exception)
            raise NodeAuthoritiesException(exception)

        online_authorities = multi_result[0] or []
        incoming_authorities = multi_result[1] or []
        outgoing_authorities = multi_result[2] or []

        if identity_index in online_authorities:
            status = AuthorityStatus.ONLINE
        elif identity_index in incoming_authorities:
            status = AuthorityStatus.INCOMING
        elif identity_index in outgoing_authorities:
            status = AuthorityStatus.OUTGOING

        return status

    def get_all(self) -> Dict[int, List[int]]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodeAuthoritiesInterface.get_all.__doc__
        )
        all_by_status = {}

        if (
            not self.node.connection.is_connected()
            or self.node.connection.client is None
        ):
            raise NodeAuthoritiesException(NetworkConnectionError())

        storage_functions: list = [
            ("AuthorityMembers", "OnlineAuthorities", []),
            ("AuthorityMembers", "IncomingAuthorities", []),
            ("AuthorityMembers", "OutgoingAuthorities", []),
        ]
        try:
            multi_result = self.node.connection.client.query_multi(storage_functions)
        except Exception as exception:
            logging.exception(exception)
            raise NodeAuthoritiesException(exception)

        all_by_status[AuthorityStatus.ONLINE.value] = multi_result[0] or []
        all_by_status[AuthorityStatus.INCOMING.value] = multi_result[1] or []
        all_by_status[AuthorityStatus.OUTGOING.value] = multi_result[2] or []

        return all_by_status
