import csv
from datetime import datetime
import sys

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.contrib.auth.models import User, Group
from django.utils import timezone

from sourcedive.settings import TEST_ENV
from sources.models import Dive, Expertise, Industry, Organization, Person


def create_person(data_dict, m2m_dict):
    """
    Create a Person in the system as part of the import process. Works for
    both import file types.
    """
    email_address = data_dict['email_address']
    # check if the person already exists:
    try:
        exists = Person.objects.get(email_address=email_address)
        create_message = f'Skipping: Person with {email_address} already exists.'
    except:
        # try:
        person_obj, person_created = Person.objects.update_or_create(**data_dict)
        # populate MANY-TO-MANY fields
        if m2m_dict:
            # created_by (FK)
            created_by_email = m2m_dict['created_by']
            user, user_created = User.objects.get_or_create(email=created_by_email)
            person_qs = Person.objects.filter(email_address=person_obj.email_address)
            person_qs.update(created_by=user)
            # expertise (M2M)
            expertise_values = m2m_dict['expertise']
            if expertise_values:
                values_list = [value.strip() for value in expertise_values.split(',')]
                for value in values_list:
                    expertise_obj, expertise_created = Expertise.objects.get_or_create(name=value)
                    person_obj.expertise.add(expertise_obj)
            # industry (M2M)
            industry_values = m2m_dict['industries']
            if industry_values:
                values_list = [value.strip() for value in industry_values.split(',')]
                for value in values_list:
                    industry_obj, industry_created = Industry.objects.get_or_create(name=value)
                    person_obj.industries.add(industry_obj)
            # organization (M2M)
            organization_values = m2m_dict['organization']
            if organization_values:
                values_list = [value.strip() for value in organization_values.split(',')]
                for value in values_list:
                    organization_obj, organization_created = Organization.objects.get_or_create(name=value)
                    person_obj.organization.add(organization_obj)
            # owned by (M2M)
            owned_by_values = m2m_dict['owned_by']
            if owned_by_values:
                values_list = [value.strip() for value in owned_by_values.split(',')]
                for value in values_list:
                    dive_obj, dive_created = Dive.objects.get_or_create(name=value)
                    person_obj.owned_by.add(dive_obj)
            # let us know how it went
            if person_created:
                create_message = f'Success: {person_obj}'
            else:
                create_message = f'Failed: {person_obj}'
        # except Exception as e:
        #     create_message = f'Error for {email_address}: {e}\n'
    print(create_message)
    # except:
    #     failed_rows.append(counter)
    # try:
    #     obj, created = Person.objects.create(**csv_to_model)
    # except:
    #     message = 'Create person' + str(sys.exc_info())
    #     print(message)


def import_csv(csv_file):
    ## start
    start_time = datetime.now()
    start_message = '\nStarted import:\t {}\n'.format(start_time)
    message = start_message
    print(message)

    # row_count = sum(1 for row in csv_reader)
    # message = 'Number of rows: {}\t'.format(row_count)
    # print(message)
    counter = 0
    failed_rows = 0

    # TODO: make this less hacky/kludgy and improve error handling + reporting
    if 'latest_export.csv' in csv_file:
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                counter += 1
                row_as_dict = dict(row)
                now = str(timezone.now())
                # we never want to use the old related user id bc a new one needs to be made
                row_as_dict.pop('related_user')
                # adjust the following as needed before import
                if row_as_dict['created'] == '':
                    row_as_dict['created'] = now
                if row_as_dict['updated'] == '':
                    row_as_dict['updated'] = now
                if row_as_dict['timezone'] == '':
                    row_as_dict.pop('timezone')
                if row_as_dict['rating'] == '':
                    row_as_dict.pop('rating')
                if row_as_dict['rating_avg'] == '':
                    row_as_dict.pop('rating_avg')
                try:
                    create_person(row_as_dict)
                except:
                    email_address = row_as_dict['email_address']
                    message = 'Failed to create a person for {}. \nException: {}'.format(
                            email_address,
                            str(sys.exc_info())
                        )
                    print(message)
    else:
        with open(csv_file) as file:
            csv_reader = csv.DictReader(file)
            ## loops thru the rows
            for counter, row in enumerate(csv_reader):
                ## special fields
                status = 'added_by_admin'
                email_address = row['email_address']
                timezone =row['timezone']
                if isinstance(timezone, int):
                    timezone_value = timezone
                else:
                    timezone_value = None

                ## map fields from csv to Person model
                csv_to_model_dict = {
                    # 'role': row['role'],
                    'privacy_level': row['privacy_level'],
                    'name': row['name'],
                    'type_of_expert': row['type_of_expert'],
                    # 'expertise': expertise_id, ## m2m field
                    'title': row['title'],
                    # 'organization': organization_id, ## m2m field
                    # 'industries': industry_id, ## m2mfield
                    'city': row['city'],
                    'state': row['state'],
                    'country': row['country'],
                    'phone_number_primary': row['phone_number_primary'],
                    'phone_number_secondary': row['phone_number_secondary'],
                    'twitter': row['twitter'],
                    # 'notes': row['notes'],
                    # 'website': row['website'],
                    'prefix': row['prefix'],
                    # 'language': 'English', ## m2mfield
                    # 'approved_by_admin': True,
                    # 'approved_by_user': True,
                    'entry_method': 'import',
                    'entry_type': 'automated',
                    'email_address': email_address,
                    # 'status': status,
                    'timezone': timezone_value,
                }
                m2m_dict = {
                    'created_by': row['created_by'],
                    'expertise': row['expertise'],
                    'industries': row['industries'],
                    'organization': row['organization'],
                    'owned_by': row['owned_by'],
                }
                create_person(csv_to_model_dict, m2m_dict)
        # message = '\nThe following rows failed: \n\n {}'.format(failed_rows)
        # print(message)

    ## end
    end_time = datetime.now()
    end_message = '\nFinished import:\t {} \n'.format(end_time)
    import_length = end_time - start_time
    message = end_message
    print(message)
    message = 'Import length:\t\t {} \n'.format(import_length)
    print(message)

    # message = 'Imported {} rows'.format(counter)
    # print(message)
    # message = '{} rows failed'.format(failed_rows)
    # print(message)


class Command(BaseCommand):
    help = 'Import sources from a csv file.'

    def add_arguments(self, parser):
        ## required
        parser.add_argument('file', 
            help='Specify the CSV file.'
        )

    def handle(self, *args, **options):
        ## unpack args
        csv_file = options['file']

        ## call the function
        import_csv(csv_file)

