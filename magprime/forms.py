from markupsafe import Markup
from wtforms import (BooleanField, DecimalField, EmailField, Form, FormField,
                     HiddenField, SelectField, SelectMultipleField, IntegerField,
                     StringField, TelField, validators, TextAreaField)
from wtforms.validators import ValidationError, StopValidation
from pockets.autolog import log

from uber.config import c
from uber.forms import AddressForm, MultiCheckbox, MagForm, IntSelect, SwitchInput, DollarInput, HiddenIntField
from uber.custom_tags import popup_link, format_currency, pluralize, table_prices


@MagForm.form_mixin
class TableInfo:
    has_prior_name = BooleanField("I have run a table under a different name at one of the past two in-person Super MAGFest events.")
    prior_name = StringField("Prior Table Name", validators=[
        validators.InputRequired("Please provide your prior table name.")
    ])
    has_permit = BooleanField(Markup("I already have a <strong>permanent</strong> Maryland Traders or Sellers Permit."))
    license = StringField("License Number", validators=[
        validators.InputRequired("Please provide your license number.")
    ], description="Please enter the license number for your Maryland Traders or Sellers Permit.")

    def get_optional_fields(self, group, is_admin=False):
        optional_fields = self.super_get_optional_fields(group)

        if not self.has_prior_name.data:
            optional_fields.append("prior_name")

        if not group.has_permit:
            optional_fields.append("license")
        
        return optional_fields
    
    def website_desc(self):
        return Markup("The link to your main portfolio. Please include additional links to social media accounts or \
                      additional places to view your items in the <em>What do you sell?</em> box below.")