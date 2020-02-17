from django.shortcuts import render
from django.http import HttpResponse
from django.utils.encoding import force_str
from django.utils.translation import ugettext as _
from wagtail.core import hooks
from wagtail.contrib.redirects.forms import RedirectForm
from wagtail.contrib.redirects.permissions import permission_policy
from wagtail.admin.auth import PermissionPolicyChecker, permission_denied

from .base_formats import DEFAULT_FORMATS
from .tmp_storages import TempFolderStorage
from .forms import ImportForm, ConfirmImportForm


from_encoding = "utf-8"
permission_checker = PermissionPolicyChecker(permission_policy)


@permission_checker.require_any('add')
def start(request):
    if not request.POST:
        return render(request, "wagtail_redirect_importer/choose_file.html", {
            'form': ImportForm(DEFAULT_FORMATS),
        })

    form_kwargs = {}
    form = ImportForm(
        DEFAULT_FORMATS,
        request.POST or None,
        request.FILES or None,
        **form_kwargs
    )

    if not form.is_valid():
        return render(request, "wagtail_redirect_importer/choose_file.html", {
            'form': form,
        })

    import_formats = get_import_formats()
    input_format = import_formats[
        int(form.cleaned_data['input_format'])
    ]()
    import_file = form.cleaned_data['import_file']
    tmp_storage = write_to_tmp_storage(import_file, input_format)

    try:
        data = tmp_storage.read(input_format.get_read_mode())
        if not input_format.is_binary() and from_encoding:
            data = force_str(data, from_encoding)
        dataset = input_format.create_dataset(data)
    except UnicodeDecodeError as e:
        return HttpResponse(_(u"<h1>Imported file has a wrong encoding: %s</h1>" % e))
    except Exception as e:
        return HttpResponse(_(u"<h1>%s encountered while trying to read file: %s</h1>" % (type(e).__name__, import_file.name)))

    initial = {
        'import_file_name': tmp_storage.name,
        'original_file_name': import_file.name,
        'input_format': form.cleaned_data['input_format'],
    }

    return render(request, "wagtail_redirect_importer/confirm_import.html", {
        'form': ConfirmImportForm(dataset.headers, initial=initial),
        'dataset': dataset,
    })


def get_import_formats():
    return [f for f in DEFAULT_FORMATS if f().can_import()]


@permission_checker.require_any('add')
def import_file(request):
    if not request.POST:
        return HttpResponse("ERR", content_type="text/plain")

    form_kwargs = {}
    form = ConfirmImportForm(
        DEFAULT_FORMATS,
        request.POST or None,
        request.FILES or None,
        **form_kwargs
    )

    is_confirm_form_valid = form.is_valid()

    import_formats = get_import_formats()
    input_format = import_formats[
        int(form.cleaned_data['input_format'])
    ]()
    tmp_storage = TempFolderStorage(
        name=form.cleaned_data['import_file_name']
    )

    if not is_confirm_form_valid:
        data = tmp_storage.read(input_format.get_read_mode())
        dataset = input_format.create_dataset(data)

        initial = {
            'import_file_name': tmp_storage.name,
            'original_file_name': form.cleaned_data['import_file_name'],
            'input_format': form.cleaned_data['input_format'],
        }

        return render(request, "wagtail_redirect_importer/confirm_import.html", {
            'form': ConfirmImportForm(
                dataset.headers,
                request.POST or None,
                request.FILES or None,
                initial=initial,
            ),
            'dataset': dataset,
        })

    data = tmp_storage.read(input_format.get_read_mode())
    if not input_format.is_binary() and from_encoding:
        data = force_str(data, from_encoding)
    dataset = input_format.create_dataset(data)

    import_summary = create_redirects_from_dataset(dataset, {
        'from_index': int(form.cleaned_data['from_index']),
        'to_index': int(form.cleaned_data['to_index']),
        'permanent': form.cleaned_data['permanent'],
        'site': form.cleaned_data['site'],
    })

    tmp_storage.remove()

    return render(request, "wagtail_redirect_importer/import_summary.html", {
        'form': ImportForm(DEFAULT_FORMATS),
        'import_summary': import_summary,
    })


def create_redirects_from_dataset(dataset, config):
    errors = []
    successes = 0
    total = 0

    for row in dataset:
        total += 1

        from_link = row[config['from_index']]
        to_link = row[config['to_index']]

        data = {
            'old_path': from_link,
            'redirect_link': to_link,
            'is_permanent': config['permanent'],
        }

        if config['site']:
            data['site'] = config['site'].pk

        form = RedirectForm(data)
        if not form.is_valid():
            error = form.errors.as_text().replace('\n', '')
            errors.append([from_link, to_link, error])
            continue

        form.save()
        successes += 1

    return {
        'errors': errors,
        'errors_count': len(errors),
        'successes': successes,
        'total': total,
    }


def write_to_tmp_storage(import_file, input_format):
    tmp_storage = TempFolderStorage()
    data = bytes()
    for chunk in import_file.chunks():
        data += chunk

        tmp_storage.save(data, input_format.get_read_mode())
        return tmp_storage
