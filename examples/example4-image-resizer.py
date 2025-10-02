# This example demonstrates how to use the ImageResizer to resize images to a target size
# It shows how to use the new resize_with_info method to get detailed metadata about
# the resizing process, including the number of passes needed to achieve the target size.
#
# The example uses different target sizes to demonstrate varying compression levels
# and shows how the resizer adapts its quality settings to meet size requirements.
#
# To run this example:
# 1. Install required packages: pip install pic_prompt
# 2. Run: cd pic-prompt && python -m examples.example4-image-resizer [image_path]
#    - image_path: Optional path to the image file to resize (default: examples/sweetgum.jpg)

import os
import sys
from pic_prompt.images.image_resizer import ImageResizer


def format_size(bytes_size: int) -> str:
    """Format bytes to human readable format."""
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} GB"


def print_resize_report(image_name: str, info: dict):
    """Print a detailed report of the resize operation."""
    print(f"\n{'='*60}")
    print(f"RESIZE REPORT: {image_name}")
    print(f"{'='*60}")

    print(f"Original size: {format_size(info['original_size'])}")
    print(f"Final size: {format_size(info['final_size'])}")
    print(f"Target size: {format_size(info['target_size'])}")

    if info["resized"]:
        compression_ratio = info["original_size"] / info["final_size"]
        print(f"Compression ratio: {compression_ratio:.2f}x")
        print(f"Image was resized: {'Yes' if info['resized'] else 'No'}")
        print(f"Format converted: {'Yes' if info['format_converted'] else 'No'}")

        if info["original_format"]:
            print(f"Original format: {info['original_format']}")
        if info.get("final_format"):
            print(f"Final format: {info['final_format']}")

        if info["dimensions"]:
            width, height = info["dimensions"]
            print(f"Dimensions: {width}x{height}")

        if info["passes"] > 0:
            print(f"Number of passes: {info['passes']}")
            print(f"Initial quality: {info['initial_quality']}%")
            print(f"Final quality: {info['final_quality']}%")
            print(f"Quality step: {info['quality_step']}%")
            print(f"Min quality: {info['min_quality']}%")
        else:
            print("Number of passes: 0 (no quality adjustment needed)")
            if info["final_quality"]:
                print(f"JPEG quality: {info['final_quality']}%")
    else:
        print("Image was resized: No (already under target size)")


def main():
    """Demonstrate image resizing with different target sizes."""

    # Parse command line arguments
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        image_path = "examples/sweetgum.jpg"

    # Test with different target sizes to show varying compression levels
    target_sizes = [
        10_000_000,  # 10MB - should not need much compression for our test images
        5_000_000,  # 5MB - may require some compression
        2_000_000,  # 2MB - will likely require quality reduction
        1_000_000,  # 1MB - will definitely require quality reduction
        500_000,  # 500KB - may require multiple passes
    ]

    if not os.path.exists(image_path):
        print(f"Error: Test image {image_path} not found.")
        return

    # Load the original image
    with open(image_path, "rb") as f:
        original_bytes = f.read()

    print("IMAGE RESIZER EXAMPLE")
    print("=" * 60)
    print(f"Testing with image: {image_path}")
    print(f"Original image size: {format_size(len(original_bytes))}")

    # Test each target size
    for target_size in target_sizes:
        print(f"\n{'-'*60}")
        print(f"TARGET SIZE: {format_size(target_size)}")
        print(f"{'-'*60}")

        # Create resizer with this target size
        resizer = ImageResizer(target_size=target_size)

        # Resize and get info
        resized_bytes, info = resizer.resize_with_info(original_bytes)

        # Print detailed report
        print_resize_report(f"{format_size(target_size)} target", info)

        # Optionally save the resized image for inspection
        if info["resized"]:
            output_filename = f"resized_to_{target_size//1_000_000}MB.jpg"
            with open(output_filename, "wb") as f:
                f.write(resized_bytes)
            print(f"Saved resized image as: {output_filename}")

    print(f"\n{'='*60}")
    print("EXAMPLE COMPLETE")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
