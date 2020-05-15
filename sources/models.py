from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from sources.choices import (
    COUNTRY_CHOICES,
    ENTRY_CHOICES,
    PRIVACY_CHOICES,
    PREFIX_CHOICES
)


class BasicInfo(models.Model):
    """ Abstract base class used across models """
    created = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    updated = models.DateTimeField(blank=True, null=True, auto_now=True, verbose_name='Updated in system', help_text='This is when the item was updated in the system.')
    # last_updated_by = models.ForeignKey(User, null=True, blank=True, related_name='last_updated_by', on_delete=models.SET_NULL)

    class Meta:
        abstract = True


class Dive(BasicInfo):
    name = models.CharField(max_length=255, null=True, blank=False, unique=True)
    users = models.ManyToManyField(User, blank=True, related_name='dive_members')

    def __str__(self):
        return '{}'.format(self.name)


class Expertise(BasicInfo):
    name = models.CharField(max_length=255, null=True, blank=False, unique=True, verbose_name='Type of expertise')

    class Meta:
        verbose_name_plural = 'Expertise'

    def __str__(self):
        return '{}'.format(self.name)


class Industry(BasicInfo):
    name = models.CharField(max_length=255, null=True, blank=False, unique=True, verbose_name='Industry name')

    class Meta:
        verbose_name_plural = 'Industries'

    def __str__(self):
        return '{}'.format(self.name)


class Organization(BasicInfo):
    name = models.CharField(max_length=255, null=True, blank=False, unique=True, verbose_name='Organization name')
    # location = models.ForeignKey(Location, null=True, blank=True)
    # website = models.URLField(max_length=200, null=True, blank=True)

    def __str__(self):
        return '{}'.format(self.name)


class PrivacyMixin(models.Model):
    privacy_level = models.CharField(choices=PRIVACY_CHOICES, max_length=255, blank=False, help_text='Who has access to view? Searchable (semi-private) means the general information is available, but not certain details.')

    class Meta:
        abstract = True


class Person(BasicInfo, PrivacyMixin):
    """ Representation of a Sources in the system """
    def timezone_choices():
        import pytz
        pytz_all = pytz.all_timezones
        tz_list = []
        for tz in pytz_all:
            item = tz, tz
            tz_list.append(item)
        timezones = tuple(tz_list)
        return timezones

    city = models.CharField(max_length=255, null=True, blank=True, verbose_name='City')
    country = models.CharField(max_length=255, choices=COUNTRY_CHOICES, null=True, blank=True, verbose_name='Country')
    email_address = models.EmailField(max_length=254, null=True, blank=False, verbose_name=('Email address'))
    entry_method = models.CharField(max_length=15, null=True, blank=True)
    entry_type = models.CharField(max_length=15, null=True, blank=True, default='manual')
    expertise = models.ManyToManyField(Expertise, blank=True)
    # expertise = models.CharField(max_length=255, null=True, blank=True, help_text='Comma-separated list', verbose_name='Expertise')
    exportable_by = models.ManyToManyField(Dive, blank=True, related_name='dive_owner', help_text='These are the dives that can export this source.')
    gatekeeper = models.BooleanField(blank=True, default=False, help_text='Is this person the contact for another source?')
    import_notes = models.TextField(null=True, blank=True, help_text='Any information deemed relevant to the source at the time of import.')
    industries = models.ManyToManyField(Industry, blank=True)
    language = models.CharField(max_length=255, null=True, blank=True, help_text='Comma-separated list', verbose_name='Language')
    linkedin = models.URLField(max_length=255, null=True, blank=True, help_text='Please include http:// at the beginning.', verbose_name='LinkedIn URL')
    name = models.CharField(max_length=255, null=True, blank=False)
    organization = models.ManyToManyField(Organization, blank=True)
    # organization = models.CharField(max_length=255, null=True, blank=True, verbose_name='Organization') # , help_text='Comma-separated list')
    phone_number_primary = models.CharField(max_length=30, null=True, blank=True, verbose_name='Primary phone number', help_text=('Ideally a cell phone'))
    phone_number_secondary = models.CharField(max_length=30, null=True, blank=True, verbose_name='Secondary phone number')
    prefix = models.CharField(max_length=30, null=True, blank=True, verbose_name='Prefix')
    # private = models.BooleanField(blank=True, default=False, help_text='Private sources will only be visible to you. Non-private sources will be visible to all newsroom users.')
    pronouns = models.CharField(null=True, blank=True, max_length=255, help_text='If provided by source (e.g. she/her, they/their, etc.)', verbose_name='Pronouns')
    skype = models.CharField(max_length=255, null=True, blank=True, verbose_name='Skype username')
    state = models.CharField(max_length=255, null=True, blank=True, verbose_name='State/province')
    title = models.CharField(max_length=255, null=True, blank=True, verbose_name='Job title')
    timezone = models.CharField(max_length=255, choices=timezone_choices(), blank=True, null=True, verbose_name='Time zone')
    twitter = models.CharField(null=True, blank=True, max_length=140, help_text='Please do not include the @ symbol.', verbose_name='Twitter')
    type_of_expert = models.CharField(max_length=255, null=True, blank=True, help_text='If applicable (e.g. economist, engineer, researcher, etc.)', verbose_name='Type of expert')
    website = models.URLField(max_length=255, null=True, blank=True, help_text='Please include http:// at the beginning.', verbose_name='Website')
    created_by = models.ForeignKey(User, null=True, blank=True, related_name='created_by_person', on_delete=models.SET_NULL)
    # TODO: remove this bc it's a vestige of other project
    related_user = models.ForeignKey(User, null=True, blank=True, related_name='related_user_person', on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        if self.twitter:
            # remove the @ sign for consistency and hyperlinking
            self.twitter = self.twitter.replace('@', '')
        if not self.entry_method:
            self.entry_method = 'manual'
        return super(Person, self).save(*args, **kwargs)

    def __str__(self):
        if self.name:
            return self.name
        else:
            return ''

    class Meta:
        ordering = ['-updated']
        verbose_name = ('Source')


class Interaction(BasicInfo, PrivacyMixin):
    """ Representation of each interaction with a source """
    INTERACTION_CHOICES = (
        ('email', 'Email'),
        ('inperson', 'In-person'),
        ('telephone', 'Telephone'),
    )
    created_by = models.ForeignKey(User, null=True, blank=True, related_name='created_by_person_interaction', on_delete=models.SET_NULL)
    date_time = models.DateTimeField(blank=False, help_text='When the interaction took place', verbose_name='When?')
    interaction_type = models.CharField(blank=True, max_length=255,choices=INTERACTION_CHOICES, verbose_name='Type')
    interviewee = models.ForeignKey(Person, null=True, related_name='interviewee', verbose_name='Interviewee', on_delete=models.SET_NULL)
    interviewer = models.ManyToManyField(User, related_name='interviewer', verbose_name='Interviewer(s)')
    notes = models.TextField(blank=True, help_text='Add any notes about interaction that may be helpful to you or others in the future.')
    # timezone with datetime ??? see newspost code

    # @property
    # def is_private(self):
    #     if self.interviewee.privacy_level == 'private_individual':
    #         return True
    #     else:
    #         return False

    def __str__(self):
        if self.interaction_type:
            interaction_info = 'via {}'.format(self.interaction_type)
        else:
            interaction_info = ''
        return '{} {} ({} at {})'.format(self.interviewee, interaction_info, self.date_time.date(), self.date_time.time())

    class Meta:
        ordering = ['-date_time']
        verbose_name = ('Interaction')
        verbose_name_plural = ('Interactions')
