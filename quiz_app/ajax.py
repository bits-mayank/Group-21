from django.contrib import messages
from django.contrib.auth import authenticate
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.utils import timezone

from .excel import generate_result_as_excel
from .models import Question, Quiz, QuizTakers, Response


def saveResponse(request):
    if not request.user.is_authenticated:
        jsonResponse = JsonResponse({"error": "logged out"})
        jsonResponse.status_code = 403
        return jsonResponse
    if request.method == "POST":
        quizTaker = request.POST.get("quizTaker")
        question = request.POST.get("question")
        answer = request.POST.get("answer")
        question = Question.objects.filter(pk=question).first()
        response = Response.objects.filter(quiztaker_id=quizTaker, question=question)
        isCorrect = answer == question.correct
        if isCorrect:
            response.update(answer=answer, isCorrect=True, marks=question.marks)
        else:
            response.update(answer=answer, isCorrect=False, marks=0)

    return JsonResponse({"success": "Response successfully saved"})


def completed(request):
    if not request.user.is_authenticated:
        jsonResponse = JsonResponse({"error": "logged out"})
        jsonResponse.status_code = 403
        return jsonResponse
    if request.method == "POST":
        quizTaker = request.POST.get("quizTaker")
        quizTaker = QuizTakers.objects.get(pk=quizTaker)
        quizTaker.completed = timezone.now()
        quizTaker.save()
        context = {
            "name": request.user.full_name,
            "title": quizTaker.quiz.title,
            "started": quizTaker.started,
            "completed": quizTaker.completed,
        }
        msg_plain = render_to_string("email/test_confirmation.txt", context)
        msg_html = render_to_string("email/test_confirmation.html", context)
        email = EmailMultiAlternatives(
            "Test submitted successfully",
            msg_plain,
            "webmaster@localhost",
            [request.user.email],
        )
        email.attach_alternative(msg_html, "text/html")

        responses = (
            quizTaker.response_set.select_related("question")
            .all()
            .order_by("question_id")[::1]
        )
        filename = f"Result {request.user.full_name}.xlsx"
        output = generate_result_as_excel(request, quizTaker.quiz, quizTaker, responses)
        email.attach(
            filename, content=output.read(), mimetype="application/vnd.ms-excel"
        )
        email.send()
    return JsonResponse({"success": "Quiz successfully saved"})


def export_result(request, quiz_id):
    quiz = get_object_or_404(Quiz, quiz_id=quiz_id)
    quizTaker = get_object_or_404(QuizTakers, quiz_id=quiz_id, user_id=request.user.pk)
    if not quizTaker.has_ended:
        messages.info(request, "The Test has not been submitted yet.")
        return redirect("quiz", quiz_id=quiz.quiz_id)

    responses = (
        quizTaker.response_set.select_related("question")
        .all()
        .order_by("question_id")[::1]
    )

    filename = f"Result {request.user.full_name}.xlsx"
    response = HttpResponse(
        generate_result_as_excel(request, quiz, quizTaker, responses),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f"attachment; filename={filename}"

    return response


def send_verification_email(request, user=None):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, email=email, password=password)
    if user and user.verify_email(request):
        return JsonResponse({"success": "Quiz successfully saved"})
    else:
        jsonResponse = JsonResponse({"error": "Email Could Not Be Sent"})
        jsonResponse.status_code = 400


def save_extra(request):
    if request.method == "POST":
        extra = request.POST.get("extra")
        # extra = json.loads(extra)
        quiz_id = request.POST.get("quiz")
        quiz = get_object_or_404(Quiz, quiz_id=quiz_id)
        quizTaker = QuizTakers.objects.get(quiz=quiz, user=request.user)
        quizTaker.extra = extra
        quizTaker.save()
        return JsonResponse({"success": "Extra Information saved successfully"})
    jsonResponse = JsonResponse({"error": "Extra Information Could Not Be Saved"})
    jsonResponse.status_code = 400


def increase_suspicious(request):
    if request.method == "POST":
        user = request.user
        quiz_id = request.POST.get("quiz")
        try:
            quiz = get_object_or_404(Quiz, quiz_id=quiz_id)
            quizTaker = get_object_or_404(QuizTakers, quiz=quiz, user=user)
            quizTaker.suspicion_count += 1
            quizTaker.save()
            max_reached = quizTaker.suspicion_count >= quiz.max_suspicion_count
            return JsonResponse(
                {"success": "Suspicious increased", "max_reached": max_reached}
            )
        except:
            pass

    jsonResponse = JsonResponse({"error": "Suspicious couldn't be increased"})
    jsonResponse.status_code = 400

