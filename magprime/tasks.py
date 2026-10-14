from collections.abc import Mapping
from datetime import timedelta, datetime
import pytz
import logging
from time import sleep, time
import traceback

from celery.schedules import crontab
from sqlalchemy.orm import joinedload

from uber import utils
from uber.email import EmailHandler
from uber.config import c
from uber.decorators import render
from uber.models import AutomatedEmail, Email, MagModel, Attendee, Session, ReceiptItem, ModelReceipt
from uber.tasks import celery


log = logging.getLogger(__name__)


@celery.schedule(crontab(minute=0, hour=0))
def superstar_receipts():
    with Session() as session:
        fixture_obj = session.query(AutomatedEmail).filter(AutomatedEmail.ident == 'superstar_receipt').first()
        if not fixture_obj:
            log.error("Superstar receipt fixture 'superstar_receipt' is missing; no receipts queued.")
            return

        extra_donations = session.query(ReceiptItem).join(ModelReceipt).filter(
            ReceiptItem.desc.contains("Extra Donation"), ReceiptItem.closed != None, ReceiptItem.amount > 0,
            ModelReceipt.owner_model == "Attendee")

        for donation in extra_donations:
            attendee = session.get(Attendee, donation.receipt.owner_id)

            if not attendee.amount_unpaid and "Automatic transfer from" not in attendee.admin_notes:
                closed_local = donation.closed.astimezone(c.EVENT_TIMEZONE).strftime('%x_%X')
                ident = f'superstar_receipt_{int(donation.amount / 100)}_{closed_local}'
                already_emailed = session.query(Email.ident).filter(Email.ident == ident, Email.fk_id == attendee.id).first()

                if not already_emailed:
                    closed_display = donation.closed.astimezone(c.EVENT_TIMEZONE).strftime('%H:%M on %B %d %Y')
                    data = {'donation_amount': donation.amount / 100, 'donation_closed': closed_display}
                    email_handler = EmailHandler(fixture_obj, attendee, ident=ident, data=data)
                    if email_handler.can_queue_email(session):
                        email_handler.queue_email_obj(session)
        session.commit()