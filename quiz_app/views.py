import json
import random
from json import JSONEncoder
from uuid import UUID

import pytz
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.timezone import datetime
from django.views.decorators.cache import cache_control
from verify_email.email_handler import send_verification_email

from .forms import QuizForm, SignUpForm
from .models import Quiz, QuizTakers, Response

# For setting the UUID field to string
# To pass that field to json object
old_default = JSONEncoder.default


def new_default(self, obj):
    if isinstance(obj, UUID):
        return str(obj)
    return old_default(self, obj)


JSONEncoder.default = new_default


def home(request):
    form = QuizForm(request.POST or None)
    if request.user.is_authenticated:
        form.fields.pop("email")
        form.fields.pop("password")
    context = {"quizForm": form}

    if request.method == "POST":
        key = request.POST.get("key", None)
        if not request.user.is_authenticated:
            user = authenticate(
                request,
                email=request.POST.get("email", ""),
                password=request.POST.get("password", ""),
            )
            if not user:
                messages.error(request, "Invalid Email Or Password")
                return render(request, "quiz_app/home.html", context)
            elif not user.is_active:
                messages.error(
                    request,
                    "Do You Want to send the verification email again?",
                    extra_tags="email_verification",
                )
                return render(request, "quiz_app/home.html", context)
            else:
                login(request, user)
                messages.success(request, "Successfully Logged In")
        if key:
            try:
                quiz = Quiz.objects.filter(key=key).first()
                if quiz:
                    if not quiz.has_started:
                        return redirect("quiz_upcoming", quiz_id=quiz.pk)
                    elif not quiz.has_ended:
                        return redirect("quiz_started", quiz_id=quiz.pk)
                    else:
                        return redirect("quiz_ended", quiz_id=quiz.pk)

                else:
                    messages.error(request, "No Quiz Found For Given ID")
                    return redirect("home")

            except ValueError:
                messages.error(request, "Invalid Id")
                return redirect("home")

    return render(request, "quiz_app/home.html", context)


context = {}


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def quiz(request, quiz_id):

    # global context
    # if context:
    #     print("Fast Checkout")
    #     return render(request, "quiz_app/quiz.html", context)

    # print("DB Load")

    quiz = get_object_or_404(Quiz, quiz_id=quiz_id)
    if not quiz.has_started:
        return redirect("quiz_upcoming", quiz_id=quiz_id)

    quizTaker = get_object_or_404(QuizTakers, quiz_id=quiz_id, user_id=request.user.pk)

    if quizTaker.has_ended:
        return redirect("quiz_result", quiz_id=quiz_id)

    if quiz.has_ended and not quizTaker.started:
        return redirect("quiz_ended", quiz_id=quiz_id)

    questions = []
    responses = []
    if quizTaker.extra:
        if quizTaker.started:
            quizTaker.suspicion_count += 1
            quizTaker.save()
            messages.warning(
                request,
                "Do not move away from the test or it will be marked suspicious.",
            )

            queryset = (
                quizTaker.response_set.select_related("question").all().order_by("pk")
            )
            # fetching questions 
            for response in queryset:
                questions.append(model_to_dict(response.question, exclude=["correct"]))
                responses.append(
                    model_to_dict(response, exclude=["id", "isCorrect", "marks"])
                )
        else:
            quizTaker.started = timezone.now()
            quizTaker.save()
            shuffledQuestions = quiz.question_set.all()[::1]
            random.shuffle(shuffledQuestions)

            responseList = []
            for question in shuffledQuestions:
                response = Response(quiztaker=quizTaker, question=question, answer="")
                responseList.append(response)
                questions.append(model_to_dict(question, exclude=["correct"]))
                responses.append(
                    model_to_dict(response, exclude=["id", "isCorrect", "marks"])
                )
            Response.objects.bulk_create(responseList, ignore_conflicts=True)
    else:
        return redirect("quiz_instructions", quiz_id=quiz_id)
    shuffle = quiz.isShuffle
    context = {
        "quiz": quiz,
        "questions": json.dumps(questions),
        "responses": json.dumps(responses),
        "shuffle": json.dumps(shuffle),
        "quizTaker": quizTaker,
    }
    return render(request, "quiz_app/quiz.html", context)


def quiz_view(request):
    return redirect("home")


def quiz_result(request, quiz_id):
    # global context
    # if context:
    #     print("Fast Checkout")
    #     return render(request, "quiz_app/quiz_result.html", context)

    # print("DB Load")

    quiz = get_object_or_404(Quiz, quiz_id=quiz_id)

    if not request.user.is_authenticated:
        return redirect("login")

    quizTaker = get_object_or_404(QuizTakers, quiz_id=quiz_id, user_id=request.user.pk)
    if quiz.has_ended and not quizTaker.started:
        return redirect("quiz_ended", quiz_id=quiz_id)
    if quiz.has_started and not quizTaker.has_ended:
        return redirect("quiz", quiz_id=quiz_id)
    queryset = (
        quizTaker.response_set.select_related("question").all().order_by("question_id")
    )

    context = {
        "quiz": quiz,
        "responses": queryset,
        "quizTaker": quizTaker,
    }

    return render(request, "quiz_app/quiz_result.html", context)


def quiz_upcoming(request, quiz_id):
    quiz = get_object_or_404(Quiz, quiz_id=quiz_id)
    try:
        quizTaker = QuizTakers.objects.get(quiz=quiz, user=request.user)
    except QuizTakers.DoesNotExist:
        messages.warning(request, "You are not authorized to access this test")
        return redirect("home")
    if quiz.has_ended and not quizTaker.started:
        return redirect("quiz_ended", quiz_id=quiz_id)
    if quizTaker.has_ended:
        return redirect("quiz_result", quiz_id=quiz_id)
    if quiz.has_started:
        return redirect("quiz_started", quiz_id=quiz_id)

    context = {"quiz": quiz}
    return render(request, "quiz_app/quiz_upcoming.html", context)


@login_required
def quiz_started(request, quiz_id):
    quiz = get_object_or_404(Quiz, quiz_id=quiz_id)
    try:
        quizTaker = QuizTakers.objects.get(quiz=quiz, user=request.user)
    except QuizTakers.DoesNotExist:
        messages.warning(request, "You are not authorized to access this test")
        return redirect("home")
    if not quiz.has_started:
        return redirect("quiz_upcoming", quiz_id=quiz_id)
    if quiz.has_ended and not quizTaker.started:
        return redirect("quiz_ended", quiz_id=quiz_id)
    if quizTaker.has_ended:
        return redirect("quiz_result", quiz_id=quiz_id)

    context = {"quiz": quiz}
    return render(request, "quiz_app/quiz_started.html", context)


def quiz_ended(request, quiz_id):
    quiz = get_object_or_404(Quiz, quiz_id=quiz_id)
    if not quiz.has_started:
        return redirect("quiz_upcoming", quiz_id=quiz_id)
    if not quiz.has_ended:
        return redirect("quiz_started", quiz_id=quiz_id)

    context = {"quiz": quiz}
    return render(request, "quiz_app/quiz_ended.html", context)


@login_required
def quiz_instructions(request, quiz_id):
    quiz = get_object_or_404(Quiz, quiz_id=quiz_id)
    try:
        quizTaker = QuizTakers.objects.get(quiz=quiz, user=request.user)
    except QuizTakers.DoesNotExist:
        messages.warning(request, "You are not authorized to access this test")
        return redirect("home")
    if not quiz.has_started:
        return redirect("quiz_upcoming", quiz_id=quiz_id)
    if quiz.has_ended and not quizTaker.started:
        return redirect("quiz_ended", quiz_id=quiz_id)
    if quizTaker.completed:
        return redirect("quiz_result", quiz_id=quiz_id)
    if quizTaker.started:
        return redirect("quiz", quiz_id=quiz_id)

    if request.method == "POST":
        return redirect("quiz", quiz_id=quiz_id)

    context = {"quiz": quiz}
    return render(request, "quiz_app/quiz_instructions.html", context)


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            send_verification_email(request, form)
            messages.info(
                request, "Please Confirm Your Email Address Before Continuing"
            )
            return redirect("login")
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})


@login_required
def profile(request):
    if request.user.is_staff:
        return redirect("staff_admin:index")
    quizTakers = QuizTakers.objects.filter(user=request.user).all()
    past = []
    current = []
    upcoming = []
    for quizTaker in quizTakers:
        if quizTaker.was_missed:
            past.append(quizTaker)
            continue
        if quizTaker.has_ended:
            past.append(quizTaker)
            continue
        if not quizTaker.quiz.has_started:
            upcoming.append(quizTaker)
            continue
        current.append(quizTaker)
    curDateTime = datetime.utcnow().replace(tzinfo=pytz.UTC)
    past.sort(key=lambda q: abs(curDateTime - q.quiz.start_date))
    current.sort(key=lambda q: abs(curDateTime - q.quiz.start_date))
    upcoming.sort(key=lambda q: abs(curDateTime - q.quiz.start_date))
    context = {
        "past": past,
        "current": current,
        "upcoming": upcoming,
    }
    return render(request, "registration/profile.html", context)

