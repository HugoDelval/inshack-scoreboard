import os

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.encoding import smart_text


class TeamProfile(models.Model):
    team = models.OneToOneField(User)
    # team logo
    avatar = models.URLField()

    # team origin
    comes_from = models.CharField(max_length=255, blank=True, null=True)

    # does the team wants to be contacted by partners?
    wants_to_be_contacted = models.BooleanField(default=False)

    # date of last validation
    date_last_validation = models.DateTimeField(default=timezone.now)

    # number of unread news
    nb_unread_news = models.PositiveIntegerField(default=0)

    # bug bounty points
    bug_bounty_points = models.PositiveIntegerField(default=0)

    # comment bug bounty
    comment_bug_bounty = models.TextField(blank=True, null=True)

    # validated challenges accessed by -> validated_challenges

    # is the team playing on site ?
    on_site = models.BooleanField(default=False)

    def __str__(self) -> str:
        return str(self.team)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.score = 0  # updated dynamically
        self.challenges_state = []  # updated dynamically
        self.saved_bugbounty_points = 0  # updated dynamically


class Ssh(models.Model):
    password = models.CharField(max_length=255)
    id_team_profile = models.IntegerField()
