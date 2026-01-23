"""
PRAY.COM Brand Voice Configuration
===================================
Defines PRAY.COM's brand personality, tone guidelines, and copywriting principles.
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class BrandVoice:
    """PRAY.COM's brand voice and tone guidelines."""

    # Core brand personality traits
    personality_traits = [
        "Faithful and reverent",
        "Encouraging and uplifting",
        "Warm and conversational",
        "Modern and accessible",
        "Guiding and empowering"
    ]

    # Tone characteristics
    tone_guidelines = """
PRAY.COM's brand personality is faithful, encouraging, approachable, and digitally-savvy.
It speaks like a compassionate pastor crossed with a tech-forward friend, always pointing
users toward a deeper connection with God while meeting them exactly where they are — often
in moments of stress, fatigue, or spiritual hunger.

🙏 Faith-Focused and Reverent
PRAY.COM positions itself as a spiritual companion. Its tone reflects respect for Christian
values and Scripture, often speaking with humility and devotion. It emphasizes God's presence,
biblical truth, and prayer as central to its mission.

🌟 Inspirational and Uplifting
The brand aims to elevate and encourage, offering hope, peace, and strength through stories,
guided prayers, devotionals, and content from pastors and faith leaders. It speaks to users
who may be struggling or seeking deeper meaning, using positive, affirming language that
inspires personal growth and faithfulness.

💬 Warm and Conversational
Despite being a faith platform, PRAY.COM avoids overly formal or inaccessible language. Its
messaging feels personal and inviting, like a trusted friend or community member. It often
uses second-person language ("you") to draw the user in and create an emotional connection.

📱 Modern and Accessible
The brand is highly aware of its digital context. It blends traditional Christian content
with modern formats like apps, podcasts, SMS, and emails. The tone is simple, clear, and
optimized for quick consumption on mobile — reflecting a personality that values ease, reach,
and relevance.

💡 Guiding and Empowering
Rather than preaching, PRAY.COM tends to guide and empower users to take small, meaningful
actions — like listening to a bedtime prayer, starting a devotional, or donating to a pastor.
It gives the user a sense of agency in their spiritual walk.
"""

    # Writing principles
    writing_principles = {
        "dos": [
            "Speak directly to the reader using 'you'",
            "Use warm, conversational language",
            "Focus on benefits and transformation",
            "Include specific, actionable next steps",
            "Reference God's presence and biblical truth naturally",
            "Meet users where they are emotionally",
            "Use simple, mobile-friendly language",
            "Empower rather than preach",
            "Create emotional connection through storytelling",
            "Acknowledge struggles while offering hope"
        ],
        "donts": [
            "Don't use overly formal or religious jargon",
            "Don't preach or lecture",
            "Don't make assumptions about faith level",
            "Don't be vague or abstract",
            "Don't use corporate or sales-y language",
            "Don't make guilt-based appeals",
            "Don't be long-winded or complex",
            "Don't ignore the digital context"
        ]
    }

    # Voice examples by campaign type
    voice_examples = {
        "daily_prayer": {
            "good": "Start your morning with a moment of peace. Today's prayer is ready for you.",
            "bad": "Please access your daily spiritual content via the application interface."
        },
        "premium_upsell": {
            "good": "You've taken the first step. Now unlock unlimited prayers, ad-free listening, and a deeper connection with God.",
            "bad": "Upgrade to Premium subscription to access enhanced features and premium content."
        },
        "abandoned_cart": {
            "good": "You were so close to starting your journey. We saved your spot — ready to continue?",
            "bad": "You left items in your cart. Complete your purchase to proceed."
        },
        "year_in_review": {
            "good": "Look how far you've come. Your 387 minutes in prayer this year show a heart seeking God — and He sees every moment.",
            "bad": "View your annual statistics and usage metrics for the previous calendar year."
        },
        "new_feature": {
            "good": "Meet your new bedtime companion. Our Sleep Stories blend Scripture with calming narration to help you rest in God's peace.",
            "bad": "We have released a new feature category called Sleep Stories which is now available."
        }
    }

    # Key phrases that embody the brand
    signature_phrases = [
        "Your faith journey",
        "Meet you where you are",
        "A moment of peace",
        "Rest in God's presence",
        "Take the next step",
        "You're never alone",
        "Start your day grounded",
        "Find your peace",
        "Connect with God anywhere",
        "Join millions in prayer"
    ]

    # Words to use frequently
    power_words = [
        "peace", "journey", "moment", "heart", "soul", "discover",
        "find", "connect", "start", "rest", "hope", "strength",
        "faith", "prayer", "guided", "daily", "transform", "deepen"
    ]

    # Words to avoid
    avoid_words = [
        "leverage", "utilize", "synergy", "interface", "solution",
        "onboarding", "metrics", "dashboard", "access", "platform",
        "deploy", "implement", "functionality", "parameters"
    ]

    @staticmethod
    def get_copywriting_prompt(campaign_type: str, context: str, segment: str = "general") -> str:
        """
        Generate a copywriting prompt that enforces PRAY.COM's brand voice.

        Args:
            campaign_type: Type of campaign (daily_prayer, premium, abandoned_cart, etc.)
            context: Campaign brief or context
            segment: Audience segment

        Returns:
            Prompt string for AI copywriting
        """
        return f"""You are a copywriter for PRAY.COM, a Christian prayer and meditation app. Your mission is to write email copy that embodies PRAY.COM's brand voice.

BRAND VOICE GUIDELINES:
{BrandVoice.tone_guidelines}

WRITING PRINCIPLES:
DO:
{chr(10).join('- ' + principle for principle in BrandVoice.writing_principles['dos'])}

DON'T:
{chr(10).join('- ' + principle for principle in BrandVoice.writing_principles['donts'])}

SIGNATURE PHRASES TO USE:
{', '.join(BrandVoice.signature_phrases[:5])}

CAMPAIGN TYPE: {campaign_type}
TARGET SEGMENT: {segment}
CONTEXT: {context}

Write compelling email copy that:
1. Speaks like a compassionate pastor crossed with a tech-forward friend
2. Meets the user where they are emotionally (stress, fatigue, spiritual hunger)
3. Points toward deeper connection with God
4. Uses warm, conversational language (not corporate or sales-y)
5. Empowers rather than preaches
6. Is mobile-friendly and concise
7. Includes specific, actionable next steps

Generate ONLY the copy, no explanations or meta-commentary."""

    @staticmethod
    def get_subject_line_prompt(context: str, tone: str, segment: str = "general") -> str:
        """Generate a prompt for subject line generation."""
        return f"""You are writing email subject lines for PRAY.COM, a Christian prayer and meditation app.

BRAND VOICE: Faithful, encouraging, approachable, digitally-savvy. Like a compassionate pastor crossed with a tech-forward friend.

TONE: {tone}
TARGET SEGMENT: {segment}
CONTEXT: {context}

SUBJECT LINE BEST PRACTICES:
- Keep it under 50 characters for mobile
- Create curiosity or offer clear benefit
- Use warm, conversational language
- Avoid overly formal or corporate tone
- Can use emojis sparingly (🙏 ✨ 💛 🕊️ 📖)
- Use "you" language to create connection
- Reference faith/prayer naturally, not forced

GOOD EXAMPLES:
- "Your peace starts here 🙏"
- "{{{{custom_attribute.${{first_name}}}}}}, we saved this for you"
- "What 5 minutes of prayer did for Sarah"
- "Ready to start your day grounded?"
- "You've come so far this year"

BAD EXAMPLES:
- "Access Premium Features Today" (too corporate)
- "Devotional Content Available" (too bland)
- "Spiritual Growth Platform Update" (too formal)

Generate 5 subject lines that embody PRAY.COM's voice. Output ONLY the subject lines, one per line, no numbering."""


# Example usage and validation
def validate_copy(copy: str) -> Dict[str, any]:
    """
    Validate if copy aligns with PRAY.COM brand voice.

    Returns:
        Dictionary with validation results and suggestions
    """
    issues = []
    score = 100

    # Check for avoid words
    for word in BrandVoice.avoid_words:
        if word.lower() in copy.lower():
            issues.append(f"Uses corporate word '{word}' - consider more conversational alternative")
            score -= 10

    # Check for power words (should have at least 2)
    power_word_count = sum(1 for word in BrandVoice.power_words if word.lower() in copy.lower())
    if power_word_count < 2:
        issues.append("Could use more brand power words (peace, journey, heart, etc.)")
        score -= 10

    # Check for "you" language
    if "you" not in copy.lower() and "your" not in copy.lower():
        issues.append("Missing 'you' language - should speak directly to reader")
        score -= 15

    # Check for overly formal punctuation
    if copy.count(";") > 0:
        issues.append("Semicolons feel too formal - use shorter sentences")
        score -= 5

    # Check length (mobile-friendly)
    if len(copy) > 500:
        issues.append("Copy might be too long for mobile - consider breaking into shorter paragraphs")
        score -= 10

    return {
        "score": max(0, score),
        "passes": score >= 70,
        "issues": issues,
        "power_word_count": power_word_count
    }
