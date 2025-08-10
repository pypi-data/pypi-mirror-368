"""DNS utilities including CAA record checks."""

from typing import Dict, Any

import dns.resolver
import dns.exception


def query_caa(domain: str) -> Dict[str, Any]:
    """Query DNS CAA records for a domain.

    Args:
        domain (str): Domain to query.

    Returns:
        Dict[str, Any]: Summary with keys:
            - checked (bool): Whether the query was executed.
            - found (bool): Whether CAA records were found.
            - records (List[dict]): Parsed CAA records.
            - error (str | None): Error message if any.
    """
    result: Dict[str, Any] = {
        "checked": True,
        "found": False,
        "records": [],
        "error": None,
    }
    try:
        answers = dns.resolver.resolve(domain, "CAA")
        for rdata in answers:
            result["records"].append({
                "flags": int(getattr(rdata, "flags", 0)),
                "tag": str(getattr(rdata, "tag", "")),
                "value": str(getattr(rdata, "value", "")),
            })
        result["found"] = len(result["records"]) > 0
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        # No CAA records exist for the domain. This is not an error.
        result["found"] = False
        result["records"] = []
    except dns.exception.DNSException as exc:
        result["error"] = str(exc)
    return result
