from django import forms
from django.utils.safestring import mark_safe
from .utils import msgs, language_code
from .models import Resources, ResourceTypes, ResourceStatuses, Langs, Authors


class SuggestResourceForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        msgs = kwargs.pop('msgs')
        super().__init__(*args, **kwargs)
        self.msgs = msgs
        self.language_code = msgs['language_code']

        print(self.msgs)

        self.fields['title'].label = msgs['suggest_title']
        self.fields['title'].error_messages = {'required': msgs['suggest_title'] + ' ' + msgs['error_required']}

        self.fields['subtitle'].label = msgs['suggest_subtitle']

        self.fields['type'].label = msgs['resource_type']
        self.fields['type'].error_messages = {'required': msgs['resource_type'] + ' ' + msgs['error_required']}
        self.fields['type'].queryset = ResourceTypes.objects.filter(lang_id=self.language_code)

        self.fields['description'].label = msgs['suggest_desc']
        self.fields['description'].error_messages = {'required': msgs['suggest_desc'] + ' ' + msgs['error_required']}

        self.fields['resource_link'].label = msgs['link']
        self.fields['group_link'].label = msgs['group_link']
        self.fields['date_created'].label = msgs['resourcecreated']
        self.fields['suggested_authors'].label = msgs['suggested_authors']
        self.fields['suggested_editors'].label = msgs['suggested_editors']
        self.fields['submitter_name'].label = msgs['submitter_name']
        self.fields['submitter_email'].label = msgs['submitter_email']
        self.fields['book'].label = msgs['book_name_for_chapter']
        self.fields['isbn'].label = 'ISBN'
        self.fields['journal'].label = msgs['journal_name']
        self.fields['journal_issue'].label = msgs['journal_issue']

    title = forms.CharField(label=msgs['suggest_title'],
                            max_length=255,
                            help_text="255 characters max.",
                            error_messages={"required": msgs['error_required'],
                                            "max_length": msgs['error_max_chars']})  # 255

    subtitle = forms.CharField(label=msgs['suggest_subtitle'],
                               required=False,
                               max_length=500,
                               help_text="500 characters max.",
                               error_messages={"max_length": msgs['error_max_chars']})  # 500

    type = forms.ModelChoiceField(queryset=ResourceTypes.objects.filter(lang_id=language_code),
                                  label=msgs['resource_type'],
                                  error_messages={'required': msgs['error_required']},
                                  widget=forms.Select(attrs={'onchange': 'toggleFields(this);'}),
                                  to_field_name='resource_type_id')

    description = forms.CharField(label=msgs['suggest_desc'], widget=forms.Textarea,
                                  max_length=1000,
                                  error_messages={"required": msgs['error_required'],
                                                  "max_length": msgs['error_max_chars']})  # 1000

    submitter_comments = forms.CharField(label=msgs['submitter_comments'], required=False, widget=forms.Textarea,
                                         max_length=1000)

    class Meta():
        def __init__(self, outer_instance):
            self.outer_instance = outer_instance
            self.msgs = outer_instance.msgs

        model = Resources
        fields = ['title', 'subtitle', 'description',
                  'type',
                  'book', 'isbn', 'journal', 'journal_issue',
                  'suggested_authors', 'suggested_editors',
                  'resource_link',
                  'group_link',
                  'date_created',
                  'submitter_name', 'submitter_email', 'submitter_comments']
        labels = {
            'resource_link': msgs['link'],
            'group_link': msgs['group_link'],
            'date_created': msgs['resourcecreated'],
            'suggested_authors': msgs['suggested_authors'],
            'suggested_editors': msgs['suggested_editors'],
            'submitter_name': msgs['submitter_name'],
            'submitter_email': msgs['submitter_email'],
            'book': msgs['book_name_for_chapter'],
            'isbn': 'ISBN',
            'journal': msgs['journal_name'],
            'journal_issue': msgs['journal_issue']
        }


class ReviewSuggestedResource(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__()
        msgs = kwargs.pop('msgs')
        resource_instance = kwargs.pop('instance', None)
        #language_code = kwargs.pop('language_code')
        self.msgs = msgs
        #self.language_code = language_code
        self.language_code = msgs['language_code']
        self.langs = kwargs.pop('langs')

    title = forms.CharField(label=msgs['suggest_title'],
                            max_length=255,
                            help_text="255 characters max.",
                            error_messages={"required": msgs['suggest_title'] + ' ' + msgs['error_required'],
                                            "max_length": msgs['error_max_chars']})  # 255

    subtitle = forms.CharField(label=msgs['suggest_subtitle'],
                               required=False,
                               max_length=500,
                               help_text="500 characters max.",
                               error_messages={"max_length": msgs['error_max_chars']})  # 500

    type = forms.ModelChoiceField(queryset=ResourceTypes.objects.filter(lang_id=language_code),
                                  label=msgs['resource_type'],
                                  error_messages={'required': msgs['resource_type'] + ' ' + msgs['error_required']},
                                  widget=forms.Select(attrs={'onchange': 'toggleFields(this);'}),
                                  to_field_name='resource_type_id')

    lang = forms.ModelChoiceField(queryset=Langs.objects.all(),
                                  label=msgs['lang'],
                                  error_messages={'required': msgs['lang'] + ' ' + msgs['error_required']},
                                  to_field_name='id')

    description = forms.CharField(label=msgs['suggest_desc'], widget=forms.Textarea,
                                  max_length=1000,
                                  error_messages={"required": msgs['suggest_desc'] + ' ' + msgs['error_required'],
                                                  "max_length": msgs['error_max_chars']})  # 1000

    submitter_comments = forms.CharField(label=msgs['submitter_comments'], required=False, widget=forms.Textarea,
                                         max_length=1000)

    resource_status = forms.ModelChoiceField(queryset=ResourceStatuses.objects.all(),
                                             label='STATUS',
                                             initial=ResourceStatuses.objects.get(pk=1),
                                             widget=forms.Select(),
                                             to_field_name='id')

    authors = forms.ModelMultipleChoiceField(
        queryset=Authors.objects.all(),
        label=mark_safe('Select Author(s)<br><i>Use [Shift] to select more than one. Select ----- for no author</i>'),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control authors-multiselect'}),
    )

    editors = forms.ModelMultipleChoiceField(
        queryset=Authors.objects.all(),
        label=mark_safe('Select Editor(s)<br><i>Use [Shift] to select more than one. Select ----- for no editors</i>'),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control authors-multiselect'}),
    )

    resource_file = forms.FileField(
        allow_empty_file=True,
        label='File',
        required=False
    )

    img = forms.ImageField(
        allow_empty_file=True,
        label='Resource image',
        required=False
    )

    class Meta:

        def __init__(self, outer_instance):
            self.outer_instance = outer_instance
            self.msgs = outer_instance.msgs

        model = Resources
        fields = ['resource_status', 'slug',
                  'title', 'subtitle', 'description',
                  'type', 'lang',
                  'book', 'isbn', 'journal', 'journal_issue',
                  'suggested_authors', 'authors',
                  'suggested_editors', 'editors',
                  'resource_link',
                  'group_link',
                  'date_created',
                  'submitter_name', 'submitter_email', 'submitter_comments',
                  'resource_file', 'img'
                  ]
        labels = {
            'resource_link': msgs['link'],
            'group_link': msgs['group_link'],
            'date_created': msgs['resourcecreated'],
            'suggested_authors': msgs['suggested_authors'],
            'suggested_editors': msgs['suggested_editors'],
            'submitter_name': msgs['submitter_name'],
            'submitter_email': msgs['submitter_email'],
            'book': msgs['book_name_for_chapter'],
            'isbn': 'ISBN',
            'journal': msgs['journal_name'],
            'journal_issue': msgs['journal_issue']
        }
