"""
Deliverability Dashboard - Streamlit UI
========================================
Visual interface for email deliverability monitoring.
"""

import streamlit as st
from datetime import datetime
from typing import Optional

from .dashboard import DeliverabilityDashboard, HealthStatus
from .auth_checker import AuthStatus
from .reputation_checker import ReputationLevel, PostmasterToolsConfig, MicrosoftSNDSConfig


def render_deliverability_dashboard():
    """Render the full deliverability dashboard UI."""
    st.markdown("### Email Deliverability Monitor")
    st.markdown("Check your domain's email deliverability health across blocklists, authentication, and reputation.")

    # Input section
    col1, col2 = st.columns([3, 1])

    with col1:
        domain = st.text_input(
            "Domain to check",
            value=st.session_state.get("last_domain", ""),
            placeholder="example.com",
            help="Enter the domain you send emails from"
        )

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        check_button = st.button("Run Full Check", type="primary", use_container_width=True)

    # Optional: Custom DKIM selectors
    with st.expander("Advanced Options"):
        custom_selectors = st.text_input(
            "Custom DKIM Selectors (comma-separated)",
            placeholder="selector1, selector2, braze, google",
            help="Add custom DKIM selectors to check. Common ones are checked by default."
        )
        custom_ip = st.text_input(
            "Specific IP to check (optional)",
            placeholder="192.0.2.1",
            help="If not provided, will resolve from domain"
        )

    if check_button and domain:
        st.session_state["last_domain"] = domain

        # Parse custom selectors
        selectors = None
        if custom_selectors:
            selectors = [s.strip() for s in custom_selectors.split(",") if s.strip()]

        ip = custom_ip if custom_ip else None

        with st.spinner("Running deliverability checks... This may take 15-30 seconds."):
            try:
                dashboard = DeliverabilityDashboard(dkim_selectors=selectors)
                report = dashboard.run_full_check(domain, ip)
                st.session_state["deliverability_report"] = report
            except Exception as e:
                st.error(f"Error running checks: {str(e)}")
                return

    # Display results
    if "deliverability_report" in st.session_state:
        report = st.session_state["deliverability_report"]
        render_report(report)


def render_report(report):
    """Render the deliverability report."""

    # Overall score card
    st.markdown("---")

    # Score display
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        score_color = _get_score_color(report.score.total_score)
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {score_color}22, {score_color}11);
                    border: 2px solid {score_color};
                    border-radius: 12px; padding: 20px; text-align: center;">
            <div style="font-size: 3rem; font-weight: bold; color: {score_color};">
                {report.score.grade}
            </div>
            <div style="font-size: 1.5rem; color: #ffffff;">
                {report.score.total_score}/100
            </div>
            <div style="font-size: 0.9rem; color: #888;">Overall Score</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        auth_color = _get_score_color(report.score.authentication_score * 100 // 35)
        st.markdown(f"""
        <div style="background: #1a1a2e; border-radius: 12px; padding: 20px; text-align: center; border: 1px solid #333;">
            <div style="font-size: 2rem; font-weight: bold; color: {auth_color};">
                {report.score.authentication_score}/35
            </div>
            <div style="font-size: 0.9rem; color: #888;">Authentication</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        bl_color = _get_score_color(report.score.blocklist_score * 100 // 35)
        st.markdown(f"""
        <div style="background: #1a1a2e; border-radius: 12px; padding: 20px; text-align: center; border: 1px solid #333;">
            <div style="font-size: 2rem; font-weight: bold; color: {bl_color};">
                {report.score.blocklist_score}/35
            </div>
            <div style="font-size: 0.9rem; color: #888;">Blocklist</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        rep_color = _get_score_color(report.score.reputation_score * 100 // 30)
        st.markdown(f"""
        <div style="background: #1a1a2e; border-radius: 12px; padding: 20px; text-align: center; border: 1px solid #333;">
            <div style="font-size: 2rem; font-weight: bold; color: {rep_color};">
                {report.score.reputation_score}/30
            </div>
            <div style="font-size: 0.9rem; color: #888;">Reputation</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Health status banner
    status_config = {
        HealthStatus.HEALTHY: ("✅", "#22c55e", "All systems healthy"),
        HealthStatus.WARNING: ("⚠️", "#f59e0b", "Some issues need attention"),
        HealthStatus.CRITICAL: ("🚨", "#ef4444", "Critical issues detected"),
        HealthStatus.UNKNOWN: ("❓", "#6b7280", "Unable to determine status")
    }
    emoji, color, message = status_config[report.health_status]

    st.markdown(f"""
    <div style="background: {color}22; border-left: 4px solid {color};
                padding: 15px 20px; border-radius: 8px; margin-bottom: 20px;">
        <span style="font-size: 1.2rem;">{emoji} <strong>{report.health_status.value.upper()}</strong></span>
        <span style="color: #888; margin-left: 10px;">{message}</span>
    </div>
    """, unsafe_allow_html=True)

    # Critical issues
    if report.critical_issues:
        st.markdown("#### 🚨 Critical Issues")
        for issue in report.critical_issues:
            st.error(issue)

    # Warnings
    if report.warnings:
        with st.expander(f"⚠️ Warnings ({len(report.warnings)})", expanded=len(report.warnings) <= 3):
            for warning in report.warnings:
                st.warning(warning)

    # Tabs for detailed results
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔐 Authentication",
        "🚫 Blocklists",
        "📊 Reputation",
        "💡 Recommendations"
    ])

    with tab1:
        render_authentication_tab(report)

    with tab2:
        render_blocklist_tab(report)

    with tab3:
        render_reputation_tab(report)

    with tab4:
        render_recommendations_tab(report)

    # Export options
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            "📥 Download Report (JSON)",
            report.to_json(),
            file_name=f"deliverability_report_{report.domain}_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json"
        )

    with col2:
        st.markdown(f"*Last checked: {report.checked_at.strftime('%Y-%m-%d %H:%M:%S UTC')}*")


def render_authentication_tab(report):
    """Render authentication details tab."""
    auth = report.authentication

    st.markdown("##### SPF (Sender Policy Framework)")
    spf_status_icon = _get_status_icon(auth.spf.status)
    st.markdown(f"{spf_status_icon} **Status:** {auth.spf.status.value}")

    if auth.spf.raw_record:
        with st.expander("View SPF Record"):
            st.code(auth.spf.raw_record, language="text")
            if auth.spf.policy:
                st.markdown(f"**Policy:** `{auth.spf.policy}`")
            if auth.spf.includes:
                st.markdown(f"**Includes:** {', '.join(auth.spf.includes)}")
            st.markdown(f"**DNS Lookups:** {auth.spf.dns_lookups}/10")

    st.markdown("---")
    st.markdown("##### DKIM (DomainKeys Identified Mail)")

    valid_dkim = [d for d in auth.dkim if d.status == AuthStatus.VALID]
    warning_dkim = [d for d in auth.dkim if d.status == AuthStatus.WARNING]
    missing_dkim = [d for d in auth.dkim if d.status == AuthStatus.MISSING]

    if valid_dkim:
        st.success(f"Found {len(valid_dkim)} valid DKIM selector(s)")
        for dkim in valid_dkim:
            with st.expander(f"✅ Selector: {dkim.selector}"):
                st.markdown(f"**Key Type:** {dkim.key_type}")
                if dkim.key_bits:
                    st.markdown(f"**Key Size:** ~{dkim.key_bits} bits")
                if dkim.raw_record:
                    st.code(dkim.raw_record[:200] + "..." if len(dkim.raw_record) > 200 else dkim.raw_record)
    elif warning_dkim:
        st.warning(f"Found {len(warning_dkim)} DKIM selector(s) with issues")
        for dkim in warning_dkim:
            st.markdown(f"- **{dkim.selector}**: {', '.join(dkim.issues)}")
    else:
        st.error("No valid DKIM records found")

    st.markdown("---")
    st.markdown("##### DMARC (Domain-based Message Authentication)")
    dmarc_status_icon = _get_status_icon(auth.dmarc.status)
    st.markdown(f"{dmarc_status_icon} **Status:** {auth.dmarc.status.value}")

    if auth.dmarc.raw_record:
        policy_colors = {
            "reject": "#22c55e",
            "quarantine": "#f59e0b",
            "none": "#ef4444"
        }
        policy_color = policy_colors.get(auth.dmarc.policy, "#888")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div style="text-align: center; padding: 10px; background: {policy_color}22;
                        border-radius: 8px; border: 1px solid {policy_color};">
                <div style="font-size: 1.2rem; font-weight: bold; color: {policy_color};">
                    {auth.dmarc.policy or 'none'}
                </div>
                <div style="font-size: 0.8rem; color: #888;">Policy</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div style="text-align: center; padding: 10px; background: #1a1a2e; border-radius: 8px;">
                <div style="font-size: 1.2rem; font-weight: bold; color: #ffffff;">
                    {auth.dmarc.percentage}%
                </div>
                <div style="font-size: 0.8rem; color: #888;">Coverage</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            rua_status = "✅" if auth.dmarc.rua else "❌"
            st.markdown(f"""
            <div style="text-align: center; padding: 10px; background: #1a1a2e; border-radius: 8px;">
                <div style="font-size: 1.2rem; font-weight: bold; color: #ffffff;">
                    {rua_status}
                </div>
                <div style="font-size: 0.8rem; color: #888;">Reports (rua)</div>
            </div>
            """, unsafe_allow_html=True)

        with st.expander("View DMARC Record"):
            st.code(auth.dmarc.raw_record, language="text")


def render_blocklist_tab(report):
    """Render blocklist details tab."""
    st.markdown("##### Domain Blocklist Results")

    domain_report = report.blocklist_domain
    listed_domain = [r for r in domain_report.results if r.is_listed]
    clean_domain = [r for r in domain_report.results if not r.is_listed]

    if not listed_domain:
        st.success(f"✅ Domain is clean on all {domain_report.total_checked} checked blocklists")
    else:
        st.error(f"🚨 Domain listed on {len(listed_domain)} blocklist(s)")
        for result in listed_domain:
            st.markdown(f"""
            <div style="background: #ef444422; border-left: 4px solid #ef4444;
                        padding: 10px 15px; border-radius: 4px; margin: 5px 0;">
                <strong>{result.blocklist_name}</strong><br>
                <span style="color: #888;">{result.meaning or 'Listed'}</span>
            </div>
            """, unsafe_allow_html=True)

    with st.expander(f"View all checked blocklists ({domain_report.total_checked})"):
        for result in domain_report.results:
            icon = "🚨" if result.is_listed else "✅"
            st.markdown(f"{icon} {result.blocklist_name} (`{result.blocklist_zone}`)")

    st.markdown("---")
    st.markdown("##### IP Blocklist Results")

    if report.blocklist_ip:
        ip_report = report.blocklist_ip
        listed_ip = [r for r in ip_report.results if r.is_listed]

        st.markdown(f"**Checked IP:** `{report.ip}`")

        if not listed_ip:
            st.success(f"✅ IP is clean on all {ip_report.total_checked} checked blocklists")
        else:
            st.error(f"🚨 IP listed on {len(listed_ip)} blocklist(s)")
            for result in listed_ip:
                st.markdown(f"""
                <div style="background: #ef444422; border-left: 4px solid #ef4444;
                            padding: 10px 15px; border-radius: 4px; margin: 5px 0;">
                    <strong>{result.blocklist_name}</strong><br>
                    <span style="color: #888;">{result.meaning or 'Listed'}</span>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No IP address resolved for blocklist check")


def render_reputation_tab(report):
    """Render reputation details tab."""
    rep = report.reputation

    # Overall reputation
    rep_colors = {
        ReputationLevel.EXCELLENT: "#22c55e",
        ReputationLevel.GOOD: "#84cc16",
        ReputationLevel.NEUTRAL: "#f59e0b",
        ReputationLevel.POOR: "#f97316",
        ReputationLevel.BAD: "#ef4444",
        ReputationLevel.UNKNOWN: "#6b7280"
    }
    rep_color = rep_colors.get(rep.overall_reputation, "#888")

    st.markdown(f"""
    <div style="background: {rep_color}22; border: 2px solid {rep_color};
                border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 20px;">
        <div style="font-size: 1.5rem; font-weight: bold; color: {rep_color};">
            {rep.overall_reputation.value.upper()}
        </div>
        <div style="font-size: 2rem; color: #ffffff;">{rep.overall_score}/100</div>
        <div style="color: #888;">Overall Reputation Score</div>
    </div>
    """, unsafe_allow_html=True)

    # Domain info
    st.markdown("##### Domain Information")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**Domain:** {rep.domain}")
        st.markdown(f"**IP:** {rep.ip or 'Not resolved'}")
        st.markdown(f"**Has Website:** {'✅ Yes' if rep.domain_info.has_website else '❌ No'}")

    with col2:
        if rep.domain_info.mx_records:
            st.markdown("**MX Records:**")
            for mx in rep.domain_info.mx_records[:3]:
                st.markdown(f"- `{mx.priority}` {mx.host}")

    # Reputation sources
    st.markdown("---")
    st.markdown("##### Reputation Sources")

    for source in rep.sources:
        source_color = rep_colors.get(source.reputation, "#888")
        score_text = f" ({source.score}/100)" if source.score else ""

        st.markdown(f"""
        <div style="background: #1a1a2e; border-left: 4px solid {source_color};
                    padding: 10px 15px; border-radius: 4px; margin: 5px 0;">
            <strong>{source.source_name}</strong>
            <span style="color: {source_color}; margin-left: 10px;">
                {source.reputation.value}{score_text}
            </span><br>
            <span style="color: #888; font-size: 0.9rem;">{source.details or ''}</span>
        </div>
        """, unsafe_allow_html=True)

    # Manual check URLs
    st.markdown("---")
    st.markdown("##### Manual Check Links")
    st.markdown("*For deeper analysis, check these external tools:*")

    for name, url in rep.manual_check_urls.items():
        st.markdown(f"- [{name}]({url})")


def render_recommendations_tab(report):
    """Render recommendations tab."""
    if report.recommendations:
        st.markdown("##### Actionable Recommendations")
        for i, rec in enumerate(report.recommendations, 1):
            st.markdown(f"""
            <div style="background: #1a1a2e; border-left: 4px solid #e3af4a;
                        padding: 10px 15px; border-radius: 4px; margin: 5px 0;">
                <strong>{i}.</strong> {rec}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("No immediate recommendations - your setup looks good!")

    st.markdown("---")
    st.markdown("##### Setup Guides")

    with st.expander("📊 Google Postmaster Tools Setup"):
        config = PostmasterToolsConfig()
        st.markdown(config.get_setup_instructions())

    with st.expander("📈 Microsoft SNDS Setup"):
        config = MicrosoftSNDSConfig()
        st.markdown(config.get_setup_instructions())

    with st.expander("🔧 General Deliverability Best Practices"):
        st.markdown("""
**Email Authentication:**
1. Ensure SPF record includes all sending sources
2. Set up DKIM signing with 2048-bit keys
3. Implement DMARC with at least `p=quarantine`
4. Monitor DMARC reports regularly

**List Hygiene:**
1. Use double opt-in for new subscribers
2. Remove bounced addresses immediately
3. Re-engage or remove inactive subscribers
4. Never purchase email lists

**Content Best Practices:**
1. Maintain consistent sending patterns
2. Include clear unsubscribe links
3. Avoid spam trigger words
4. Balance text-to-image ratio

**Infrastructure:**
1. Use dedicated IPs for high-volume sending
2. Warm up new IPs gradually
3. Set up feedback loops with major ISPs
4. Monitor blocklists daily
        """)


def _get_score_color(score: int) -> str:
    """Get color based on score."""
    if score >= 80:
        return "#22c55e"  # Green
    elif score >= 60:
        return "#f59e0b"  # Yellow/Orange
    elif score >= 40:
        return "#f97316"  # Orange
    else:
        return "#ef4444"  # Red


def _get_status_icon(status: AuthStatus) -> str:
    """Get icon for auth status."""
    icons = {
        AuthStatus.VALID: "✅",
        AuthStatus.WARNING: "⚠️",
        AuthStatus.INVALID: "❌",
        AuthStatus.MISSING: "❓",
        AuthStatus.ERROR: "💥"
    }
    return icons.get(status, "❓")
