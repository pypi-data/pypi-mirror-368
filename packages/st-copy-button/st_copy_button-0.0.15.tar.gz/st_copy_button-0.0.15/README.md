# st-copy-button

A simple Streamlit component for copying text to the user's clipboard with one click.

Contains portions derived from mmz-001's st-copy-to-clipboard component.

## Installation instructions

```sh
pip install st-copy-button
```

## Usage instructions

> Note: The clipboard API is only available in secure contexts (HTTPS)

```python
import streamlit as st
from st_copy_button import st_copy_button

# Basic usage
st_copy_button("Copy this to clipboard")

# With custom labels
st_copy_button(
    text="Custom text",
    before_copy_label="📋 Push to copy",
    after_copy_label="✅ Text copied!",
    show_text=True
)
```
