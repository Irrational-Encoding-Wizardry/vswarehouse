from django.contrib import admin
from warehouse.models import Project, Release


class ReleaseInline(admin.TabularInline):
    model = Release


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    inlines = [ReleaseInline]
    list_filter = ["category", "type", "using_pip", "from_vsutil"]
    search_fields = ["identifier", "name", "description"]
    list_display = ["name", "identifier", "description"]

