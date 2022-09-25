from sideboard.lib import parse_config, request_cached_property
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
    def FORMATTED_DONATION_DESCRIPTIONS(self):
        """
        A list of the donation descriptions, formatted for use on attendee-facing pages.
        
        This does NOT filter out unavailable kick-ins so we can use it on attendees' confirmation pages
        to show unavailable kick-ins they've already purchased. To show only available kick-ins, use
        PREREG_DONATION_DESCRIPTIONS.
        """
        donation_list = self.DONATION_TIER_DESCRIPTIONS.items()

        donation_list = sorted(donation_list, key=lambda tier: tier[1]['price'])

        # add in all previous descriptions.  the higher tiers include all the lower tiers
        for entry in donation_list:
            all_desc_and_links = [(entry[1]['description'], entry[1]['link'])]

            # maybe slight hack. descriptions and links are separated by '|' characters so we can have multiple
            # items displayed in the donation tiers.  in an ideal world, these would already be separated in the INI
            # and we wouldn't have to do it here.
            entry[1]['all_descriptions'] = []
            for item in all_desc_and_links:
                descriptions = item[0].split('|')
                links = item[1].split('|')
                entry[1]['all_descriptions'] += list(zip(descriptions, links))

        return [dict(tier[1]) for tier in donation_list]

    @property
    def DEALER_REG_OPEN(self):
        return self.AFTER_DEALER_REG_START and self.BEFORE_DEALER_REG_SHUTDOWN and not self.DEALER_REG_SOFT_CLOSED
