from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist


def add_permissions_to_new_whitelisted_users(backend, user, response, *args, **kwargs):
    if not user.last_login:
        user.is_staff = True

        try:
            # get the group
            group = Group.objects.get(name='Newsroom user')
            # add the user to that group
            group.user_set.add(user)
        except ObjectDoesNotExist:
            pass
        # goes outside try/except bc needed for user.is_staff
        user.save()
