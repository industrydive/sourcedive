from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.urls import reverse

from sources.choices import PREFIX_CHOICES, COUNTRY_CHOICES, ENTRY_CHOICES


class BasicInfo(models.Model):
    """ abstract base class used across models """
    created = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    updated = models.DateTimeField(blank=True, null=True, auto_now=True, verbose_name=('Updated in system'), help_text=('This is when the item was updated in the system.'))

    class Meta:
        abstract = True


class Person(BasicInfo):
    """ representation of a Sources in the system """
    city = models.CharField(max_length=255, null=True, blank=False, verbose_name=('City'))
    country = models.CharField(max_length=255, choices=COUNTRY_CHOICES, null=True, blank=False, verbose_name=('Country'))
    email_address = models.EmailField(max_length=254, null=True, blank=False, verbose_name=('Email address'))
    entry_method = models.CharField(max_length=15, null=True, blank=True)
    entry_type = models.CharField(max_length=15, null=True, blank=True, default='manual')
    expertise = models.CharField(max_length=255, null=True, blank=True, help_text=('Comma-separated list'), verbose_name=('Expertise'))
    first_name = models.CharField(max_length=255, null=True, blank=False, verbose_name=('First name'))
    last_name = models.CharField(max_length=255, null=True, blank=False, verbose_name=('Last name'))
    middle_name = models.CharField(max_length=255, null=True, blank=True, verbose_name=('Middle name'))
    language = models.CharField(max_length=255, null=True, blank=True, help_text=('Comma-separated list'), verbose_name=('Language'))
    notes = models.TextField(null=True, blank=True)
    organization = models.CharField(max_length=255, null=True, blank=False, verbose_name=('Organization')) # , help_text=('Comma-separated list'))
    phone_number_primary = models.CharField(max_length=30, null=True, blank=False, verbose_name=('Primary phone number'), help_text=('Ideally a cell phone'))
    phone_number_secondary = models.CharField(max_length=30, null=True, blank=True, verbose_name=('Secondary phone number'))
    prefix = models.CharField(choices=PREFIX_CHOICES, max_length=5, null=True, blank=True, verbose_name=('Prefix'))
    private = models.BooleanField(blank=True, default=True, help_text='Private sources will only be visible to you. Non-private sources will be visible to all newsroom users.')
    pronouns = models.CharField(null=True, blank=True, max_length=255, help_text=('e.g. she/her, they/their, etc.'), verbose_name=('Pronouns'))  # switch to ManyToManyField?
    skype = models.CharField(max_length=255, null=True, blank=True, verbose_name=('Skype username'))
    state = models.CharField(max_length=255, null=True, blank=True, verbose_name=('State/province'))
    title = models.CharField(max_length=255, null=True, blank=True, verbose_name=('Title'))
    timezone = models.IntegerField(null=True, blank=False, validators=[MinValueValidator(-12),MaxValueValidator(12)], verbose_name=('Time zone offset from GMT'), help_text=('-4, 10, etc.'))  # look up based on city/state/county combo?
    twitter = models.CharField(null=True, blank=True, max_length=140, help_text=('Please do not include the @ symbol.'), verbose_name=('Twitter'))
    type_of_expert = models.CharField(max_length=255, null=True, blank=False, help_text=('e.g. Biologist, Engineer, Mathematician, Sociologist, etc.'), verbose_name=('Type of expert'))
    website = models.URLField(max_length=255, null=True, blank=False, help_text=("Please include http:// at the beginning."), verbose_name=('Website'))
    created_by = models.ForeignKey(User, null=True, blank=True, related_name='created_by_person', on_delete=models.SET_NULL)
    related_user = models.ForeignKey(User, null=True, blank=True, related_name='related_user_person', on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
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
        verbose_name = ('Person')
        verbose_name_plural = ('People')


class Interaction(BasicInfo):
    """ representation of each interaction with a source """
    INTERACTION_CHOICES = (
        ('email', 'Email'),
        ('inperson', 'In-person'),
        ('telephone', 'Telephone'),
    )
    created_by = models.ForeignKey(User, null=True, blank=True, related_name='created_by_person_interaction', on_delete=models.SET_NULL)
    date_time = models.DateTimeField(blank=False, help_text='When the interaction took place', verbose_name='When?')
    interaction_type = models.CharField(blank=True, max_length=255,choices=INTERACTION_CHOICES, verbose_name='Type')
    interviewee = models.ForeignKey(Person, null=True, related_name='interviee', verbose_name='Interviewee', on_delete=models.SET_NULL)
    interviewer = models.ManyToManyField(User, related_name='interviewer', verbose_name='Interviewer(s)')
    notes = models.TextField(blank=True, help_text='Add any notes about interaction that may be helpful to you or others in the future.')
    # timezone ??? see newspost code

    def __str__(self):
        return '{} via {} ({} at {})'.format(self.interviewee, self.interaction_type, self.date_time.date(), self.date_time.time())

    class Meta:
        verbose_name = ('Interaction')
        verbose_name_plural = ('Interactions')
