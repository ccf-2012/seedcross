from email.policy import default
from django import forms
from .models import CLIENT_TYPES, INDEXER_TYPES
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, HTML, Div
from crispy_forms.bootstrap import PrependedText


class ParamSettingForm(forms.Form):
    client_type = forms.ChoiceField(label='Type', choices=CLIENT_TYPES)
    client_host = forms.GenericIPAddressField(label='Host')
    client_port = forms.IntegerField(label='Port')
    client_username = forms.CharField(label='Username', required=False)
    client_password = forms.CharField(
        label='Password', widget=forms.PasswordInput(render_value=True), required=False)
    include_cjk = forms.BooleanField(label='Search CJK title',  required=False)
    category_indexers = forms.BooleanField(label='Category indexers',  required=False)
    indexer_movie = forms.CharField(label='Movie/TV indexers',  required=False)
    indexer_tv = forms.CharField(label='Movie/TV indexers',  required=False)
    indexer_music = forms.CharField(label='Music indexers',  required=False)
    indexer_ebook = forms.CharField(label='eBook indexers',  required=False)
    indexer_audio = forms.CharField(label='Audio indexers',  required=False)
    indexer_other = forms.CharField(label='Other(Unknown) indexers',  required=False)
    jackett_prowlarr = forms.ChoiceField(label='Jackett or Prowlarr', choices=INDEXER_TYPES)
    jackett_url = forms.URLField(label='Jackett/Prowlarr Url')
    jackett_api_key = forms.CharField(label='Jackett/Prowlarr Api key')
    jackett_trackers = forms.CharField(label='Tracker / Indexer',  required=False)
    fc_count = forms.IntegerField(label='Flow control: Count limit')
    fc_interval = forms.IntegerField(label='Flow control: Interval')
    cyclic_reload = forms.BooleanField(label='Cycle run',  required=False)
    reload_interval_min = forms.IntegerField(label='Cycle run interval (minutes)', required=False)
    max_size_difference = forms.IntegerField(label='Max size difference (bytes) when compare torrents.', required=False)
    map_from_path = forms.CharField(label='Map From: Download client(QB/Tr/De) path', required=False)
    map_to_path = forms.CharField(label='Map to: seedcross path', required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.form_class = 'form-horizontal'
        # self.helper.label_class = 'col-lg-2'
        # self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(
            HTML("""
            <p><strong>Download Client Setting</strong></p>
            """),
            Field('client_type'), 
            Row(
                Column(Field('client_host',
                             placeholder='only IP addr'),
                       css_class='form-group col-md-8 mb-0'
                       ),
                Column(PrependedText('client_port', ':', placeholder="Port"),
                       css_class='form-group col-md-4 mb-0'
                       ),
                # Column('client_port', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'),
            Row(Column('client_username',
                       css_class='form-group col-md-6 mb-0'
                       ),
                Column('client_password',
                       css_class='form-group col-md-6 mb-0'
                       ),
                css_class='form-row'),

            HTML("""
            <p><strong>Jackett/Prowlarr Setting</strong></p>
            """),
            Field('jackett_prowlarr',
                  placeholder='Jackett or Prowlarr'),
            Field('jackett_url',
                  placeholder='ex. http://jackett/prowlarr.server.ip:9117/'),
            Field('jackett_api_key',
                  placeholder='copy from jackett/prowlarr web ui'),
            Field('jackett_trackers',
                  placeholder='leave blank to search all configured indexers'),
            HTML("""
            <p><strong>Search options</strong></p>
            """),
            # TODO: shoud this be configurable
            Field('max_size_difference', placeholder="max size difference (in bytes)"),
            Field('include_cjk'),
            Field('category_indexers', id='check_id'),
            Div(
                Field('indexer_movietv'),
                Field('indexer_music'),
                Field('indexer_ebook'),
                Field('indexer_audio'),
                Field('indexer_other'),
                css_id='CategoryIndexers', 
            ), 
            HTML("""
            <p><strong>Flow Control Setting</strong></p>
            """),
            Row(Column(Field('fc_count'),
                       css_class='form-group col-md-6 mb-0'),
                Column(Field('fc_interval'),
                       css_class='form-group col-md-6 mb-0'),
                css_class='form-row'),
            HTML("""
            <p><strong>Cycle run options</strong></p>
            """),
            Field('cyclic_reload'),
            Field('reload_interval_min'),
            HTML("""
            <p><strong>Fix options</strong> (required: your download client is running on the same machine as seedcross)</p>
            """),
            Row(Column(Field('map_from_path'),
                       css_class='form-group col-md-6 mb-0'),
                Column(Field('map_to_path'),
                       css_class='form-group col-md-6 mb-0'),
                css_class='form-row'),
        )
        self.helper.add_input(
            Submit('submit', 'Save Settings', css_class='btn-primary'))
        self.helper.form_method = 'POST'

    # helper = FormHelper()
    # # helper.form_class = 'form-horizontal'
    # # helper.label_class = 'col-lg-2'
    # # helper.field_class = 'col-lg-8'
    # helper.layout = Layout(

    #     'jackett_url',
    #     'jackett_api_key',
    #     Row(
    #     'fc_count',
    #     'fc_interval',
    #     ),
    #     'client_type',
    #     Row(
    #     'client_host',
    #     'client_port',
    #     ),
    #     Row(
    #     'client_username',
    #     'client_password',
    #     ),

    #     Submit('submit', 'Submit'),
    # )

    # class Meta:
    #     fields = ['clienttype', 'client_host', 'client_port', 'client_username', 'client_password', 'jackett_url']
