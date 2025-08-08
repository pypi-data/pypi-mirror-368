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

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from hashlib import sha256
from typing import Optional, TypeVar
from uuid import UUID

import base58

from tikka.libs.keypair import ss58_decode

AccountType = TypeVar("AccountType", bound="Account")


class AccountCryptoType(int, Enum):
    ED25519 = 0
    SR25519 = 1
    ECDSA = 2


@dataclass
class Account:

    address: str
    name: Optional[str] = None
    crypto_type: AccountCryptoType = AccountCryptoType.ED25519
    balance: Optional[int] = None
    path: Optional[str] = None
    root: Optional[str] = None
    file_import: bool = False
    category_id: Optional[UUID] = None
    legacy_v1: bool = False
    total_transfers_count: int = 0
    last_transfer_timestamp: Optional[datetime] = None
    oldest_transfer_timestamp: Optional[datetime] = None

    def __str__(self):
        """
        Return string representation

        :return:
        """
        if self.name:
            return f"{self.address} - {self.name}"
        return f"{self.address}"

    def __eq__(self, other):
        """
        Test equality on address

        :param other: Account instance
        :return:
        """
        if not isinstance(other, self.__class__):
            return False
        return other.address == self.address

    def __hash__(self):
        return hash(self.address)

    def get_v1_address(self, ss58_format: int):
        """
        Return address in V1 format (Base58 of pubkey)

        :return:
        """
        pubkey_hex = ss58_decode(self.address, ss58_format)
        checksum = base58.b58encode(
            sha256(sha256(bytes.fromhex(pubkey_hex)).digest()).digest()
        ).decode("utf8")[:3]
        v1_address = base58.b58encode(bytes.fromhex(pubkey_hex)).decode("utf8")
        return f"{v1_address}:{checksum}"
