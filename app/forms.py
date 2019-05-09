from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField
from wtforms.validators import DataRequired

class EditConfigField(FlaskForm):
    config_interval=FloatField('config_interval', validators=[DataRequired()])
    FileVersionMS=FloatField('FileVersionMS', validators=[DataRequired()])
    # logs
    cpu_interval=FloatField('cpu_interval', validators=[DataRequired()])
    FileVersionLS=FloatField('FileVersionLS', validators=[DataRequired()])
    data_url=StringField('data_url', validators=[DataRequired()])
    num=FloatField('num', validators=[DataRequired()])
    MonitorPath=StringField('MonitorPath', validators=[DataRequired()])
    debug=FloatField('debug', validators=[DataRequired()])
    upload_interval=FloatField('upload_interval', validators=[DataRequired()])

    def __init__(self, hash_key, *args, **kwargs):
        super(EditConfigField, self).__init__(*args, **kwargs)
        self.hash_key = hash_key