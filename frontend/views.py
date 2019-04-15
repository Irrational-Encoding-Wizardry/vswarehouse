from typing import Optional

from django.shortcuts import render, get_object_or_404

from warehouse.models import Project


def get_categories():
    return [
        p["category"]
        for p in Project.objects.order_by("category").values("category").distinct()
    ]


def static_page(request, tab: str, template: str):
    return render(request, f"frontend/{template}.html", {
        "tab": tab,
        "categories": get_categories()
    })


def plugin(request, project: str):
    project = get_object_or_404(Project, identifier=project)
    releases = project.sorted_releases()
    return render(request, "frontend/plugin.html", {
        "tab": project.category,
        "project": project,
        "releases": releases,
        "categories": get_categories()
    })


def listing(request, category: Optional[str] = None):
    tab = category

    projects = Project.objects.get_queryset()
    if category is not None:
        projects = projects.filter(category__exact=category)

    return render(request, "frontend/listing.html", {
        "tab": tab,
        "projects": projects,
        "current_category": category,
        "categories": get_categories()
    })
