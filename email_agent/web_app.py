"""
PRAY.COM Email Template Generator - Web Interface
==================================================
A Streamlit-based visual interface for generating email templates
and subject lines.

Run with: streamlit run web_app.py
"""

import streamlit as st
import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Add the current directory to path for imports
current_dir = Path(__file__).parent.absolute()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from template_generator import EmailTemplateGenerator
from subject_line_factory import SubjectLineFactory
from campaign_parser import CampaignBriefParser
from components import EmailComponents


# Page configuration
st.set_page_config(
    page_title="Email Template Generator",
    page_icon="✉️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme matching PRAY.COM brand
st.markdown("""
<style>
    .stApp {
        background-color: #0b0c0e;
    }
    .main-header {
        color: #e3af4a;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        color: #d0d0d8;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .subject-line {
        background-color: #1a1a1c;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 8px 0;
        border-left: 3px solid #e3af4a;
    }
    .ab-variant {
        background-color: #1a1a1c;
        padding: 16px;
        border-radius: 8px;
        margin: 12px 0;
    }
    .hypothesis {
        color: #888;
        font-size: 0.85rem;
        font-style: italic;
    }
    .preview-frame {
        background: white;
        border-radius: 8px;
        padding: 0;
        overflow: hidden;
    }
    .stat-card {
        background-color: #1a1a1c;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
    }
    .stat-value {
        color: #e3af4a;
        font-size: 2rem;
        font-weight: 700;
    }
    .stat-label {
        color: #d0d0d8;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    if "generated_html" not in st.session_state:
        st.session_state.generated_html = None
    if "generated_subjects" not in st.session_state:
        st.session_state.generated_subjects = None
    if "history" not in st.session_state:
        st.session_state.history = []


def main():
    """Main application."""
    init_session_state()

    # Sidebar
    with st.sidebar:
        st.image("https://pray-email-assets.s3.amazonaws.com/pray-logo-white.png", width=120)
        st.markdown("---")

        mode = st.radio(
            "Mode",
            ["📧 Full Email Generator", "✍️ Subject Lines Only", "🧩 Component Builder"],
            index=0
        )

        st.markdown("---")
        st.markdown("### Quick Tips")
        st.markdown("""
        - Be specific in your brief
        - Include target audience
        - Mention the tone you want
        - Specify the CTA
        """)

    # Main content
    st.markdown('<p class="main-header">✉️ Email Template Generator</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Generate EAA-compliant, mobile-responsive HTML emails and subject lines</p>', unsafe_allow_html=True)

    if mode == "📧 Full Email Generator":
        render_full_generator()
    elif mode == "✍️ Subject Lines Only":
        render_subject_generator()
    else:
        render_component_builder()


def render_full_generator():
    """Render the full email generator interface."""
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### Campaign Brief")

        brief = st.text_area(
            "Describe your campaign",
            height=150,
            placeholder="""Example: Launch campaign for our new "Bible in a Year" reading plan.
Target: engaged users who have completed at least one devotional.
Highlight guided daily readings and community aspect.
Tone: inspiring. CTA: Start Your Journey""",
            help="Include campaign goal, target audience, key message, tone, and CTA"
        )

        col_a, col_b = st.columns(2)
        with col_a:
            template_type = st.selectbox(
                "Template Type",
                ["promotional", "newsletter", "announcement", "transactional"],
                help="Choose the email template style"
            )
        with col_b:
            include_personalization = st.checkbox("Include Personalization", value=True)

        # Advanced options
        with st.expander("Advanced Options"):
            headline = st.text_input("Custom Headline (optional)", placeholder="Auto-generated from brief")
            subheadline = st.text_input("Subheadline (optional)")
            cta_text = st.text_input("CTA Button Text", value="Learn More")
            cta_url = st.text_input("CTA URL", value="https://pray.com")

        if st.button("🚀 Generate Email", type="primary", use_container_width=True):
            if brief:
                with st.spinner("Generating your email..."):
                    generate_full_email(
                        brief, template_type, include_personalization,
                        headline, subheadline, cta_text, cta_url
                    )
            else:
                st.warning("Please enter a campaign brief")

    with col2:
        st.markdown("### Preview & Results")

        if st.session_state.generated_html:
            # Tabs for different views
            tab1, tab2, tab3 = st.tabs(["📱 Preview", "📝 Subject Lines", "💻 HTML Code"])

            with tab1:
                st.markdown("#### Email Preview")
                # HTML preview in iframe
                st.components.v1.html(
                    st.session_state.generated_html,
                    height=600,
                    scrolling=True
                )

            with tab2:
                render_subject_lines_display()

            with tab3:
                st.code(st.session_state.generated_html, language="html")
                st.download_button(
                    "📥 Download HTML",
                    st.session_state.generated_html,
                    file_name=f"email_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                    mime="text/html"
                )
        else:
            st.info("Generate an email to see the preview here")


def render_subject_generator():
    """Render the subject line generator interface."""
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### Campaign Context")

        context = st.text_area(
            "Describe your campaign",
            height=120,
            placeholder="Example: New meditation feature launch for daily stress relief",
            help="Describe what the email is about"
        )

        col_a, col_b = st.columns(2)
        with col_a:
            segment = st.selectbox(
                "Target Segment",
                ["general", "new_users", "engaged", "lapsed", "premium"],
                help="Who is this email for?"
            )
        with col_b:
            tone = st.selectbox(
                "Tone",
                ["inspiring", "urgent", "curious", "personal", "celebration"],
                help="What feeling should it evoke?"
            )

        col_c, col_d = st.columns(2)
        with col_c:
            num_variants = st.slider("Number of Variants", 3, 10, 5)
        with col_d:
            include_emoji = st.checkbox("Include Emojis", value=True)

        if st.button("✨ Generate Subject Lines", type="primary", use_container_width=True):
            if context:
                with st.spinner("Crafting subject lines..."):
                    generate_subjects_only(context, segment, tone, num_variants, include_emoji)
            else:
                st.warning("Please enter campaign context")

    with col2:
        st.markdown("### Generated Subject Lines")

        if st.session_state.generated_subjects:
            render_subject_lines_display()

            # Download option
            st.download_button(
                "📥 Download Subject Lines (JSON)",
                json.dumps(st.session_state.generated_subjects, indent=2),
                file_name=f"subjects_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        else:
            st.info("Generate subject lines to see results here")


def render_component_builder():
    """Render the component builder interface."""
    st.markdown("### Component Builder")
    st.markdown("Build individual email components to copy into your templates")

    component_type = st.selectbox(
        "Select Component",
        ["Header", "Hero Text", "CTA Button", "Stat Card", "Feature Grid", "Testimonial", "Footer"]
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        if component_type == "Header":
            logo_url = st.text_input("Logo URL", "https://pray-email-assets.s3.amazonaws.com/pray-logo-white.png")
            if st.button("Generate Component"):
                html = EmailComponents.header(logo_url)
                st.session_state.component_html = html

        elif component_type == "Hero Text":
            headline = st.text_input("Headline", "Your Prayer Journey Awaits")
            subheadline = st.text_input("Subheadline (optional)", "")
            personalized = st.checkbox("Include personalized greeting", value=True)
            if st.button("Generate Component"):
                html = EmailComponents.hero_text(headline, subheadline, personalized)
                st.session_state.component_html = html

        elif component_type == "CTA Button":
            cta_text = st.text_input("Button Text", "Start Now")
            cta_url = st.text_input("Button URL", "https://pray.com")
            style = st.selectbox("Style", ["primary", "secondary"])
            if st.button("Generate Component"):
                html = EmailComponents.cta_button(cta_text, cta_url, style)
                st.session_state.component_html = html

        elif component_type == "Stat Card":
            icon = st.text_input("Icon (emoji)", "🙏")
            value = st.text_input("Value", "100")
            label = st.text_input("Label", "Prayers")
            liquid_var = st.text_input("Liquid Variable (optional)", "")
            if st.button("Generate Component"):
                html = EmailComponents.stat_card(icon, value, label, liquid_var)
                st.session_state.component_html = html

        elif component_type == "Feature Grid":
            st.markdown("##### Add Features")
            num_features = st.number_input("Number of features", 2, 4, 2)
            features = []
            for i in range(num_features):
                with st.expander(f"Feature {i+1}"):
                    icon = st.text_input(f"Icon {i+1}", "🙏", key=f"icon_{i}")
                    title = st.text_input(f"Title {i+1}", f"Feature {i+1}", key=f"title_{i}")
                    desc = st.text_input(f"Description {i+1}", "Description here", key=f"desc_{i}")
                    features.append({"icon": icon, "title": title, "description": desc})
            if st.button("Generate Component"):
                html = EmailComponents.feature_grid(features)
                st.session_state.component_html = html

        elif component_type == "Testimonial":
            quote = st.text_area("Quote", "This app has transformed my prayer life!")
            author = st.text_input("Author", "Sarah M.")
            title = st.text_input("Title (optional)", "Premium Member")
            if st.button("Generate Component"):
                html = EmailComponents.testimonial(quote, author, title)
                st.session_state.component_html = html

        elif component_type == "Footer":
            if st.button("Generate Component"):
                html = EmailComponents.footer()
                st.session_state.component_html = html

    with col2:
        st.markdown("### Component Code")
        if "component_html" in st.session_state and st.session_state.component_html:
            st.code(st.session_state.component_html, language="html")
            st.download_button(
                "📥 Copy Component",
                st.session_state.component_html,
                file_name=f"component_{component_type.lower()}.html",
                mime="text/html"
            )


def generate_full_email(brief, template_type, personalization, headline, subheadline, cta_text, cta_url):
    """Generate full email from brief."""
    parser = CampaignBriefParser()
    generator = EmailTemplateGenerator()
    subject_factory = SubjectLineFactory()

    # Parse brief
    parsed = parser.parse(brief)

    # Override with custom values if provided
    if headline:
        parsed["headline"] = headline
    if subheadline:
        parsed["subheadline"] = subheadline
    if cta_text:
        parsed["cta_text"] = cta_text
    if cta_url:
        parsed["cta_url"] = cta_url

    parsed["personalization"] = {"use_first_name": personalization}

    # Generate HTML
    html = generator.generate(
        campaign_name=parsed.get("campaign_name", "Campaign"),
        headline=parsed.get("headline", ""),
        subheadline=parsed.get("subheadline", ""),
        body_content=parsed.get("body_content", []),
        cta_text=parsed.get("cta_text", "Learn More"),
        cta_url=parsed.get("cta_url", "https://pray.com"),
        template_type=template_type,
        personalization=parsed.get("personalization", {}),
        sections=parsed.get("sections", [])
    )

    # Generate subject lines
    subjects = subject_factory.generate(
        context=brief,
        segment=parsed.get("segment", "general"),
        tone=parsed.get("tone", "inspiring"),
        num_variants=5
    )

    st.session_state.generated_html = html
    st.session_state.generated_subjects = subjects

    # Add to history
    st.session_state.history.append({
        "timestamp": datetime.now().isoformat(),
        "brief": brief,
        "type": template_type
    })


def generate_subjects_only(context, segment, tone, num_variants, include_emoji):
    """Generate subject lines only."""
    factory = SubjectLineFactory()

    subjects = factory.generate(
        context=context,
        segment=segment,
        tone=tone,
        num_variants=num_variants,
        include_emoji=include_emoji
    )

    st.session_state.generated_subjects = subjects


def render_subject_lines_display():
    """Render subject lines in a nice format."""
    subjects = st.session_state.generated_subjects

    if not subjects:
        return

    st.markdown("#### Primary Subject Lines")
    for i, line in enumerate(subjects.get("primary", []), 1):
        st.markdown(f"""
        <div class="subject-line">
            <strong>{i}.</strong> {line}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("#### A/B Test Variants")
    for i, variant in enumerate(subjects.get("ab_variants", []), 1):
        st.markdown(f"""
        <div class="ab-variant">
            <strong>Test {i}</strong><br>
            <strong>A:</strong> {variant['a']}<br>
            <strong>B:</strong> {variant['b']}<br>
            <p class="hypothesis">💡 {variant['hypothesis']}</p>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
