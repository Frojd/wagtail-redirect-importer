from io import StringIO
import os
import tempfile

from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import CommandError
from wagtail.core.models import Site
from wagtail.contrib.redirects.models import Redirect


TEST_ROOT = os.path.abspath(os.path.dirname(__file__))


class ImportCsvCommandTest(TestCase):
    def test_empty_command_raises_errors(self):
        with self.assertRaises(CommandError):
            out = StringIO()
            call_command("import_redirects", stdout=out)

    def test_missing_file_raises_error(self):
        with self.assertRaisesMessage(Exception, "Missing file 'random'"):
            out = StringIO()
            call_command("import_redirects", src="random", stdout=out)

    def test_invalid_extension_raises_error(self):
        f = "{}/files/example.numbers".format(TEST_ROOT)

        with self.assertRaisesMessage(Exception, "Invalid format 'numbers'"):
            out = StringIO()
            call_command("import_redirects", src=f, stdout=out)

    def test_empty_file_raises_error(self):
        empty_file = tempfile.NamedTemporaryFile()

        with self.assertRaisesMessage(
            Exception, "File '{}' is empty".format(empty_file.name)
        ):
            out = StringIO()
            call_command("import_redirects", src=empty_file.name, stdout=out)

    def test_header_are_not_imported(self):
        invalid_file = tempfile.NamedTemporaryFile(mode="w+", encoding="utf-8")
        invalid_file.write("from,to")
        invalid_file.seek(0)

        out = StringIO()
        call_command(
            "import_redirects", src=invalid_file.name, stdout=out, format="csv"
        )

        self.assertEqual(Redirect.objects.count(), 0)

    def test_redirect_gets_imported(self):
        invalid_file = tempfile.NamedTemporaryFile(mode="w+", encoding="utf-8")
        invalid_file.write("from,to\n")
        invalid_file.write("/alpha,http://omega.test/")
        invalid_file.seek(0)

        out = StringIO()
        call_command(
            "import_redirects", src=invalid_file.name, stdout=out, format="csv"
        )

        self.assertEqual(Redirect.objects.count(), 1)
        redirect = Redirect.objects.first()
        self.assertEqual(redirect.old_path, "/alpha")
        self.assertEqual(redirect.redirect_link, "http://omega.test/")
        self.assertEqual(redirect.is_permanent, True)

    def test_trailing_slash_gets_stripped(self):
        invalid_file = tempfile.NamedTemporaryFile(mode="w+", encoding="utf-8")
        invalid_file.write("from,to\n")
        invalid_file.write("/alpha/,http://omega.test/")
        invalid_file.seek(0)

        out = StringIO()
        call_command(
            "import_redirects", src=invalid_file.name, stdout=out, format="csv"
        )

        redirect = Redirect.objects.first()
        self.assertEqual(redirect.old_path, "/alpha")
        self.assertEqual(redirect.redirect_link, "http://omega.test/")

    def test_site_id_does_not_exist(self):
        with self.assertRaisesMessage(Exception, "Site matching query does not exist"):
            out = StringIO()
            call_command("import_redirects", src="random", site_id=5, stdout=out)

    def test_redirect_gets_added_to_site(self):
        invalid_file = tempfile.NamedTemporaryFile(mode="w+", encoding="utf-8")
        invalid_file.write("from,to\n")
        invalid_file.write("/alpha/,http://omega.test/")
        invalid_file.seek(0)

        current_site = Site.objects.first()
        site = Site.objects.create(
            hostname="random.test", root_page=current_site.root_page
        )

        out = StringIO()
        call_command(
            "import_redirects",
            src=invalid_file.name,
            site_id=site.pk,
            stdout=out,
            format="csv",
        )

        redirect = Redirect.objects.first()
        self.assertEqual(redirect.old_path, "/alpha")
        self.assertEqual(redirect.redirect_link, "http://omega.test/")
        self.assertEqual(redirect.site, site)

    def test_temporary_redirect(self):
        invalid_file = tempfile.NamedTemporaryFile(mode="w+", encoding="utf-8")
        invalid_file.write("from,to\n")
        invalid_file.write("/alpha/,http://omega.test/")
        invalid_file.seek(0)

        out = StringIO()
        call_command(
            "import_redirects",
            src=invalid_file.name,
            permanent=False,
            stdout=out,
            format="csv",
        )

        redirect = Redirect.objects.first()
        self.assertEqual(redirect.old_path, "/alpha")
        self.assertEqual(redirect.redirect_link, "http://omega.test/")
        self.assertEqual(redirect.is_permanent, False)

    def test_duplicate_from_links_get_skipped(self):
        invalid_file = tempfile.NamedTemporaryFile(mode="w+", encoding="utf-8")
        invalid_file.write("from,to\n")
        invalid_file.write("/alpha/,http://omega.test/\n")
        invalid_file.write("/alpha/,http://omega2.test/\n")
        invalid_file.seek(0)

        out = StringIO()
        call_command(
            "import_redirects",
            src=invalid_file.name,
            permanent=False,
            format="csv",
            stdout=out,
        )

        self.assertEqual(Redirect.objects.count(), 1)

    def test_non_absolute_to_links_get_skipped(self):
        invalid_file = tempfile.NamedTemporaryFile(mode="w+", encoding="utf-8")
        invalid_file.write("from,to\n")
        invalid_file.write("/alpha/,/omega.test/\n")
        invalid_file.seek(0)

        out = StringIO()
        call_command(
            "import_redirects",
            src=invalid_file.name,
            permanent=False,
            stdout=out,
            format="csv",
        )

        self.assertEqual(Redirect.objects.count(), 0)
        self.assertIn("Errors: 1", out.getvalue())

    def test_from_links_are_converted_to_relative(self):
        invalid_file = tempfile.NamedTemporaryFile(mode="w+", encoding="utf-8")
        invalid_file.write("from,to\n")
        invalid_file.write("http://alpha.test/alpha/,http://omega.test/\n")
        invalid_file.seek(0)

        out = StringIO()
        call_command(
            "import_redirects", src=invalid_file.name, format="csv", stdout=out
        )

        self.assertEqual(Redirect.objects.count(), 1)
        redirect = Redirect.objects.first()
        self.assertEqual(redirect.old_path, "/alpha")
        self.assertEqual(redirect.redirect_link, "http://omega.test/")

    def test_column_index_are_used(self):
        invalid_file = tempfile.NamedTemporaryFile(mode="w+", encoding="utf-8")
        invalid_file.write("priority,from,year,to\n")
        invalid_file.write("5,/alpha,2020,http://omega.test/")
        invalid_file.seek(0)

        out = StringIO()
        call_command(
            "import_redirects",
            src=invalid_file.name,
            from_index=1,
            to_index=3,
            format="csv",
            stdout=out,
        )

        self.assertEqual(Redirect.objects.count(), 1)
        redirect = Redirect.objects.first()
        self.assertEqual(redirect.old_path, "/alpha")
        self.assertEqual(redirect.redirect_link, "http://omega.test/")
        self.assertEqual(redirect.is_permanent, True)

    def test_nothing_gets_saved_on_dry_run(self):
        invalid_file = tempfile.NamedTemporaryFile(mode="w+", encoding="utf-8")
        invalid_file.write("from,to\n")
        invalid_file.write("/alpha,http://omega.test/")
        invalid_file.seek(0)

        out = StringIO()
        call_command(
            "import_redirects",
            src=invalid_file.name,
            format="csv",
            dry_run=True,
            stdout=out,
        )

        self.assertEqual(Redirect.objects.count(), 0)
