"""
PRAY.COM Email Template Generator Agent
=======================================

An AI-powered agent for generating EAA-compliant, mobile-responsive
HTML email templates and benefit-driven subject lines for Braze campaigns.
"""

from .template_generator import EmailTemplateGenerator, EmailConfig
from .subject_line_factory import SubjectLineFactory
from .campaign_parser import CampaignBriefParser
from .components import EmailComponents

__version__ = "1.0.0"
__all__ = [
    "EmailTemplateGenerator",
    "EmailConfig",
    "SubjectLineFactory",
    "CampaignBriefParser",
    "EmailComponents"
]
