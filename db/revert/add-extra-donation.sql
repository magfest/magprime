-- Revert magprime:add-extra-donation from pg

BEGIN;

ALTER TABLE attendee
        DROP COLUMN extra_donation;

COMMIT;
