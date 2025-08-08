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

from tikka.domains.entities.password import Password
from tikka.interfaces.adapters.repository.db_repository import DBRepositoryInterface
from tikka.interfaces.adapters.repository.passwords import PasswordsRepositoryInterface

TABLE_NAME = "passwords"


class DBPasswordsRepository(PasswordsRepositoryInterface, DBRepositoryInterface):
    """
    DBPasswordsRepository class
    """

    def list(self) -> List[Password]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            PasswordsRepositoryInterface.list.__doc__
        )

        result_set = self.client.select(f"SELECT * FROM {TABLE_NAME}")

        list_ = []
        for row in result_set:
            list_.append(Password(*row))

        return list_

    def add(self, password: Password) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            PasswordsRepositoryInterface.add.__doc__
        )

        # insert only non hidden fields
        self.client.insert(
            TABLE_NAME,
            **{
                key: value
                for (key, value) in password.__dict__.items()
                if not key.startswith("_")
            },
        )

    def get(self, root: str) -> Optional[Password]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            PasswordsRepositoryInterface.get.__doc__
        )

        row = self.client.select_one(
            f"SELECT * FROM {TABLE_NAME} WHERE root=?", (root,)
        )
        if row is None:
            return None

        return Password(*row)

    def update(self, password: Password) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            PasswordsRepositoryInterface.update.__doc__
        )

        # update only non hidden fields
        self.client.update(
            TABLE_NAME,
            f"root='{password.root}'",
            **{
                key: value
                for (key, value) in password.__dict__.items()
                if not key.startswith("_")
            },
        )

    def delete(self, root: str) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            PasswordsRepositoryInterface.delete.__doc__
        )

        self.client.delete(TABLE_NAME, root=root)

    def delete_all(self) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            PasswordsRepositoryInterface.delete_all.__doc__
        )

        self.client.clear(TABLE_NAME)

    def exists(self, root: str) -> bool:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            PasswordsRepositoryInterface.exists.__doc__
        )

        row = self.client.select_one(
            f"SELECT count(root) FROM {TABLE_NAME} WHERE root=?", (root,)
        )
        if row is None:
            return False

        return row[0] == 1
