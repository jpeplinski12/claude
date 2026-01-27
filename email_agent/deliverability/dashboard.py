"""
Deliverability Dashboard Module
===============================
Unified dashboard combining all deliverability checks.
"""

import json
from dataclasses import dataclass, field, asdict
from typing import Optional
from datetime import datetime
from enum import Enum

from .blocklist_checker import BlocklistChecker, BlocklistReport
from .auth_checker import AuthenticationChecker, AuthenticationReport, AuthStatus
from .reputation_checker import ReputationChecker, ReputationReport, ReputationLevel


class HealthStatus(Enum):
    """Overall health status."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class DeliverabilityScore:
    """Breakdown of deliverability score."""
    authentication_score: int  # 0-35
    blocklist_score: int  # 0-35
    reputation_score: int  # 0-30
    total_score: int  # 0-100

    @property
    def grade(self) -> str:
        """Letter grade based on score."""
        if self.total_score >= 90:
            return "A"
        elif self.total_score >= 80:
            return "B"
        elif self.total_score >= 70:
            return "C"
        elif self.total_score >= 60:
            return "D"
        else:
            return "F"


@dataclass
class DeliverabilityReport:
    """Complete deliverability report."""
    domain: str
    ip: Optional[str]
    health_status: HealthStatus
    score: DeliverabilityScore
    authentication: AuthenticationReport
    blocklist_domain: BlocklistReport
    blocklist_ip: Optional[BlocklistReport]
    reputation: ReputationReport
    critical_issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    checked_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "domain": self.domain,
            "ip": self.ip,
            "health_status": self.health_status.value,
            "score": {
                "authentication": self.score.authentication_score,
                "blocklist": self.score.blocklist_score,
                "reputation": self.score.reputation_score,
                "total": self.score.total_score,
                "grade": self.score.grade
            },
            "critical_issues": self.critical_issues,
            "warnings": self.warnings,
            "recommendations": self.recommendations,
            "checked_at": self.checked_at.isoformat()
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class DeliverabilityDashboard:
    """
    Main deliverability dashboard that orchestrates all checks.

    Usage:
        dashboard = DeliverabilityDashboard()
        report = dashboard.run_full_check("example.com")
        print(f"Score: {report.score.total_score}/100 ({report.score.grade})")
    """

    def __init__(
        self,
        timeout: float = 5.0,
        dkim_selectors: Optional[list[str]] = None
    ):
        """
        Initialize the dashboard.

        Args:
            timeout: Timeout for DNS queries
            dkim_selectors: Custom DKIM selectors to check
        """
        self.blocklist_checker = BlocklistChecker(timeout=timeout)
        self.auth_checker = AuthenticationChecker(timeout=timeout)
        self.reputation_checker = ReputationChecker(timeout=timeout)
        self.dkim_selectors = dkim_selectors

    def run_full_check(self, domain: str, ip: Optional[str] = None) -> DeliverabilityReport:
        """
        Run a complete deliverability check.

        Args:
            domain: Domain to check
            ip: Optional IP address. If not provided, resolves from domain.

        Returns:
            DeliverabilityReport with all results
        """
        import socket

        # Resolve IP if not provided
        if ip is None:
            try:
                ip = socket.gethostbyname(domain)
            except socket.gaierror:
                ip = None

        # Run all checks
        auth_report = self.auth_checker.check_all(domain, self.dkim_selectors)
        blocklist_domain = self.blocklist_checker.check_domain(domain)
        blocklist_ip = self.blocklist_checker.check_ip(ip) if ip else None
        reputation_report = self.reputation_checker.check_reputation(domain, ip)

        # Calculate scores
        auth_score = self._calculate_auth_score(auth_report)
        blocklist_score = self._calculate_blocklist_score(blocklist_domain, blocklist_ip)
        reputation_score = self._calculate_reputation_score(reputation_report)
        total_score = auth_score + blocklist_score + reputation_score

        score = DeliverabilityScore(
            authentication_score=auth_score,
            blocklist_score=blocklist_score,
            reputation_score=reputation_score,
            total_score=total_score
        )

        # Collect issues and recommendations
        critical_issues = []
        warnings = []
        recommendations = []

        self._collect_auth_issues(auth_report, critical_issues, warnings, recommendations)
        self._collect_blocklist_issues(blocklist_domain, blocklist_ip, critical_issues, warnings)
        self._collect_reputation_issues(reputation_report, warnings, recommendations)

        # Determine overall health
        if critical_issues:
            health_status = HealthStatus.CRITICAL
        elif warnings or total_score < 70:
            health_status = HealthStatus.WARNING
        elif total_score >= 80:
            health_status = HealthStatus.HEALTHY
        else:
            health_status = HealthStatus.WARNING

        return DeliverabilityReport(
            domain=domain,
            ip=ip,
            health_status=health_status,
            score=score,
            authentication=auth_report,
            blocklist_domain=blocklist_domain,
            blocklist_ip=blocklist_ip,
            reputation=reputation_report,
            critical_issues=critical_issues,
            warnings=warnings,
            recommendations=recommendations
        )

    def _calculate_auth_score(self, auth: AuthenticationReport) -> int:
        """Calculate authentication score (max 35 points)."""
        score = 0

        # SPF (12 points)
        if auth.spf.status == AuthStatus.VALID:
            score += 12
        elif auth.spf.status == AuthStatus.WARNING:
            score += 8
        elif auth.spf.status == AuthStatus.INVALID:
            score += 3

        # DKIM (12 points)
        valid_dkim = any(d.status == AuthStatus.VALID for d in auth.dkim)
        warning_dkim = any(d.status == AuthStatus.WARNING for d in auth.dkim)
        if valid_dkim:
            score += 12
        elif warning_dkim:
            score += 7

        # DMARC (11 points)
        if auth.dmarc.status == AuthStatus.VALID:
            if auth.dmarc.policy == "reject":
                score += 11
            elif auth.dmarc.policy == "quarantine":
                score += 9
            else:
                score += 6
        elif auth.dmarc.status == AuthStatus.WARNING:
            score += 5

        return min(score, 35)

    def _calculate_blocklist_score(
        self,
        domain_report: BlocklistReport,
        ip_report: Optional[BlocklistReport]
    ) -> int:
        """Calculate blocklist score (max 35 points)."""
        # Start with full points
        score = 35

        # Deduct for domain listings
        if domain_report.total_listed > 0:
            # Critical blocklists have more impact
            for result in domain_report.results:
                if result.is_listed:
                    if "spamhaus" in result.blocklist_name.lower():
                        score -= 10
                    elif "surbl" in result.blocklist_name.lower():
                        score -= 8
                    else:
                        score -= 5

        # Deduct for IP listings
        if ip_report and ip_report.total_listed > 0:
            for result in ip_report.results:
                if result.is_listed:
                    if "spamhaus" in result.blocklist_name.lower():
                        score -= 10
                    elif "barracuda" in result.blocklist_name.lower():
                        score -= 8
                    elif "spamcop" in result.blocklist_name.lower():
                        score -= 6
                    else:
                        score -= 4

        return max(score, 0)

    def _calculate_reputation_score(self, rep: ReputationReport) -> int:
        """Calculate reputation score (max 30 points)."""
        base_score = rep.overall_score  # 0-100

        # Scale to 0-30
        return int((base_score / 100) * 30)

    def _collect_auth_issues(
        self,
        auth: AuthenticationReport,
        critical: list[str],
        warnings: list[str],
        recommendations: list[str]
    ):
        """Collect authentication issues and recommendations."""
        # SPF issues
        if auth.spf.status == AuthStatus.MISSING:
            critical.append("No SPF record found - email may be rejected")
        elif auth.spf.status == AuthStatus.INVALID:
            critical.append(f"Invalid SPF record: {', '.join(auth.spf.issues)}")
        else:
            for issue in auth.spf.issues:
                warnings.append(f"SPF: {issue}")
        recommendations.extend(auth.spf.recommendations)

        # DKIM issues
        has_valid_dkim = any(d.status == AuthStatus.VALID for d in auth.dkim)
        if not has_valid_dkim:
            if all(d.status == AuthStatus.MISSING for d in auth.dkim):
                critical.append("No DKIM records found - authentication incomplete")
            else:
                for dkim in auth.dkim:
                    for issue in dkim.issues:
                        warnings.append(f"DKIM ({dkim.selector}): {issue}")
        for dkim in auth.dkim:
            recommendations.extend(dkim.recommendations)

        # DMARC issues
        if auth.dmarc.status == AuthStatus.MISSING:
            critical.append("No DMARC record - domain vulnerable to spoofing")
        elif auth.dmarc.policy == "none":
            warnings.append("DMARC policy is 'none' - no protection against spoofing")
        for issue in auth.dmarc.issues:
            warnings.append(f"DMARC: {issue}")
        recommendations.extend(auth.dmarc.recommendations)

    def _collect_blocklist_issues(
        self,
        domain_report: BlocklistReport,
        ip_report: Optional[BlocklistReport],
        critical: list[str],
        warnings: list[str]
    ):
        """Collect blocklist issues."""
        # Domain blocklist issues
        for result in domain_report.results:
            if result.is_listed:
                if "spamhaus" in result.blocklist_name.lower():
                    critical.append(
                        f"Domain listed on {result.blocklist_name}: {result.meaning}"
                    )
                else:
                    warnings.append(
                        f"Domain listed on {result.blocklist_name}: {result.meaning}"
                    )

        # IP blocklist issues
        if ip_report:
            for result in ip_report.results:
                if result.is_listed:
                    if "spamhaus" in result.blocklist_name.lower():
                        critical.append(
                            f"IP listed on {result.blocklist_name}: {result.meaning}"
                        )
                    else:
                        warnings.append(
                            f"IP listed on {result.blocklist_name}: {result.meaning}"
                        )

    def _collect_reputation_issues(
        self,
        rep: ReputationReport,
        warnings: list[str],
        recommendations: list[str]
    ):
        """Collect reputation issues."""
        for source in rep.sources:
            if source.reputation in (ReputationLevel.POOR, ReputationLevel.BAD):
                warnings.append(f"{source.source_name}: {source.details}")

        # Add recommendations for manual checks
        if rep.overall_score < 70:
            recommendations.append(
                "Set up Google Postmaster Tools for detailed Gmail deliverability data"
            )
            recommendations.append(
                "Register for Microsoft SNDS to monitor Outlook/Hotmail reputation"
            )

    def quick_check(self, domain: str) -> dict:
        """
        Run a quick check (authentication only, faster).

        Returns a simplified dict with key findings.
        """
        auth_report = self.auth_checker.check_all(domain)

        return {
            "domain": domain,
            "spf": {
                "status": auth_report.spf.status.value,
                "policy": auth_report.spf.policy
            },
            "dkim": {
                "found": any(d.status != AuthStatus.MISSING for d in auth_report.dkim),
                "valid_selectors": [
                    d.selector for d in auth_report.dkim
                    if d.status == AuthStatus.VALID
                ]
            },
            "dmarc": {
                "status": auth_report.dmarc.status.value,
                "policy": auth_report.dmarc.policy
            },
            "score": auth_report.overall_score,
            "fully_authenticated": auth_report.is_fully_authenticated
        }

    def get_monitoring_config(self) -> dict:
        """
        Get recommended monitoring configuration.

        Returns a dict with:
        - domains: List of domains to monitor
        - check_frequency: Recommended check frequency
        - alert_thresholds: When to alert
        """
        return {
            "recommended_frequency": {
                "full_check": "daily",
                "blocklist_check": "every_6_hours",
                "auth_check": "weekly"
            },
            "alert_thresholds": {
                "score_warning": 70,
                "score_critical": 50,
                "blocklist_any": True,
                "spamhaus_immediate": True
            },
            "notification_channels": [
                "email",
                "slack"
            ],
            "setup_instructions": {
                "slack": "Create incoming webhook at https://api.slack.com/messaging/webhooks",
                "email": "Configure SMTP settings in environment variables"
            }
        }


def run_cli_check(domain: str):
    """Run a check from command line."""
    print(f"\n{'='*60}")
    print(f"  Deliverability Check: {domain}")
    print(f"{'='*60}\n")

    dashboard = DeliverabilityDashboard()

    print("Running checks...")
    report = dashboard.run_full_check(domain)

    # Display results
    print(f"\n{'='*60}")
    print(f"  RESULTS")
    print(f"{'='*60}")

    # Score
    grade_emoji = {
        "A": "🟢", "B": "🟢", "C": "🟡", "D": "🟠", "F": "🔴"
    }
    emoji = grade_emoji.get(report.score.grade, "⚪")
    print(f"\n{emoji} Overall Score: {report.score.total_score}/100 (Grade: {report.score.grade})")
    print(f"   - Authentication: {report.score.authentication_score}/35")
    print(f"   - Blocklist:      {report.score.blocklist_score}/35")
    print(f"   - Reputation:     {report.score.reputation_score}/30")

    # Health status
    status_emoji = {
        HealthStatus.HEALTHY: "✅",
        HealthStatus.WARNING: "⚠️",
        HealthStatus.CRITICAL: "🚨",
        HealthStatus.UNKNOWN: "❓"
    }
    print(f"\n{status_emoji[report.health_status]} Status: {report.health_status.value.upper()}")

    # Critical issues
    if report.critical_issues:
        print(f"\n🚨 CRITICAL ISSUES ({len(report.critical_issues)}):")
        for issue in report.critical_issues:
            print(f"   • {issue}")

    # Warnings
    if report.warnings:
        print(f"\n⚠️  WARNINGS ({len(report.warnings)}):")
        for warning in report.warnings[:5]:  # Limit to 5
            print(f"   • {warning}")
        if len(report.warnings) > 5:
            print(f"   ... and {len(report.warnings) - 5} more")

    # Recommendations
    if report.recommendations:
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in report.recommendations[:5]:
            print(f"   • {rec}")

    # Quick stats
    print(f"\n📊 Quick Stats:")
    print(f"   • IP: {report.ip or 'Not resolved'}")
    print(f"   • SPF: {report.authentication.spf.status.value}")
    print(f"   • DKIM: {sum(1 for d in report.authentication.dkim if d.status == AuthStatus.VALID)} valid selector(s)")
    print(f"   • DMARC: {report.authentication.dmarc.policy or 'none'}")
    print(f"   • Domain Blocklists: {report.blocklist_domain.total_listed}/{report.blocklist_domain.total_checked}")
    if report.blocklist_ip:
        print(f"   • IP Blocklists: {report.blocklist_ip.total_listed}/{report.blocklist_ip.total_checked}")

    print(f"\n{'='*60}\n")

    return report


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        domain = sys.argv[1]
    else:
        domain = "pray.com"

    run_cli_check(domain)
