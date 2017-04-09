import os
from django.db import models
from django.utils.text import slugify

from user_manager.models import TeamProfile


class CTFSettings(models.Model):
    NOT_STARTED = "NST"
    GLOBAL_START = "STA"
    ON_SITE_HIDDEN = "OSH"
    ON_SITE_END = "OSE"
    ONLINE_HIDDEN = "OLH"
    ONLINE_END = "OLE"
    STATE_CHOICES = (
        (NOT_STARTED, 'Not started'),
        (GLOBAL_START, 'Globally started'),
        (ON_SITE_HIDDEN, 'On site scoreboard hidden'),
        (ON_SITE_END, 'On site end'),
        (ONLINE_HIDDEN, 'Online scoreboard hidden'),
        (ONLINE_END, 'Online end'),
    )

    state = models.CharField(max_length=3,
                             choices=STATE_CHOICES,
                             default=NOT_STARTED)

    local_scoreboard_saved = models.TextField(blank=True, null=True)
    global_scoreboard_saved = models.TextField(blank=True, null=True)
    url_challenges_state = models.URLField()

    @property
    def has_been_started(self):
        return self.state != self.NOT_STARTED

    @property
    def should_use_saved_local_scoreboard(self):
        return self.state in [self.ON_SITE_HIDDEN, self.ON_SITE_END, self.ONLINE_HIDDEN, self.ONLINE_END]

    @property
    def should_use_saved_global_scoreboard(self):
        return self.state in [self.ON_SITE_HIDDEN, self.ONLINE_HIDDEN, self.ONLINE_END]


class ChallengeManagerNoDisabled(models.Manager):
    def get_queryset(self):
        return super(ChallengeManagerNoDisabled, self).get_queryset().exclude(is_enabled=False)


class Challenge(models.Model):
    MISC = 'MIC'
    WEB = 'WEB'
    PPC = 'PPC'
    FORENSICS = 'FOR'
    REVERSE = 'REV'
    PWN = 'PWN'
    CRYPTO = 'CRY'
    CATEGORY_CHOICES = (
        (MISC, 'MISC'),
        (PPC, 'Programming'),
        (WEB, 'Web'),
        (FORENSICS, 'Forensics'),
        (REVERSE, 'Reverse'),
        (PWN, 'Pwn'),
        (CRYPTO, 'Crypto'),
    )

    # Number of points of the chall
    nb_points = models.IntegerField(default=50)
    # name of the chall
    name = models.CharField(max_length=50, unique=True)
    # slug of the chall, generated from the name (unique for URL)
    slug = models.SlugField(max_length=50, blank=True, unique=True)
    # chall's description, a fun story
    description = models.TextField()
    # chall's category
    category = models.CharField(max_length=3,
                                choices=CATEGORY_CHOICES,
                                default=WEB)
    # teams having solved the challenge (by date of solving)
    flaggers = models.ManyToManyField(TeamProfile, through='TeamFlagChall', blank=True,
                                      related_name='validated_challenges')
    # chall's flag
    flag = models.CharField(max_length=255)
    # is chall visible by everyone ?
    is_enabled = models.BooleanField(default=False)
    # file (or archive) of the chall
    chall_file = models.URLField(blank=True, null=True)

    # managers
    # except is_enabled=False
    objects = ChallengeManagerNoDisabled()
    # all challs
    all_objects = models.Manager()
    is_ovh_chall = models.BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.nb_of_validations = 0  # updated dynamically

    def __str__(self):
        return self.name


class TeamFlagChall(models.Model):
    flagger = models.ForeignKey(TeamProfile)
    chall = models.ForeignKey(Challenge)
    date_flagged = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date_flagged"]
        unique_together = (("flagger", "chall"),)

    def __str__(self):
        return str(self.flagger) + " flagged " + str(self.chall)
