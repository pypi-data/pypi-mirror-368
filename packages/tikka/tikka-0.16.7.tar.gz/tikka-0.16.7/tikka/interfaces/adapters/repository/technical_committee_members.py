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
from typing import List

from tikka.domains.entities.technical_committee import TechnicalCommitteeMember


class TechnicalCommitteeMembersRepositoryInterface(abc.ABC):
    """
    TechnicalCommitteeMembersRepositoryInterface class
    """

    @abc.abstractmethod
    def set_list(self, members: List[TechnicalCommitteeMember]) -> None:
        """
        Store list of TechnicalCommitteeMember instances in repository

        :param members: List of TechnicalCommitteeMember instances
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def list(self) -> List[TechnicalCommitteeMember]:
        """
        Return list of all TechnicalCommitteeMember instances in repository

        :return:
        """
        raise NotImplementedError
