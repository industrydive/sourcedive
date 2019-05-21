from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from .models import Person


class PersonAdmin(admin.ModelAdmin):
    # fieldsets = (
    #     (None, {

    #     }),
    #     ('Location', {
            # 'fields': ('timezone', 'city', 'state', 'country')
    #     }),
    #     (, {}),
    # )
    fields = ['prefix', 'pronouns', 'first_name', 'middle_name', 'last_name', 'type_of_expert', 'title', 'organization', 'website', 'expertise', 'email_address', 'phone_number_primary', 'phone_number_secondary', 'twitter', 'skype', 'language', 'timezone', 'city', 'state', 'country', 'notes', 'entry_method', 'entry_type'] # 'location', 'woman', 'underrepresented', 'rating','media',
    list_display = ['last_name', 'first_name', 'updated', 'entry_method', 'entry_type'] # 'country', 'timezone_abbrev', 'title', 'type_of_expert', 'rating' ## 'email_address', 'phone_number', 'website', 'first_last_name', 'id_as_woman', 'id_as_underrepresented',
    # list_editable = ['']
    list_filter = ['timezone', 'city', 'state', 'country'] ## , 'title', 'underrepresented', 'woman'
    search_fields = ['city', 'country', 'email_address', 'expertise', 'first_name', 'language', 'last_name', 'notes', 'organization', 'state', 'title', 'type_of_expert', 'twitter', 'website'] # 'location', 'underrepresented', # 'expertise__name', 'language__name', 'organization__name',
    # filter_horizontal = ['expertise', 'organization', 'language']
    readonly_fields = ['entry_method', 'entry_type']
    save_as = True
    save_on_top = True
    # exclude  = ['']

    def timezone_abbrev(self, obj):
        return obj.timezone
    timezone_abbrev.short_description = _('Timezone offset')

    ## THIS NEEDS TO SUPPORT
        # DONE if user.email is Person's email
        # ??? if person is approved (did I mean status-wise?)
    def get_queryset(self, request):
        """ only show the current user if not admin """
        qs = super(PersonAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(email_address=request.user.email)
            # return qs.filter(newsroom=request.user.documentcloudcredentials.newsroom)

    def save_model(self, request, obj, form, change):
        if not obj.created:
            ## associate the Person being created with the User who created them
            current_user = request.user
            # obj.created_by = current_user
            ## set the status
            if current_user.is_superuser == True:
                status = 'added_by_admin'
            elif current_user.email == obj.email:
                status = 'added_by_self'
            else:
                status = 'added_by_other'
            if not obj.entry_method:
                obj.entry_method = 'admin-form'
        # obj.status = status

        ## save
        super(PersonAdmin, self).save_model(request, obj, form, change)


# class SourceForAdminAdmin(admin.ModelAdmin):
#     fields = ['approved_by_admin', 'approved_by_user', 'declined_by_admin', 'role', 'prefix', 'pronouns', 'first_name', 'middle_name', 'last_name', 'type_of_expert', 'title', 'organization', 'website', 'expertise', 'email_address', 'phone_number_primary', 'phone_number_secondary', 'twitter', 'skype', 'language', 'timezone', 'city', 'state', 'country', 'notes', 'entry_method', 'entry_type']
#     list_display = ['last_name', 'first_name', 'updated', 'entry_method', 'entry_type', 'approved_by_user', 'approved_by_admin', 'declined_by_admin', 'role' ]
#     list_editable = ['approved_by_admin', 'declined_by_admin']
#     list_filter = ['created', 'updated', 'approved_by_user', 'approved_by_admin', 'declined_by_admin', 'entry_method', 'entry_type'] # PersonAdmin.list_filter
#     readonly_fields = ['entry_method', 'entry_type']
#     search_fields = PersonAdmin.search_fields
#     save_on_top = True

#     def timezone_abbrev(self, obj):
#         return obj.timezone
#     timezone_abbrev.short_description = _('Timezone offset')

#     def get_queryset(self, request):
#         """ only show Person objects with a role of source """
#         qs = super(SourceForAdminAdmin, self).get_queryset(request)
#         return qs.filter(role='source')


admin.site.register(Person, PersonAdmin)
