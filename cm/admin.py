from django.contrib import admin
from noc.cm.models import ObjectCategory,Config,DNS,PrefixList,RPSL

class ObjectCategoryAdmin(admin.ModelAdmin):
    list_display=["name","description"]
    
class ConfigAdmin(admin.ModelAdmin):
    list_display=["repo_path","activator","profile_name","scheme","address","last_modified","pull_every","last_pull","next_pull","view_link"]
    list_filter=["categories","profile_name","activator"]
    search_fields=["repo_path","address"]

class DNSAdmin(admin.ModelAdmin):
    list_display=["repo_path","last_modified","view_link"]
    list_filter=["categories"]
    search_fields=["repo_path"]
    
class PrefixListAdmin(admin.ModelAdmin):
    list_display=["repo_path","last_modified","view_link"]
    list_filter=["categories"]
    search_fields=["repo_path"]
    
class RPSLAdmin(admin.ModelAdmin):
    list_display=["repo_path","last_modified","view_link"]
    list_filter=["categories"]
    search_fields=["repo_path"]

admin.site.register(ObjectCategory, ObjectCategoryAdmin)
admin.site.register(Config,         ConfigAdmin)
admin.site.register(DNS,            DNSAdmin)
admin.site.register(PrefixList,     PrefixListAdmin)
admin.site.register(RPSL,           RPSLAdmin)

