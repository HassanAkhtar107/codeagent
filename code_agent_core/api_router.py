from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from users.api.views import (
    UserViewSet,
    SignupViewSet,
    LoginViewSet,
    verifyOtpView,
    sendOtpView,
    resetEmailView,
    resetPasswordView,
    userProfileView,
    deleteUserView,
    AdminUserViewSet,
)
from agents.views import AgentViewSet, AgentSessionViewSet
from conversations.views import ConversationViewSet
from projects.views import ProjectViewSet, ProjectFileViewSet
from executor.views import ExecutorViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

# ── Auth & User Routes ────────────────────────────────────────────────────────
router.register("users", UserViewSet, basename="users")
router.register("signup", SignupViewSet, basename="signup")
router.register("login", LoginViewSet, basename="login")
router.register("verify-otp", verifyOtpView, basename="verify-otp")
router.register("send-otp", sendOtpView, basename="send-otp")
router.register("reset-email", resetEmailView, basename="reset-email")
router.register("reset-password", resetPasswordView, basename="reset-password")
router.register("user-profile", userProfileView, basename="user-profile")
router.register("delete-user", deleteUserView, basename="delete-user")
router.register("admin_users", AdminUserViewSet, basename="admin-users")

# ── Agent Routes ──────────────────────────────────────────────────────────────
# /api/agents/ — list, create, configure AI agents
router.register("agents", AgentViewSet, basename="agents")
# /api/agent-sessions/ — manage agent conversation sessions
router.register("agent-sessions", AgentSessionViewSet, basename="agent-sessions")

# ── Conversation Routes ───────────────────────────────────────────────────────
# /api/conversations/ — chat threads with agents
router.register("conversations", ConversationViewSet, basename="conversations")

# ── Project Routes ────────────────────────────────────────────────────────────
# /api/projects/ — coding project workspaces
router.register("projects", ProjectViewSet, basename="projects")
# /api/project-files/ — individual files within projects
router.register("project-files", ProjectFileViewSet, basename="project-files")

# ── Code Execution Routes ─────────────────────────────────────────────────────
# /api/executor/ — sandboxed code execution
router.register("executor", ExecutorViewSet, basename="executor")

app_name = "api"
urlpatterns = router.urls
