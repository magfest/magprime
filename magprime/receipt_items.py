from collections import defaultdict

from uber.config import c
from uber.decorators import receipt_calculation
from uber.receipt_items import Attendee


@receipt_calculation.Attendee
def swadge_addon_cost(attendee, new_attendee=None):
    if not new_attendee and not attendee.swadge_addon:
        return
    elif not new_attendee:
        return (f"Add Swadge", c.SWADGE_PRICE * 100, 'swadge_addon')

    if attendee.swadge_addon == new_attendee.swadge_addon:
        return

    if not attendee.swadge_addon:
        return (f"Add Swadge", c.SWADGE_PRICE * 100, 'swadge_addon')
    elif not new_attendee.swadge_addon:
        return (f"Remove Swadge Add-On", c.SWADGE_PRICE * 100 * -1, 'swadge_addon')


Attendee.receipt_changes['swadge_addon'] = (swadge_addon_cost, c.MERCH)