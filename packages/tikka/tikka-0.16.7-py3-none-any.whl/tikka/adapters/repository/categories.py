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
from uuid import UUID

from tikka.domains.entities.category import Category
from tikka.interfaces.adapters.repository.categories import (
    CategoriesRepositoryInterface,
)
from tikka.interfaces.adapters.repository.db_repository import DBRepositoryInterface

TABLE_NAME = "categories"


class DBCategoriesRepository(CategoriesRepositoryInterface, DBRepositoryInterface):
    """
    DBCategoriesRepository class
    """

    def add(self, category: Category) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            CategoriesRepositoryInterface.add.__doc__
        )

        # insert only non hidden fields
        self.client.insert(
            TABLE_NAME,
            **get_fields_from_category(category),
        )

    def get(self, id: UUID) -> Optional[Category]:  # pylint: disable=redefined-builtin
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            CategoriesRepositoryInterface.get.__doc__
        )

        row = self.client.select_one(
            f"SELECT * FROM {TABLE_NAME} WHERE id=?", (id.hex,)
        )
        if row is None:
            return None

        return get_category_from_row(row)

    def update(self, category: Category) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            CategoriesRepositoryInterface.update.__doc__
        )

        # update only non hidden fields
        self.client.update(
            TABLE_NAME,
            f"id='{category.id.hex}'",
            **get_fields_from_category(category),
        )

    def update_parent_id(self, parent_id: UUID, new_parent_id: Optional[UUID]):
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            CategoriesRepositoryInterface.update_parent_id.__doc__
        )
        self.client.update(
            TABLE_NAME,
            f"parent_id='{parent_id.hex}'",
            parent_id=new_parent_id.hex if new_parent_id is not None else None,
        )

    def delete(self, id: UUID) -> None:  # pylint: disable=redefined-builtin
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            CategoriesRepositoryInterface.delete.__doc__
        )

        self.client.delete(TABLE_NAME, id=id.hex)

    def delete_all(self) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            CategoriesRepositoryInterface.delete_all.__doc__
        )

        self.client.clear(TABLE_NAME)

    def list(self, parent_id: Optional[UUID]) -> List[Category]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            CategoriesRepositoryInterface.list.__doc__
        )
        sql_parent_id = None if parent_id is None else parent_id.hex
        if sql_parent_id is None:
            sql = f"SELECT * FROM {TABLE_NAME} WHERE parent_id IS ? ORDER BY name ASC"
        else:
            sql = f"SELECT * FROM {TABLE_NAME} WHERE parent_id=? ORDER BY name ASC"
        result_set = self.client.select(
            sql,
            (sql_parent_id,),
        )

        list_ = []
        for row in result_set:
            list_.append(get_category_from_row(row))

        return list_

    def list_all(self) -> List[Category]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            CategoriesRepositoryInterface.list.__doc__
        )
        result_set = self.client.select(f"SELECT * FROM {TABLE_NAME} ORDER BY name ASC")

        list_ = []
        for row in result_set:
            list_.append(get_category_from_row(row))

        return list_


def get_fields_from_category(category: Category) -> dict:
    """
    Return a dict of supported fields with normalized value

    :param category: Category instance
    :return:
    """
    fields = {}
    for (key, value) in category.__dict__.items():
        if key.startswith("_"):
            continue
        if isinstance(value, UUID):
            value = value.hex
        elif isinstance(value, bool):
            value = 1 if value is True else 0
        fields[key] = value

    return fields


def get_category_from_row(row: tuple) -> Category:
    """
    Return a Category instance from a result set row

    :param row: Result set row
    :return:
    """
    values: List[Any] = []
    count = 0
    for value in row:
        if count in (0, 3):
            if value is not None:
                values.append(UUID(hex=value))
        elif count == 2:
            values.append(value == 1)
        else:
            values.append(value)
        count += 1

    return Category(*values)  # pylint: disable=no-value-for-parameter
