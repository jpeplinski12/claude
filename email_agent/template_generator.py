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
    # Theme identifier
    theme: str = "light"  # "light" or "dark"

    # Brand colors
    bg_color: str = "#f7f5f2"
    container_bg: str = "#ffffff"
    primary_color: str = "#9e6900"
    primary_hover: str = "#7a5200"
    text_color: str = "#2c2c2c"
    heading_color: str = "#1a1a1a"
    secondary_text: str = "#6b6b6b"
    quote_bg: str = "#faf8f5"
    quote_text: str = "#3d3d3d"
    divider_color: str = "#e5e0d8"
    footer_text: str = "#9b9b9b"
    link_color: str = "#9e6900"

    # Dark mode colors (for @media queries)
    dark_bg: str = "#1a1a1a"
    dark_container: str = "#2c2c2c"
    dark_quote_bg: str = "#3d3d3d"
    dark_text: str = "#ffffff"
    dark_secondary: str = "#d0d0d0"
    dark_footer: str = "#b0b0b0"
    dark_divider: str = "#4a4a4a"
    dark_link: str = "#c9a227"

    # Typography
    font_family: str = "Satoshi, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Fira Sans', 'Droid Sans', Helvetica, sans-serif"
    heading_size: str = "28px"
    body_size: str = "18px"
    body_line_height: str = "1.7"
    heading_line_height: str = "1.3"

    # Layout
    email_width: str = "600px"
    mobile_breakpoint: str = "600px"
    border_radius: str = "12px"
    box_shadow: str = "0 2px 8px rgba(0,0,0,0.06)"

    # Padding (desktop)
    outer_padding: str = "30px 10px 40px 10px"
    header_padding: str = "35px 40px 25px 40px"
    content_padding_h: str = "50px"
    hero_padding: str = "10px 50px 25px 50px"
    quote_padding: str = "0 50px 25px 50px"
    cta_padding: str = "0 40px 0px 40px"
    footer_padding: str = "0px 40px 35px 40px"

    # Padding (mobile - roughly half)
    mobile_outer_padding: str = "15px 5px 20px 5px"
    mobile_header_padding: str = "18px 20px 12px 20px"
    mobile_content_h: str = "24px"
    mobile_hero_padding: str = "8px 24px 12px 24px"
    mobile_quote_padding: str = "0 24px 12px 24px"
    mobile_cta_padding: str = "0 24px 0 24px"
    mobile_footer_padding: str = "0 20px 18px 20px"

    # Braze settings
    preference_center: str = "{{preference_center.${PRAY-Preference-Center}}}"
    unsubscribe_url: str = "{{${set_user_to_unsubscribed_url}}}"

    # Assets
    logo_url: str = "https://braze-images.com/appboy/communication/assets/image_assets/images/66621fa029d6eb0059bcc330/original.png?1717706656"
    logo_width: str = "160"


# Theme Presets
class LightThemeConfig(EmailConfig):
    """Light theme configuration for plain text/triggered emails (600px)."""
    def __init__(self):
        super().__init__()
        self.theme = "light"
        self.bg_color = "#f7f5f2"
        self.container_bg = "#ffffff"
        self.text_color = "#2c2c2c"
        self.heading_color = "#1a1a1a"
        self.secondary_text = "#6b6b6b"
        self.quote_bg = "#faf8f5"
        self.quote_text = "#3d3d3d"
        self.divider_color = "#e5e0d8"
        self.footer_text = "#9b9b9b"
        self.link_color = "#9e6900"
        self.email_width = "600px"
        self.mobile_breakpoint = "600px"
        self.border_radius = "12px"
        self.box_shadow = "0 2px 8px rgba(0,0,0,0.06)"


class DarkThemeConfig(EmailConfig):
    """Dark theme configuration for promotional/premium emails (680px)."""
    def __init__(self):
        super().__init__()
        self.theme = "dark"
        self.bg_color = "#212224"
        self.container_bg = "#141414"
        self.text_color = "#fffffe"
        self.heading_color = "#fffffe"
        self.secondary_text = "#cfcfd2"
        self.quote_bg = "#323237"
        self.quote_text = "#fffffe"
        self.divider_color = "#3a3a3c"
        self.footer_text = "#cfcfd2"
        self.link_color = "#E3AF4A"
        self.primary_color = "#E3AF4A"
        self.primary_hover = "#c9a227"
        self.email_width = "680px"
        self.mobile_breakpoint = "600px"
        self.border_radius = "20px"
        self.box_shadow = "none"
        # Wider padding for premium feel
        self.content_padding_h = "40px"
        self.hero_padding = "10px 40px 20px 40px"


# Template Type Configurations
TEMPLATE_TYPES = {
    "plain_text": {
        "name": "Plain Text / Triggered",
        "description": "Simple triggered emails like Daily Prayer reminders",
        "theme": "light",
        "components": ["header", "hero", "content", "cta", "footer"],
        "use_cases": ["daily_prayer", "onboarding", "reminders", "transactional"]
    },
    "premium": {
        "name": "Premium / Subscription",
        "description": "Premium subscription promotions with rich layouts",
        "theme": "dark",
        "components": ["header", "hero", "hero_image", "content", "two_column", "testimonial", "cta", "footer"],
        "use_cases": ["subscription_offers", "premium_features", "upsells"]
    },
    "sponsored": {
        "name": "Sponsored / Partner",
        "description": "Emails featuring sponsored content or ministry partners",
        "theme": "dark",
        "components": ["header", "hero", "hero_image", "content", "two_column", "testimonial", "steps", "multiple_ctas", "footer"],
        "use_cases": ["ministry_partnerships", "fundraising", "sponsored_content"]
    },
    "holiday": {
        "name": "Holiday / Seasonal",
        "description": "Special holiday campaigns with festive styling",
        "theme": "light",
        "components": ["header", "hero", "content", "cta", "footer"],
        "use_cases": ["christmas", "easter", "thanksgiving", "seasonal"]
    },
    "cart_abandonment": {
        "name": "Cart Abandonment",
        "description": "Abandoned cart recovery sequences",
        "theme": "light",
        "components": ["header", "hero", "content", "quote", "cta", "preference", "footer"],
        "use_cases": ["abandoned_cart", "winback", "recovery"]
    },
    "newsletter": {
        "name": "Newsletter / Digest",
        "description": "Regular content digests and newsletters",
        "theme": "light",
        "components": ["header", "hero", "multiple_sections", "dividers", "footer"],
        "use_cases": ["weekly_digest", "monthly_newsletter", "content_roundup"]
    },
    "announcement": {
        "name": "Announcement / News",
        "description": "Important announcements and updates",
        "theme": "light",
        "components": ["header", "hero", "content", "cta", "footer"],
        "use_cases": ["product_launch", "feature_announcement", "company_news"]
    }
}


class EmailTemplateGenerator:
    """Generates mobile-responsive HTML email templates for Braze."""

    def __init__(self, config: Optional[EmailConfig] = None, theme: str = "light"):
        """
        Initialize the template generator.

        Args:
            config: Custom EmailConfig (optional)
            theme: "light" or "dark" theme preset
        """
        if config:
            self.config = config
        else:
            self.config = LightThemeConfig() if theme == "light" else DarkThemeConfig()

    @staticmethod
    def get_template_type_info(template_type: str) -> Dict:
        """Get information about a template type."""
        return TEMPLATE_TYPES.get(template_type, TEMPLATE_TYPES["plain_text"])

    @staticmethod
    def list_template_types() -> Dict:
        """List all available template types."""
        return TEMPLATE_TYPES

    def generate(
        self,
        campaign_name: str,
        headline: str,
        subheadline: str = "",
        body_content: List[str] = None,
        cta_text: str = "Learn More",
        cta_url: str = "https://pray.com",
        template_type: str = "plain_text",
        personalization: Dict = None,
        sections: List[Dict] = None,
        theme: str = None
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
            template_type: Template type (plain_text, premium, sponsored, holiday, cart_abandonment, newsletter, announcement)
            personalization: Dict of Braze personalization options
            sections: Additional content sections
            theme: Override theme ("light" or "dark"), uses template type default if not specified

        Returns:
            Complete HTML email template string
        """
        body_content = body_content or []
        personalization = personalization or {}
        sections = sections or []

        # Get template type configuration
        template_config = self.get_template_type_info(template_type)

        # Apply theme override if specified
        if theme and theme != self.config.theme:
            self.config = LightThemeConfig() if theme == "light" else DarkThemeConfig()
        elif not theme and template_config["theme"] != self.config.theme:
            # Use template type's recommended theme
            self.config = LightThemeConfig() if template_config["theme"] == "light" else DarkThemeConfig()

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
        """Generate XHTML doctype for email compatibility matching PRAY.COM standards."""
        return """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html dir="ltr" xmlns="http://www.w3.org/1999/xhtml" xmlns:o="urn:schemas-microsoft-com:office:office" lang="en">"""

    def _generate_head(self, campaign_name: str) -> str:
        """Generate the head section with styles and meta tags matching PRAY.COM standards."""
        return f"""<head>
<meta charset="UTF-8">
<meta content="width=device-width, initial-scale=1" name="viewport">
<meta name="x-apple-disable-message-reformatting">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta content="telephone=no" name="format-detection">
<meta name="color-scheme" content="light dark">
<meta name="supported-color-schemes" content="light dark">
<title>{campaign_name}</title>
<!--[if mso]>
<style>
  span,td,table,div,p,a {{font-family:Arial,sans-serif !important;}}
</style>
<![endif]-->
<!--[if (mso 16)]>
<style type="text/css">
  a {{text-decoration: none;}}
</style>
<![endif]-->
<!--[if gte mso 9]><style>sup {{ font-size: 100% !important; }}</style><![endif]-->
<!--[if gte mso 9]>
<xml>
  <o:OfficeDocumentSettings>
    <o:AllowPNG></o:AllowPNG>
    <o:PixelsPerInch>96</o:PixelsPerInch>
  </o:OfficeDocumentSettings>
</xml>
<![endif]-->
<!--[if !mso]><!-->
<link href="https://d2alqht3442852.cloudfront.net/fonts/Satoshi-Variable.woff" rel="stylesheet">
<!--<![endif]-->
<style type="text/css">
@font-face {{
  font-family: 'Satoshi';
  src: url('https://d2alqht3442852.cloudfront.net/fonts/Satoshi-Variable.woff2') format('woff2'),
       url('https://d2alqht3442852.cloudfront.net/fonts/Satoshi-Variable.woff') format('woff'),
       url('https://d2alqht3442852.cloudfront.net/fonts/Satoshi-Variable.ttf') format('truetype');
  font-weight: 300 900;
  font-display: swap;
  font-style: normal;
}}

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
  outline: none;
  text-decoration: none;
}}

body {{
  margin: 0 !important;
  padding: 0 !important;
  width: 100% !important;
  background-color: {self.config.bg_color};
}}

#outlook a {{ padding: 0; }}

a[x-apple-data-detectors] {{
  color: inherit !important;
  text-decoration: none !important;
  font-size: inherit !important;
  font-family: inherit !important;
  font-weight: inherit !important;
  line-height: inherit !important;
}}

.body-text {{
  font-family: {self.config.font_family};
  font-size: {self.config.body_size};
  line-height: {self.config.body_line_height};
  color: {self.config.text_color};
  letter-spacing: 0.01em;
}}

.headline {{
  font-family: {self.config.font_family};
  font-size: {self.config.heading_size};
  font-weight: 700;
  line-height: {self.config.heading_line_height};
  color: {self.config.heading_color};
  letter-spacing: -0.01em;
  margin: 0 0 20px 0;
}}

.cta-button {{
  background-color: {self.config.primary_color};
  border: none;
  color: #ffffff !important;
  padding: 18px 36px;
  text-align: center;
  text-decoration: none !important;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  border-radius: 8px;
  font-family: {self.config.font_family};
  display: inline-block;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}}

.cta-button:hover {{
  background-color: {self.config.primary_hover} !important;
}}

.prayer-quote {{
  background-color: {self.config.quote_bg};
  border-left: 4px solid {self.config.primary_color};
  padding: 24px 28px;
  margin: 25px 0;
  border-radius: 0 8px 8px 0;
}}

.prayer-quote p {{
  font-family: Satoshi, Georgia, 'Times New Roman', serif;
  font-size: 19px;
  font-style: italic;
  line-height: 1.7;
  color: {self.config.quote_text};
  margin: 0;
  letter-spacing: 0.01em;
}}

.preference-text {{
  font-family: {self.config.font_family};
  font-size: 16px;
  line-height: 1.6;
  color: {self.config.secondary_text};
  margin: 20px 0 0 0;
  text-align: center;
}}

.preference-text a {{
  color: {self.config.link_color};
  text-decoration: underline;
}}

.divider {{
  border: none;
  border-top: 1px solid {self.config.divider_color};
  margin: 35px 0;
}}

.preheader {{
  display: none !important;
  visibility: hidden;
  opacity: 0;
  color: transparent;
  height: 0;
  width: 0;
  max-height: 0;
  max-width: 0;
  overflow: hidden;
  mso-hide: all;
}}

/* Dark mode support for iOS Mail and other clients */
:root {{
  color-scheme: light dark;
  supported-color-schemes: light dark;
}}

@media (prefers-color-scheme: dark) {{
  /* Backgrounds */
  .email-body,
  .email-body table {{ background-color: {self.config.dark_bg} !important; }}
  .email-container,
  .email-container td {{ background-color: {self.config.dark_container} !important; }}

  /* All text elements - explicit targeting */
  .body-text,
  .headline,
  h1,
  p,
  td {{ color: {self.config.dark_text} !important; }}

  /* Prayer quote */
  .prayer-quote {{ background-color: {self.config.dark_quote_bg} !important; }}
  .prayer-quote p {{ color: {self.config.dark_text} !important; }}

  /* Secondary text */
  .preference-text {{ color: {self.config.dark_secondary} !important; }}

  /* Footer text - slightly muted */
  .footer-text,
  .footer-links,
  .footer-address {{ color: {self.config.dark_footer} !important; }}

  /* Divider */
  .divider {{ border-top-color: {self.config.dark_divider} !important; }}

  /* Links */
  a {{ color: {self.config.dark_link} !important; }}
  .cta-button {{ color: #ffffff !important; }}
}}

/* Mobile styles - Roughly half of desktop padding */
@media only screen and (max-width: {self.config.mobile_breakpoint}) {{
  /* Container - full width on mobile, no border radius */
  .email-container {{
    width: 100% !important;
    max-width: 100% !important;
    border-radius: 0 !important;
  }}

  /* Padding adjustments */
  .outer-padding {{
    padding: {self.config.mobile_outer_padding} !important;
  }}

  .header-padding {{
    padding: {self.config.mobile_header_padding} !important;
  }}

  .content-padding {{
    padding-left: {self.config.mobile_content_h} !important;
    padding-right: {self.config.mobile_content_h} !important;
  }}

  .hero-padding {{
    padding: {self.config.mobile_hero_padding} !important;
  }}

  .quote-padding {{
    padding: {self.config.mobile_quote_padding} !important;
  }}

  .cta-padding {{
    padding: {self.config.mobile_cta_padding} !important;
  }}

  .footer-padding {{
    padding: {self.config.mobile_footer_padding} !important;
  }}

  /* Typography adjustments */
  .headline {{
    font-size: 24px !important;
    line-height: 1.3 !important;
    margin-bottom: 18px !important;
  }}

  .body-text {{
    font-size: 16px !important;
    line-height: 1.65 !important;
  }}

  /* Prayer quote */
  .prayer-quote {{
    padding: 12px 14px !important;
    margin: 0 0 12px 0 !important;
  }}
  .prayer-quote p {{
    font-size: 16px !important;
  }}

  /* CTA Button */
  .cta-button {{
    width: 100% !important;
    padding: 16px 20px !important;
    font-size: 16px !important;
    box-sizing: border-box !important;
  }}

  /* Logo */
  .mobile-logo {{
    width: 130px !important;
  }}

  /* Divider */
  .divider {{
    margin: 18px 0 !important;
  }}

  /* Preference text */
  .preference-text {{
    font-size: 16px !important;
    margin-top: 10px !important;
  }}

  /* Footer text sizes */
  .footer-text {{
    font-size: 13px !important;
    line-height: 1.5 !important;
  }}

  .footer-links {{
    font-size: 13px !important;
    margin-bottom: 8px !important;
  }}

  .footer-address {{
    font-size: 12px !important;
    line-height: 1.5 !important;
  }}

  /* Social icons */
  .social-table {{
    width: 280px !important;
  }}
  .social-icon {{
    width: 32px !important;
    height: 32px !important;
  }}
}}
</style>
</head>"""

    def _generate_body_start(self) -> str:
        """Generate the body opening with wrapper table matching PRAY.COM structure."""
        return f"""<body class="email-body" style="margin:0; padding:0; background-color:{self.config.bg_color};">

  <center style="width:100%; background-color:{self.config.bg_color};">
    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color:{self.config.bg_color};">
      <tr>
        <td class="outer-padding" align="center" valign="top" style="padding: {self.config.outer_padding};">

          <!--[if mso]>
          <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="{self.config.email_width}" align="center">
          <tr>
          <td>
          <![endif]-->

          <table class="email-container" role="presentation" cellspacing="0" cellpadding="0" border="0" width="{self.config.email_width}" style="max-width:{self.config.email_width}; background-color:{self.config.container_bg}; border-radius:{self.config.border_radius}; overflow:hidden; box-shadow: {self.config.box_shadow};">"""

    def _generate_header(self) -> str:
        """Generate the email header with logo matching PRAY.COM style."""
        return f"""
            <!-- Logo Header -->
            <tr>
              <td class="header-padding" align="center" style="padding: {self.config.header_padding}; background-color:{self.config.container_bg};">
                <a universal="true" href="https://pray.com" target="_blank">
                  <img class="mobile-logo" src="{self.config.logo_url}" alt="PRAY.COM" width="{self.config.logo_width}" style="display:block; width:{self.config.logo_width}px; max-width:{self.config.logo_width}px; border:0;">
                </a>
              </td>
            </tr>"""

    def _generate_hero(self, headline: str, subheadline: str, personalization: Dict) -> str:
        """Generate the hero section with headline and personalized greeting matching PRAY.COM style."""
        subhead_html = ""
        if subheadline:
            subhead_html = f"""
                <p class="body-text" style="font-family:{self.config.font_family}; font-size:{self.config.body_size}; line-height:{self.config.body_line_height}; color:{self.config.text_color}; margin:0 0 20px 0;">
                  {subheadline}
                </p>"""

        return f"""
            <!-- Hero Section -->
            <tr>
              <td class="content-padding hero-padding" style="padding: {self.config.hero_padding}; background-color:{self.config.container_bg};">

                <h1 class="headline" style="font-family:{self.config.font_family}; font-size:{self.config.heading_size}; font-weight:700; line-height:{self.config.heading_line_height}; color:{self.config.heading_color}; margin:0 0 25px 0; letter-spacing: .3px;">
                  {headline}
                </h1>
                {subhead_html}
              </td>
            </tr>"""

    def _generate_main_content(self, body_content: List[str]) -> str:
        """Generate the main body content section matching PRAY.COM style."""
        if not body_content:
            return ""

        paragraphs = ""
        for para in body_content:
            paragraphs += f"""
                <p class="body-text" style="font-family:{self.config.font_family}; font-size:{self.config.body_size}; line-height:{self.config.body_line_height}; color:{self.config.text_color}; margin:0 0 20px 0;">
                  {para}
                </p>"""

        return f"""
            <!-- Main Content -->
            <tr>
              <td class="content-padding" style="padding: 0 {self.config.content_padding_h} 30px {self.config.content_padding_h}; background-color:{self.config.container_bg};">
                {paragraphs}
              </td>
            </tr>"""

    def _generate_cta(self, cta_text: str, cta_url: str) -> str:
        """Generate the CTA button section with Outlook VML fallback matching PRAY.COM style."""
        return f"""
            <!-- CTA Button -->
            <tr>
              <td class="content-padding cta-padding" align="center" style="padding: {self.config.cta_padding}; background-color:{self.config.container_bg};">
                <!--[if mso]>
                <v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="urn:schemas-microsoft-com:office:word" href="{cta_url}" style="height:54px;v-text-anchor:middle;width:300px;" arcsize="15%" strokecolor="{self.config.primary_color}" fillcolor="{self.config.primary_color}">
                <w:anchorlock/>
                <center style="color:#ffffff;font-family:Arial,sans-serif;font-size:14px;font-weight:bold;letter-spacing:1px;">{cta_text.upper()}</center>
                </v:roundrect>
                <![endif]-->
                <!--[if !mso]><!-->
                <a universal="true" href="{cta_url}" class="cta-button" style="background-color:{self.config.primary_color}; border:none; color:#ffffff !important; padding:18px 20px; text-align:center; text-decoration:none !important; font-size:16px; font-weight:700; cursor:pointer; border-radius:8px; font-family:{self.config.font_family}; display:inline-block; letter-spacing:0.03em; text-transform:uppercase;">
                  {cta_text.upper()}
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
        """Generate the email footer with social links and legal text matching PRAY.COM style."""
        return f"""
            <!-- Divider -->
            <tr>
              <td class="content-padding divider-padding" style="padding: 0 {self.config.content_padding_h}; background-color:{self.config.container_bg};">
                <hr class="divider" style="border:none; border-top:1px solid {self.config.divider_color}; margin:0;">
              </td>
            </tr>

            <!-- Social Icons -->
            <tr>
              <td class="social-padding" align="center" style="padding: 35px 40px 20px 40px; background-color:{self.config.container_bg};">
                <table class="social-table" role="presentation" cellspacing="0" cellpadding="0" border="0" width="310">
                  <tr>
                    <td width="50" align="center" valign="middle">
                      <a href="https://www.facebook.com/pray/">
                        <img class="social-icon" src="https://braze-images.com/appboy/communication/assets/image_assets/images/622a7f73a4943e1bce16f6f0/original.png?1646952307" alt="Facebook" width="36" height="36" style="display:block; width:36px; height:36px; border:0;">
                      </a>
                    </td>
                    <td width="50" align="center" valign="middle">
                      <a href="https://www.youtube.com/channel/UCNyNg5QgG5irAuFCs8L8BSg">
                        <img class="social-icon" src="https://braze-images.com/appboy/communication/assets/image_assets/images/622a7f7359344573bd4ccd3d/original.png?1646952307" alt="YouTube" width="36" height="36" style="display:block; width:36px; height:36px; border:0;">
                      </a>
                    </td>
                    <td width="50" align="center" valign="middle">
                      <a href="https://www.instagram.com/pray/">
                        <img class="social-icon" src="https://braze-images.com/appboy/communication/assets/image_assets/images/622a7f7359344574564ccff9/original.png?1646952307" alt="Instagram" width="36" height="36" style="display:block; width:36px; height:36px; border:0;">
                      </a>
                    </td>
                    <td width="50" align="center" valign="middle">
                      <a href="https://x.com/pray?lang=en">
                        <img class="social-icon" src="https://braze-images.com/appboy/communication/assets/image_assets/images/622a7f73a4943e1d4716f6e9/original.png?1646952307" alt="X" width="36" height="36" style="display:block; width:36px; height:36px; border:0;">
                      </a>
                    </td>
                    <td width="50" align="center" valign="middle">
                      <a href="https://www.linkedin.com/company/pray.com/">
                        <img class="social-icon" src="https://braze-images.com/appboy/communication/assets/image_assets/images/622a7f73fde9db4f948352c3/original.png?1646952307" alt="LinkedIn" width="36" height="36" style="display:block; width:36px; height:36px; border:0;">
                      </a>
                    </td>
                    <td width="50" align="center" valign="middle">
                      <a href="https://www.tiktok.com/@pray?lang=en">
                        <img class="social-icon" src="https://braze-images.com/appboy/communication/assets/image_assets/images/622a7f733e3a900d48a2ee82/original.png?1646952307" alt="TikTok" width="36" height="36" style="display:block; width:36px; height:36px; border:0;">
                      </a>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>

            <!-- Footer -->
            <tr>
              <td class="footer-padding" align="center" style="padding: {self.config.footer_padding}; background-color:{self.config.container_bg};">
                <p class="footer-text" style="margin:0;margin-bottom:0;font-family:{self.config.font_family};font-size: 15px;">You received this email because you created a PRAY&zwnj;.&zwnj;COM account and now you are on your way to enriching your&nbsp;faith.</p><br>

                <p class="footer-text" style="margin:0;margin-bottom:0;font-family:{self.config.font_family};font-size: 15px;">Do you want fewer emails or just a different devotional type? We have plenty to choose&nbsp;from.<br><span style="color: #ffffff;"><a href="{self.config.preference_center}" target="_blank" style="text-decoration: underline;font-weight: 600; color: #000000;">You can personalize&nbsp;your email&nbsp;preferences&nbsp;here</a></span>.</p><br>
                <p class="footer-links" style="font-family:{self.config.font_family}; font-size:15px; line-height:1.6; color:{self.config.secondary_text}; margin:0 0 12px 0;">
                  <a href="https://www.pray.com/privacy-policy/" target="_blank" style="color:{self.config.link_color}; text-decoration:underline;">Privacy Policy</a>
                  &nbsp;&nbsp;|&nbsp;&nbsp;
                  <a href="https://help.pray.com/hc/en-us" target="_blank" style="color:{self.config.link_color}; text-decoration:underline;">Help Center</a>
                  &nbsp;&nbsp;|&nbsp;&nbsp;
                  <a href="{self.config.preference_center}" target="_blank" style="color:{self.config.link_color}; text-decoration:underline;">Unsubscribe</a>
                </p>
                <p class="footer-address" style="font-family:{self.config.font_family}; font-size:14px; line-height:1.6; color:{self.config.footer_text}; margin:0;">
                  4607 &zwnj;Lakeview Canyon Rd. &zwnj;#456<br>
                  Westlake Village, &zwnj;CA 91361<br>
                  © {{{{'now' | date: '%Y'}}}} PRAY&#8203;.&#8203;COM
                </p>
              </td>
            </tr>"""

    def _generate_body_end(self) -> str:
        """Generate the closing body tags matching PRAY.COM structure."""
        return """
          </table>

          <!--[if mso]>
          </td>
          </tr>
          </table>
          <![endif]-->

        </td>
      </tr>
    </table>
  </center>

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
