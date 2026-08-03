import os

from django.conf import settings
from django.core.management.base import BaseCommand

BASE_DIR = str(settings.BASE_DIR)


class Command(BaseCommand):
    help = "Clean apps code by sorting imports and check code style"

    def handle(self, *args, **options):
        commands = [
            f'flake8 --ignore=E501 "{BASE_DIR}\\mysite"',
            f'isort "{BASE_DIR}\\mysite"',
        ]
        for command in commands:
            print("-" * 100)
            print(f"Executando o comando: {command}")
            os.system(command)
            print("-" * 100, "\n")
