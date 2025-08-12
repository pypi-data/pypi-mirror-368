import os
import streamlit.components.v1 as components

_RELEASE = True

if not _RELEASE:
    _component_func = components.declare_component(
        "st_copy_button",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component(
        "st_copy_button", path=build_dir
    )


def st_copy_button(
    text: str,
    before_copy_label: str = "📋",
    after_copy_label: str = "✅",
    show_text: bool = False,
    key=None
):
    """Create a button that copies text to the user's clipboard when clicked.

    Parameters
    ----------
    text: str
        The text to be copied to the clipboard.
    before_copy_label: str
        The button label before copying occurs. Defaults to "📋".
    after_copy_label: str
        The button label after copying occurs. Defaults to "✅".
    show_text: bool
        If True, displays the text to be copied as a second, also clickable
        button, to the left of the first.
    key: str or None
        An optional key that uniquely identifies this component.

    Returns
    -------
    component_value
    """
    component_value = _component_func(
        text=text,
        before_copy_label=before_copy_label,
        after_copy_label=after_copy_label,
        show_text=show_text,
        key=key,
    )
    return component_value
