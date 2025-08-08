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
from typing import List, Optional
from uuid import UUID, uuid4

from tikka.domains.accounts import Accounts
from tikka.domains.entities.category import Category
from tikka.domains.entities.events import CategoryEvent
from tikka.domains.events import EventDispatcher
from tikka.interfaces.adapters.repository.categories import (
    CategoriesRepositoryInterface,
)


class Categories:

    """
    Categories domain class
    """

    def __init__(
        self,
        repository: CategoriesRepositoryInterface,
        accounts: Accounts,
        event_dispatcher: EventDispatcher,
    ):
        """
        Init Categories domain

        :param repository: AccountsRepositoryInterface instance
        :param accounts: Accounts domain instance
        :param event_dispatcher: EventDispatcher instance
        """
        self.repository = repository
        self.accounts = accounts
        self.event_dispatcher = event_dispatcher

    @staticmethod
    def create(name: str, parent_id: Optional[UUID] = None):
        """
        Return a new Category instance with a unique ID

        :param name: Name of the category
        :param parent_id: UUID of the parent category
        :return:
        """
        return Category(id=uuid4(), name=name, parent_id=parent_id)

    def add(self, category: Category):
        """
        Add category in repository

        :param category: Category instance
        :return:
        """
        self.repository.add(category)
        self.event_dispatcher.dispatch_event(
            CategoryEvent(CategoryEvent.EVENT_TYPE_ADD, category)
        )

    def update(self, category: Category):
        """
        Update category in repository

        :param category: Category instance
        :return:
        """
        self.repository.update(category)
        self.event_dispatcher.dispatch_event(
            CategoryEvent(CategoryEvent.EVENT_TYPE_UPDATE, category)
        )

    def get(self, id: UUID) -> Optional[Category]:  # pylint: disable=redefined-builtin
        """
        Get category instance

        :param id: Category ID
        :return:
        """
        return self.repository.get(id)

    def delete(self, id: UUID) -> None:  # pylint: disable=redefined-builtin
        """
        Delete category in repository

        :param id: Category ID to delete
        :return:
        """
        category = self.get(id)
        if category is None:
            return None

        self.repository.delete(id)
        self.event_dispatcher.dispatch_event(
            CategoryEvent(CategoryEvent.EVENT_TYPE_DELETE, category)
        )

        return None

    def delete_all(self) -> None:
        """
        Delete all categories in repository

        :return:
        """
        self.repository.delete_all()

    def list(self, parent_id: Optional[UUID]) -> List[Category]:
        """
        Return list of Category instances with parent_id

        :param parent_id: Parent ID
        :return:
        """
        return self.repository.list(parent_id)

    def list_all(self) -> List[Category]:
        """
        Return list with all Category instances

        :return:
        """
        return self.repository.list_all()

    def expand(self, category: Category):
        """
        Update category with expanded attribute to True

        :param category: Category instance
        :return:
        """
        category.expanded = True
        self.repository.update(category)

    def collapse(self, category: Category):
        """
        Update category with expanded attribute to False

        :param category: Category instance
        :return:
        """
        category.expanded = False
        self.repository.update(category)
