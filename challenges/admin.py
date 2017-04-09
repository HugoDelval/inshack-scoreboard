from django.contrib import admin

from challenges.models import Challenge, TeamFlagChall, CTFSettings

admin.site.register(Challenge)
admin.site.register(TeamFlagChall)
admin.site.register(CTFSettings)
