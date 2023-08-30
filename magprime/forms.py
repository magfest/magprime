from markupsafe import Markup
from wtforms import (BooleanField, DecimalField, EmailField, Form, FormField,
                     HiddenField, SelectField, SelectMultipleField, IntegerField,
                     StringField, TelField, validators, TextAreaField)
from wtforms.validators import ValidationError, StopValidation
from wtforms.widgets import html_params
from pockets.autolog import log

from uber.config import c
from uber.forms import AddressForm, NumberInputGroup, MagForm, IntSelect, SwitchInput, HiddenIntField
from uber.custom_tags import popup_link, format_currency, pluralize, table_prices, email_to_link


class NumberInputWithChoices(NumberInputGroup):
    def __init__(self, choices=None, **kwargs):
        self.choices = choices
        super().__init__(**kwargs)

    def __call__(self, field, choices=None, **kwargs):
        choices = choices or self.choices
        field_id = kwargs.get('id', field.id)
        field_value = field.data
        field_readonly_or_disabled = kwargs.get('readonly', kwargs.get('disabled', False)) \
                                     or field.flags.disabled or field.flags.readonly
        if field_value not in [value for value, label in choices]:
            field_value = -1
        html = []
        first_opt = True

        for value, label in choices:
            choice_id = '{}-{}'.format(field_id, value)
            
            html.append(f'<input type="radio" class="btn-check" name="{field_id}-options" \
                        value="{value}" autocomplete="off" id="{choice_id}" \
                        {" disabled" if field_readonly_or_disabled else ""} \
                        {" checked" if value == field_value else ""}>')
            html.append(f'<label class="btn btn-outline-secondary{" rounded-start" if first_opt else ""}" for="{choice_id}">{label}</label>')
            first_opt = False

        html.append(super().__call__(field, **kwargs))
        html.append(f"""
                    <script type='text/javascript'>
                    $(function () {{
                        $("input[type=radio][name={field_id}-options]").on('change', function() {{
                            if($(this).val() == -1) {{
                                $('#{field_id}').focus();
                                return false;
                            }}

                            var currentVal = $('#{field_id}').val();
                            var newVal = $(this).val() == 0 ? '' : $(this).val();
                            if (currentVal != newVal) {{
                                $("#{field_id}").val(newVal).trigger('blur');
                            }}
                        }})
                    }});
                    </script>
                    """)
        
        return Markup(''.join(html))


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
    

@MagForm.form_mixin
class BadgeExtras:
    extra_donation = IntegerField('Superstar Donation', validators=[
        validators.NumberRange(min=0, message="Superstar donation must be a number that is 0 or higher.")
        ], widget=NumberInputWithChoices(choices=c.SUPERSTAR_DONATION_OPTS))
    
    def extra_donation_label(self):
        return Markup("Superstar Donation ({})".format(popup_link("../static_views/givingExtra.html", "Learn more")))
