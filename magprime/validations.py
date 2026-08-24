from wtforms import validators
from wtforms.validators import ValidationError, StopValidation

from .config import c
from uber.validations import PersonalInfo, TableInfo, BadgeExtras, PanelInfo, PanelConsents, RoomLottery, \
    DietaryRestrictions, JobInfo, JobTemplateInfo, ignore_unassigned_and_placeholders


TableInfo.field_validation.required_fields['prior_name'] = ("Please provide your prior table name.", 'has_prior_name')
TableInfo.field_validation.required_fields['license'] = ("Please provide your license number.", 'has_permit')


@PersonalInfo.field_validation('cellphone')
@ignore_unassigned_and_placeholders
def cellphone_required(form, field):
    if not field.data and (not hasattr(form, 'copy_phone') or not form.copy_phone.data):
        if not form.no_cellphone.data and (form.model.is_dealer or form.model.staffing_or_will_be):
            raise ValidationError("Please provide a phone number.")
        if form.gets_emergency_texts.data:
            raise ValidationError("You must provide a phone number to sign up for the emergency text alert system.")


BadgeExtras.field_validation.validations['extra_donation']['minimum'] = validators.NumberRange(
    min=0, message="Superstar donation must be a number that is 0 or higher.")


PanelInfo.field_validation.required_fields['broadcast_title'] = ("Please provide a short title for digital displays.",
                                                                 'name', lambda x: len(x) > 40)
PanelInfo.field_validation.required_fields['broadcast_subtitle'] = "Please provide a one-line summary for digital displays."
PanelInfo.field_validation.required_fields['recording_details'] = ("Please provide details for how your panel should be recorded.",
                                                                   'need_recording_details')


PanelConsents.field_validation.required_fields['no_transfer'] = "Please acknowledge that your panelist badge cannot be transferred."


@RoomLottery.field_validation('room_type_preference')
def atrium_gaylord_only(form, field):
    if not field.data or not form.hotel_preference or not form.hotel_preference.data:
        return
    
    if (c.HOTEL_LOTTERY_KING_ATRIUM in field.data or c.HOTEL_LOTTERY_DOUBLE_ATRIUM in field.data
            ) and c.HOTEL_LOTTERY_GAYLORD not in form.hotel_preference.data:
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