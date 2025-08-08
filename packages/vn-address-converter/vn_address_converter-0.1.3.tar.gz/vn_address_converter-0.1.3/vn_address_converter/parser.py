"""Address parsing functionality for Vietnamese addresses."""

from .models import Address, AddressLevel
import re


def _extract_embedded_ward(street_address: str) -> tuple[str, str]:
    """Extract ward information embedded within street address.
    
    Returns:
        tuple: (cleaned_street_address, extracted_ward) or (original_street, None)
    """
    if not street_address:
        return street_address, None
    
    # Pattern to match embedded ward patterns at the END of street address only
    ward_patterns = [
        r'\bP\.([A-Za-zÀ-ỹ\s\d]{1,50})$',  # P.Tân Kiểng or P.14 at end (limit to reasonable ward name)
        r'\bph\.([A-Za-zÀ-ỹ\s\d]{1,50})$',  # ph.Something at end (limit to reasonable ward name)
        r'\bX\.([A-Za-zÀ-ỹ\s\d]{1,50})$',  # X.Tân Nhựt at end (limit to reasonable ward name)
        r'\bphường\s+([^,]+)$',  # phường Something at end
        r'\bphuong\s+([^,]+)$',  # phuong Something at end
        r'[-–—]\s*phường\s+([^,]+)$',  # - phường Something at end
        r'[-–—]\s*phuong\s+([^,]+)$',  # - phuong Something at end
        r'\bxã\s+([^,]+)$',      # xã Something at end
        r'\bxa\s+([^,]+)$',      # xa Something at end
        r'[-–—]\s*xã\s+([^,]+)$',  # - xã Something at end
        r'[-–—]\s*xa\s+([^,]+)$',  # - xa Something at end
        r'\bthị\s+trấn\s+([^,]+)$',  # thị trấn Something at end
        r'\bthi\s+tran\s+([^,]+)$',  # thi tran Something at end
        r'[-–—]\s*thị\s+trấn\s+([^,]+)$',  # - thị trấn Something at end
        r'[-–—]\s*thi\s+tran\s+([^,]+)$',  # - thi tran Something at end
        r'\bTT\s+([^,]+)$',      # TT Something at end
        r'\btt\s+([^,]+)$',      # tt Something at end  
        r'[-–—]\s*TT\s+([^,]+)$',  # -TT Something at end
        r'[-–—]\s*tt\s+([^,]+)$',  # -tt Something at end
    ]
    
    for pattern in ward_patterns:
        match = re.search(pattern, street_address, re.IGNORECASE)
        if match:
            ward_name = match.group(1).strip()
            # Reconstruct proper ward name
            if pattern.startswith(r'\bP\.'):
                extracted_ward = f"Phường {ward_name}"
            elif pattern.startswith(r'\bph\.'):
                extracted_ward = f"Phường {ward_name}"
            elif pattern.startswith(r'\bX\.'):
                extracted_ward = f"Xã {ward_name}"
            elif 'thị trấn' in pattern or 'thi tran' in pattern:
                extracted_ward = f"Thị trấn {ward_name}"
            elif 'TT' in pattern or 'tt' in pattern:
                extracted_ward = f"Thị trấn {ward_name}"
            elif 'phường' in pattern or 'phuong' in pattern:
                # For patterns with "phường" (including hyphen patterns), reconstruct properly
                extracted_ward = f"Phường {ward_name}"
            elif 'xã' in pattern or 'xa' in pattern:
                # For patterns with "xã" (including hyphen patterns), reconstruct properly  
                extracted_ward = f"Xã {ward_name}"
            else:
                # For full patterns, keep the original format
                extracted_ward = match.group(0).strip()
            
            # Remove the matched pattern from street address
            cleaned_street = re.sub(pattern, '', street_address, flags=re.IGNORECASE).strip()
            # Clean up extra spaces and commas
            cleaned_street = re.sub(r'\s*,\s*,\s*', ', ', cleaned_street)
            cleaned_street = re.sub(r'^,\s*|,\s*$', '', cleaned_street)
            cleaned_street = re.sub(r'\s*[-–—]\s*$', '', cleaned_street)  # Remove trailing dashes
            cleaned_street = re.sub(r'\s+', ' ', cleaned_street).strip()
            
            return cleaned_street if cleaned_street else None, extracted_ward
    
    return street_address, None


def _detect_component_type_with_context(part: str, parts: list, original_parts: list = None) -> AddressLevel:
    """Detect component type with context of other parts."""
    part_lower = part.lower().strip()
    
    # Ward keywords
    ward_keywords = ['phường', 'phuong', 'xã', 'xa', 'thị trấn', 'thi tran']
    for keyword in ward_keywords:
        if part_lower.startswith(keyword):
            return AddressLevel.WARD
    
    # Province keywords (check first to prioritize over district keywords)
    province_keywords = ['tỉnh', 'tinh']
    for keyword in province_keywords:
        if part_lower.startswith(keyword):
            return AddressLevel.PROVINCE
    
    # District keywords (check after thành phố logic, remove 'tp' since it's handled above)
    district_keywords = ['quận', 'quan', 'huyện', 'huyen', 'thị xã', 'thi xa']
    for keyword in district_keywords:
        if part_lower.startswith(keyword):
            return AddressLevel.DISTRICT

    # For "thành phố" - need to distinguish between province-level cities and district-level
    if part_lower.startswith('thành phố') or part_lower.startswith('thanh pho') \
        or part_lower.startswith('tp ') or part_lower.startswith('tp.'):
        
        # Check if there's a "Tỉnh" component anywhere in the address (use original parts if available)
        check_parts = original_parts if original_parts else parts
        has_tinh = any('tỉnh' in p.lower() or 'tinh' in p.lower() for p in check_parts)
        
        if has_tinh:
            # If there's a "Tỉnh" anywhere, then this "Thành phố" is district-level
            return AddressLevel.DISTRICT
        else:
            # If there are 3+ words total, it's probably a province
            words = part_lower.split()
            if len(words) >= 3:
                return AddressLevel.PROVINCE
            else:
                return AddressLevel.DISTRICT
    
    # Check if this could be a province when no explicit Tỉnh keyword is present
    check_parts = original_parts if original_parts else parts
    has_tinh = any('tỉnh' in p.lower() or 'tinh' in p.lower() for p in check_parts)
    
    if not has_tinh:  # Only apply this heuristic when no Tỉnh is detected in the address
        # If we have a district in the parts and this is the last part, assume it's province
        has_district = any(p.lower().startswith(('quận', 'quan', 'huyện', 'huyen', 'thị xã', 'thi xa')) for p in check_parts)
        if has_district and check_parts and part == check_parts[-1]:
            return AddressLevel.PROVINCE

    # Check if it starts with a number (likely street address)
    if part_lower and (part_lower[0].isdigit() or part_lower.startswith('#')):
        return AddressLevel.STREET
    
    # If no keyword matches, assume it's a street address
    return AddressLevel.STREET


def _filter_empty_parts(parts: list) -> list:
    """Filter out empty parts but handle cases where we have valid structure with gaps."""
    # If we have exactly 4 parts and the first one is empty, remove it (missing street)
    if len(parts) == 4 and parts[0] == '':
        return parts[1:]
    
    # If we have exactly 4 parts and the second one is empty, remove it (missing ward)  
    if len(parts) == 4 and parts[1] == '':
        return [parts[0]] + parts[2:] if parts[0] else parts[2:]
    
    # Handle case where we have 3 parts with middle empty (street, , district, province)
    if len(parts) == 4 and parts[1] == '' and parts[0] and parts[2] and parts[3]:
        return [parts[0], parts[2], parts[3]]
    
    # Filter out trailing empty parts
    while parts and parts[-1] == '':
        parts.pop()
    
    # Filter out all empty parts, but keep at least 2 parts
    filtered = [part for part in parts if part]
    return filtered if len(filtered) >= 2 else parts


def parse_address(address_string: str) -> Address:
    """Parse an address string into components.
    
    Args:
        address_string: Address string separated by comma, semicolon, pipe, or hyphen in formats:
                       - "district, province" (e.g., "Quận 10, TP Hồ Chí Minh")
                       - "ward, district, province"
                       - "street_address, ward, district, province"
    
    Returns:
        Address: Parsed address with components
    """
    if not address_string or not address_string.strip():
        raise ValueError("Address string cannot be empty")
    
    # Try different separators in order of preference
    separators = [',', ';', '|', '-']
    parts = None
    
    for separator in separators:
        if separator in address_string:
            # Don't filter out empty parts yet - we need to handle them properly
            parts = [part.strip() for part in address_string.split(separator)]
            break
    
    if parts is None:
        # No separator found, treat as single component
        parts = [address_string.strip()]

    if parts and parts[-1].lower() in ("việt nam", "vietnam", "vn"):
        # Remove "Việt Nam" if it's the last part
        parts = parts[:-1]
    
    # Store original parts before filtering for context detection
    original_parts = parts.copy()
    
    # Filter and clean empty parts
    parts = _filter_empty_parts(parts)
    
    if len(parts) < 2:
        raise ValueError("Address must have at least district and province")
    elif len(parts) == 2:
        # Format: "district, province" (e.g., "Quận 10, TP Hồ Chí Minh")
        district, province = parts
        ward = None
        street_address = None
    elif len(parts) == 3:
        # Use heuristics to determine which components are present
        types = [_detect_component_type_with_context(part, parts, original_parts) for part in parts]
        
        # Initialize all variables
        street_address = None
        ward = None
        district = None
        province = None
        
        # Apply heuristics based on detected types
        # Handle all possible combinations explicitly
        if types.count(AddressLevel.PROVINCE) == 2 and AddressLevel.STREET in types:
            # Special case: [STREET, PROVINCE, PROVINCE] - first PROVINCE is actually district
            street_address = parts[types.index(AddressLevel.STREET)]
            district = parts[types.index(AddressLevel.PROVINCE)]  # First province is district
            # Find the last occurrence of PROVINCE
            province_indices = [i for i, t in enumerate(types) if t == AddressLevel.PROVINCE]
            province = parts[province_indices[-1]]  # Last province is province
        elif AddressLevel.WARD in types and AddressLevel.DISTRICT in types and AddressLevel.PROVINCE in types:
            # All three components detected: ward, district, province
            ward = parts[types.index(AddressLevel.WARD)]
            district = parts[types.index(AddressLevel.DISTRICT)]
            province = parts[types.index(AddressLevel.PROVINCE)]
        elif AddressLevel.STREET in types and AddressLevel.DISTRICT in types and AddressLevel.PROVINCE in types:
            # street, district, province (missing ward)
            street_address = parts[types.index(AddressLevel.STREET)]
            district = parts[types.index(AddressLevel.DISTRICT)]
            province = parts[types.index(AddressLevel.PROVINCE)]
        elif AddressLevel.STREET in types and AddressLevel.WARD in types and AddressLevel.PROVINCE in types:
            # street, ward, province (missing district)
            street_address = parts[types.index(AddressLevel.STREET)]
            ward = parts[types.index(AddressLevel.WARD)]
            province = parts[types.index(AddressLevel.PROVINCE)]
        elif AddressLevel.STREET in types and AddressLevel.WARD in types and AddressLevel.DISTRICT in types:
            # street, ward, district (missing province)
            street_address = parts[types.index(AddressLevel.STREET)]
            ward = parts[types.index(AddressLevel.WARD)]
            district = parts[types.index(AddressLevel.DISTRICT)]
        elif AddressLevel.WARD in types and AddressLevel.DISTRICT in types:
            # ward, district, unknown (assume unknown is province)
            ward = parts[types.index(AddressLevel.WARD)]
            district = parts[types.index(AddressLevel.DISTRICT)]
            # Find the remaining part
            for i, part in enumerate(parts):
                if types[i] not in [AddressLevel.WARD, AddressLevel.DISTRICT]:
                    province = part
                    break
        elif AddressLevel.WARD in types and AddressLevel.PROVINCE in types:
            # ward, province, unknown (assume unknown is street)
            ward = parts[types.index(AddressLevel.WARD)]
            province = parts[types.index(AddressLevel.PROVINCE)]
            # Find the remaining part
            for i, part in enumerate(parts):
                if types[i] not in [AddressLevel.WARD, AddressLevel.PROVINCE]:
                    street_address = part
                    break
        elif AddressLevel.DISTRICT in types and AddressLevel.PROVINCE in types:
            # district, province, unknown (assume unknown is street)
            district = parts[types.index(AddressLevel.DISTRICT)]
            province = parts[types.index(AddressLevel.PROVINCE)]
            # Find the remaining part
            for i, part in enumerate(parts):
                if types[i] not in [AddressLevel.DISTRICT, AddressLevel.PROVINCE]:
                    street_address = part
                    break
        else:
            # Default: assume ward, district, province format
            ward = parts[0]
            district = parts[1]
            province = parts[2]
    elif len(parts) == 4:
        # Use heuristics to determine which components are present
        types = [_detect_component_type_with_context(part, parts, original_parts) for part in parts]
        
        # Initialize all variables
        street_address = None
        ward = None
        district = None
        province = None
        
        # Apply heuristics based on detected types
        if AddressLevel.WARD in types and AddressLevel.DISTRICT in types and AddressLevel.PROVINCE in types:
            # street, ward, district, province
            ward = parts[types.index(AddressLevel.WARD)]
            district = parts[types.index(AddressLevel.DISTRICT)]
            province = parts[types.index(AddressLevel.PROVINCE)]
            # Find the remaining part (street)
            for i, part in enumerate(parts):
                if types[i] not in [AddressLevel.WARD, AddressLevel.DISTRICT, AddressLevel.PROVINCE]:
                    street_address = part
                    break
        elif AddressLevel.WARD in types and AddressLevel.PROVINCE in types:
            # Missing district - could be street1, street2, ward, province
            ward = parts[types.index(AddressLevel.WARD)]
            province = parts[types.index(AddressLevel.PROVINCE)]
            # Combine all non-ward, non-province parts as street address
            street_parts = []
            for i, part in enumerate(parts):
                if types[i] not in [AddressLevel.WARD, AddressLevel.PROVINCE]:
                    street_parts.append(part)
            if street_parts:
                street_address = ", ".join(street_parts)
        elif AddressLevel.DISTRICT in types and AddressLevel.PROVINCE in types:
            # Missing ward - could be street1, street2, district, province OR street, ward, district, province
            district = parts[types.index(AddressLevel.DISTRICT)]
            province = parts[types.index(AddressLevel.PROVINCE)]
            
            # Find all non-district, non-province parts
            other_parts = []
            for i, part in enumerate(parts):
                if types[i] not in [AddressLevel.DISTRICT, AddressLevel.PROVINCE]:
                    other_parts.append((i, part))
            
            if len(other_parts) == 2:
                # Two other parts: assume street, ward format
                street_address = other_parts[0][1]
                ward = other_parts[1][1]
            elif len(other_parts) == 1:
                # One other part: assume it's street
                street_address = other_parts[0][1]
            else:
                # Multiple parts: combine as street address
                street_parts = [part for _, part in other_parts]
                if street_parts:
                    street_address = ", ".join(street_parts)
        else:
            # Default fallback: assume street_address, ward, district, province
            street_address, ward, district, province = parts
    else:
        # Format: >4 parts - use heuristics to detect components
        types = [_detect_component_type_with_context(part, parts, original_parts) for part in parts]
        
        # Initialize all variables
        street_address = None
        ward = None
        district = None
        province = None
        
        # Apply heuristics based on detected types
        if AddressLevel.WARD in types and AddressLevel.DISTRICT in types and AddressLevel.PROVINCE in types:
            # Full address with all components
            ward = parts[types.index(AddressLevel.WARD)]
            district = parts[types.index(AddressLevel.DISTRICT)]
            province = parts[types.index(AddressLevel.PROVINCE)]
            # Combine all non-administrative parts as street address
            street_parts = []
            for i, part in enumerate(parts):
                if types[i] not in [AddressLevel.WARD, AddressLevel.DISTRICT, AddressLevel.PROVINCE]:
                    street_parts.append(part)
            if street_parts:
                street_address = ", ".join(street_parts)
        elif AddressLevel.WARD in types and AddressLevel.PROVINCE in types:
            # Missing district - ward and province detected
            ward = parts[types.index(AddressLevel.WARD)]
            province = parts[types.index(AddressLevel.PROVINCE)]
            # Combine all non-ward, non-province parts as street address
            street_parts = []
            for i, part in enumerate(parts):
                if types[i] not in [AddressLevel.WARD, AddressLevel.PROVINCE]:
                    street_parts.append(part)
            if street_parts:
                street_address = ", ".join(street_parts)
        elif AddressLevel.DISTRICT in types and AddressLevel.PROVINCE in types:
            # Missing ward - district and province detected
            district = parts[types.index(AddressLevel.DISTRICT)]
            province = parts[types.index(AddressLevel.PROVINCE)]
            # Combine all non-district, non-province parts as street address
            street_parts = []
            for i, part in enumerate(parts):
                if types[i] not in [AddressLevel.DISTRICT, AddressLevel.PROVINCE]:
                    street_parts.append(part)
            if street_parts:
                street_address = ", ".join(street_parts)
        else:
            # Fallback: assume the last 3 parts are ward, district, province
            # Take the last 3 parts as ward, district, province
            # Combine the rest as street_address
            ward, district, province = parts[-3:]
            street_address = ", ".join(parts[:-3])
    
    # Extract embedded ward information from street address if not explicitly provided
    if street_address and ward is None:
        street_address, extracted_ward = _extract_embedded_ward(street_address)
        if extracted_ward:
            ward = extracted_ward
    
    return Address(
        street_address=street_address if street_address else None,
        ward=ward if ward else None,
        district=district if district else None,
        province=province if province else None
    )