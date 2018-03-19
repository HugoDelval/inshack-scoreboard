from django import forms

from challenges.models import Challenge


class ChallengeForm(forms.ModelForm):
    class Meta:
        model = Challenge
        fields = ['name', 'description', 'category', 'difficulty', 'flag', 'chall_file', 'is_enabled', 'is_ovh_chall', 'nb_points_override']

    def __init__(self, *args, **kwargs):
        super(ChallengeForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = 'Challenge name'
        self.fields['name'].widget.attrs.update({
            'class': 'form-control validate',
        })

        self.fields['description'].label = 'Description'
        self.fields['description'].widget.attrs.update({
            'class': 'md-textarea validate',
        })

        self.fields['category'].label = ''
        self.fields['category'].widget.attrs.update({
            'class': 'form-control validate',
        })

        self.fields['difficulty'].label = ''
        self.fields['difficulty'].widget.attrs.update({
            'class': 'form-control validate',
        })

        self.fields['nb_points_override'].label = 'If value > -3, then will override the automagic points calculus'
        self.fields['nb_points_override'].widget.attrs.update({
            'class': 'form-control validate',
        })

        self.fields['flag'].label = 'Flag'
        self.fields['flag'].widget.attrs.update({
            'class': 'form-control validate',
        })

        self.fields['chall_file'].label = '(opt) Challenge\'s file(s)'
        self.fields['chall_file'].widget.attrs.update({
            'class': 'form-control validate',
        })

        self.fields['is_enabled'].label = 'Put online now ?'
        self.fields['is_ovh_chall'].label = 'Is this a challenge from OVH?'


class SubmitionForm(forms.Form):
    flag = forms.CharField(widget=forms.TextInput)

    def __init__(self, *args, **kwargs):
        super(SubmitionForm, self).__init__(*args, **kwargs)
        self.fields['flag'].label = 'Flag'
        self.fields['flag'].widget.attrs.update({
            'class': 'form-control'
        })
