from django.contrib import admin
from django.contrib.admin.filters import SimpleListFilter
from django.contrib.admin.utils import flatten_fieldsets
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.models import User
from django.db.models import Q
from django.forms import ModelMultipleChoiceField
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html

from sources.models import (
    Dive,
    Expertise,
    Industry,
    Interaction,
    Organization,
    Person,
)


def get_user_display_name(obj):
    return obj.get_full_name() or obj.username

class UserChoiceField(ModelMultipleChoiceField):
    """
        This will change how the user (might be field interviewer, etc) is
        displayed inside the dropdowns. It will now show the user's full name
        instead of the user's username.
    """
    def label_from_instance(self, obj):
        return get_user_display_name(obj)

class DiveAdmin(admin.ModelAdmin):
    fields = ['name', 'users']
    filter_horizontal = ['users']
    list_display = ['name']
    search_fields = ['name']

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """
            Overwrites formfield_for_manytomany is db field is users.
            Allows us to display user's full name in select dropdowns
        """
        if db_field.name == 'users':
            return UserChoiceField(queryset=User.objects.all(), widget=FilteredSelectMultiple('users', is_stacked=False))
        return super().formfield_for_manytomany(db_field, request, **kwargs)


class ExpertiseAdmin(admin.ModelAdmin):
    fields = ['name']
    list_display = ['name']
    search_fields = ['name']


class IndustryAdmin(admin.ModelAdmin):
    fields = ['name']
    list_display = ['name']
    search_fields = ['name']


# TO-DO: need a way to hide private interactions in the inline
# see https://stackoverflow.com/a/47261297
class InteractionInline(admin.TabularInline):
    model = Interaction
    # the fields are listed explicity to avoid showing notes, which can't be easily displayed like the other hidden field values
    fields = ['privacy_level', 'date_time', 'interaction_type', 'interviewee', 'interviewers_listview', 'created_by', 'notes_view']

    max_num = 0
    readonly_fields = fields  # ['notes_semiprivate']
    show_change_link = True
    classes = ['interactions-previous']


    def notes_view(self, obj):
        """ Generate note text replacement depending on privacy """
        url = reverse('admin:sources_interaction_change', args=(obj.id,))
        if obj.privacy_level == 'searchable':
            display_text = 'Contact <strong>{}</strong> for these notes. <a href="{}">View interaction page</a>.'.format(obj.created_by, url)
        else:
            display_text = obj.notes
        return format_html(display_text)
    notes_view.short_description = 'Notes'


    def get_queryset(self, request):
        """ only show private interactions to the person who created them """
        qs = super(InteractionInline, self).get_queryset(request)

        # if the interaction is not private, then include them
        # if the interaction is private and created by that user, then include them
        return qs.filter(
            # IMPORANT! don't give superusers access to everything
            ~Q(privacy_level__contains='private') | \
            Q(created_by=request.user, privacy_level='private_individual')
        )

    def interviewers_listview(self, obj):
        return InteractionAdmin.interviewers_listview(None, obj)
    interviewers_listview.short_description = 'Interviewer(s)'

class InteractionNewInline(admin.TabularInline):
    model = Interaction
    fields = ['privacy_level', 'date_time', 'interaction_type', 'interviewee', 'interviewer', 'created_by', 'notes']
    extra = 0
    verbose_name = 'interaction (be sure to "save" after)'
    classes = ['interactions-new']


    def get_queryset(self, request):
        """ show none """
        qs = super(InteractionNewInline, self).get_queryset(request)

        return qs.none()

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        return InteractionAdmin.formfield_for_manytomany(self, db_field, request, **kwargs)

class InteractionAdmin(admin.ModelAdmin):
    list_display = ['interviewee', 'interaction_type', 'date_time', 'get_created_by', 'interviewers_listview', 'privacy_level']
    list_filter = ['interaction_type']
    filter_horizontal = ['interviewer']

    _fields_always_readonly = ['get_created_by']
    _fields_before_notes = ['privacy_level', 'date_time', 'interaction_type', 'interviewee', 'interviewer']
    _fields_after_notes = ['get_created_by']


    def _determine_whether_to_hide_notes(self, request, obj):
        """
        Given a request and an object, determine if we need to hide the contact data for the object. If
        the object is None (doesn't exist yet), always return False (we don't need to hide anything).

        Returns True if we need to hide the notes, False if the user has permissions to see/edit the notes.

        NOTE: this could be abstracted out, as it is virtually identical to _determine_whether_to_hide_contact_data
        in PersonAdmin.
        """
        if not obj:
            return False
        elif obj.privacy_level in ['searchable', 'private_individual'] and obj.created_by != request.user:
            return True
        else:
            return False

    def get_readonly_fields(self, request, obj=None):
        """
        If the user doesn't have permission to see the notes, both the notes display and the
        privacy level are added to the default readonly fields.

        Use Django's built in hook for accessing readonly fields. NOTE: Manipulating self.readonly_fields
        directly leads to problems.
        """
        hide_data = self._determine_whether_to_hide_notes(request, obj)
        if hide_data:
            return self._fields_always_readonly + ['notes_semiprivate_display', 'privacy_level']
        else:
            return self._fields_always_readonly


    def get_fields(self, request, obj=None):
        """
        If the user doesn't have permission to view the notes, display the replacement notes field instead.

        Use Django's built in hook for accessing fields. NOTE: Manipulating self.fields directly can lead to problems.
        """
        hide_data = self._determine_whether_to_hide_notes(request, obj)
        if hide_data:
            return self._fields_before_notes + ['notes_semiprivate_display'] + self._fields_after_notes
        else:
            return self._fields_before_notes + ['notes'] + self._fields_after_notes

    def get_queryset(self, request):
        """ only show private interactions to the person who created them """
        qs = super(InteractionAdmin, self).get_queryset(request)

        # if the source is not private, then include them
        # if the source is private and created by that user, then include them
        return qs.filter(
            # IMPORANT! don't give superusers access to everything
            ~Q(privacy_level__contains='private') | \
            Q(created_by=request.user, privacy_level='private_individual')
        )

    def save_model(self, request, obj, form, change):
        ## associate the Interaction being created with the User who created them
        current_user = request.user
        if not obj.created_by:
            obj.created_by = current_user

        ## save
        super(InteractionAdmin, self).save_model(request, obj, form, change)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """
            Overwrites formfield_for_manytomany is db field is interviewer.
            Allows us to display user's full name in select dropdowns
        """
        if db_field.name == 'interviewer':
            return UserChoiceField(queryset=User.objects.all(), widget=FilteredSelectMultiple('interviewer', is_stacked=False))
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def get_created_by(self, obj):
        """
            This will display a custom created_by field by using
            the user's first and last name instead of the user's username
        """
        return get_user_display_name(obj.created_by)
    get_created_by.short_description = 'Created By'

    def interviewers_listview(self, obj):
        interviewers_list = obj.interviewer.all()
        interviewers = [get_user_display_name(interviewer) for interviewer in interviewers_list]
        return ', '.join(interviewers)
    interviewers_listview.short_description = 'Interviewer(s)'


    def notes_semiprivate_display(self, obj):
        display_text = 'Please contact <strong>{}</strong> for this information'.format(obj.created_by)
        return format_html(display_text)
    notes_semiprivate_display.short_description = 'Notes'


class OrganizationAdmin(admin.ModelAdmin):
    fields = ['name']
    list_display = ['name']
    search_fields = ['name']


# for SimpleListFilter classes
all_sources = Person.objects.all()
private_sources = all_sources.filter(privacy_level='private_individual')
non_private_sources = all_sources.exclude(privacy_level='private_individual')


# for SimpleListFilter classes
def get_displayable_list(private_items, non_private_items):
    overlap_set = set(private_items) & set(non_private_items)

    set(non_private_items).update(overlap_set)

    displayable_list = list(set(non_private_items))

    return displayable_list


class ExpertiseFilter(SimpleListFilter):
    title = 'Expertise'
    parameter_name = 'expertise__name'

    def lookups(self, request, model_admin):
        private_expertise = [expertise.name for source in private_sources for expertise in source.expertise.all()]
        non_private_expertise = [expertise.name for source in non_private_sources for expertise in source.expertise.all()]

        options = get_displayable_list(private_expertise, non_private_expertise)
        filters_list = [(option, option) for option in options]

        return tuple(filters_list)


    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(expertise__name=self.value())
        else:
            return queryset


class IndustryFilter(SimpleListFilter):
    title = 'Industry'
    parameter_name = 'industries__name'

    def lookups(self, request, model_admin):
        private_industries = [industry.name for source in private_sources for industry in source.industries.all()]
        non_private_industries = [industry.name for source in non_private_sources for industry in source.industries.all()]

        options = get_displayable_list(private_industries, non_private_industries)
        filters_list = [(option, option) for option in options]

        return tuple(filters_list)


    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(industries__name=self.value())
        else:
            return queryset


class OrganizationFilter(SimpleListFilter):
    title = 'Organization'
    parameter_name = 'organization__name'

    def lookups(self, request, model_admin):
        private_organizations = [organization.name for source in private_sources for organization in source.organization.all()]
        non_private_organizations = [organization.name for source in non_private_sources for organization in source.organization.all()]

        options = get_displayable_list(private_organizations, non_private_organizations)
        filters_list = [(option, option) for option in options]

        return tuple(filters_list)


    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(organization__name=self.value())
        else:
            return queryset


class PersonAdmin(admin.ModelAdmin):
    list_display = ['name', 'updated', 'get_created_by', 'privacy_level']
    list_filter = [IndustryFilter, ExpertiseFilter, OrganizationFilter, 'city', 'state', 'privacy_level', 'gatekeeper']
    search_fields = ['city', 'country', 'email_address', 'expertise__name', 'first_name', 'language', 'name', 'notes', 'organization', 'state', 'title', 'type_of_expert', 'twitter', 'website']
    filter_horizontal = ['expertise', 'industries', 'organization', 'exportable_by']
    readonly_fields = ['entry_method', 'entry_type', 'get_created_by', 'updated']
    # save_as = True
    save_on_top = True
    view_on_site = False  # THIS DOES NOT WORK CURRENTLY
    inlines = (InteractionInline, InteractionNewInline,)


    def email_address_semiprivate_display(self, obj):
        display_text = 'Please contact <strong>{}</strong> for this information'.format(obj.created_by)
        return format_html(display_text)
    email_address_semiprivate_display.short_description = 'Email address'


    def phone_number_primary_semiprivate_display(self, obj):
        display_text = 'Please contact <strong>{}</strong> for this information'.format(obj.created_by)
        return format_html(display_text)
    phone_number_primary_semiprivate_display.short_description = 'Phone number primary'


    def phone_number_secondary_semiprivate_display(self, obj):
        display_text = 'Please contact <strong>{}</strong> for this information'.format(obj.created_by)
        return format_html(display_text)
    phone_number_secondary_semiprivate_display.short_description = 'Phone number secondary'


    def _get_correct_contact_field_names(self, hide_contact_data=False):
        """
        Returns a list of the contact field names that differ depending on privacy. (the base field
        names such as twitter or linkedin are not returned from here)
        """

        prepend_contact_fields = [
            'email_address',
            'phone_number_primary',
            'phone_number_secondary',
        ]

        if hide_contact_data:
            # set the semiprivate fields to the display value
            return [name + '_semiprivate_display' for name in prepend_contact_fields]
        else:
            return prepend_contact_fields


    def _determine_whether_to_hide_contact_data(self, request, obj):
        """
        Given a request and an object, determine if we need to hide the contact data for the object. If
        the object is None (doesn't exist yet), always return False (we don't need to hide anything).

        Returns True if we need to hide the data, False if the user has permissions to see/edit the data.

        NOTE: this could be abstracted out, as it is virtually identical to _determine_whether_to_hide_notes
        in InteractionAdmin.
        """
        if not obj:
            # If creating a new `Person`, give all permissions
            return False
        elif obj.created_by == request.user:
            # Users can always see their own `Person`s
            return False
        elif obj.privacy_level in ['searchable', 'private_individual']:
            # If the `Person` is at all private, and the user didn't create the
            # object, don't allow viewing of contact data
            return True
        else:
            # Only reach here for public `Person`s created by a different user
            return False


    def _return_fieldsets(self, hide_contact_data=False):
        """
        Returns the correct fieldsets based on whether we're hiding data. This is called when we're
        building the fieldsets as well as when we are setting all fields to readonly.

        NOTE: This could be considerably more abstract and thus complicated: it could change fieldsets
        besides the contact info. I decided to shy away from that right now -- we can always come
        back and change it.

        Arguments:
            hide_contact_data - if True, replace the email & phone fields with the semiprivate display values, as well
                as setting the readonly fields to include these fields.
        """

        base_contact_fields = [
            'linkedin',
            'twitter',
            'skype',
        ]
        custom_contact_fields = self._get_correct_contact_field_names(hide_contact_data=hide_contact_data)
        current_contact_fields = base_contact_fields + custom_contact_fields

        return (
            ('Privacy', {
                'fields': ('privacy_level',)
            }),
            ('General info', {
                'fields': (
                    'prefix',
                    'pronouns',
                    'name',
                    'title',
                    'gatekeeper',
                    'industries',
                    'organization',
                    'website',
                    'type_of_expert',
                    'expertise',
                ),
            }),
            ('Contact info', {
                'fields': current_contact_fields
            }),
            ('Location info', {
                'fields': (
                    'timezone',
                    'city',
                    'state',
                    'country',
                ),
            }),
            ('Advanced info', {
                'classes': ('collapse',),
                'fields': (
                    'exportable_by',
                    'entry_method',
                    'entry_type',
                    'get_created_by',
                    # 'last_updated_by',
                    'updated',
                ),
            }),
        )


    def get_queryset(self, request):
        """ only show private sources to the person who created them """
        qs = super(PersonAdmin, self).get_queryset(request)

        # if the source is not private, then include them
        # if the source is private and created by that user, then include them
        return qs.filter(
            # IMPORANT! don't give superusers access to everything
            ~Q(privacy_level__contains='private') | \
            Q(created_by=request.user, privacy_level='private_individual')
        )


    def get_fieldsets(self, request, obj=None):
        """
        Use Django's built in hook for accessing the fieldsets. Manipulating self.fieldsets directly
        leads to problems.
        """

        # TODO: we may able to delete this if statement, as we believe the first case is covered
        # by the queryset restrictions
        if obj and obj.created_by != request.user and obj.privacy_level == 'private_individual':
            # Cover the one weird edge case not covered by `_determine_whether_to_hide_contact_data`
            # This is if the user is trying to view a person they're not even allowed to know exists
            return [(None, {'fields': []})]
        else:
            # Construct the correct fieldsets based on permissions
            hide_contact_data = self._determine_whether_to_hide_contact_data(request, obj)
            return self._return_fieldsets(hide_contact_data=hide_contact_data)


    def get_readonly_fields(self, request, obj=None):
        """
        Use Django's built in hook for accessing readonly fields. Manipulating self.readonly_fields
        directly leads to problems.
        """
        if not obj:
            # If creating the obj, use only default readonly fields
            return self.readonly_fields

        hide_contact_data = self._determine_whether_to_hide_contact_data(request, obj)

        if 'edit' not in request.GET:
            # If we're not editing, all fields should be readonly
            # Use _return_fieldsets to get the correct fields for this permission level
            current_fieldsets = self._return_fieldsets(hide_contact_data=hide_contact_data)
            return flatten_fieldsets(current_fieldsets)
        elif hide_contact_data:
            # If we're editing, and data is hidden from the user, we want the contact data to be readonly
            # We also want the privacy level field to be readonly
            contact_fields_to_add = self._get_correct_contact_field_names(hide_contact_data=hide_contact_data)
            return self.readonly_fields + ['privacy_level'] + contact_fields_to_add
        else:
            # If we're editing AND the user has permissions, use the default fields
            return self.readonly_fields


    def response_change(self, request, obj):
        url = reverse('admin:sources_person_change', args=(obj.id,))

        if '_edit' in request.POST:
            return HttpResponseRedirect(url + '?edit=true')
        elif '_view' in request.POST:
            return HttpResponseRedirect(url)

        return super(PersonAdmin, self).response_change(request, obj)


    def save_model(self, request, obj, form, change):
        ## associate the Person being created with the User who created them
        current_user = request.user
        if not obj.created_by:
            obj.created_by = current_user
        if not obj.entry_method:
            obj.entry_method = 'admin-form'

        ## save
        super(PersonAdmin, self).save_model(request, obj, form, change)

    def get_created_by(self, obj):
        """
            This will display a custom created_by field by using
            the user's first and last name instead of the user's username
        """
        return get_user_display_name(obj.created_by)
    get_created_by.short_description = 'Created By'


admin.site.register(Dive, DiveAdmin)
admin.site.register(Expertise, ExpertiseAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Industry, IndustryAdmin)
admin.site.register(Interaction, InteractionAdmin)
admin.site.register(Person, PersonAdmin)

admin.site.site_header = 'Source Dive'
