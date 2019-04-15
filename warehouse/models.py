import natsort
from django.db import models


class Project(models.Model):
    """
    The original project file.
    """
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=30)
    description = models.TextField()
    website = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    identifier = models.SlugField(max_length=100)
    dependencies = models.TextField()

    def sorted_releases(self):
        return list(reversed(natsort.natsorted(self.release_set.all(), key=lambda r: r.sanitized_pypa_version)))

    def latest_release(self):
        return self.sorted_releases()[0]

    class Meta:
        ordering = ["identifier"]


class Release(models.Model):
    pypa_version = models.CharField(max_length=60)
    release_version = models.CharField(max_length=60)

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    configuration = models.TextField()

    release_url = models.URLField(max_length=100)

    @property
    def sanitized_pypa_version(self):
        return self.pypa_version.split("+")[0]

    class Meta:
        ordering = ["pypa_version", "release_version"]


class Distribution(models.Model):
    pypa_platform_string = models.CharField(max_length=60)
    release = models.ForeignKey(Release, on_delete=models.CASCADE)
    file = models.FileField()
