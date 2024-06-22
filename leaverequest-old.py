# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from email.mime.text import MIMEText
import smtplib
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
import os
from datetime import datetime
