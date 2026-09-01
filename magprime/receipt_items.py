from collections import defaultdict

from uber.config import c
from uber.decorators import receipt_calculation
from uber.receipt_items import Attendee


@receipt_calculation.Attendee
def swadge_addon_cost(attendee, new_attendee=None):
    from uber.custom_tags import format_currency

    if c.MERCH_TAX:
        tax = c.get_amount_extra_tax(c.SWADGE_PRICE)
        swadge_cost = c.SWADGE_PRICE + tax
        label_addon = f" (Includes {format_currency(c.SWADGE_PRICE)} base price + {format_currency(tax)} Sales Tax)"
    else:
        swadge_cost = c.SWADGE_PRICE
        label_addon = ""

    if not new_attendee and not attendee.swadge_addon:
        return
    elif not new_attendee:
        return (f"Add Swadge{label_addon}", swadge_cost * 100, 'swadge_addon')

    if attendee.swadge_addon == new_attendee.swadge_addon:
        return

    if not attendee.swadge_addon:
        return (f"Add Swadge{label_addon}", swadge_cost * 100, 'swadge_addon')
    elif not new_attendee.swadge_addon:
        return (f"Remove Swadge Add-On", swadge_cost * 100 * -1, 'swadge_addon')


Attendee.receipt_changes['swadge_addon'] = (swadge_addon_cost, c.MERCH)