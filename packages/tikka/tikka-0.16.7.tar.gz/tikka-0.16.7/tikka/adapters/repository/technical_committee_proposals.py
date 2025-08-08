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
from dataclasses import asdict
from datetime import datetime
from typing import Any, List

from tikka.domains.entities.technical_committee import (
    TechnicalCommitteeCall,
    TechnicalCommitteeProposal,
    TechnicalCommitteeVoting,
)
from tikka.interfaces.adapters.repository.db_repository import DBRepositoryInterface
from tikka.interfaces.adapters.repository.technical_committee_proposals import (
    TechnicalCommitteeProposalsRepositoryInterface,
)

TABLE_NAME = "technical_committee_proposals"


class DBTechnicalCommitteeProposalsRepository(
    TechnicalCommitteeProposalsRepositoryInterface, DBRepositoryInterface
):
    """
    DBTechnicalCommitteeProposalsRepository class
    """

    def set_list(self, proposals: List[TechnicalCommitteeProposal]) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            TechnicalCommitteeProposalsRepositoryInterface.set_list.__doc__
        )
        self.client.clear(TABLE_NAME)
        rows = [
            get_fields_from_technical_committee_proposal(proposal)
            for proposal in proposals
        ]
        if len(rows) > 0:
            self.client.insert_many(TABLE_NAME, rows)

    def list(self) -> List[TechnicalCommitteeProposal]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            TechnicalCommitteeProposalsRepositoryInterface.list.__doc__
        )
        result_set = self.client.select(f"SELECT * FROM {TABLE_NAME} ORDER BY hash ASC")

        list_ = []
        for row in result_set:
            list_.append(get_technical_committee_proposal_from_row(row))

        return list_


def get_fields_from_technical_committee_proposal(
    technical_committee_proposal: TechnicalCommitteeProposal,
) -> dict:
    """
    Return a dict of supported fields with normalized value

    :param technical_committee_proposal: TechnicalCommitteeProposal instance
    :return:
    """
    fields = {}
    for (key, value) in technical_committee_proposal.__dict__.items():
        if key.startswith("_"):
            continue
        elif key == "call":
            fields[key] = json.dumps(asdict(value))
        elif key == "voting":
            voting_dict = asdict(value)
            voting_dict["end"] = voting_dict["end"].timestamp()
            fields[key] = json.dumps(voting_dict)
        else:
            fields[key] = value

    return fields


def get_technical_committee_proposal_from_row(row: tuple) -> TechnicalCommitteeProposal:
    """
    Return an TechnicalCommitteeProposal instance from a result set row

    :param row: Result set row
    :return:
    """
    values: List[Any] = []
    count = 0
    for value in row:
        if count == 1:
            value = TechnicalCommitteeCall(**json.loads(value))
        elif count == 2:
            voting_dict = json.loads(value)
            voting_dict["end"] = datetime.fromtimestamp(voting_dict["end"])
            value = TechnicalCommitteeVoting(**voting_dict)
        values.append(value)
        count += 1

    return TechnicalCommitteeProposal(*values)  # pylint: disable=no-value-for-parameter
