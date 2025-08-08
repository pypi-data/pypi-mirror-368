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

from tikka.interfaces.adapters.repository.preferences import (
    PreferencesRepositoryInterface,
)


class Preferences:
    """
    Preferences domain class
    """

    def __init__(self, repository: PreferencesRepositoryInterface):
        """
        Init Preferences domain instance

        :param repository: PreferencesRepositoryInterface instance
        """
        self.repository = repository

    def set(self, key: str, value: Optional[str]):
        """
        Set key to value

        :param key: Key string
        :param value: Value
        :return:
        """
        self.repository.set(key, value)

    def get(self, key: str) -> Optional[str]:
        """
        Return value of key

        :param key: Key string
        :return:
        """
        return self.repository.get(key)

    def delete_all(self) -> None:
        """
        Delete all preferences in repository

        :return:
        """
        self.repository.delete_all()

    def list(self) -> Dict[str, str]:
        """
        Return list of all preferences as dict {key: value}

        :return:
        """
        return self.repository.list()
