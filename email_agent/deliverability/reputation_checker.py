"""
Reputation Checker Module
=========================
Aggregates domain/IP reputation from various sources.
"""

import socket
import re
import json
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from enum import Enum
import urllib.request
import urllib.error


class ReputationLevel(Enum):
    """Reputation level classification."""
    EXCELLENT = "excellent"
    GOOD = "good"
    NEUTRAL = "neutral"
    POOR = "poor"
    BAD = "bad"
    UNKNOWN = "unknown"


@dataclass
class ReputationSource:
    """Result from a single reputation source."""
    source_name: str
    reputation: ReputationLevel
    score: Optional[float] = None  # 0-100 if available
    details: Optional[str] = None
    url: Optional[str] = None  # Link to check manually
    checked_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class MXRecord:
    """MX record information."""
    priority: int
    host: str
    ip: Optional[str] = None


@dataclass
class DomainInfo:
    """Domain information and metadata."""
    domain: str
    mx_records: list[MXRecord] = field(default_factory=list)
    has_website: bool = False
    registrar: Optional[str] = None
    created_date: Optional[str] = None
    nameservers: list[str] = field(default_factory=list)


@dataclass
class ReputationReport:
    """Full reputation report."""
    domain: str
    ip: Optional[str]
    domain_info: DomainInfo
    sources: list[ReputationSource] = field(default_factory=list)
    overall_reputation: ReputationLevel = ReputationLevel.UNKNOWN
    overall_score: int = 0  # 0-100
    checked_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def manual_check_urls(self) -> dict:
        """Return URLs for manual reputation checks."""
        urls = {
            "Google Postmaster Tools": "https://postmaster.google.com/",
            "Microsoft SNDS": "https://sendersupport.olc.protection.outlook.com/snds/",
            "Talos Intelligence": f"https://talosintelligence.com/reputation_center/lookup?search={self.domain}",
            "MXToolbox": f"https://mxtoolbox.com/SuperTool.aspx?action=mx:{self.domain}&run=toolpage",
            "Sender Score": f"https://senderscore.org/assess/get-your-score/?lookup={self.domain}",
            "BarracudaCentral": f"https://www.barracudacentral.org/lookups/lookup-reputation?lookup_entry={self.ip or self.domain}",
        }
        return urls


class ReputationChecker:
    """
    Checks domain and IP reputation from various sources.

    Note: Some reputation services require API keys for full access.
    This module provides what's available via public DNS/web queries.
    """

    def __init__(self, timeout: float = 5.0):
        """Initialize the reputation checker."""
        self.timeout = timeout
        socket.setdefaulttimeout(timeout)

    def _get_mx_records(self, domain: str) -> list[MXRecord]:
        """Get MX records for a domain."""
        records = []
        try:
            import dns.resolver
            resolver = dns.resolver.Resolver()
            resolver.timeout = self.timeout

            answers = resolver.resolve(domain, "MX")
            for rdata in answers:
                mx_host = str(rdata.exchange).rstrip(".")
                try:
                    mx_ip = socket.gethostbyname(mx_host)
                except socket.gaierror:
                    mx_ip = None
                records.append(MXRecord(
                    priority=rdata.preference,
                    host=mx_host,
                    ip=mx_ip
                ))
        except ImportError:
            # Fallback
            pass
        except Exception:
            pass

        return sorted(records, key=lambda x: x.priority)

    def _get_nameservers(self, domain: str) -> list[str]:
        """Get nameservers for a domain."""
        nameservers = []
        try:
            import dns.resolver
            resolver = dns.resolver.Resolver()
            answers = resolver.resolve(domain, "NS")
            for rdata in answers:
                nameservers.append(str(rdata.target).rstrip("."))
        except Exception:
            pass
        return nameservers

    def _check_website(self, domain: str) -> bool:
        """Check if domain has a working website."""
        try:
            req = urllib.request.Request(
                f"https://{domain}",
                headers={"User-Agent": "Mozilla/5.0 (compatible; DeliverabilityChecker/1.0)"}
            )
            urllib.request.urlopen(req, timeout=self.timeout)
            return True
        except Exception:
            try:
                req = urllib.request.Request(
                    f"http://{domain}",
                    headers={"User-Agent": "Mozilla/5.0 (compatible; DeliverabilityChecker/1.0)"}
                )
                urllib.request.urlopen(req, timeout=self.timeout)
                return True
            except Exception:
                return False

    def _check_reverse_dns(self, ip: str) -> Optional[str]:
        """Check reverse DNS (PTR record) for an IP."""
        try:
            hostname, _, _ = socket.gethostbyaddr(ip)
            return hostname
        except socket.herror:
            return None
        except Exception:
            return None

    def _check_talos_reputation(self, target: str) -> ReputationSource:
        """
        Check Cisco Talos reputation.
        Note: Full API requires registration, this is a basic check.
        """
        return ReputationSource(
            source_name="Cisco Talos",
            reputation=ReputationLevel.UNKNOWN,
            details="Manual check required - API key needed for automated checks",
            url=f"https://talosintelligence.com/reputation_center/lookup?search={target}"
        )

    def _check_ip_quality_score(self, ip: str) -> ReputationSource:
        """
        Check IPQualityScore (requires API key for full access).
        """
        return ReputationSource(
            source_name="IPQualityScore",
            reputation=ReputationLevel.UNKNOWN,
            details="Manual check required - API key needed for automated checks",
            url=f"https://www.ipqualityscore.com/free-ip-lookup-proxy-vpn-test/lookup/{ip}"
        )

    def _analyze_mx_reputation(self, mx_records: list[MXRecord]) -> ReputationSource:
        """Analyze MX records for reputation indicators."""
        if not mx_records:
            return ReputationSource(
                source_name="MX Analysis",
                reputation=ReputationLevel.POOR,
                details="No MX records found - domain cannot receive email"
            )

        # Check for known good email providers
        good_providers = [
            "google.com", "googlemail.com", "outlook.com", "microsoft.com",
            "amazonses.com", "sendgrid.net", "mailgun.org", "postmarkapp.com",
            "sparkpostmail.com", "mcsv.net", "mailchimp.com"
        ]

        primary_mx = mx_records[0].host.lower()

        for provider in good_providers:
            if provider in primary_mx:
                return ReputationSource(
                    source_name="MX Analysis",
                    reputation=ReputationLevel.GOOD,
                    details=f"Using reputable email provider ({provider})",
                    score=80
                )

        # Check for self-hosted mail
        return ReputationSource(
            source_name="MX Analysis",
            reputation=ReputationLevel.NEUTRAL,
            details=f"Custom MX: {primary_mx}",
            score=50
        )

    def _check_ptr_record(self, ip: str) -> ReputationSource:
        """Check PTR (reverse DNS) record."""
        ptr = self._check_reverse_dns(ip)

        if ptr:
            return ReputationSource(
                source_name="PTR Record",
                reputation=ReputationLevel.GOOD,
                details=f"Reverse DNS configured: {ptr}",
                score=80
            )
        else:
            return ReputationSource(
                source_name="PTR Record",
                reputation=ReputationLevel.POOR,
                details="No reverse DNS (PTR) record - may affect deliverability",
                score=30
            )

    def _check_domain_age_signals(self, domain: str) -> ReputationSource:
        """
        Check domain age and signals.
        Note: Full WHOIS requires API. This checks DNS-based signals.
        """
        # Check for established signals
        signals = []

        # Has MX?
        mx = self._get_mx_records(domain)
        if mx:
            signals.append("Has MX records")

        # Has website?
        if self._check_website(domain):
            signals.append("Has active website")

        # Has nameservers?
        ns = self._get_nameservers(domain)
        if ns:
            signals.append(f"Has {len(ns)} nameservers")

        if len(signals) >= 3:
            return ReputationSource(
                source_name="Domain Maturity",
                reputation=ReputationLevel.GOOD,
                details=f"Established domain: {', '.join(signals)}",
                score=75
            )
        elif len(signals) >= 1:
            return ReputationSource(
                source_name="Domain Maturity",
                reputation=ReputationLevel.NEUTRAL,
                details=f"Basic setup: {', '.join(signals)}",
                score=50
            )
        else:
            return ReputationSource(
                source_name="Domain Maturity",
                reputation=ReputationLevel.POOR,
                details="Domain appears new or unconfigured",
                score=25
            )

    def get_domain_info(self, domain: str) -> DomainInfo:
        """Get comprehensive domain information."""
        mx_records = self._get_mx_records(domain)
        nameservers = self._get_nameservers(domain)
        has_website = self._check_website(domain)

        return DomainInfo(
            domain=domain,
            mx_records=mx_records,
            has_website=has_website,
            nameservers=nameservers
        )

    def check_reputation(self, domain: str, ip: Optional[str] = None) -> ReputationReport:
        """
        Check reputation from multiple sources.

        Args:
            domain: Domain to check
            ip: Optional IP to check. If not provided, resolves from domain.

        Returns:
            ReputationReport with aggregated results
        """
        # Resolve IP if not provided
        if ip is None:
            try:
                ip = socket.gethostbyname(domain)
            except socket.gaierror:
                ip = None

        # Get domain info
        domain_info = self.get_domain_info(domain)

        sources = []

        # Run reputation checks
        sources.append(self._analyze_mx_reputation(domain_info.mx_records))

        if ip:
            sources.append(self._check_ptr_record(ip))

        sources.append(self._check_domain_age_signals(domain))

        # Add manual check references
        sources.append(self._check_talos_reputation(domain))
        if ip:
            sources.append(self._check_ip_quality_score(ip))

        # Calculate overall reputation
        scored_sources = [s for s in sources if s.score is not None]
        if scored_sources:
            avg_score = sum(s.score for s in scored_sources) / len(scored_sources)
        else:
            avg_score = 50

        # Determine overall level
        if avg_score >= 80:
            overall_rep = ReputationLevel.EXCELLENT
        elif avg_score >= 65:
            overall_rep = ReputationLevel.GOOD
        elif avg_score >= 45:
            overall_rep = ReputationLevel.NEUTRAL
        elif avg_score >= 25:
            overall_rep = ReputationLevel.POOR
        else:
            overall_rep = ReputationLevel.BAD

        return ReputationReport(
            domain=domain,
            ip=ip,
            domain_info=domain_info,
            sources=sources,
            overall_reputation=overall_rep,
            overall_score=int(avg_score)
        )


class PostmasterToolsConfig:
    """
    Configuration for Google Postmaster Tools API integration.

    To use:
    1. Go to https://postmaster.google.com/
    2. Add and verify your domain
    3. Create OAuth2 credentials in Google Cloud Console
    4. Enable Gmail Postmaster Tools API
    """

    def __init__(self, credentials_path: Optional[str] = None):
        self.credentials_path = credentials_path
        self.api_base = "https://gmailpostmastertools.googleapis.com/v1"

    def get_setup_instructions(self) -> str:
        return """
Google Postmaster Tools Setup:
==============================
1. Visit https://postmaster.google.com/
2. Click 'Get Started' and sign in with your Google account
3. Add your sending domain (e.g., pray.com)
4. Verify ownership via DNS TXT record
5. Wait 24-48 hours for data to populate

For API Access:
1. Go to https://console.cloud.google.com/
2. Create a new project or select existing
3. Enable 'Gmail Postmaster Tools API'
4. Create OAuth2 credentials (Desktop app type)
5. Download credentials JSON
6. Set GOOGLE_POSTMASTER_CREDENTIALS env var to path

Once configured, you'll see:
- Domain reputation (High/Medium/Low/Bad)
- Spam rate percentage
- Authentication rates (SPF/DKIM/DMARC pass rates)
- Encryption rates (TLS usage)
- Delivery errors breakdown
"""


class MicrosoftSNDSConfig:
    """
    Configuration for Microsoft SNDS (Smart Network Data Services).

    To use:
    1. Go to https://sendersupport.olc.protection.outlook.com/snds/
    2. Sign up with Microsoft account
    3. Request access for your sending IPs
    4. Wait for approval (usually 24-48 hours)
    """

    def __init__(self):
        self.portal_url = "https://sendersupport.olc.protection.outlook.com/snds/"

    def get_setup_instructions(self) -> str:
        return """
Microsoft SNDS Setup:
=====================
1. Visit https://sendersupport.olc.protection.outlook.com/snds/
2. Sign in with your Microsoft account
3. Click 'Request Access'
4. Enter your sending IP addresses/ranges
5. Complete verification (may require authorization from IP owner)
6. Wait for approval (24-48 hours)

Once approved, you'll see:
- IP reputation status (Green/Yellow/Red)
- Spam trap hits
- Complaint rates
- Filter results (% delivered to inbox vs junk)
- Sample spam trap data

JMRP (Junk Mail Reporting Program):
Also consider enrolling in JMRP at the same portal to receive
feedback loop reports when users mark your email as spam.
"""


if __name__ == "__main__":
    # Test the checker
    checker = ReputationChecker()

    print("Testing pray.com reputation...")
    report = checker.check_reputation("pray.com")

    print(f"\nDomain: {report.domain}")
    print(f"IP: {report.ip}")
    print(f"Overall Reputation: {report.overall_reputation.value}")
    print(f"Overall Score: {report.overall_score}/100")

    print("\nDomain Info:")
    print(f"  Has Website: {report.domain_info.has_website}")
    print(f"  MX Records: {len(report.domain_info.mx_records)}")
    for mx in report.domain_info.mx_records[:3]:
        print(f"    - {mx.priority} {mx.host}")

    print("\nReputation Sources:")
    for source in report.sources:
        score_str = f" ({source.score}/100)" if source.score else ""
        print(f"  {source.source_name}: {source.reputation.value}{score_str}")
        if source.details:
            print(f"    {source.details}")

    print("\nManual Check URLs:")
    for name, url in report.manual_check_urls.items():
        print(f"  {name}: {url}")
