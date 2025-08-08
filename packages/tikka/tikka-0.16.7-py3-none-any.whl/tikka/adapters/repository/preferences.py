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

# Copyright 2023 Vincent Texier <vit@free.fr>
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
from typing import Dict, Optional

from tikka.interfaces.adapters.repository.db_repository import DBRepositoryInterface
from tikka.interfaces.adapters.repository.preferences import (
    PreferencesRepositoryInterface,
)

TABLE_NAME = "preferences"


class DBPreferencesRepository(PreferencesRepositoryInterface, DBRepositoryInterface):
    """
    DBPreferencesRepository class
    """

    def get(self, key: str) -> Optional[str]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            PreferencesRepositoryInterface.get.__doc__
        )

        result = self.client.select_one(
            f"SELECT value_ FROM {TABLE_NAME} WHERE key_=?", (key,)
        )
        if result is None:
            return None

        return result[0]

    def set(self, key: str, value: Optional[str]) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            PreferencesRepositoryInterface.get.__doc__
        )

        # update existing key to value
        self.client.update(TABLE_NAME, f"key_='{key}'", value_=value)

        # if update fails create key with value
        self.client.insert(TABLE_NAME, key_=key, value_=value)

    def delete_all(self) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            PreferencesRepositoryInterface.delete_all.__doc__
        )

        self.client.clear(TABLE_NAME)

    def list(self) -> Dict[str, str]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            PreferencesRepositoryInterface.list.__doc__
        )

        result_set = self.client.select(f"SELECT * FROM {TABLE_NAME}")
        preferences = {}
        for row in result_set:
            preferences[row[0]] = row[1]

        return preferences
