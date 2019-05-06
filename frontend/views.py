import pickle
from operator import or_
from functools import reduce
from typing import Optional

from django.core.cache import cache
from django.db.models import Q
from django.shortcuts import render, get_object_or_404

from warehouse.models import Project


def get_categories():
    categories = cache.get("frontend.all_categories")
    if categories is None:
        categories = [
            p["category"]
            for p in Project.objects.order_by("category").values("category").distinct()
        ]
        cache.set("frontend.all_categories", pickle.dumps(categories), 1800)
    else:
        categories = pickle.loads(categories)
    return categories


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

    cat_cache_key = '%All%' if category is None else category.replace(" ", "-")
    projects = cache.get("frontend.listing.qcache::%r" % cat_cache_key)
    if projects is not None:
        projects = pickle.loads(projects)
    else:
        projects = Project.objects.get_queryset()
        if category is not None:
            projects = projects.filter(category__exact=category)
        cache.set("frontend.listing.qcache::%r" % cat_cache_key, pickle.dumps(
            list(projects),
        ), 1800)

    return render(request, "frontend/listing.html", {
        "tab": tab,
        "projects": projects,
        "current_category": category,
        "categories": get_categories()
    })


def search(request):
    query = request.GET.get("q", None)
    if not query:
        return render(request, "frontend/search.html", {
            "tab": "search",
            "query": "",
            "projects": [],
            "categories": get_categories()
        })

    projects = Project.objects.get_queryset()
    projects = projects.filter(
        reduce(or_, (
            reduce(or_, (
                Q(**{"%s__icontains" % c: word})
                for c in ("name", "identifier", "description")
            ))
        for word in query.split())
    ))

    return render(request, "frontend/search.html", {
        "tab": "search",
        "query": query,
        "projects": projects,
        "categories": get_categories()
    })