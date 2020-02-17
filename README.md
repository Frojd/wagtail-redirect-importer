[![Build Status](https://travis-ci.org/frojd/wagtail-redirect-importer.svg?branch=develop)](https://travis-ci.org/frojd/wagtail-redirect-importer)
# Wagtail Redirect Importer

Your friendly neighborhood importer that lets you import redirects from different tabular data formats, such as .csv and .xls

![Screen1](https://raw.githubusercontent.com/frojd/wagtail-redirect-importer/develop/img/screen_1.png)


## Features

- Bulk import redirects from the Wagtail admin
- Supports these formats:
    - csv
    - tsv
    - xls
    - xlsx
    - df
    - Basically [all import formats supported by tablib](https://tablib.readthedocs.io/en/stable/formats/)
- The cli tool `import_redirects` for powerusers


## Requirements

- Python 3.5+
- Wagtail 2.7+


## Installation

Install the library:

```
pip install wagtail_redirect_importer
```

Add `wagtail_redirect_importer` to your `INSTALLED_APPS` in Django settings.

```python
INSTALLED_APPS = (
    # ...
    'wagtail_redirect_importer',
)
```


## Screenshots

![Screen1](https://raw.githubusercontent.com/frojd/wagtail-redirect-importer/develop/img/screen_1.png)

Step 1: Select data file and format

![Screen2](https://raw.githubusercontent.com/frojd/wagtail-redirect-importer/develop/img/screen_2.png)

Step 2: Inspect data, configure header mapping and target site, then hit import

![Screen3](https://raw.githubusercontent.com/frojd/wagtail-redirect-importer/develop/img/screen_3.png)

Step 3: After import is complete you get a summary with potential error details


## Credits

- [django-import-export](https://github.com/django-import-export/django-import-export) - Pieces of the admin code are heavily inspired by this library, it also includes the modules for formats and temporary storage.
- [tablib](https://github.com/jazzband/tablib) - Enables us to load data from several data formats.


## License

Wagtail-Redirect-Importer is released under the [MIT License](http://www.opensource.org/licenses/MIT).
