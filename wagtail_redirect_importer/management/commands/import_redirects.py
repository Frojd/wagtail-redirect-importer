import os

import tablib
from tablib.formats import registry
from django.core.management.base import BaseCommand
from wagtail.contrib.redirects.forms import RedirectForm
from wagtail.core.models import Site


class Command(BaseCommand):
    help = "Imports redirects from .csv, .xls, .xlsx"

    def add_arguments(self, parser):
        parser.add_argument(
            "--src", help="Path to file", type=str, required=True,
        )
        parser.add_argument(
            "--site_id", help="The site where redirects will be associated", type=int,
        )
        parser.add_argument(
            "--permanent",
            help="Save redirects as permanent redirects",
            type=bool,
            default=True,
        )
        parser.add_argument(
            "--from_index",
            help="The column where to read from link",
            default=0,
            type=int,
        )
        parser.add_argument(
            "--to_index", help="The column where to read to link", default=1, type=int,
        )
        parser.add_argument(
            "--dry_run",
            default=False,
            help="Run only in test mode, will not create redirects",
            type=bool,
        )
        parser.add_argument(
            "--ask", help="Ask before creating", default=False, type=bool,
        )

        available_formats = [key for key in registry._formats]
        parser.add_argument(
            "--format",
            help="Source file format (.csv, .xls etc)",
            choices=available_formats,
            type=str,
        )

    def handle(self, *args, **options):
        src = options["src"]
        from_index = options.pop("from_index")
        to_index = options.pop("to_index")
        site_id = options.pop("site_id", None)
        permament = options.pop("permanent")
        dry_run = options.pop("dry_run")
        format_ = options.pop("format", None)
        ask = options.pop("ask")

        errors = []
        successes = 0
        skipped = 0
        total = 0
        site = None

        if site_id:
            site = Site.objects.get(id=site_id)

        if not os.path.exists(src):
            raise Exception("Missing file '{0}'".format(src))

        if not os.path.getsize(src) > 0:
            raise Exception("File '{0}' is empty".format(src))

        _, extension = os.path.splitext(src)
        extension = extension.lstrip(".")
        available_formats = [key for key in registry._formats]

        if not format_ and extension not in available_formats:
            raise Exception("Invalid format '{}'".format(extension))

        if not format_:
            format_ = extension

        if extension in ["xls", "xlsx"]:
            mode = "rb"
        else:
            mode = "r"

        with open(src, mode) as fh:
            imported_data = tablib.Dataset().load(fh.read(), format=format_)

            sample_data = tablib.Dataset(
                *imported_data[: min(len(imported_data), 4)],
                headers=imported_data.headers
            )

            try:
                self.stdout.write("Sample data:")
                self.stdout.write(str(sample_data))
            except:
                self.stdout.write("Warning: Cannot display sample data")

            self.stdout.write("--------------")

            if site:
                self.stdout.write("Using site: {}".format(site.hostname))

            self.stdout.write("Importing redirects:")
            for row in imported_data:
                total += 1

                from_link = row[from_index]
                to_link = row[to_index]

                data = {
                    "old_path": from_link,
                    "redirect_link": to_link,
                    "is_permanent": permament,
                }

                if site:
                    data["site"] = site.pk

                form = RedirectForm(data)
                if not form.is_valid():
                    error = form.errors.as_text().replace("\n", "")
                    self.stdout.write(
                        "{}. Error: {} -> {} (Reason: {})".format(
                            total, from_link, to_link, error,
                        )
                    )
                    errors.append(error)
                    continue

                if ask:
                    answer = get_input(
                        "{}. Found {} -> {} Create? Y/n: ".format(
                            total, from_link, to_link,
                        )
                    )

                    if answer != "Y":
                        skipped += 1
                        continue
                else:
                    self.stdout.write("{}. {} -> {}".format(total, from_link, to_link,))

                if dry_run:
                    successes += 1
                    continue

                form.save()
                successes += 1

        self.stdout.write("\n")
        self.stdout.write("Found: {}".format(total))
        self.stdout.write("Created: {}".format(successes))
        self.stdout.write("Skipped : {}".format(skipped))
        self.stdout.write("Errors: {}".format(len(errors)))

    @staticmethod
    def build_header(header):
        header = map(lambda x: x or "", header)
        header_body = " | ".join(header)
        header_body = "| {} |".format(header_body)

        delimiter = "-" * len(header_body)

        out = "{}\n{}\n{}".format(delimiter, header_body, delimiter)
        return out


def get_input(msg):
    return input(msg)
