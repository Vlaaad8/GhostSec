from datetime import datetime

class Log_Alert:
    def __init__(self, ip_address, first_request, last_request, requested_url, matched_rules):
        self.ip_address = ip_address
        self.request_numbers = 1
        self.first_request = self._to_datetime(first_request)
        self.last_request = self._to_datetime(last_request)
        self.requested_url = requested_url
        self.matched_rules = matched_rules if matched_rules else []
        self.avg_rate = 0

    def _to_datetime(self, value):
        """Convert string or numeric timestamp to datetime."""
        if isinstance(value, datetime):
            return value
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value)
        if isinstance(value, str):
            for fmt in [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S",
                "%d/%b/%Y:%H:%M:%S %z",
            ]:
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    continue
            raise ValueError(f"Unsupported datetime string: {value}")
        raise TypeError(f"Unsupported time format: {type(value)}")

    def update(self, new_last_request):
        self.last_request = self._to_datetime(new_last_request)
        self.request_numbers += 1
        total_time = (self.last_request - self.first_request).total_seconds()
        self.avg_rate = self.request_numbers / total_time if total_time > 0 else self.request_numbers
        print("Updated avg_rate:", self.avg_rate)
    def get_ip(self): 
        return self.ip_address

    def add_matched_rules(self, rules):
        if isinstance(rules, list):
            self.matched_rules.extend(rules)
        else:
            self.matched_rules.append(rules)

    def to_str(self):
        return (f"Log_Alert(ip_address={self.ip_address}, first_request={self.first_request}, "
                f"last_request={self.last_request}, requested_url={self.requested_url}, "
                f"matched_rules={self.matched_rules})"
                f"avg_rate={self.avg_rate})")

    def get_matched_rules(self):
        return self.matched_rules