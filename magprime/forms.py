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


class NumberInputGroupChoices(NumberInputGroup):
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
class GroupInfo:
    def tables_desc(self):
        return "Amount of 6ft x 30in tables requested. MAGFest DOES NOT sell booth spaces, only tables."


@MagForm.form_mixin
class TableInfo:
    has_prior_name = BooleanField("I have run a table under a different name at one of the past two in-person Super MAGFest events.")
    prior_name = StringField("Prior Table Name")
    has_permit = BooleanField(Markup("I already have a <strong>permanent</strong> Maryland Traders or Sellers Permit."))
    license = StringField("License Number",
                          description="Please enter the license number for your Maryland Traders or Sellers Permit.")

    def website_desc(self):
        return Markup("The link to your main portfolio. Please include additional links to social media accounts or "
                      "additional places to view your items in the <em>What do you sell?</em> box below.")

    def wares_desc(self):
        return "You must include links to what you sell or a portfolio otherwise you will be automatically declined."
    
    def special_needs_desc(self):
        return Markup("Location requests, people you'd like to be near/away from, or any other needs we should "
                      "be aware of. While we take requests into account when placing tables, there are no "
                      "guarantees we can accommodate any requests.")


@MagForm.form_mixin
class PersonalInfo:
    def onsite_contact_label(self):
        return "MAGBuddy"


@MagForm.form_mixin
class BadgeExtras:
    extra_donation = IntegerField('Superstar Donation', widget=NumberInputGroupChoices(choices=c.SUPERSTAR_DONATION_OPTS))
    
    def extra_donation_label(self):
        return Markup("Superstar Donation ({})".format(popup_link("https://super.magfest.org/superstars", "Learn more")))


@MagForm.form_mixin
class AdminBadgeExtras:
    extra_donation = IntegerField('Superstar Donation', widget=NumberInputGroup())


@MagForm.form_mixin
class PanelistInfo:
    def display_name_desc(self):
        return "The personal or group name to show on the schedule to let people know who is hosting the panel. Leave this field blank if you do not want a name displayed on the schedule or on digital displays at the event."


@MagForm.form_mixin
class PanelInfo:
    broadcast_title = StringField("Broadcast Title",
                                  description="The short version of this panel's title that will appear on screens and digital signage. Max 40 characters.")
    broadcast_subtitle = StringField("Broadcast Subtitle",
                                     description="A one-line summary that appears below your panel's title on digital displays. Max 100 characters.")
    magscouts_opt_in = SelectField("Do you want your content to be highlighted by the MAGScouts program?", coerce=int,
                                   choices=c.PANEL_MAGSCOUTS_OPTS)
    
    def public_description_label(self):
        return Markup('Guidebook Description <span class="popup"><a href="../static_views/guidebook_html.html" target="_blank"><i class="fa fa-question-circle" aria-hidden="true"></i> HTML Guide</a></span>')


@MagForm.form_mixin
class RoomLottery:
    def wants_ada_desc(self):
        return """Checking this box does not guarantee you a room. It lets MAGFest know that the room you may receive should meet your needs
               as noted below. If you do not receive a room in the initial lottery, rooms will continue to be assigned as room cancellations
               come in. Your information below remains throughout the lottery assignment process."""

    def earliest_checkin_date_label(self):
        return "Check-In Date"
    
    def latest_checkout_date_label(self):
        return "Check-Out Date"
