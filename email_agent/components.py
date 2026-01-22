"""
Email Components Library
========================
Reusable HTML email components that can be combined
to create complete email templates.
"""

from typing import Dict, List, Optional


class EmailComponents:
    """Library of reusable email components for Braze templates."""

    # Brand configuration
    BRAND = {
        "bg_color": "#0b0c0e",
        "primary_color": "#e3af4a",
        "text_color": "#ffffff",
        "secondary_text": "#d0d0d8",
        "divider_color": "#3a3a3c",
        "card_bg": "#1a1a1c",
        "font_family": "'Satoshi', 'Helvetica Neue', Helvetica, Arial, sans-serif"
    }

    @classmethod
    def header(cls, logo_url: str = "https://pray-email-assets.s3.amazonaws.com/pray-logo-white.png") -> str:
        """Standard email header with logo."""
        return f'''
<!-- Header -->
<tr>
    <td align="center" style="padding: 40px 24px 20px;" class="mobile-padding">
        <a href="https://pray.com" target="_blank">
            <img src="{logo_url}"
                 alt="PRAY.COM"
                 width="120"
                 style="display: block; max-width: 120px; height: auto;"
            />
        </a>
    </td>
</tr>'''

    @classmethod
    def hero_text(
        cls,
        headline: str,
        subheadline: str = "",
        personalized_greeting: bool = True
    ) -> str:
        """Hero section with headline and optional greeting."""
        greeting = ""
        if personalized_greeting:
            greeting = f'''
<p style="margin: 0 0 16px; font-size: 18px; color: {cls.BRAND["secondary_text"]};">
    {{% if {{{{custom_attribute.${{first_name}}}}}} != blank %}}
        Hi {{{{custom_attribute.${{first_name}}}}}},
    {{% else %}}
        Hi there,
    {{% endif %}}
</p>'''

        subhead = ""
        if subheadline:
            subhead = f'''
<p style="margin: 16px 0 0; font-size: 18px; color: {cls.BRAND["secondary_text"]}; line-height: 1.5;">
    {subheadline}
</p>'''

        return f'''
<!-- Hero Section -->
<tr>
    <td style="padding: 20px 40px 30px;" class="mobile-padding">
        {greeting}
        <h1 class="headline" style="margin: 0; font-size: 32px; font-weight: 700; color: {cls.BRAND["text_color"]}; line-height: 1.2;">
            {headline}
        </h1>
        {subhead}
    </td>
</tr>'''

    @classmethod
    def hero_image(
        cls,
        image_url: str,
        alt_text: str = "",
        link_url: str = ""
    ) -> str:
        """Hero image section."""
        img = f'''<img src="{image_url}" alt="{alt_text}" width="560" style="display: block; width: 100%; max-width: 560px; height: auto; border-radius: 12px;" />'''

        if link_url:
            img = f'''<a href="{link_url}" target="_blank" universal="true">{img}</a>'''

        return f'''
<!-- Hero Image -->
<tr>
    <td align="center" style="padding: 20px 40px;" class="mobile-padding">
        {img}
    </td>
</tr>'''

    @classmethod
    def text_block(cls, paragraphs: List[str]) -> str:
        """Text content block."""
        content = ""
        for para in paragraphs:
            content += f'''
<p class="body-text" style="margin: 0 0 16px; font-size: 16px; color: {cls.BRAND["secondary_text"]}; line-height: 1.6;">
    {para}
</p>'''

        return f'''
<!-- Text Block -->
<tr>
    <td style="padding: 0 40px 30px;" class="mobile-padding">
        {content}
    </td>
</tr>'''

    @classmethod
    def cta_button(
        cls,
        text: str,
        url: str,
        style: str = "primary"
    ) -> str:
        """Call-to-action button with Outlook VML support."""
        bg_color = cls.BRAND["primary_color"] if style == "primary" else cls.BRAND["card_bg"]
        text_color = "#000000" if style == "primary" else cls.BRAND["text_color"]

        return f'''
<!-- CTA Button -->
<tr>
    <td align="center" style="padding: 10px 40px 40px;" class="mobile-padding">
        <!--[if mso]>
        <v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="urn:schemas-microsoft-com:office:word" href="{url}" style="height:52px;v-text-anchor:middle;width:200px;" arcsize="15%" stroke="f" fillcolor="{bg_color}">
            <w:anchorlock/>
            <center style="color:{text_color};font-family:Arial,sans-serif;font-size:16px;font-weight:bold;">{text}</center>
        </v:roundrect>
        <![endif]-->
        <!--[if !mso]><!-->
        <a href="{url}"
           target="_blank"
           class="button"
           style="background-color: {bg_color}; border-radius: 8px; color: {text_color}; display: inline-block; font-family: {cls.BRAND["font_family"]}; font-size: 16px; font-weight: 600; padding: 16px 40px; text-align: center; text-decoration: none;"
           universal="true">
            {text}
        </a>
        <!--<![endif]-->
    </td>
</tr>'''

    @classmethod
    def stat_card(
        cls,
        icon: str,
        value: str,
        label: str,
        liquid_var: str = ""
    ) -> str:
        """Stat card with icon, value, and label."""
        display_value = f"{{{{{{custom_attribute.${{{liquid_var}}}}}}}}}" if liquid_var else value

        return f'''
<!-- Stat Card -->
<tr>
    <td style="padding: 20px 40px;" class="mobile-padding">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: {cls.BRAND["card_bg"]}; border-radius: 12px;">
            <tr>
                <td style="padding: 24px; text-align: center;">
                    <div style="font-size: 32px; margin-bottom: 8px;">{icon}</div>
                    <div style="font-size: 36px; font-weight: 700; color: {cls.BRAND["primary_color"]}; margin-bottom: 4px;">
                        {display_value}
                    </div>
                    <div style="font-size: 14px; color: {cls.BRAND["secondary_text"]}; text-transform: uppercase; letter-spacing: 1px;">
                        {label}
                    </div>
                </td>
            </tr>
        </table>
    </td>
</tr>'''

    @classmethod
    def stat_row(cls, stats: List[Dict]) -> str:
        """Row of 2-3 stat cards side by side."""
        cells = ""
        width = f"{100 // len(stats)}%"

        for stat in stats:
            cells += f'''
<td width="{width}" style="padding: 8px; vertical-align: top;" class="mobile-stack">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: {cls.BRAND["card_bg"]}; border-radius: 8px;">
        <tr>
            <td style="padding: 20px; text-align: center;">
                <div style="font-size: 24px; margin-bottom: 8px;">{stat.get("icon", "")}</div>
                <div style="font-size: 28px; font-weight: 700; color: {cls.BRAND["primary_color"]}; margin-bottom: 4px;">
                    {stat.get("value", "")}
                </div>
                <div style="font-size: 12px; color: {cls.BRAND["secondary_text"]}; text-transform: uppercase;">
                    {stat.get("label", "")}
                </div>
            </td>
        </tr>
    </table>
</td>'''

        return f'''
<!-- Stat Row -->
<tr>
    <td style="padding: 10px 32px;" class="mobile-padding">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
            <tr>
                {cells}
            </tr>
        </table>
    </td>
</tr>'''

    @classmethod
    def feature_card(
        cls,
        icon: str,
        title: str,
        description: str,
        link_url: str = ""
    ) -> str:
        """Feature card with icon, title, and description."""
        content = f'''
<div style="font-size: 32px; margin-bottom: 12px;">{icon}</div>
<div style="font-size: 18px; font-weight: 600; color: {cls.BRAND["text_color"]}; margin-bottom: 8px;">{title}</div>
<div style="font-size: 14px; color: {cls.BRAND["secondary_text"]}; line-height: 1.5;">{description}</div>'''

        if link_url:
            content = f'''<a href="{link_url}" target="_blank" style="text-decoration: none;" universal="true">{content}</a>'''

        return f'''
<!-- Feature Card -->
<tr>
    <td style="padding: 12px 40px;" class="mobile-padding">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: {cls.BRAND["card_bg"]}; border-radius: 12px;">
            <tr>
                <td style="padding: 24px; text-align: center;">
                    {content}
                </td>
            </tr>
        </table>
    </td>
</tr>'''

    @classmethod
    def feature_grid(cls, features: List[Dict], columns: int = 2) -> str:
        """Grid of feature cards."""
        rows_html = ""
        for i in range(0, len(features), columns):
            row_features = features[i:i + columns]
            cells = ""

            for feature in row_features:
                cells += f'''
<td width="{100 // columns}%" style="padding: 8px; vertical-align: top;" class="mobile-stack">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: {cls.BRAND["card_bg"]}; border-radius: 8px;">
        <tr>
            <td style="padding: 20px; text-align: center;">
                <div style="font-size: 28px; margin-bottom: 12px;">{feature.get("icon", "")}</div>
                <div style="font-size: 16px; font-weight: 600; color: {cls.BRAND["text_color"]}; margin-bottom: 8px;">{feature.get("title", "")}</div>
                <div style="font-size: 14px; color: {cls.BRAND["secondary_text"]};">{feature.get("description", "")}</div>
            </td>
        </tr>
    </table>
</td>'''

            rows_html += f'''
<tr>
    {cells}
</tr>'''

        return f'''
<!-- Feature Grid -->
<tr>
    <td style="padding: 10px 32px;" class="mobile-padding">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
            {rows_html}
        </table>
    </td>
</tr>'''

    @classmethod
    def divider(cls) -> str:
        """Horizontal divider line."""
        return f'''
<!-- Divider -->
<tr>
    <td style="padding: 20px 40px;" class="mobile-padding">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
            <tr>
                <td style="border-top: 1px solid {cls.BRAND["divider_color"]}; font-size: 0; line-height: 0;">&nbsp;</td>
            </tr>
        </table>
    </td>
</tr>'''

    @classmethod
    def section_title(cls, title: str, subtitle: str = "") -> str:
        """Section title with optional subtitle."""
        sub = ""
        if subtitle:
            sub = f'''
<p style="margin: 8px 0 0; font-size: 14px; color: {cls.BRAND["secondary_text"]};">
    {subtitle}
</p>'''

        return f'''
<!-- Section Title -->
<tr>
    <td style="padding: 30px 40px 16px;" class="mobile-padding">
        <h2 style="margin: 0; font-size: 24px; font-weight: 600; color: {cls.BRAND["text_color"]};">
            {title}
        </h2>
        {sub}
    </td>
</tr>'''

    @classmethod
    def testimonial(
        cls,
        quote: str,
        author: str,
        title: str = ""
    ) -> str:
        """Testimonial block with quote and attribution."""
        attribution = author
        if title:
            attribution = f"{author}, {title}"

        return f'''
<!-- Testimonial -->
<tr>
    <td style="padding: 20px 40px;" class="mobile-padding">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: {cls.BRAND["card_bg"]}; border-radius: 12px;">
            <tr>
                <td style="padding: 24px;">
                    <p style="margin: 0 0 16px; font-size: 18px; font-style: italic; color: {cls.BRAND["text_color"]}; line-height: 1.5;">
                        "{quote}"
                    </p>
                    <p style="margin: 0; font-size: 14px; color: {cls.BRAND["primary_color"]}; font-weight: 500;">
                        - {attribution}
                    </p>
                </td>
            </tr>
        </table>
    </td>
</tr>'''

    @classmethod
    def countdown(cls, end_date_liquid: str = "{{campaign.${end_date}}}") -> str:
        """Countdown timer placeholder (requires Braze dynamic content)."""
        return f'''
<!-- Countdown Timer -->
<tr>
    <td align="center" style="padding: 20px 40px;" class="mobile-padding">
        <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="background-color: {cls.BRAND["card_bg"]}; border-radius: 8px;">
            <tr>
                <td style="padding: 20px 40px; text-align: center;">
                    <p style="margin: 0 0 8px; font-size: 12px; color: {cls.BRAND["secondary_text"]}; text-transform: uppercase; letter-spacing: 1px;">
                        Ends In
                    </p>
                    <p style="margin: 0; font-size: 28px; font-weight: 700; color: {cls.BRAND["primary_color"]};">
                        {end_date_liquid}
                    </p>
                </td>
            </tr>
        </table>
    </td>
</tr>'''

    @classmethod
    def social_proof(cls, number: str, label: str) -> str:
        """Social proof element showing community size."""
        return f'''
<!-- Social Proof -->
<tr>
    <td align="center" style="padding: 20px 40px;" class="mobile-padding">
        <p style="margin: 0; font-size: 14px; color: {cls.BRAND["secondary_text"]};">
            Join <span style="color: {cls.BRAND["primary_color"]}; font-weight: 600;">{number}</span> {label}
        </p>
    </td>
</tr>'''

    @classmethod
    def footer(cls) -> str:
        """Standard email footer with social links and legal."""
        return f'''
<!-- Divider -->
<tr>
    <td style="padding: 30px 40px 10px;" class="mobile-padding">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
            <tr>
                <td style="border-top: 1px solid {cls.BRAND["divider_color"]}; font-size: 0; line-height: 0;">&nbsp;</td>
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
            &copy; {{{{"now" | date: "%Y"}}}} Pray.com, Inc. All rights reserved.
        </p>
        <p style="margin: 0 0 8px; font-size: 12px; color: #888888;">
            &zwnj;2390 E Camelback Rd, Suite 130, Phoenix, AZ 85016&zwnj;
        </p>
        <p style="margin: 0; font-size: 12px; color: #888888;">
            <a href="{{{{preference_center.${{PRAY-Preference-Center}}}}}}" style="color: #888888; text-decoration: underline;">Manage Preferences</a>
            &nbsp;|&nbsp;
            <a href="{{{{${{set_user_to_unsubscribed_url}}}}}}" style="color: #888888; text-decoration: underline;">Unsubscribe</a>
        </p>
    </td>
</tr>'''

    @classmethod
    def liquid_conditional(
        cls,
        attribute: str,
        operator: str,
        value: str,
        content_if_true: str,
        content_if_false: str = ""
    ) -> str:
        """Generate Liquid conditional block."""
        if_block = f'''{{% if {{{{custom_attribute.${{{attribute}}}}}}} {operator} {value} %}}
{content_if_true}'''

        if content_if_false:
            if_block += f'''
{{% else %}}
{content_if_false}'''

        if_block += '''
{% endif %}'''

        return if_block

    @classmethod
    def liquid_assign(cls, var_name: str, attribute: str, default: str = "") -> str:
        """Generate Liquid variable assignment."""
        if default:
            return f'''{{% assign {var_name} = custom_attribute.${{{attribute}}} | default: "{default}" %}}'''
        return f'''{{% assign {var_name} = custom_attribute.${{{attribute}}} %}}'''

    @classmethod
    def deep_link_url(
        cls,
        page: str,
        params: Dict = None,
        desktop_fallback: str = "https://pray.com"
    ) -> str:
        """Generate deep link URL with desktop fallback."""
        base = f"https://pray.com/{page}"
        deep_link = f"pray://{page}"

        if params:
            param_str = "&".join(f"{k}={v}" for k, v in params.items())
            deep_link += f"?{param_str}"

        return f"{base}?deeplink={deep_link}&$desktop_url={desktop_fallback}"
