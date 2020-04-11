import os

from django.test import TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from wagtail.contrib.redirects.models import Redirect
from wagtail.core.models import Page, Site
from wagtail.tests.utils import WagtailTestUtils

from ..base_formats import DEFAULT_FORMATS
from ..admin_views import write_to_tmp_storage


TEST_ROOT = os.path.abspath(os.path.dirname(__file__))


@override_settings(
    ALLOWED_HOSTS=["testserver", "localhost", "test.example.com", "other.example.com"]
)
class TestRedirectImporterAdminView(TestCase, WagtailTestUtils):
    def setUp(self):
        self.login()

    def get(self, params={}):
        return self.client.get(reverse("wagtailredirectimporter:start"), params)

    def post(self, post_data={}):
        return self.client.post(reverse("wagtailredirectimporter:start"), post_data)

    def post_import(self, post_data={}):
        return self.client.post(reverse("wagtailredirectimporter:import"), post_data)

    def test_request_start_with_get_returns_initial_form(self):
        response = self.get()
        self.assertEqual(
            response.templates[0].name, "wagtail_redirect_importer/choose_file.html",
        )

    def test_empty_import_file_returns_error(self):
        response = self.post({"import_file": "", "input_format": "0",})

        self.assertTrue("import_file" in response.context["form"].errors)

    def test_valid_csv_triggers_confirm_view(self):
        f = "{}/files/example.csv".format(TEST_ROOT)
        (_, filename) = os.path.split(f)

        with open(f, "rb") as infile:
            upload_file = SimpleUploadedFile(filename, infile.read())

            response = self.post({"import_file": upload_file, "input_format": "0",})

            self.assertEqual(
                response.templates[0].name,
                "wagtail_redirect_importer/confirm_import.html",
            )
            self.assertEqual(len(response.context["dataset"]), 3)

    def test_import_step(self):
        f = "{}/files/example.csv".format(TEST_ROOT)
        (_, filename) = os.path.split(f)

        with open(f, "rb") as infile:
            upload_file = SimpleUploadedFile(filename, infile.read())

            self.assertEqual(Redirect.objects.all().count(), 0)

            response = self.post({"import_file": upload_file, "input_format": "0",})

            import_response = self.post_import(
                {
                    **response.context["form"].initial,
                    "from_index": 0,
                    "to_index": 1,
                    "permanent": True,
                }
            )

            self.assertEqual(
                import_response.templates[0].name,
                "wagtail_redirect_importer/import_summary.html",
            )

            self.assertEqual(Redirect.objects.all().count(), 2)

    def test_permanent_setting(self):
        f = "{}/files/example.csv".format(TEST_ROOT)
        (_, filename) = os.path.split(f)

        with open(f, "rb") as infile:
            upload_file = SimpleUploadedFile(filename, infile.read())

            self.assertEqual(Redirect.objects.all().count(), 0)

            response = self.post({"import_file": upload_file, "input_format": "0",})

            import_response = self.post_import(
                {
                    **response.context["form"].initial,
                    "from_index": 0,
                    "to_index": 1,
                    "permanent": False,
                }
            )

            self.assertEqual(
                import_response.templates[0].name,
                "wagtail_redirect_importer/import_summary.html",
            )

            self.assertFalse(Redirect.objects.first().is_permanent)

    def test_site_setting(self):
        f = "{}/files/example.csv".format(TEST_ROOT)
        (_, filename) = os.path.split(f)

        default_site = Site.objects.first()
        new_site = Site.objects.create(
            hostname="hello.dev", root_page=default_site.root_page,
        )

        with open(f, "rb") as infile:
            upload_file = SimpleUploadedFile(filename, infile.read())

            self.assertEqual(Redirect.objects.all().count(), 0)

            response = self.post({"import_file": upload_file, "input_format": "0",})

            import_response = self.post_import(
                {
                    **response.context["form"].initial,
                    "from_index": 0,
                    "to_index": 1,
                    "permanent": False,
                    "site": new_site.pk,
                }
            )

            self.assertEqual(
                import_response.templates[0].name,
                "wagtail_redirect_importer/import_summary.html",
            )

            self.assertEqual(Redirect.objects.count(), 2)
            self.assertEqual(Redirect.objects.first().site, new_site)

    def test_import_xls(self):
        f = "{}/files/example.xls".format(TEST_ROOT)
        (_, filename) = os.path.split(f)

        with open(f, "rb") as infile:
            upload_file = SimpleUploadedFile(filename, infile.read())

            self.assertEqual(Redirect.objects.all().count(), 0)

            response = self.post({"import_file": upload_file, "input_format": "1",})

            self.assertEqual(
                response.templates[0].name,
                "wagtail_redirect_importer/confirm_import.html",
            )

            import_response = self.post_import(
                {
                    **response.context["form"].initial,
                    "from_index": 0,
                    "to_index": 1,
                    "permanent": True,
                }
            )

            self.assertEqual(
                import_response.templates[0].name,
                "wagtail_redirect_importer/import_summary.html",
            )

            self.assertEqual(Redirect.objects.all().count(), 3)

    def test_import_xlsx(self):
        f = "{}/files/example.xlsx".format(TEST_ROOT)
        (_, filename) = os.path.split(f)

        with open(f, "rb") as infile:
            upload_file = SimpleUploadedFile(filename, infile.read())

            self.assertEqual(Redirect.objects.all().count(), 0)

            response = self.post({"import_file": upload_file, "input_format": "2",})

            self.assertEqual(
                response.templates[0].name,
                "wagtail_redirect_importer/confirm_import.html",
            )

            import_response = self.post_import(
                {
                    **response.context["form"].initial,
                    "from_index": 0,
                    "to_index": 1,
                    "permanent": True,
                }
            )

            self.assertEqual(
                import_response.templates[0].name,
                "wagtail_redirect_importer/import_summary.html",
            )

            self.assertEqual(Redirect.objects.all().count(), 3)
