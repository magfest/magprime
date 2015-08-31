-- Verify magprime:add-extra-donation on pg

BEGIN;

SELECT column_name FROM information_schema.columns WHERE table_name = 'attendee' AND column_name = 'extra_donation';

ROLLBACK;
