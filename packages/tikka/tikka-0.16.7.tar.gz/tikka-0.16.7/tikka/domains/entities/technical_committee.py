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
from typing import List, Optional, TypeVar


@dataclass
class TechnicalCommitteeMember:
    address: str
    identity_index: int
    identity_name: Optional[str] = None


TechnicalCommitteeVotingType = TypeVar(
    "TechnicalCommitteeVotingType", bound="TechnicalCommitteeVoting"
)


@dataclass
class TechnicalCommitteeVoting:

    index: int
    threshold: int
    ayes: List[str]
    nays: List[str]
    end: datetime


TechnicalCommitteeCallType = TypeVar(
    "TechnicalCommitteeCallType", bound="TechnicalCommitteeCall"
)


@dataclass
class TechnicalCommitteeCall:
    index: int
    hash: str
    module: str
    function: str
    args: str


TechnicalCommitteeProposalType = TypeVar(
    "TechnicalCommitteeProposalType", bound="TechnicalCommitteeProposal"
)


@dataclass
class TechnicalCommitteeProposal:
    hash: str
    call: TechnicalCommitteeCall
    voting: TechnicalCommitteeVoting

    def __str__(self):
        """
        Return string representation

        :return:
        """
        return f"{self.hash}"
