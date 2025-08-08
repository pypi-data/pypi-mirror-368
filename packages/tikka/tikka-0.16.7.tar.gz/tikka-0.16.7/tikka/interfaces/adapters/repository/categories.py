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
from typing import List, Optional
from uuid import UUID

from tikka.domains.entities.category import Category


class CategoriesRepositoryInterface(abc.ABC):
    """
    CategoriesRepositoryInterface class
    """

    COLUMN_ID = "category_id"
    COLUMN_NAME = "category_name"
    COLUMN_EXPANDED = "category_expanded"
    COLUMN_PARENT_ID = "category_parent_id"

    @abc.abstractmethod
    def add(self, category: Category) -> None:
        """
        Add a new category in repository

        :param category: Category instance
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, id: UUID) -> Optional[Category]:  # pylint: disable=redefined-builtin
        """
        Return Category instance from repository

        :param id: Category ID
        :return:
        """
        raise NotImplementedError

    def update(self, category: Category) -> None:
        """
        Update category in repository

        :param category: Category instance
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def update_parent_id(self, parent_id: UUID, new_parent_id: Optional[UUID]):
        """
        Update all category with parent_id to new_parent_id

        :param parent_id: Parent ID
        :param new_parent_id: New parent ID
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, id: UUID) -> None:  # pylint: disable=redefined-builtin
        """
        Delete category in repository

        :param id: Category ID to delete
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete_all(self) -> None:
        """
        Delete all categories in repository

        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def list(self, parent_id: Optional[UUID]) -> List[Category]:
        """
        Return categories with parent_id from repository

        :param parent_id: Category parent ID
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def list_all(self) -> List[Category]:
        """
        Return all categories by ascending alphabetical order from repository

        :return:
        """
        raise NotImplementedError
