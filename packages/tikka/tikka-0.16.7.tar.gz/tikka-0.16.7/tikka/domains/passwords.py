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
import random
from typing import List, Optional

from Crypto.Cipher import ChaCha20_Poly1305
from Crypto.Protocol.KDF import scrypt

from tikka.domains.entities.constants import PASSWORDS_NONCE_SIZE
from tikka.domains.entities.password import Password
from tikka.interfaces.adapters.repository.passwords import PasswordsRepositoryInterface
from tikka.libs.keypair import Keypair


class Passwords:
    """
    Passwords domain class
    """

    chacha_key_length = 32
    scrypt_n = 8
    scrypt_r = 1
    scrypt_p = 16

    def __init__(self, repository: PasswordsRepositoryInterface):
        """
        Init Passwords domain

        :param repository: Database adapter instance
        """
        self.repository = repository

    @staticmethod
    def create(keypair: Keypair, clear_password: str) -> Password:
        """
        Return an encrypted Password instance

        :param keypair: Keypair instance
        :param clear_password: Clear password
        :return:
        """
        nonce = random_bytes(PASSWORDS_NONCE_SIZE)
        key = scrypt(
            keypair.private_key.hex(),
            keypair.public_key.hex(),
            Passwords.chacha_key_length,
            Passwords.scrypt_n,
            Passwords.scrypt_r,
            Passwords.scrypt_p,
        )
        assert isinstance(key, bytes)
        cypher = ChaCha20_Poly1305.new(key=key, nonce=nonce)
        encrypted_password, mac_tag = cypher.encrypt_and_digest(
            clear_password.encode("utf-8")
        )
        return Password(
            root=keypair.ss58_address,
            encrypted_password=encrypted_password.hex(),
            encryption_nonce=nonce.hex(),
            encryption_mac_tag=mac_tag.hex(),
        )

    def new(self, keypair: Keypair, clear_password: str) -> Password:
        """
        Create Password instance and add it to repository
        if password already exists, update password

        :param keypair: Seed hexadecimal string
        :param clear_password: Password string
        :return:
        """
        password = self.create(keypair, clear_password)

        if self.exists(keypair.ss58_address):
            self.update(password)
        else:
            self.add(password)

        return password

    def add(self, password: Password):
        """
        Add Password instance in repository

        :param password: Password instance
        :return:
        """
        self.repository.add(password)

    def get(self, root: str) -> Optional[Password]:
        """
        Return Password instance from root address

        :param root: Root address
        :return:
        """
        return self.repository.get(root)

    def get_clear_password(self, keypair: Keypair) -> Optional[str]:
        """
        Get clear password from Keypair

        :param keypair: Keypair of root account
        :return:
        """
        password = self.get(keypair.ss58_address)
        if password is None:
            return None
        key = scrypt(
            keypair.private_key.hex(),
            keypair.public_key.hex(),
            Passwords.chacha_key_length,
            Passwords.scrypt_n,
            Passwords.scrypt_r,
            Passwords.scrypt_p,
        )
        assert isinstance(key, bytes)
        cypher = ChaCha20_Poly1305.new(
            key=key, nonce=bytes.fromhex(password.encryption_nonce)
        )
        return cypher.decrypt_and_verify(
            bytes.fromhex(password.encrypted_password),
            bytes.fromhex(password.encryption_mac_tag),
        ).decode("utf-8")

    def update(self, password: Password):
        """
        Update password

        :param password: Password instance
        :return:
        """
        self.repository.update(password)

    def delete(self, root: str) -> None:
        """
        Delete password in repository

        :param root: Root address of password to delete
        :return:
        """
        self.repository.delete(root)

    def delete_all(self) -> None:
        """
        Delete all passwords in repository

        :return:
        """
        self.repository.delete_all()

    def exists(self, root: str) -> bool:
        """
        Return True if password with root address exists in repository

        :param root: Root address to check
        :return:
        """
        return self.repository.exists(root)

    def list(self) -> List[Password]:
        """
        Return list of all passwords

        :return:
        """
        return self.repository.list()


def random_bytes(size: int) -> bytes:
    """
    Return random bytes of given length

    :param size: Size of nonce in bytes
    :return:
    """
    return bytearray(random.getrandbits(8) for _ in range(size))
