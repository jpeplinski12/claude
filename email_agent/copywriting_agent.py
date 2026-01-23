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
        # STEP 1: Extract specific details first
        extraction_prompt = f"""Read this campaign brief and extract SPECIFIC CONCRETE DETAILS:

BRIEF: {campaign_brief}

Extract and list:
- Numbers (millions, thousands, prices, timeframes, percentages, counts)
- Names (people, products, features)
- Dollar amounts
- Timeframes (60 seconds, 1 hour, 30 days)
- Quantities (10,000+ prayers, 10M+ users)

Output ONLY a bulleted list of these specific details, nothing else."""

        extraction_response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=256,
            temperature=0.3,
            messages=[{"role": "user", "content": extraction_prompt}]
        )

        extracted_details = extraction_response.content[0].text.strip()

        # STEP 2: Generate copy that MUST use these specifics
        prompt = f"""{self.brand_voice.get_copywriting_prompt(campaign_type, campaign_brief, segment)}

EXTRACTED SPECIFIC DETAILS FROM YOUR BRIEF:
{extracted_details}

CRITICAL INSTRUCTION: You MUST use AT LEAST 2-3 of these specific details in your copy.
Do NOT write generic copy. Do NOT use forbidden phrases.

Now generate the email copy. Follow these rules STRICTLY:

1. HEADLINE (5-10 words):
   ❌ NEVER use: "Welcome", "Discover", "Introducing", "Check Out", "New Feature"
   ✅ MUST include: A specific number, name, or detail from the list above
   ✅ Example: "Your $49.99 Premium is waiting" or "60 seconds to 10,000+ prayers"

2. SUBHEADLINE (one sentence or empty):
   - Include another specific detail from the list
   - Use contractions (you've, we're) to sound conversational

3. BODY (2-3 paragraphs):
   ❌ FORBIDDEN phrases: "we're excited", "pleased to announce", "we have", "feature", "functionality", "check out", "discover"
   ✅ REQUIRED: Start paragraphs with "You" or reference their specific situation
   ✅ MUST include: AT LEAST ONE specific detail from the list above PER PARAGRAPH

4. CTA (2-4 words):
   ❌ NEVER: "Learn More", "Get Started", "Discover"
   ✅ Use: Specific action with detail (e.g., "Complete My $49.99", "Unlock 10,000+ Prayers", "Finish in 60 Seconds")

Format as JSON:
{{
    "headline": "Your headline here",
    "subheadline": "Optional subheadline or empty string",
    "body_paragraphs": ["First paragraph", "Second paragraph", "Optional third paragraph"],
    "cta_text": "Button Text"
}}

SELF-CHECK BEFORE RESPONDING:
- Did headline include a specific number/detail? If no, REWRITE.
- Did body paragraphs each include specific details? If no, REWRITE.
- Did you use "we're excited", "we have", or "discover"? If yes, REWRITE.
- Did you use contractions? If no, ADD THEM."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1500,
                temperature=0.7,
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
        # STEP 1: Extract key details from context
        extraction_prompt = f"""Read this campaign brief and extract SPECIFIC CONCRETE DETAILS (numbers, names, amounts, timeframes):

BRIEF: {context}

List out ONLY the specific details (numbers, dollar amounts, people's names, specific timeframes, specific features):
- Example: "10M+ believers", "$49.99/year", "Matthew McConaughey", "60 seconds", "10,000+ prayers"

Output ONLY a bulleted list of specific details, nothing else."""

        extraction_response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=256,
            temperature=0.3,
            messages=[{"role": "user", "content": extraction_prompt}]
        )

        extracted_details = extraction_response.content[0].text.strip()

        # STEP 2: Generate subject lines that MUST use these details
        prompt = f"""{self.brand_voice.get_subject_line_prompt(context, tone, segment)}

EXTRACTED SPECIFIC DETAILS FROM THE BRIEF:
{extracted_details}

CRITICAL REQUIREMENT: Each subject line MUST include AT LEAST ONE of the specific details above.
Do NOT use generic language. Do NOT use: "Discover", "Introducing", "Check Out", "New", "Welcome"

Generate {num_variants} distinct subject lines. EACH LINE MUST CONTAIN A SPECIFIC DETAIL FROM THE LIST ABOVE.

Examples of SPECIFIC vs GENERIC:
❌ BAD: "Discover peace today" (no specifics)
❌ BAD: "Your Premium awaits" (no specifics)
✅ GOOD: "Your $49.99 Premium saved 💛" (includes price)
✅ GOOD: "Join 10M believers - cart saved" (includes number)
✅ GOOD: "60 seconds to 10,000+ prayers" (includes timeframe and number)

Output ONLY the subject lines, one per line, no numbering or explanations."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=512,
                temperature=0.8,  # Lower temperature for more instruction-following
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            content = response.content[0].text
            subject_lines = [line.strip() for line in content.strip().split("\n") if line.strip()]

            # STEP 3: Validate each line contains a number or specific detail
            validated_lines = []
            for line in subject_lines[:num_variants]:
                # Check if line contains at least one digit or specific word from context
                has_number = any(char.isdigit() for char in line)
                # Extract some key words from extracted details
                detail_words = [word.strip('- ') for word in extracted_details.lower().split() if len(word) > 3]
                has_specific = any(word in line.lower() for word in detail_words[:10])

                if has_number or has_specific:
                    validated_lines.append(line)

            # If we don't have enough validated lines, use what we have
            subject_lines = validated_lines if len(validated_lines) >= 3 else subject_lines[:num_variants]

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
                    model="claude-sonnet-4-20250514",
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
                model="claude-sonnet-4-20250514",
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
                model="claude-sonnet-4-20250514",
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
