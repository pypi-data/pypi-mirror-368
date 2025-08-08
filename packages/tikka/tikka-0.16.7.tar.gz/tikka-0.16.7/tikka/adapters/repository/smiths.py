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
import json
from datetime import datetime
from typing import Any, List, Optional

from tikka.domains.entities.smith import Smith, SmithStatus
from tikka.interfaces.adapters.repository.db_repository import DBRepositoryInterface
from tikka.interfaces.adapters.repository.smiths import SmithsRepositoryInterface

TABLE_NAME = "smiths"


class DBSmithsRepository(SmithsRepositoryInterface, DBRepositoryInterface):
    """
    DBSmithsRepository class
    """

    def add(self, smith: Smith) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            SmithsRepositoryInterface.add.__doc__
        )

        # insert only non hidden fields
        self.client.insert(
            TABLE_NAME,
            **get_fields_from_smith(smith),
        )

    def get(self, index: int) -> Optional[Smith]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            SmithsRepositoryInterface.get.__doc__
        )

        row = self.client.select_one(
            f"SELECT * FROM {TABLE_NAME} WHERE identity_index=?", (index,)
        )
        if row is None:
            return None

        return get_smith_from_row(row)

    def update(self, smith: Smith) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            SmithsRepositoryInterface.update.__doc__
        )

        # update only non hidden fields
        self.client.update(
            TABLE_NAME,
            f"identity_index='{smith.identity_index}'",
            **get_fields_from_smith(smith),
        )

    def delete(self, index: int) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            SmithsRepositoryInterface.delete.__doc__
        )

        self.client.delete(TABLE_NAME, identity_index=index)

    def delete_all(self) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            SmithsRepositoryInterface.delete_all.__doc__
        )

        self.client.clear(TABLE_NAME)

    def exists(self, index: int) -> bool:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            SmithsRepositoryInterface.exists.__doc__
        )

        row = self.client.select_one(
            f"SELECT count(identity_index) FROM {TABLE_NAME} WHERE identity_index=?",
            (index,),
        )
        if row is None:
            return False

        return row[0] == 1

    def list(self) -> List[Smith]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            SmithsRepositoryInterface.list.__doc__
        )
        result_set = self.client.select(
            f"SELECT * FROM {TABLE_NAME} ORDER BY identity_index ASC"
        )

        list_ = []
        for row in result_set:
            list_.append(get_smith_from_row(row))

        return list_


def get_fields_from_smith(smith: Smith) -> dict:
    """
    Return a dict of supported fields with normalized value

    :param smith: Smith instance
    :return:
    """
    fields = {}
    for (key, value) in smith.__dict__.items():
        if key.startswith("_"):
            continue
        if key == "status":
            # convert SmithStatus Enum to int
            value = value.value
        if key == "expire_on" and value is not None:
            # fixme: store field as datetime in DB (as string in Sqlite timestamp column type)
            # convert datetime to int
            value = int(value.timestamp())
        if key == "certifications_received" or key == "certifications_issued":
            value = json.dumps(value)
        fields[key] = value

    return fields


def get_smith_from_row(row: tuple) -> Smith:
    """
    Return a Smith instance from a result set row

    :param row: Result set row
    :return:
    """
    values: List[Any] = []
    count = 0
    for value in row:
        if count == 1:
            # convert int to SmithStatus Enum
            values.append(SmithStatus(value))
        elif count == 2 and value is not None:
            # convert timestamp to datetime
            values.append(datetime.fromtimestamp(value))
        elif count == 3 or count == 4:
            # convert certifications json string to list
            values.append(json.loads(value))
        else:
            values.append(value)
        count += 1

    return Smith(*values)  # pylint: disable=no-value-for-parameter
