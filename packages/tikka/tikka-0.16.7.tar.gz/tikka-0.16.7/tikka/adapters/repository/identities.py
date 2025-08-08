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

from typing import Any, Dict, List, Optional

from tikka.domains.entities.identity import Identity, IdentityStatus
from tikka.interfaces.adapters.repository.db_repository import DBRepositoryInterface
from tikka.interfaces.adapters.repository.identities import (
    IdentitiesRepositoryInterface,
)

TABLE_NAME = "identities"


class DBIdentitiesRepository(IdentitiesRepositoryInterface, DBRepositoryInterface):
    """
    DBIdentitiesRepository class
    """

    def add(self, identity: Identity) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            IdentitiesRepositoryInterface.add.__doc__
        )

        # insert only non hidden fields
        self.client.insert(
            TABLE_NAME,
            **get_fields_from_identity(identity),
        )

    def get(self, index: int) -> Optional[Identity]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            IdentitiesRepositoryInterface.get.__doc__
        )

        row = self.client.select_one(
            f"SELECT * FROM {TABLE_NAME} WHERE index_=?", (index,)
        )
        if row is None:
            return None

        return get_identity_from_row(row)

    def get_by_address(self, address: str) -> Optional[Identity]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            IdentitiesRepositoryInterface.get_by_address.__doc__
        )

        row = self.client.select_one(
            f"SELECT * FROM {TABLE_NAME} WHERE address=?", (address,)
        )
        if row is None:
            return None

        return get_identity_from_row(row)

    def get_by_addresses(self, addresses: List[str]) -> Dict[str, Optional[Identity]]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            IdentitiesRepositoryInterface.get_by_addresses.__doc__
        )
        question_mark_string = ",".join(f'"{address}"' for address in addresses)

        rows = self.client.select(
            f"SELECT * FROM {TABLE_NAME} WHERE address IN ({question_mark_string})"
        )

        identities_by_address: Dict[str, Optional[Identity]] = {}
        for row in rows:
            identities_by_address[row[4]] = get_identity_from_row(row)
        for address in addresses:
            if address not in identities_by_address:
                identities_by_address[address] = None

        return identities_by_address

    def get_index_by_address(self, address: str) -> Optional[int]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            IdentitiesRepositoryInterface.get_index_by_address.__doc__
        )

        row = self.client.select_one(
            f"SELECT index_ FROM {TABLE_NAME} WHERE address=?", (address,)
        )
        if row is None:
            return None

        return row[0]

    def update(self, identity: Identity) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            IdentitiesRepositoryInterface.update.__doc__
        )

        # update only non hidden fields
        self.client.update(
            TABLE_NAME,
            f"index_='{identity.index}'",
            **get_fields_from_identity(identity),
        )

    def delete(self, index: int) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            IdentitiesRepositoryInterface.delete.__doc__
        )

        self.client.delete(TABLE_NAME, index_=index)

    def delete_all(self) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            IdentitiesRepositoryInterface.delete_all.__doc__
        )

        self.client.clear(TABLE_NAME)

    def exists(self, index: int) -> bool:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            IdentitiesRepositoryInterface.exists.__doc__
        )

        row = self.client.select_one(
            f"SELECT count(index_) FROM {TABLE_NAME} WHERE index_=?", (index,)
        )
        if row is None:
            return False

        return row[0] == 1

    def list(self) -> List[Identity]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            IdentitiesRepositoryInterface.list.__doc__
        )

        result_set = self.client.select(f"SELECT * FROM {TABLE_NAME}")
        list_ = []
        for row in result_set:
            list_.append(get_identity_from_row(row))

        return list_

    def list_indice(self) -> List[int]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            IdentitiesRepositoryInterface.list_indice.__doc__
        )

        result_set = self.client.select(f"SELECT index_ FROM {TABLE_NAME}")
        list_indice = []
        for row in result_set:
            list_indice.append(row[0])

        return list_indice


def get_fields_from_identity(identity: Identity) -> dict:
    """
    Return a dict of supported fields with normalized value

    :param identity: Identity instance
    :return:
    """
    fields = {}
    for (key, value) in identity.__dict__.items():
        if key.startswith("_"):
            continue
        if key == "index":
            # index is a reserved keyword in sqlite3
            key = "index_"
        if key == "status":
            # convert IdentityStatus Enum to int
            value = value.value
        fields[key] = value

    return fields


def get_identity_from_row(row: tuple) -> Identity:
    """
    Return an Identity instance from a result set row

    :param row: Result set row
    :return:
    """
    values: List[Any] = []
    count = 0
    for value in row:
        if count == 3:
            # convert int to IdentityStatus Enum
            values.append(IdentityStatus(value))
        else:
            values.append(value)
        count += 1

    return Identity(*values)  # pylint: disable=no-value-for-parameter
