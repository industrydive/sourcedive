from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.utils.html import format_html
from .models import Interaction, Person


class InteractionInline(admin.TabularInline):
    model = Interaction


class InteractionAdmin(admin.ModelAdmin):
    fields = ['date_time', 'interaction_type', 'interviewee', 'interviewer', 'notes', 'created_by']
    filter_horizontal = ['interviewer']
    readonly_fields = ['created_by']

    # def get_queryset(self, request):
    #     """ only show private interactions to the person who created them """
    #     qs = super(InteractionAdmin, self).get_queryset(request)
    #     return qs.exclude(private=True)


class PersonAdmin(admin.ModelAdmin):
    # fieldsets = (
    #     ('General info', {

    #     }),
    #     ('Contact', {}),
    #     ('Location', {
            # 'fields': ('timezone', 'city', 'state', 'country')
    #     })
    # ),
    fields = ['private', 'prefix', 'pronouns', 'first_name', 'middle_name', 'last_name', 'type_of_expert', 'title', 'organization', 'website', 'expertise', 'email_address', 'phone_number_primary', 'phone_number_secondary', 'twitter', 'skype', 'language', 'timezone', 'city', 'state', 'country', 'notes', 'entry_method', 'entry_type', 'created_by']
    list_display = ['last_name', 'first_name', 'updated', 'entry_method', 'entry_type', 'private'] # 'country', 'timezone_abbrev', 'title', 'type_of_expert', 'rating' ## 'email_address', 'phone_number', 'website', 'id_as_woman'
    list_filter = ['timezone', 'city', 'state', 'country']
    search_fields = ['city', 'country', 'email_address', 'expertise', 'first_name', 'language', 'last_name', 'notes', 'organization', 'state', 'title', 'type_of_expert', 'twitter', 'website']  # 'location',
    # filter_horizontal = ['expertise', 'organization', 'language']
    readonly_fields = ['entry_method', 'entry_type', 'created_by']
    # save_as = True
    save_on_top = True
    view_on_site = False  # THIS DOES NOT WORK CURRENTLY
    inlines = (InteractionInline,)

    def timezone_abbrev(self, obj):
        return obj.timezone
    timezone_abbrev.short_description = ('Timezone offset')

    def get_queryset(self, request):
        """ only show private sources to the person who created them """
        qs = super(PersonAdmin, self).get_queryset(request)

        # if the source is not private, then include them
        # if the source is private and created by that user, then include them
        return qs.filter(
            # IMPORANT! don't give superusers access to everything
            Q(private=False) | Q(created_by=request.user, private=True)
        )

    def save_model(self, request, obj, form, change):
        ## associate the Person being created with the User who created them
        current_user = request.user
        obj.created_by = current_user
        if not obj.entry_method:
            obj.entry_method = 'admin-form'

        ## save
        super(PersonAdmin, self).save_model(request, obj, form, change)


admin.site.register(Interaction, InteractionAdmin)
admin.site.register(Person, PersonAdmin)
