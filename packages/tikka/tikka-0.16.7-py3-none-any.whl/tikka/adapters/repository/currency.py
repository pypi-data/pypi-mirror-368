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

from typing import Optional

from tikka.domains.entities.currency import Currency
from tikka.interfaces.adapters.repository.currency import CurrencyRepositoryInterface
from tikka.interfaces.adapters.repository.db_repository import DBRepositoryInterface

TABLE_NAME = "currency"


class DBCurrencyRepository(CurrencyRepositoryInterface, DBRepositoryInterface):
    """
    DBCurrencyRepository class
    """

    def add(self, currency: Currency) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            DBCurrencyRepository.add.__doc__
        )

        # insert only non hidden fields
        self.client.insert(
            TABLE_NAME,
            **get_fields_from_currency(currency),
        )

    def get(self, code_name: str) -> Optional[Currency]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            CurrencyRepositoryInterface.get.__doc__
        )

        row = self.client.select_one(
            f"SELECT * FROM {TABLE_NAME} WHERE code_name=?", (code_name,)
        )

        if row is None:
            return None

        return get_currency_from_row(row)

    def update(self, currency: Currency) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            CurrencyRepositoryInterface.update.__doc__
        )
        # update only non hidden fields
        self.client.update(
            TABLE_NAME,
            f"code_name='{currency.code_name}'",
            **get_fields_from_currency(currency),
        )


def get_fields_from_currency(currency: Currency) -> dict:
    """
    Return a dict of supported fields with normalized value

    :param currency: Currency instance
    :return:
    """
    fields = {}
    for (key, value) in currency.__dict__.items():
        if key.startswith("_"):
            continue
        elif key == "universal_dividend" and value is not None:
            # fix overflow with big numbers
            fields[key] = str(value)
        elif key == "monetary_mass" and value is not None:
            # fix overflow with big numbers
            fields[key] = str(value)
        else:
            fields[key] = value

    return fields


def get_currency_from_row(row: tuple) -> Currency:
    """
    Return a Currency instance from a result set row

    :param row: Result set row
    :return:
    """
    values = list(row)
    # # convert to integer from str type
    if values[5] is not None:
        values[5] = int(values[5])
    if values[6] is not None:
        values[6] = int(values[6])
    return Currency(*values)
