from django.contrib import admin
from django.db.models import Q
from django.utils.html import format_html

from .models import (
    Expertise,
    Industry,
    Interaction,
    Organization,
    Person,
)


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
    fields = ['privacy_level', 'date_time', 'interaction_type', 'interviewee', 'interviewer', 'created_by']


class InteractionAdmin(admin.ModelAdmin):
    list_display = ['interviewee', 'interaction_type', 'privacy_level', 'date_time']
    filter_horizontal = ['interviewer']


    def change_view(self, request, object_id, form_url='', extra_context=None):
        """
        If the privacy level is semi-private/searchable and the logged
        in user is not the one who created the interaction, then remove
        notes field for them
        """
        obj = Interaction.objects.get(id=object_id)
        if obj.privacy_level == 'searchable' and obj.created_by != request.user:
            self.fields = ['privacy_level', 'date_time', 'interaction_type', 'interviewee', 'interviewer', 'notes_semiprivate_display', 'created_by']
            self.readonly_fields = ['created_by', 'privacy_level', 'notes_semiprivate_display']
        else:
            self.fields = ['privacy_level', 'date_time', 'interaction_type', 'interviewee', 'interviewer', 'notes', 'created_by']
            self.readonly_fields = ['created_by']
        return self.changeform_view(request, object_id, form_url, extra_context)


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

    def notes_semiprivate_display(self, obj):
        display_text = 'Please contact <strong>{}</strong> for this information'.format(obj.created_by)
        return format_html(display_text)
    notes_semiprivate_display.short_description = 'Notes'


class OrganizationAdmin(admin.ModelAdmin):
    fields = ['name']
    list_display = ['name']
    search_fields = ['name']


class PersonAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'updated', 'created_by', 'privacy_level']
    list_filter = ['organization__name', 'expertise__name', 'timezone', 'city', 'state', 'privacy_level']
    search_fields = ['city', 'country', 'email_address', 'expertise__name', 'first_name', 'language', 'last_name', 'notes', 'organization', 'state', 'title', 'type_of_expert', 'twitter', 'website']
    filter_horizontal = ['expertise', 'industries', 'organization']
    readonly_fields = ['entry_method', 'entry_type', 'created_by']
    # save_as = True
    save_on_top = True
    view_on_site = False  # THIS DOES NOT WORK CURRENTLY
    inlines = (InteractionInline,)


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


    def change_view(self, request, object_id, form_url='', extra_context=None):
        """
        If the privacy level is semi-private/searchable and the logged
        in user is not the one who created the interaction, then remove
        notes field for them
        """
        obj = Person.objects.get(id=object_id)
        if obj.privacy_level == 'searchable' and obj.created_by != request.user:
            self.fieldsets = (
                ('Privacy', {
                    'fields': ('privacy_level',)
                }),
                ('General info', {
                    'fields': (
                        'prefix',
                        'pronouns',
                        'first_name',
                        'middle_name',
                        'last_name',
                        'title',
                        'industries',
                        'organization',
                        'website',
                        'type_of_expert',
                        'expertise',
                    ),
                }),
                ('Contact info', {
                    'fields': (
                        'email_address_semiprivate_display',
                        'phone_number_primary_semiprivate_display',
                        'phone_number_secondary_semiprivate_display',
                        'linkedin',
                        'twitter',
                        'skype',
                    ),
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
                        'entry_method',
                        'entry_type',
                        'created_by',
                    ),
                }),
            )
            self.readonly_fields = [
                'created_by',
                'entry_method',
                'entry_type',
                'email_address_semiprivate_display',
                'phone_number_primary_semiprivate_display',
                'phone_number_secondary_semiprivate_display',
            ]
        else:
            self.fieldsets = (
                ('Privacy', {
                    'fields': ('privacy_level',)
                }),
                ('General info', {
                    'fields': (
                        'prefix',
                        'pronouns',
                        'first_name',
                        'middle_name',
                        'last_name',
                        'title',
                        'industries',
                        'organization',
                        'website',
                        'type_of_expert',
                        'expertise',
                    ),
                }),
                ('Contact info', {
                    'fields': (
                        'email_address',
                        'phone_number_primary',
                        'phone_number_secondary',
                        'linkedin',
                        'twitter',
                        'skype',
                    ),
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
                        'entry_method',
                        'entry_type',
                        'created_by',
                    ),
                }),
            )
            self.readonly_fields = [
                'created_by',
                'entry_method',
                'entry_type',
            ]
        return self.changeform_view(request, object_id, form_url, extra_context)


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


    def save_model(self, request, obj, form, change):
        ## associate the Person being created with the User who created them
        current_user = request.user
        obj.created_by = current_user
        if not obj.entry_method:
            obj.entry_method = 'admin-form'

        ## save
        super(PersonAdmin, self).save_model(request, obj, form, change)


admin.site.register(Expertise, ExpertiseAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Industry, IndustryAdmin)
admin.site.register(Interaction, InteractionAdmin)
admin.site.register(Person, PersonAdmin)
