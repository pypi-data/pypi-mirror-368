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
from typing import Optional, TypeVar

TransferType = TypeVar("TransferType", bound="Transfer")


@dataclass
class Transfer:
    id: str
    issuer_address: str
    issuer_identity_index: Optional[int]
    issuer_identity_name: Optional[str]
    receiver_address: str
    receiver_identity_index: Optional[int]
    receiver_identity_name: Optional[str]
    amount: int
    timestamp: datetime
    comment: Optional[str]
    comment_type: Optional[str]

    def __eq__(self, other):
        """
        Test equality on address

        :param other: Account instance
        :return:
        """
        if not isinstance(other, self.__class__):
            return False
        return self.__hash__() == other.__hash__()

    def __hash__(self):
        return hash(f"{self.id}")
