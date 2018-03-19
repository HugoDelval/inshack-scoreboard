from django.contrib import admin

from user_manager.models import TeamProfile, Ssh


class TeamProfileAdmin(admin.ModelAdmin):
    readonly_fields = ('date_last_validation',)

admin.site.register(TeamProfile, TeamProfileAdmin)
admin.site.register(Ssh)
