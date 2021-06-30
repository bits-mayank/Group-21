from django.urls import path

from quiz_app import ajax, views
from quiz_app.staff_admin import staff_admin_site

urlpatterns = [
    path("", views.home, name="home"),
    path("quiz/<quiz_id>", views.quiz, name="quiz"),
    path("quiz/result/<quiz_id>/", views.quiz_result, name="quiz_result"),
    path("quiz/export/<quiz_id>/", ajax.export_result, name="export_result"),
    path("quiz/upcoming/<quiz_id>", views.quiz_upcoming, name="quiz_upcoming"),
    path("quiz/started/<quiz_id>", views.quiz_started, name="quiz_started"),
    path("quiz/ended/<quiz_id>", views.quiz_ended, name="quiz_ended"),
    path("quiz/inst/<quiz_id>", views.quiz_instructions, name="quiz_instructions"),
    path("quiz/inst/save_extra/", ajax.save_extra, name="save_extra"),
    path("quiz/response/save/", ajax.saveResponse, name="save_response"),
    path("quiz/completed/", ajax.completed, name="completed"),
    path("quiz/", views.quiz_view, name="quiz_view"),
    path("increase_suspicious/", ajax.increase_suspicious, name="increase_suspicious"),
    path(
        "send_verification_email/",
        ajax.send_verification_email,
        name="send_verification_email",
    ),
    path("signup/", views.signup, name="signup"),
    path("profile/", views.profile, name="profile"),
    path("staff/", staff_admin_site.home),
    path("staff/quiz_app/", staff_admin_site.home),
    path("staff/quiz_app/account/add/", staff_admin_site.home),
    path("staff/quiz_app/account/<pk>/change/", staff_admin_site.home),
    path("staff/quiz_app/account/<pk>/history/", staff_admin_site.home),
    path("staff/quiz_app/account/<pk>/delete/", staff_admin_site.home),
    # path("staff/quiz_app/question_bank/add/", staff_admin_site.home),
    # path("staff/quiz_app/question_bank/<pk>/change/", staff_admin_site.home),
    # path("staff/quiz_app/question_bank/<pk>/history/", staff_admin_site.home),
    # path("staff/quiz_app/question_bank/<pk>/delete/", staff_admin_site.home),
    path("staff/", staff_admin_site.urls),
]
