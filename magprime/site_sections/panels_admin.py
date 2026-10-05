import logging

from uber.config import c
from uber.decorators import ajax, all_renderable, csrf_protected, csv_file, render

log = logging.getLogger(__name__)


@all_renderable()
class Root:
    @csv_file
    def everything(self, out, session):
        dept_col = ['Department'] if len(c.PANELS_DEPT_OPTS_WITH_DESC) > 1 else []
        rating_col = ['Rating'] if len(c.PANEL_RATING_OPTS) > 1 else []
        content_cols = ['Mature Content', 'Opted in to MAGScouts'] if len(c.PANEL_CONTENT_OPTS) > 1 else []
        if len(c.LIVESTREAM_OPTS) > 2:
            recording_cols = ['Recording or Livestreaming OK']
        elif c.CAN_LIVESTREAM:
            recording_cols = ['Recording OK', 'Livestreaming OK']
        else:
            recording_cols = ['Recording OK']
        
        header_row = ['Panel Name'] + dept_col + [
            'Type of Panel', 'Broadcast Title', 'Broadcast Subtitle',
            'Description', 'Guidebook Description'
            ] + rating_col + content_cols + [
            'Expected Length', 'Reason for Length', 'Noise Level'
            ] + recording_cols + ['Recording Details',
            'Special Table Set-up', 'Upfront Cost and Materials',
            'Unavailability', 'After 9 PM?', 'Before 11 AM or after 11 PM?',
            'Technical Needs', 'Loud Environment Requested',
            'Extra Info for Internal Use', 'Panelist Is Bringing', 'Affiliations',
            'Past Attendance', 'Applied', 'Panelists']
        out.writerow(header_row)

        for app in session.panel_apps():
            panelists = []
            for panelist in app.applicants:
                panelists.extend([
                    panelist.full_name,
                    panelist.email,
                    panelist.cellphone
                ])
            dept = [app.department_name] if len(c.PANELS_DEPT_OPTS_WITH_DESC) > 1 else []
            rating = [app.rating_label] if len(c.PANEL_RATING_OPTS) > 1 else []
            content = [' / '.join(app.granular_rating_labels),
                           'N/A' if app.magscouts_opt_in == c.NO_CHOICE else app.magscouts_opt_in_label] if len(c.PANEL_CONTENT_OPTS) > 1 else []
            if len(c.LIVESTREAM_OPTS) > 2:
                recording = [app.livestream_label]
            elif c.CAN_LIVESTREAM:
                recording = [app.record_label, app.livestream_label]
            else:
                recording = [app.record_label]

            row = [app.name] + dept + [
                app.other_presentation if app.presentation == c.OTHER else app.presentation_label,
                app.broadcast_title, app.broadcast_subtitle,
                app.description, app.public_description] + rating + content + [
                app.length_text if app.length == c.OTHER or app.length_text else app.length_label,
                app.length_reason if app.length == c.OTHER or app.length_text else 'N/A',
                app.noise_level_label] + recording + [app.recording_details,
                app.tables_desc, app.cost_desc, app.unavailable, app.after_9pm, app.extreme_times,
                ' / '.join(app.tech_needs_labels) + (' / ' if app.other_tech_needs else '') + app.other_tech_needs,
                app.is_loud if app.presentation == c.MUSIC else 'N/A', app.extra_info,
                app.panelist_bringing, app.affiliations, app.past_attendance, app.applied.strftime('%Y-%m-%d')] + panelists
            
            out.writerow(row)