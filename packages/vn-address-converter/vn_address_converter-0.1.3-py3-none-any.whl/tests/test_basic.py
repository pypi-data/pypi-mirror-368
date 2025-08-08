"""
Basic functionality tests for vn-address-converter.
"""
from vn_address_converter import convert_to_new_address, Address, AddressLevel
from vn_address_converter.models import MappingMissingError
import pytest
import unicodedata


def unicode_equal(str1: str, str2: str) -> bool:
    """Compare two strings with Unicode normalization."""
    return unicodedata.normalize("NFC", str1) == unicodedata.normalize("NFC", str2)

@pytest.mark.parametrize("address,expected", [
    (
        Address(
            street_address="720A Điện Biên Phủ",
            ward="Phường 22",
            district="Quận Bình Thạnh",
            province="Thành phố Hồ Chí Minh"
        ),
        Address(
            street_address="720A Điện Biên Phủ",
            ward="Phường Thạnh Mỹ Tây",
            district=None,
            province="Thành phố Hồ Chí Minh"
        )
    ),
    (
        Address(
            street_address="1 P. Nhà Thờ",
            ward="Phường Hàng Trống",
            district="Quận Hoàn Kiếm",
            province="Thành phố Hà Nội"
        ),
        Address(
            street_address="1 P. Nhà Thờ",
            ward="Phường Hoàn Kiếm",
            district=None,
            province="Thành phố Hà Nội"
        )
    ),
        (
        Address(
            street_address="",
            ward="Phường 8",
            district="quan 10",
            province="Thành phố Hồ Chí Minh"
        ),
        Address(
            street_address="",
            ward="Phường Diên Hồng",
            district=None,
            province="Thành phố Hồ Chí Minh"
        )
    ),
    (
        # case insensitive ward and district
        Address(
            street_address="07 Công trường Lam Sơn",
            ward="phường bến nghé",
            district="quận 1",
            province="thành phố hồ chí minh"
        ),
        Address(
            street_address="07 Công trường Lam Sơn",
            ward="Phường Sài Gòn",
            district=None,
            province="Thành phố Hồ Chí Minh"
        )
    ),
    # Phường 01
    (
        Address(
            street_address="123 Đường Test",
            ward="Phường 01",
            district="Quận Gò Vấp",
            province="Thành phố Hồ Chí Minh"
        ),
        Address(
            street_address="123 Đường Test",
            ward="Phường Hạnh Thông",
            district=None,
            province="Thành phố Hồ Chí Minh"
        )
    ),
    (
        # no accented characters
        Address(
            street_address="07 Cong truong Lam Son",
            ward="phuong ben nghe",
            district="quan 1",
            province="thanh pho ho chi minh"
        ),
        Address(
            street_address="07 Cong truong Lam Son",
            ward="Phường Sài Gòn",
            district=None,
            province="Thành phố Hồ Chí Minh"
        )
    ),
    (
        # test aliases
        Address(
            street_address="51 Lê Lợi",
            ward="Phú Hội",
            district="Thuận Hóa",
            province="Huế"
        ),
        Address(
            street_address="51 Lê Lợi",
            ward="Phường Thuận Hóa",
            district=None,
            province="Thành phố Huế"
        )
    ),
    (
        # test aliases for Bà Rịa - Vũng Tàu
        Address(
            street_address="31-33-35 Nguyễn Văn Cừ",
            ward="Long Toàn",
            district="Bà Rịa",
            province="Bà Rịa - Vũng Tàu"
        ),
        Address(
            street_address="31-33-35 Nguyễn Văn Cừ",
            ward="Phường Bà Rịa",
            district=None,
            province="Thành phố Hồ Chí Minh"
        )
    ),
])
def test_convert_address_table(address, expected):
    result = convert_to_new_address(address)
    assert result == expected


# Test error handling cases
def test_convert_address_missing_province():
    """Test that missing province raises ValueError"""
    with pytest.raises(ValueError, match="Missing province or ward in address"):
        convert_to_new_address(Address(
            street_address="123 Test St",
            ward="Phường 1",
            district="Quận 1",
            province=None
        ))


def test_convert_address_missing_district():
    """Test that missing district returns a copy of the original address"""
    original_address = Address(
        street_address="123 Test St",
        ward="Phường 1",
        district=None,
        province="Thành phố Hồ Chí Minh"
    )
    result = convert_to_new_address(original_address)
    
    # Should return a copy of the original address
    assert result.street_address == original_address.street_address
    assert result.ward == original_address.ward
    assert result.district == original_address.district
    assert result.province == original_address.province
    
    # Should be a copy, not the same object
    assert result is not original_address


def test_convert_address_missing_ward():
    """Test that missing ward raises ValueError"""
    with pytest.raises(ValueError, match="Missing province or ward in address"):
        convert_to_new_address(Address(
            street_address="123 Test St",
            ward=None,
            district="Quận 1",
            province="Thành phố Hồ Chí Minh"
        ))


def test_convert_address_invalid_province():
    """Test that invalid province raises MappingMissingError"""
    with pytest.raises(MappingMissingError, match="Province not found in mapping"):
        convert_to_new_address(Address(
            street_address="123 Test St",
            ward="Phường 1",
            district="Quận 1",
            province="Invalid Province"
        ))


def test_convert_address_invalid_district():
    """Test that invalid district raises MappingMissingError"""
    with pytest.raises(MappingMissingError, match="District not found in mapping"):
        convert_to_new_address(Address(
            street_address="123 Test St",
            ward="Phường 1",
            district="Invalid District",
            province="Thành phố Hồ Chí Minh"
        ))


def test_convert_address_invalid_ward():
    """Test that invalid ward raises MappingMissingError"""
    with pytest.raises(MappingMissingError, match="Ward not found in mapping"):
        convert_to_new_address(Address(
            street_address="123 Test St",
            ward="Invalid Ward",
            district="Quận Gò Vấp",
            province="Thành phố Hồ Chí Minh"
        ))


# Test different province formats and edge cases
def test_convert_address_case_variations():
    """Test case insensitive address conversion"""
    result = convert_to_new_address(Address(
        street_address="100 Trần Hưng Đạo",
        ward="PHƯỜNG 12",
        district="QUẬN GÒ VẤP",
        province="THÀNH PHỐ HỒ CHÍ MINH"
    ))
    # Check that conversion works with uppercase input
    assert result.street_address == "100 Trần Hưng Đạo"
    assert result.district is None
    assert result.province == "Thành phố Hồ Chí Minh"
    # Ward should map to the correct new name
    assert 'Phường' in result.ward
    assert 'An H' in result.ward
    assert 'Tây' in result.ward


def test_convert_address_with_spaces():
    """Test address conversion with extra spaces"""
    result = convert_to_new_address(Address(
        street_address="  200 Nguyễn Thị Minh Khai  ",
        ward="  phường 5  ",
        district="  quận gò vấp  ",
        province="  thành phố hồ chí minh  "
    ))
    # Check that conversion works with extra spaces
    assert result.street_address == "  200 Nguyễn Thị Minh Khai  "
    assert result.district is None
    assert result.province == "Thành phố Hồ Chí Minh"
    # Ward should map to the correct new name
    assert 'Phường' in result.ward
    assert 'Nhơn' in result.ward


def test_convert_address_khanh_hoa():
    """Test address conversion with Khánh Hòa province"""
    result = convert_to_new_address(Address(
        street_address="300 Yersin",
        ward="Phường Ninh Giang",
        district="Thị xã Ninh Hòa",
        province="Tỉnh Khánh Hòa"
    ))
    # Check that conversion works with Tỉnh format
    assert result.street_address == "300 Yersin"
    assert result.district is None
    assert result.province == "Khánh Hòa"
    # Ward should map to the correct new name
    assert 'Phường' in result.ward
    assert 'Thắng' in result.ward


def test_convert_address_go_vap_variations():
    """Test various Gò Vấp ward conversions"""
    # Test Phường 1 -> Phường Hạnh Thông
    result1 = convert_to_new_address(Address(
        street_address="123 Đường Test",
        ward="Phường 1",
        district="Quận Gò Vấp",
        province="Thành phố Hồ Chí Minh"
    ))
    assert result1.district is None
    assert result1.province == "Thành phố Hồ Chí Minh"
    assert 'Hạnh Thông' in result1.ward

    # Test Phường 10 -> Phường Gò Vấp
    result2 = convert_to_new_address(Address(
        street_address="456 Phan Văn Trị",
        ward="Phường 10",
        district="Quận Gò Vấp",
        province="Thành phố Hồ Chí Minh"
    ))
    assert result2.district is None
    assert result2.province == "Thành phố Hồ Chí Minh"
    assert 'Gò Vấp' in result2.ward


def test_convert_address_cam_ranh():
    """Test address conversion with Cam Ranh"""
    result = convert_to_new_address(Address(
        street_address="789 Trần Phú",
        ward="Phường Ba Ngòi",
        district="Thành phố Cam Ranh",
        province="Tỉnh Khánh Hòa"
    ))
    # Check that conversion works
    assert result.street_address == "789 Trần Phú"
    assert result.district is None
    assert result.province == "Khánh Hòa"
    # Ward should be preserved in this case
    assert result.ward == "Phường Ba Ngòi"


def test_manual_aliases():
    """Test manual aliases functionality"""
    # Test province alias
    result1 = convert_to_new_address(Address(
        street_address="123 Test St",
        ward="Phường 12",
        district="Quận Gò Vấp",
        province="HCM"  # Using manual alias
    ))
    assert result1.province == "Thành phố Hồ Chí Minh"
    assert result1.district is None
    assert unicode_equal(result1.ward, "Phường An Hội Tây")

    # Test district alias
    result2 = convert_to_new_address(Address(
        street_address="456 Test St",
        ward="Phường 12",
        district="Gò Vấp",  # Using manual alias
        province="Thành phố Hồ Chí Minh"
    ))
    assert result2.province == "Thành phố Hồ Chí Minh"
    assert result2.district is None
    assert unicode_equal(result2.ward, "Phường An Hội Tây")

    # Test ward alias
    result3 = convert_to_new_address(Address(
        street_address="789 Test St",
        ward="P12",  # Using manual alias
        district="Quận Gò Vấp",
        province="Thành phố Hồ Chí Minh"
    ))
    assert result3.province == "Thành phố Hồ Chí Minh"
    assert result3.district is None
    assert unicode_equal(result3.ward, "Phường An Hội Tây")


def test_convert_address_con_dao():
    """Test Côn Đảo address conversion
    
    This test documents the expected behavior once mapping data is updated.
    """
    result = convert_to_new_address(Address(
        street_address="01A Võ Thị Sáu, Khu dân cư số 6",
        ward="Thị Trấn Côn Đảo",
        district="Huyện Côn Đảo", 
        province="Tỉnh Bà Rịa - Vũng Tàu"
    ))
    
    assert result.street_address == "01A Võ Thị Sáu, Khu dân cư số 6"
    assert result.district is None  # Districts eliminated in new structure
    assert result.province == "Thành phố Hồ Chí Minh"
    assert result.ward == "Đặc khu Côn Đảo"
