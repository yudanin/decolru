from django.contrib import admin
from .models import Msgs, Authors, Resources, AuthorsXResources, Langs, Tags, TagsXResources

admin.site.site_header = "Decolru Admin"
admin.site.site_title = "Admin"
admin.site.index_title = "Decolru"

class MsgsAdmin(admin.ModelAdmin):
    list_filter = ("lang_code", "page_id", "msg_name")
    list_display = ("lang_code", "msg_name", "description")


class LangsAdmin(admin.ModelAdmin):
    list_filter = ("lang_name", "lang_code_2", "lang_code_3")
    list_display = ("lang_name", "lang_code_2", "lang_code_3")


#class AuthorsInline(admin.TabularInline):
#    model = AuthorsXResources
#    extra = 1 # Number of empty forms to show for adding new related authors


class AuthorsXResourcesInline(admin.TabularInline):
    model = AuthorsXResources
    extra = 1

class TagsInline(admin.TabularInline):
    model = TagsXResources
    extra = 1 # Number of empty forms to show for adding new related authors


class ResourcesAdmin(admin.ModelAdmin):
    inlines = [AuthorsXResourcesInline, TagsInline]
    list_display = ['title', 'subtitle', 'resource_status', 'get_authors']
    actions = ['custom_remove_author']

    def get_authors(self, obj):
        return ', '.join([author.full_name() for author in obj.authored_resources.all()])
    get_authors.short_description = 'Authors'



admin.site.register(Msgs, MsgsAdmin)
admin.site.register(Authors)
admin.site.register(Resources, ResourcesAdmin)
admin.site.register(Langs, LangsAdmin)
admin.site.register(Tags)