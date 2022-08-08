from subprocess import call

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    command_list = [
        "black .",
        "isort .",
        "flake8 .",
        "mypy .",
    ]

    def handle(self, *args, **kwargs):
        for command in self.command_list:
            self.stdout.write(f"{command:-^79}")
            call(command, shell=True)
            self.stdout.write("_" * 79 + "\n\n")
