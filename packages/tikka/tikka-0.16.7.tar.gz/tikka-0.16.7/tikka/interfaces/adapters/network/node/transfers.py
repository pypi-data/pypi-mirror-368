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

import abc
from typing import Optional

from tikka.adapters.network.node.substrate_client import ExtrinsicReceipt
from tikka.interfaces.adapters.network.node.node import NetworkNodeInterface
from tikka.libs.keypair import Keypair


class NodeTransfersInterface(abc.ABC):
    """
    NodeTransfersInterface class
    """

    @abc.abstractmethod
    def __init__(self, node: NetworkNodeInterface) -> None:
        """
        Use node connection to request transfers information

        :param node: NetworkNodeInterface instance
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def send(
        self, sender_keypair: Keypair, recipient_address: str, amount: int
    ) -> Optional[ExtrinsicReceipt]:
        """
        Send amount (blockchain unit) from sender_account to recipient_address
        wait for extrinsic finalization and return ExtrinsicReceipt

        :param sender_keypair: Sender Keypair
        :param recipient_address: Recipient address
        :param amount: Amount in blockchain units
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def send_with_comment(
        self, sender_keypair: Keypair, recipient_address: str, amount: int, comment: str
    ) -> Optional[ExtrinsicReceipt]:
        """
        Send amount (blockchain unit) from sender_account to recipient_address
        wait for extrinsic finalization and return ExtrinsicReceipt

        :param sender_keypair: Sender Keypair
        :param recipient_address: Recipient address
        :param amount: Amount in blockchain units
        :param comment: Comment from user
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def fees(
        self, sender_keypair: Keypair, recipient_address: str, amount: int
    ) -> Optional[int]:
        """
        Fetch transfer fees and return it

        :param sender_keypair: Sender Keypair
        :param recipient_address: Recipient address
        :param amount: Amount in blockchain units
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def transfer_all(
        self, sender_keypair: Keypair, recipient_address: str, keep_alive: bool = False
    ) -> Optional[ExtrinsicReceipt]:
        """
        Send amount (blockchain unit) from sender_account to recipient_address
        wait for extrinsic finalization and return ExtrinsicReceipt

        :param sender_keypair: Sender Keypair
        :param recipient_address: Recipient address
        :param keep_alive: Optional, default False
        :return:
        """
        raise NotImplementedError


class NodeTransfersException(Exception):
    """
    NodeTransfersException class
    """
