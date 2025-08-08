import pytest
from vn_address_converter import parse_address, Address


class TestParseAddress:
    """Test cases for the parse_address function."""
    
    def test_parse_address_with_street_address(self):
        """Test parsing address with street address included."""
        address_str = "123 Nguyen Van Linh, Phường 1, Quận 7, Thành phố Hồ Chí Minh"
        result = parse_address(address_str)
        
        assert result.street_address == "123 Nguyen Van Linh"
        assert result.ward == "Phường 1"
        assert result.district == "Quận 7"
        assert result.province == "Thành phố Hồ Chí Minh"
    
    def test_parse_address_without_street_address(self):
        """Test parsing address without street address."""
        address_str = "Phường 1, Quận 7, Thành phố Hồ Chí Minh"
        result = parse_address(address_str)
        
        assert result.street_address is None
        assert result.ward == "Phường 1"
        assert result.district == "Quận 7"
        assert result.province == "Thành phố Hồ Chí Minh"
    
    def test_parse_address_with_whitespace(self):
        """Test parsing address with extra whitespace."""
        address_str = "  123 Le Loi  ,  Phường 2  ,  Quận 1  ,  Thành phố Hồ Chí Minh  "
        result = parse_address(address_str)
        
        assert result.street_address == "123 Le Loi"
        assert result.ward == "Phường 2"
        assert result.district == "Quận 1"
        assert result.province == "Thành phố Hồ Chí Minh"
    
    def test_parse_address_different_province(self):
        """Test parsing address from different province."""
        address_str = "456 Tran Hung Dao, Xã Tân Thạnh, Huyện Cần Giờ, Tỉnh Khánh Hòa"
        result = parse_address(address_str)
        
        assert result.street_address == "456 Tran Hung Dao"
        assert result.ward == "Xã Tân Thạnh"
        assert result.district == "Huyện Cần Giờ"
        assert result.province == "Tỉnh Khánh Hòa"
    
    def test_parse_address_empty_string(self):
        """Test parsing empty string raises ValueError."""
        with pytest.raises(ValueError, match="Address string cannot be empty"):
            parse_address("")
    
    def test_parse_address_whitespace_only(self):
        """Test parsing whitespace-only string raises ValueError."""
        with pytest.raises(ValueError, match="Address string cannot be empty"):
            parse_address("   ")
    
    def test_parse_address_too_few_components(self):
        """Test parsing address with too few components raises ValueError."""
        with pytest.raises(ValueError, match="Address must have at least district and province"):
            parse_address("Phường 1")
    
    def test_parse_address_two_components(self):
        """Test parsing address with district and province only."""
        address_str = "Quận 10, TP Hồ Chí Minh"
        result = parse_address(address_str)
        
        assert result.street_address is None
        assert result.ward is None
        assert result.district == "Quận 10"
        assert result.province == "TP Hồ Chí Minh"
    
    def test_parse_address_too_many_components(self):
        """Test parsing address with too many components combines them into street_address."""
        address = parse_address("123 Street, Building A, Phường 1, Quận 7, Thành phố Hồ Chí Minh")
        assert address.street_address == "123 Street, Building A"
        assert address.ward == "Phường 1"
        assert address.district == "Quận 7"
        assert address.province == "Thành phố Hồ Chí Minh"
    
    def test_parse_address_empty_components(self):
        """Test parsing address with empty components."""
        address_str = ", Phường 1, Quận 7, Thành phố Hồ Chí Minh"
        result = parse_address(address_str)
        
        assert result.street_address is None
        assert result.ward == "Phường 1"
        assert result.district == "Quận 7"
        assert result.province == "Thành phố Hồ Chí Minh"
    
    def test_parse_address_special_characters(self):
        """Test parsing address with special characters."""
        address_str = "123/45 Đường Nguyễn Huệ, Phường Bến Nghé, Quận 1, Thành phố Hồ Chí Minh"
        result = parse_address(address_str)
        
        assert result.street_address == "123/45 Đường Nguyễn Huệ"
        assert result.ward == "Phường Bến Nghé"
        assert result.district == "Quận 1"
        assert result.province == "Thành phố Hồ Chí Minh"
    
    def test_parse_address_with_empty_component(self):
        """Test parsing address with empty component (double comma)."""
        address_str = "Thôn Quảng Đạt, xã Ngũ Phúc, , Huyện Kim Thành, Hải Dương"
        result = parse_address(address_str)
        
        assert result.street_address == "Thôn Quảng Đạt"
        assert result.ward == "xã Ngũ Phúc"
        assert result.district == "Huyện Kim Thành"
        assert result.province == "Hải Dương"
    
    @pytest.mark.parametrize("address_str,expected", [
        ("Quận 10, TP Hồ Chí Minh", {
            'street_address': None,
            'ward': None,
            'district': "Quận 10",
            'province': "TP Hồ Chí Minh"
        }),
        ("Phường 1, Quận 7, Thành phố Hồ Chí Minh", {
            'street_address': None,
            'ward': "Phường 1",
            'district': "Quận 7",
            'province': "Thành phố Hồ Chí Minh"
        }),
        ("789 Lê Văn Việt, Xã Hiệp Phú, Huyện Thủ Đức, Tỉnh Đồng Nai", {
            'street_address': "789 Lê Văn Việt",
            'ward': "Xã Hiệp Phú",
            'district': "Huyện Thủ Đức",
            'province': "Tỉnh Đồng Nai"
        }),
        ("Phường 12, Quận Gò Vấp, Thành phố Hồ Chí Minh", {
            'street_address': None,
            'ward': "Phường 12",
            'district': "Quận Gò Vấp",
            'province': "Thành phố Hồ Chí Minh"
        })
    ])
    def test_parse_address_parametrized(self, address_str, expected):
        """Parametrized test for various address formats."""
        result = parse_address(address_str)
        assert result.street_address == expected['street_address']
        assert result.ward == expected['ward']
        assert result.district == expected['district']
        assert result.province == expected['province']
    
    def test_parse_address_returns_address_type(self):
        """Test that parse_address returns Address type."""
        address_str = "Phường 1, Quận 7, Thành phố Hồ Chí Minh"
        result = parse_address(address_str)
        
        # Check that result is an Address dataclass
        assert hasattr(result, 'street_address')
        assert hasattr(result, 'ward')
        assert hasattr(result, 'district')
        assert hasattr(result, 'province')
    
    def test_parse_address_heuristic_three_parts(self):
        """Test heuristic parsing for 3-part addresses with missing components."""
        
        # Test: street, district, province (missing ward)
        address_str = "123 Main Street, Quận 1, Thành phố Hồ Chí Minh"
        result = parse_address(address_str)
        
        assert result.street_address == "123 Main Street"
        assert result.ward is None
        assert result.district == "Quận 1"
        assert result.province == "Thành phố Hồ Chí Minh"
        
        # Test: street, ward, province (missing district)
        address_str = "456 Elm Street, Phường 2, Tỉnh Khánh Hòa"
        result = parse_address(address_str)
        
        assert result.street_address == "456 Elm Street"
        assert result.ward == "Phường 2"
        assert result.district is None
        assert result.province == "Tỉnh Khánh Hòa"
        
        # Test: ward, district missing, standard order (street, ward, province)
        address_str = "789 Oak Street, Phường 3, Tỉnh Đồng Nai"
        result = parse_address(address_str)
        
        assert result.street_address == "789 Oak Street"
        assert result.ward == "Phường 3"
        assert result.district is None
        assert result.province == "Tỉnh Đồng Nai"
        
        # Test: ward missing, standard order (street, district, province)
        address_str = "321 Pine Street, Quận 7, Thành phố Hồ Chí Minh"
        result = parse_address(address_str)
        
        assert result.street_address == "321 Pine Street"
        assert result.ward is None
        assert result.district == "Quận 7"
        assert result.province == "Thành phố Hồ Chí Minh"
        
        # Test: traditional format still works (ward, district, province)
        address_str = "Phường 1, Quận 2, Thành phố Hồ Chí Minh"
        result = parse_address(address_str)
        
        assert result.street_address is None
        assert result.ward == "Phường 1"
        assert result.district == "Quận 2"
        assert result.province == "Thành phố Hồ Chí Minh"
    
    def test_parse_address_heuristic_keywords(self):
        """Test heuristic parsing with various Vietnamese keywords."""
        
        # Test with alternative ward keywords
        address_str = "ABC Building, Xã Tân Phú, Tỉnh Long An"
        result = parse_address(address_str)
        
        assert result.street_address == "ABC Building"
        assert result.ward == "Xã Tân Phú"
        assert result.district is None
        assert result.province == "Tỉnh Long An"
        
        # Test with alternative district keywords
        address_str = "XYZ Complex, Huyện Bình Chánh, Thành phố Hồ Chí Minh"
        result = parse_address(address_str)
        
        assert result.street_address == "XYZ Complex"
        assert result.ward is None
        assert result.district == "Huyện Bình Chánh"
        assert result.province == "Thành phố Hồ Chí Minh"
        
        # Test with non-accented keywords
        address_str = "123 Test St, Phuong 5, Quan 3"
        result = parse_address(address_str)
        
        assert result.street_address == "123 Test St"
        assert result.ward == "Phuong 5"
        assert result.district == "Quan 3"
        assert result.province is None

    def test_parse_address_non_standard_formats(self):
        """Test parsing non-standard address formats."""
        # Test with semicolon separator
        address_str = "123 Lê Lợi; Phường 1; Quận 7; Thành phố Hồ Chí Minh"
        result = parse_address(address_str)
        
        assert result.street_address == "123 Lê Lợi"
        assert result.ward == "Phường 1"
        assert result.district == "Quận 7"
        assert result.province == "Thành phố Hồ Chí Minh"
        
        # Test with hyphen separator
        address_str = "456 Nguyễn Trãi - Phường 2 - Quận 1 - Thành phố Hồ Chí Minh"
        result = parse_address(address_str)
        
        assert result.street_address == "456 Nguyễn Trãi"
        assert result.ward == "Phường 2"
        assert result.district == "Quận 1"
        assert result.province == "Thành phố Hồ Chí Minh"
        
        # Test with pipe separator
        address_str = "789 Hai Bà Trưng | Phường 3 | Quận 3 | Thành phố Hồ Chí Minh"
        result = parse_address(address_str)
        
        assert result.street_address == "789 Hai Bà Trưng"
        assert result.ward == "Phường 3"
        assert result.district == "Quận 3"
        assert result.province == "Thành phố Hồ Chí Minh"

    def test_parse_address_missing_district_multiple_commas(self):
        """Test parsing address with missing district but multiple street components."""
        address_str = "ABC, DEF, Phường Sài Gòn, TP Hồ Chí Minh"
        result = parse_address(address_str)

        assert result.street_address == "ABC, DEF"
        assert result.ward == "Phường Sài Gòn"
        assert result.district is None
        assert result.province == "TP Hồ Chí Minh"

    def test_parse_address_thanh_pho_district_with_tinh_province(self):
        """Test parsing address with 'Thành phố' as district when followed by 'Tỉnh' province."""
        address_str = "123A Đại lộ Đồng Khởi, Phường Phú Tân, Thành phố Bến Tre, Tỉnh Bến Tre"
        result = parse_address(address_str)
        
        assert result.street_address == "123A Đại lộ Đồng Khởi"
        assert result.ward == "Phường Phú Tân"
        assert result.district == "Thành phố Bến Tre"
        assert result.province == "Tỉnh Bến Tre"