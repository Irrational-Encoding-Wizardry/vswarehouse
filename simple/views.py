import io
import zipfile

from django.http import FileResponse, Http404, HttpResponse
from django.template import loader
from django.shortcuts import render, get_object_or_404

from warehouse.models import Project, Release


def find_project_fuzzy(project):
    p = Project.objects.filter(identifier__iexact=project).first()
    if p is not None: return p

    project = project.replace("-", ".")
    p = Project.objects.filter(identifier__iexact=project.replace("-", ".")).first()
    if p is not None: return p

    project = project.replace(".", "_")
    p = Project.objects.filter(identifier__iexact=project.replace("-", ".")).first()
    if p is not None: return p

    raise Http404


def overview(request):
    return render(request, "simple/overview.html", {'projects': Project.objects.all()})


def project(request, project):
    project = find_project_fuzzy(project)
    return render(request, "simple/project.html", {'project': project})


def setup(request, project, release):
    project = find_project_fuzzy(project)
    release = get_object_or_404(Release, project=project, release_version=release)
    response = render(request, "install/script.py", {"project": project, "release": release})
    response["Content-Type"] = "text/plain; charset=UTF-8"
    return response


def zip(request, project, release, filename=None):
    project = find_project_fuzzy(project)
    release = get_object_or_404(Release, project=project, release_version=release)

    directory = f"{project.identifier}-{release.pypa_version}"
    target = directory + "/setup.py"
    rendered = loader.render_to_string("install/script.py", {"project": project, "release": release}, request)

    result = io.BytesIO()
    z = zipfile.ZipFile(result, mode="w", compression=zipfile.ZIP_DEFLATED)
    with z.open(target, "w") as f:
        f.write(rendered.encode("utf-8"))
    with z.open(directory + "/MANIFEST.in", "w") as f:
        f.write("global-include *.dll\n".encode("utf-8"))
    z.close()
    return HttpResponse(result.getvalue(), content_type="application/octet-stream")
