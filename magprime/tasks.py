from collections.abc import Mapping
import json
from datetime import timedelta, datetime
import pytz
import logging
from time import sleep, time
import traceback

from celery.schedules import crontab
from sqlalchemy.orm import joinedload

from uber import utils
from uber.email import EmailService
from uber.config import c
from uber.decorators import render
from uber.models import AutomatedEmail, Email, MagModel, Attendee, Session, ReceiptItem, ModelReceipt
from uber.tasks import celery


log = logging.getLogger(__name__)


@celery.schedule(crontab(minute=0, hour=0))
def superstar_receipts():
    with Session() as session:
        # queue_email saves every receipt under one ident, so the donation ID in render_data marks what was sent.
        receipted_ids = set()
        for render_data, in session.query(Email.render_data).filter(Email.ident == 'superstar_receipt'):
            if render_data and 'donation_id' in render_data:
                receipted_ids.add(json.loads(render_data['donation_id']))

        extra_donations = session.query(ReceiptItem).join(ModelReceipt).filter(
            ReceiptItem.desc.contains("Extra Donation"), ReceiptItem.closed != None, ReceiptItem.amount > 0,
            ModelReceipt.owner_model == "Attendee")

        for donation in extra_donations:
            if donation.id in receipted_ids:
                continue

            attendee = session.get(Attendee, donation.receipt.owner_id)

            if not attendee or not attendee.gets_emails:
                continue

            if not attendee.amount_unpaid and "Automatic transfer from" not in attendee.admin_notes:
                closed_display = donation.closed.astimezone(c.EVENT_TIMEZONE).strftime('%H:%M on %B %d %Y')
                EmailService.queue_email(session, 'superstar_receipt', attendee, data={
                    'donation_id': donation.id,
                    'donation_amount': donation.amount / 100,
                    'donation_closed': closed_display})
        session.commit()