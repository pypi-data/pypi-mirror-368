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
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from tikka.adapters.network.node.substrate_client import ExtrinsicReceipt
from tikka.domains.currencies import Currencies
from tikka.domains.entities.account import Account
from tikka.domains.entities.events import TransferEvent
from tikka.domains.entities.transfer import Transfer
from tikka.domains.events import EventDispatcher
from tikka.domains.wallets import Wallets
from tikka.interfaces.adapters.network.indexer.transfers import (
    IndexerTransfersInterface,
)
from tikka.interfaces.adapters.network.node.transfers import NodeTransfersInterface
from tikka.interfaces.adapters.repository.transfers import TransfersRepositoryInterface
from tikka.libs.keypair import Keypair


def format_datetime(dt: datetime) -> str:
    """
    Formate une date en OFX (YYYYMMDDHHMMSS).

    :param dt: Datetime data
    :return:
    """
    return dt.strftime("%Y%m%d%H%M%S")


class Transfers:
    """
    Transfers domain class
    """

    def __init__(
        self,
        wallets: Wallets,
        repository: TransfersRepositoryInterface,
        currencies: Currencies,
        node_transfers: NodeTransfersInterface,
        indexer_transfers: IndexerTransfersInterface,
        event_dispatcher: EventDispatcher,
    ):
        """
        Init Transfers domain

        :param wallets: Wallets domain
        :param repository: TransfersRepositoryInterface adapter instance
        :param currencies: Currencies domain instance
        :param node_transfers: NodeTransfersInterface adapter instance
        :param event_dispatcher: EventDispatcher instance
        """
        self.wallets = wallets
        self.repository = repository
        self.currencies = currencies
        self.node_transfers = node_transfers
        self.indexer_transfers = indexer_transfers
        self.event_dispatcher = event_dispatcher

    def add(self, address: str, transfer: Transfer):
        """
        Add transfer to repository

        :param transfer: Transfer instance
        :return:
        """
        self.repository.add(address, transfer)

    def delete(self, transfer_id: str):
        """
        Delete transfer with transfer_id in repository

        :param transfer_id: Transfer ID to delete
        :return:
        """
        self.repository.delete(transfer_id)

    def delete_all(self) -> None:
        """
        Delete all transfers in repository

        :return:
        """
        self.repository.delete_all()

    def count(self, address: str) -> int:
        """
        Return total number of transfers issued and received by address

        :return:
        """
        return self.repository.count(address)

    def list(
        self,
        address: str,
        filters: Optional[Dict[str, Any]] = None,
        sort_column: str = TransfersRepositoryInterface.COLUMN_TIMESTAMP,
        sort_order: str = TransfersRepositoryInterface.SORT_ORDER_DESCENDING,
        limit: int = 10,
        offset: int = 0,
    ) -> List[Transfer]:
        """
        List transfers from and to address, from repository with optional filters and sort_column

        :param address: Account address
        :param filters: Dict with {column: value} filters or None
        :param sort_column: Sort column constant, TransfersRepositoryInterface.COLUMN_TIMESTAMP by default
        :param sort_order: Sort order constant, TransfersRepositoryInterface.SORT_ORDER_DESCENDING by default
        :param limit: Number of rows to return
        :param offset: Offset of first row to return
        :return:
        """
        return self.repository.list(
            address, filters, sort_column, sort_order, limit, offset
        )

    def network_fetch_history_for_account(self, account: Account, limit: int) -> None:
        """
        Fetch history of last transfers from and to account

        :param account: Account instance to filter issuers and receivers
        :param limit: Maximum number of transfers to fetch
        :return:
        """
        transfers = self.indexer_transfers.list(account.address, limit=limit)
        if len(transfers) > 0:
            self.repository.set_history(account.address, transfers)
            # account.last_transfer_timestamp = transfers[0].timestamp
            # # dispatch event
            # event = LastTransferEvent(
            #     LastTransferEvent.EVENT_TYPE_LAST_TRANSFER_CHANGED,
            #     account.address,
            #     transfers[0],
            # )
            # self.event_dispatcher.dispatch_event(event)

    def network_fetch_total_count_for_address(self, address: str) -> int:
        """
        Fetch total count of transfers from and to address

        :param address: Address to filter issuers and receivers
        :return:
        """
        return self.indexer_transfers.count(address)

    def network_fees(
        self, sender_keypair: Keypair, recipient_address: str, amount: int
    ) -> Optional[int]:
        """
        Fetch transfer fees from network and return it if request is successful

        :param sender_keypair: Sender Keypair instance
        :param recipient_address: Recipient address
        :param amount: Amount in blockchain unit
        :return:
        """
        return self.node_transfers.fees(sender_keypair, recipient_address, amount)

    def network_send(
        self, sender_keypair: Keypair, recipient_address: str, amount: int
    ) -> Optional[ExtrinsicReceipt]:
        """
        Send transfer to network and return ExtrinsicReceipt if request is successful

        :param sender_keypair: Sender Keypair instance
        :param recipient_address: Recipient address
        :param amount: Amount in blockchain unit
        :return:
        """
        receipt = self.node_transfers.send(sender_keypair, recipient_address, amount)

        if receipt is not None and receipt.is_success is True:
            # dispatch event
            event = TransferEvent(
                TransferEvent.EVENT_TYPE_SENT,
            )
            self.event_dispatcher.dispatch_event(event)

        return receipt

    def network_send_with_comment(
        self, sender_keypair: Keypair, recipient_address: str, amount: int, comment: str
    ) -> Optional[ExtrinsicReceipt]:
        """
        Send transfer to network and return ExtrinsicReceipt if request is successful

        :param sender_keypair: Sender Keypair instance
        :param recipient_address: Recipient address
        :param amount: Amount in blockchain unit
        :param comment: Comment from user
        :return:
        """
        receipt = self.node_transfers.send_with_comment(
            sender_keypair, recipient_address, amount, comment
        )

        if receipt is not None and receipt.is_success is True:
            # dispatch event
            event = TransferEvent(
                TransferEvent.EVENT_TYPE_SENT,
            )
            self.event_dispatcher.dispatch_event(event)

        return receipt

    def network_send_all(
        self, sender_keypair: Keypair, recipient_address: str, keep_alive: bool = False
    ) -> Optional[ExtrinsicReceipt]:
        """
        Send transfer to network and return ExtrinsicReceipt if request is successful

        :param sender_keypair: Sender Keypair instance
        :param recipient_address: Recipient address
        :param keep_alive: Optional, default False
        :return:
        """
        receipt = self.node_transfers.transfer_all(
            sender_keypair, recipient_address, keep_alive
        )

        if receipt is not None and receipt.is_success is True:
            # dispatch event
            event = TransferEvent(
                TransferEvent.EVENT_TYPE_SENT,
            )
            self.event_dispatcher.dispatch_event(event)

        return receipt

    def export_as_ofx(
        self,
        filepath: str,
        address: str,
        from_datetime: Optional[datetime] = None,
        to_datetime: Optional[datetime] = None,
    ):
        """
        Export transfers for address in an OFX format file

        :param filepath: Path of the file
        :param address: Account address
        :param from_datetime: Optional period start date
        :param to_datetime: Optional period end date
        :return:
        """
        batch_size = 100
        offset = 0

        with open(filepath, "w", encoding="utf-8") as f:
            # Écriture de l'en-tête OFX
            f.write(
                f"""OFXHEADER:100
    DATA:OFXSGML
    VERSION:102
    SECURITY:NONE
    ENCODING:USASCII
    CHARSET:1252
    COMPRESSION:NONE
    OLDFILEUID:NONE
    NEWFILEUID:NONE
    
    <OFX>
        <BANKMSGSRSV1>
            <STMTTRNRS>
                <STMTRS>
                    <CURDEF>EUR</CURDEF>
                    <BANKACCTFROM>
                        <BANKID>{self.currencies.get_current().name}</BANKID>
                        <ACCTID>{address}</ACCTID>
                        <ACCTTYPE>CHECKING</ACCTTYPE>
                    </BANKACCTFROM>
                    <BANKTRANLIST>
    """
            )

            while True:
                # Récupérer un lot de 100 transferts depuis GraphQL
                transfers = self.indexer_transfers.list(
                    address=address,
                    limit=batch_size,
                    offset=offset,
                    from_datetime=from_datetime,
                    to_datetime=to_datetime,
                )

                if not transfers:
                    break  # Arrêter si plus de transferts à récupérer

                total_amount: float = 0.0
                for transfer in transfers:
                    if transfer.issuer_address != address:
                        amount_sign = 1
                        name = (
                            f"{transfer.issuer_address} - {transfer.issuer_identity_name}#{transfer.issuer_identity_index}"
                            if transfer.issuer_identity_name
                            else transfer.issuer_address
                        )
                    else:
                        amount_sign = -1
                        name = (
                            f"{transfer.receiver_address} - {transfer.receiver_identity_name}#{transfer.receiver_identity_index}"
                            if transfer.receiver_identity_name
                            else transfer.receiver_address
                        )
                    total_amount += (
                        transfer.amount / 100
                    ) * amount_sign  # Convert cents to dollars

                    f.write(
                        f"""
                    <STMTTRN>
                        <TRNTYPE>XFER</TRNTYPE>
                        <DTPOSTED>{format_datetime(transfer.timestamp)}</DTPOSTED>
                        <TRNAMT>{(transfer.amount / 100)*amount_sign:.2f}</TRNAMT>
                        <FITID>{transfer.id}</FITID>
                        <NAME>{name}</NAME>
                        <MEMO>{transfer.comment or ''}</MEMO>
                    </STMTTRN>
                    """
                    )

                offset += batch_size  # Passer au lot suivant

            current_datetime = format_datetime(datetime.utcnow())

            # Écriture du pied de fichier OFX
            f.write(
                f"""
                    </BANKTRANLIST>
                    <LEDGERBAL>
                        <BALAMT>{total_amount:.2f}</BALAMT>
                        <DTASOF>{current_datetime}</DTASOF>
                    </LEDGERBAL>
                    <AVAILBAL>
                        <BALAMT>{total_amount:.2f}</BALAMT>
                        <DTASOF>{current_datetime}</DTASOF>
                    </AVAILBAL>
                </STMTRS>
            </STMTTRNRS>
        </BANKMSGSRSV1>
    </OFX>
    """
            )

        logging.debug(f"Export OFX terminé : {filepath}")
