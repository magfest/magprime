-- Deploy magprime:add-extra-donation to pg

BEGIN;

ALTER TABLE attendee
        ADD COLUMN extra_donation integer DEFAULT 0 NOT NULL;

COMMIT;
