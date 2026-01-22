#!/usr/bin/env python3
"""
PRAY.COM Email Template Generator Agent
========================================
An AI-powered agent that generates EAA-compliant, mobile-responsive HTML email
templates and benefit-driven subject lines for Braze campaigns.

Usage:
    python email_agent.py generate --brief "Campaign brief text"
    python email_agent.py subjects --context "Campaign context" --segment "Audience segment"
    python email_agent.py interactive
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from template_generator import EmailTemplateGenerator
from subject_line_factory import SubjectLineFactory
from campaign_parser import CampaignBriefParser


class EmailAgent:
    """Main agent orchestrating email template and subject line generation."""

    def __init__(self, output_dir: str = "./output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.template_generator = EmailTemplateGenerator()
        self.subject_factory = SubjectLineFactory()
        self.brief_parser = CampaignBriefParser()

    def generate_from_brief(self, brief: str, template_type: str = "promotional") -> dict:
        """
        Generate a complete email package from a campaign brief.

        Args:
            brief: Campaign brief text describing the email purpose
            template_type: Type of template (promotional, transactional, newsletter, announcement)

        Returns:
            Dictionary with html_template, subject_lines, and metadata
        """
        # Parse the campaign brief
        parsed = self.brief_parser.parse(brief)

        # Generate HTML template
        html = self.template_generator.generate(
            campaign_name=parsed.get("campaign_name", "Campaign"),
            headline=parsed.get("headline", ""),
            subheadline=parsed.get("subheadline", ""),
            body_content=parsed.get("body_content", []),
            cta_text=parsed.get("cta_text", "Learn More"),
            cta_url=parsed.get("cta_url", "https://pray.com"),
            template_type=template_type,
            personalization=parsed.get("personalization", {}),
            sections=parsed.get("sections", [])
        )

        # Generate subject lines
        subjects = self.subject_factory.generate(
            context=parsed.get("context", brief),
            segment=parsed.get("segment", "general"),
            tone=parsed.get("tone", "inspiring"),
            num_variants=5
        )

        result = {
            "html_template": html,
            "subject_lines": subjects,
            "parsed_brief": parsed,
            "generated_at": datetime.now().isoformat(),
            "template_type": template_type
        }

        return result

    def generate_subjects_only(
        self,
        context: str,
        segment: str = "general",
        tone: str = "inspiring",
        num_variants: int = 5
    ) -> dict:
        """Generate only subject lines for a campaign."""
        subjects = self.subject_factory.generate(
            context=context,
            segment=segment,
            tone=tone,
            num_variants=num_variants
        )

        return {
            "subject_lines": subjects,
            "context": context,
            "segment": segment,
            "generated_at": datetime.now().isoformat()
        }

    def save_output(self, result: dict, filename: str) -> Path:
        """Save generated content to files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"{filename}_{timestamp}"

        # Save HTML template
        if "html_template" in result:
            html_path = self.output_dir / f"{base_name}.html"
            html_path.write_text(result["html_template"])
            print(f"HTML template saved to: {html_path}")

        # Save subject lines
        if "subject_lines" in result:
            subjects_path = self.output_dir / f"{base_name}_subjects.json"
            subjects_path.write_text(json.dumps(result["subject_lines"], indent=2))
            print(f"Subject lines saved to: {subjects_path}")

        # Save full result
        result_path = self.output_dir / f"{base_name}_full.json"
        # Remove HTML from JSON to keep it readable
        json_result = {k: v for k, v in result.items() if k != "html_template"}
        json_result["html_file"] = f"{base_name}.html"
        result_path.write_text(json.dumps(json_result, indent=2))

        return self.output_dir

    def interactive_mode(self):
        """Run the agent in interactive mode."""
        print("\n" + "=" * 60)
        print("  PRAY.COM Email Template Generator Agent")
        print("=" * 60)
        print("\nCommands:")
        print("  1. generate  - Generate full email from brief")
        print("  2. subjects  - Generate subject lines only")
        print("  3. template  - Generate template with custom options")
        print("  4. help      - Show detailed help")
        print("  5. quit      - Exit the agent")
        print()

        while True:
            try:
                command = input("\n> Enter command: ").strip().lower()

                if command in ["quit", "exit", "q"]:
                    print("Goodbye!")
                    break

                elif command in ["1", "generate"]:
                    self._interactive_generate()

                elif command in ["2", "subjects"]:
                    self._interactive_subjects()

                elif command in ["3", "template"]:
                    self._interactive_template()

                elif command in ["4", "help"]:
                    self._show_help()

                else:
                    print("Unknown command. Type 'help' for available commands.")

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")

    def _interactive_generate(self):
        """Interactive full generation flow."""
        print("\n--- Generate Email from Brief ---")
        print("Enter your campaign brief (press Enter twice to finish):")

        lines = []
        while True:
            line = input()
            if line == "":
                if lines and lines[-1] == "":
                    break
                lines.append(line)
            else:
                lines.append(line)

        brief = "\n".join(lines[:-1])  # Remove trailing empty line

        if not brief.strip():
            print("No brief provided.")
            return

        print("\nSelect template type:")
        print("  1. promotional (default)")
        print("  2. newsletter")
        print("  3. announcement")
        print("  4. transactional")

        type_choice = input("Template type [1]: ").strip() or "1"
        type_map = {"1": "promotional", "2": "newsletter", "3": "announcement", "4": "transactional"}
        template_type = type_map.get(type_choice, "promotional")

        print("\nGenerating email package...")
        result = self.generate_from_brief(brief, template_type)

        # Display subject lines
        print("\n--- Generated Subject Lines ---")
        for i, subject in enumerate(result["subject_lines"]["primary"], 1):
            print(f"  {i}. {subject}")

        print("\n--- A/B Test Variants ---")
        for variant in result["subject_lines"]["ab_variants"]:
            print(f"  A: {variant['a']}")
            print(f"  B: {variant['b']}")
            print()

        # Save option
        save = input("\nSave to files? [Y/n]: ").strip().lower()
        if save != "n":
            name = input("Filename (without extension): ").strip() or "email_campaign"
            self.save_output(result, name)

    def _interactive_subjects(self):
        """Interactive subject line generation."""
        print("\n--- Subject Line Factory ---")

        context = input("Campaign context/description: ").strip()
        if not context:
            print("Context is required.")
            return

        print("\nAudience segments:")
        print("  1. general")
        print("  2. new_users")
        print("  3. engaged")
        print("  4. lapsed")
        print("  5. premium")

        seg_choice = input("Select segment [1]: ").strip() or "1"
        seg_map = {
            "1": "general", "2": "new_users", "3": "engaged",
            "4": "lapsed", "5": "premium"
        }
        segment = seg_map.get(seg_choice, "general")

        print("\nTone options:")
        print("  1. inspiring (default)")
        print("  2. urgent")
        print("  3. curious")
        print("  4. personal")
        print("  5. celebration")

        tone_choice = input("Select tone [1]: ").strip() or "1"
        tone_map = {
            "1": "inspiring", "2": "urgent", "3": "curious",
            "4": "personal", "5": "celebration"
        }
        tone = tone_map.get(tone_choice, "inspiring")

        num = input("Number of variants [5]: ").strip() or "5"

        print("\nGenerating subject lines...")
        result = self.generate_subjects_only(context, segment, tone, int(num))

        print("\n--- Primary Subject Lines ---")
        for i, subject in enumerate(result["subject_lines"]["primary"], 1):
            print(f"  {i}. {subject}")

        print("\n--- A/B Test Pairs ---")
        for i, variant in enumerate(result["subject_lines"]["ab_variants"], 1):
            print(f"  Pair {i}:")
            print(f"    A: {variant['a']}")
            print(f"    B: {variant['b']}")
            print(f"    Hypothesis: {variant['hypothesis']}")
            print()

    def _interactive_template(self):
        """Interactive template generation with full customization."""
        print("\n--- Custom Template Builder ---")

        campaign_name = input("Campaign name: ").strip() or "Campaign"
        headline = input("Main headline: ").strip()
        subheadline = input("Subheadline (optional): ").strip()

        print("\nEnter body paragraphs (empty line to finish):")
        body_content = []
        while True:
            para = input("  Paragraph: ").strip()
            if not para:
                break
            body_content.append(para)

        cta_text = input("CTA button text [Learn More]: ").strip() or "Learn More"
        cta_url = input("CTA URL [https://pray.com]: ").strip() or "https://pray.com"

        print("\nTemplate type:")
        print("  1. promotional")
        print("  2. newsletter")
        print("  3. announcement")

        type_choice = input("Select [1]: ").strip() or "1"
        type_map = {"1": "promotional", "2": "newsletter", "3": "announcement"}
        template_type = type_map.get(type_choice, "promotional")

        print("\nGenerating template...")
        html = self.template_generator.generate(
            campaign_name=campaign_name,
            headline=headline,
            subheadline=subheadline,
            body_content=body_content,
            cta_text=cta_text,
            cta_url=cta_url,
            template_type=template_type
        )

        save = input("\nSave template? [Y/n]: ").strip().lower()
        if save != "n":
            name = input("Filename: ").strip() or campaign_name.lower().replace(" ", "_")
            path = self.output_dir / f"{name}.html"
            path.write_text(html)
            print(f"Saved to: {path}")

    def _show_help(self):
        """Display detailed help information."""
        help_text = """
PRAY.COM Email Template Generator Agent
=======================================

This agent helps you create EAA-compliant, mobile-responsive HTML email
templates for Braze campaigns, along with benefit-driven subject lines.

FEATURES:
---------
1. Email Template Generator
   - Generates mobile-responsive HTML emails
   - Braze Liquid templating support
   - Outlook VML compatibility
   - Dark theme with gold accents (PRAY.COM brand)
   - Multiple template types: promotional, newsletter, announcement

2. Subject Line Factory
   - Benefit-driven, curiosity-sparking headlines
   - Multiple audience segment targeting
   - Automatic A/B test variant generation
   - Various tone options

CAMPAIGN BRIEF FORMAT:
---------------------
When providing a brief, include:
- Campaign objective/goal
- Target audience/segment
- Key message or offer
- Desired tone
- Any specific calls-to-action
- Personalization requirements

Example brief:
"Launch campaign for our new 'Bible in a Year' reading plan.
Target: engaged users who have completed at least one devotional.
Highlight the guided daily readings and community aspect.
Tone: inspiring and inviting. CTA: Start Your Journey"

SUBJECT LINE STYLES:
-------------------
The factory generates subject lines in proven styles:
- Curiosity hooks: "What happens when you pray this before bed?"
- Benefit-driven: "Start your morning with peace and purpose"
- Personal: "{{first_name}}, your prayer journey awaits"
- Urgency: "24 hours left to join thousands in prayer"
- Question-based: "Ready to transform your prayer life?"

TEMPLATE TYPES:
--------------
1. promotional - Product/feature launches, special offers
2. newsletter - Regular updates, content digests
3. announcement - Important news, events
4. transactional - Account-related, confirmations

OUTPUT:
-------
- HTML file ready for Braze upload
- JSON file with subject lines and A/B variants
- Metadata file with generation details
        """
        print(help_text)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="PRAY.COM Email Template Generator Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python email_agent.py interactive
  python email_agent.py generate --brief "Launch campaign for Bible in a Year..."
  python email_agent.py subjects --context "New meditation feature" --segment engaged
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate email from brief")
    gen_parser.add_argument("--brief", "-b", required=True, help="Campaign brief text")
    gen_parser.add_argument("--type", "-t", default="promotional",
                           choices=["promotional", "newsletter", "announcement", "transactional"],
                           help="Template type")
    gen_parser.add_argument("--output", "-o", default="./output", help="Output directory")
    gen_parser.add_argument("--name", "-n", default="campaign", help="Output filename base")

    # Subjects command
    sub_parser = subparsers.add_parser("subjects", help="Generate subject lines only")
    sub_parser.add_argument("--context", "-c", required=True, help="Campaign context")
    sub_parser.add_argument("--segment", "-s", default="general",
                           choices=["general", "new_users", "engaged", "lapsed", "premium"],
                           help="Audience segment")
    sub_parser.add_argument("--tone", "-t", default="inspiring",
                           choices=["inspiring", "urgent", "curious", "personal", "celebration"],
                           help="Subject line tone")
    sub_parser.add_argument("--num", "-n", type=int, default=5, help="Number of variants")

    # Interactive command
    subparsers.add_parser("interactive", help="Run in interactive mode")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    agent = EmailAgent(output_dir=getattr(args, "output", "./output"))

    if args.command == "interactive":
        agent.interactive_mode()

    elif args.command == "generate":
        result = agent.generate_from_brief(args.brief, args.type)
        agent.save_output(result, args.name)

        print("\n--- Generated Subject Lines ---")
        for i, subject in enumerate(result["subject_lines"]["primary"], 1):
            print(f"  {i}. {subject}")

    elif args.command == "subjects":
        result = agent.generate_subjects_only(
            args.context, args.segment, args.tone, args.num
        )

        print("\n--- Subject Lines ---")
        for i, subject in enumerate(result["subject_lines"]["primary"], 1):
            print(f"  {i}. {subject}")

        print("\n--- A/B Variants ---")
        for variant in result["subject_lines"]["ab_variants"]:
            print(f"  A: {variant['a']}")
            print(f"  B: {variant['b']}")
            print()


if __name__ == "__main__":
    main()
