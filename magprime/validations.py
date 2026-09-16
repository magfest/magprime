from wtforms import validators
from wtforms.validators import ValidationError, StopValidation

from .config import c
from uber.validations import PersonalInfo, PreregOtherInfo, StaffingInfo, TableInfo, BadgeExtras, PanelInfo, PanelConsents, RoomLottery, \
    DietaryRestrictions, JobInfo, JobTemplateInfo, ignore_unassigned_and_placeholders


TableInfo.field_validation.required_fields['prior_name'] = ("Please provide your prior table name.", 'has_prior_name')
TableInfo.field_validation.required_fields['license'] = ("Please provide your license number.", 'has_permit')


@PersonalInfo.field_validation('cellphone')
@ignore_unassigned_and_placeholders
def cellphone_required(form, field):
    if form.model.birthdate and form.model.age_group_conf['consent_form']:
        return

    if not field.data and (not hasattr(form, 'copy_phone') or not form.copy_phone.data):
        if not form.no_cellphone.data and (form.model.is_dealer or form.model.staffing_or_will_be):
            raise ValidationError("Please provide a phone number.")
        if form.gets_emergency_texts.data:
            raise ValidationError("You must provide a phone number to sign up for the emergency text alert system.")


StaffingInfo.field_validation.required_fields.update({
    'requested_depts_ids': (
        'Please select at least one department to volunteer for, or check "Anywhere".',
        'requested_depts_ids',
        lambda x: not x.form.is_admin and x.form.model.staffing_or_will_be and len(c.PUBLIC_DEPARTMENT_OPTS_WITH_DESC) > 1 \
            and not x.form.model.assigned_depts_ids and not x.form.other_requested_dept.data),
    })


StaffingInfo.field_validation.validations['active_times']['optional'] = validators.Optional()


StaffingInfo.field_validation.validations['request_depts_experience']['length'] = validators.Length(
    max=500, message=f"Please describe your prior experience in under 500 characters.")


BadgeExtras.field_validation.validations['extra_donation']['minimum'] = validators.NumberRange(
    min=0, message="Superstar donation must be a number that is 0 or higher.")


@BadgeExtras.new_or_changed('swadge_addon')
def upgrade_sold_out(form, field):
    if form.is_admin:
        return

    if field.data and not c.SWADGE_ADDON_AVAILABLE:
        raise ValidationError(f"The ${c.SWADGE_PRICE} swadge add-on is sold out.")


PanelInfo.field_validation.required_fields.update({
    'broadcast_title': ("Please provide a short title for digital displays.", 'name', lambda x: len(x) > 40),
    'broadcast_subtitle': "Please provide a one-line summary for digital displays.",
    'recording_details': ("Please provide details for how your panel should be recorded.", 'need_recording_details'),
})


PanelConsents.field_validation.required_fields['no_transfer'] = "Please acknowledge that your panelist badge cannot be transferred."


@RoomLottery.field_validation('room_type_preference')
def atrium_gaylord_only(form, field):
    if not field.data or not form.hotel_preference or not form.hotel_preference.data:
        return

    # Hotels and room types are database rows now, so match them by name.
    # If either set is empty for this event's data, the rule is a no-op.
    def ids_named(choices, term):
        return {val for val, label in (choices or [])
                if term in (label.get('name', '') if isinstance(label, dict) else str(label)).lower()}

    atrium_types = ids_named(field.choices, 'atrium')
    gaylord_hotels = ids_named(form.hotel_preference.choices, 'gaylord')
    if (atrium_types.intersection(field.data)
            and gaylord_hotels and not gaylord_hotels.intersection(form.hotel_preference.data)):
        raise ValidationError("Atrium rooms are only available at the Gaylord National Harbor.")


DietaryRestrictions.field_validation.required_fields = {
    'has_allergies': ("Please let us know if you have any allergies or dietary restrictions.",
                      'has_allergies', lambda x: x.raw_data == []),
    'standard': ("Please select one or more dietary restrictions, or 'Other'.",
                 'has_allergies'),
    'freeform': ("Please list each of your other allergies, separated by commas.",
                 'standard', lambda x: c.OTHER in x.data),
}


JobInfo.field_validation.required_fields['slots'] = "The minimum number of job slots is 1."
JobTemplateInfo.field_validation.required_fields['min_slots'] = "Please set a minimum of at least 1 job slot."