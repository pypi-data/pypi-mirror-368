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

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, TypeVar

SmithType = TypeVar("SmithType", bound="Smith")


class SmithStatus(int, Enum):
    INVITED = 0
    PENDING = 1
    SMITH = 2
    EXCLUDED = 3


@dataclass
class Smith:
    identity_index: int
    status: SmithStatus
    expire_on: Optional[datetime]
    certifications_received: List[int] = field(default_factory=lambda: list())
    certifications_issued: List[int] = field(default_factory=lambda: list())
