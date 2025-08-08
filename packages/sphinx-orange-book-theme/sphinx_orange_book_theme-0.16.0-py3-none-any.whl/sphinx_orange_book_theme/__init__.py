"""An orange version of sphinx-book-theme."""

import os

import sphinx.application


def setup(app: sphinx.application.Sphinx) -> None:
    """Setup this theme.

    Args:
        app (sphinx.application.Sphinx): Sphinx application.
    """
    theme_path = os.path.dirname(os.path.abspath(__file__))
    app.add_html_theme("sphinx_orange_book_theme", theme_path)
