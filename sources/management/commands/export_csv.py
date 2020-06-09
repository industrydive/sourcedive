import csv
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.contrib.auth.models import User
# from django.http import HttpResponse

from sources.models import Person, Dive


def export_sources(user_id):
    """
    Generate a list and provide a csv. Sources included are based on sources:
        - this user created
        - another user set exportable by a Dive this user is affiliated with
        - another user set exportable by this user
    """
    user = User.objects.get(id=user_id)
    sources = Person.objects.all()

    # created by this user (all privacy levels)
    sources_created_by_user = sources.filter(created_by=user)
    # exportable by Dive (only public for now)
    try:
        user_dive = Dive.objects.get(users=user)
        sources_exportable_by_dive = sources.filter(
            privacy_level='public',
            exportable_by=user_dive
        )
        # combine the querysets
        sources_to_export = sources_created_by_user | sources_exportable_by_dive
    except:
        sources_to_export = sources_created_by_user
    # exportable by another user; TODO after this field is added
    # sources_exportable_by_user = sources.filter()

    # create the csv
    username = user.get_username()
    date = datetime.today().strftime('%Y%m%d')
    filename = f'sources-{username}-{date}.csv'

    with open(filename, mode='w') as csv_file:
        fields = ['city', 'country', 'email_address', 'expertise', 'exportable_by', 'gatekeeper', 'import_notes', 'industries', 'linkedin','name', 'organization', 'phone_number_primary', 'phone_number_secondary', 'prefix', 'privacy_level', 'pronouns', 'skype', 'state','title', 'timezone', 'twitter', 'type_of_expert', 'website', 'created_by', 'created', 'updated']
        sources_writer = csv.DictWriter(csv_file, fieldnames=fields, delimiter=',', quotechar='"')

        sources_writer.writeheader()

        # must be so verbose in order to join the M2M fields values into strings
        for source in sources:
            expertise = ', '.join(
                [expertise.name for expertise in source.expertise.all()]
            )
            industries = ', '.join(
                [industry.name for industry in source.industries.all()]
            )
            organizations = ', '.join(
                [organization.name for organization in source.organization.all()]
            )

            row_dict = {
                'city': source.city,
                'country': source.country,
                'email_address': source.email_address,
                'expertise': expertise,
                'gatekeeper': source.gatekeeper,
                'import_notes': source.import_notes,
                'industries': industries,
                'linkedin': source.linkedin,
                'name': source.name,
                'organization': organizations,
                'phone_number_primary': source.phone_number_primary,
                'phone_number_secondary': source.phone_number_secondary,
                'prefix': source.prefix,
                'privacy_level': source.privacy_level,
                'pronouns': source.pronouns,
                'skype': source.skype,
                'state': source.state,
                'title': source.title,
                'timezone': source.timezone,
                'twitter': source.twitter,
                'type_of_expert': source.type_of_expert,
                'website': source.website,
                'created_by': source.created_by.username,
                'updated': source.updated,
            }
            sources_writer.writerow(row_dict)


class Command(BaseCommand):
    help = 'Export sources to a csv file.'

    def add_arguments(self, parser):
        # required arg
        parser.add_argument('user_id', 
            help='Specify the relevant user id.'
        )

    def handle(self, *args, **options):
        user_id = options['user_id']

        export_sources(user_id)

