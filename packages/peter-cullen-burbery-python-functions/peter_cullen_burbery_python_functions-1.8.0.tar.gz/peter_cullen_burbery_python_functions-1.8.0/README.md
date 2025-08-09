# peter_cullen_burbery_python_functions

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.16727183.svg)](https://doi.org/10.5281/zenodo.16727183)

A utility package by Peter Cullen Burbery offering high-precision date/time formatting, image comparison tools, and system management helpers.

Available on PyPi at [peter_cullen_burbery_python_functions](https://pypi.org/project/peter-cullen-burbery-python-functions/).

📚 Documentation: [Read the Docs](https://peter-cullen-burbery-python-functions.readthedocs.io/) *(auto-generated via Sphinx)*

For most up to date docs, please visit [Read the Docs](https://peter-cullen-burbery-python-functions.readthedocs.io/).

## ✨ Features

### 📅 `date_time_functions`

- `date_time_stamp()`

  Returns a precise timestamp string including:
  - Gregorian calendar date
  - Time with nanosecond precision
  - IANA time zone
  - ISO week format (e.g., `2025-W030-005`)
  - Ordinal day of the year

Example:
```text
2025-007-025 015.005.004.990819700 America/New_York 2025-W030-005 2025-206
```

---

### 🖼️ `image_functions`

- `compare_images(image_path_1, image_path_2)`

  Compares two images using:
  - 🔐 SHA-256 hash
  - 🧮 Pixel-wise difference via `ImageChops`
  - 📏 Structural Similarity Index (SSIM)
  - 📊 ImageMagick absolute error metric (if available)

Outputs:
- Matching/difference status
- SSIM score
- Optional diff image (if images differ)

---

### 🛠️ `system_management_functions`

- `convert_blob_to_raw_github_url(blob_url: str)`

  Converts a GitHub `blob` URL to a `raw` content URL.

  Example:
  ```python
  from peter_cullen_burbery_python_functions.system_management_functions import convert_blob_to_raw_github_url

  raw_url = convert_blob_to_raw_github_url("https://github.com/user/repo/blob/main/script.ps1")
  print(raw_url)
  # Output: https://github.com/user/repo/raw/main/script.ps1
  ```

- `validate_Windows_filename_with_reasons(name: str)`

  Validates a Windows filename against Microsoft’s rules for illegal characters, reserved device names, and invalid trailing characters.

  Returns a dictionary indicating whether the filename is valid, and if not, why.

  Example:
  ```python
  from peter_cullen_burbery_python_functions.system_management_functions import validate_Windows_filename_with_reasons

  result = validate_Windows_filename_with_reasons("CON.txt")
  print(result)
  # Output: {'valid': False, 'problems': [{'character': 'CON', 'reason': 'Reserved device name: console'}]}
  ```

- `valid_Windows_filename(name: str)`

  Lightweight check to determine whether a Windows filename is valid.

  Returns a simple boolean (`True` or `False`) based on the same rules used in `validate_Windows_filename_with_reasons()`.

  Example:
  ```python
  from peter_cullen_burbery_python_functions.system_management_functions import valid_Windows_filename

  print(valid_Windows_filename("normal_file.txt"))  # True
  print(valid_Windows_filename("NUL.txt"))          # False
  ```

---

## 📦 Installation

```bash
pip install peter-cullen-burbery-python-functions
```

## 🧪 Example Usage

```python
from peter_cullen_burbery_python_functions.date_time_functions import date_time_stamp
from peter_cullen_burbery_python_functions.image_functions import compare_images
from peter_cullen_burbery_python_functions.system_management_functions import (
    convert_blob_to_raw_github_url,
    validate_Windows_filename_with_reasons,
    valid_Windows_filename,
)

print("🕒 Timestamp:", date_time_stamp())
compare_images("image1.png", "image2.png")

url = "https://github.com/user/repo/blob/main/example.txt"
print("🔗 Raw URL:", convert_blob_to_raw_github_url(url))

filename = "COM1.txt"
print("📁 Validity with reasons:", validate_Windows_filename_with_reasons(filename))
print("✅ Is valid?", valid_Windows_filename(filename))
```

---

## 📘 Documentation

This package uses [Sphinx](https://www.sphinx-doc.org/) and the [sphinx_rtd_theme](https://sphinx-rtd-theme.readthedocs.io/) to build documentation.

To build docs locally:

```bash
cd docs
make html
```

The output will be in `docs/build/html`.

---

## 🧑‍💻 Author

**Peter Cullen Burbery**

This utility library is part of a broader collection of tools for automation, data processing, and system utility scripting.

---

## ⚠️ Disclaimer

This is a development and educational project. All code is provided in good faith and intended for system automation, productivity, and learning purposes.

If you're a rights holder and want attribution changed or material removed, please contact the maintainer.

---

Maintained with care by Peter Cullen Burbery.

## 📘 Citation

If you use this module in your work, please cite the following:

> Peter Cullen Burbery. (2025). Peter Cullen Burbery Python functions [Software]. Zenodo. https://doi.org/10.5281/zenodo.16727183