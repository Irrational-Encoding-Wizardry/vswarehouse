from functools import reduce

import operator
import natsort
import json
from django.db import models
from django.db.models import Q


class Project(models.Model):
    """
    The original project file.
    """
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=30)
    description = models.TextField()

    website = models.CharField(max_length=255)
    github = models.CharField(max_length=255, blank=True)
    doom9 = models.CharField(max_length=255, blank=True)

    category = models.CharField(max_length=255)
    identifier = models.SlugField(max_length=100)
    dependencies = models.TextField()

    def sorted_releases(self):
        return list(reversed(natsort.natsorted(self.release_set.all(), key=lambda r: r.sanitized_pypa_version)))

    def latest_release(self):
        return self.sorted_releases()[0]

    def dependency_list(self):
        q = reduce(operator.or_, [Q(identifier__iexact=n) for n in json.loads(self.dependencies)], Q(pk=None))
        return Project.objects.filter(q)

    class Meta:
        ordering = ["identifier"]


class Release(models.Model):
    pypa_version = models.CharField(max_length=60)
    release_version = models.CharField(max_length=60)
    published = models.DateTimeField(null=True)

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    configuration = models.TextField()

    @property
    def sanitized_pypa_version(self):
        return self.pypa_version.split("+")[0]

    class Meta:
        ordering = ["pypa_version", "release_version"]


class Distribution(models.Model):
    platform = models.CharField(max_length=60)
    release = models.ForeignKey(Release, on_delete=models.CASCADE)
    url = models.URLField(max_length=255, blank=True)
