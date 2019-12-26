from django.contrib import admin
from django.contrib.admin.filters import RelatedFieldListFilter, SimpleListFilter
from django.db.models import Q
from django.urls import reverse
from django.utils.html import format_html

from sources.models import (
    Expertise,
    Industry,
    Interaction,
    Organization,
    Person,
)


# for SimpleListFilter classes
all_sources = Person.objects.all()


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
    fields = ['privacy_level', 'date_time', 'interaction_type', 'interviewee', 'interviewer', 'created_by', 'notes_view']

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


class InteractionAdmin(admin.ModelAdmin):
    list_display = ['interviewee', 'interaction_type', 'date_time', 'created_by', 'interviewers_listview', 'privacy_level']
    list_filter = ['interaction_type']
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

    def save_model(self, request, obj, form, change):
        ## associate the Interaction being created with the User who created them
        current_user = request.user
        if not obj.created_by:
            obj.created_by = current_user

        ## save
        super(InteractionAdmin, self).save_model(request, obj, form, change)


    def interviewers_listview(self, obj):
        interviewers_list = obj.interviewer.all()
        interviewers = [interviewer.username for interviewer in interviewers_list]
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


def get_displayable_list(private_items, non_private_items):
    overlap_set = set(private_items) & set(non_private_items)

    set(non_private_items).update(overlap_set)

    displayable_list = list(set(non_private_items))

    return displayable_list


class IndustryFilter(SimpleListFilter):
    title = 'Industry'
    parameter_name = 'industries__name'

    def lookups(self, request, model_admin):
        private_sources = all_sources.filter(privacy_level='private_individual')
        private_industries = [industry.name for source in private_sources for industry in source.industries.all()]

        non_private_sources = all_sources.exclude(privacy_level='private_individual')
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
        private_sources = all_sources.filter(privacy_level='private_individual')
        private_organizations = [organization.name for source in private_sources for organization in source.organization.all()]

        non_private_sources = all_sources.exclude(privacy_level='private_individual')
        non_private_orgnizations = [organization.name for source in non_private_sources for organization in source.organization.all()]

        options = get_displayable_list(private_organizations, non_private_orgnizations)
        filters_list = [(option, option) for option in options]

        return tuple(filters_list)


    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(organization__name=self.value())
        else:
            return queryset


class ExpertiseFilter(SimpleListFilter):
    title = 'Expertise'
    parameter_name = 'expertise__name'

    def lookups(self, request, model_admin):
        private_sources = all_sources.filter(privacy_level='private_individual')
        private_expertise = [expertise.name for source in private_sources for expertise in source.expertise.all()]

        non_private_sources = all_sources.exclude(privacy_level='private_individual')
        non_private_expertise = [expertise.name for source in non_private_sources for expertise in source.industries.all()]

        options = get_displayable_list(private_expertise, non_private_expertise)
        filters_list = [(option, option) for option in options]

        return tuple(filters_list)


    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(expertise__name=self.value())
        else:
            return queryset


class PersonAdmin(admin.ModelAdmin):
    list_display = ['name', 'updated', 'created_by', 'privacy_level']
    list_filter = [IndustryFilter, ExpertiseFilter, OrganizationFilter, 'timezone', 'city', 'state', 'privacy_level']
    # list_filter = ['industries__name', 'organization__name', 'expertise__name', 'timezone', 'city', 'state', 'privacy_level']
    search_fields = ['city', 'country', 'email_address', 'expertise__name', 'first_name', 'language', 'name', 'notes', 'organization', 'state', 'title', 'type_of_expert', 'twitter', 'website']
    filter_horizontal = ['expertise', 'industries', 'organization']
    readonly_fields = ['entry_method', 'entry_type', 'created_by']
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
                        'name',
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
                        'name',
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
        if not obj.created_by:
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
