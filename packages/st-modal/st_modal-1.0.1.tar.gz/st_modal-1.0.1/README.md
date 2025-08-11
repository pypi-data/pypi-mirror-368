# st-modal

A modern modal dialog component for Streamlit applications. This is a fork of the original [streamlit_modal](https://github.com/teamtv/streamlit_modal) with improvements and adjustments.

## Installation

```bash
pip install st-modal
```

## Quick Start

```python
import streamlit as st
from st_modal import Modal

# Create modal with markdown title
modal = Modal("## 🎉 My Modal", key="my-modal")

# Trigger to open modal
if st.button("Open Modal"):
    modal.open()

# Modal content
if modal.is_open():
    with modal.container():
        st.write("Hello from inside the modal!")
        
        value = st.slider("Pick a value", 0, 100, 50)
        st.write(f"Selected: {value}")
        
        if st.button("Close", key="close-modal"):
            modal.close()
```

## API Reference

### Modal Class

```python
Modal(title, key, padding=20, max_width=744, show_close_button=True)
```

**Parameters:**
- `title` (str): Title displayed at the top of the modal. Supports full markdown syntax including `#` headers, **bold**, *italic*, and emojis
- `key` (str): Unique identifier for the modal (required)
- `padding` (int): Internal padding in pixels (default: 20)
- `max_width` (int): Maximum width in pixels (default: 744)
- `show_close_button` (bool): Whether to show the Material Design close button (default: True)

**Methods:**
- `modal.open()`: Opens the modal and triggers a rerun
- `modal.close()`: Closes the modal and triggers a rerun
- `modal.is_open()`: Returns True if modal is currently open
- `modal.container()`: Context manager for adding content to the modal