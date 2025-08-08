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

from typing import Any, List

from tikka.domains.entities.technical_committee import TechnicalCommitteeMember
from tikka.interfaces.adapters.repository.db_repository import DBRepositoryInterface
from tikka.interfaces.adapters.repository.technical_committee_members import (
    TechnicalCommitteeMembersRepositoryInterface,
)

TABLE_NAME = "technical_committee_members"


class DBTechnicalCommitteeMembersRepository(
    TechnicalCommitteeMembersRepositoryInterface, DBRepositoryInterface
):
    """
    DBTechnicalCommitteeMembersRepository class
    """

    def set_list(self, members: List[TechnicalCommitteeMember]) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            TechnicalCommitteeMembersRepositoryInterface.set_list.__doc__
        )
        self.client.clear(TABLE_NAME)
        rows = [
            get_fields_from_technical_committee_member(member) for member in members
        ]
        if len(rows) > 0:
            self.client.insert_many(TABLE_NAME, rows)

    def list(self) -> List[TechnicalCommitteeMember]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            TechnicalCommitteeMembersRepositoryInterface.list.__doc__
        )
        result_set = self.client.select(
            f"SELECT * FROM {TABLE_NAME} ORDER BY address ASC"
        )

        list_ = []
        for row in result_set:
            list_.append(get_technical_committee_member_from_row(row))

        return list_


def get_fields_from_technical_committee_member(
    technical_committee_member: TechnicalCommitteeMember,
) -> dict:
    """
    Return a dict of supported fields with normalized value

    :param technical_committee_member: TechnicalCommitteeMember instance
    :return:
    """
    fields = {}
    for (key, value) in technical_committee_member.__dict__.items():
        if key.startswith("_"):
            continue
        fields[key] = value

    return fields


def get_technical_committee_member_from_row(row: tuple) -> TechnicalCommitteeMember:
    """
    Return an TechnicalCommitteeMember instance from a result set row

    :param row: Result set row
    :return:
    """
    values: List[Any] = []
    count = 0
    for value in row:
        values.append(value)
        count += 1

    return TechnicalCommitteeMember(*values)  # pylint: disable=no-value-for-parameter
