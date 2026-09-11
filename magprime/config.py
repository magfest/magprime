from collections import defaultdict
from datetime import timedelta
from pathlib import Path

from uber.config import c, Config, dynamic, parse_config
from uber.menu import MenuItem
from uber.utils import localized_now

config = parse_config("magprime", Path(__file__).parents[0])
c.include_plugin_config(config)

@Config.mixin
class ExtraConfig:
    @property
    @dynamic
    def SEASON_BADGE_PRICE(self):
        return self.BADGE_PRICE + self.SEASON_LEVEL

    @property
    def SEASON_EVENTS(self):
        return config['season_events']
    
    @property
    def SUPERSTAR_MINIMUM(self):
        return list(c.SUPERSTAR_DONATIONS.keys())[1]
    
    @property
    def EXTRA_ADDON_STATS(self):
        return [
            (f"Number of ${self.SWADGE_PRICE} swadge add-ons purchased", self.SWADGE_ADDON_COUNT)
        ]
    
    @property
    def SWADGE_ADDON_COUNT(self):
        from uber.models import Session, Attendee

        with Session() as session:
            count = session.query(Attendee).filter(
                Attendee.swadge_addon == True, Attendee.amount_extra == c.SUPPORTER_LEVEL,
                ~Attendee.badge_status.in_([c.INVALID_GROUP_STATUS, c.INVALID_STATUS,
                                            c.IMPORTED_STATUS, c.REFUNDED_STATUS])
                ).count()
        return count

    @property
    def PREREG_BADGE_TYPES(self):
        types = [self.ATTENDEE_BADGE, self.PSEUDO_DEALER_BADGE]
        if c.AGE_GROUP_CONFIGS[c.UNDER_13]['can_register']:
            types.append(self.CHILD_BADGE)
        for reg_open, badge_type in [(self.BEFORE_GROUP_PREREG_TAKEDOWN, self.PSEUDO_GROUP_BADGE)]:
            if reg_open:
                types.append(badge_type)
        return types

    @property
    def DEALER_REG_OPEN(self):
        return self.AFTER_DEALER_REG_START and self.BEFORE_DEALER_REG_SHUTDOWN and not self.DEALER_REG_SOFT_CLOSED
