from wtforms import validators
from wtforms.validators import ValidationError, StopValidation

from .config import c
from uber.validations import TableInfo, BadgeExtras


TableInfo.field_validation.required_fields['prior_name'] = ("Please provide your prior table name.", 'has_prior_name')
TableInfo.field_validation.required_fields['license'] = ("Please provide your license number.", 'has_permit')


BadgeExtras.field_validation.validations['extra_donation']['minimum'] = validators.NumberRange(
    min=0, message="Superstar donation must be a number that is 0 or higher.")