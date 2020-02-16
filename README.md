[![Build Status](https://travis-ci.org/frojd/wagtail-redirect-importer.svg?branch=develop)](https://travis-ci.org/frojd/wagtail-redirect-importer)
# Wagtail Redirect Importer

Your friendly neighborhood importer that lets you import redirects from different tabular data formats, such as .csv and .xls

![Screen1](https://raw.githubusercontent.com/frojd/wagtail-redirect-importer/develop/img/screen1.png)
![Screen2](https://raw.githubusercontent.com/frojd/wagtail-redirect-importer/develop/img/screen2.png)
![Screen3](https://raw.githubusercontent.com/frojd/wagtail-redirect-importer/develop/img/screen3.png)

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

## Credits

- [django-import-export](https://github.com/django-import-export/django-import-export) - Pieces of the admin code are heavily inspired by this library, it also includes the modules for formats and temporary storage.
- [tablib](https://github.com/jazzband/tablib) - Enables us to load data from several data formats.

## License

Wagtail-Redirect-Importer is released under the [MIT License](http://www.opensource.org/licenses/MIT).
