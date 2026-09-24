from urllib.parse import urlparse


def detect_ats(url: str) -> str:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    path = (parsed.path or "").lower()
    if "greenhouse.io" in host or "boards.greenhouse" in host:
        return "greenhouse"
    if "lever.co" in host:
        return "lever"
    if "ashbyhq.com" in host:
        return "ashby"
    if "workday" in host or "myworkdayjobs" in host:
        return "workday"
    if "linkedin.com" in host and "/jobs" in path:
        return "linkedin"
    return "generic"
