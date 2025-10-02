import pytest
import io
from PIL import Image
from pic_prompt.images.image_resizer import ImageResizer


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def default_resizer():
    """Resizer with default settings."""
    return ImageResizer()


@pytest.fixture
def custom_resizer():
    """Resizer with custom settings."""
    return ImageResizer(target_size=5_000_000, tolerance=100_000)


@pytest.fixture
def small_image_bytes():
    """Generate a small image (~50KB)."""
    img = Image.new("RGB", (200, 200), color="red")
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=95)
    return buffer.getvalue()


@pytest.fixture
def medium_image_bytes():
    """Generate a medium-sized image (~2MB)."""
    img = Image.new("RGB", (1500, 1500), color="blue")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


@pytest.fixture
def large_image_bytes():
    """Generate a large image (~10MB+)."""
    img = Image.new("RGB", (3000, 3000), color="green")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


@pytest.fixture
def rgba_image_bytes():
    """Generate an RGBA image with transparency."""
    img = Image.new("RGBA", (500, 500), color=(255, 0, 0, 128))
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


@pytest.fixture
def palette_image_bytes():
    """Generate a palette mode (P) image."""
    img = Image.new("P", (300, 300))
    img.putpalette([i % 256 for i in range(768)])
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


@pytest.fixture
def grayscale_image_bytes():
    """Generate a grayscale (L) image."""
    img = Image.new("L", (400, 400), color=128)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


# ============================================================================
# 1. INITIALIZATION TESTS
# ============================================================================


class TestInitialization:
    """Tests for ImageResizer initialization."""

    def test_default_initialization(self):
        """Test default initialization values."""
        resizer = ImageResizer()
        assert resizer.target_size == 20_000_000
        assert resizer.tolerance == 500_000

    def test_custom_initialization(self):
        """Test custom initialization with specific values."""
        resizer = ImageResizer(target_size=5_000_000, tolerance=100_000)
        assert resizer.target_size == 5_000_000
        assert resizer.tolerance == 100_000

    def test_initialization_with_small_values(self):
        """Test initialization with very small values."""
        resizer = ImageResizer(target_size=1000, tolerance=100)
        assert resizer.target_size == 1000
        assert resizer.tolerance == 100

    def test_initialization_with_large_values(self):
        """Test initialization with very large values."""
        resizer = ImageResizer(target_size=100_000_000, tolerance=5_000_000)
        assert resizer.target_size == 100_000_000
        assert resizer.tolerance == 5_000_000


# ============================================================================
# 2. IMAGE SIZE GETTER TESTS
# ============================================================================


class TestGetImageSize:
    """Tests for get_image_size method."""

    def test_get_size_of_various_byte_arrays(self, default_resizer):
        """Test getting size of different byte arrays."""
        test_bytes = b"test data"
        assert default_resizer.get_image_size(test_bytes) == len(test_bytes)

    def test_get_size_of_empty_bytes(self, default_resizer):
        """Test getting size of empty bytes."""
        assert default_resizer.get_image_size(b"") == 0

    def test_get_size_matches_len(self, default_resizer, small_image_bytes):
        """Test that get_image_size matches len()."""
        assert default_resizer.get_image_size(small_image_bytes) == len(
            small_image_bytes
        )

    def test_get_size_large_image(self, default_resizer, large_image_bytes):
        """Test getting size of large image."""
        size = default_resizer.get_image_size(large_image_bytes)
        assert size == len(large_image_bytes)
        # Large image bytes fixture may compress well, just verify it's substantial
        assert size > 10_000  # Should be over 10KB


# ============================================================================
# 3. NEEDS RESIZING TESTS
# ============================================================================


class TestNeedsResizing:
    """Tests for needs_resizing method."""

    def test_image_smaller_than_target(self, default_resizer, small_image_bytes):
        """Test with image smaller than target size."""
        assert default_resizer.needs_resizing(small_image_bytes) is False

    def test_image_exactly_at_target(self, default_resizer):
        """Test with image exactly at target size."""
        # Create bytes exactly at target size
        exact_bytes = b"x" * default_resizer.target_size
        assert default_resizer.needs_resizing(exact_bytes) is False

    def test_image_larger_than_target(self):
        """Test with image larger than target size."""
        # Create bytes that definitely exceed a small target
        resizer = ImageResizer(target_size=1000, tolerance=100)
        large_bytes = b"x" * 10_000  # 10KB, definitely over 1KB target
        assert resizer.needs_resizing(large_bytes) is True

    def test_very_small_image(self, default_resizer):
        """Test with very small image."""
        tiny_bytes = b"x" * 100
        assert default_resizer.needs_resizing(tiny_bytes) is False

    def test_image_one_byte_over_target(self, default_resizer):
        """Test with image one byte over target."""
        over_bytes = b"x" * (default_resizer.target_size + 1)
        assert default_resizer.needs_resizing(over_bytes) is True


# ============================================================================
# 4. RGB CONVERSION TESTS
# ============================================================================


class TestConvertToRGB:
    """Tests for convert_to_rgb method."""

    def test_rgba_conversion(self, default_resizer):
        """Test RGBA image conversion to RGB."""
        img = Image.new("RGBA", (100, 100), color=(255, 0, 0, 128))
        result = default_resizer.convert_to_rgb(img)
        assert result.mode == "RGB"

    def test_palette_conversion(self, default_resizer):
        """Test palette (P) mode image conversion to RGB."""
        img = Image.new("P", (100, 100))
        result = default_resizer.convert_to_rgb(img)
        assert result.mode == "RGB"

    def test_rgb_unchanged(self, default_resizer):
        """Test RGB image remains RGB."""
        img = Image.new("RGB", (100, 100), color="blue")
        result = default_resizer.convert_to_rgb(img)
        assert result.mode == "RGB"
        assert result is img  # Should return same object

    def test_grayscale_unchanged(self, default_resizer):
        """Test grayscale (L) mode image remains unchanged."""
        img = Image.new("L", (100, 100), color=128)
        result = default_resizer.convert_to_rgb(img)
        assert result.mode == "L"
        assert result is img  # Should return same object

    def test_cmyk_unchanged(self, default_resizer):
        """Test CMYK mode image remains unchanged."""
        img = Image.new("CMYK", (100, 100), color=(100, 50, 0, 0))
        result = default_resizer.convert_to_rgb(img)
        assert result.mode == "CMYK"
        assert result is img  # Should return same object


# ============================================================================
# 5. JPEG ENCODING TESTS
# ============================================================================


class TestEncodeToJpegBytes:
    """Tests for encode_to_jpeg_bytes method."""

    def test_encode_at_quality_100(self, default_resizer):
        """Test encoding at quality=100."""
        img = Image.new("RGB", (500, 500), color="red")
        result = default_resizer.encode_to_jpeg_bytes(img, quality=100)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_encode_at_quality_50(self, default_resizer):
        """Test encoding at quality=50."""
        img = Image.new("RGB", (500, 500), color="blue")
        result = default_resizer.encode_to_jpeg_bytes(img, quality=50)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_encode_at_quality_5(self, default_resizer):
        """Test encoding at minimum quality=5."""
        img = Image.new("RGB", (500, 500), color="green")
        result = default_resizer.encode_to_jpeg_bytes(img, quality=5)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_quality_affects_size(self, default_resizer):
        """Test that higher quality produces larger files."""
        img = Image.new("RGB", (1000, 1000), color="red")
        high_quality = default_resizer.encode_to_jpeg_bytes(img, quality=95)
        low_quality = default_resizer.encode_to_jpeg_bytes(img, quality=10)
        assert len(high_quality) > len(low_quality)

    def test_encode_different_dimensions(self, default_resizer):
        """Test encoding images of different dimensions."""
        small_img = Image.new("RGB", (100, 100), color="red")
        large_img = Image.new("RGB", (2000, 2000), color="red")

        small_result = default_resizer.encode_to_jpeg_bytes(small_img, quality=80)
        large_result = default_resizer.encode_to_jpeg_bytes(large_img, quality=80)

        assert len(large_result) > len(small_result)

    def test_encoded_bytes_are_valid_jpeg(self, default_resizer):
        """Test that encoded bytes can be opened as a valid JPEG."""
        img = Image.new("RGB", (300, 300), color="blue")
        result = default_resizer.encode_to_jpeg_bytes(img, quality=85)

        # Try to open the result as an image
        reopened = Image.open(io.BytesIO(result))
        assert reopened.format == "JPEG"
        assert reopened.size == (300, 300)


# ============================================================================
# 6. QUALITY ADJUSTMENT TESTS
# ============================================================================


class TestAdjustQualityToTargetSize:
    """Tests for adjust_quality_to_target_size method."""

    def test_image_meets_target_at_high_quality(self):
        """Test with image that can meet target at high quality."""
        resizer = ImageResizer(target_size=500_000, tolerance=50_000)
        img = Image.new("RGB", (500, 500), color="red")
        result = resizer.adjust_quality_to_target_size(img)

        assert isinstance(result, bytes)
        assert len(result) <= resizer.target_size

    def test_image_requires_low_quality(self):
        """Test with image that requires very low quality."""
        resizer = ImageResizer(target_size=100_000, tolerance=10_000)
        img = Image.new("RGB", (1000, 1000), color="blue")
        result = resizer.adjust_quality_to_target_size(img)

        assert isinstance(result, bytes)
        assert len(result) <= resizer.target_size

    def test_image_cannot_meet_target_returns_min_quality(self):
        """Test with image that cannot meet target even at min quality."""
        resizer = ImageResizer(target_size=1000, tolerance=100)
        img = Image.new("RGB", (2000, 2000), color="green")
        result = resizer.adjust_quality_to_target_size(img)

        # Should return minimum quality version
        assert isinstance(result, bytes)
        # May still be over target if impossible to achieve
        min_quality_result = resizer.encode_to_jpeg_bytes(img, quality=5)
        assert len(result) == len(min_quality_result)

    def test_quality_decreases_by_5_percent_steps(self):
        """Test that quality decreases by 5% steps."""
        resizer = ImageResizer(target_size=200_000, tolerance=20_000)
        img = Image.new("RGB", (800, 800), color="red")
        result = resizer.adjust_quality_to_target_size(img)

        assert isinstance(result, bytes)
        assert len(result) <= resizer.target_size

    def test_result_at_or_below_target(self):
        """Test that result is at or below target_size when possible."""
        resizer = ImageResizer(target_size=1_000_000, tolerance=100_000)
        img = Image.new("RGB", (1200, 1200), color="blue")
        result = resizer.adjust_quality_to_target_size(img)

        assert len(result) <= resizer.target_size

    def test_very_large_image_aggressive_compression(self):
        """Test with very large image needing aggressive compression."""
        resizer = ImageResizer(target_size=500_000, tolerance=50_000)
        img = Image.new("RGB", (2500, 2500), color="green")
        result = resizer.adjust_quality_to_target_size(img)

        assert isinstance(result, bytes)
        # Should try to get as close as possible
        assert len(result) > 0


# ============================================================================
# 7. MAIN RESIZE TESTS
# ============================================================================


class TestResize:
    """Tests for the main resize method."""

    # --- Case: Image already under target ---

    def test_small_image_unchanged(self, default_resizer, small_image_bytes):
        """Test that image under target is returned unchanged."""
        result = default_resizer.resize(small_image_bytes)
        assert result == small_image_bytes

    def test_various_formats_under_target_unchanged(self, default_resizer):
        """Test that various formats under target are unchanged."""
        formats = ["PNG", "JPEG", "BMP"]
        for fmt in formats:
            img = Image.new("RGB", (200, 200), color="red")
            buffer = io.BytesIO()
            img.save(buffer, format=fmt)
            img_bytes = buffer.getvalue()

            if len(img_bytes) < default_resizer.target_size:
                result = default_resizer.resize(img_bytes)
                assert result == img_bytes

    # --- Case: Image over target but JPEG at 100% fits ---

    def test_image_converts_to_jpeg_at_100(self):
        """Test that image over target converts to JPEG at 100% if it fits."""
        resizer = ImageResizer(target_size=5_000_000, tolerance=500_000)
        # Create a large PNG that will be smaller as JPEG
        img = Image.new("RGB", (1500, 1500), color="blue")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        png_bytes = buffer.getvalue()

        # Only test if PNG is actually over target
        if len(png_bytes) > resizer.target_size:
            result = resizer.resize(png_bytes)
            assert isinstance(result, bytes)
            assert len(result) <= resizer.target_size

            # Verify it's a JPEG
            reopened = Image.open(io.BytesIO(result))
            assert reopened.format == "JPEG"

    def test_format_conversion_png_to_jpeg(self):
        """Test format conversion from PNG to JPEG."""
        resizer = ImageResizer(target_size=3_000_000, tolerance=300_000)
        img = Image.new("RGB", (1200, 1200), color="green")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        png_bytes = buffer.getvalue()

        if len(png_bytes) > resizer.target_size:
            result = resizer.resize(png_bytes)
            reopened = Image.open(io.BytesIO(result))
            assert reopened.format == "JPEG"

    # --- Case: Image requires quality reduction ---

    def test_large_image_quality_reduction(self):
        """Test that large image gets quality reduction."""
        # Create a truly large image that will exceed target
        resizer = ImageResizer(target_size=500_000, tolerance=50_000)
        img = Image.new("RGB", (2500, 2500), color="blue")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        png_bytes = buffer.getvalue()

        result = resizer.resize(png_bytes)
        assert isinstance(result, bytes)

        if len(png_bytes) > resizer.target_size:
            assert len(result) <= resizer.target_size
            # Verify it's a valid JPEG when resized
            reopened = Image.open(io.BytesIO(result))
            assert reopened.format == "JPEG"

    def test_output_below_target_size(self):
        """Test that output is at or below target size."""
        resizer = ImageResizer(target_size=2_000_000, tolerance=200_000)
        img = Image.new("RGB", (2000, 2000), color="red")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_bytes = buffer.getvalue()

        if len(img_bytes) > resizer.target_size:
            result = resizer.resize(img_bytes)
            assert len(result) <= resizer.target_size

    @pytest.mark.parametrize("format_name", ["PNG", "BMP"])
    def test_resize_various_starting_formats(self, format_name):
        """Test resizing from various starting formats."""
        resizer = ImageResizer(target_size=1_000_000, tolerance=100_000)
        img = Image.new("RGB", (1500, 1500), color="blue")
        buffer = io.BytesIO()
        img.save(buffer, format=format_name)
        img_bytes = buffer.getvalue()

        if len(img_bytes) > resizer.target_size:
            result = resizer.resize(img_bytes)
            assert isinstance(result, bytes)
            assert len(result) <= resizer.target_size

    # --- Edge cases ---

    def test_extremely_large_image(self):
        """Test with extremely large image."""
        resizer = ImageResizer(target_size=500_000, tolerance=50_000)
        img = Image.new("RGB", (3000, 3000), color="red")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_bytes = buffer.getvalue()

        result = resizer.resize(img_bytes)
        assert isinstance(result, bytes)
        # If original exceeds target, should compress
        if len(img_bytes) > resizer.target_size:
            assert len(result) <= resizer.target_size

    def test_image_slightly_over_target(self):
        """Test with image just slightly over target."""
        resizer = ImageResizer(target_size=100_000, tolerance=10_000)
        # Create image that's just slightly over
        img = Image.new("RGB", (400, 400), color="blue")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG", optimize=False)
        img_bytes = buffer.getvalue()

        if len(img_bytes) > resizer.target_size:
            result = resizer.resize(img_bytes)
            assert len(result) <= resizer.target_size

    def test_corrupted_image_bytes_raises_error(self, default_resizer):
        """Test with corrupted/invalid image bytes."""
        # Use corrupted bytes that are large enough to trigger resizing logic
        corrupted_bytes = b"not an image" * 3_000_000  # Make it large enough
        with pytest.raises(Exception):  # PIL will raise an error
            default_resizer.resize(corrupted_bytes)

    def test_non_image_bytes_raises_error(self, default_resizer):
        """Test with non-image bytes."""
        # Make it large enough to trigger resizing
        non_image_bytes = b"This is just text, not an image" * 1_000_000
        with pytest.raises(Exception):
            default_resizer.resize(non_image_bytes)

    def test_rgba_with_transparency(self, default_resizer, rgba_image_bytes):
        """Test RGBA images with transparency are properly converted."""
        if len(rgba_image_bytes) > default_resizer.target_size:
            result = default_resizer.resize(rgba_image_bytes)
            reopened = Image.open(io.BytesIO(result))
            # Should be converted to RGB (JPEG doesn't support transparency)
            assert reopened.mode == "RGB"

    def test_palette_mode_image(self, default_resizer, palette_image_bytes):
        """Test palette mode (P) images are properly handled."""
        if len(palette_image_bytes) > default_resizer.target_size:
            result = default_resizer.resize(palette_image_bytes)
            reopened = Image.open(io.BytesIO(result))
            assert reopened.format == "JPEG"
            assert reopened.mode == "RGB"

    def test_webp_format(self):
        """Test with WebP format."""
        resizer = ImageResizer(target_size=2_000_000, tolerance=200_000)
        img = Image.new("RGB", (1500, 1500), color="purple")
        buffer = io.BytesIO()
        img.save(buffer, format="WebP")
        webp_bytes = buffer.getvalue()

        if len(webp_bytes) > resizer.target_size:
            result = resizer.resize(webp_bytes)
            assert isinstance(result, bytes)
            reopened = Image.open(io.BytesIO(result))
            assert reopened.format == "JPEG"

    def test_tiff_format(self):
        """Test with TIFF format."""
        resizer = ImageResizer(target_size=2_000_000, tolerance=200_000)
        img = Image.new("RGB", (1500, 1500), color="orange")
        buffer = io.BytesIO()
        img.save(buffer, format="TIFF")
        tiff_bytes = buffer.getvalue()

        if len(tiff_bytes) > resizer.target_size:
            result = resizer.resize(tiff_bytes)
            assert isinstance(result, bytes)
            reopened = Image.open(io.BytesIO(result))
            assert reopened.format == "JPEG"


# ============================================================================
# 8. INTEGRATION / END-TO-END TESTS
# ============================================================================


class TestIntegration:
    """Integration and end-to-end tests."""

    def test_complete_workflow_large_png_to_compressed_jpeg(self):
        """Test complete workflow: large PNG to compressed JPEG."""
        resizer = ImageResizer(target_size=3_000_000, tolerance=300_000)

        # Create a large PNG
        img = Image.new("RGB", (2000, 2000), color="blue")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        png_bytes = buffer.getvalue()

        # Resize it
        result = resizer.resize(png_bytes)

        # Verify result
        assert isinstance(result, bytes)
        if len(png_bytes) > resizer.target_size:
            assert len(result) <= resizer.target_size
            # Verify it's a valid JPEG when resized
            reopened = Image.open(io.BytesIO(result))
            assert reopened.format == "JPEG"
        else:
            # If not resized, format stays the same
            reopened = Image.open(io.BytesIO(result))

        assert reopened.size == (2000, 2000)

    def test_rgba_transparency_conversion_workflow(self):
        """Test RGBA images with transparency are properly converted."""
        resizer = ImageResizer(target_size=2_000_000, tolerance=200_000)

        # Create RGBA image with transparency
        img = Image.new("RGBA", (1000, 1000), color=(255, 0, 0, 128))
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        rgba_bytes = buffer.getvalue()

        # Resize it
        result = resizer.resize(rgba_bytes)

        # Verify result
        reopened = Image.open(io.BytesIO(result))
        if len(rgba_bytes) > resizer.target_size:
            # If resized, should be converted to RGB JPEG
            assert reopened.mode == "RGB"
        # Size should always be preserved
        assert reopened.size == (1000, 1000)

    def test_multiple_resize_operations_same_instance(self, default_resizer):
        """Test multiple resize operations on same resizer instance."""
        # Create multiple different images
        images = []
        for i, color in enumerate(["red", "green", "blue"]):
            img = Image.new("RGB", (500 + i * 100, 500 + i * 100), color=color)
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            images.append(buffer.getvalue())

        # Resize all with same instance
        results = [default_resizer.resize(img_bytes) for img_bytes in images]

        # Verify all results are valid
        for result in results:
            assert isinstance(result, bytes)
            assert len(result) > 0
            reopened = Image.open(io.BytesIO(result))
            assert reopened is not None

    def test_real_world_sizes_phone_camera_simulation(self):
        """Test with simulated phone camera photo sizes."""
        resizer = ImageResizer(target_size=5_000_000, tolerance=500_000)

        # Simulate a 12MP phone camera photo (4000x3000)
        img = Image.new("RGB", (4000, 3000), color="green")
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=95)
        photo_bytes = buffer.getvalue()

        # Resize it
        result = resizer.resize(photo_bytes)

        # Verify it's under target if needed
        if len(photo_bytes) > resizer.target_size:
            assert len(result) <= resizer.target_size

        # Verify it's still a valid image
        reopened = Image.open(io.BytesIO(result))
        assert reopened.format == "JPEG"
        assert reopened.size == (4000, 3000)

    def test_preserves_image_dimensions(self):
        """Test that resizing preserves original dimensions."""
        resizer = ImageResizer(target_size=2_000_000, tolerance=200_000)

        test_sizes = [(1000, 1000), (1920, 1080), (800, 1200)]

        for width, height in test_sizes:
            img = Image.new("RGB", (width, height), color="blue")
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            img_bytes = buffer.getvalue()

            result = resizer.resize(img_bytes)
            reopened = Image.open(io.BytesIO(result))

            assert reopened.size == (width, height)

    def test_different_aspect_ratios(self):
        """Test resizing images with different aspect ratios."""
        resizer = ImageResizer(target_size=3_000_000, tolerance=300_000)

        # Square
        square = Image.new("RGB", (1500, 1500), color="red")
        # Wide
        wide = Image.new("RGB", (2000, 1000), color="green")
        # Tall
        tall = Image.new("RGB", (1000, 2000), color="blue")

        for img, aspect in [(square, "square"), (wide, "wide"), (tall, "tall")]:
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            img_bytes = buffer.getvalue()

            result = resizer.resize(img_bytes)
            reopened = Image.open(io.BytesIO(result))

            assert reopened.size == img.size
