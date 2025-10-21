from sqlalchemy import or_
from uber.config import c
from uber.decorators import all_renderable, csv_file, render, site_mappable
from uber.models import Attendee, FoodRestrictions, GuestCharity


@all_renderable()
class Root:
    def food_restrictions(self, session):
        all_fr = session.query(FoodRestrictions).all()
        guests = session.query(Attendee).filter_by(badge_type=c.GUEST_BADGE).count()
        volunteers = len([
            a for a in session.query(Attendee).filter_by(staffing=True).all()
            if a.badge_type == c.STAFF_BADGE or a.weighted_hours or not a.takes_shifts])

        return {
            'guests': guests,
            'volunteers': volunteers,
            'notes': filter(bool, [getattr(fr, 'freeform', '') for fr in all_fr]),
            'standard': {
                c.FOOD_RESTRICTIONS[getattr(c, category)]: len([fr for fr in all_fr if getattr(fr, category)])
                for category in c.FOOD_RESTRICTION_VARS
            },
        }

    @csv_file
    @site_mappable(download=True)
    def food_eligible(self, out, session):
        header = ['Name', 'Badge Type', 'Badge #', 'Eligible', 'Restrictions?']
        ordered_food_restrictions = []
        for val, label in c.FOOD_RESTRICTIONS.items():
            ordered_food_restrictions.append(str(val))
            header.append(label)
        
        header.append('Other Restrictions')
        out.writerow(header)

        base_query = session.attendees_with_badges().filter(Attendee.is_unassigned == False)

        guests = base_query.filter_by(badge_type=c.GUEST_BADGE).all()
        volunteers = [a for a in base_query.filter_by(staffing=True).all() if a.badge_type == c.STAFF_BADGE
                    or a.weighted_hours or not a.takes_shifts]
        
        for a in volunteers + guests:
            row = [a.full_name, a.badge_type_label, a.badge_num,
                   'Yes' if a.badge_type in [c.STAFF_BADGE, c.GUEST_BADGE] or (
                       a.weighted_hours > c.HOURS_FOR_FOOD and a.worked_hours) else 'No',
                       'Yes' if a.food_restrictions and a.food_restrictions.standard else 'No']
            for key in ordered_food_restrictions:
                row.append("Yes" if a.food_restrictions and key in a.food_restrictions.standard else "No")
            row.append(a.food_restrictions.freeform if a.food_restrictions else "")
            out.writerow(row)