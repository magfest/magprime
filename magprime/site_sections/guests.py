import os
import shutil
import logging
import cherrypy
from cherrypy.lib.static import serve_file
from sqlalchemy.orm.exc import NoResultFound

from uber.config import c
from uber.custom_tags import format_image_size
from uber.decorators import ajax, all_renderable, render
from uber.errors import HTTPRedirect
from uber.files import FileService
from uber.models import GuestMerch, GuestDetailedTravelPlan, GuestTravelPlans, GuestPanel
from uber.model_checks import mivs_show_info_required_fields
from uber.utils import check, filename_extension


log = logging.getLogger(__name__)


@all_renderable(public=True)
class Root:
    def bio(self, session, guest_id, message='', bio_pic=None, header_image=None, thumbnail_image=None, **params):
        guest = session.guest_group(guest_id)
        guest_bio = session.guest_bio(params)
        if cherrypy.request.method == 'POST':
            file_handlers = []

            if not guest_bio.desc:
                message = 'Please provide a brief bio for our website.'

            if not message:
                if bio_pic.filename:
                    file_handler = FileService.file_handler(session, guest_bio, flags={'bio_pic': True})
                    message = file_handler.process_file_upload(bio_pic, allowed_extensions=c.ALLOWED_BIO_PIC_EXTENSIONS,
                                                               delete_existing=False)
                    file_handlers.append(file_handler)

            if not message:
                existing_header = FileService.get_existing_files(session, guest_bio, and_flags=['guidebook_header'])
                existing_thumbnail = FileService.get_existing_files(session, guest_bio, and_flags=['guidebook_thumbnail'])
                if not existing_header and not header_image.filename:
                    message = f"You must upload a {format_image_size(c.GUIDEBOOK_HEADER_SIZE)} header image."

                if not message and not existing_thumbnail and not thumbnail_image.filename:
                    message = f"You must upload a {format_image_size(c.GUIDEBOOK_THUMBNAIL_SIZE)} thumbnail image."

            if not message and header_image and header_image.filename:
                file_handler = FileService.file_handler(session, guest_bio, flags={'guidebook_header': True})
                message = file_handler.process_file_upload(header_image,
                                                        allowed_extensions=c.GUIDEBOOK_ALLOWED_IMAGE_TYPES,
                                                        delete_existing=False, update_model=guest_bio)
                file_handlers.append(file_handler)

            if not message and thumbnail_image and thumbnail_image.filename:
                file_handler = FileService.file_handler(session, guest_bio, flags={'guidebook_thumbnail': True})
                message = file_handler.process_file_upload(thumbnail_image,
                                                        allowed_extensions=c.GUIDEBOOK_ALLOWED_IMAGE_TYPES,
                                                        delete_existing=False, update_model=guest_bio)
                file_handlers.append(file_handler)

            if message:
                for handler in file_handlers:
                    handler.delete()
            else:
                for handler in file_handlers:
                    FileService.delete_existing_files(session, handler.file_obj, and_flags=handler.file_obj.true_flags)
                guest.bio = guest_bio
                session.add(guest_bio)
                raise HTTPRedirect('index?id={}&message={}', guest.id, 'Your bio information has been updated')

        return {
            'guest': guest,
            'guest_bio': guest.bio or guest_bio,
            'guest_bio_pic': FileService.get_existing_files(session, guest.bio or guest_bio, and_flags=['bio_pic']),
            'guest_guidebook_header': FileService.get_existing_files(session, guest.bio or guest_bio, and_flags=['guidebook_header']),
            'guest_guidebook_thumbnail': FileService.get_existing_files(session, guest.bio or guest_bio, and_flags=['guidebook_thumbnail']),
            'message': message
        }