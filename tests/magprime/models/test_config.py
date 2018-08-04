from datetime import timedelta

import uber
from uber.config import c
from uber.utils import localized_now


class TestDealerConfig:
    def test_dealer_reg_open(self, monkeypatch):
        monkeypatch.setattr(c, 'DEALER_REG_START', localized_now() - timedelta(days=1))
        monkeypatch.setattr(c, 'DEALER_REG_SHUTDOWN', localized_now() + timedelta(days=1))
        monkeypatch.setattr(uber.config.Config, 'DEALER_REG_SOFT_CLOSED',
                            property(lambda s: False))
        assert c.DEALER_REG_OPEN

    def test_dealer_reg_soft_closed_really_closed(self, monkeypatch):
        monkeypatch.setattr(uber.config.Config, 'DEALER_REG_SOFT_CLOSED',
                            property(lambda s: True))
        assert not c.DEALER_REG_OPEN
