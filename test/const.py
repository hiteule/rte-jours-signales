"""Constants for testing."""

import datetime

from custom_components.rte_jours_signales.api_worker import SignalDay
from custom_components.rte_jours_signales.const import FRANCE_TZ

MOCK_CLIENT_ID = "my-client-id"
MOCK_CLIENT_SECRET = "my-client-secret"

def get_mock_signal_day() -> list[SignalDay]:
    """Build a SignalDay list"""

    signal_days_time: list[SignalDay] = []

    signal_days_time.append(
        SignalDay(
            Start=datetime.datetime(year=2025, month=1, day=2, hour=0, minute=0, second=0, tzinfo=FRANCE_TZ),
            End=datetime.datetime(year=2025, month=1, day=3, hour=0, minute=0, second=0, tzinfo=FRANCE_TZ),
            Value=0,
            Updated=datetime.datetime(year=2025, month=1, day=3, hour=0, minute=0, second=0, tzinfo=FRANCE_TZ),
        )
    )

    signal_days_time.append(
        SignalDay(
            Start=datetime.datetime(year=2025, month=1, day=1, hour=0, minute=0, second=0, tzinfo=FRANCE_TZ),
            End=datetime.datetime(year=2025, month=1, day=2, hour=0, minute=0, second=0, tzinfo=FRANCE_TZ),
            Value=1,
            Updated=datetime.datetime(year=2025, month=1, day=2, hour=0, minute=0, second=0, tzinfo=FRANCE_TZ),
        )
    )

    return signal_days_time

MOCK_SIGNAL_DAY = get_mock_signal_day()
