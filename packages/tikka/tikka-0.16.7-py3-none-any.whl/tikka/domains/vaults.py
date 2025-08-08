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
from typing import List

from tikka.domains.accounts import Accounts
from tikka.domains.currencies import Currencies
from tikka.domains.entities.account import Account, AccountCryptoType
from tikka.domains.entities.constants import DERIVATION_SCAN_MAX_NUMBER
from tikka.interfaces.adapters.network.node.accounts import NodeAccountsInterface
from tikka.libs.keypair import Keypair


class Vaults:
    """
    Vaults domain class
    """

    def __init__(
        self,
        network: NodeAccountsInterface,
        accounts: Accounts,
        currencies: Currencies,
    ):
        """
        Init Vaults domain

        :param network: NetworkAccountsInterface instance
        :param accounts: Accounts domain instance
        :param currencies: Currencies domain instance
        """
        self.network = network
        self.accounts = accounts
        self.currencies = currencies

    def network_get_derived_accounts(
        self,
        root_address: str,
        mnemonic: str,
        language_code: str,
        crypto_type: AccountCryptoType,
    ) -> List[Account]:
        """
        Return list of derived accounts of root_address from network

        :param root_address: Root account address
        :param mnemonic: Mnemonic phrase
        :param language_code: Language code
        :param crypto_type: Crypto type

        :return:
        """
        derived_accounts = []
        addresses = []
        for derivation_number in range(0, DERIVATION_SCAN_MAX_NUMBER + 1):
            derivation = f"//{derivation_number}"
            # # debug on Alice,...
            # if derivation == "//0":
            #     derivation = "//Alice"
            # if derivation == "//1":
            #     derivation = "//Bob"
            # if derivation == "//2":
            #     derivation = "//Charlie"
            # if derivation == "//3":
            #     derivation = "//Dave"

            suri = mnemonic + derivation
            keypair = Keypair.create_from_uri(
                suri,
                language_code=language_code,
                ss58_format=self.currencies.get_current().ss58_format,
                crypto_type=crypto_type,
            )
            derived_account = self.accounts.get_by_address(keypair.ss58_address)
            if derived_account is None:
                derived_account = self.accounts.get_instance(
                    keypair.ss58_address, f"{derivation}"
                )
            derived_account.root = root_address
            derived_account.path = derivation
            derived_accounts.append(derived_account)
            addresses.append(keypair.ss58_address)

        balances = self.accounts.network_get_balances(addresses)
        existing_accounts = []
        for derived_account in derived_accounts:
            if balances[derived_account.address] is not None:
                derived_account.balance = balances[derived_account.address]
                existing_accounts.append(derived_account)

        return existing_accounts
