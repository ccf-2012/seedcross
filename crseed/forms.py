from django import forms
from .models import CLIENT_TYPES
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, HTML, Div
from crispy_forms.bootstrap import PrependedText


class ParamSettingForm(forms.Form):
    client_type = forms.ChoiceField(label='Type', choices=CLIENT_TYPES)
    client_host = forms.GenericIPAddressField(label='Host')
    client_port = forms.IntegerField(label='Port')
    client_username = forms.CharField(label='Username')
    client_password = forms.CharField(
        label='Password', widget=forms.PasswordInput(render_value=True))

    jackett_url = forms.URLField(label='Jackett Url')
    jackett_api_key = forms.CharField(label='Jackett Api key')
    jackett_trackers = forms.CharField(label='Trackers / Indexers',  required=False)
    fc_count = forms.IntegerField(label='Flow control: Count limit')
    fc_interval = forms.IntegerField(label='Flow control: Interval')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML("""
            <p><strong>Download Client Setting</strong></p>
            """),
            'client_type',
            Row(
                Column(Field('client_host',
                             placeholder='IP addr of the download client'),
                       css_class='form-group col-md-8 mb-0'),
                Column(PrependedText('client_port', ':', placeholder="Port"),
                       css_class='form-group col-md-4 mb-0'),
                # Column('client_port', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'),
            Row(Column('client_username',
                       css_class='form-group col-md-6 mb-0'),
                Column('client_password',
                       css_class='form-group col-md-6 mb-0'),
                css_class='form-row'),
            HTML("""
            <p><strong>Jackett Setting</strong></p>
            """),
            Field('jackett_url',
                  placeholder='ex. http://jackett.server.ip:9117/'),
            Field('jackett_api_key',
                  placeholder='get it from your Jackett web ui'),
            Field('jackett_trackers',
                  placeholder='leave blank to search all indexers in Jackett '),
            HTML("""
            <p><strong>Flow Control Setting</strong></p>
            """),
            Row(Column(Field('fc_count',
                             placeholder='count limit for one click'),
                       css_class='form-group col-md-6 mb-0'),
                Column(Field('fc_interval',
                             placeholder='seconds between 2 queries'),
                       css_class='form-group col-md-6 mb-0'),
                css_class='form-row'))
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
