import json
import re
import urllib.parse
from domain.log_alert import Log_Alert


class Analyze_Logs:
    def __init__(self):
        with open('RULES.json', 'r') as f:
            self.rules = json.load(f)['rules']

        for rule in self.rules:
            patterns = rule.get('patterns', [])
            compiled = []
            for p in patterns:
                if isinstance(p, dict) and 'pattern' in p:
                    pattern_str = p['pattern']
                else:
                    pattern_str = p
                try:
                    compiled.append(re.compile(pattern_str, re.IGNORECASE))
                except re.error:
                    compiled.append(re.compile(re.escape(str(pattern_str)), re.IGNORECASE))
            rule['compiled_patterns'] = compiled

    def match_rules(self, url: str):
        matches = []
        raw = url or ""
        decoded = urllib.parse.unquote(raw)
        decoded_plus = urllib.parse.unquote_plus(raw)
        raw_with_spaces = raw.replace('+', ' ')

        for rule in self.rules:
            applies = rule.get('applies_to')
            if applies and 'url' not in applies and 'method' not in applies:
                continue

            for pattern in rule.get('compiled_patterns', []):
                if pattern.search(raw) or pattern.search(decoded) or pattern.search(decoded_plus) or pattern.search(raw_with_spaces):
                    matches.append({
                        'name': rule.get('name'),
                        'category': rule.get('category'),
                        'severity': rule.get('severity'),
                        'pattern': pattern.pattern
                    })
                    break

        return matches

    def analyze_logs(self, log_line):
        log_pattern = r'(\S+) (\S+) (\S+) \[([\w:/]+\s[+\-]\d{4})\] "(\S+) (\S+)\s*(\S*)" (\d{3}) (\d+)'
        match = re.match(log_pattern, log_line)
        new_log = None
        if match:
            ip_address = match.group(1)
            date_time = match.group(4)
            method = match.group(5)
            requested_url = match.group(6)
            http_status = match.group(8)

            new_log = Log_Alert(ip_address=ip_address,
                                first_request=date_time,
                                last_request=date_time,
                                requested_url=requested_url,
                                matched_rules=[])

            # Match URL rules and attach results
            matched = self.match_rules(requested_url)
            setattr(new_log, 'matched_rules', matched)
            print("IP Address:", ip_address)
            print("Date/Time:", date_time)
            print("Method:", method)
            print("Requested URL:", requested_url)
            print("HTTP Status:", http_status)
            if matched:
                print("Matched Rules:")
                for m in matched:
                    print(f" - {m['name']} (category={m.get('category')}, severity={m.get('severity')}) pattern={m['pattern']}")
        else:
            print("Log entry does not match the expected format.")

        return new_log