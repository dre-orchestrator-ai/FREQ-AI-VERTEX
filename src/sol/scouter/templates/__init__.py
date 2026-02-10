"""
Templates for Executor Scouter

LinkedIn post templates and outreach sequence message templates.
All templates designed for founder-authentic voice.
"""

from .linkedin_posts import (
    LINKEDIN_POST_TEMPLATES,
    PostCategory,
    render_post,
    get_templates_by_category,
)

from .outreach_sequences import (
    OUTREACH_TEMPLATES,
    render_outreach_message,
    get_template,
)

__all__ = [
    "LINKEDIN_POST_TEMPLATES",
    "PostCategory",
    "render_post",
    "get_templates_by_category",
    "OUTREACH_TEMPLATES",
    "render_outreach_message",
    "get_template",
]
