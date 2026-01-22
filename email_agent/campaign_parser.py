"""
Campaign Brief Parser
=====================
Parses campaign briefs to extract structured information
for template generation.
"""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ParsedBrief:
    """Structured representation of a parsed campaign brief."""
    campaign_name: str
    headline: str
    subheadline: str
    body_content: List[str]
    cta_text: str
    cta_url: str
    context: str
    segment: str
    tone: str
    personalization: Dict
    sections: List[Dict]


class CampaignBriefParser:
    """
    Parses natural language campaign briefs into structured data
    for email template generation.
    """

    # Keywords for segment detection
    SEGMENT_KEYWORDS = {
        "new_users": ["new user", "onboarding", "welcome", "first time", "getting started", "just joined"],
        "engaged": ["active", "engaged", "regular", "loyal", "frequent", "dedicated"],
        "lapsed": ["lapsed", "inactive", "dormant", "haven't been", "miss you", "come back", "return"],
        "premium": ["premium", "subscriber", "paid", "plus", "pro", "member", "vip"]
    }

    # Keywords for tone detection
    TONE_KEYWORDS = {
        "urgent": ["urgent", "limited time", "hurry", "act now", "last chance", "ending soon", "deadline"],
        "curious": ["discover", "secret", "reveal", "surprising", "unexpected", "mystery"],
        "personal": ["personal", "individual", "just for you", "tailored", "customized"],
        "celebration": ["celebrate", "congratulations", "achievement", "milestone", "anniversary", "special"]
    }

    # CTA keyword mapping
    CTA_KEYWORDS = {
        "start": ["start", "begin", "get started", "launch"],
        "join": ["join", "sign up", "register", "enroll"],
        "learn": ["learn", "discover", "explore", "find out"],
        "try": ["try", "experience", "test"],
        "download": ["download", "get", "install"],
        "donate": ["donate", "give", "support", "contribute"],
        "subscribe": ["subscribe", "upgrade", "unlock"],
        "read": ["read", "see", "view", "check out"],
        "listen": ["listen", "hear", "tune in"],
        "pray": ["pray", "meditate", "reflect"]
    }

    def __init__(self):
        pass

    def parse(self, brief: str) -> Dict:
        """
        Parse a campaign brief into structured data.

        Args:
            brief: Natural language campaign brief text

        Returns:
            Dictionary with extracted components
        """
        brief_lower = brief.lower()

        # Extract components
        campaign_name = self._extract_campaign_name(brief)
        headline = self._extract_headline(brief)
        subheadline = self._extract_subheadline(brief)
        body_content = self._extract_body_content(brief)
        cta_text, cta_url = self._extract_cta(brief)
        segment = self._detect_segment(brief_lower)
        tone = self._detect_tone(brief_lower)
        personalization = self._extract_personalization(brief_lower)
        sections = self._extract_sections(brief)

        return {
            "campaign_name": campaign_name,
            "headline": headline,
            "subheadline": subheadline,
            "body_content": body_content,
            "cta_text": cta_text,
            "cta_url": cta_url,
            "context": brief,
            "segment": segment,
            "tone": tone,
            "personalization": personalization,
            "sections": sections
        }

    def _extract_campaign_name(self, brief: str) -> str:
        """Extract or generate campaign name."""
        # Look for explicit campaign name
        patterns = [
            r"campaign[:\s]+[\"']?([^\"'\n]+)[\"']?",
            r"name[:\s]+[\"']?([^\"'\n]+)[\"']?",
            r"for[:\s]+[\"']?([^\"'\n]+)[\"']?(?:\s+campaign)?",
        ]

        for pattern in patterns:
            match = re.search(pattern, brief, re.IGNORECASE)
            if match:
                return match.group(1).strip()[:50]

        # Generate from first significant words
        words = brief.split()[:5]
        return " ".join(w for w in words if len(w) > 3)[:50] or "Campaign"

    def _extract_headline(self, brief: str) -> str:
        """Extract or generate headline."""
        # Look for explicit headline
        patterns = [
            r"headline[:\s]+[\"']?([^\"'\n]+)[\"']?",
            r"title[:\s]+[\"']?([^\"'\n]+)[\"']?",
            r"subject[:\s]+[\"']?([^\"'\n]+)[\"']?",
        ]

        for pattern in patterns:
            match = re.search(pattern, brief, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        # Generate from context
        return self._generate_headline_from_context(brief)

    def _generate_headline_from_context(self, brief: str) -> str:
        """Generate a headline from the campaign context."""
        brief_lower = brief.lower()

        # Feature launches
        if "new" in brief_lower and any(w in brief_lower for w in ["feature", "launch", "introducing"]):
            topic = self._extract_topic(brief)
            return f"Introducing {topic}"

        # Bible/devotional campaigns
        if "bible" in brief_lower:
            return "Your Daily Scripture Awaits"

        # Year in review
        if "year" in brief_lower and any(w in brief_lower for w in ["review", "stats", "journey"]):
            return "Your Year in Prayer"

        # Meditation
        if "meditation" in brief_lower or "meditat" in brief_lower:
            return "Find Your Peace Today"

        # Community
        if "community" in brief_lower:
            return "Join Our Prayer Community"

        # Default
        return "A Special Message for You"

    def _extract_topic(self, brief: str) -> str:
        """Extract the main topic from the brief."""
        # Look for quoted topics
        quoted = re.findall(r"[\"']([^\"']+)[\"']", brief)
        if quoted:
            return quoted[0]

        # Look for capitalized phrases
        caps = re.findall(r"\b([A-Z][a-z]+(?: [A-Z][a-z]+)*)\b", brief)
        if caps:
            # Filter out common words
            caps = [c for c in caps if c.lower() not in ["the", "a", "an", "for", "to"]]
            if caps:
                return caps[0]

        return "this feature"

    def _extract_subheadline(self, brief: str) -> str:
        """Extract optional subheadline."""
        patterns = [
            r"subheadline[:\s]+[\"']?([^\"'\n]+)[\"']?",
            r"subtitle[:\s]+[\"']?([^\"'\n]+)[\"']?",
            r"tagline[:\s]+[\"']?([^\"'\n]+)[\"']?",
        ]

        for pattern in patterns:
            match = re.search(pattern, brief, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return ""

    def _extract_body_content(self, brief: str) -> List[str]:
        """Extract body content paragraphs."""
        content = []

        # Look for explicit body content
        body_match = re.search(r"body[:\s]+(.+?)(?:cta|button|$)", brief, re.IGNORECASE | re.DOTALL)
        if body_match:
            text = body_match.group(1).strip()
            paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
            return paragraphs if paragraphs else [text]

        # Look for key message
        message_patterns = [
            r"message[:\s]+[\"']?([^\"'\n]+)[\"']?",
            r"highlight[:\s]+[\"']?([^\"'\n]+)[\"']?",
            r"key point[:\s]+[\"']?([^\"'\n]+)[\"']?",
        ]

        for pattern in message_patterns:
            match = re.search(pattern, brief, re.IGNORECASE)
            if match:
                content.append(match.group(1).strip())

        # Generate default content from brief context
        if not content:
            content = self._generate_body_from_context(brief)

        return content

    def _generate_body_from_context(self, brief: str) -> List[str]:
        """Generate body content from campaign context."""
        brief_lower = brief.lower()
        content = []

        # Detect campaign type and generate appropriate content
        if "year" in brief_lower and "prayer" in brief_lower:
            content.append("Take a moment to celebrate your prayer journey this past year.")
            content.append("We've gathered your personal stats to show just how far you've come.")

        elif "bible" in brief_lower:
            content.append("Start each day grounded in Scripture with our guided reading plan.")
            content.append("Join thousands who are discovering the peace of daily Bible reading.")

        elif "meditation" in brief_lower:
            content.append("Find moments of peace and reflection in your busy day.")
            content.append("Our guided meditations help you connect with God anywhere, anytime.")

        elif "community" in brief_lower:
            content.append("You're never alone in your faith journey.")
            content.append("Connect with millions of believers around the world in prayer.")

        else:
            # Default content
            content.append("We have something special to share with you.")

        return content

    def _extract_cta(self, brief: str) -> tuple:
        """Extract CTA text and URL."""
        # Look for explicit CTA
        cta_patterns = [
            r"cta[:\s]+[\"']?([^\"'\n]+)[\"']?",
            r"button[:\s]+[\"']?([^\"'\n]+)[\"']?",
            r"call.to.action[:\s]+[\"']?([^\"'\n]+)[\"']?",
        ]

        cta_text = "Learn More"
        for pattern in cta_patterns:
            match = re.search(pattern, brief, re.IGNORECASE)
            if match:
                cta_text = match.group(1).strip()
                break

        # If no explicit CTA, detect from context
        if cta_text == "Learn More":
            cta_text = self._detect_cta_from_context(brief.lower())

        # Look for URL
        url_patterns = [
            r"url[:\s]+[\"']?([^\s\"']+)[\"']?",
            r"link[:\s]+[\"']?([^\s\"']+)[\"']?",
            r"(https?://[^\s\"']+)",
        ]

        cta_url = "https://pray.com"
        for pattern in url_patterns:
            match = re.search(pattern, brief, re.IGNORECASE)
            if match:
                cta_url = match.group(1).strip()
                break

        return cta_text, cta_url

    def _detect_cta_from_context(self, brief: str) -> str:
        """Detect appropriate CTA text from context."""
        for cta_type, keywords in self.CTA_KEYWORDS.items():
            for keyword in keywords:
                if keyword in brief:
                    cta_map = {
                        "start": "Start Now",
                        "join": "Join Now",
                        "learn": "Learn More",
                        "try": "Try It Free",
                        "download": "Download Now",
                        "donate": "Give Now",
                        "subscribe": "Subscribe",
                        "read": "Read More",
                        "listen": "Listen Now",
                        "pray": "Start Praying"
                    }
                    return cta_map.get(cta_type, "Learn More")

        return "Learn More"

    def _detect_segment(self, brief: str) -> str:
        """Detect target audience segment."""
        for segment, keywords in self.SEGMENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in brief:
                    return segment
        return "general"

    def _detect_tone(self, brief: str) -> str:
        """Detect desired email tone."""
        for tone, keywords in self.TONE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in brief:
                    return tone

        # Check for explicit tone
        tone_match = re.search(r"tone[:\s]+[\"']?(\w+)[\"']?", brief, re.IGNORECASE)
        if tone_match:
            detected = tone_match.group(1).lower()
            if detected in ["inspiring", "urgent", "curious", "personal", "celebration"]:
                return detected

        return "inspiring"

    def _extract_personalization(self, brief: str) -> Dict:
        """Extract personalization requirements."""
        personalization = {
            "use_first_name": True,  # Default to using first name
            "use_stats": False,
            "use_preferences": False,
            "conditional_content": False
        }

        if "personal" in brief or "name" in brief:
            personalization["use_first_name"] = True

        if "stats" in brief or "metrics" in brief or "data" in brief:
            personalization["use_stats"] = True

        if "preference" in brief or "interest" in brief:
            personalization["use_preferences"] = True

        if "conditional" in brief or "segment" in brief or "if" in brief:
            personalization["conditional_content"] = True

        return personalization

    def _extract_sections(self, brief: str) -> List[Dict]:
        """Extract additional content sections."""
        sections = []
        brief_lower = brief.lower()

        # Detect section types from brief
        if "stats" in brief_lower or "metrics" in brief_lower:
            sections.append({
                "type": "stat_card",
                "icon": "📊",
                "value": "{{custom_attribute.${metric}}}",
                "label": "Your Progress",
                "liquid_var": "total_minutes_listened"
            })

        if "feature" in brief_lower:
            sections.append({
                "type": "feature_grid",
                "features": [
                    {"icon": "🙏", "title": "Daily Prayer", "description": "Start each day with guided prayer"},
                    {"icon": "📖", "title": "Scripture", "description": "Daily Bible readings and devotionals"},
                ]
            })

        if "image" in brief_lower or "hero" in brief_lower:
            # Look for image URL
            img_match = re.search(r"image[:\s]+[\"']?([^\s\"']+)[\"']?", brief, re.IGNORECASE)
            if img_match:
                sections.append({
                    "type": "image",
                    "src": img_match.group(1),
                    "alt": "Campaign Image"
                })

        return sections

    def validate_brief(self, brief: str) -> Dict:
        """Validate a campaign brief and return suggestions."""
        issues = []
        suggestions = []

        if len(brief) < 20:
            issues.append("Brief is too short")
            suggestions.append("Add more context about the campaign goal and target audience")

        if not any(word in brief.lower() for word in ["goal", "objective", "purpose", "promote", "announce"]):
            suggestions.append("Consider adding a clear campaign objective")

        if not any(word in brief.lower() for word in self.SEGMENT_KEYWORDS.keys()):
            if not any(word in brief.lower() for words in self.SEGMENT_KEYWORDS.values() for word in words):
                suggestions.append("Consider specifying the target audience segment")

        if not re.search(r"cta|button|call.to.action", brief, re.IGNORECASE):
            suggestions.append("Consider specifying a call-to-action")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions
        }
