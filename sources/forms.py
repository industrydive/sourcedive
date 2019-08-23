from django import forms

from sources.models import Interaction


class InteractionInlineForm(forms.ModelForm):

    class Meta:
        model = Interaction
        fields = ['privacy_level', 'date_time', 'interaction_type', 'interviewee', 'interviewer', 'created_by']
