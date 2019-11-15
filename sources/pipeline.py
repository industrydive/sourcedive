from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist

from sources.models import Expertise, Industry, Interaction, Organization, Source


def add_permissions_to_new_whitelisted_users(backend, user, response, *args, **kwargs):
    if not user.last_login:
        user.is_staff = True

        try:
            # get the group
            group = Group.objects.get(name='Newsroom user')
            # add the user to that group
            group.user_set.add(user)
            user.save()
        except ObjectDoesNotExist:
            pass
        # group, created_now = Group.objects.get_or_create(name='Newsroom user')
        # if created_now:
        #     a = ContentType.objects.get_for_model()
        #     b = etc etc 
        """     can we abstract this? e.g. use this for model names
                    from django.apps import apps

                    Model = apps.get_model('app_name', 'model_name')
                and then add them to an iterable so we can loop thru?
        """
        #     # add the permissions objects to the group
        #     permission = Permission.objects.create(
        #         codename='can_add_project',
        #         name='Can add project',
        #         content_type=ct
        #     )
        #     new_group.permissions.add(permission)

