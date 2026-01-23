"""
AI-Powered Copywriting Agent for PRAY.COM
==========================================
Uses Anthropic's Claude API to generate brand-aligned email copy.
"""

import os
import json
from typing import Dict, List, Optional
from anthropic import Anthropic

from brand_voice import BrandVoice


class CopywritingAgent:
    """
    Generates high-quality email copy using AI, aligned with PRAY.COM's brand voice.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the copywriting agent.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key required. Set ANTHROPIC_API_KEY environment variable or pass api_key parameter.")

        self.client = Anthropic(api_key=self.api_key)
        self.brand_voice = BrandVoice()

    def generate_email_copy(
        self,
        campaign_brief: str,
        campaign_type: str = "promotional",
        segment: str = "general",
        tone: str = "inspiring"
    ) -> Dict[str, any]:
        """
        Generate complete email copy from a campaign brief.

        Args:
            campaign_brief: Natural language description of the campaign
            campaign_type: Type of campaign (daily_prayer, premium, abandoned_cart, etc.)
            segment: Audience segment (general, new_users, engaged, lapsed, premium)
            tone: Desired tone (inspiring, urgent, curious, personal, celebration)

        Returns:
            Dictionary with headline, subheadline, body_paragraphs, and cta_text
        """
        prompt = f"""{self.brand_voice.get_copywriting_prompt(campaign_type, campaign_brief, segment)}

Based on the creative brief above, generate:

1. HEADLINE: Compelling and specific to THIS campaign (5-10 words). Not generic like "Welcome" or "Discover More"
2. SUBHEADLINE: Supporting detail that adds context (one sentence, or empty string if not needed)
3. BODY: 2-3 short paragraphs. Each paragraph should:
   - Reference specific details from the brief
   - Use conversational, everyday language
   - Show you understand their situation
   - Feel personal, not like a mass email
4. CTA: Action-oriented button text (2-4 words) that's specific to what they'll do

Format as JSON:
{{
    "headline": "Your headline here",
    "subheadline": "Optional subheadline or empty string",
    "body_paragraphs": ["First paragraph", "Second paragraph", "Optional third paragraph"],
    "cta_text": "Button Text"
}}

CRITICAL REMINDERS:
- Use specific details from the brief (don't be vague!)
- Write like you're texting a friend, not writing a press release
- Show empathy for their situation
- Reference God's presence naturally
- Make every word count (mobile users are busy)"""

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1500,
                temperature=0.9,  # Higher temperature for more creative, specific copy
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Extract JSON from response
            content = response.content[0].text

            # Try to parse JSON from the response
            # Sometimes Claude wraps JSON in markdown code blocks
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                json_str = content.strip()

            result = json.loads(json_str)

            # Validate the copy
            full_copy = f"{result['headline']} {result['subheadline']} {' '.join(result['body_paragraphs'])}"
            validation = BrandVoice.validate_copy(full_copy)

            result["validation"] = validation

            return result

        except Exception as e:
            # Fallback to template-based generation if API fails
            print(f"Warning: AI generation failed ({str(e)}), using fallback")
            return self._fallback_generation(campaign_brief, campaign_type)

    def generate_subject_lines(
        self,
        context: str,
        segment: str = "general",
        tone: str = "inspiring",
        num_variants: int = 5
    ) -> Dict[str, any]:
        """
        Generate benefit-driven subject lines using AI.

        Args:
            context: Campaign context/description
            segment: Audience segment
            tone: Desired tone
            num_variants: Number of subject line variants to generate

        Returns:
            Dictionary with primary subject lines and A/B variants
        """
        prompt = f"""{self.brand_voice.get_subject_line_prompt(context, tone, segment)}

Generate {num_variants} distinct subject lines that embody PRAY.COM's brand voice.

Each line should:
- Be under 50 characters for mobile
- Create curiosity or offer clear benefit
- Use warm, conversational language
- Feel like it's from a trusted friend, not a company
- Can optionally include Braze personalization: {{{{custom_attribute.${{first_name}}}}}}

Output ONLY the subject lines, one per line, no numbering or explanations."""

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=512,
                temperature=1.0,  # High temperature for diverse, creative subject lines
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            content = response.content[0].text
            subject_lines = [line.strip() for line in content.strip().split("\n") if line.strip()]

            # Generate A/B variants
            ab_variants = []
            for i, line in enumerate(subject_lines[:3]):
                variant_prompt = f"""Given this subject line for PRAY.COM: "{line}"

Create an A/B test variant and explain the hypothesis.

BRAND VOICE: Faithful, encouraging, approachable, digitally-savvy.

The variant should test a different approach (e.g., with/without emoji, question vs statement, personalized vs generic, urgency vs curiosity).

Format as JSON:
{{
    "variant_b": "Alternative subject line here",
    "hypothesis": "Brief explanation of what we're testing and why"
}}"""

                variant_response = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=256,
                    temperature=0.8,
                    messages=[{
                        "role": "user",
                        "content": variant_prompt
                    }]
                )

                variant_content = variant_response.content[0].text

                # Parse JSON
                if "```json" in variant_content:
                    json_str = variant_content.split("```json")[1].split("```")[0].strip()
                elif "```" in variant_content:
                    json_str = variant_content.split("```")[1].split("```")[0].strip()
                else:
                    json_str = variant_content.strip()

                try:
                    variant_data = json.loads(json_str)
                    ab_variants.append({
                        "a": line,
                        "b": variant_data["variant_b"],
                        "hypothesis": variant_data["hypothesis"]
                    })
                except:
                    # Fallback if JSON parsing fails
                    ab_variants.append({
                        "a": line,
                        "b": f"🙏 {line}",
                        "hypothesis": "Testing if adding emoji increases open rate"
                    })

            return {
                "primary": subject_lines[:num_variants],
                "ab_variants": ab_variants,
                "metadata": {
                    "context": context,
                    "segment": segment,
                    "tone": tone,
                    "generation_method": "ai"
                }
            }

        except Exception as e:
            print(f"Warning: AI subject line generation failed ({str(e)})")
            # Fallback to template-based generation
            from subject_line_factory import SubjectLineFactory
            factory = SubjectLineFactory()
            return factory.generate(context, segment, tone, num_variants)

    def refine_copy(self, copy: str, feedback: str) -> str:
        """
        Refine existing copy based on feedback.

        Args:
            copy: Existing email copy
            feedback: Feedback or revision request

        Returns:
            Refined copy
        """
        prompt = f"""You are a copywriter for PRAY.COM. Here's some email copy that needs refinement:

CURRENT COPY:
{copy}

FEEDBACK:
{feedback}

BRAND VOICE REMINDER:
- Faithful, encouraging, approachable, digitally-savvy
- Like a compassionate pastor crossed with a tech-forward friend
- Warm and conversational, never corporate
- Empower rather than preach

Please revise the copy based on the feedback while maintaining PRAY.COM's brand voice.
Output ONLY the revised copy, no explanations."""

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                temperature=0.7,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            return response.content[0].text.strip()

        except Exception as e:
            print(f"Warning: Copy refinement failed ({str(e)})")
            return copy

    def _fallback_generation(self, brief: str, campaign_type: str) -> Dict:
        """Fallback to template-based generation if AI fails."""
        return {
            "headline": "A Special Message for You",
            "subheadline": "Your faith journey continues",
            "body_paragraphs": [
                "We have something meaningful to share with you today.",
                "Take a moment to connect with God and find the peace you've been seeking."
            ],
            "cta_text": "Learn More",
            "validation": {
                "score": 60,
                "passes": False,
                "issues": ["Fallback generation - using generic templates"],
                "power_word_count": 0
            }
        }

    def generate_preheader(self, subject_line: str, context: str) -> str:
        """
        Generate a complementary preheader for a subject line.

        Args:
            subject_line: The email subject line
            context: Campaign context

        Returns:
            Preheader text (50-100 characters)
        """
        prompt = f"""Generate a compelling email preheader text for PRAY.COM.

SUBJECT LINE: {subject_line}
CONTEXT: {context}

BRAND VOICE: Faithful, encouraging, approachable, digitally-savvy.

The preheader should:
- Complement the subject line (not repeat it)
- Be 50-100 characters
- Create curiosity or reinforce benefit
- Use warm, conversational language
- Work well on mobile

Output ONLY the preheader text, no explanations."""

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=128,
                temperature=0.7,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            return response.content[0].text.strip()[:100]

        except:
            return "Open to learn more..."


# Example usage
if __name__ == "__main__":
    # This requires ANTHROPIC_API_KEY environment variable
    try:
        agent = CopywritingAgent()

        # Example: Generate email copy
        result = agent.generate_email_copy(
            campaign_brief="""
            Launch campaign for our new "Year in Prayer" feature that shows users their
            prayer stats and journey over the past year. Target engaged users who have
            been active on the app. Tone should be celebratory and inspiring. CTA to
            view their personalized stats.
            """,
            campaign_type="year_in_review",
            segment="engaged",
            tone="celebration"
        )

        print("Generated Email Copy:")
        print(json.dumps(result, indent=2))

    except ValueError as e:
        print(f"Note: {e}")
        print("Set ANTHROPIC_API_KEY environment variable to test AI generation")
