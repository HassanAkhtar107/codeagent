from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ConversationsConfig(AppConfig):
    name = "conversations"
    verbose_name = _("Conversations")

    def ready(self):
        pass
