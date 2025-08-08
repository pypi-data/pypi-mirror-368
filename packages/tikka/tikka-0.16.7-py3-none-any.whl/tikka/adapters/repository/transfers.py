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
from functools import reduce
from typing import Any, Dict, List, Optional

from dateutil import parser
from sql import Column, Delete, Flavor, Table
from sql.operators import And, Equal

from tikka.domains.entities.transfer import Transfer
from tikka.interfaces.adapters.repository.db_repository import DBRepositoryInterface
from tikka.interfaces.adapters.repository.transfers import TransfersRepositoryInterface

TABLE_NAME = "transfers"
ACCOUNTS_TRANSFERS_TABLE_NAME = "accounts_transfers"

# create sql table wrapper
sql_transfers_table = Table(TABLE_NAME)


class DBTransfersRepository(TransfersRepositoryInterface, DBRepositoryInterface):
    """
    DBTransfersRepository class
    """

    def list(
        self,
        address: str,
        filters: Optional[Dict[str, Any]] = None,
        sort_column: str = TransfersRepositoryInterface.COLUMN_TIMESTAMP,
        sort_order: str = TransfersRepositoryInterface.SORT_ORDER_DESCENDING,
        limit: int = 10,
        offset: int = 0,
    ) -> List[Transfer]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            TransfersRepositoryInterface.list.__doc__
        )

        sql_columns = {
            TransfersRepositoryInterface.COLUMN_ID: sql_transfers_table.id,
            TransfersRepositoryInterface.COLUMN_ISSUER_ADDRESS: sql_transfers_table.issuer_address,
            TransfersRepositoryInterface.COLUMN_ISSUER_IDENTITY_INDEX: sql_transfers_table.issuer_identity_index,
            TransfersRepositoryInterface.COLUMN_ISSUER_IDENTITY_NAME: sql_transfers_table.issuer_identity_name,
            TransfersRepositoryInterface.COLUMN_RECEIVER_ADDRESS: sql_transfers_table.receiver_address,
            TransfersRepositoryInterface.COLUMN_RECEIVER_IDENTITY_INDEX: sql_transfers_table.receiver_identity_index,
            TransfersRepositoryInterface.COLUMN_RECEIVER_IDENTITY_NAME: sql_transfers_table.receiver_identity_name,
            TransfersRepositoryInterface.COLUMN_AMOUNT: sql_transfers_table.amount,
            TransfersRepositoryInterface.COLUMN_TIMESTAMP: sql_transfers_table.timestamp,
            TransfersRepositoryInterface.COLUMN_COMMENT: sql_transfers_table.comment,
            TransfersRepositoryInterface.COLUMN_COMMENT_TYPE: sql_transfers_table.comment_type,
        }

        sql_accounts_transfers_join = sql_transfers_table.join(
            Table(ACCOUNTS_TRANSFERS_TABLE_NAME)
        )
        sql_accounts_transfers_join.condition = Equal(
            sql_accounts_transfers_join.right.account_id, address
        ) & Equal(sql_accounts_transfers_join.right.transfer_id, sql_transfers_table.id)

        # if sort column...
        if sort_column is not None:
            # set sort column
            sql_sort_colum: Column = sql_columns[sort_column]
            # create select query wrapper with order by
            sql_select = sql_accounts_transfers_join.select(
                *sql_columns.values(),
                order_by=sql_sort_colum.asc
                if sort_order == TransfersRepositoryInterface.SORT_ORDER_ASCENDING
                else sql_sort_colum.desc,
                limit=limit,
                offset=offset,
            )
        else:
            #  create select query wrapper without order by
            sql_select = sql_accounts_transfers_join.select(
                *sql_columns.values(), limit=limit, offset=offset
            )

        # create where conditions
        conditions = []
        if filters is not None:
            for key, value in filters.items():
                conditions.append(sql_columns[key] == value)

        # conditions are added with and operator
        def and_(a, b):
            return And((a, b))

        if len(conditions) > 0:
            sql_select.where = reduce(and_, conditions)

        # config sql with ? as param style
        Flavor.set(Flavor(paramstyle="qmark"))

        sql, args = tuple(sql_select)
        result_set = self.client.select(sql, args)

        list_ = []
        for row in result_set:
            list_.append(get_transfer_from_row(row))

        return list_

    def add(self, address: str, transfer: Transfer) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            TransfersRepositoryInterface.add.__doc__
        )

        # insert only non hidden fields
        self.client.insert(
            TABLE_NAME,
            **get_fields_from_transfer(transfer),
        )
        # insert in cross table
        self.client.insert(
            ACCOUNTS_TRANSFERS_TABLE_NAME, account_id=address, transfer_id=transfer.id
        )

    def set_history(self, address: str, transfers: List[Transfer]) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            TransfersRepositoryInterface.set_history.__doc__
        )
        # delete current account history in cross table
        self.client.delete(ACCOUNTS_TRANSFERS_TABLE_NAME, account_id=address)

        # delete orphan transfers not in cross table
        sql_accounts_transfers_table = Table(ACCOUNTS_TRANSFERS_TABLE_NAME)
        sql_delete = Delete(
            sql_transfers_table,
            where=~sql_transfers_table.id.in_(
                sql_accounts_transfers_table.select(
                    sql_accounts_transfers_table.transfer_id
                )
            ),
        )
        sql, args = tuple(sql_delete)
        self.client.execute(sql)

        if len(transfers) > 0:
            # batch insert of transfers
            transfer_rows = []
            account_transfer_rows = []
            for transfer in transfers:
                transfer_rows.append(get_fields_from_transfer(transfer))
                account_transfer_rows.append(
                    {"account_id": address, "transfer_id": transfer.id}
                )

            self.client.insert_many(TABLE_NAME, transfer_rows)
            self.client.insert_many(
                ACCOUNTS_TRANSFERS_TABLE_NAME, account_transfer_rows
            )

    def delete(self, transfer_id: str) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            TransfersRepositoryInterface.delete.__doc__
        )
        self.client.delete(TABLE_NAME, id=transfer_id)

    def delete_all(self) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            TransfersRepositoryInterface.delete_all.__doc__
        )
        self.client.clear(TABLE_NAME)

    def count(self, address) -> int:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            TransfersRepositoryInterface.count.__doc__
        )
        row = self.client.select_one(
            f"SELECT count(transfer_id) FROM {ACCOUNTS_TRANSFERS_TABLE_NAME} WHERE account_id=?",
            (address,),
        )
        if row is None:
            return 0

        return row[0]


def get_fields_from_transfer(transfer: Transfer) -> dict:
    """
    Return a dict of supported fields with normalized value

    :param transfer: Transfer instance
    :return:
    """
    fields = {}
    for (key, value) in transfer.__dict__.items():
        if key.startswith("_"):
            continue
        fields[key] = value

    return fields


def get_transfer_from_row(row: tuple) -> Transfer:
    """
    Return a Transfer instance from a result set row

    :param row: Result set row
    :return:
    """
    values: List[Any] = []
    count = 0
    for value in row:
        if count == 8:
            # python datetime does not handle timezone until 3.11
            values.append(parser.parse(value))
        else:
            values.append(value)
        count += 1

    return Transfer(*values)  # pylint: disable=no-value-for-parameter
