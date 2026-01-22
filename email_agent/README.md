# PRAY.COM Email Template Generator Agent

An AI-powered agent that generates EAA-compliant, mobile-responsive HTML email templates and benefit-driven subject lines for Braze campaigns.

## Features

### 1. Email Template Generator
- **Mobile-Responsive**: Optimized for all devices with 660px and 480px breakpoints
- **Braze-Ready**: Full Liquid templating support with personalization
- **Outlook Compatible**: VML fallbacks for buttons and shapes
- **PRAY.COM Branded**: Dark theme with gold accents, Satoshi font
- **Component Library**: Reusable components for stats, features, testimonials

### 2. Subject Line Factory
- **Benefit-Driven**: Focus on user value and outcomes
- **Curiosity-Sparking**: Hook formats like "What happens when you pray before bed?"
- **A/B Test Variants**: Automatic generation with testing hypotheses
- **Segment-Aware**: Tailored for new users, engaged, lapsed, premium
- **Personalization**: First name and custom attribute support

## Installation

```bash
cd email_agent
# No external dependencies required - uses Python standard library
```

## Quick Start

### Interactive Mode
```bash
python email_agent.py interactive
```

### Generate from Brief
```bash
python email_agent.py generate --brief "Launch campaign for our new Bible in a Year reading plan. Target engaged users who have completed at least one devotional. Highlight guided daily readings and community aspect. Tone: inspiring. CTA: Start Your Journey"
```

### Generate Subject Lines Only
```bash
python email_agent.py subjects --context "New meditation feature launch" --segment engaged --tone curious
```

## Usage

### Campaign Brief Format

When providing a brief, include:
- Campaign objective/goal
- Target audience/segment
- Key message or offer
- Desired tone
- Specific calls-to-action
- Personalization requirements

**Example Brief:**
```
Launch campaign for our new "Bible in a Year" reading plan.
Target: engaged users who have completed at least one devotional.
Highlight the guided daily readings and community aspect.
Tone: inspiring and inviting.
CTA: Start Your Journey
URL: https://pray.com/bible-in-a-year
```

### Subject Line Styles

The factory generates subject lines in proven styles:

| Style | Example |
|-------|---------|
| Curiosity | "What happens when you pray this before bed?" |
| Benefit | "Start your morning with peace and purpose" |
| Personal | "{{first_name}}, your prayer journey awaits" |
| Urgency | "24 hours left to join thousands in prayer" |
| Question | "Ready to transform your prayer life?" |

### Template Types

1. **promotional** - Product/feature launches, special offers
2. **newsletter** - Regular updates, content digests
3. **announcement** - Important news, events
4. **transactional** - Account-related, confirmations

## Output

The agent produces:
- `{name}.html` - Complete HTML email template ready for Braze
- `{name}_subjects.json` - Subject lines with A/B variants
- `{name}_full.json` - Metadata and generation details

## Components

### Available Components

```python
from components import EmailComponents

# Header with logo
EmailComponents.header()

# Hero section with personalized greeting
EmailComponents.hero_text("Your Headline", "Subheadline", personalized_greeting=True)

# CTA button with Outlook support
EmailComponents.cta_button("Start Now", "https://pray.com")

# Stat card with Liquid variable
EmailComponents.stat_card("🙏", "100", "prayers", liquid_var="prayer_count")

# Feature grid
EmailComponents.feature_grid([
    {"icon": "📖", "title": "Daily Reading", "description": "Scripture for every day"},
    {"icon": "🙏", "title": "Guided Prayer", "description": "Never pray alone"}
])

# Footer with social links
EmailComponents.footer()
```

### Liquid Templating Helpers

```python
# Conditional content
EmailComponents.liquid_conditional(
    attribute="total_minutes_listened",
    operator=">=",
    value="15",
    content_if_true="<p>You're a dedicated prayer!</p>",
    content_if_false="<p>Start your journey today!</p>"
)

# Variable assignment
EmailComponents.liquid_assign("user_streak", "longest_streak", default="0")

# Deep links
EmailComponents.deep_link_url("devotional/123", {"source": "email"})
```

## Customization

### Brand Colors

Edit `components.py` to customize the brand:

```python
BRAND = {
    "bg_color": "#0b0c0e",      # Dark background
    "primary_color": "#e3af4a",  # Gold accent
    "text_color": "#ffffff",     # White text
    "secondary_text": "#d0d0d8", # Light gray
    "divider_color": "#3a3a3c",  # Divider lines
    "card_bg": "#1a1a1c",        # Card backgrounds
}
```

### Adding New Subject Line Templates

Edit `subject_line_factory.py` to add templates:

```python
TEMPLATES = {
    "your_style": [
        "Your template with {placeholder}",
        "Another template for {topic}",
    ]
}
```

## File Structure

```
email_agent/
├── email_agent.py        # Main CLI agent
├── template_generator.py # HTML template generation
├── subject_line_factory.py # Subject line generation
├── campaign_parser.py    # Brief parsing
├── components.py         # Reusable email components
├── README.md            # This file
└── output/              # Generated files (created on first run)
```

## Examples

### Year in Prayer Campaign

```bash
python email_agent.py generate \
  --brief "Year in Prayer stats email for all users. Show personal prayer statistics, streak data, and community highlights. Personalized with user stats. Celebratory tone." \
  --type promotional \
  --name year-in-prayer
```

### Bible Reading Plan Launch

```bash
python email_agent.py generate \
  --brief "Launch new Bible in a Year reading plan. Target new users who signed up in the last 30 days. Emphasize ease of getting started and community support. Inspiring tone. CTA: Begin Reading" \
  --type announcement \
  --name bible-launch
```

### Re-engagement Campaign

```bash
python email_agent.py subjects \
  --context "Win back users who haven't opened the app in 30 days with a new meditation series" \
  --segment lapsed \
  --tone personal \
  --num 10
```

## Best Practices

1. **Always test** - Preview in Litmus or Email on Acid
2. **Check personalization** - Ensure Liquid variables exist in Braze
3. **Mobile first** - Test on mobile devices
4. **Subject length** - Keep under 50 characters for mobile
5. **Preheader** - Always include a compelling preheader

## Troubleshooting

### Template not rendering in Outlook
- Ensure VML fallbacks are included (automatic with `cta_button`)
- Check for unsupported CSS properties

### Liquid errors in Braze
- Verify custom attribute names match exactly
- Use `| default:` filters for optional attributes
- Test with preview users

### Mobile layout issues
- Check `class="mobile-stack"` on columns
- Verify `class="mobile-padding"` on content cells
- Test responsive breakpoints
