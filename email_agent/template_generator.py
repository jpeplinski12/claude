"""
Email Template Generator
========================
Generates EAA-compliant, mobile-responsive HTML email templates
ready for Braze with Liquid templating support.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class EmailConfig:
    """Configuration for email template generation."""
    # Brand colors
    bg_color: str = "#0b0c0e"
    primary_color: str = "#e3af4a"  # Gold
    text_color: str = "#ffffff"
    secondary_text: str = "#d0d0d8"
    divider_color: str = "#3a3a3c"

    # Typography
    font_family: str = "'Satoshi', 'Helvetica Neue', Helvetica, Arial, sans-serif"
    heading_size: str = "32px"
    body_size: str = "16px"

    # Layout
    email_width: str = "640px"
    mobile_breakpoint: str = "660px"
    small_mobile_breakpoint: str = "480px"

    # Braze settings
    preference_center: str = "{{preference_center.${PRAY-Preference-Center}}}"
    unsubscribe_url: str = "{{${set_user_to_unsubscribed_url}}}"


class EmailTemplateGenerator:
    """Generates mobile-responsive HTML email templates for Braze."""

    def __init__(self, config: Optional[EmailConfig] = None):
        self.config = config or EmailConfig()

    def generate(
        self,
        campaign_name: str,
        headline: str,
        subheadline: str = "",
        body_content: List[str] = None,
        cta_text: str = "Learn More",
        cta_url: str = "https://pray.com",
        template_type: str = "promotional",
        personalization: Dict = None,
        sections: List[Dict] = None
    ) -> str:
        """
        Generate a complete HTML email template.

        Args:
            campaign_name: Name of the campaign (for comments/tracking)
            headline: Main headline text
            subheadline: Optional subheadline
            body_content: List of paragraph strings
            cta_text: Call-to-action button text
            cta_url: CTA destination URL
            template_type: promotional, newsletter, announcement, transactional
            personalization: Dict of Braze personalization options
            sections: Additional content sections

        Returns:
            Complete HTML email template string
        """
        body_content = body_content or []
        personalization = personalization or {}
        sections = sections or []

        # Build template parts
        doctype = self._generate_doctype()
        head = self._generate_head(campaign_name)
        body_start = self._generate_body_start()
        header = self._generate_header()
        hero = self._generate_hero(headline, subheadline, personalization)
        main_content = self._generate_main_content(body_content)
        cta_section = self._generate_cta(cta_text, cta_url)
        additional_sections = self._generate_sections(sections)
        footer = self._generate_footer()
        body_end = self._generate_body_end()

        # Assemble template
        template = f"""{doctype}
{head}
{body_start}
{header}
{hero}
{main_content}
{cta_section}
{additional_sections}
{footer}
{body_end}
</html>"""

        return template

    def _generate_doctype(self) -> str:
        """Generate XHTML doctype for email compatibility."""
        return """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">"""

    def _generate_head(self, campaign_name: str) -> str:
        """Generate the head section with styles and meta tags."""
        return f"""<head>
    <!--[if gte mso 9]>
    <xml>
        <o:OfficeDocumentSettings>
            <o:AllowPNG/>
            <o:PixelsPerInch>96</o:PixelsPerInch>
        </o:OfficeDocumentSettings>
    </xml>
    <![endif]-->
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <meta name="x-apple-disable-message-reformatting" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <title>{campaign_name}</title>

    <!-- Custom Font -->
    <link href="https://api.fontshare.com/v2/css?f[]=satoshi@400,500,700&display=swap" rel="stylesheet">

    <style type="text/css">
        /* Reset styles */
        body, table, td, p, a, li, blockquote {{
            -webkit-text-size-adjust: 100%;
            -ms-text-size-adjust: 100%;
        }}
        table, td {{
            mso-table-lspace: 0pt;
            mso-table-rspace: 0pt;
            border-collapse: collapse !important;
        }}
        img {{
            -ms-interpolation-mode: bicubic;
            border: 0;
            height: auto;
            line-height: 100%;
            outline: none;
            text-decoration: none;
        }}
        body {{
            margin: 0 !important;
            padding: 0 !important;
            width: 100% !important;
            background-color: {self.config.bg_color};
        }}

        /* Typography */
        .email-body {{
            font-family: {self.config.font_family};
            font-size: {self.config.body_size};
            line-height: 1.6;
            color: {self.config.text_color};
        }}

        /* Links */
        a {{
            color: {self.config.primary_color};
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}

        /* Button styles */
        .button {{
            background-color: {self.config.primary_color};
            border-radius: 8px;
            color: #000000 !important;
            display: inline-block;
            font-family: {self.config.font_family};
            font-size: 16px;
            font-weight: 600;
            line-height: 1;
            padding: 16px 32px;
            text-align: center;
            text-decoration: none;
            -webkit-text-size-adjust: none;
        }}

        /* Responsive styles */
        @media only screen and (max-width: {self.config.mobile_breakpoint}) {{
            .email-container {{
                width: 100% !important;
                max-width: 100% !important;
            }}
            .mobile-padding {{
                padding-left: 24px !important;
                padding-right: 24px !important;
            }}
            .mobile-stack {{
                display: block !important;
                width: 100% !important;
            }}
            .mobile-center {{
                text-align: center !important;
            }}
            .mobile-hide {{
                display: none !important;
            }}
            .headline {{
                font-size: 28px !important;
                line-height: 1.2 !important;
            }}
        }}

        @media only screen and (max-width: {self.config.small_mobile_breakpoint}) {{
            .mobile-padding {{
                padding-left: 16px !important;
                padding-right: 16px !important;
            }}
            .headline {{
                font-size: 24px !important;
            }}
            .body-text {{
                font-size: 15px !important;
            }}
        }}

        /* Dark mode support */
        @media (prefers-color-scheme: dark) {{
            .email-body {{
                background-color: {self.config.bg_color} !important;
            }}
        }}
    </style>

    <!--[if mso]>
    <style type="text/css">
        body, table, td {{
            font-family: Arial, Helvetica, sans-serif !important;
        }}
    </style>
    <![endif]-->
</head>"""

    def _generate_body_start(self) -> str:
        """Generate the body opening with wrapper table."""
        return f"""<body style="margin: 0; padding: 0; background-color: {self.config.bg_color};">
    <!-- Preheader text (hidden) -->
    <div style="display: none; max-height: 0; overflow: hidden;">
        {{{{ preview_text }}}}
        &nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;
    </div>

    <!-- Email wrapper -->
    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: {self.config.bg_color};">
        <tr>
            <td align="center" style="padding: 20px 0;">
                <!-- Email container -->
                <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="{self.config.email_width}" class="email-container" style="max-width: {self.config.email_width}; width: 100%;">"""

    def _generate_header(self) -> str:
        """Generate the email header with logo."""
        return f"""
                    <!-- Header -->
                    <tr>
                        <td align="center" style="padding: 40px 24px 20px;" class="mobile-padding">
                            <a href="https://pray.com" target="_blank">
                                <img src="https://pray-email-assets.s3.amazonaws.com/pray-logo-white.png"
                                     alt="PRAY.COM"
                                     width="120"
                                     style="display: block; max-width: 120px; height: auto;"
                                />
                            </a>
                        </td>
                    </tr>"""

    def _generate_hero(self, headline: str, subheadline: str, personalization: Dict) -> str:
        """Generate the hero section with headline and personalized greeting."""
        # Build personalized greeting
        greeting = ""
        if personalization.get("use_first_name", True):
            greeting = """
                            <p style="margin: 0 0 16px; font-size: 18px; color: {secondary};">
                                {{% if {{{{custom_attribute.${{first_name}}}}}} != blank %}}
                                    Hi {{{{custom_attribute.${{first_name}}}}}},
                                {{% else %}}
                                    Hi there,
                                {{% endif %}}
                            </p>""".format(secondary=self.config.secondary_text)

        subhead_html = ""
        if subheadline:
            subhead_html = f"""
                            <p style="margin: 16px 0 0; font-size: 18px; color: {self.config.secondary_text}; line-height: 1.5;">
                                {subheadline}
                            </p>"""

        return f"""
                    <!-- Hero Section -->
                    <tr>
                        <td style="padding: 20px 40px 30px;" class="mobile-padding">
                            {greeting}
                            <h1 class="headline" style="margin: 0; font-size: {self.config.heading_size}; font-weight: 700; color: {self.config.text_color}; line-height: 1.2;">
                                {headline}
                            </h1>
                            {subhead_html}
                        </td>
                    </tr>"""

    def _generate_main_content(self, body_content: List[str]) -> str:
        """Generate the main body content section."""
        if not body_content:
            return ""

        paragraphs = ""
        for para in body_content:
            paragraphs += f"""
                            <p class="body-text" style="margin: 0 0 16px; font-size: 16px; color: {self.config.secondary_text}; line-height: 1.6;">
                                {para}
                            </p>"""

        return f"""
                    <!-- Main Content -->
                    <tr>
                        <td style="padding: 0 40px 30px;" class="mobile-padding">
                            {paragraphs}
                        </td>
                    </tr>"""

    def _generate_cta(self, cta_text: str, cta_url: str) -> str:
        """Generate the CTA button section with Outlook VML fallback."""
        return f"""
                    <!-- CTA Button -->
                    <tr>
                        <td align="center" style="padding: 10px 40px 40px;" class="mobile-padding">
                            <!--[if mso]>
                            <v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="urn:schemas-microsoft-com:office:word" href="{cta_url}" style="height:52px;v-text-anchor:middle;width:200px;" arcsize="15%" stroke="f" fillcolor="{self.config.primary_color}">
                                <w:anchorlock/>
                                <center style="color:#000000;font-family:Arial,sans-serif;font-size:16px;font-weight:bold;">{cta_text}</center>
                            </v:roundrect>
                            <![endif]-->
                            <!--[if !mso]><!-->
                            <a href="{cta_url}"
                               target="_blank"
                               class="button"
                               style="background-color: {self.config.primary_color}; border-radius: 8px; color: #000000; display: inline-block; font-family: {self.config.font_family}; font-size: 16px; font-weight: 600; padding: 16px 40px; text-align: center; text-decoration: none;"
                               universal="true">
                                {cta_text}
                            </a>
                            <!--<![endif]-->
                        </td>
                    </tr>"""

    def _generate_sections(self, sections: List[Dict]) -> str:
        """Generate additional content sections."""
        if not sections:
            return ""

        sections_html = ""
        for section in sections:
            section_type = section.get("type", "text")

            if section_type == "divider":
                sections_html += self._generate_divider()
            elif section_type == "stat_card":
                sections_html += self._generate_stat_card(section)
            elif section_type == "image":
                sections_html += self._generate_image_section(section)
            elif section_type == "text":
                sections_html += self._generate_text_section(section)
            elif section_type == "feature_grid":
                sections_html += self._generate_feature_grid(section)

        return sections_html

    def _generate_divider(self) -> str:
        """Generate a divider line."""
        return f"""
                    <!-- Divider -->
                    <tr>
                        <td style="padding: 10px 40px;" class="mobile-padding">
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                                <tr>
                                    <td style="border-top: 1px solid {self.config.divider_color}; font-size: 0; line-height: 0;">&nbsp;</td>
                                </tr>
                            </table>
                        </td>
                    </tr>"""

    def _generate_stat_card(self, section: Dict) -> str:
        """Generate a stat card section."""
        icon = section.get("icon", "")
        value = section.get("value", "")
        label = section.get("label", "")
        liquid_var = section.get("liquid_var", "")

        # If liquid variable provided, use conditional rendering
        value_display = value
        if liquid_var:
            value_display = f"{{{{{{custom_attribute.${{{liquid_var}}}}}}}}}"

        return f"""
                    <!-- Stat Card -->
                    <tr>
                        <td style="padding: 20px 40px;" class="mobile-padding">
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #1a1a1c; border-radius: 12px;">
                                <tr>
                                    <td style="padding: 24px; text-align: center;">
                                        <div style="font-size: 32px; margin-bottom: 8px;">{icon}</div>
                                        <div style="font-size: 36px; font-weight: 700; color: {self.config.primary_color}; margin-bottom: 4px;">
                                            {value_display}
                                        </div>
                                        <div style="font-size: 14px; color: {self.config.secondary_text}; text-transform: uppercase; letter-spacing: 1px;">
                                            {label}
                                        </div>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>"""

    def _generate_image_section(self, section: Dict) -> str:
        """Generate an image section."""
        src = section.get("src", "")
        alt = section.get("alt", "")
        link = section.get("link", "")

        img_html = f"""<img src="{src}" alt="{alt}" width="560" style="display: block; width: 100%; max-width: 560px; height: auto; border-radius: 12px;" />"""

        if link:
            img_html = f"""<a href="{link}" target="_blank">{img_html}</a>"""

        return f"""
                    <!-- Image Section -->
                    <tr>
                        <td align="center" style="padding: 20px 40px;" class="mobile-padding">
                            {img_html}
                        </td>
                    </tr>"""

    def _generate_text_section(self, section: Dict) -> str:
        """Generate a text section with optional heading."""
        heading = section.get("heading", "")
        content = section.get("content", "")

        heading_html = ""
        if heading:
            heading_html = f"""
                            <h2 style="margin: 0 0 16px; font-size: 24px; font-weight: 600; color: {self.config.text_color};">
                                {heading}
                            </h2>"""

        return f"""
                    <!-- Text Section -->
                    <tr>
                        <td style="padding: 20px 40px;" class="mobile-padding">
                            {heading_html}
                            <p style="margin: 0; font-size: 16px; color: {self.config.secondary_text}; line-height: 1.6;">
                                {content}
                            </p>
                        </td>
                    </tr>"""

    def _generate_feature_grid(self, section: Dict) -> str:
        """Generate a feature grid section."""
        features = section.get("features", [])

        if not features:
            return ""

        feature_cells = ""
        for feature in features:
            icon = feature.get("icon", "")
            title = feature.get("title", "")
            desc = feature.get("description", "")

            feature_cells += f"""
                                <td width="50%" style="padding: 12px; vertical-align: top;" class="mobile-stack">
                                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                        <tr>
                                            <td style="background-color: #1a1a1c; border-radius: 8px; padding: 20px; text-align: center;">
                                                <div style="font-size: 28px; margin-bottom: 12px;">{icon}</div>
                                                <div style="font-size: 16px; font-weight: 600; color: {self.config.text_color}; margin-bottom: 8px;">{title}</div>
                                                <div style="font-size: 14px; color: {self.config.secondary_text};">{desc}</div>
                                            </td>
                                        </tr>
                                    </table>
                                </td>"""

        return f"""
                    <!-- Feature Grid -->
                    <tr>
                        <td style="padding: 20px 28px;" class="mobile-padding">
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                                <tr>
                                    {feature_cells}
                                </tr>
                            </table>
                        </td>
                    </tr>"""

    def _generate_footer(self) -> str:
        """Generate the email footer with social links and legal text."""
        return f"""
                    <!-- Divider -->
                    <tr>
                        <td style="padding: 30px 40px 10px;" class="mobile-padding">
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                                <tr>
                                    <td style="border-top: 1px solid {self.config.divider_color}; font-size: 0; line-height: 0;">&nbsp;</td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- Social Icons -->
                    <tr>
                        <td align="center" style="padding: 20px 40px;" class="mobile-padding">
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0">
                                <tr>
                                    <td style="padding: 0 8px;">
                                        <a href="https://www.instagram.com/pray" target="_blank">
                                            <img src="https://pray-email-assets.s3.amazonaws.com/icon-instagram.png" alt="Instagram" width="32" height="32" style="display: block;" />
                                        </a>
                                    </td>
                                    <td style="padding: 0 8px;">
                                        <a href="https://www.facebook.com/praydotcom" target="_blank">
                                            <img src="https://pray-email-assets.s3.amazonaws.com/icon-facebook.png" alt="Facebook" width="32" height="32" style="display: block;" />
                                        </a>
                                    </td>
                                    <td style="padding: 0 8px;">
                                        <a href="https://twitter.com/pray" target="_blank">
                                            <img src="https://pray-email-assets.s3.amazonaws.com/icon-twitter.png" alt="Twitter" width="32" height="32" style="display: block;" />
                                        </a>
                                    </td>
                                    <td style="padding: 0 8px;">
                                        <a href="https://www.youtube.com/praydotcom" target="_blank">
                                            <img src="https://pray-email-assets.s3.amazonaws.com/icon-youtube.png" alt="YouTube" width="32" height="32" style="display: block;" />
                                        </a>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- Footer Text -->
                    <tr>
                        <td align="center" style="padding: 10px 40px 40px;" class="mobile-padding">
                            <p style="margin: 0 0 8px; font-size: 12px; color: #888888;">
                                &copy; {{{{\"now\" | date: \"%Y\"}}}} Pray.com, Inc. All rights reserved.
                            </p>
                            <p style="margin: 0 0 8px; font-size: 12px; color: #888888;">
                                &zwnj;2390 E Camelback Rd, Suite 130, Phoenix, AZ 85016&zwnj;
                            </p>
                            <p style="margin: 0; font-size: 12px; color: #888888;">
                                <a href="{self.config.preference_center}" style="color: #888888; text-decoration: underline;">Manage Preferences</a>
                                &nbsp;|&nbsp;
                                <a href="{self.config.unsubscribe_url}" style="color: #888888; text-decoration: underline;">Unsubscribe</a>
                            </p>
                        </td>
                    </tr>"""

    def _generate_body_end(self) -> str:
        """Generate the closing body tags."""
        return """
                </table>
                <!-- /Email container -->
            </td>
        </tr>
    </table>
    <!-- /Email wrapper -->
</body>"""

    def generate_newsletter_template(
        self,
        campaign_name: str,
        headline: str,
        articles: List[Dict]
    ) -> str:
        """Generate a newsletter-style template with multiple articles."""
        sections = []
        for article in articles:
            sections.append({"type": "divider"})
            sections.append({
                "type": "text",
                "heading": article.get("title", ""),
                "content": article.get("summary", "")
            })
            if article.get("image"):
                sections.append({
                    "type": "image",
                    "src": article["image"],
                    "alt": article.get("title", ""),
                    "link": article.get("link", "")
                })

        return self.generate(
            campaign_name=campaign_name,
            headline=headline,
            template_type="newsletter",
            sections=sections
        )

    def generate_announcement_template(
        self,
        campaign_name: str,
        headline: str,
        announcement: str,
        cta_text: str = "Learn More",
        cta_url: str = "https://pray.com",
        image_url: str = ""
    ) -> str:
        """Generate an announcement-style template."""
        sections = []
        if image_url:
            sections.append({
                "type": "image",
                "src": image_url,
                "alt": headline,
                "link": cta_url
            })

        return self.generate(
            campaign_name=campaign_name,
            headline=headline,
            body_content=[announcement],
            cta_text=cta_text,
            cta_url=cta_url,
            template_type="announcement",
            sections=sections
        )
