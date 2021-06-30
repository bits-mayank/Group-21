from django.contrib.admin import AdminSite
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from .admin import AccountAdmin, Question_bank_admin, QuestionAdmin, QuizAdmin
from .forms import QuizAddFormStaff
from .models import Account, Question_bank, Quiz


class StaffAdminSite(AdminSite):
    """Add a new admin site for staff"""

    def home(*args, **kwargs):
        return HttpResponseRedirect(reverse("staff_admin:quiz_app_quiz_changelist"))

    site_header = "Staff Admin"
    site_title = "Staff Admin Portal"
    index_title = "Welcome"


class AccountAdmin(AccountAdmin):
    """Only allow staff to view the accounts"""

    def __init__(self, *args, **kwargs):
        super(AccountAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = None

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class QuestionAdmin(QuestionAdmin):
    """Allow the staff full access to questions"""

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def has_add_permission(self, request, obj=None):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff


class QuizAdmin(QuizAdmin):
    """Allow the staff full access to only their quizzes"""

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff and (
            (obj and obj.invigilator == request.user) or not obj
        )

    def has_add_permission(self, request):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff and (
            (obj and obj.invigilator == request.user) or not obj
        )

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff and (
            (obj and obj.invigilator == request.user) or not obj
        )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(invigilator=request.user)

    def save_model(self, request, obj, form, change):
        if not change and not obj.invigilator_id:
            obj.invigilator = request.user
        super(QuizAdmin, self).save_model(request, obj, form, change)

    form = QuizAddFormStaff
    inlines = [
        QuestionAdmin,
    ]


class Question_bank_admin(Question_bank_admin):
    """Allow the staff full access to question bank"""

    def __init__(self, *args, **kwargs):
        super(Question_bank_admin, self).__init__(*args, **kwargs)
        self.list_display_links = None

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff and obj and obj.invigilator == request.user

    def has_add_permission(self, request):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff


staff_admin_site = StaffAdminSite(name="staff_admin")
staff_admin_site.register(Account, AccountAdmin)
staff_admin_site.register(Quiz, QuizAdmin)
staff_admin_site.register(Question_bank, Question_bank_admin)
