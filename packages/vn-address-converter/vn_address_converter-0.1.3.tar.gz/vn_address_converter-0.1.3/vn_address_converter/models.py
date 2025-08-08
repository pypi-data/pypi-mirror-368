from dataclasses import dataclass
from typing import Optional
from enum import Enum


class AddressLevel(Enum):
    PROVINCE = 'province'
    DISTRICT = 'district'
    WARD = 'ward'
    STREET = 'street'


class MappingMissingError(Exception):
    """Exception raised when address mapping is missing for a given level and value."""
    
    def __init__(self, level: AddressLevel, value: str, message: str = None):
        self.level = level
        self.value = value
        if message is None:
            message = f'{level.value.capitalize()} not found in mapping: {value}'
        super().__init__(message)


@dataclass
class Address:
    """Address dataclass represents a Vietnamese address with optional fields."""
    street_address: Optional[str] = None  # Street address (optional)
    ward: Optional[str] = None           # Ward/commune name (optional)
    district: Optional[str] = None       # District name (optional)
    province: Optional[str] = None       # Province/city name (optional)
    
    def format(self) -> str:
        """Convert address to string format.
        
        Returns:
            str: Address in format "street_address, ward, district, province"
                 or "ward, district, province" if no street address
        """
        components = []
        
        if self.street_address:
            components.append(self.street_address)
        
        if self.ward:
            components.append(self.ward)
        
        if self.district:
            components.append(self.district)
        
        if self.province:
            components.append(self.province)
        
        return ', '.join(components)