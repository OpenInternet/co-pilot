import string
from flask.ext.login import LoginManager
from copilot import app
from copilot import bcrypt, db
from flask.ext.login import UserMixin
from copilot.models.config import get_config_file

#stat logging
import logging
log = logging.getLogger(__name__)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view =  "login"

@login_manager.user_loader
def load_user(userid):
    _user = get_trainer()
    if not _user:
        log.info("No trainer object found. Assuming a new user.")
    return _user

def get_trainer():
    """Only allow one trainer account. """
    _trainer = Trainer.query.first()
    if not _trainer:
        log.info("No trainer found.")
    return _trainer

def get_ap_status():
    trainer = get_trainer()
    ap = {}
    current_ap = False
    try:
        current_ap = trainer.ap_name
    except:
        log.warn("FIX THIS SOON (function get_ap_status)")
    if current_ap:
        ap['status'] = "on"
        ap['value'] = current_ap
    else:
        ap['status'] = "off"
        ap['value'] = "NONE"
    return ap

class Base(db.Model):

    __abstract__  = True

    id            = db.Column(db.Integer, primary_key=True)
    date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(),
                                           onupdate=db.func.current_timestamp())

class Trainer(Base, UserMixin):
    """ The trainer (SINGLE user) model"""

    __tablename__ = 'trainer'

    #DataBase Values
    # Ensure Solo account
    _solo  = db.Column(db.Boolean,  default=True, nullable=False)
    # AP Name
    _ap_name   = db.Column(db.String(128),  nullable=False)
    # AP password
    _ap_password = db.Column(db.String(192),  nullable=False)
    # Trainer password
    _password = db.Column(db.String(192),  nullable=False)
    _current = db.Column(db.String(192),  nullable=True)

    def __init__(self, trainer_pass, ap_name="copilot", ap_password="copilot"):
        log.debug("Creating new trainer object.")
        log.debug("Trainer AP: {0}".format(ap_name))
        self.password = trainer_pass
        self.ap_name = ap_name
        self.ap_password = ap_password
        self.solo = True
        self.current = False

    @property
    def solo(self):
        return self._solo

    @solo.setter
    def solo(self, val=True):
        self._solo = True

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, plaintext):
        self._password = bcrypt.generate_password_hash(plaintext)

    @property
    def current(self):
        return self._current

    @current.setter
    def current(self, plaintext):
        self._current = plaintext

    def is_correct_password(self, plaintext):
        return bcrypt.check_password_hash(self._password, plaintext)

    @property
    def ap_password(self):
        return self._ap_pass

    @password.setter
    def ap_password(self, plaintext):
        if (8 < len(str(plaintext)) <= 63 and
            all(char in string.printable for char in plaintext)):
            self._ap_password = plaintext
        else:
            print(plaintext)
            raise ValueError("Access Point passwords must be between 8 and 63 characters long and use only printable ASCII characters.")

    @property
    def ap_name(self):
        return self._ap_name

    @ap_name.setter
    def ap_name(self, name):
        if 0 < len(str(name)) <= 31:
            self._ap_name = name
        else:
            raise ValueError("Access Point names must be between 1 and 31 characters long.")

    def write_ap_config(self):
        #TODO Replace with config obj
        AP_CONFIG = get_config_file("create_ap")
        with open(AP_CONFIG, 'w') as config_file:
            config_file.write("wlan0 eth0 {0} {1}".format(self._ap_name, self._ap_password))

    def __repr__(self):
        return '<Ap Name %r Solo %r>' % (self.ap_name, self.solo)