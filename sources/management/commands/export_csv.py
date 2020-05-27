import csv
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.contrib.auth.models import User
# from django.http import HttpResponse

from sources.models import Person, Dive


def export_sources(current_user_id):
    """
    Generate a list and provide a csv. Sources included are based on sources:
        - this user created
        - another user set exportable by a Dive this user is affiliated with
        - another user set exportable by this user
    """
    current_user = User.objects.get(id=current_user_id)
    sources = Person.objects.all()

    # created by this user
    sources_created_by_user = sources.filter(created_by=current_user)
    # exoprtable by Dive
    current_user_dive = Dive.objects.get(users=current_user)
    sources_exportable_by_dive = sources.filter(exportable_by=current_user_dive)
    # exportable by another user; TODO after this field is added
    # sources_exportable_by_user = sources.filter()

    # combine those querysets
    sources_to_export = sources_created_by_user | sources_exportable_by_dive

    # create the csv
    username = current_user.get_username()
    date = datetime.today().strftime('%Y%m%d')
    filename = f'sources-{username}-{date}.csv'

    # response = HttpResponse(content_type='text/csv')
    # response['Content-Disposition'] = f'attachment; filename="{filename}"'

    with open(filename, mode='w') as csv_file:
        sources_writer = csv.writer(csv_file, delimiter=',', quotechar='"')
        # sources_writer = csv.writer(response)
        header = [field.name for field in Person._meta.fields]
        sources_writer.writerow(header)

        for source in sources_to_export.values_list():
            sources_writer.writerow(source)

    # return response


class Command(BaseCommand):
    help = 'Export sources to a csv file.'

    def add_arguments(self, parser):
        # required arg
        parser.add_argument('current_user_id', 
            help='Specify the current user.'
        )

    def handle(self, *args, **options):
        current_user_id = options['current_user_id']

        export_sources(current_user_id)

