# ipyswiper

A reusable interactive image gallery component for Jupyter Notebooks.

This component provides an interactive image gallery with:
- Main image display with optional fade effects
- Scrollable thumbnail strip
- Keyboard navigation support
- Multiple instances support without conflicts
- Standalone HTML export capability

## For Administrators

### How to Publish to PyPI

To publish this package to PyPI, you will need to have `flit` installed.

1.  **Install flit**

    ```bash
    pip install flit
    ```

2.  **Build the package**

    ```bash
    flit build
    ```

3.  **Publish to PyPI**

    ```bash
    flit publish
    ```

    You will be prompted for your PyPI username and password.