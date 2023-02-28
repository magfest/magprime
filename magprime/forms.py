from wtforms import BooleanField
from markupsafe import Markup

from uber.config import c
from uber.forms import MagForm, SwitchInput
from uber.custom_tags import popup_link, email_to_link


@MagForm.form_mixin
class PersonalInfo:
    def onsite_contact_label(self):
        return 'MAGBuddy'


