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
from dataclasses import dataclass
from typing import Optional


@dataclass
class Currency:

    code_name: str
    name: str
    ss58_format: int
    token_decimals: Optional[int] = None
    token_symbol: Optional[str] = None
    universal_dividend: Optional[int] = None
    monetary_mass: Optional[int] = None
    members_count: Optional[int] = None
    block_duration: int = 6000
    epoch_duration: int = 3600000

    certification_number_to_be_member: Optional[int] = None
    minimum_delay_between_two_membership_renewals: Optional[int] = None
    validity_duration_of_membership: Optional[int] = None
    minimum_certifications_received_to_be_certifier: Optional[int] = None
    validity_duration_of_certification: Optional[int] = None
    minimum_delay_between_two_certifications: Optional[int] = None
    maximum_number_of_certifications_per_member: Optional[int] = None
    maximum_distance_in_step: Optional[int] = None
    minimum_percentage_of_remote_referral_members_to_be_member: Optional[int] = None
    identity_automatic_revocation_period: Optional[int] = None
    minimum_delay_between_changing_identity_owner: Optional[int] = None
    confirm_identity_period: Optional[int] = None
    identity_deletion_after_revocation: Optional[int] = None
    minimum_delay_between_identity_creation: Optional[int] = None
    identity_validation_period: Optional[int] = None
    maximum_certifications_per_smith: Optional[int] = None
    number_of_certifications_to_become_smith: Optional[int] = None
    maximum_inactivity_duration_allowed_for_smith: Optional[int] = None
    genesis_hash: Optional[str] = None
