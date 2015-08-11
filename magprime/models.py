from magprime import *


class SeasonPassTicket(MagModel):
    fk_id    = Column(UUID)
    slug     = Column(UnicodeText)

    @property
    def fk(self):
        return self.session.season_pass(self.fk_id)


class PrevSeasonSupporter(MagModel):
    first_name = Column(UnicodeText)
    last_name  = Column(UnicodeText)
    email      = Column(UnicodeText)

    email_model_name = 'attendee'  # used by AutomatedEmail code

    _repr_attr_names = ['first_name', 'last_name', 'email']
