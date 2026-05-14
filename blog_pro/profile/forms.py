from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField ,PasswordField ,SubmitField, EmailField, BooleanField
from wtforms.validators import data_required, Length, EqualTo, ValidationError
from blog_pro.models import User


class UpdateAccount(FlaskForm) :
    username = StringField("Username", validators=[data_required(),Length(3,10)])
    email = EmailField("Email", validators=[data_required()])
    file_field = FileField("Updadte profile picture", validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField("Update")

    def validate_username(self, username) :
        user = User.query.filter_by(username=username.data).first()
        if user and current_user.username != username.data :
            raise ValidationError("That username has already choosen")

    def validate_email(self, email) :
        user = User.query.filter_by(email=email.data).first()
        if user and current_user.email != email.data :
            raise ValidationError("That email has already choosen") 
        
    def validate_submit(self, submit):
        if self.email.data == current_user.email and self.username.data== current_user.username and not self.file_field.data  :
            raise ValidationError("No Change has been done")

