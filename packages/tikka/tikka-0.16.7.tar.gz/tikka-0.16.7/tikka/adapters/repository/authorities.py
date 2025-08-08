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

from typing import Any, List, Optional

from tikka.domains.entities.authorities import Authority, AuthorityStatus
from tikka.interfaces.adapters.repository.authorities import (
    AuthoritiesRepositoryInterface,
)
from tikka.interfaces.adapters.repository.db_repository import DBRepositoryInterface

TABLE_NAME = "authorities"


class DBAuthoritiesRepository(AuthoritiesRepositoryInterface, DBRepositoryInterface):
    """
    DBAuthoritiesRepository class
    """

    def add(self, authority: Authority) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            AuthoritiesRepositoryInterface.add.__doc__
        )

        # insert only non hidden fields
        self.client.insert(
            TABLE_NAME,
            **get_fields_from_authority(authority),
        )

    def get(self, identity_index: int) -> Optional[Authority]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            AuthoritiesRepositoryInterface.get.__doc__
        )

        row = self.client.select_one(
            f"SELECT * FROM {TABLE_NAME} WHERE identity_index=?", (identity_index,)
        )
        if row is None:
            return None

        return get_authority_from_row(row)

    def update(self, authority: Authority) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            AuthoritiesRepositoryInterface.update.__doc__
        )

        # update only non hidden fields
        self.client.update(
            TABLE_NAME,
            f"identity_index='{authority.identity_index}'",
            **get_fields_from_authority(authority),
        )

    def delete(self, identity_index: int) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            AuthoritiesRepositoryInterface.delete.__doc__
        )

        self.client.delete(TABLE_NAME, identity_index=identity_index)

    def delete_all(self) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            AuthoritiesRepositoryInterface.delete_all.__doc__
        )

        self.client.clear(TABLE_NAME)

    def exists(self, identity_index: int) -> bool:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            AuthoritiesRepositoryInterface.exists.__doc__
        )

        row = self.client.select_one(
            f"SELECT count(identity_index) FROM {TABLE_NAME} WHERE identity_index=?",
            (identity_index,),
        )
        if row is None:
            return False

        return row[0] == 1

    def list(self) -> List[Authority]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            AuthoritiesRepositoryInterface.list.__doc__
        )
        result_set = self.client.select(
            f"SELECT * FROM {TABLE_NAME} ORDER BY identity_index ASC"
        )

        list_ = []
        for row in result_set:
            list_.append(get_authority_from_row(row))

        return list_


def get_fields_from_authority(authority: Authority) -> dict:
    """
    Return a dict of supported fields with normalized value

    :param authority: Authority instance
    :return:
    """
    fields = {}
    for (key, value) in authority.__dict__.items():
        if key.startswith("_"):
            continue
        if key == "status":
            # convert AuthorityStatus Enum to int
            value = value.value
        fields[key] = value

    return fields


def get_authority_from_row(row: tuple) -> Authority:
    """
    Return an Authority instance from a result set row

    :param row: Result set row
    :return:
    """
    values: List[Any] = []
    count = 0
    for value in row:
        if count == 1:
            # convert int to AuthorityStatus Enum
            values.append(AuthorityStatus(value))
        else:
            values.append(value)
        count += 1

    return Authority(*values)  # pylint: disable=no-value-for-parameter
