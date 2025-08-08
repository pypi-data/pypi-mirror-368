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

# Copyright  2014-2022 Vincent Texier <vit@free.fr>
#
# DuniterPy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# DuniterPy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import annotations

import base64
import binascii
import re
from hashlib import scrypt, sha256
from typing import Optional, Type, Union

import libnacl.sign
import pyaes
from base58 import b58decode, b58encode
from libnacl.utils import load_key

# Scrypt
SCRYPT_PARAMS = {"N": 4096, "r": 16, "p": 1, "seed_length": 32}


class ScryptParams:
    """
    Class to simplify handling of scrypt parameters
    """

    def __init__(
        self,
        n: int = SCRYPT_PARAMS["N"],
        r: int = SCRYPT_PARAMS["r"],
        p: int = SCRYPT_PARAMS["p"],
        seed_length: int = SCRYPT_PARAMS["seed_length"],
    ) -> None:
        """
        Init a ScryptParams instance with crypto parameters

        :param n: scrypt param N, default see constant SCRYPT_PARAMS
        :param r: scrypt param r, default see constant SCRYPT_PARAMS
        :param p: scrypt param p, default see constant SCRYPT_PARAMS
        :param seed_length: scrypt param seed_length, default see constant SCRYPT_PARAMS
        """
        self.N = n
        self.r = r
        self.p = p
        self.seed_length = seed_length


def ensure_bytes(data: Union[str, bytes]) -> bytes:
    """
    Convert data in bytes if data is a string

    :param data: Data
    :return:
    """
    if isinstance(data, str):
        return bytes(data, "utf-8")

    return data


def xor_bytes(b1: bytes, b2: bytes) -> bytearray:
    """
    Apply XOR operation on two bytes arguments

    :param b1: First bytes argument
    :param b2: Second bytes argument
    :return:
    """
    result = bytearray()
    for i1, i2 in zip(b1, b2):
        result.append(i1 ^ i2)
    return result


def hex_decode(data: bytes) -> bytes:
    """
    Convert hexadecimal byte string to bytes

    :param data: Data to decode
    :return:
    """
    return binascii.unhexlify(data)


def hex_encode(data: bytes) -> bytes:
    """
    Convert bytes to hexadecimal byte string

    :param data: Data to encode
    :return:
    """
    return binascii.hexlify(data)


def convert_seedhex_to_seed(seedhex: str) -> bytes:
    """
    Convert seedhex to seed

    :param seedhex: seed coded in hexadecimal base
    :return:
    """
    return bytes(hex_decode(seedhex.encode("utf-8")))


def convert_seed_to_seedhex(seed: bytes) -> str:
    """
    Convert seed to seedhex

    :param seed: seed
    :rtype str:
    """
    return hex_encode(seed).decode("utf-8")


class SigningKey(libnacl.sign.Signer):
    def __init__(self, seed: bytes) -> None:
        """
        Init pubkey property

        :param str seed: Hexadecimal seed string
        """
        super().__init__(seed)
        self.pubkey = b58encode(self.vk).decode("utf8")

    @classmethod
    def from_credentials(
        cls: Type[SigningKey],
        salt: Union[str, bytes],
        password: Union[str, bytes],
        scrypt_params: Optional[ScryptParams] = None,
    ) -> SigningKey:
        """
        Create a SigningKey object from credentials

        :param salt: Secret salt passphrase credential
        :param password: Secret password credential
        :param scrypt_params: ScryptParams instance or None
        """
        if scrypt_params is None:
            scrypt_params = ScryptParams()

        salt = ensure_bytes(salt)
        password = ensure_bytes(password)
        seed = scrypt(
            password,
            salt=salt,
            n=scrypt_params.N,
            r=scrypt_params.r,
            p=scrypt_params.p,
            dklen=scrypt_params.seed_length,
        )

        return cls(seed)

    @classmethod
    def from_credentials_file(
        cls, path: str, scrypt_params: Optional[ScryptParams] = None
    ) -> SigningKey:
        """
        Create a SigningKey object from a credentials file

        A file with the salt on the first line and the password on the second line

        :param path: Credentials file path
        :param scrypt_params: ScryptParams instance or None
        :return:
        """
        # capture credentials from file
        with open(path, encoding="utf-8") as fh:
            lines = fh.readlines()
            assert len(lines) > 1
            salt = lines[0].strip()
            password = lines[1].strip()

        return cls.from_credentials(salt, password, scrypt_params)

    def save_seedhex_file(self, path: str) -> None:
        """
        Save hexadecimal seed file from seed

        :param path: Authentication file path
        """
        seedhex = convert_seed_to_seedhex(self.seed)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(seedhex)

    @staticmethod
    def from_seedhex_file(path: str) -> SigningKey:
        """
        Return SigningKey instance from Seedhex file

        :param str path: Hexadecimal seed file path
        """
        with open(path, encoding="utf-8") as fh:
            seedhex = fh.read()
        return SigningKey.from_seedhex(seedhex)

    @classmethod
    def from_seedhex(cls: Type[SigningKey], seedhex: str) -> SigningKey:
        """
        Return SigningKey instance from Seedhex

        :param str seedhex: Hexadecimal seed string
        """
        regex_seedhex = re.compile("([0-9a-fA-F]{64})")
        match = re.search(regex_seedhex, seedhex)
        if not match:
            raise Exception("Error: Bad seed hexadecimal format")
        seedhex = match.groups()[0]
        seed = convert_seedhex_to_seed(seedhex)
        return cls(seed)

    def save_private_key(self, path: str) -> None:
        """
        Save authentication file

        :param path: Authentication file path
        """
        self.save(path)

    @staticmethod
    def from_private_key(path: str) -> SigningKey:
        """
        Read authentication file
        Add public key attribute

        :param path: Authentication file path
        """
        key = load_key(path)
        key.pubkey = b58encode(key.vk)
        return key

    def decrypt_seal(self, data: bytes) -> bytes:
        """
        Decrypt bytes data with a curve25519 version of the ed25519 key pair

        :param data: Encrypted data

        :return:
        """
        curve25519_public_key = libnacl.crypto_sign_ed25519_pk_to_curve25519(self.vk)
        curve25519_secret_key = libnacl.crypto_sign_ed25519_sk_to_curve25519(self.sk)
        return libnacl.crypto_box_seal_open(
            data, curve25519_public_key, curve25519_secret_key
        )

    @classmethod
    def from_pubsec_file(cls: Type[SigningKey], path: str) -> SigningKey:
        """
        Return SigningKey instance from Duniter WIF file

        :param path: Path to WIF file
        """
        with open(path, encoding="utf-8") as fh:
            pubsec_content = fh.read()

        # line patterns
        regex_pubkey = re.compile("pub: ([1-9A-HJ-NP-Za-km-z]{43,44})", re.MULTILINE)
        regex_signkey = re.compile("sec: ([1-9A-HJ-NP-Za-km-z]{87,90})", re.MULTILINE)

        # check public key field
        match = re.search(regex_pubkey, pubsec_content)
        if not match:
            raise Exception("Error: Bad format PubSec v1 file, missing public key")

        # check signkey field
        match = re.search(regex_signkey, pubsec_content)
        if not match:
            raise Exception("Error: Bad format PubSec v1 file, missing sec key")

        # capture signkey
        signkey_hex = match.groups()[0]

        # extract seed from signkey
        seed = bytes(b58decode(signkey_hex)[0:32])

        return cls(seed)

    def save_pubsec_file(self, path: str) -> None:
        """
        Save a Duniter PubSec file (PubSec) v1

        :param path: Path to file
        """
        # version
        version = 1

        # base58 encode keys
        base58_signing_key = b58encode(self.sk).decode("utf8")

        # save file
        content = f"Type: PubSec\n\
Version: {version}\n\
pub: {self.pubkey}\n\
sec: {base58_signing_key}"
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)

    @classmethod
    def from_wif_or_ewif_file(
        cls, path: str, password: Optional[str] = None
    ) -> SigningKey:
        """
        Return SigningKey instance from Duniter WIF or EWIF file

        :param path: Path to WIF of EWIF file
        :param password: Password needed for EWIF file
        """
        with open(path, encoding="utf-8") as fh:
            wif_content = fh.read()

        # check data field
        regex = re.compile("Data: ([1-9A-HJ-NP-Za-km-z]+)", re.MULTILINE)
        match = re.search(regex, wif_content)
        if not match:
            raise Exception("Error: Bad format WIF or EWIF v1 file")

        # capture hexa wif key
        wif_hex = match.groups()[0]
        return cls.from_wif_or_ewif_hex(wif_hex, password)

    @classmethod
    def from_wif_or_ewif_hex(
        cls, wif_hex: str, password: Optional[str] = None
    ) -> SigningKey:
        """
        Return SigningKey instance from Duniter WIF or EWIF in hexadecimal format

        :param wif_hex: WIF or EWIF string in hexadecimal format
        :param password: Password of EWIF encrypted seed
        """
        wif_bytes = b58decode(wif_hex)

        fi = wif_bytes[0:1]

        if fi == b"\x01":
            result = cls.from_wif_hex(wif_hex)
        elif fi == b"\x02" and password is not None:
            result = cls.from_ewif_hex(wif_hex, password)
        else:
            raise Exception("Error: Bad format: not WIF nor EWIF")

        return result

    @classmethod
    def from_wif_file(cls, path: str) -> SigningKey:
        """
        Return SigningKey instance from Duniter WIF file

        :param path: Path to WIF file
        """
        with open(path, encoding="utf-8") as fh:
            wif_content = fh.read()

        # check data field
        regex = re.compile("Data: ([1-9A-HJ-NP-Za-km-z]+)", re.MULTILINE)
        match = re.search(regex, wif_content)
        if not match:
            raise Exception("Error: Bad format WIF v1 file")

        # capture hexa wif key
        wif_hex = match.groups()[0]
        return cls.from_wif_hex(wif_hex)

    @classmethod
    def from_wif_hex(cls: Type[SigningKey], wif_hex: str) -> SigningKey:
        """
        Return SigningKey instance from Duniter WIF in hexadecimal format

        :param wif_hex: WIF string in hexadecimal format
        """
        wif_bytes = b58decode(wif_hex)
        if len(wif_bytes) != 35:
            raise Exception("Error: the size of WIF is invalid")

        # extract data
        checksum_from_wif = wif_bytes[-2:]
        fi = wif_bytes[0:1]
        seed = wif_bytes[1:-2]
        seed_fi = wif_bytes[0:-2]

        # check WIF format flag
        if fi != b"\x01":
            raise Exception("Error: bad format version, not WIF")

        # checksum control
        checksum = libnacl.crypto_hash_sha256(libnacl.crypto_hash_sha256(seed_fi))[0:2]
        if checksum_from_wif != checksum:
            raise Exception("Error: bad checksum of the WIF")

        return cls(seed)

    def save_wif_file(self, path: str) -> None:
        """
        Save a Wallet Import Format file (WIF) v1

        :param path: Path to file
        """
        # version
        version = 1

        # add format to seed (1=WIF,2=EWIF)
        seed_fi = b"\x01" + self.seed

        # calculate checksum
        sha256_v1 = libnacl.crypto_hash_sha256(seed_fi)
        sha256_v2 = libnacl.crypto_hash_sha256(sha256_v1)
        checksum = sha256_v2[0:2]

        # base58 encode key and checksum
        wif_key = b58encode(seed_fi + checksum).decode("utf8")

        content = f"Type: WIF\n\
Version: {version}\n\
Data: {wif_key}"
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)

    @classmethod
    def from_ewif_file(cls, path: str, password: str) -> SigningKey:
        """
        Return SigningKey instance from Duniter EWIF file

        :param path: Path to EWIF file
        :param password: Password of the encrypted seed
        """
        with open(path, encoding="utf-8") as fh:
            wif_content = fh.read()

        # check data field
        regex = re.compile("Data: ([1-9A-HJ-NP-Za-km-z]+)", re.MULTILINE)
        match = re.search(regex, wif_content)
        if not match:
            raise Exception("Error: Bad format EWIF v1 file")

        # capture ewif key
        ewif_hex = match.groups()[0]
        return cls.from_ewif_hex(ewif_hex, password)

    @classmethod
    def from_ewif_hex(
        cls: Type[SigningKey], ewif_hex: str, password: str
    ) -> SigningKey:
        """
        Return SigningKey instance from Duniter EWIF in hexadecimal format

        :param ewif_hex: EWIF string in hexadecimal format
        :param password: Password of the encrypted seed
        """
        ewif_bytes = b58decode(ewif_hex)
        if len(ewif_bytes) != 39:
            raise Exception("Error: the size of EWIF is invalid")

        # extract data
        fi = ewif_bytes[0:1]
        checksum_from_ewif = ewif_bytes[-2:]
        ewif_no_checksum = ewif_bytes[0:-2]
        salt = ewif_bytes[1:5]
        encryptedhalf1 = ewif_bytes[5:21]
        encryptedhalf2 = ewif_bytes[21:37]

        # check format flag
        if fi != b"\x02":
            raise Exception("Error: bad format version, not EWIF")

        # checksum control
        checksum = libnacl.crypto_hash_sha256(
            libnacl.crypto_hash_sha256(ewif_no_checksum)
        )[0:2]
        if checksum_from_ewif != checksum:
            raise Exception("Error: bad checksum of the EWIF")

        # SCRYPT
        password_bytes = password.encode("utf-8")
        scrypt_seed = scrypt(password_bytes, salt=salt, n=16384, r=8, p=8, dklen=64)
        derivedhalf1 = scrypt_seed[0:32]
        derivedhalf2 = scrypt_seed[32:64]

        # AES
        aes = pyaes.AESModeOfOperationECB(derivedhalf2)
        decryptedhalf1 = aes.decrypt(encryptedhalf1)
        decryptedhalf2 = aes.decrypt(encryptedhalf2)

        # XOR
        seed1 = xor_bytes(decryptedhalf1, derivedhalf1[0:16])
        seed2 = xor_bytes(decryptedhalf2, derivedhalf1[16:32])
        seed = bytes(seed1 + seed2)

        # Password Control
        signer = SigningKey(seed)
        salt_from_seed = libnacl.crypto_hash_sha256(
            libnacl.crypto_hash_sha256(b58decode(signer.pubkey))
        )[0:4]
        if salt_from_seed != salt:
            raise Exception("Error: bad Password of EWIF address")

        return cls(seed)

    def save_ewif_file(self, path: str, password: str) -> None:
        """
        Save an Encrypted Wallet Import Format file (WIF v2)

        :param path: Path to file
        :param password:
        """
        # version
        version = 1

        # add version to seed
        salt = libnacl.crypto_hash_sha256(
            libnacl.crypto_hash_sha256(b58decode(self.pubkey))
        )[0:4]

        # SCRYPT
        password_bytes = password.encode("utf-8")
        scrypt_seed = scrypt(password_bytes, salt=salt, n=16384, r=8, p=8, dklen=64)
        derivedhalf1 = scrypt_seed[0:32]
        derivedhalf2 = scrypt_seed[32:64]

        # XOR
        seed1_xor_derivedhalf1_1 = bytes(xor_bytes(self.seed[0:16], derivedhalf1[0:16]))
        seed2_xor_derivedhalf1_2 = bytes(
            xor_bytes(self.seed[16:32], derivedhalf1[16:32])
        )

        # AES
        aes = pyaes.AESModeOfOperationECB(derivedhalf2)
        encryptedhalf1 = aes.encrypt(seed1_xor_derivedhalf1_1)
        encryptedhalf2 = aes.encrypt(seed2_xor_derivedhalf1_2)

        # add format to final seed (1=WIF,2=EWIF)
        seed_bytes = b"\x02" + salt + encryptedhalf1 + encryptedhalf2

        # calculate checksum
        sha256_v1 = libnacl.crypto_hash_sha256(seed_bytes)
        sha256_v2 = libnacl.crypto_hash_sha256(sha256_v1)
        checksum = sha256_v2[0:2]

        # B58 encode final key string
        ewif_key = b58encode(seed_bytes + checksum).decode("utf8")

        # save file
        content = f"Type: EWIF\n\
Version: {version}\n\
Data: {ewif_key}"
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)

    @classmethod
    def from_ssb_file(cls: Type[SigningKey], path: str) -> SigningKey:
        """
        Return SigningKey instance from ScuttleButt .ssb/secret file

        :param path: Path to Scuttlebutt secret file
        """
        with open(path, encoding="utf-8") as fh:
            ssb_content = fh.read()

        # check data field
        regex = re.compile(
            '{\\s*"curve": "ed25519",\\s*"public": "(.+)\\.ed25519",\\s*"private":\\s*"(.+)\\.ed25519",\\s*"id":\\s*"@\\1.ed25519"\\s*}',
            re.MULTILINE,
        )
        match = re.search(regex, ssb_content)
        if not match:
            raise Exception("Error: Bad scuttlebutt secret file")

        # capture ssb secret key
        secret = match.groups()[1]

        # extract seed from secret
        seed = bytes(base64.b64decode(secret)[0:32])

        return cls(seed)

    @classmethod
    def from_dubp_mnemonic(
        cls, mnemonic: str, scrypt_params: Optional[ScryptParams] = None
    ) -> SigningKey:
        """
        Generate key pair instance from a DUBP mnemonic passphrase

        See https://git.duniter.org/documents/rfcs/blob/dubp-mnemonic/rfc/0014_Dubp_Mnemonic.md

        :param mnemonic: Passphrase generated from a mnemonic algorithm
        :param scrypt_params: ScryptParams instance (default=None)
        :return:
        """
        if scrypt_params is None:
            scrypt_params = ScryptParams()

        _password = mnemonic.encode("utf-8")  # type: bytes
        _salt = sha256(b"dubp" + _password).digest()  # type: bytes
        _seed = scrypt(
            password=_password,
            salt=_salt,
            n=scrypt_params.N,  # 4096
            r=scrypt_params.r,  # 16
            p=scrypt_params.p,  # 1
            dklen=scrypt_params.seed_length,  # 32
        )  # type: bytes
        return cls(_seed)
