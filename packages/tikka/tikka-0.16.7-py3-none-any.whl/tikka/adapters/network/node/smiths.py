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
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, List, Optional

from tikka.domains.entities.smith import Smith, SmithStatus
from tikka.interfaces.adapters.network.connection import NetworkConnectionError
from tikka.interfaces.adapters.network.node.smiths import (
    NodeSmithsException,
    NodeSmithsInterface,
)
from tikka.libs.keypair import Keypair

if TYPE_CHECKING:
    from tikka.adapters.network.node.node import NetworkNode


class NodeSmiths(NodeSmithsInterface):
    """
    NodeSmiths class
    """

    status_map = {
        "Invited": SmithStatus.INVITED,
        "Pending": SmithStatus.PENDING,
        "Smith": SmithStatus.SMITH,
        "Excluded": SmithStatus.EXCLUDED,
    }

    def __init__(self, node: "NetworkNode") -> None:
        """
        Use NetworkNodeInterface to request/send smiths information

        :param node: NetworkNodeInterface instance
        :return:
        """
        self.node = node

    def get_smith(self, identity_index: int) -> Optional[Smith]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodeSmithsInterface.get_smith.__doc__
        )
        if (
            not self.node.connection.is_connected()
            or self.node.connection.client is None
        ):
            raise NodeSmithsException(NetworkConnectionError())

        try:
            result = self.node.connection.client.query(
                "SmithMembers", "Smiths", [identity_index]
            )
        except Exception as exception:
            logging.exception(exception)
            raise NodeSmithsException(exception)

        smith = None
        if result is not None:
            if result["expires_on"] is not None:
                expire_on_datetime = self.get_datetime_from_epoch(result["expires_on"])
            else:
                expire_on_datetime = None
            smith = Smith(
                identity_index=identity_index,
                status=self.status_map[result["status"]],
                expire_on=expire_on_datetime,
                certifications_received=result["received_certs"],
                certifications_issued=result["issued_certs"],
            )

        return smith

    def get_smiths(self, identity_indice: List[int]) -> List[Optional[Smith]]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodeSmithsInterface.get_smiths.__doc__
        )
        if (
            not self.node.connection.is_connected()
            or self.node.connection.client is None
        ):
            raise NodeSmithsException(NetworkConnectionError())

        storage_functions = []
        for identity_index in identity_indice:
            storage_functions.append(("SmithMembers", "Smiths", [identity_index]))

        try:
            multi_result = self.node.connection.client.query_multi(storage_functions)
        except Exception as exception:
            logging.exception(exception)
            raise NodeSmithsException(exception)

        smiths: List[Optional[Smith]] = []
        for index, value_obj in enumerate(multi_result):
            if value_obj is not None:
                if value_obj["expires_on"] is not None:
                    expire_on_datetime = self.get_datetime_from_epoch(
                        value_obj["expires_on"]
                    )
                else:
                    expire_on_datetime = None

                smiths.append(
                    Smith(
                        identity_index=identity_indice[index],
                        status=self.status_map[value_obj["status"]],
                        expire_on=expire_on_datetime,
                        certifications_received=value_obj["received_certs"],
                        certifications_issued=value_obj["issued_certs"],
                    )
                )
            else:
                smiths.append(None)

        return smiths

    def invite(self, keypair: Keypair, identity_index: int) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodeSmithsInterface.invite.__doc__
        )
        if (
            not self.node.connection.is_connected()
            or self.node.connection.client is None
        ):
            raise NodeSmithsException(NetworkConnectionError())

        params = {
            "receiver": identity_index,
        }

        try:
            call = self.node.connection.client.compose_call(
                call_module="SmithMembers",
                call_function="invite_smith",
                call_params=params,
            )
        except Exception as exception:
            logging.exception(exception)
            raise NodeSmithsException(exception)

        try:
            extrinsic = self.node.connection.client.create_signed_extrinsic(
                call=call, keypair=keypair
            )
        except Exception as exception:
            logging.exception(exception)
            raise NodeSmithsException(exception)

        try:
            # fixme: code stuck infinitely if no blocks are created on blockchain
            #       should have a timeout option
            receipt = self.node.connection.client.submit_extrinsic(
                extrinsic, wait_for_inclusion=True
            )
        except Exception as exception:
            logging.exception(exception)
            raise NodeSmithsException(exception)

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
                else "smiths.invite error"
            )
            raise NodeSmithsException(message)

    def accept_invitation(self, keypair: Keypair) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodeSmithsInterface.accept_invitation.__doc__
        )
        if (
            not self.node.connection.is_connected()
            or self.node.connection.client is None
        ):
            raise NodeSmithsException(NetworkConnectionError())

        try:
            call = self.node.connection.client.compose_call(
                call_module="SmithMembers",
                call_function="accept_invitation",
                call_params=None,
            )
        except Exception as exception:
            logging.exception(exception)
            raise NodeSmithsException(exception)

        try:
            extrinsic = self.node.connection.client.create_signed_extrinsic(
                call=call, keypair=keypair
            )
        except Exception as exception:
            logging.exception(exception)
            raise NodeSmithsException(exception)

        try:
            # fixme: code stuck infinitely if no blocks are created on blockchain
            #       should have a timeout option
            receipt = self.node.connection.client.submit_extrinsic(
                extrinsic, wait_for_inclusion=True
            )
        except Exception as exception:
            logging.exception(exception)
            raise NodeSmithsException(exception)

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
                else "smiths.accept_invitation error"
            )
            raise NodeSmithsException(message)

    def certify(self, keypair: Keypair, identity_index: int) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodeSmithsInterface.certify.__doc__
        )
        if (
            not self.node.connection.is_connected()
            or self.node.connection.client is None
        ):
            raise NodeSmithsException(NetworkConnectionError())

        params = {
            "receiver": identity_index,
        }

        try:
            call = self.node.connection.client.compose_call(
                call_module="SmithMembers",
                call_function="certify_smith",
                call_params=params,
            )
        except Exception as exception:
            logging.exception(exception)
            raise NodeSmithsException(exception)

        try:
            extrinsic = self.node.connection.client.create_signed_extrinsic(
                call=call, keypair=keypair
            )
        except Exception as exception:
            logging.exception(exception)
            raise NodeSmithsException(exception)

        # fixme: code stuck infinitely if no blocks are created on blockchain
        #       should have a timeout option
        receipt = self.node.connection.client.submit_extrinsic(
            extrinsic, wait_for_inclusion=True
        )
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
                else "smiths.certify error"
            )
            raise NodeSmithsException(message)

    def get_datetime_from_epoch(self, epoch_index: int) -> Optional[datetime]:
        """
        Return a datetime object from an epoch index

        :param epoch_index: Epoch number
        :return:
        """
        if (
            not self.node.connection.is_connected()
            or self.node.connection.client is None
        ):
            raise NodeSmithsException(NetworkConnectionError())

        try:
            result = self.node.connection.client.get_constant("Babe", "EpochDuration")
        except Exception as exception:
            logging.exception(exception)
            raise NodeSmithsException(exception)

        epoch_duration_in_blocks = result

        try:
            result = self.node.connection.client.get_constant(
                "Babe", "ExpectedBlockTime"
            )
        except Exception as exception:
            logging.exception(exception)
            raise NodeSmithsException(exception)

        block_duration_in_ms = result
        epoch_duration_in_ms = epoch_duration_in_blocks * block_duration_in_ms

        try:
            current_epoch_result = self.node.connection.client.query(
                "Babe", "EpochIndex"
            )
        except Exception as exception:
            logging.exception(exception)
            raise NodeSmithsException(exception)

        # fix epoch is None at chain start
        current_epoch_index = (
            current_epoch_result if current_epoch_result is not None else 0
        )

        current_time = datetime.now()
        epoch_diff = epoch_index - current_epoch_index
        if epoch_diff < 0:
            block_time = current_time - timedelta(
                milliseconds=abs(epoch_diff) * epoch_duration_in_ms
            )
        else:
            block_time = current_time + timedelta(
                milliseconds=abs(epoch_diff) * epoch_duration_in_ms
            )

        return block_time
