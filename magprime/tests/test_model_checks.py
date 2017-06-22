import pytest

from uber.common import *
from magprime.model_checks import *


class TestAttendeeValidations:

    def test_extra_donation_nan(self):
        assert "What you entered for Extra Donation (blah) isn't even a number" == extra_donation_valid(Attendee(extra_donation="blah"))

    def test_extra_donation_below_zero(self):
        assert "Extra Donation must be a number that is 0 or higher." == extra_donation_valid(Attendee(extra_donation=-10))

    def test_extra_donation_valid(self):
        assert None == extra_donation_valid(Attendee(extra_donation=10))
