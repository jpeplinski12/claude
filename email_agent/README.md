# PRAY.COM Email Template Generator Agent

An AI-powered agent that generates EAA-compliant, mobile-responsive HTML email templates and benefit-driven subject lines for Braze campaigns.

## Features

### 1. **NEW:** AI-Powered Copywriting ✨
- **Brand Voice Integration**: Uses Claude AI to generate copy that matches PRAY.COM's tone
- **Quality Scoring**: Automatic validation to ensure copy meets brand standards (aim for 80+/100)
- **Conversational Tone**: Writes like "a compassionate pastor crossed with a tech-forward friend"
- **Smart Fallbacks**: Automatically uses template-based generation if AI is unavailable

### 2. Email Template Generator
- **Template Types**: Plain Text, Premium, Sponsored, Holiday, Cart Abandonment, Newsletter, Announcement
- **Light/Dark Themes**: Automatic theme selection (600px light, 680px dark) or manual override
- **Mobile-Responsive**: Optimized for all devices with mobile breakpoints
- **Braze-Ready**: Full Liquid templating support with personalization
- **Outlook Compatible**: VML fallbacks for buttons and shapes
- **PRAY.COM Branded**: Professional themes with Satoshi font

### 3. Subject Line Factory
- **AI-Generated**: Creates benefit-driven, curiosity-sparking subject lines
- **A/B Test Variants**: Automatic generation with testing hypotheses
- **Segment-Aware**: Tailored for new users, engaged, lapsed, premium
- **Under 50 Characters**: Mobile-optimized length
- **Personalization**: First name and custom attribute support

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set up API key for AI copywriting (required for best results)
export ANTHROPIC_API_KEY="your-api-key-here"
```

Get your API key from: https://console.anthropic.com/

## Quick Start

### Web Interface (Recommended)
```bash
streamlit run email_agent/web_app.py
```

Then:
1. Toggle "🤖 Use AI Copywriting" in the sidebar (if API key is set)
2. Enter your campaign brief
3. Select template type and theme
4. Generate high-quality, brand-aligned content

### CLI - Interactive Mode
```bash
python email_agent.py interactive
```

### CLI - Generate from Brief
```bash
python email_agent.py generate --brief "Launch campaign for our new Bible in a Year reading plan. Target engaged users who have completed at least one devotional. Highlight guided daily readings and community aspect. Tone: inspiring. CTA: Start Your Journey"
```

### CLI - Generate Subject Lines Only
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

## AI Copywriting vs Template-Based

### ✨ With AI Copywriting (Recommended)
**Good Example:**
> "Look how far you've come. Your 387 minutes in prayer this year show a heart seeking God — and He sees every moment."

- Professional copywriting matching PRAY.COM's brand voice
- Warm, conversational tone that creates emotional connection
- Automatic quality scoring (aim for 80+/100)
- Empowering language that guides rather than preaches

### 📝 Without AI Copywriting (Fallback)
**Bad Example:**
> "View your annual statistics and usage metrics for the previous calendar year."

- Uses template-based generation with predefined phrases
- Generic copy that may feel corporate or sales-y
- Requires manual editing to match brand voice
- Good for quick testing when API is unavailable

## PRAY.COM Brand Voice

Your content should embody:
- **Faithful and Reverent**: Emphasizes God's presence and biblical truth
- **Encouraging and Uplifting**: Offers hope, peace, and strength
- **Warm and Conversational**: Like a trusted friend, not a corporation
- **Modern and Accessible**: Digital-first, mobile-optimized
- **Guiding and Empowering**: Empowers action rather than preaching

**Writing Principles:**
- ✅ Speak directly using "you" language
- ✅ Meet users where they are emotionally (stress, fatigue, spiritual hunger)
- ✅ Include specific, actionable next steps
- ✅ Use simple, mobile-friendly language
- ❌ Don't use corporate jargon (leverage, utilize, synergy, platform)
- ❌ Don't preach or lecture
- ❌ Don't be vague or overly formal

## File Structure

```
email_agent/
├── web_app.py              # Streamlit web interface
├── copywriting_agent.py    # NEW: AI-powered copywriting
├── brand_voice.py          # NEW: Brand voice configuration
├── email_agent.py          # Main CLI agent
├── template_generator.py   # HTML template generation
├── subject_line_factory.py # Subject line generation
├── campaign_parser.py      # Brief parsing
├── requirements.txt        # Dependencies
├── README.md              # This file
└── output/                # Generated files (created on first run)
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

1. **Enable AI Copywriting** - Set `ANTHROPIC_API_KEY` for much better results
2. **Provide Detailed Briefs** - Include objective, audience, tone, and key messages
3. **Check Quality Scores** - Aim for 80+/100 on the validation scoring
4. **Always test** - Preview in Litmus or Email on Acid
5. **Check personalization** - Ensure Liquid variables exist in Braze
6. **Mobile first** - Test on mobile devices
7. **Subject length** - Keep under 50 characters for mobile
8. **Preheader** - Always include a compelling preheader

## Troubleshooting

### "AI copywriting not available" warning
- **Solution**: Set `ANTHROPIC_API_KEY` environment variable
- Get your key from: https://console.anthropic.com/
- For Streamlit Cloud: Add as a secret in app settings
- App will fall back to template-based generation automatically

### Copy quality score is low (< 60)
- **Solution**: Provide more detailed campaign brief
- Specify tone, audience segment, and key messages
- Include specific CTAs and personalization requirements
- Review PRAY.COM brand voice guidelines above

### Generic/corporate-sounding copy
- **Solution**: Enable AI copywriting (requires API key)
- Without AI: Copy may need significant manual editing
- Check that brief includes emotional context (stress, hunger for peace, etc.)

### Template not rendering in Outlook
- Ensure VML fallbacks are included (automatic with `cta_button`)
- Check for unsupported CSS properties

### Liquid errors in Braze
- Verify custom attribute names match exactly
- Use `| default:` filters for optional attributes
- Test with preview users

### Mobile layout issues
- Check responsive breakpoints in template
- Test on actual mobile devices
- Verify padding and font sizes are mobile-friendly
