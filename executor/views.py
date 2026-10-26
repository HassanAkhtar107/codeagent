import subprocess
import time
from django.conf import settings
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import CodeRun
from .serializers import CodeRunSerializer, CodeRunRequestSerializer

TIMEOUT = int(getattr(settings, "EXECUTOR_TIMEOUT_SECONDS", 30))
MAX_OUTPUT = int(getattr(settings, "EXECUTOR_MAX_OUTPUT_BYTES", 65536))

LANGUAGE_COMMANDS = {
    "python": ["python3", "-c"],
    "javascript": ["node", "-e"],
    "bash": ["bash", "-c"],
    "typescript": ["npx", "ts-node", "-e"],
}


class ExecutorViewSet(viewsets.GenericViewSet):
    """
    ViewSet for sandboxed code execution.
    POST /api/executor/run/ — run a code snippet.
    GET  /api/executor/ — list past runs for the authenticated user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """List the authenticated user's past code runs."""
        runs = CodeRun.objects.filter(user=request.user)[:50]
        serializer = CodeRunSerializer(runs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="run")
    def run(self, request):
        """
        Execute a code snippet in the sandbox.
        Returns stdout, stderr, exit_code, and duration_ms.
        """
        req_serializer = CodeRunRequestSerializer(data=request.data)
        if not req_serializer.is_valid():
            return Response(req_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        language = req_serializer.validated_data["language"]
        source_code = req_serializer.validated_data["source_code"]
        stdin_input = req_serializer.validated_data.get("stdin", "")

        cmd = LANGUAGE_COMMANDS.get(language)
        if not cmd:
            return Response(
                {"error": f"Language '{language}' is not supported for execution."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        code_run = CodeRun.objects.create(
            user=request.user,
            language=language,
            source_code=source_code,
            stdin=stdin_input,
            status="running",
        )

        try:
            start = time.monotonic()
            result = subprocess.run(
                cmd + [source_code],
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=TIMEOUT,
            )
            duration_ms = int((time.monotonic() - start) * 1000)

            stdout = result.stdout[:MAX_OUTPUT]
            stderr = result.stderr[:MAX_OUTPUT]
            exit_code = result.returncode
            run_status = "success" if exit_code == 0 else "error"

        except subprocess.TimeoutExpired:
            stdout, stderr, exit_code, duration_ms = "", "Execution timed out.", -1, TIMEOUT * 1000
            run_status = "timeout"
        except Exception as e:
            stdout, stderr, exit_code, duration_ms = "", str(e), -1, 0
            run_status = "error"

        code_run.stdout = stdout
        code_run.stderr = stderr
        code_run.exit_code = exit_code
        code_run.status = run_status
        code_run.duration_ms = duration_ms
        code_run.save(update_fields=["stdout", "stderr", "exit_code", "status", "duration_ms"])

        return Response(CodeRunSerializer(code_run).data, status=status.HTTP_200_OK)
