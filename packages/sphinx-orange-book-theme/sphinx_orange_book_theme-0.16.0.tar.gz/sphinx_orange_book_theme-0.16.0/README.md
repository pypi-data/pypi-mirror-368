# sphinx-orange-book-theme

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/sphinx-orange-book-theme)
[![PyPI - Version](https://img.shields.io/pypi/v/sphinx-orange-book-theme)](https://pypi.org/project/sphinx-orange-book-theme/)
![PyPI - License](https://img.shields.io/pypi/l/sphinx-orange-book-theme)
![Gitlab pipeline status](https://img.shields.io/gitlab/pipeline-status/MusicScience37Projects%2Futility-libraries%2Fsphinx-orange-book-theme?branch=main)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

An orange version of [sphinx-book-theme](https://sphinx-book-theme.readthedocs.io/en/latest/index.html).

This python package overrides CSS of sphinx-book-theme
to change its design.

For an example of built document, see
[Documentation built on main branch](https://sphinx-orange-book-theme-musicscience37projects--1dc46f9ab80e60.gitlab.io/).

## Usage

To use this theme,

1. Install
   [sphinx-orange-book-theme](https://pypi.org/project/sphinx-orange-book-theme/)
   package from PyPI, for example, using the following command:

   ```shell
   pip install sphinx-orange-book-theme
   ```

2. Update your conf.py file to use `sphinx_orange_book_theme` theme as following:

   ```python
   html_theme = "sphinx_orange_book_theme"
   ```

3. (Recommended) Add following options to conf.py:

   ```python
   html_theme_options = {
       "pygments_light_style": "gruvbox-light",
       "pygments_dark_style": "native",
   }
   ```

   Although these options are not required to use this theme,
   this theme is designed with the above options.

## Documentation

- [Documentation built on main branch](https://sphinx-orange-book-theme-musicscience37projects--1dc46f9ab80e60.gitlab.io/)
