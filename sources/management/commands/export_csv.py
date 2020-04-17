import csv
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.contrib.auth.models import Dive, User

from sources.models import Person


def export_sources(current_user_id):
    """
    Generate a list and provide a csv. Sources included are based on sources:
        - this user created
        - another user set exportable by a Dive this user is affiliated with
        - another user set exportable by this user
    """
    user = User.objects.get(id=current_user_id)
    sources = Person.objects.all()

    # reverse lookup based on Dive
    # 
    # reverse lookup based on User
    # 


class Command(BaseCommand):
    help = 'Export sources to a csv file.'

    def add_arguments(self, parser):
        # required arg
        parser.add_argument('current_user_id', 
            help='Specify the current user.'
        )

    def handle(self, *args, **options):
        current_user_id = options['current_user_id']

        export_csv(current_user_id)

