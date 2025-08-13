#!/usr/bin/env python3
"""
Basic usage example for the imagenet-classes package.
"""

from class_mapping import ClassDictionary


def main():
    """Demonstrate basic usage of the ClassDictionary class."""
    
    print("ImageNet Classes Package - Basic Usage Example")
    print("=" * 50)
    
    # Initialize the class dictionary
    print("Initializing ClassDictionary...")
    class_dict = ClassDictionary()
    
    # Demonstrate utility methods
    print("\n1. Creating class name dictionaries:")
    sample_classes = ['tench', 'goldfish', 'great_white_shark', 'tiger_shark', 'hammerhead']
    
    # Create index to class name mapping
    idx_to_name = class_dict.create_cls_name_dict(sample_classes)
    print(f"   Index to name: {idx_to_name}")
    
    # Create class name to index mapping
    name_to_idx = class_dict.create_im_to_orig(sample_classes)
    print(f"   Name to index: {name_to_idx}")
    
    print("\n2. Accessing class data:")
    print("   Note: Data files (.npy) need to be present for these methods to work")
    
    # Try to get class names (will return None if files don't exist)
    class_name = class_dict.get_class_name(0)
    print(f"   Class 0: {class_name}")
    
    # Try to get custom class names
    custom_name = class_dict.get_custom_class_name(0)
    print(f"   Custom class 0: {custom_name}")
    
    # Try to get ImageNet21k mappings
    class_1k = class_dict.get_class_1k("n01440764")
    print(f"   ImageNet21k mapping for n01440764: {class_1k}")
    
    print("\n3. File paths:")
    print(f"   ImageNet2012 classes: {class_dict.filename}")
    print(f"   ImageNet21k classes: {class_dict.filename_21k}")
    print(f"   Custom classes: {class_dict.custom_cls_filename}")
    
    print("\nExample completed successfully!")
    print("\nTo use with actual data:")
    print("1. Ensure the required .npy files are in the class_mapping directory")
    print("2. The package will automatically load data when methods are called")
    print("3. Data is loaded lazily for optimal memory usage")


if __name__ == "__main__":
    main()
