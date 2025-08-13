# ImageNet Classes

A Python package for managing and retrieving ImageNet-1k (ImageNet2012) class names and mappings.

## Installation

### From PyPI (when published)
```bash
pip install imagenet-classes
```

### From Source
```bash
git clone https://github.com/gonikisgo/imagenet-classes.git
cd imagenet-classes
pip install -e .
```

## Quick Start

```python
from class_mapping import ClassDictionary

# Initialize the class dictionary
class_dict = ClassDictionary()

# Get class name for ImageNet-1k class index 0
class_name = class_dict.get_class_name(0)
print(f"Class 0: {class_name}")

# Get ImageNet21k to ImageNet-1k class mapping
class_1k = class_dict.get_class_1k("n01440764")
print(f"Class 1k mapping: {class_1k}")

# Get custom class name
custom_name = class_dict.get_custom_class_name(0)
print(f"Custom name: {custom_name}")
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue on the [GitHub repository](https://github.com/gonikisgo/imagenet-classes/issues).