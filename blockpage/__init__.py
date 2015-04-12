# -*- coding: utf-8 -*-

#import flask
from flask import Flask

# If we set instance_relative_config=True when we create our app with the Flask() call, app.config.from_pyfile() will load the specified file from the instance/ directory.
blockpage = Flask('blockpage', instance_relative_config=True)
blockpage.config.from_object('config')
# Load configuration variables from an instance folder.
blockpage.config.from_pyfile('config.py')

#Putting the import at the end avoids the circular import error.
from blockpage import models
from blockpage import controllers
from blockpage import views