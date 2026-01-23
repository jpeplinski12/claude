#!/usr/bin/env python3
"""
PRAY.COM Email Template Generator - Streamlit Web App
======================================================
User-friendly web interface for generating email templates and subject lines.
"""

import streamlit as st
import json
from datetime import datetime
from pathlib import Path
import base64

from email_agent import EmailAgent
from subject_line_factory import SubjectLineFactory
from template_generator import EmailTemplateGenerator
from copywriting_agent import CopywritingAgent
import os


# Page configuration
st.set_page_config(
    page_title="PRAY.COM Email Template Generator",
    page_icon="✉️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #e3af4a;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #d0d0d8;
        margin-bottom: 2rem;
    }
    .subject-line {
        background-color: #1a1a1c;
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 8px;
        border-left: 4px solid #e3af4a;
    }
    .ab-variant {
        background-color: #2a2a2c;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 12px;
    }
    .success-box {
        background-color: #1a3a1a;
        padding: 16px;
        border-radius: 8px;
        border-left: 4px solid #4ade80;
        margin: 16px 0;
    }
    .stTextArea textarea {
        font-family: 'Monaco', 'Menlo', monospace;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)


def download_button(content: str, filename: str, label: str, mime_type: str = "text/html"):
    """Create a download button for generated content."""
    b64 = base64.b64encode(content.encode()).decode()
    href = f'<a href="data:{mime_type};base64,{b64}" download="{filename}" style="display:inline-block;padding:0.5rem 1rem;background-color:#e3af4a;color:#000;text-decoration:none;border-radius:8px;font-weight:600;">{label}</a>'
    return href


def main():
    # Initialize session state
    if 'generated_html' not in st.session_state:
        st.session_state.generated_html = None
    if 'generated_subjects' not in st.session_state:
        st.session_state.generated_subjects = None
    if 'campaign_name' not in st.session_state:
        st.session_state.campaign_name = ""
    if 'use_ai_copywriting' not in st.session_state:
        st.session_state.use_ai_copywriting = bool(os.getenv("ANTHROPIC_API_KEY"))

    # Header
    st.markdown('<div class="main-header">✉️ PRAY.COM Email Template Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Generate EAA-compliant, mobile-responsive email templates and benefit-driven subject lines for Braze campaigns.</div>', unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.image("https://pray-email-assets.s3.amazonaws.com/pray-logo-white.png", width=150)
        st.markdown("---")

        mode = st.radio(
            "Select Mode",
            ["📧 Full Email Generation", "✏️ Subject Lines Only", "🎨 Custom Template"],
            help="Choose what you want to generate"
        )

        st.markdown("---")

        # AI Copywriting toggle
        api_key_set = bool(os.getenv("ANTHROPIC_API_KEY"))
        if api_key_set:
            st.session_state.use_ai_copywriting = st.checkbox(
                "🤖 Use AI Copywriting",
                value=True,
                help="Uses Claude AI to generate brand-aligned copy that matches PRAY.COM's tone of voice"
            )
            if st.session_state.use_ai_copywriting:
                st.success("✨ AI copywriting enabled")
        else:
            st.warning("⚠️ Set ANTHROPIC_API_KEY to enable AI copywriting")
            st.session_state.use_ai_copywriting = False

        st.markdown("---")
        st.markdown("### 📚 Resources")
        st.markdown("""
        - [Email Best Practices](https://pray.com)
        - [Braze Documentation](https://www.braze.com/docs)
        - [Subject Line Guide](https://pray.com)
        """)

    # Main content area
    if mode == "📧 Full Email Generation":
        show_full_generation()
    elif mode == "✏️ Subject Lines Only":
        show_subject_lines()
    else:
        show_custom_template()


def show_full_generation():
    """Full email generation from campaign brief."""
    st.markdown("## 📧 Full Email Generation")
    st.markdown("Generate a complete email package from your campaign brief.")

    # Template type selection
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### Campaign Brief")
        brief = st.text_area(
            "Paste your campaign brief here",
            height=400,
            placeholder="""Example brief:

Project Title: Abandon Cart Email Series - PRAY.COM Premium Subscription

Overview: 3-email automated sequence to re-engage users who didn't complete their premium subscription purchase.

Target Audience: Age 30-65, spiritually curious to practicing Christians, hesitant at checkout.

Email 1 (1 Hour): Gentle reminder
Subject: You're so close to unlimited prayer & peace
Body: Hi {{first_name}}, we noticed you started to join PRAY Premium...

[Include full email copy, CTAs, and desired structure]
""",
            help="Include campaign objective, target audience, tone, key messages, and CTAs"
        )

    with col2:
        # Import template types
        from template_generator import TEMPLATE_TYPES

        # Create friendly display names
        template_options = {
            "plain_text": "📄 Plain Text / Triggered",
            "premium": "✨ Premium / Subscription",
            "sponsored": "🤝 Sponsored / Partner",
            "holiday": "🎄 Holiday / Seasonal",
            "cart_abandonment": "🛒 Cart Abandonment",
            "newsletter": "📰 Newsletter / Digest",
            "announcement": "📢 Announcement / News"
        }

        template_type = st.selectbox(
            "Template Type",
            list(template_options.keys()),
            format_func=lambda x: template_options[x],
            help="Choose the type of email template"
        )

        # Show template description
        if template_type in TEMPLATE_TYPES:
            st.info(TEMPLATE_TYPES[template_type]["description"])

        # Theme selector
        theme = st.selectbox(
            "Theme",
            ["auto", "light", "dark"],
            help="auto = use template type's recommended theme"
        )

        num_variants = st.number_input(
            "Subject Line Variants",
            min_value=3,
            max_value=10,
            value=5,
            help="Number of subject line variations to generate"
        )

    # Generate button
    if st.button("🚀 Generate Email Package", type="primary", use_container_width=True):
        if not brief.strip():
            st.error("⚠️ Please provide a campaign brief.")
        else:
            with st.spinner("Generating your email package..."):
                try:
                    # Determine theme to use
                    theme_to_use = None if theme == "auto" else theme
                    actual_theme = theme if theme != "auto" else TEMPLATE_TYPES[template_type]["theme"]

                    # Parse brief first
                    from campaign_parser import CampaignBriefParser
                    parser = CampaignBriefParser()
                    parsed = parser.parse(brief)

                    # Use AI copywriting if enabled
                    if st.session_state.use_ai_copywriting:
                        try:
                            copywriter = CopywritingAgent()

                            # Generate AI copy
                            copy_result = copywriter.generate_email_copy(
                                campaign_brief=brief,
                                campaign_type=template_type,
                                segment=parsed.get("segment", "general"),
                                tone=parsed.get("tone", "inspiring")
                            )

                            # Use AI-generated copy
                            headline = copy_result["headline"]
                            subheadline = copy_result["subheadline"]
                            body_content = copy_result["body_paragraphs"]
                            cta_text = copy_result["cta_text"]

                            # Generate AI subject lines
                            subjects = copywriter.generate_subject_lines(
                                context=brief,
                                segment=parsed.get("segment", "general"),
                                tone=parsed.get("tone", "inspiring"),
                                num_variants=num_variants
                            )

                            # Show validation score
                            if copy_result["validation"]["score"] >= 80:
                                st.success(f"✨ AI copywriting quality score: {copy_result['validation']['score']}/100")
                            elif copy_result["validation"]["score"] >= 60:
                                st.info(f"💡 AI copywriting quality score: {copy_result['validation']['score']}/100")
                            else:
                                st.warning(f"⚠️ Quality score: {copy_result['validation']['score']}/100 - May need refinement")

                        except Exception as e:
                            st.warning(f"AI generation failed: {str(e)}. Using template-based generation.")
                            headline = parsed.get("headline", "")
                            subheadline = parsed.get("subheadline", "")
                            body_content = parsed.get("body_content", [])
                            cta_text = parsed.get("cta_text", "Learn More")

                            factory = SubjectLineFactory()
                            subjects = factory.generate(
                                context=parsed.get("context", brief),
                                segment=parsed.get("segment", "general"),
                                tone=parsed.get("tone", "inspiring"),
                                num_variants=num_variants
                            )
                    else:
                        # Use template-based generation
                        headline = parsed.get("headline", "")
                        subheadline = parsed.get("subheadline", "")
                        body_content = parsed.get("body_content", [])
                        cta_text = parsed.get("cta_text", "Learn More")

                        factory = SubjectLineFactory()
                        subjects = factory.generate(
                            context=parsed.get("context", brief),
                            segment=parsed.get("segment", "general"),
                            tone=parsed.get("tone", "inspiring"),
                            num_variants=num_variants
                        )

                    # Generate HTML template
                    generator = EmailTemplateGenerator(theme=actual_theme)
                    html = generator.generate(
                        campaign_name=parsed.get("campaign_name", "Campaign"),
                        headline=headline,
                        subheadline=subheadline,
                        body_content=body_content,
                        cta_text=cta_text,
                        cta_url=parsed.get("cta_url", "https://pray.com"),
                        template_type=template_type,
                        theme=theme_to_use
                    )

                    st.session_state.generated_html = html
                    st.session_state.generated_subjects = subjects
                    st.session_state.campaign_name = parsed.get("campaign_name", "campaign")

                    st.success("✅ Email package generated successfully!")
                except Exception as e:
                    st.error(f"❌ Error generating email: {str(e)}")

    # Display results
    if st.session_state.generated_html or st.session_state.generated_subjects:
        st.markdown("---")
        st.markdown("## 📊 Generated Content")

        # Subject lines
        if st.session_state.generated_subjects:
            st.markdown("### ✏️ Subject Lines")

            subjects = st.session_state.generated_subjects

            st.markdown("#### Primary Options")
            for i, subject in enumerate(subjects.get("primary", []), 1):
                st.markdown(f'<div class="subject-line"><strong>{i}.</strong> {subject}</div>', unsafe_allow_html=True)

            st.markdown("#### A/B Test Variants")
            for i, variant in enumerate(subjects.get("ab_variants", []), 1):
                st.markdown(f"""
                <div class="ab-variant">
                    <strong>Variant {i}:</strong><br>
                    <strong>A:</strong> {variant['a']}<br>
                    <strong>B:</strong> {variant['b']}<br>
                    <em>Hypothesis:</em> {variant['hypothesis']}
                </div>
                """, unsafe_allow_html=True)

            # Download subject lines
            subjects_json = json.dumps(subjects, indent=2)
            st.markdown(
                download_button(
                    subjects_json,
                    f"{st.session_state.campaign_name}_subjects.json",
                    "📥 Download Subject Lines (JSON)",
                    "application/json"
                ),
                unsafe_allow_html=True
            )

        # HTML preview and download
        if st.session_state.generated_html:
            st.markdown("### 🎨 HTML Template")

            tab1, tab2 = st.tabs(["Preview", "HTML Code"])

            with tab1:
                st.markdown("**Email Preview:**")
                st.components.v1.html(st.session_state.generated_html, height=800, scrolling=True)

            with tab2:
                st.code(st.session_state.generated_html, language="html")

            # Download HTML
            st.markdown(
                download_button(
                    st.session_state.generated_html,
                    f"{st.session_state.campaign_name}.html",
                    "📥 Download HTML Template"
                ),
                unsafe_allow_html=True
            )


def show_subject_lines():
    """Subject line generation only."""
    st.markdown("## ✏️ Subject Line Factory")
    st.markdown("Generate benefit-driven, curiosity-sparking subject lines.")

    col1, col2 = st.columns([2, 1])

    with col1:
        context = st.text_area(
            "Campaign Context/Description",
            height=200,
            placeholder="Example: Abandoned cart email series for premium subscription. Target users who started checkout but didn't complete. Focus on value, urgency, and overcoming objections.",
            help="Describe your campaign's purpose, audience, and key messages"
        )

    with col2:
        segment = st.selectbox(
            "Audience Segment",
            ["general", "new_users", "engaged", "lapsed", "premium"],
            help="Target audience segment"
        )

        tone = st.selectbox(
            "Tone",
            ["inspiring", "urgent", "curious", "personal", "celebration"],
            help="Desired tone for subject lines"
        )

        num_variants = st.number_input(
            "Number of Variants",
            min_value=3,
            max_value=10,
            value=5,
            help="How many subject line variations to generate"
        )

    if st.button("✨ Generate Subject Lines", type="primary", use_container_width=True):
        if not context.strip():
            st.error("⚠️ Please provide campaign context.")
        else:
            with st.spinner("Generating subject lines..."):
                try:
                    # Use AI copywriting if enabled
                    if st.session_state.use_ai_copywriting:
                        try:
                            copywriter = CopywritingAgent()
                            subjects = copywriter.generate_subject_lines(
                                context=context,
                                segment=segment,
                                tone=tone,
                                num_variants=num_variants
                            )
                            st.success("✅ AI-generated subject lines ready!")
                        except Exception as e:
                            st.warning(f"AI generation failed: {str(e)}. Using template-based generation.")
                            factory = SubjectLineFactory()
                            subjects = factory.generate(context, segment, tone, num_variants)
                    else:
                        factory = SubjectLineFactory()
                        subjects = factory.generate(context, segment, tone, num_variants)

                    st.session_state.generated_subjects = subjects
                    st.success("✅ Subject lines generated successfully!")
                except Exception as e:
                    st.error(f"❌ Error generating subject lines: {str(e)}")

    # Display subject lines
    if st.session_state.generated_subjects:
        st.markdown("---")
        subjects = st.session_state.generated_subjects

        st.markdown("### Primary Subject Lines")
        for i, subject in enumerate(subjects.get("primary", []), 1):
            st.markdown(f'<div class="subject-line"><strong>{i}.</strong> {subject}</div>', unsafe_allow_html=True)

        st.markdown("### A/B Test Variants")
        for i, variant in enumerate(subjects.get("ab_variants", []), 1):
            st.markdown(f"""
            <div class="ab-variant">
                <strong>Variant {i}:</strong><br>
                <strong>A:</strong> {variant['a']}<br>
                <strong>B:</strong> {variant['b']}<br>
                <em>Hypothesis:</em> {variant['hypothesis']}
            </div>
            """, unsafe_allow_html=True)

        # Download
        subjects_json = json.dumps(subjects, indent=2)
        st.markdown(
            download_button(
                subjects_json,
                f"subject_lines_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "📥 Download Subject Lines (JSON)",
                "application/json"
            ),
            unsafe_allow_html=True
        )


def show_custom_template():
    """Custom template builder."""
    st.markdown("## 🎨 Custom Template Builder")
    st.markdown("Build a template with custom options.")

    col1, col2 = st.columns(2)

    with col1:
        campaign_name = st.text_input("Campaign Name", placeholder="Summer Campaign 2026")
        headline = st.text_input("Main Headline", placeholder="Your Spiritual Journey Awaits")
        subheadline = st.text_input("Subheadline (optional)", placeholder="Discover peace through prayer")

        st.markdown("**Body Content**")
        body_para_1 = st.text_area("Paragraph 1", height=100, placeholder="First paragraph...")
        body_para_2 = st.text_area("Paragraph 2", height=100, placeholder="Second paragraph (optional)...")
        body_para_3 = st.text_area("Paragraph 3", height=100, placeholder="Third paragraph (optional)...")

    with col2:
        cta_text = st.text_input("CTA Button Text", value="Learn More", placeholder="Start Your Journey")
        cta_url = st.text_input("CTA URL", value="https://pray.com", placeholder="https://pray.com/premium")

        # Import template types
        from template_generator import TEMPLATE_TYPES

        template_options = {
            "plain_text": "📄 Plain Text / Triggered",
            "premium": "✨ Premium / Subscription",
            "sponsored": "🤝 Sponsored / Partner",
            "holiday": "🎄 Holiday / Seasonal",
            "cart_abandonment": "🛒 Cart Abandonment",
            "newsletter": "📰 Newsletter / Digest",
            "announcement": "📢 Announcement / News"
        }

        template_type = st.selectbox(
            "Template Type",
            list(template_options.keys()),
            format_func=lambda x: template_options[x],
            help="Choose template style"
        )

        theme = st.selectbox(
            "Theme",
            ["auto", "light", "dark"],
            help="auto = use template type's recommended theme"
        )

        use_personalization = st.checkbox("Use First Name Personalization", value=True)
        include_stats = st.checkbox("Include Stat Card", value=False)

    if st.button("🎨 Generate Template", type="primary", use_container_width=True):
        if not headline.strip():
            st.error("⚠️ Please provide a headline.")
        else:
            with st.spinner("Generating template..."):
                try:
                    # Determine theme
                    theme_to_use = None if theme == "auto" else theme
                    actual_theme = theme if theme != "auto" else TEMPLATE_TYPES[template_type]["theme"]

                    generator = EmailTemplateGenerator(theme=actual_theme)

                    body_content = [p for p in [body_para_1, body_para_2, body_para_3] if p.strip()]

                    personalization = {
                        "use_first_name": use_personalization,
                        "use_stats": include_stats
                    }

                    sections = []
                    if include_stats:
                        sections.append({
                            "type": "stat_card",
                            "icon": "📊",
                            "value": "{{custom_attribute.${total_minutes_listened}}}",
                            "label": "Your Progress",
                            "liquid_var": "total_minutes_listened"
                        })

                    html = generator.generate(
                        campaign_name=campaign_name or "Campaign",
                        headline=headline,
                        subheadline=subheadline,
                        body_content=body_content,
                        cta_text=cta_text,
                        cta_url=cta_url,
                        template_type=template_type,
                        personalization=personalization,
                        sections=sections,
                        theme=theme_to_use
                    )

                    st.session_state.generated_html = html
                    st.session_state.campaign_name = campaign_name or "campaign"
                    st.success("✅ Template generated successfully!")
                except Exception as e:
                    st.error(f"❌ Error generating template: {str(e)}")

    # Display template
    if st.session_state.generated_html:
        st.markdown("---")
        st.markdown("### 🎨 Generated Template")

        tab1, tab2 = st.tabs(["Preview", "HTML Code"])

        with tab1:
            st.components.v1.html(st.session_state.generated_html, height=800, scrolling=True)

        with tab2:
            st.code(st.session_state.generated_html, language="html")

        # Download
        st.markdown(
            download_button(
                st.session_state.generated_html,
                f"{st.session_state.campaign_name}.html",
                "📥 Download HTML Template"
            ),
            unsafe_allow_html=True
        )


if __name__ == "__main__":
    main()
