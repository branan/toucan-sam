from django.contrib import admin

from django.contrib.auth.models import Group
from core.models import Song, SetList, Gig


class SongAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'artist',
        'key',
        'singers',
        'run_time',
        'difficulty',
        'proposed',
        'active'
    )
    list_editable = (
        'singers',
        'run_time',
        'difficulty',
        'proposed',
        'active'
    )

    class Media:
        css = {
            "all": ("css/custom_admin.css",)
        }


admin.site.register(Song, SongAdmin)
admin.site.register(SetList)
admin.site.register(Gig)

# hide useless stuff...
admin.site.unregister(Group)