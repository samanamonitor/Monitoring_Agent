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
    debug=FloatField('debug')
    upload_interval=FloatField('upload_interval', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, hash_key, *args, **kwargs):
        super(EditConfigField, self).__init__(*args, **kwargs)
        self.hash_key = hash_key

    def toDict(self):
        return {
            'config_interval' : self.config_interval.data,
            'FileVersionMS' : self.FileVersionMS.data,
            'cpu_interval' : self.cpu_interval.data,
            'FileVersionLS' : self.FileVersionLS.data,
            'data_url' : self.data_url.data,
            'num' : self.num.data,
            'MonitorPath' : self.MonitorPath.data,
            'debug' : self.debug.data,
            'upload_interval' : self.upload_interval.data,
        }
        