import ntplib
from datetime import datetime, timezone
import pytz

class TimeChecker:
    def __init__(self, ntp_server='pool.ntp.org', timezone = 'Asia/Kolkata'):
        self.ntp_server = ntp_server
        self.timezone = timezone

    def get_ntp_date(self):
        client = ntplib.NTPClient()
        try:
            response = client.request(self.ntp_server, version=3)
            utc_time = datetime.fromtimestamp(response.tx_time, tz=timezone.utc)
            local_time = utc_time.astimezone(pytz.timezone(self.timezone))
            return local_time.date()
        except Exception as e:
            print(f"Failed to get NTP time: {e}")
            return None

    def get_system_date(self):
        system_time = datetime.now(pytz.timezone(self.timezone))
        return system_time.date()

    def compare_dates(self):
        ntp_date = self.get_ntp_date()
        system_date = self.get_system_date()

        if ntp_date and system_date:
            if ntp_date == system_date:
                return True
            else:
                return False
        else:
            return False