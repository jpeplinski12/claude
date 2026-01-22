"""
Subject Line Factory
====================
Generates benefit-driven, curiosity-sparking email subject lines
with automatic A/B test variants.
"""

import random
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class SubjectLineStyle:
    """Configuration for subject line style."""
    name: str
    templates: List[str]
    description: str


class SubjectLineFactory:
    """
    Generates email subject lines optimized for open rates.

    Styles supported:
    - Curiosity hooks: "What happens when you pray this before bed?"
    - Benefit-driven: "Start your morning with peace and purpose"
    - Personal: "{{first_name}}, your prayer journey awaits"
    - Urgency: "24 hours left to join thousands in prayer"
    - Question-based: "Ready to transform your prayer life?"
    """

    # Proven subject line templates organized by style
    TEMPLATES = {
        "curiosity": [
            "What happens when you {action}",
            "The {adjective} thing about {topic}",
            "You won't believe what {subject} discovered",
            "This {adjective} {noun} changes everything",
            "Here's what {number}+ people learned about {topic}",
            "The secret to {benefit} (it's not what you think)",
            "Why {topic} is {outcome}",
            "What no one tells you about {topic}",
            "The {adjective} way to {benefit}",
            "This changes how you think about {topic}",
        ],
        "benefit": [
            "Start your {timeframe} with {benefit}",
            "Find {benefit} in just {duration}",
            "{benefit} starts here",
            "Your path to {benefit}",
            "Experience {benefit} today",
            "Discover the {benefit} you've been seeking",
            "{action} your way to {benefit}",
            "Unlock {benefit} with {method}",
            "The {benefit} you deserve",
            "Transform your {aspect} with {method}",
        ],
        "personal": [
            "{{{{custom_attribute.${{first_name}}}}}}, {message}",
            "A message for you, {{{{custom_attribute.${{first_name}}}}}}",
            "{{{{custom_attribute.${{first_name}}}}}}, we thought of you",
            "This is for you, {{{{custom_attribute.${{first_name}}}}}}",
            "{{{{custom_attribute.${{first_name}}}}}}, your {noun} awaits",
            "Just for you: {offer}",
            "{{{{custom_attribute.${{first_name}}}}}}, something special inside",
            "We made this for you, {{{{custom_attribute.${{first_name}}}}}}",
        ],
        "urgency": [
            "{timeframe} left to {action}",
            "Don't miss: {offer}",
            "Ending soon: {offer}",
            "Last chance to {action}",
            "Today only: {offer}",
            "{number} hours left",
            "Before it's gone: {offer}",
            "Your {offer} expires {timeframe}",
            "Act now: {offer}",
            "Limited time: {offer}",
        ],
        "question": [
            "Ready to {action}?",
            "What if you could {benefit}?",
            "Have you tried {method}?",
            "Looking for {benefit}?",
            "Want to {action}?",
            "Can {duration} change your {aspect}?",
            "What would {benefit} mean for you?",
            "Is {topic} on your mind?",
            "Could this be your {noun}?",
            "Ever wondered about {topic}?",
        ],
        "story": [
            "How {subject} found {benefit}",
            "The {adjective} story of {subject}",
            "From {state_a} to {state_b}",
            "{subject}'s journey to {benefit}",
            "What {subject} taught us about {topic}",
            "The moment everything changed for {subject}",
        ],
        "number": [
            "{number} ways to {action}",
            "{number} {noun} that will {benefit}",
            "The {number}-{unit} {method} for {benefit}",
            "{number} reasons to {action} today",
            "{number} {adjective} {noun} you need",
            "In just {number} {unit}: {benefit}",
        ],
        "emoji": [
            "{emoji} {message}",
            "{message} {emoji}",
            "{emoji} {message} {emoji}",
        ]
    }

    # Prayer/faith-specific vocabulary
    FAITH_VOCABULARY = {
        "actions": [
            "pray", "meditate", "reflect", "worship", "give thanks",
            "seek guidance", "find peace", "connect with God", "study Scripture",
            "join in prayer", "start your day with prayer", "pray before bed"
        ],
        "benefits": [
            "peace", "hope", "clarity", "strength", "comfort", "joy",
            "guidance", "connection", "purpose", "faith", "serenity",
            "inner peace", "spiritual growth", "renewed faith"
        ],
        "nouns": [
            "prayer", "devotional", "Scripture", "journey", "blessing",
            "meditation", "reflection", "moment", "verse", "reading plan"
        ],
        "timeframes": [
            "morning", "evening", "day", "night", "week", "moment"
        ],
        "adjectives": [
            "powerful", "transformative", "daily", "peaceful", "inspiring",
            "life-changing", "simple", "beautiful", "meaningful", "sacred"
        ],
        "emojis": [
            "🙏", "✨", "💛", "🕊️", "📖", "💫", "🌅", "🌙", "❤️", "🔥"
        ]
    }

    # Segment-specific modifiers
    SEGMENT_MODIFIERS = {
        "general": {
            "tone": "welcoming",
            "urgency_level": "low",
            "personalization": "optional"
        },
        "new_users": {
            "tone": "encouraging",
            "urgency_level": "low",
            "focus": ["getting started", "first steps", "welcome"],
            "personalization": "high"
        },
        "engaged": {
            "tone": "appreciative",
            "urgency_level": "medium",
            "focus": ["deepen", "continue", "next level"],
            "personalization": "high"
        },
        "lapsed": {
            "tone": "gentle",
            "urgency_level": "low",
            "focus": ["return", "miss you", "welcome back"],
            "personalization": "high"
        },
        "premium": {
            "tone": "exclusive",
            "urgency_level": "medium",
            "focus": ["exclusive", "premium", "special access"],
            "personalization": "high"
        }
    }

    def __init__(self):
        self.vocab = self.FAITH_VOCABULARY

    def generate(
        self,
        context: str,
        segment: str = "general",
        tone: str = "inspiring",
        num_variants: int = 5,
        include_emoji: bool = True,
        max_length: int = 50
    ) -> Dict:
        """
        Generate subject lines with A/B test variants.

        Args:
            context: Campaign context/description
            segment: Target audience segment
            tone: Desired tone (inspiring, urgent, curious, personal, celebration)
            num_variants: Number of primary subject lines to generate
            include_emoji: Whether to include emoji variants
            max_length: Maximum subject line length

        Returns:
            Dictionary with primary lines, A/B variants, and metadata
        """
        # Extract key elements from context
        elements = self._extract_elements(context)

        # Select appropriate styles based on tone
        styles = self._select_styles(tone, segment)

        # Generate primary subject lines
        primary_lines = []
        for _ in range(num_variants):
            style = random.choice(styles)
            line = self._generate_line(style, elements, segment, include_emoji)
            if len(line) <= max_length and line not in primary_lines:
                primary_lines.append(line)

        # Ensure we have enough unique lines
        attempts = 0
        while len(primary_lines) < num_variants and attempts < 20:
            style = random.choice(styles)
            line = self._generate_line(style, elements, segment, include_emoji)
            if len(line) <= max_length and line not in primary_lines:
                primary_lines.append(line)
            attempts += 1

        # Generate A/B test variants
        ab_variants = self._generate_ab_variants(primary_lines[:3], elements, segment)

        return {
            "primary": primary_lines,
            "ab_variants": ab_variants,
            "metadata": {
                "context": context,
                "segment": segment,
                "tone": tone,
                "styles_used": styles
            }
        }

    def _extract_elements(self, context: str) -> Dict:
        """Extract key elements from the campaign context."""
        context_lower = context.lower()

        elements = {
            "topic": self._extract_topic(context),
            "benefit": self._find_matching_word(context_lower, self.vocab["benefits"]) or "peace",
            "action": self._find_matching_word(context_lower, self.vocab["actions"]) or "pray",
            "noun": self._find_matching_word(context_lower, self.vocab["nouns"]) or "prayer",
            "timeframe": self._find_matching_word(context_lower, self.vocab["timeframes"]) or "day",
            "adjective": random.choice(self.vocab["adjectives"]),
            "emoji": random.choice(self.vocab["emojis"]),
            "number": random.choice(["3", "5", "7", "10", "21", "30"]),
            "duration": random.choice(["5 minutes", "10 minutes", "a moment", "one minute"]),
            "unit": random.choice(["minute", "day", "step"]),
        }

        # Extract specific offers or features mentioned
        if "bible" in context_lower:
            elements["topic"] = "Bible reading"
            elements["noun"] = "Scripture"
        if "meditation" in context_lower:
            elements["action"] = "meditate"
            elements["topic"] = "meditation"
        if "year" in context_lower:
            elements["topic"] = "your year in prayer"
        if "streak" in context_lower:
            elements["benefit"] = "consistency"
        if "community" in context_lower:
            elements["benefit"] = "connection"

        return elements

    def _extract_topic(self, context: str) -> str:
        """Extract the main topic from context."""
        # Simple extraction - in production would use NLP
        words = context.split()
        for word in words:
            if len(word) > 4 and word.lower() not in ["about", "their", "would", "could", "should"]:
                return word.lower()
        return "prayer"

    def _find_matching_word(self, context: str, word_list: List[str]) -> Optional[str]:
        """Find a matching word from the vocabulary in the context."""
        for word in word_list:
            if word.lower() in context:
                return word
        return None

    def _select_styles(self, tone: str, segment: str) -> List[str]:
        """Select appropriate subject line styles based on tone and segment."""
        style_map = {
            "inspiring": ["benefit", "story", "question"],
            "urgent": ["urgency", "number", "benefit"],
            "curious": ["curiosity", "question", "story"],
            "personal": ["personal", "benefit", "question"],
            "celebration": ["emoji", "benefit", "personal"]
        }

        base_styles = style_map.get(tone, ["benefit", "question"])

        # Adjust for segment
        if segment == "new_users":
            base_styles = ["benefit", "question", "personal"]
        elif segment == "lapsed":
            base_styles = ["personal", "benefit", "curiosity"]
        elif segment == "premium":
            base_styles = ["benefit", "personal", "curiosity"]

        return base_styles

    def _generate_line(
        self,
        style: str,
        elements: Dict,
        segment: str,
        include_emoji: bool
    ) -> str:
        """Generate a single subject line."""
        templates = self.TEMPLATES.get(style, self.TEMPLATES["benefit"])
        template = random.choice(templates)

        # Fill in template
        line = template.format(
            action=elements.get("action", "pray"),
            topic=elements.get("topic", "prayer"),
            benefit=elements.get("benefit", "peace"),
            noun=elements.get("noun", "prayer"),
            adjective=elements.get("adjective", "powerful"),
            timeframe=elements.get("timeframe", "day"),
            duration=elements.get("duration", "5 minutes"),
            number=elements.get("number", "5"),
            unit=elements.get("unit", "day"),
            emoji=elements.get("emoji", "🙏") if include_emoji else "",
            message=self._get_contextual_message(elements),
            subject="thousands",
            offer=self._get_offer_text(elements),
            method=f"{elements.get('adjective', 'daily')} {elements.get('noun', 'prayer')}",
            aspect=random.choice(["morning", "prayer life", "faith journey", "day"]),
            state_a=random.choice(["stress", "uncertainty", "chaos"]),
            state_b=random.choice(["peace", "clarity", "faith"]),
            outcome=random.choice(["transforming lives", "changing everything", "so powerful"]),
        )

        # Capitalize first letter
        line = line[0].upper() + line[1:] if line else line

        return line.strip()

    def _get_contextual_message(self, elements: Dict) -> str:
        """Get a contextual message based on elements."""
        messages = [
            f"find {elements.get('benefit', 'peace')} today",
            f"your {elements.get('noun', 'prayer')} journey continues",
            f"discover something {elements.get('adjective', 'powerful')}",
            f"we have something for you",
            f"start your {elements.get('timeframe', 'day')} right",
        ]
        return random.choice(messages)

    def _get_offer_text(self, elements: Dict) -> str:
        """Get offer text based on elements."""
        offers = [
            f"{elements.get('adjective', 'powerful')} {elements.get('noun', 'prayers')}",
            f"your {elements.get('benefit', 'peace')} awaits",
            f"join {elements.get('number', 'thousands')} in prayer",
            f"a special {elements.get('noun', 'devotional')}",
        ]
        return random.choice(offers)

    def _generate_ab_variants(
        self,
        primary_lines: List[str],
        elements: Dict,
        segment: str
    ) -> List[Dict]:
        """Generate A/B test variant pairs with hypotheses."""
        variants = []

        for line in primary_lines:
            # Generate variations for testing
            variant_b, hypothesis = self._create_variant(line, elements)

            variants.append({
                "a": line,
                "b": variant_b,
                "hypothesis": hypothesis
            })

        return variants

    def _create_variant(self, original: str, elements: Dict) -> tuple:
        """Create a variant of a subject line with a testing hypothesis."""
        strategies = [
            self._add_emoji_variant,
            self._add_personalization_variant,
            self._change_tone_variant,
            self._add_urgency_variant,
            self._question_variant,
        ]

        strategy = random.choice(strategies)
        return strategy(original, elements)

    def _add_emoji_variant(self, original: str, elements: Dict) -> tuple:
        """Add or change emoji."""
        emoji = elements.get("emoji", "🙏")
        if emoji in original:
            # Remove emoji
            variant = original.replace(emoji, "").strip()
            hypothesis = "Testing if removing emoji improves professional feel"
        else:
            # Add emoji
            variant = f"{emoji} {original}"
            hypothesis = "Testing if emoji increases open rate through visual appeal"
        return variant, hypothesis

    def _add_personalization_variant(self, original: str, elements: Dict) -> tuple:
        """Add personalization."""
        if "{{" in original:
            # Already personalized, make generic
            variant = original.split(",")[-1].strip() if "," in original else original
            hypothesis = "Testing generic vs personalized subject lines"
        else:
            variant = f"{{{{custom_attribute.${{first_name}}}}}}, {original[0].lower()}{original[1:]}"
            hypothesis = "Testing if personalization with first name increases open rate"
        return variant, hypothesis

    def _change_tone_variant(self, original: str, elements: Dict) -> tuple:
        """Change the tone of the subject line."""
        if "?" in original:
            # Change question to statement
            variant = original.replace("?", "").replace("Ready to", "Time to")
            hypothesis = "Testing question vs statement format"
        else:
            # Change statement to question
            variant = f"Ready to {original[0].lower()}{original[1:]}?"
            hypothesis = "Testing statement vs question format"
        return variant, hypothesis

    def _add_urgency_variant(self, original: str, elements: Dict) -> tuple:
        """Add urgency element."""
        urgent_prefixes = ["Today:", "Now:", "Don't wait:"]
        prefix = random.choice(urgent_prefixes)
        variant = f"{prefix} {original}"
        hypothesis = "Testing if urgency prefix increases immediate opens"
        return variant, hypothesis

    def _question_variant(self, original: str, elements: Dict) -> tuple:
        """Convert to curiosity question."""
        variant = f"What if you could {elements.get('action', 'pray')} your way to {elements.get('benefit', 'peace')}?"
        hypothesis = "Testing curiosity-driven question format"
        return variant, hypothesis

    def generate_preheader(self, subject: str, context: str) -> str:
        """Generate a complementary preheader for a subject line."""
        preheaders = [
            f"Discover what {context} can do for you",
            "Open to learn more...",
            f"Your journey to {self._extract_elements(context).get('benefit', 'peace')} starts now",
            "We thought you'd want to see this",
            "Something special inside",
            f"Join thousands finding {self._extract_elements(context).get('benefit', 'peace')}",
        ]
        return random.choice(preheaders)
