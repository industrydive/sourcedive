from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from sources.choices import PREFIX_CHOICES, COUNTRY_CHOICES, ENTRY_CHOICES


class BasicInfo(models.Model):
    """ abstract base class used across models """
    created = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    updated = models.DateTimeField(blank=True, null=True, auto_now=True, verbose_name=_('Updated in system'), help_text=_('This is when the item was updated in the system.'))

    class Meta:
        abstract = True


class Person(BasicInfo):
    """ class to be inherited by Sources and Journalists """
    # added_by_other = models.BooleanField(default=False, verbose_name=_('Is the person you just added not you?'))
    city = models.CharField(max_length=255, null=True, blank=False, verbose_name=_('City'))
    country = models.CharField(max_length=255, choices=COUNTRY_CHOICES, null=True, blank=False, verbose_name=_('Country'))
    # declined_by_admin = models.BooleanField(default=False, verbose_name=_('Declined'))
    email_address = models.EmailField(max_length=254, null=True, blank=False, verbose_name=_('Email address'))
    entry_method = models.CharField(max_length=15, null=True, blank=True)
    entry_type = models.CharField(max_length=15, null=True, blank=True, default='manual')
    expertise = models.CharField(max_length=255, null=True, blank=True, help_text=_('Comma-separated list'), verbose_name=_('Expertise'))
    # expertise = models.ManyToManyField(Expertise, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=False, verbose_name=_('First name'))
    last_name = models.CharField(max_length=255, null=True, blank=False, verbose_name=_('Last name'))
    # media_audio = models.BooleanField(default=False, verbose_name=_('Audio/radio/podcast'))
    # media_text = models.BooleanField(default=False, verbose_name=_('Text/print'))
    # media_video = models.BooleanField(default=False, verbose_name=_('Video/TV'))
    middle_name = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('Middle name'))
    language = models.CharField(max_length=255, null=True, blank=True, help_text=_('Comma-separated list'), verbose_name=_('Language'))
    # language = models.ManyToManyField(Language)
    # location = models.ForeignKey(Location, null=True, blank=True)
    notes = models.TextField(null=True, blank=True, verbose_name=_('Public notes'), help_text=_('If you would like to share the underrepresented group(s) you identify with, please do so here.'))
    organization = models.CharField(max_length=255, null=True, blank=False, verbose_name=_('Organization')) # , help_text=_('Comma-separated list'))
    # organization = models.ManyToManyField(Organization, blank=True)
    phone_number_primary = models.CharField(max_length=30, null=True, blank=False, verbose_name=_('Primary phone number'), help_text=_('Ideally a cell phone'))
    phone_number_secondary = models.CharField(max_length=30, null=True, blank=True, verbose_name=_('Secondary phone number'))
    prefix = models.CharField(choices=PREFIX_CHOICES, max_length=5, null=True, blank=True, verbose_name=_('Prefix'))
    pronouns = models.CharField(null=True, blank=True, max_length=255, help_text=_('e.g. she/her, they/their, etc.'), verbose_name=_('Pronouns')) ## switch to ManyToManyField? # help_text=_('Everyone is encouraged to enter theirs so journalists know which ones to use (e.g. she/her, they/their, etc.))
    skype = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('Skype username'))
    # slug = models.CharField(null=True, blank=True, max_length=50) # .SlugField(max_length=50)
    state = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('State/province'))
    title = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('Title'))
    timezone = models.IntegerField(null=True, blank=False, validators=[MinValueValidator(-12),MaxValueValidator(12)], verbose_name=_('Time zone offset from GMT'), help_text=_('-4, 10, etc.')) ## lookup based on city/state/county combo?
    twitter = models.CharField(null=True, blank=True, max_length=140, help_text=_('Please do not include the @ symbol. Be sure to include this so we can promote you on Twitter.'), verbose_name=_('Twitter'))
    type_of_expert = models.CharField(max_length=255, null=True, blank=False, help_text=_('e.g. Biologist, Engineer, Mathematician, Sociologist, etc.'), verbose_name=_('Type of expert'))
    # underrepresented = models.BooleanField(default=False, verbose_name=_('Do you identify as a member of an underrepresented group?'))
    website = models.URLField(max_length=255, null=True, blank=False, help_text=_("Please include http:// at the beginning."), verbose_name=_('Website'))
    # woman = models.BooleanField(default=False, verbose_name=_('Do you identify as a woman?''))
    # created_by = models.ForeignKey(User, null=True, blank=True, related_name='created_by_person', on_delete=models.SET_NULL)
    related_user = models.ForeignKey(User, null=True, blank=True, related_name='related_user_person', on_delete=models.SET_NULL)

    def first_last_name(self):
        if self.middle_name:
            return '{} {}'.format(self.first_name, self.middle_name, self.last_name)
        else:
            return '{} {}'.format(self.first_name, self.last_name)
    first_last_name.short_description = _('Name')


    def save(self, *args, **kwargs):
        # elif not self.status:
        #     self.status = 'added'
        # # if self.added_by_other:
        # #     self.status = 'added_by_other'
        if self.twitter:
            # remove the @ sign for consistency and hyperlinking
            self.twitter = self.twitter.replace('@', '')
        if not self.entry_method:
            self.entry_method = 'manual'
        return super(Person, self).save(*args, **kwargs) 

    def __str__(self):
        if self.prefix and self.middle_name:
            name = '{} {} {} {}'.format(self.prefix, self.first_name, self.middle_name, self.last_name)
        elif self.prefix:
            name = '{} {} {}'.format(self.prefix, self.first_name, self.last_name)
        elif self.middle_name:
            name = '{} {} {}'.format(self.first_name, self.middle_name, self.last_name)
        else:
            name = '{} {}'.format(self.first_name, self.last_name)
        return name

    class Meta:
        verbose_name = _('Person')
        verbose_name_plural = _('People')
