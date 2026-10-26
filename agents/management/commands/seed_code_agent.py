from django.core.management.base import BaseCommand
from agents.models import Agent


SEED_AGENTS = [
    {
        "name": "Code Writer",
        "description": "Expert at writing clean, production-ready code in any language.",
        "provider": "openai",
        "model_name": "gpt-4o",
        "system_prompt": (
            "You are an expert software engineer. Write clean, well-documented, "
            "production-ready code. Follow best practices and include comments where necessary."
        ),
        "temperature": 0.3,
        "max_tokens": 8192,
        "is_public": True,
    },
    {
        "name": "Code Reviewer",
        "description": "Reviews code for bugs, security issues, and performance improvements.",
        "provider": "anthropic",
        "model_name": "claude-3-5-sonnet-20241022",
        "system_prompt": (
            "You are an expert code reviewer. Analyze code for bugs, security vulnerabilities, "
            "performance bottlenecks, and style issues. Provide actionable feedback with examples."
        ),
        "temperature": 0.2,
        "max_tokens": 4096,
        "is_public": True,
    },
    {
        "name": "Debugger",
        "description": "Specializes in finding and fixing bugs quickly.",
        "provider": "openai",
        "model_name": "gpt-4o",
        "system_prompt": (
            "You are an expert debugger. When given buggy code, identify the root cause, "
            "explain why it fails, and provide a corrected version with explanation."
        ),
        "temperature": 0.1,
        "max_tokens": 4096,
        "is_public": True,
    },
    {
        "name": "Architect",
        "description": "Designs system architecture, APIs, and database schemas.",
        "provider": "anthropic",
        "model_name": "claude-3-5-sonnet-20241022",
        "system_prompt": (
            "You are a senior software architect. Design scalable systems, APIs, and database schemas. "
            "Consider trade-offs between different approaches and justify your design decisions."
        ),
        "temperature": 0.5,
        "max_tokens": 8192,
        "is_public": True,
    },
    {
        "name": "Documentation Writer",
        "description": "Writes comprehensive technical documentation and README files.",
        "provider": "gemini",
        "model_name": "gemini-1.5-pro",
        "system_prompt": (
            "You are a technical writer. Write clear, comprehensive documentation "
            "including README files, API docs, inline comments, and usage examples."
        ),
        "temperature": 0.7,
        "max_tokens": 4096,
        "is_public": True,
    },
]


class Command(BaseCommand):
    help = "Seed the Code Agent platform with demo agent configurations."

    def handle(self, *args, **options):
        self.stdout.write("Seeding demo agents...")
        created_count = 0

        for agent_data in SEED_AGENTS:
            agent, created = Agent.objects.get_or_create(
                name=agent_data["name"],
                defaults=agent_data,
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"  ✓ Created agent: {agent.name}"))
            else:
                self.stdout.write(f"  - Already exists: {agent.name}")

        self.stdout.write(
            self.style.SUCCESS(f"\nDone! {created_count} new agents created.")
        )
