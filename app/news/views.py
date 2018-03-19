from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods, logger
from news.forms import NewsForm
from news.models import News

from user_manager.models import TeamProfile


@require_http_methods(["GET"])
def news(request: HttpRequest) -> HttpResponse:
    news = News.objects.all().order_by("-updated_date")
    return render(request, 'news/list.html', locals())


@csrf_protect
@never_cache
@require_http_methods(["POST"])
def empty_news(request):
    if request.user.is_authenticated and request.user.teamprofile:
        tp = request.user.teamprofile
        tp.nb_unread_news = 0
        tp.save()
    return JsonResponse({"error": False})


##################
### Admin actions
##################

@staff_member_required
@never_cache
@csrf_protect
@require_http_methods(["POST"])
def add(request):
    news_form = NewsForm(request.POST)
    if news_form.is_valid():
        try:
            news_form.save()
            for t in TeamProfile.objects.all():
                t.nb_unread_news += 1
                t.save()
            messages.add_message(request, messages.SUCCESS, "The news has been posted.")
        except Exception:
            logger.exception("Error adding news:")
    return redirect(reverse("news:list"))


@staff_member_required
@never_cache
@csrf_protect
@require_http_methods(["POST"])
def delete(request, id_news):
    news = get_object_or_404(News.objects, id=id_news)
    try:
        news.delete()
        messages.add_message(request, messages.SUCCESS, "The news has been deleted.")
    except Exception:
        logger.exception("Error deleting news: ")
    return redirect(reverse("news:list"))


@staff_member_required
@never_cache
@csrf_protect
@require_http_methods(["GET", "POST"])
def modify(request, id_news):
    news = get_object_or_404(News.objects, id=id_news)
    if request.method == "POST":
        news_form = NewsForm(request.POST, instance=news)
        if news_form.is_valid():
            try:
                news_form.save()
                for t in TeamProfile.objects.all():
                    t.nb_unread_news += 1
                    t.save()
                messages.add_message(request, messages.SUCCESS, "The news has been updated.")
            except Exception:
                logger.exception("Error adding news: ")
                messages.add_message(request, messages.ERROR, "Error while updating the news.")
            return redirect(reverse("news:list"))
    elif request.method == "GET":
        news_form = NewsForm(instance=news)
    return render(request, "news/modify.html", locals())
