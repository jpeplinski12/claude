"""
Email Authentication Checker Module
====================================
Validates SPF, DKIM, and DMARC records for domains.
"""

import re
import socket
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from enum import Enum


class AuthStatus(Enum):
    """Authentication record status."""
    VALID = "valid"
    INVALID = "invalid"
    MISSING = "missing"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class SPFRecord:
    """SPF record analysis result."""
    status: AuthStatus
    raw_record: Optional[str] = None
    mechanisms: list[str] = field(default_factory=list)
    includes: list[str] = field(default_factory=list)
    policy: Optional[str] = None  # all, ~all, -all, ?all
    dns_lookups: int = 0
    issues: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return self.status in (AuthStatus.VALID, AuthStatus.WARNING)


@dataclass
class DKIMRecord:
    """DKIM record analysis result."""
    selector: str
    status: AuthStatus
    raw_record: Optional[str] = None
    key_type: Optional[str] = None  # rsa, ed25519
    key_bits: Optional[int] = None
    issues: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return self.status in (AuthStatus.VALID, AuthStatus.WARNING)


@dataclass
class DMARCRecord:
    """DMARC record analysis result."""
    status: AuthStatus
    raw_record: Optional[str] = None
    policy: Optional[str] = None  # none, quarantine, reject
    subdomain_policy: Optional[str] = None
    percentage: int = 100
    rua: list[str] = field(default_factory=list)  # Aggregate report URIs
    ruf: list[str] = field(default_factory=list)  # Forensic report URIs
    aspf: Optional[str] = None  # SPF alignment (r=relaxed, s=strict)
    adkim: Optional[str] = None  # DKIM alignment
    issues: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return self.status in (AuthStatus.VALID, AuthStatus.WARNING)


@dataclass
class AuthenticationReport:
    """Full authentication report for a domain."""
    domain: str
    spf: SPFRecord
    dkim: list[DKIMRecord]
    dmarc: DMARCRecord
    overall_score: int = 0  # 0-100
    checked_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def is_fully_authenticated(self) -> bool:
        """Check if domain has valid SPF, DKIM, and DMARC."""
        has_valid_dkim = any(d.is_valid for d in self.dkim) if self.dkim else False
        return self.spf.is_valid and has_valid_dkim and self.dmarc.is_valid


class AuthenticationChecker:
    """
    Checks email authentication records (SPF, DKIM, DMARC).

    Validates DNS records and provides recommendations for improvement.
    """

    # Common DKIM selectors to check
    COMMON_SELECTORS = [
        "default",
        "selector1",  # Microsoft 365
        "selector2",  # Microsoft 365
        "google",     # Google Workspace
        "k1",         # Mailchimp
        "mandrill",   # Mandrill
        "s1",         # Generic
        "s2",         # Generic
        "smtp",       # Generic
        "mail",       # Generic
        "dkim",       # Generic
        "email",      # Generic
        "braze",      # Braze
        "braze1",     # Braze
        "braze2",     # Braze
        "sendgrid",   # SendGrid
        "em",         # SendGrid
        "scph0316",   # SendGrid custom
    ]

    def __init__(self, timeout: float = 5.0):
        """Initialize the authentication checker."""
        self.timeout = timeout
        socket.setdefaulttimeout(timeout)

    def _dns_txt_lookup(self, domain: str) -> list[str]:
        """Perform DNS TXT record lookup."""
        try:
            import dns.resolver
            resolver = dns.resolver.Resolver()
            resolver.timeout = self.timeout
            resolver.lifetime = self.timeout

            answers = resolver.resolve(domain, "TXT")
            records = []
            for rdata in answers:
                # Join multiple strings in TXT record
                txt = "".join(s.decode() if isinstance(s, bytes) else s
                             for s in rdata.strings)
                records.append(txt)
            return records
        except ImportError:
            # Fallback to basic socket-based lookup
            return self._dns_txt_lookup_fallback(domain)
        except Exception:
            return []

    def _dns_txt_lookup_fallback(self, domain: str) -> list[str]:
        """Fallback TXT lookup using nslookup via subprocess."""
        import subprocess
        try:
            result = subprocess.run(
                ["nslookup", "-type=txt", domain],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            # Parse nslookup output
            records = []
            for line in result.stdout.split("\n"):
                if "text =" in line.lower() or '\"' in line:
                    # Extract quoted text
                    matches = re.findall(r'"([^"]*)"', line)
                    if matches:
                        records.append("".join(matches))
            return records
        except Exception:
            return []

    def check_spf(self, domain: str) -> SPFRecord:
        """
        Check SPF record for a domain.

        Args:
            domain: Domain to check

        Returns:
            SPFRecord with analysis
        """
        records = self._dns_txt_lookup(domain)

        # Find SPF record
        spf_records = [r for r in records if r.startswith("v=spf1")]

        if not spf_records:
            return SPFRecord(
                status=AuthStatus.MISSING,
                issues=["No SPF record found"],
                recommendations=[
                    "Add an SPF record to authorize your email servers",
                    "Example: v=spf1 include:_spf.google.com ~all"
                ]
            )

        if len(spf_records) > 1:
            return SPFRecord(
                status=AuthStatus.INVALID,
                raw_record=spf_records[0],
                issues=["Multiple SPF records found - only one is allowed"],
                recommendations=["Merge all SPF records into a single record"]
            )

        spf = spf_records[0]
        issues = []
        recommendations = []
        mechanisms = []
        includes = []

        # Parse mechanisms
        parts = spf.split()
        dns_lookups = 0

        for part in parts[1:]:  # Skip v=spf1
            if part.startswith("include:"):
                includes.append(part[8:])
                dns_lookups += 1
            elif part.startswith("a:") or part == "a":
                mechanisms.append(part)
                dns_lookups += 1
            elif part.startswith("mx:") or part == "mx":
                mechanisms.append(part)
                dns_lookups += 1
            elif part.startswith("ptr"):
                mechanisms.append(part)
                dns_lookups += 1
                issues.append("PTR mechanism is deprecated and slow")
            elif part.startswith("redirect="):
                dns_lookups += 1
                mechanisms.append(part)
            elif part.startswith("ip4:") or part.startswith("ip6:"):
                mechanisms.append(part)
            elif part in ("all", "+all", "-all", "~all", "?all"):
                mechanisms.append(part)

        # Determine policy
        policy = None
        for p in ["-all", "~all", "?all", "+all", "all"]:
            if p in spf or spf.endswith(p):
                policy = p
                break

        # Check for issues
        if dns_lookups > 10:
            issues.append(f"Too many DNS lookups ({dns_lookups}/10 max)")

        if policy == "+all" or policy == "all":
            issues.append("Policy '+all' allows anyone to send - very insecure!")
            recommendations.append("Change to '-all' (hard fail) or '~all' (soft fail)")
        elif policy == "?all":
            issues.append("Policy '?all' is neutral - provides no protection")
            recommendations.append("Change to '-all' or '~all' for better protection")
        elif policy == "~all":
            recommendations.append("Consider using '-all' for stricter enforcement")

        if len(spf) > 255:
            issues.append("SPF record exceeds 255 characters")
            recommendations.append("Use includes to reduce record length")

        # Determine status
        if issues and any("insecure" in i.lower() or "too many" in i.lower() for i in issues):
            status = AuthStatus.INVALID
        elif issues:
            status = AuthStatus.WARNING
        else:
            status = AuthStatus.VALID

        return SPFRecord(
            status=status,
            raw_record=spf,
            mechanisms=mechanisms,
            includes=includes,
            policy=policy,
            dns_lookups=dns_lookups,
            issues=issues,
            recommendations=recommendations
        )

    def check_dkim(self, domain: str, selectors: Optional[list[str]] = None) -> list[DKIMRecord]:
        """
        Check DKIM records for a domain.

        Args:
            domain: Domain to check
            selectors: List of DKIM selectors to check. Defaults to common selectors.

        Returns:
            List of DKIMRecord results
        """
        if selectors is None:
            selectors = self.COMMON_SELECTORS

        results = []

        for selector in selectors:
            dkim_domain = f"{selector}._domainkey.{domain}"
            records = self._dns_txt_lookup(dkim_domain)

            if not records:
                continue  # Selector not found, try next

            # Find DKIM record
            dkim_records = [r for r in records if "v=DKIM1" in r or "k=" in r or "p=" in r]

            if not dkim_records:
                continue

            dkim = dkim_records[0]
            issues = []
            recommendations = []

            # Parse key type
            key_type = "rsa"  # default
            if "k=ed25519" in dkim:
                key_type = "ed25519"
            elif "k=rsa" in dkim:
                key_type = "rsa"

            # Check for public key
            key_match = re.search(r'p=([A-Za-z0-9+/=]*)', dkim)
            key_bits = None

            if not key_match or not key_match.group(1):
                issues.append("No public key found (p= is empty) - key may be revoked")
            else:
                # Estimate key size from base64 length
                key_b64 = key_match.group(1)
                key_bytes = len(key_b64) * 3 / 4
                key_bits = int(key_bytes * 8)

                if key_type == "rsa" and key_bits < 1024:
                    issues.append(f"RSA key too short ({key_bits} bits)")
                    recommendations.append("Use at least 1024-bit, preferably 2048-bit RSA keys")
                elif key_type == "rsa" and key_bits < 2048:
                    recommendations.append("Consider upgrading to 2048-bit RSA key")

            # Check for testing mode
            if "t=y" in dkim:
                issues.append("DKIM is in testing mode (t=y)")
                recommendations.append("Remove t=y flag for production")

            # Determine status
            if issues and any("no public key" in i.lower() for i in issues):
                status = AuthStatus.INVALID
            elif issues:
                status = AuthStatus.WARNING
            else:
                status = AuthStatus.VALID

            results.append(DKIMRecord(
                selector=selector,
                status=status,
                raw_record=dkim,
                key_type=key_type,
                key_bits=key_bits,
                issues=issues,
                recommendations=recommendations
            ))

        # If no DKIM found at all
        if not results:
            results.append(DKIMRecord(
                selector="(none found)",
                status=AuthStatus.MISSING,
                issues=["No DKIM records found for common selectors"],
                recommendations=[
                    "Set up DKIM signing with your email provider",
                    "Common selectors: google, selector1, selector2, default"
                ]
            ))

        return results

    def check_dmarc(self, domain: str) -> DMARCRecord:
        """
        Check DMARC record for a domain.

        Args:
            domain: Domain to check

        Returns:
            DMARCRecord with analysis
        """
        dmarc_domain = f"_dmarc.{domain}"
        records = self._dns_txt_lookup(dmarc_domain)

        # Find DMARC record
        dmarc_records = [r for r in records if r.startswith("v=DMARC1")]

        if not dmarc_records:
            return DMARCRecord(
                status=AuthStatus.MISSING,
                issues=["No DMARC record found"],
                recommendations=[
                    "Add a DMARC record to protect your domain from spoofing",
                    "Start with: v=DMARC1; p=none; rua=mailto:dmarc@yourdomain.com",
                    "Gradually move to p=quarantine then p=reject"
                ]
            )

        dmarc = dmarc_records[0]
        issues = []
        recommendations = []

        # Parse DMARC tags
        tags = {}
        for part in dmarc.split(";"):
            part = part.strip()
            if "=" in part:
                key, value = part.split("=", 1)
                tags[key.strip()] = value.strip()

        policy = tags.get("p", "none")
        subdomain_policy = tags.get("sp", policy)
        percentage = int(tags.get("pct", "100"))

        # Parse report URIs
        rua = []
        ruf = []
        if "rua" in tags:
            rua = [uri.strip() for uri in tags["rua"].split(",")]
        if "ruf" in tags:
            ruf = [uri.strip() for uri in tags["ruf"].split(",")]

        aspf = tags.get("aspf", "r")  # relaxed default
        adkim = tags.get("adkim", "r")  # relaxed default

        # Check for issues
        if policy == "none":
            issues.append("DMARC policy is 'none' - no protection against spoofing")
            recommendations.append("Move to p=quarantine once you've reviewed reports")
        elif policy == "quarantine":
            recommendations.append("Consider moving to p=reject for maximum protection")

        if not rua:
            issues.append("No aggregate report URI (rua) configured")
            recommendations.append("Add rua=mailto:dmarc-reports@yourdomain.com to receive reports")

        if percentage < 100:
            issues.append(f"DMARC only applies to {percentage}% of messages")
            recommendations.append("Increase pct to 100 for full coverage")

        if subdomain_policy == "none" and policy != "none":
            issues.append("Subdomain policy (sp) is weaker than domain policy")
            recommendations.append("Set sp= to match your main policy")

        # Determine status
        if policy == "none":
            status = AuthStatus.WARNING
        elif issues:
            status = AuthStatus.WARNING
        else:
            status = AuthStatus.VALID

        return DMARCRecord(
            status=status,
            raw_record=dmarc,
            policy=policy,
            subdomain_policy=subdomain_policy,
            percentage=percentage,
            rua=rua,
            ruf=ruf,
            aspf=aspf,
            adkim=adkim,
            issues=issues,
            recommendations=recommendations
        )

    def check_all(self, domain: str, dkim_selectors: Optional[list[str]] = None) -> AuthenticationReport:
        """
        Perform full authentication check.

        Args:
            domain: Domain to check
            dkim_selectors: Optional list of DKIM selectors

        Returns:
            AuthenticationReport with all results
        """
        spf = self.check_spf(domain)
        dkim = self.check_dkim(domain, dkim_selectors)
        dmarc = self.check_dmarc(domain)

        # Calculate overall score
        score = 0

        # SPF scoring (30 points max)
        if spf.status == AuthStatus.VALID:
            score += 30
        elif spf.status == AuthStatus.WARNING:
            score += 20
        elif spf.status == AuthStatus.INVALID:
            score += 5

        # DKIM scoring (35 points max)
        valid_dkim = [d for d in dkim if d.status == AuthStatus.VALID]
        warning_dkim = [d for d in dkim if d.status == AuthStatus.WARNING]
        if valid_dkim:
            score += 35
        elif warning_dkim:
            score += 20

        # DMARC scoring (35 points max)
        if dmarc.status == AuthStatus.VALID:
            if dmarc.policy == "reject":
                score += 35
            elif dmarc.policy == "quarantine":
                score += 30
            else:
                score += 20
        elif dmarc.status == AuthStatus.WARNING:
            score += 15

        return AuthenticationReport(
            domain=domain,
            spf=spf,
            dkim=dkim,
            dmarc=dmarc,
            overall_score=score
        )


if __name__ == "__main__":
    # Test the checker
    checker = AuthenticationChecker()

    print("Testing pray.com authentication...")
    report = checker.check_all("pray.com")

    print(f"\nOverall Score: {report.overall_score}/100")
    print(f"Fully Authenticated: {report.is_fully_authenticated}")

    print(f"\nSPF: {report.spf.status.value}")
    if report.spf.raw_record:
        print(f"  Record: {report.spf.raw_record[:80]}...")
    for issue in report.spf.issues:
        print(f"  Issue: {issue}")

    print(f"\nDKIM:")
    for dkim in report.dkim:
        print(f"  Selector '{dkim.selector}': {dkim.status.value}")
        for issue in dkim.issues:
            print(f"    Issue: {issue}")

    print(f"\nDMARC: {report.dmarc.status.value}")
    if report.dmarc.policy:
        print(f"  Policy: {report.dmarc.policy}")
    for issue in report.dmarc.issues:
        print(f"  Issue: {issue}")
