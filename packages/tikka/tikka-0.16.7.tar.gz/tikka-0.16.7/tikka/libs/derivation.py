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
import re
from typing import Optional

from tikka.domains.entities.constants import DERIVATION_PATH_MEMBER
from tikka.libs.keypair import Keypair

RE_TRANSPARENT_DERIVATION_PATH_PATTERN = re.compile(r"^\/\/(\d+)$")


def get_root_address_from_suri(
    suri: str, crypto_type: int, ss58_format: int, language_code: str
) -> str:
    """
    Return the root address of a derivation path from a Substrate URI

    :param suri: Substrate URI
    :param crypto_type: KeypairType constant
    :param ss58_format: Blockchain address format number
    :param language_code: Mnemonic language code as Keypair.MnemonicLanguageCode constant
    :return:
    """
    parts = re.split("/", suri)
    mnemonic = parts[0]
    keypair = Keypair.create_from_mnemonic(
        mnemonic,
        crypto_type=crypto_type,
        ss58_format=ss58_format,
        language_code=language_code,
    )

    return keypair.ss58_address


def get_path_from_suri(suri: str) -> Optional[str]:
    """
    Return the derivation path from a Substrate URI

    :param suri: Substrate URI
    :return:
    """
    parts = re.split("/", suri.strip())
    mnemonic = parts[0]
    path = suri.replace(mnemonic, "")
    return None if path == "" else path


def detect_derivation(
    address: str, mnemonic: str, langage_code: str, ss58_format: int, crypto_type: int
) -> Optional[str]:
    """
    Detect derivation to add to mnemonic to find address

    :param address: SS58 address
    :param mnemonic: Mnemonic phrase
    :param langage_code: Mnemonic langage code
    :param ss58_format: SS58 Format number
    :param crypto_type: Crypto type constant
    :return:
    """
    # detect root address (empty derivation)
    keypair = Keypair.create_from_mnemonic(
        mnemonic,
        language_code=langage_code,
        ss58_format=ss58_format,
        crypto_type=crypto_type,
    )
    if keypair.ss58_address == address:
        return ""

    # detect member account
    suri = mnemonic + DERIVATION_PATH_MEMBER
    keypair = Keypair.create_from_uri(
        suri,
        language_code=langage_code,
        ss58_format=ss58_format,
        crypto_type=crypto_type,
    )
    if keypair.ss58_address == address:
        return DERIVATION_PATH_MEMBER

    # detect transparent derivation (//[even])
    for account_id in range(2, 100, 2):
        derivation = f"//{account_id}"
        suri = mnemonic + derivation
        keypair = Keypair.create_from_uri(
            suri,
            language_code=langage_code,
            ss58_format=ss58_format,
            crypto_type=crypto_type,
        )
        if keypair.ss58_address == address:
            return derivation

    return None
