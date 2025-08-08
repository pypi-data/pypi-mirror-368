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
from typing import Any, Dict, List, Optional
from uuid import UUID

from tikka.domains.currencies import Currencies
from tikka.domains.entities.account import Account, AccountCryptoType
from tikka.domains.entities.constants import DERIVATION_SCAN_MAX_NUMBER
from tikka.domains.entities.events import AccountEvent, LastTransferEvent
from tikka.domains.entities.identity import Identity
from tikka.domains.events import EventDispatcher
from tikka.domains.passwords import Passwords
from tikka.domains.transfers import Transfers
from tikka.domains.wallets import Wallets
from tikka.interfaces.adapters.network.indexer.accounts import IndexerAccountsInterface
from tikka.interfaces.adapters.network.node.accounts import NodeAccountsInterface
from tikka.interfaces.adapters.repository.accounts import AccountsRepositoryInterface
from tikka.interfaces.adapters.repository.file_wallets import (
    V1FileWalletsRepositoryInterface,
)
from tikka.libs.derivation import RE_TRANSPARENT_DERIVATION_PATH_PATTERN
from tikka.libs.keypair import Keypair
from tikka.libs.signing_key_v1 import SigningKey


class Accounts:
    """
    Accounts domain class
    """

    def __init__(
        self,
        repository: AccountsRepositoryInterface,
        network_node: NodeAccountsInterface,
        network_indexer: IndexerAccountsInterface,
        passwords: Passwords,
        wallets: Wallets,
        transfers: Transfers,
        file_wallets_repository: V1FileWalletsRepositoryInterface,
        currencies: Currencies,
        event_dispatcher: EventDispatcher,
    ):
        """
        Init Accounts domain

        :param repository: AccountsRepositoryInterface instance
        :param network_node: NodeAccountsInterface instance
        :param network_indexer: IndexerAccountsInterface instance
        :param passwords: Passwords domain instance
        :param wallets: Wallets domain instance
        :param transfers: Transfers domain instance
        :param file_wallets_repository: FileWalletsRepository adapter instance
        :param currencies: Currencies domain instance
        :param event_dispatcher: EventDispatcher instance
        """
        self.repository = repository
        self.network_node = network_node
        self.network_indexer = network_indexer
        self.passwords = passwords
        self.wallets = wallets
        self.transfers = transfers
        self.file_wallets_repository = file_wallets_repository
        self.currencies = currencies
        self.event_dispatcher = event_dispatcher

        # subscribe to events
        self.event_dispatcher.add_event_listener(
            LastTransferEvent.EVENT_TYPE_LAST_TRANSFER_CHANGED,
            self.on_last_transfer_changed,
        )

    @staticmethod
    def get_instance(address: str, name: Optional[str] = None) -> Account:
        """
        Return an Account instance from arguments

        :param address: Account address
        :param name: Optional account name
        :return:
        """
        return Account(address=address, name=name)

    def get_list(
        self,
        filters: Optional[Dict[str, Any]] = None,
        sort_column: Optional[str] = None,
        sort_order: str = AccountsRepositoryInterface.SORT_ORDER_ASCENDING,
    ):
        """
        Return accounts from repository with optional filters and sort_column

        :param filters: Dict with {column: value} filters or None
        :param sort_column: Sort column constant like COLUMN_ADDRESS or None
        :param sort_order: Sort order constant SORT_ORDER_ASCENDING or SORT_ORDER_DESCENDING
        :return:
        """
        # get accounts from database
        return self.repository.list(filters, sort_column, sort_order)

    def add(self, account: Account):
        """
        Add account

        :param account: Account instance
        :return:
        """
        # add account
        self.repository.add(account)

        # dispatch event
        event = AccountEvent(
            AccountEvent.EVENT_TYPE_ADD,
            account,
        )
        self.event_dispatcher.dispatch_event(event)

    def update(self, account: Account):
        """
        Update account

        :param account: Account instance
        :return:
        """
        self.repository.update(account)

        # dispatch event
        event = AccountEvent(
            AccountEvent.EVENT_TYPE_UPDATE,
            account,
        )
        self.event_dispatcher.dispatch_event(event)

    def get_by_index(self, index: int) -> Account:
        """
        Return account instance from index

        :param index: Index in account list
        :return:
        """
        return self.get_list()[index]

    def get_by_address(self, address: str) -> Optional[Account]:
        """
        Return account instance from address

        :param address: Account address
        :return:
        """
        for account in self.get_list():
            if account.address == address:
                return account

        return None

    def delete(self, account: Account) -> None:
        """
        Delete account in list and repository

        :param account: Account instance to delete
        :return:
        """
        self.repository.delete(account.address)

        # dispatch event
        event = AccountEvent(
            AccountEvent.EVENT_TYPE_DELETE,
            account,
        )
        self.event_dispatcher.dispatch_event(event)

    def delete_all(self) -> None:
        """
        Delete all accounts in repository

        :return:
        """
        self.repository.delete_all()

    def count(self) -> int:
        """
        Return total number of accounts

        :return:
        """
        return self.repository.count()

    def get_total_balance(self) -> int:
        """
        Return total balance of all accounts

        :return:
        """
        return self.repository.total_balance()

    def unlock(self, account: Account, wallet_password: str) -> bool:
        """
        Unlock wallet of account if wallet_password is OK

        :param account: Account instance
        :param wallet_password: Passphrase
        :return:
        """
        result = self.wallets.unlock(account.address, wallet_password)
        if result is False:
            return False

        self.update(account)
        return True

    def lock(self, account: Account):
        """
        Lock account

        :param account: Account instance
        :return:
        """
        self.wallets.lock(account.address)

        # dispatch event
        event = AccountEvent(
            AccountEvent.EVENT_TYPE_UPDATE,
            account,
        )
        self.event_dispatcher.dispatch_event(event)

    def forget_wallet(self, account: Account) -> None:
        """
        Delete stored wallet for this account

        :return:
        """
        self.wallets.delete(account.address)
        # update account display
        self.event_dispatcher.dispatch_event(
            AccountEvent(AccountEvent.EVENT_TYPE_UPDATE, account)
        )

    def network_update_balance(self, account: Account) -> Account:
        """
        Update account balance from network

        :param account: Account instance
        :return:
        """
        account.balance = self.network_node.get_balance(account.address)
        self.repository.update(account)

        return account

    def network_update_account(self, account: Account) -> Account:
        """
        Update
        - balance
        - total_transfers_count
        from network

        :param account: Account instance
        :return:
        """
        account.balance = self.network_node.get_balance(account.address)
        self.repository.update(account)

        return account

    def network_update_balances(self, accounts: List[Account]) -> None:
        """
        Update balances of account list from network

        :param accounts: Account list
        :return:
        """
        balances = self.network_node.get_balances(
            [account.address for account in accounts]
        )
        for account in accounts:
            account.balance = balances[account.address]
            self.repository.update(account)

    def network_get_balance(self, address: str) -> Optional[int]:
        """
        Return account balance from network

        :param address: Account address
        :return:
        """
        return self.network_node.get_balance(address)

    def network_get_balances(self, addresses: List[str]) -> Dict[str, Optional[int]]:
        """
        Return balances of address list from network

        :param addresses: Account address list
        :return:
        """
        return self.network_node.get_balances(addresses)

    def network_get_unclaimed_ud_balance(self, identity: Identity) -> int:
        """
        Return the unclaimed UD balance of identity from network

        :param identity: Identity instance
        :return:
        """
        balance = self.network_node.get_unclaimed_ud_balance(identity.first_eligible_ud)

        return balance

    def network_update_total_transfers_count(self, account: Account) -> Account:
        """
        Update account total_transfers_count from network

        :param account: Account to update
        :return:
        """
        account.total_transfers_count = (
            self.transfers.network_fetch_total_count_for_address(account.address)
        )
        self.repository.update(account)
        return account

    def list_by_category_id(self, category_id: Optional[UUID]) -> List[Account]:
        """
        Return all accounts in category_id

        :param category_id: Category ID
        :return:
        """
        result = []
        for account in self.get_list():
            # do not list derived accounts
            if account.category_id is None and account.root is not None:
                continue
            if account.category_id == category_id:
                result.append(account)

        return result

    def get_derivation_accounts(self, address: str) -> List[Account]:
        """
        Return list of derivation accounts from this root address

        :param address: Root account address
        :return:
        """
        filters = {AccountsRepositoryInterface.COLUMN_ROOT: address}
        # sort ascending by derivation path numbers
        return self.repository.list(
            filters=filters,
            sort_column=AccountsRepositoryInterface.COLUMN_PATH,
            sort_order=AccountsRepositoryInterface.SORT_ORDER_ASCENDING,
        )

    def create_new_account(
        self,
        mnemonic: str,
        language_code: str,
        derivation: str,
        crypto_type: AccountCryptoType,
        name: str,
        password: str,
        add_event: bool = True,
    ) -> Account:
        """
        Create a root account (read-only if derivation not empty) with mnemonic, if it does not already exist,
        and create a derived account if derivation is not "" as per RFC 0019.
        Return root account if derivation == "", derived account otherwise.

        :param mnemonic: Mnemonic phrase
        :param language_code: Mnemonic language code
        :param derivation: Derivation path
        :param crypto_type: Key type as AccountCryptoType instance
        :param name: Account name
        :param password: Wallet password
        :param add_event: Trigger event if True
        :return:
        """
        # get root keypair
        root_keypair = Keypair.create_from_mnemonic(
            mnemonic=mnemonic,
            language_code=language_code,
            crypto_type=crypto_type,
            ss58_format=self.currencies.get_current().ss58_format,
        )
        existing_account = self.get_by_address(root_keypair.ss58_address)
        if existing_account is None:
            # store new password for new root account
            if derivation == "":
                self.create_new_root_account(
                    mnemonic, language_code, crypto_type, name, password
                )
            else:
                # read-only root account
                self.create_new_root_account(
                    mnemonic, language_code, crypto_type, None, None, False
                )
            self.passwords.new(root_keypair, password)
            root_account = self.get_by_address(root_keypair.ss58_address)
        else:
            # get password of root account
            clear_password = self.passwords.get_clear_password(root_keypair)
            if clear_password is not None:
                password = clear_password
            root_account = existing_account

        if derivation == "":
            return root_account  # type: ignore

        # create keypair from mnemonic and path
        keypair = Keypair.create_from_uri(
            suri=mnemonic + derivation,
            language_code=language_code,
            crypto_type=crypto_type,
            ss58_format=self.currencies.get_current().ss58_format,
        )

        # create and store Account instance
        account = Account(
            keypair.ss58_address,
            crypto_type=crypto_type,
            legacy_v1=False,
            name=None if name == "" else name,
            root=root_account.address,  # type: ignore
            path=derivation,
        )

        if add_event:
            self.add(account)
        else:
            self.repository.add(account)

        # create and store Wallet instance
        wallet = self.wallets.create(keypair, password)
        if not self.wallets.exists(keypair.ss58_address):
            self.wallets.add(wallet)
            self.wallets.unlock(keypair.ss58_address, password)

        return account

    def create_new_root_account(
        self,
        mnemonic: str,
        language_code: str,
        crypto_type: AccountCryptoType,
        name: Optional[str],
        password: Optional[str],
        add_event: bool = True,
    ) -> Account:
        """
        Create and return a root account from mnemonic

        :param mnemonic: Mnemonic phrase
        :param language_code: Mnemonic language code
        :param crypto_type: Key type as AccountCryptoType instance
        :param name: Optional account name
        :param password: Optional Wallet password, if None no wallet will be created
        :param add_event: Optional, Default True to trigger add event
        :return:
        """

        # get root keypair
        root_keypair = Keypair.create_from_mnemonic(
            mnemonic=mnemonic,
            language_code=language_code,
            crypto_type=crypto_type,
            ss58_format=self.currencies.get_current().ss58_format,
        )

        root_account = Account(
            root_keypair.ss58_address, crypto_type=crypto_type, name=name
        )

        if add_event:
            self.add(root_account)
        else:
            # add root account in repository without event
            self.repository.add(root_account)

        if password is not None:
            # create and store Wallet instance
            wallet = self.wallets.new(root_keypair, password)
            self.wallets.unlock(wallet.address, password)
            # store new password for new V1 root account
            self.passwords.new(root_keypair, password)

        return root_account

    def create_new_root_account_v1_from_credentials(
        self, secret_id: str, password_id: str, name: str, password: str
    ) -> Optional[Account]:
        """
        Create an unlocked V1 root account with credentials secret_id and password_id

        :param secret_id: Secret ID
        :param password_id: Password ID
        :param name: Name of account
        :param password: Password of wallet
        :return:
        """
        signing_key = SigningKey.from_credentials(secret_id, password_id)
        return self.create_new_root_account_v1_from_seed(
            signing_key.seed.hex(), name, password
        )

    def create_new_root_account_v1_from_seed(
        self, seed_hex: str, name: str, password: str
    ) -> Optional[Account]:
        """
        Create an unlocked V1 root account from hexadecimal seed string

        :param seed_hex: Hexadecimal seed string
        :param name: Name of account
        :param password: Password of wallet
        :return:
        """
        keypair = Keypair.create_from_seed(
            seed_hex=seed_hex,
            ss58_format=self.currencies.get_current().ss58_format,
            crypto_type=AccountCryptoType.ED25519,
        )
        address = keypair.ss58_address
        account = self.get_by_address(address)
        if account is not None:
            return account

        # create and store Account instance
        account = Account(
            address,
            crypto_type=AccountCryptoType.ED25519,
            legacy_v1=True,
            name=None if name == "" else name,
        )
        self.add(account)

        # create and store Wallet instance
        wallet = self.wallets.create(keypair, password)
        self.wallets.add(wallet)
        self.wallets.unlock(wallet.address, password)

        # store new password for new V1 root account
        self.passwords.new(keypair, password)

        return account

    def get_available_derivation_list(self, root_account: Account) -> List[str]:
        """
        Return a list of derivation accounts from root account given, not already in account list

        :param root_account: Root account instance
        :return:
        """
        derived_accounts = self.get_derivation_accounts(root_account.address)
        available_derivation_list = []

        # get max existing transparent derivation number
        derivation_numbers: List[int] = []
        max_derivation_number = 0
        for account in derived_accounts:
            if account.path is None:
                continue
            match = RE_TRANSPARENT_DERIVATION_PATH_PATTERN.fullmatch(account.path)
            if match:
                account_derivation_number = int(match.group(1))
                derivation_numbers.append(account_derivation_number)
                max_derivation_number = max(
                    max_derivation_number, account_derivation_number
                )

        for derivation_number in range(
            0, max(max_derivation_number, DERIVATION_SCAN_MAX_NUMBER) + 1, 1
        ):
            if derivation_number not in derivation_numbers:
                # add next available transparent derivation path
                available_derivation_list.append(f"//{derivation_number}")

        return available_derivation_list

    def update_category_id(
        self, category_id: UUID, new_category_id: Optional[UUID]
    ) -> None:
        """
        Move all accounts with category_id to new_category_id

        :param category_id: Category ID
        :param new_category_id: New category ID
        :return:
        """
        for account in self.list_by_category_id(category_id):
            account.category_id = new_category_id
            self.update(account)

    def reset_password(
        self, root_keypair: Keypair, mnemonic: str, language_code: str, password: str
    ):
        """
        Update wallet encryption with password for all wallets derived from mnemonic

        :param root_keypair: Keypair of root account
        :param mnemonic: Mnemonic phrase
        :param language_code: Language code
        :param password: Password to set
        :return:
        """
        # if root wallet exists...
        if self.wallets.exists(root_keypair.ss58_address):
            # update root wallet with new password
            self.wallets.update(self.wallets.create(root_keypair, password))

        for account in self.get_derivation_accounts(root_keypair.ss58_address):
            # if account wallet exists...
            if self.wallets.exists(account.address) and account.path is not None:
                # update account wallet with new password
                suri = mnemonic + account.path
                keypair = Keypair.create_from_uri(
                    suri=suri,
                    language_code=language_code,
                    crypto_type=root_keypair.crypto_type,
                    ss58_format=root_keypair.ss58_format,
                )
                self.wallets.update(self.wallets.create(keypair, password))

    def on_last_transfer_changed(self, event: LastTransferEvent):
        """
        Update account with last transfer timestamp got from network

        :param event: LastTransferEvent instance
        :return:
        """
        account = self.get_by_address(event.address)
        if account is not None:
            account.last_transfer_timestamp = event.transfer.timestamp
            self.repository.update(account)

    def network_is_legacy_v1(self, address: str) -> bool:
        """
        Return True if account is a legacy v1 account (present in genesis)

        :param address: ss58 account address
        :return:
        """
        return self.network_indexer.is_legacy_v1(address)
