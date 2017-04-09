import json
from _sha256 import sha256
from datetime import datetime
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods, logger
import requests
from challenges.forms import ChallengeForm
from challenges.models import Challenge, CTFSettings, TeamFlagChall
from news.forms import NewsForm
from news.models import News
from user_manager.models import TeamProfile

logger.setLevel(0)


def create_or_update_challenge(request, chall_form, creating):
    if chall_form.is_valid():
        chall = chall_form.save(commit=False)
        if creating:
            chall_slug = slugify(chall.name)
            nb_same_slug = Challenge.objects.filter(slug=chall_slug).count()
            if nb_same_slug != 0:
                chall_slug += '-' + str(nb_same_slug)
            chall.slug = chall_slug
            messages.add_message(request, messages.SUCCESS, "Challenge created. Thanks for your contribution.")
        else:
            messages.add_message(request, messages.SUCCESS, "Challenge updated. Thanks for your contribution.")
        chall.flag = sha256(chall.flag.encode('utf-8')).hexdigest()
        chall.save()
        return redirect(reverse('challenges:admin'))
    return None


@staff_member_required
@csrf_protect
@require_http_methods(["GET", "POST"])
@never_cache
def add_challenge(request: HttpRequest) -> HttpResponse:
    creating = True
    if request.method == 'POST':
        challenge_form = ChallengeForm(request.POST, request.FILES)
        response = create_or_update_challenge(request, challenge_form, creating)
        if response is not None:
            return response
    else:
        challenge_form = ChallengeForm()
    return render(request, 'challenges/add.html', locals())


@require_http_methods(["GET"])
def list_challenges(request: HttpRequest) -> HttpResponse:
    ctf_settings = CTFSettings.objects.first()
    if ctf_settings.has_been_started:
        challenges = Challenge.objects.all().order_by('nb_points')
        for c in challenges:
            c.nb_of_validations = len(c.flaggers.filter(team__is_staff=False))
    categories = Challenge.CATEGORY_CHOICES

    try:
        r = requests.get(ctf_settings.url_challenges_state)
        challenges_states = r.json()
        logger.info(challenges_states)
    except Exception as e:
        challenges_states = {}
        logger.error(str(e))

    return render(request, 'challenges/list.html', locals())


@never_cache
@require_http_methods(["GET"])
def get_validated_challenges(request):
    challs_validated = []
    if request.user.is_authenticated:
        challs_validated = [c.id for c in request.user.teamprofile.validated_challenges.all()]
    return JsonResponse({"challs_validated": challs_validated})


@csrf_protect
@never_cache
@require_http_methods(["POST"])
def validate(request: HttpRequest, chall_id: int) -> JsonResponse:
    team = request.user
    if not team.is_authenticated():
        return JsonResponse({"message": "You should login to validate your challenges", "error": True})
    team_profile = team.teamprofile
    error = True
    message = "An error occurred while validating your flag. Please be sure to fill all the fields."
    ctf_settings = CTFSettings.objects.first()
    if not ctf_settings.has_been_started and not request.user.is_staff:
        message = "You can't validate a challenge now, the CTF is not running. Please contact us for any question!"
    else:
        if team.is_staff:
            challenge = get_object_or_404(Challenge.all_objects, id=chall_id)
        else:
            challenge = get_object_or_404(Challenge.objects, id=chall_id)
        flag = request.POST.get("flag")
        if flag:
            flag_sha256 = sha256(flag.encode('utf-8')).hexdigest()
            if flag_sha256 == challenge.flag:
                if TeamFlagChall.objects.filter(flagger=team_profile, chall=challenge).count() > 0:
                    message = "This is indeed the correct flag. But your team already flagged this challenge."
                else:
                    new_team_flagger = TeamFlagChall(flagger=team_profile, chall=challenge)
                    team_profile.date_last_validation = datetime.now()
                    try:
                        new_team_flagger.save()  # fail if not unique together
                        team_profile.save()
                        message = "That's correct, congratulations ! You won " + str(challenge.nb_points) + "pts !"
                        error = False
                    except Exception as e:
                        logger.error("An error occurred while trying to flag a chall: " + str(e))
            else:
                with open("/srv/web/flags", "a") as f:
                    f.write("Team '" + team.username + "' tried : '" + flag + "'\n")
                message = "Sorry it's not the correct flag. Try harder."
    return JsonResponse({"message": message, "error": error})


@staff_member_required()
@csrf_protect
@never_cache
@require_http_methods(["POST", "GET"])
def update_challenge(request: HttpRequest, slug: str) -> HttpResponse:
    challenge = get_object_or_404(Challenge.all_objects, slug=slug)
    creating = False
    if request.method == 'POST':
        challenge_form = ChallengeForm(request.POST, request.FILES, instance=challenge)
        response = create_or_update_challenge(request, challenge_form, creating)
        if response is not None:
            return response
    else:
        challenge.flag = ''
        challenge_form = ChallengeForm(instance=challenge)
    return render(request, 'challenges/add.html', locals())


@staff_member_required
@csrf_protect
@never_cache
@require_http_methods(["POST"])
def delete_challenge(request, slug):
    if request.method == "POST":
        challenge = get_object_or_404(Challenge.all_objects, slug=slug)
        challenge.delete()
        messages.add_message(request, messages.SUCCESS, "The challenge has been deleted.")
    return redirect(reverse('challenges:admin'))


def get_all_teams(ctf_settings: CTFSettings) -> [User]:
    if ctf_settings.should_use_saved_global_scoreboard:
        global_scoreboard_saved = json.loads(ctf_settings.global_scoreboard_saved)
        return User.objects.filter(pk__in=list(global_scoreboard_saved))
    else:
        return User.objects.filter(is_active=True, is_staff=False, teamprofile__isnull=False)


def get_local_teams(ctf_settings: CTFSettings, all_teams: [User]) -> [User]:
    if ctf_settings.should_use_saved_local_scoreboard:
        local_scoreboard_saved = json.loads(ctf_settings.local_scoreboard_saved)
        return User.objects.filter(pk__in=list(local_scoreboard_saved))
    else:
        return list(filter(lambda t: t.teamprofile.on_site, all_teams))


def get_global_validated_challs(ctf_settings: CTFSettings, team: User) -> ([Challenge], int):
    if ctf_settings.should_use_saved_global_scoreboard:
        global_scoreboard_saved = json.loads(ctf_settings.global_scoreboard_saved)
        pk_validated_challs, bugbounty_points = global_scoreboard_saved.get(str(team.pk), ([], 0))
        return Challenge.objects.filter(pk__in=pk_validated_challs), bugbounty_points
    else:
        return team.teamprofile.validated_challenges.all(), team.teamprofile.bug_bounty_points


def get_onsite_validated_challs(ctf_settings: CTFSettings, team: User) -> ([Challenge], int):
    if ctf_settings.should_use_saved_local_scoreboard:
        local_scoreboard_saved = json.loads(ctf_settings.local_scoreboard_saved)
        pk_validated_challs, bugbounty_points = local_scoreboard_saved.get(str(team.pk), ([], 0))
        return Challenge.objects.filter(pk__in=pk_validated_challs), bugbounty_points
    else:
        return team.teamprofile.validated_challenges.all(), team.teamprofile.bug_bounty_points


def get_scoreboards(challenges):
    ctf_settings = CTFSettings.objects.first()
    all_teams = get_all_teams(ctf_settings)
    teams_onsite = get_local_teams(ctf_settings, all_teams)
    for i in range(len(all_teams)):
        validated_challs, bugbounty_points = get_global_validated_challs(ctf_settings, all_teams[i])
        all_teams[i].teamprofile.saved_bugbounty_points = bugbounty_points
        all_teams[i].teamprofile.score = sum(map(lambda c: c.nb_points, validated_challs)) + bugbounty_points
        all_teams[i].teamprofile.challenges_state = [(c in validated_challs) for c in challenges]
    for i in range(len(teams_onsite)):
        validated_challs, bugbounty_points = get_onsite_validated_challs(ctf_settings, teams_onsite[i])
        all_teams[i].teamprofile.saved_bugbounty_points = bugbounty_points
        teams_onsite[i].teamprofile.score = sum(map(lambda c: c.nb_points, validated_challs)) + bugbounty_points
        teams_onsite[i].teamprofile.challenges_state = [(c in validated_challs) for c in challenges]

    all_teams = sorted(all_teams, key=lambda t: (-t.teamprofile.score, t.teamprofile.date_last_validation))
    teams_onsite = sorted(teams_onsite, key=lambda t: (-t.teamprofile.score, t.teamprofile.date_last_validation))
    return all_teams, teams_onsite


@require_http_methods(["GET"])
def scoreboard(request):
    ctf_settings = CTFSettings.objects.first()
    challenges = []
    ctf_has_been_started = ctf_settings.has_been_started
    if ctf_has_been_started:
        challenges = Challenge.objects.all().order_by('nb_points', 'category')
    all_teams, teams_onsite = get_scoreboards(challenges)
    return render(request, 'challenges/scoreboard.html', locals())


@staff_member_required
@require_http_methods(["GET"])
def admin(request):
    ctf_settings = CTFSettings.objects.first()
    ctf_state = ctf_settings.get_state_display()
    ctf_has_been_started = ctf_settings.has_been_started or request.user.is_staff

    challenges = Challenge.all_objects.all().order_by('nb_points')
    for c in challenges:
        c.nb_of_validations = len(c.flaggers.filter(team__is_staff=False))
    categories = Challenge.CATEGORY_CHOICES
    challs_validated = request.user.teamprofile.validated_challenges

    try:
        r = requests.get(ctf_settings.url_challenges_state)
        challenges_states = r.json()
        logger.info(challenges_states)
    except Exception as e:
        challenges_states = {}
        logger.error(str(e))

    news = News.objects.all().order_by("-updated_date")
    if request.user.is_staff:
        news_form = NewsForm()

    return render(request, 'challenges/admin.html', locals())


def change_ctf_state_to(state):
    ctf_settings = CTFSettings.objects.first()
    ctf_settings.state = state
    ctf_settings.save()


def save_scoreboards_state_and_change_ctf_state_to(state, update_local_too=True):
    ctf_settings = CTFSettings.objects.first()
    challenges = Challenge.objects.all().order_by('nb_points', 'category')
    global_scoreboard, local_scoreboard = get_scoreboards(challenges)
    ctf_settings.global_scoreboard_saved = json.dumps(
        {team.pk: ([i.pk for i in team.teamprofile.validated_challenges.all()], team.teamprofile.bug_bounty_points) for
         team in global_scoreboard})
    if update_local_too:
        ctf_settings.local_scoreboard_saved = json.dumps(
            {team.pk: ([i.pk for i in team.teamprofile.validated_challenges.all()], team.teamprofile.bug_bounty_points)
             for team in local_scoreboard})
    ctf_settings.state = state
    ctf_settings.save()


def post_news(text):
    news = News(text=text)
    try:
        news.save()
        for t in TeamProfile.objects.all():
            t.nb_unread_news += 1
            t.save()
    except Exception as e:
        logger.error("Error adding news: " + str(e))


@staff_member_required
@never_cache
@csrf_protect
@require_http_methods(["POST"])
def ctf_not_started(request):
    change_ctf_state_to(CTFSettings.NOT_STARTED)
    messages.add_message(request, messages.SUCCESS, "CTF is not started")
    return redirect(reverse('challenges:admin'))


@staff_member_required
@never_cache
@csrf_protect
@require_http_methods(["POST"])
def start_ctf(request):
    change_ctf_state_to(CTFSettings.GLOBAL_START)
    post_news('The CTF has officially started! Let\'s hack ;). Please see the home page to read the rules and see '
              'when the CTF ends.')
    messages.add_message(request, messages.SUCCESS, "CTF has started!")
    return redirect(reverse('challenges:admin'))


@staff_member_required
@never_cache
@csrf_protect
@require_http_methods(["POST"])
def freeze_local_scoreboard(request):
    save_scoreboards_state_and_change_ctf_state_to(CTFSettings.ON_SITE_HIDDEN)
    post_news('The scoreboard is now frozen until the CTF on-site is finished. You can still submit flags but the '
              'evolution of the scoreboard is hidden until the end of the on-site competition. Let the suspense build '
              'up! (See the home page to know when the on-site CTF ends)')
    messages.add_message(request, messages.SUCCESS, "Local scoreboard frozen")
    return redirect(reverse('challenges:admin'))


@staff_member_required
@never_cache
@csrf_protect
@require_http_methods(["POST"])
def stop_local_scoreboard(request):
    save_scoreboards_state_and_change_ctf_state_to(CTFSettings.ON_SITE_END)
    post_news('The on-site CTF is now finished! Congratulations to the participants :). Don\'t worry, you can still '
              'play online (cf home page). And we will keep adding new challenges.')
    messages.add_message(request, messages.SUCCESS, "Local competition stopped")
    return redirect(reverse('challenges:admin'))


@staff_member_required
@never_cache
@csrf_protect
@require_http_methods(["POST"])
def freeze_global_scoreboard(request):
    save_scoreboards_state_and_change_ctf_state_to(CTFSettings.ONLINE_HIDDEN, False)
    post_news('The scoreboard is now frozen until the CTF is finished. You can still submit flags but the '
              'evolution of the scoreboard is hidden until the end of the on-site competition. Let the suspense build '
              'up! (See the home page to know when the on-site CTF ends)')
    messages.add_message(request, messages.SUCCESS, "Global scoreboard frozen")
    return redirect(reverse('challenges:admin'))


@staff_member_required
@never_cache
@csrf_protect
@require_http_methods(["POST"])
def end_ctf(request):
    save_scoreboards_state_and_change_ctf_state_to(CTFSettings.ONLINE_END, False)
    post_news('The CTF is now finished! Congratulations to the participants :). Thanks a lot, it was awesome!')
    messages.add_message(request, messages.SUCCESS, "CTF has ended")
    return redirect(reverse('challenges:admin'))
