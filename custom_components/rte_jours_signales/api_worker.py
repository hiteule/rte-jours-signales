"""API worker for RTE Jours Signalés integration."""
from __future__ import annotations

import datetime
import logging
import random
import threading
from typing import NamedTuple

from oauthlib.oauth2 import BackendApplicationClient, TokenExpiredError
from oauthlib.oauth2.rfc6749.errors import OAuth2Error
import requests
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session

from homeassistant.core import callback

from .const import (
    API_DATE_FORMAT,
    API_KEY_END,
    API_KEY_ERROR,
    API_KEY_ERROR_DESC,
    API_KEY_START,
    API_KEY_UPDATED,
    API_KEY_VALUE,
    API_REQ_TIMEOUT,
    API_DEMAND_RESPONSE_SIGNAL_ENDPOINT,
    API_TOKEN_ENDPOINT,
    CONFIRM_HOUR,
    CONFIRM_MIN,
    FRANCE_TZ,
    USER_AGENT,
)

_LOGGER = logging.getLogger(__name__)

class SignalDay(NamedTuple):
    """Represents a signal day."""

    Start: datetime.datetime | datetime.date
    End: datetime.datetime | datetime.date
    Value: int
    Updated: datetime.datetime

# https://data.rte-france.com/documents/20182/224298/FR_GU_API_Demand_Response_Signal_v02.00.01.pdf
class APIWorker(threading.Thread):
    """API Worker is an autonomous thread querying, parsing an caching the RTE Demand Response Signal API in an optimal way."""

    def __init__(self, client_id: str, client_secret: str) -> None:
        """Initialize the API Worker thread."""
        # Thread
        self._stopevent = threading.Event()
        # OAuth
        self._auth = HTTPBasicAuth(client_id, client_secret)
        self._oauth = OAuth2Session(
            client=BackendApplicationClient(client_id=client_id)
        )
        # Worker
        self._signal_days_time: list[SignalDay] = []
        # Init parent thread class
        super().__init__(name="RTE Demand Response Signal API Worker")

    def get_signal_days(self) -> list[SignalDay]:
        """Get the signal days."""
        return self._signal_days_time

    def run(self):
        """Execute thread payload."""
        _LOGGER.info("Starting thread")
        stop = False
        while not stop:
            # First auth
            if self._oauth.token == {}:
                self._get_access_token()
            # Fetch data
            localized_now = datetime.datetime.now(FRANCE_TZ)
            last_day = self._update_signal_days()
            # Wait depending on last result fetched
            wait_time = self._compute_wait_time(localized_now, last_day)
            stop = self._stopevent.wait(float(wait_time.seconds))
        # stopping thread
        _LOGGER.info("Thread stopped")

    @callback
    def signalstop(self, event):
        """Activate the stop flag in order to stop the thread from within."""
        _LOGGER.info(
            "Stopping RTE Demand Response Signal API Worker serial thread reader (received %s)",
            event,
        )
        self._stopevent.set()

    def _compute_wait_time(
        self, localized_now: datetime.datetime, last_day: datetime.datetime | None
    ) -> datetime.timedelta:
        if not last_day:
            # something went wrong, retry in 10 minutes
            return datetime.timedelta(minutes=10)
        # else compute appropriate wait time depending on date_end
        day_diff = last_day.day - localized_now.day

        if day_diff > 0:
            # We have next day, check if we need to confirm or wait until tomorrow
            confirmation_date = datetime.datetime(
                year=localized_now.year,
                month=localized_now.month,
                day=localized_now.day,
                hour=CONFIRM_HOUR,
                minute=CONFIRM_MIN,
                tzinfo=localized_now.tzinfo,
            )
            if localized_now > confirmation_date:
                # We are past the confirmation hour, wait until tomorrow
                tomorrow = localized_now + datetime.timedelta(days=1)
                next_call = datetime.datetime(
                    year=tomorrow.year,
                    month=tomorrow.month,
                    day=tomorrow.day,
                    hour=0,
                    minute=0,
                    tzinfo=localized_now.tzinfo,
                )
                wait_time = next_call - localized_now
                wait_time = datetime.timedelta(
                    seconds=random.randrange(wait_time.seconds, wait_time.seconds + 900)
                )
                _LOGGER.info(
                    "We got next day, waiting until tomorrow to get futur next day (wait time is %s)",
                    wait_time,
                )
            else:
                # We aren't past the confirmation hour, wait until confirmation hour
                next_call = datetime.datetime(
                    year=localized_now.year,
                    month=localized_now.month,
                    day=localized_now.day,
                    hour=CONFIRM_HOUR,
                    minute=CONFIRM_MIN,
                    tzinfo=localized_now.tzinfo,
                )
                wait_time = next_call - localized_now
                wait_time = datetime.timedelta(
                    seconds=random.randrange(wait_time.seconds, wait_time.seconds + 900)
                )
                _LOGGER.info(
                    "We got next day, waiting until confirmation hour (wait time is %s)",
                    wait_time,
                )

        else:
            # We do not have next day. This shouldn't happen, let's retry in ~1hour
            # weird, should not happen
            wait_time = datetime.timedelta(hours=1)
            wait_time = datetime.timedelta(
                seconds=random.randrange(
                    int(wait_time.seconds * 5 / 6), int(wait_time.seconds * 7 / 6)
                )
            )
            _LOGGER.warning(
                "Unexpected delta encountered between today and last result, waiting %s as fallback",
                wait_time,
            )

        # all good
        return wait_time

    def _get_access_token(self):
        _LOGGER.debug("Requesting access token")
        try:
            headers = {
                "User-Agent": USER_AGENT,
            }
            self._oauth.fetch_token(token_url=API_TOKEN_ENDPOINT, auth=self._auth, headers=headers)
        except (
            requests.exceptions.RequestException,
            OAuth2Error,
        ) as requests_exception:
            _LOGGER.error("Fetching OAuth2 access token failed: %s", requests_exception)

    def _get_signal_data(self) -> requests.Response:
        headers = {
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        }
        _LOGGER.debug(
            "Calling %s with no params",
            API_DEMAND_RESPONSE_SIGNAL_ENDPOINT,
        )
        # fetch data
        try:
            return self._oauth.get(
                API_DEMAND_RESPONSE_SIGNAL_ENDPOINT,
                timeout=API_REQ_TIMEOUT,
                headers=headers,
            )
        except TokenExpiredError:
            self._get_access_token()
            return self._oauth.get(
                API_DEMAND_RESPONSE_SIGNAL_ENDPOINT,
                timeout=API_REQ_TIMEOUT,
                headers=headers,
            )

    def _update_signal_days(self) -> datetime.datetime | None:
        # Get data
        try:
            response = self._get_signal_data()
            handle_api_errors(response)
        except requests.exceptions.RequestException as requests_exception:
            _LOGGER.error("API request failed: %s", requests_exception)
            return None
        except OAuth2Error as oauth_execption:
            _LOGGER.error("API request failed with OAuth2 error: %s", oauth_execption)
            return None
        except (BadRequest, ServerError, UnexpectedError) as http_error:
            _LOGGER.error("API request failed with HTTP error code: %s", http_error)
            return None
        try:
            payload = response.json()
        except requests.JSONDecodeError as exc:
            _LOGGER.error(
                "JSON parsing error on a HTTP 200 request (%s):\n%s", exc, response.text
            )
            return None
        # Parse datetimes and fix time for start and end dates
        signal_days_time: list[SignalDay] = []
        for signal_day in payload["signals"][0]["signaled_dates"]:
            try:
                signal_days_time.append(
                    SignalDay(
                        Start=parse_rte_api_datetime(signal_day[API_KEY_START]),
                        End=parse_rte_api_datetime(signal_day[API_KEY_END]),
                        Value=signal_day[API_KEY_VALUE],
                        Updated=parse_rte_api_datetime(signal_day[API_KEY_UPDATED]),
                    )
                )
            except KeyError as key_error:
                _LOGGER.warning(
                    "Following day failed to be processed with %s, skipping: %s",
                    repr(key_error),
                    signal_day,
                )
        # Save data in memory
        self._signal_days_time = signal_days_time
        # Return results last day start date in order for caller to compute next call time
        if len(self._signal_days_time) > 0:
            newest_result = self._signal_days_time[0].Start
            return datetime.datetime(
                year=newest_result.year,
                month=newest_result.month,
                day=newest_result.day,
                hour=0,
                minute=0,
                second=0,
                tzinfo=FRANCE_TZ,
            )
        return None

def parse_rte_api_datetime(date: str) -> datetime.datetime:
    """RTE API has a date format incompatible with python parsing."""
    date = (
        date[:-3] + date[-2:]
    )  # switch to a python format (remove ':' from rte tzinfo)
    return datetime.datetime.strptime(date, API_DATE_FORMAT)

def parse_rte_api_date(date: str) -> datetime.date:
    """RTE API has a date format incompatible with python parsing."""
    day_datetime = parse_rte_api_datetime(date)
    return datetime.date(
        year=day_datetime.year, month=day_datetime.month, day=day_datetime.day
    )

def application_tester(client_id: str, client_secret: str):
    """Test application credentials against the API."""
    auth = HTTPBasicAuth(client_id, client_secret)
    oauth = OAuth2Session(client=BackendApplicationClient(client_id=client_id))
    oauth.fetch_token(token_url=API_TOKEN_ENDPOINT, auth=auth)
    response = oauth.get(API_DEMAND_RESPONSE_SIGNAL_ENDPOINT, timeout=API_REQ_TIMEOUT)
    handle_api_errors(response)

def handle_api_errors(response: requests.Response):
    """Use to handle all errors described in the API documentation."""
    if response.status_code == 400:
        try:
            payload = response.json()
            raise BadRequest(
                response.status_code,
                f"{payload[API_KEY_ERROR]}: {payload[API_KEY_ERROR_DESC]}",
            )
        except requests.JSONDecodeError as exc:
            raise BadRequest(
                response.status_code, f"Failed to decode JSON payload: {response.text}"
            ) from exc
        except KeyError as exc:
            raise BadRequest(
                response.status_code,
                f"Failed to decode access JSON error payload: {response.text}",
            ) from exc
    elif response.status_code == 401:
        raise BadRequest(response.status_code, "Unauthorized")
    elif response.status_code == 403:
        raise BadRequest(response.status_code, "Forbidden")
    elif response.status_code == 404:
        raise BadRequest(response.status_code, "Not Found")
    elif response.status_code == 408:
        raise BadRequest(response.status_code, "Request Time-out")
    elif response.status_code == 413:
        raise BadRequest(response.status_code, "Request Entity Too Large")
    elif response.status_code == 414:
        raise BadRequest(response.status_code, "Request-URI Too Long")
    elif response.status_code == 429:
        raise BadRequest(response.status_code, "Too Many Requests")
    elif response.status_code == 500:
        try:
            payload = response.json()
            raise ServerError(
                response.status_code,
                f"{payload[API_KEY_ERROR]}: {payload[API_KEY_ERROR_DESC]}",
            )
        except requests.JSONDecodeError as exc:
            raise ServerError(
                response.status_code, f"Failed to decode JSON payload: {response.text}"
            ) from exc
        except KeyError as exc:
            raise ServerError(
                response.status_code,
                f"Failed to decode access JSON error payload: {response.text}",
            ) from exc
    elif response.status_code == 503:
        raise ServerError(response.status_code, "Service Unavailable")
    elif response.status_code == 509:
        raise ServerError(response.status_code, "Bandwidth Limit Exceeded")
    elif response.status_code != 200:
        raise UnexpectedError(
            response.status_code, f"Unexpected HTTP code: {response.text}"
        )

class BadRequest(Exception):
    """Represents a API HTTP 4xx error."""

    def __init__(self, code: int, message: str) -> None:
        """Initialize the BadRequest exception."""
        self.code = code
        super().__init__(f"HTTP code {code}: {message}")

class ServerError(Exception):
    """Represents a API HTTP 5xx error."""

    def __init__(self, code: int, message: str) -> None:
        """Initialize the ServerError exception."""
        self.code = code
        super().__init__(f"HTTP code {code}: {message}")

class UnexpectedError(Exception):
    """Represents any HTTP error not described by the API documentation."""

    def __init__(self, code: int, message: str) -> None:
        """Initialize the UnexpectedError exception."""
        self.code = code
        super().__init__(f"HTTP code {code}: {message}")
