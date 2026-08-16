from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()


class Notification(models.Model):
    class notificationType(models.TextChoices):
        Invitation = (
            "INVITATION",
            _("Invitation"),
        )  # recieve invitation to join project or reject invitation
        Info = "INFO", _("Info")  # general information about project or system
        Sales = "SALES", _("Sales")  # Sales - new sale
        Expense = "EXPENSE", _("Expense")  # Expense - new expense
        Report = "REPORT", _("Report")  # Report - new report

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_notification"
    )

    title = models.CharField(_("Title"), max_length=200)
    message = models.TextField(_("Message"))
    type = models.CharField(
        _("Type"),
        max_length=50,
        choices=notificationType.choices,
        default=notificationType.Info,
    )
    read = models.BooleanField(_("Read"), default=False)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    actionUrl = models.URLField(_("Action URL"), blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.type} - {'Read' if self.read else 'Unread'}"
