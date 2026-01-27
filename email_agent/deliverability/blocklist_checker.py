"""
Blocklist Checker Module
========================
Checks domains and IPs against major email blocklists using DNS queries.
"""

import socket
import asyncio
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed


@dataclass
class BlocklistResult:
    """Result of a blocklist check."""
    blocklist_name: str
    blocklist_zone: str
    is_listed: bool
    return_code: Optional[str] = None
    meaning: Optional[str] = None
    checked_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class BlocklistReport:
    """Full blocklist report for a domain/IP."""
    target: str
    target_type: str  # 'ip' or 'domain'
    total_checked: int
    total_listed: int
    results: list[BlocklistResult] = field(default_factory=list)
    checked_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def is_clean(self) -> bool:
        return self.total_listed == 0

    @property
    def health_score(self) -> int:
        """Return health score 0-100."""
        if self.total_checked == 0:
            return 100
        return int(((self.total_checked - self.total_listed) / self.total_checked) * 100)


class BlocklistChecker:
    """
    Checks IPs and domains against major email blocklists.

    Uses DNS-based blocklist (DNSBL) queries to check if an IP or domain
    is listed on various spam blocklists.
    """

    # Major IP-based blocklists (DNSBLs)
    IP_BLOCKLISTS = {
        "Spamhaus ZEN": {
            "zone": "zen.spamhaus.org",
            "codes": {
                "127.0.0.2": "SBL - Spamhaus Block List",
                "127.0.0.3": "SBL CSS - Spamhaus CSS",
                "127.0.0.4": "XBL - Exploits Block List",
                "127.0.0.9": "SBL DROP - Spamhaus DROP",
                "127.0.0.10": "PBL - Policy Block List",
                "127.0.0.11": "PBL ISP - ISP Policy Block",
            }
        },
        "Spamhaus SBL": {
            "zone": "sbl.spamhaus.org",
            "codes": {"127.0.0.2": "Listed in SBL"}
        },
        "Spamhaus XBL": {
            "zone": "xbl.spamhaus.org",
            "codes": {"127.0.0.4": "Listed in XBL - Exploits"}
        },
        "Barracuda": {
            "zone": "b.barracudacentral.org",
            "codes": {"127.0.0.2": "Listed in Barracuda RBL"}
        },
        "SpamCop": {
            "zone": "bl.spamcop.net",
            "codes": {"127.0.0.2": "Listed in SpamCop"}
        },
        "SORBS SPAM": {
            "zone": "spam.dnsbl.sorbs.net",
            "codes": {"127.0.0.6": "Listed as spam source"}
        },
        "SORBS Recent": {
            "zone": "recent.spam.dnsbl.sorbs.net",
            "codes": {"127.0.0.6": "Recent spam source"}
        },
        "UCEProtect L1": {
            "zone": "dnsbl-1.uceprotect.net",
            "codes": {"127.0.0.2": "Listed in UCEProtect Level 1"}
        },
        "Invaluement": {
            "zone": "dnsbl.invaluement.com",
            "codes": {"127.0.0.2": "Listed for spam/phishing"}
        },
        "0Spam": {
            "zone": "bl.0spam.org",
            "codes": {"127.0.0.2": "Listed in 0spam"}
        },
    }

    # Domain-based blocklists (DBLs)
    DOMAIN_BLOCKLISTS = {
        "Spamhaus DBL": {
            "zone": "dbl.spamhaus.org",
            "codes": {
                "127.0.1.2": "Spam domain",
                "127.0.1.4": "Phishing domain",
                "127.0.1.5": "Malware domain",
                "127.0.1.6": "Botnet C&C domain",
                "127.0.1.102": "Abused legit spam",
                "127.0.1.103": "Abused redirector",
                "127.0.1.104": "Abused legit phishing",
                "127.0.1.105": "Abused legit malware",
                "127.0.1.106": "Abused legit botnet",
            }
        },
        "SURBL Multi": {
            "zone": "multi.surbl.org",
            "codes": {
                "127.0.0.2": "SC - SpamCop data",
                "127.0.0.4": "WS - sa-blacklist data",
                "127.0.0.8": "PH - Phishing data",
                "127.0.0.16": "MW - Malware data",
                "127.0.0.64": "ABUSE - Abuse data",
                "127.0.0.128": "CR - Cracked/compromised",
            }
        },
        "URIBL Multi": {
            "zone": "multi.uribl.com",
            "codes": {
                "127.0.0.2": "Listed in URIBL black",
                "127.0.0.4": "Listed in URIBL grey",
                "127.0.0.8": "Listed in URIBL red",
            }
        },
        "Invaluement URI": {
            "zone": "dnsbl.invaluement.com",
            "codes": {"127.0.0.2": "Listed domain"}
        },
    }

    def __init__(self, timeout: float = 3.0, max_workers: int = 10):
        """
        Initialize the blocklist checker.

        Args:
            timeout: DNS query timeout in seconds
            max_workers: Max concurrent DNS queries
        """
        self.timeout = timeout
        self.max_workers = max_workers
        socket.setdefaulttimeout(timeout)

    def _reverse_ip(self, ip: str) -> str:
        """Reverse IP octets for DNSBL query."""
        parts = ip.split(".")
        return ".".join(reversed(parts))

    def _dns_query(self, query: str) -> Optional[str]:
        """
        Perform DNS A record query.

        Returns the IP address if found (meaning listed), None if not listed.
        """
        try:
            result = socket.gethostbyname(query)
            return result
        except socket.gaierror:
            # NXDOMAIN - not listed
            return None
        except socket.timeout:
            # Timeout - treat as not listed but log
            return None
        except Exception:
            return None

    def _check_single_blocklist(
        self,
        target: str,
        blocklist_name: str,
        blocklist_info: dict,
        is_ip: bool = True
    ) -> BlocklistResult:
        """Check a single blocklist."""
        zone = blocklist_info["zone"]

        if is_ip:
            query = f"{self._reverse_ip(target)}.{zone}"
        else:
            query = f"{target}.{zone}"

        result_ip = self._dns_query(query)

        is_listed = result_ip is not None
        meaning = None

        if is_listed and result_ip:
            # Look up the meaning of the return code
            codes = blocklist_info.get("codes", {})
            meaning = codes.get(result_ip, f"Listed (code: {result_ip})")

        return BlocklistResult(
            blocklist_name=blocklist_name,
            blocklist_zone=zone,
            is_listed=is_listed,
            return_code=result_ip,
            meaning=meaning
        )

    def check_ip(self, ip: str, blocklists: Optional[dict] = None) -> BlocklistReport:
        """
        Check an IP address against IP-based blocklists.

        Args:
            ip: IP address to check (e.g., "192.0.2.1")
            blocklists: Optional custom blocklist dict, defaults to IP_BLOCKLISTS

        Returns:
            BlocklistReport with all results
        """
        if blocklists is None:
            blocklists = self.IP_BLOCKLISTS

        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(
                    self._check_single_blocklist,
                    ip,
                    name,
                    info,
                    True
                ): name
                for name, info in blocklists.items()
            }

            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception:
                    # Skip failed checks
                    pass

        listed_count = sum(1 for r in results if r.is_listed)

        return BlocklistReport(
            target=ip,
            target_type="ip",
            total_checked=len(results),
            total_listed=listed_count,
            results=results
        )

    def check_domain(self, domain: str, blocklists: Optional[dict] = None) -> BlocklistReport:
        """
        Check a domain against domain-based blocklists.

        Args:
            domain: Domain to check (e.g., "example.com")
            blocklists: Optional custom blocklist dict, defaults to DOMAIN_BLOCKLISTS

        Returns:
            BlocklistReport with all results
        """
        if blocklists is None:
            blocklists = self.DOMAIN_BLOCKLISTS

        # Strip any subdomain prefixes for base domain check
        domain = domain.lower().strip()
        if domain.startswith("www."):
            domain = domain[4:]

        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(
                    self._check_single_blocklist,
                    domain,
                    name,
                    info,
                    False
                ): name
                for name, info in blocklists.items()
            }

            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception:
                    pass

        listed_count = sum(1 for r in results if r.is_listed)

        return BlocklistReport(
            target=domain,
            target_type="domain",
            total_checked=len(results),
            total_listed=listed_count,
            results=results
        )

    def check_full(self, domain: str, ip: Optional[str] = None) -> dict:
        """
        Perform a full check on both domain and IP.

        Args:
            domain: Domain to check
            ip: Optional IP to check. If not provided, will attempt DNS lookup.

        Returns:
            Dict with 'domain' and 'ip' BlocklistReports
        """
        # Get IP from domain if not provided
        if ip is None:
            try:
                ip = socket.gethostbyname(domain)
            except socket.gaierror:
                ip = None

        domain_report = self.check_domain(domain)
        ip_report = self.check_ip(ip) if ip else None

        return {
            "domain": domain_report,
            "ip": ip_report,
            "resolved_ip": ip
        }

    def get_critical_blocklists(self) -> list[str]:
        """Return list of most critical blocklists to monitor."""
        return [
            "Spamhaus ZEN",
            "Spamhaus DBL",
            "Barracuda",
            "SpamCop",
            "SURBL Multi"
        ]


if __name__ == "__main__":
    # Test the checker
    checker = BlocklistChecker()

    # Test with a known good domain
    print("Testing pray.com...")
    result = checker.check_full("pray.com")

    print(f"\nDomain Report:")
    print(f"  Target: {result['domain'].target}")
    print(f"  Health Score: {result['domain'].health_score}%")
    print(f"  Listed on: {result['domain'].total_listed}/{result['domain'].total_checked} blocklists")

    if result['ip']:
        print(f"\nIP Report ({result['resolved_ip']}):")
        print(f"  Health Score: {result['ip'].health_score}%")
        print(f"  Listed on: {result['ip'].total_listed}/{result['ip'].total_checked} blocklists")
