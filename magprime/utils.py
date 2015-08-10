from magprime import *

class SeasonEvent(Registry):
    instances = OrderedDict()

    def __init__(self, slug, **kwargs):
        assert re.match('^[a-z0-9_]+$', slug), 'Season Event sections must have separated_by_underscore names'
        for opt in ['url', 'location']:
            assert kwargs.get(opt), '{!r} is a required option for Season Event subsections'.format(opt)

        self.slug = slug
        self.name = kwargs['name'] or slug.replace('_', ' ').title()
        self.day = c.EVENT_TIMEZONE.localize(datetime.strptime(kwargs['day'], '%Y-%m-%d'))
        self.url = kwargs['url']
        self.location = kwargs['location']
        if kwargs['deadline']:
            self.deadline = c.EVENT_TIMEZONE.localize(datetime.strptime(kwargs['deadline'], '%Y-%m-%d'))
        else:
            self.deadline = (self.day - timedelta(days=7)).replace(hour=23, minute=59)

for _slug, _conf in c.SEASON_EVENTS.items():
    SeasonEvent.register(_slug, _conf)
