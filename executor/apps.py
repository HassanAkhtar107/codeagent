from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ExecutorConfig(AppConfig):
    name = "executor"
    verbose_name = _("Code Executor")

    def ready(self):
        pass
