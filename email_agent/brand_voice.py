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
        return f"""You are a senior copywriter for PRAY.COM, a Christian prayer and meditation app. Write email copy that feels like it's from a close friend who deeply cares about the reader's spiritual journey.

CRITICAL: Avoid generic, corporate, or vague language at all costs. Be SPECIFIC, PERSONAL, and CONVERSATIONAL.

BRAND VOICE:
{BrandVoice.tone_guidelines}

EXAMPLES OF GREAT VS. BAD COPY:

❌ BAD (Generic, corporate, vague):
"We have implemented a new feature that allows users to access premium content through our platform."
"View your annual statistics and usage metrics for the previous calendar year."
"Our meditation functionality provides enhanced spiritual growth opportunities."

✅ GOOD (Specific, personal, conversational):
"Meet your new bedtime companion. Our Sleep Stories blend Scripture with calming narration to help you rest in God's peace."
"Look how far you've come. Your 387 minutes in prayer this year show a heart seeking God — and He sees every moment."
"You were so close to starting your journey. We saved your spot — ready to continue?"

WRITING RULES (MUST FOLLOW):
DO:
{chr(10).join('- ' + principle for principle in BrandVoice.writing_principles['dos'])}

DON'T:
{chr(10).join('- ' + principle for principle in BrandVoice.writing_principles['donts'])}

CAMPAIGN TYPE: {campaign_type}
TARGET SEGMENT: {segment}
CREATIVE BRIEF: {context}

Based on this brief, write copy that:
1. Directly addresses the reader's specific situation (use details from the brief!)
2. Feels warm and personal, like a text from a caring friend
3. References God's presence naturally (not forced or preachy)
4. Uses simple, everyday language (how you'd actually talk)
5. Gives a clear, specific next step
6. Shows you understand their struggle/desire (meet them where they are)

Generate ONLY the copy, no explanations."""

    @staticmethod
    def get_subject_line_prompt(context: str, tone: str, segment: str = "general") -> str:
        """Generate a prompt for subject line generation."""
        return f"""You are writing email subject lines for PRAY.COM, a Christian prayer and meditation app.

BRAND VOICE: Like a close friend who cares deeply about their spiritual journey. Warm, personal, never corporate.

TONE: {tone}
TARGET SEGMENT: {segment}
CONTEXT: {context}

SUBJECT LINE REQUIREMENTS:
- Under 50 characters for mobile
- Specific to THIS campaign (use details from context!)
- Warm and conversational (like texting a friend)
- Create curiosity OR offer clear personal benefit
- Can use emojis naturally (🙏 ✨ 💛 🕊️ 📖)
- Optional Braze personalization: {{{{custom_attribute.${{first_name}}}}}}

EXAMPLES OF SPECIFIC VS. GENERIC:

❌ TOO GENERIC (avoid these):
"New Feature Available"
"Check Out What's New"
"Important Update Inside"
"Your Weekly Newsletter"
"Premium Subscription Benefits"

✅ SPECIFIC & PERSONAL (aim for this):
"Your 387 minutes in prayer 💛"
"{{{{custom_attribute.${{first_name}}}}}}, you were so close"
"The prayer that changed Sarah's mornings"
"Your 30-day streak deserves this 🙏"
"What happens when you pray at bedtime?"

Based on the context above, generate 5 subject lines that:
1. Reference specific details from the campaign
2. Feel personal and conversational
3. Would make someone actually want to open the email
4. Avoid corporate/generic language

Output ONLY the subject lines, one per line, no numbering or explanations."""


# Example usage and validation
def validate_copy(copy: str) -> Dict[str, any]:
    """
    Validate if copy aligns with PRAY.COM brand voice.

    Returns:
        Dictionary with validation results and suggestions
    """
    issues = []
    score = 100

    # Check for avoid words (more severe penalty)
    for word in BrandVoice.avoid_words:
        if word.lower() in copy.lower():
            issues.append(f"Uses corporate word '{word}' - replace with conversational alternative")
            score -= 15  # Increased penalty

    # Check for power words (should have at least 2)
    power_word_count = sum(1 for word in BrandVoice.power_words if word.lower() in copy.lower())
    if power_word_count < 2:
        issues.append("Could use more brand power words (peace, journey, heart, faith, discover)")
        score -= 5  # Reduced penalty
    elif power_word_count >= 4:
        score += 5  # Bonus for good use

    # Check for "you" language
    you_count = copy.lower().count("you") + copy.lower().count("your")
    if you_count == 0:
        issues.append("Missing 'you' language - should speak directly to reader")
        score -= 10  # Reduced penalty
    elif you_count >= 3:
        score += 5  # Bonus for personal language

    # Check for generic phrases (major penalty)
    generic_phrases = [
        "we are pleased to announce",
        "we are excited to share",
        "we are excited to",
        "we have implemented",
        "we have",
        "we're excited",
        "platform update",
        "new functionality",
        "enhanced features",
        "usage metrics",
        "annual statistics",
        "access premium content",
        "check out",
        "discover more",
        "learn more about",
        "introducing",
        "welcome to",
        "new feature",
        "take advantage"
    ]
    for phrase in generic_phrases:
        if phrase.lower() in copy.lower():
            issues.append(f"GENERIC PHRASE: '{phrase}' - sounds corporate, rewrite personally")
            score -= 25  # Heavier penalty

    # Check for overly formal punctuation
    if copy.count(";") > 0:
        issues.append("Semicolons feel too formal - use shorter sentences")
        score -= 3  # Reduced penalty

    # Check for contractions (should use them for conversational tone)
    contraction_words = ["you're", "we're", "you've", "we've", "don't", "can't", "won't"]
    has_contractions = any(word in copy.lower() for word in contraction_words)
    if not has_contractions and len(copy) > 50:
        issues.append("Consider using contractions (you're, we've) for more conversational tone")
        score -= 5

    # Bonus for specific details (numbers, names, concrete examples)
    digit_count = sum(1 for char in copy if char.isdigit())
    if digit_count >= 3:
        score += 10  # Strong bonus for multiple specific numbers
        issues.append("✅ Good use of specific numbers/details!")
    elif digit_count > 0:
        score += 5  # Some bonus for specificity
    else:
        issues.append("Missing specific numbers/details - add concrete examples from brief")
        score -= 10

    # Check if copy starts sentences with "You" (very personal)
    sentences = copy.split('.')
    you_starts = sum(1 for s in sentences if s.strip().lower().startswith('you'))
    if you_starts >= 2:
        score += 5  # Bonus for personal sentence structure
        issues.append("✅ Great use of 'you' language!")

    return {
        "score": max(0, min(100, score)),  # Cap between 0-100
        "passes": score >= 70,  # Raise threshold back up
        "issues": issues,
        "power_word_count": power_word_count
    }
