from django.forms.widgets import Input


class S3SelectWidget(Input):
    input_type = 'text'
    template_name = 'templates/s3_select.html'




