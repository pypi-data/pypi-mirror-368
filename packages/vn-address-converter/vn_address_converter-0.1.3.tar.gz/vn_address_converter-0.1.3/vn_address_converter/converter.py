import copy

from typing import Union
from .models import Address, AddressLevel, MappingMissingError
from .parser import parse_address
from .mapping import get_administrative_database



def convert_to_new_address(address: Union[str, Address]) -> Address:
    # If string is provided, parse it to Address object first
    if isinstance(address, str):
        address = parse_address(address)
    
    province = address.province
    district = address.district
    ward = address.ward
    street_address = address.street_address

    # If district is missing, this could be a new address format then return as is
    if not district:
        return copy.copy(address)
    
    if not province or not ward:
        raise ValueError('Missing province or ward in address')

    db = get_administrative_database()
    province_map = db.lookup_province(province)
    if not province_map:
        raise MappingMissingError(AddressLevel.PROVINCE, province)
    
    district_map = province_map.lookup_district(district)
    if not district_map:
        raise MappingMissingError(AddressLevel.DISTRICT, district)
    
    ward_map = district_map.lookup_ward(ward)
    if not ward_map:
        raise MappingMissingError(AddressLevel.WARD, ward)

    new_province = ward_map.get_new_province()
    new_ward = ward_map.get_new_ward()

    return Address(
        street_address=street_address,
        ward=new_ward,
        district=None,
        province=new_province
    )
