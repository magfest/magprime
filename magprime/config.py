from uber.lib import parse_config
from collections import defaultdict
from datetime import timedelta

from uber.config import c, Config, dynamic
from uber.menu import MenuItem
from uber.utils import localized_now

config = parse_config(__file__)
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
