from django.forms import ModelForm

from news.models import News


class NewsForm(ModelForm):
    class Meta:
        model = News
        fields = ['text', ]

    def __init__(self, *args, **kwargs):
        super(NewsForm, self).__init__(*args, **kwargs)

        self.fields['text'].widget.attrs.update({
            'class': 'md-textarea validate',
        })

