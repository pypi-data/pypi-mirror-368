from flask_wtf.file import DataRequired
from app.validators.base import BaseForm as Form
from wtforms import StringField, FieldList, FormField



class xxxxxDictInfoForm(Form):
    xxxxx = StringField('xxxxx', validators=[DataRequired(message="order_id is required")])


class UpdateDataFileValidatorsForm(Form):
    result = FieldList(
        FormField(xxxxxDictInfoForm),  # 使用 FormField 包装子表单
        min_entries=1,
        validators=[DataRequired(message='xxx 不允许为空')]
    )
