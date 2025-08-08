"""Mapping data loading and caching functionality for Vietnamese address conversion."""

import json
import os
from typing import Dict, Any, Optional
from .models import AddressLevel
from .aliases import get_aliases, normalize


class WardMapping:
    """Represents a ward mapping with conversion methods."""
    
    def __init__(self, ward_key: str, ward_data: Dict[str, Any]):
        self.ward_key = ward_key
        self.ward_data = ward_data
    
    def get_new_province(self) -> str:
        """Get the new province name after conversion."""
        return self.ward_data['new_provine_name']
    
    def get_new_ward(self) -> str:
        """Get the new ward name after conversion."""
        return self.ward_data['new_ward_name']


class DistrictMapping:
    """Represents a district mapping with data and lookup methods."""
    
    def __init__(self, district_key: str, district_mapping: Dict[str, Any], ward_aliases: Dict[str, str]):
        self.district_key = district_key
        self.district_mapping = district_mapping
        self.ward_aliases = ward_aliases
    
    def lookup_ward(self, ward: str) -> Optional[WardMapping]:
        """Get mapping data for a specific ward within this district."""
        
        original_ward = ward
        ward = normalize(ward, AddressLevel.WARD)
        
        ward_key = None
        ward_data = None
        
        # Try direct lookup first
        if ward in self.district_mapping:
            ward_key = ward
            ward_data = self.district_mapping[ward]
        else:
            # Try all possible aliases for this ward
            from .aliases import get_aliases
            aliases_to_try = get_aliases(original_ward, AddressLevel.WARD)
            
            for alias in aliases_to_try:
                ward_key = self.ward_aliases.get(alias.lower())
                if ward_key and ward_key in self.district_mapping:
                    ward_data = self.district_mapping[ward_key]
                    break
        
        # Handle legacy ward mapping if available
        if not ward_key and self.district_mapping.get('legacy_ward_mapping'):
            legacy_mapping = self.district_mapping['legacy_ward_mapping']
            if ward in legacy_mapping:
                ward_key = legacy_mapping[ward]
                ward_data = self.district_mapping.get(ward_key)
        
        if ward_key and ward_data:
            return WardMapping(ward_key=ward_key, ward_data=ward_data)
        
        return None


class ProvinceMapping:
    """Represents a province mapping with data and lookup methods."""
    
    def __init__(self, province_key: str, province_mapping: Dict[str, Any], district_aliases: Dict[str, str], ward_aliases: Dict[str, Dict[str, str]]):
        self.province_key = province_key
        self.province_mapping = province_mapping
        self.district_aliases = district_aliases
        self.ward_aliases = ward_aliases
    
    def lookup_district(self, district: str) -> Optional[DistrictMapping]:
        """Get mapping data for a specific district within this province."""
        
        original_district = district
        district = normalize(district, AddressLevel.DISTRICT)
        
        district_key = None
        district_data = None
        
        # Try direct lookup first
        if district in self.province_mapping:
            district_key = district
            district_data = self.province_mapping[district]
        else:
            # Try all possible aliases for this district
            from .aliases import get_aliases
            aliases_to_try = get_aliases(original_district, AddressLevel.DISTRICT)
            
            for alias in aliases_to_try:
                district_key = self.district_aliases.get(alias.lower())
                if district_key and district_key in self.province_mapping:
                    district_data = self.province_mapping[district_key]
                    break
        
        # Handle legacy district mapping if available
        if not district_data and self.province_mapping.get('legacy_district_mapping'):
            legacy_mapping = self.province_mapping['legacy_district_mapping']
            # Try both normalized and original district names
            if district in legacy_mapping:
                district_key = legacy_mapping[district]
                district_data = self.province_mapping.get(district_key)
            elif original_district in legacy_mapping:
                district_key = legacy_mapping[original_district]
                district_data = self.province_mapping.get(district_key)
        
        if district_key and district_data:
            return DistrictMapping(
                district_key=district_key,
                district_mapping=district_data,
                ward_aliases=self.ward_aliases.get(district_key, {})
            )
        
        return None


class AdministrativeDatabase:
    """Database for Vietnamese province/district/ward mapping with lazy loading."""
    
    def __init__(self):
        self._mapping_data = None
        self._manual_aliases = None
        self._ward_mapping_path = os.path.join(os.path.dirname(__file__), 'data', 'ward_mapping.json')
        self._manual_aliases_path = os.path.join(os.path.dirname(__file__), 'data', 'manual_aliases.json')
    
    @property
    def manual_aliases(self) -> Dict[str, Any]:
        """Load manual aliases data from JSON file."""
        if self._manual_aliases is None:
            try:
                with open(self._manual_aliases_path, encoding='utf-8') as f:
                    self._manual_aliases = json.load(f)
            except FileNotFoundError:
                self._manual_aliases = {"provinces": {}, "districts": {}, "wards": {}}
        return self._manual_aliases
    
    @property
    def mapping_data(self) -> Dict[str, Any]:
        """Load and process ward mapping data with aliases."""
        if self._mapping_data is None:
            with open(self._ward_mapping_path, encoding='utf-8') as f:
                mapping = json.load(f)
            
            manual_aliases = self.manual_aliases
            
            province_aliases = {}
            district_aliases = {}
            ward_aliases = {}
            
            for prov_name, prov_val in mapping.items():
                # Use get_aliases to get all aliases for this province
                for alias in get_aliases(prov_name, AddressLevel.PROVINCE):
                    province_aliases[alias] = prov_name
                
                # Add manual province aliases - use case-insensitive lookup
                manual_prov_aliases = None
                
                # Try to find manual aliases with case-insensitive lookup
                if prov_name in manual_aliases.get('provinces', {}):
                    manual_prov_aliases = manual_aliases['provinces'][prov_name]
                else:
                    # Try case-insensitive province lookup
                    for manual_prov_name in manual_aliases.get('provinces', {}):
                        if manual_prov_name.lower() == prov_name.lower():
                            manual_prov_aliases = manual_aliases['provinces'][manual_prov_name]
                            break
                
                if manual_prov_aliases:
                    for alias in manual_prov_aliases:
                        province_aliases[alias.lower()] = prov_name
                
                district_aliases[prov_name] = {}
                ward_aliases[prov_name] = {}
                
                for dist_name, dist_val in prov_val.items():
                    # Use get_aliases to get all aliases for this district
                    for alias in get_aliases(dist_name, AddressLevel.DISTRICT):
                        district_aliases[prov_name][alias] = dist_name
                    
                    # Add manual district aliases - use case-insensitive lookup
                    manual_dist_aliases = None
                    
                    # Try to find manual aliases with case-insensitive lookup
                    if prov_name in manual_aliases.get('districts', {}):
                        prov_districts = manual_aliases['districts'][prov_name]
                        
                        # Try exact match first
                        if dist_name in prov_districts:
                            manual_dist_aliases = prov_districts[dist_name]
                        else:
                            # Try case-insensitive district lookup
                            for manual_dist_name in prov_districts:
                                if manual_dist_name.lower() == dist_name.lower():
                                    manual_dist_aliases = prov_districts[manual_dist_name]
                                    break
                    
                    if manual_dist_aliases:
                        for alias in manual_dist_aliases:
                            district_aliases[prov_name][alias.lower()] = dist_name
                    
                    ward_aliases[prov_name][dist_name] = {}
                    
                    for ward_name in dist_val:
                        # Use get_aliases to get all aliases for this ward
                        for alias in get_aliases(ward_name, AddressLevel.WARD):
                            ward_aliases[prov_name][dist_name][alias] = ward_name
                        
                        # Add manual ward aliases - use case-insensitive lookup
                        manual_ward_aliases = None
                        
                        # Try to find manual aliases with case-insensitive lookup
                        if prov_name in manual_aliases.get('wards', {}):
                            prov_wards = manual_aliases['wards'][prov_name]
                            
                            # Try exact match first
                            if dist_name in prov_wards and ward_name in prov_wards[dist_name]:
                                manual_ward_aliases = prov_wards[dist_name][ward_name]
                            else:
                                # Try case-insensitive district lookup
                                for manual_dist_name in prov_wards:
                                    if manual_dist_name.lower() == dist_name.lower():
                                        if ward_name in prov_wards[manual_dist_name]:
                                            manual_ward_aliases = prov_wards[manual_dist_name][ward_name]
                                            break
                                        else:
                                            # Try case-insensitive ward lookup within this district
                                            for manual_ward_name in prov_wards[manual_dist_name]:
                                                if manual_ward_name.lower() == ward_name.lower():
                                                    manual_ward_aliases = prov_wards[manual_dist_name][manual_ward_name]
                                                    break
                                        if manual_ward_aliases:
                                            break
                        
                        if manual_ward_aliases:
                            for alias in manual_ward_aliases:
                                # Add the manual alias itself
                                ward_aliases[prov_name][dist_name][alias.lower()] = ward_name
                                # Also add normalized aliases for the manual alias
                                for normalized_alias in get_aliases(alias, AddressLevel.WARD):
                                    ward_aliases[prov_name][dist_name][normalized_alias] = ward_name
            
            self._mapping_data = {
                'mapping': mapping,
                'province_aliases': province_aliases,
                'district_aliases': district_aliases,
                'ward_aliases': ward_aliases
            }
        return self._mapping_data
    
    def get_mapping(self) -> Dict[str, Any]:
        """Get the complete mapping data."""
        return self.mapping_data
    
    def lookup_province(self, province: str) -> Optional[ProvinceMapping]:
        """Get mapping data for a specific province."""
        
        province = normalize(province, AddressLevel.PROVINCE)

        mapping_data = self.mapping_data
        mapping = mapping_data['mapping']
        province_aliases = mapping_data['province_aliases']
        district_aliases = mapping_data['district_aliases']
        ward_aliases = mapping_data['ward_aliases']
        
        province_key = None
        province_data = None
        
        # Try direct lookup first
        if province in mapping:
            province_key = province
            province_data = mapping[province]
        else:
            province_key = province_aliases.get(province.lower())
            
            if province_key and province_key in mapping:
                province_data = mapping[province_key]
        
        if province_key and province_data:
            return ProvinceMapping(
                province_key=province_key,
                province_mapping=province_data,
                district_aliases=district_aliases.get(province_key, {}),
                ward_aliases=ward_aliases.get(province_key, {})
            )
        
        return None
    


# Global instance for module reuse
_administrative_db = None


def get_administrative_database() -> AdministrativeDatabase:
    """Get the global AdministrativeDatabase instance."""
    global _administrative_db
    if _administrative_db is None:
        _administrative_db = AdministrativeDatabase()
    return _administrative_db
