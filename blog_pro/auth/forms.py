from flask_wtf import FlaskForm
from wtforms import StringField ,PasswordField ,SubmitField, EmailField, BooleanField
from wtforms.validators import data_required, Length, EqualTo, ValidationError 
from blog_pro.models import User


class RegistrationForm(FlaskForm):
    username = StringField("Username",validators=[data_required("hhhh"), Length(min=3,max=10)])
    email = EmailField("Email",validators=[data_required()])
    password = PasswordField("Password",validators=[data_required()])
    confirm_password = PasswordField("Comfirm password", validators=[data_required(), EqualTo("password")])
    submit = SubmitField("Sign Up")

    def validate_username(self, username) :
        user = User.query.filter_by(username=username.data).first()
        if user :
            raise ValidationError("That username has already choosen")

    def validate_email(self, email) :
        user = User.query.filter_by(email=email.data).first()
        if user :
            raise ValidationError("That email has already choosen") 

class LoginForm(FlaskForm) :
    email = EmailField("Email",validators=[data_required()])
    password = PasswordField("Password",validators=[data_required(),Length(min=3,max=8)])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")

    # def validate_email(self,email) :
    #     user = User.query.filter_by(email=email.data).first()

    #     if not user :
    #         raise ValidationError("")
    
    # def validate_password(self,password) :
    #     user = User.query.filter_by(email=self.email.data).first()
    #     print(password.data)
    #     if not user :
    #         raise ValidationError("The email is wrong")
        
    #     elif not bcrypt.check_password_hash(user.password,password.data) :
    #         print(user.password)
    #         raise ValidationError("Wrong passwprd entered")

        