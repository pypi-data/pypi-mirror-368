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

import libnacl


def is_valid_ed25519(public_key: bytes) -> bool:
    """
    Check if a public key is valid on the Ed25519 curve.
    Equivalent to isValidEd25519 in TypeScript which uses isTorsionFree().

    This implementation performs the following checks:
    1. Correct length (32 bytes)
    2. Point is on the Ed25519 curve and has the correct order (is torsion-free)

    :param public_key: Public key as bytes

    :return:
    """
    if len(public_key) != 32:
        return False

    # Check for the identity point (all zeros) - not a valid public key
    if public_key == bytes([0] * 32):
        return False

    # Check for the point at infinity or other special encodings
    if (
        public_key[0] == 0x01
        and all(b == 0 for b in public_key[1:-1])
        and public_key[-1] == 0xFE
    ):
        return False

    # Now perform more rigorous checks
    return bool(libnacl.nacl.crypto_core_ed25519_is_valid_point(public_key))


def is_valid_sr25519(public_key: bytes) -> bool:
    """
    Check if a public key is valid on the Sr25519 curve.
    Equivalent to isValidSr25519 in TypeScript.

    Uses pysodium for Ristretto point validation, which is the basis for Sr25519.
    Sr25519 is based on Ristretto255, a specific encoding of Curve25519 points.

    :param public_key: Public key as bytes

    :return:
    """
    # import pysodium

    if len(public_key) != 32:
        return False

    # Sr25519 uses Ristretto points, which are a specific encoding of Curve25519 points
    # We can check if the point is valid by verifying it's a valid Ristretto point

    # we can use crypto_core_ristretto255_is_valid_point to check
    # if the provided bytes represent a valid Ristretto point
    is_valid = libnacl.nacl.crypto_core_ristretto255_is_valid_point(public_key)

    # Additionally, we should check that the point is not the identity element
    # and has the correct order (not a small subgroup element)
    if is_valid:
        # The identity element in Ristretto is all zeros
        if all(b == 0 for b in public_key):
            return False

        # In a complete implementation, we would also check for small subgroup elements
        # but this requires more complex operations beyond the scope of this example

        return True
    return False
