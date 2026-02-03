"""
Outreach Message Templates for Partnership Development

Multi-touch sequence templates for cold, warm, and follow-up outreach.
All templates designed for founder-authentic voice.
"""

from typing import Dict, Any, Optional


OUTREACH_TEMPLATES: Dict[str, str] = {

    # === VC COLD OUTREACH ===

    "vc_post_comment": """Insightful perspective on {post_topic}.

The point about {specific_point} resonates - we're seeing similar patterns building AI agent orchestration for enterprise.

Curious: how do you think about governance in agentic systems?""",

    "vc_connection_request": """Hi {first_name},

Enjoyed your recent post on {post_topic}. Building something relevant - FREQ is an AI agent orchestration platform with enterprise governance baked in.

Currently pre-seed, looking for investors who understand the enterprise AI infrastructure space. Would love to connect.

- Dre, Founder @ FREQ""",

    "vc_intro_message": """Hi {first_name},

Thanks for connecting. Quick context on FREQ:

We're building governed AI agents for enterprise - think multi-agent systems with built-in compliance (sub-2s response times, consensus voting, full audit trails).

Our first vertical is maritime logistics (VECTOR GAMMA) - using LiDAR + Digital Twins for automated cargo measurement.

{portfolio_connection}

Would a 15-min call make sense to share what we're building?

Best,
Dre""",

    "vc_followup_message": """Hi {first_name},

Following up - I know your calendar is packed.

Quick update: we just {recent_milestone}.

If FREQ isn't a fit for {firm_name}, totally understand. Would you point me toward anyone in your network who focuses on AI infrastructure or maritime tech?

Appreciate any direction.

Dre""",

    # === ENTERPRISE COLD OUTREACH ===

    "enterprise_post_comment": """Great point about {topic}.

We're building AI agent orchestration that might address {pain_point} - would love to share what we're seeing in the space.""",

    "enterprise_connection_request": """Hi {first_name},

Noticed {company}'s work in {area}. Building something complementary at FREQ - governed AI agents for enterprise operations.

Would value connecting to learn more about your team's priorities.

- Dre""",

    "enterprise_intro_message": """Hi {first_name},

Thanks for connecting. Wanted to share context:

FREQ builds AI agent orchestration with enterprise governance - compliance baked in, not bolted on.

Relevant to {company} because:
{relevance_point_1}
{relevance_point_2}

Currently looking for design partners to refine our enterprise features. Any interest in a quick demo?

Best,
Dre""",

    # === WARM INTRO REQUESTS ===

    "warm_intro_request": """Hi {connector_name},

Hope you're doing well! Quick ask:

I noticed you're connected to {target_name} at {target_company}. I'm building FREQ (AI agent orchestration for enterprise) and {target_company} would be a perfect {relationship_type}.

Would you be comfortable making an intro? Happy to:
1. Send you a forwardable blurb
2. Draft the intro for you
3. Just get context on best approach

{personal_touch}

No pressure if it's not a good fit. Appreciate you either way.

Dre""",

    "warm_intro_followup": """Following up on the intro request. Here's a forwardable blurb if helpful:

---

{target_first_name},

My friend Dre is building FREQ - an AI agent orchestration platform with enterprise governance built-in. Think multi-agent systems with compliance (audit trails, consensus voting, sub-2s latency).

His first use case is maritime logistics using LiDAR + Azure Digital Twins.

He's looking for {relationship_type}s and I thought you'd be a good connection. Mind if I intro you two?

---

Feel free to modify. Thanks {connector_name}!""",

    "warm_intro_forwardable_blurb": """{target_first_name},

My friend Dre is building FREQ - an AI agent orchestration platform with enterprise governance built-in.

Key points:
→ Multi-agent systems with built-in compliance
→ <2000ms SLA, consensus voting, full audit trails
→ First vertical: maritime logistics with LiDAR + Digital Twins

He's looking for {relationship_type}s and I thought you'd be interested.

Mind if I connect you two?""",

    # === POST-MEETING FOLLOW-UP ===

    "meeting_recap_email": """Subject: Great connecting - FREQ next steps

Hi {first_name},

Thanks for taking the time today. Recap of what we discussed:

{meeting_summary}

As promised, here's:
→ {deliverable_1}
→ {deliverable_2}

Next steps we agreed on:
{next_steps}

Let me know if you have questions. Looking forward to {next_meeting_topic}.

Best,
Dre

P.S. {personal_note}""",

    "meeting_followup_linkedin": """Hi {first_name},

Following up on our conversation last week.

Wanted to share: {relevant_update}

Still interested in {next_step_topic}? Happy to schedule when convenient.

Dre""",

    "meeting_second_followup": """Subject: Re: Great connecting - FREQ next steps

Hi {first_name},

Checking in - I know things get busy.

Quick update from our side: {company_update}

Still keen to {proposed_action}. Would next week work for a follow-up?

Dre""",

    # === MFSIN SPECIFIC ===

    "mfsin_application_followup": """Subject: Microsoft for Startups Application - FREQ

Hi,

Following up on our Microsoft for Startups Founders Hub application submitted on {submission_date}.

Quick summary of FREQ:
→ AI agent orchestration platform with enterprise governance
→ Azure-native: Foundry, Databricks, Digital Twins integration
→ First vertical: Maritime logistics with LiDAR automation

We're excited about the Azure ecosystem and would love to discuss how FREQ aligns with Microsoft's enterprise AI strategy.

Any update on our application status?

Best,
Dre
Founder, FREQ""",

    "mfsin_linkedin_followup": """Hi {first_name},

I recently applied to Microsoft for Startups Founders Hub and noticed your role in the program.

FREQ is building governed AI agents on Azure - we've already integrated with Foundry, Databricks, and Digital Twins.

Would love to connect and learn more about the program. Any tips for applicants building enterprise AI on Azure?

Thanks,
Dre""",

    # === ACCELERATOR OUTREACH ===

    "accelerator_application_inquiry": """Hi {first_name},

Researching {accelerator_name}'s {batch_name} batch and had a quick question.

FREQ is building governed AI agents for enterprise - multi-agent orchestration with built-in compliance. Our first vertical is maritime logistics.

Would this be a good fit for {accelerator_name}'s focus on {focus_area}?

Appreciate any guidance on the application process.

Dre""",

    # === GENERIC TEMPLATES ===

    "thank_you_intro": """Hi {first_name},

Thanks so much for the intro to {introduced_to}! Really appreciate you making that connection.

I'll reach out to them this week with context on FREQ.

Let me know if there's ever anything I can do to return the favor.

Dre""",

    "congrats_message": """Hi {first_name},

Saw the news about {achievement} - congratulations! That's a huge milestone for {company}.

{personal_comment}

Keep crushing it!

Dre""",
}


def render_outreach_message(template_key: str, variables: Dict[str, Any]) -> str:
    """
    Render an outreach template with variables.

    Args:
        template_key: Key of the template to render
        variables: Dictionary of variable values

    Returns:
        Rendered message content
    """
    if template_key not in OUTREACH_TEMPLATES:
        raise ValueError(f"Unknown template: {template_key}")

    content = OUTREACH_TEMPLATES[template_key]

    # Replace variables
    for var_name, var_value in variables.items():
        placeholder = "{" + var_name + "}"
        content = content.replace(placeholder, str(var_value))

    return content


def get_template(key: str) -> str:
    """Get a template by key."""
    if key not in OUTREACH_TEMPLATES:
        raise ValueError(f"Unknown template: {key}")
    return OUTREACH_TEMPLATES[key]


def list_templates() -> Dict[str, str]:
    """List all available templates with their first line as description."""
    return {
        key: template.split('\n')[0][:50] + "..."
        for key, template in OUTREACH_TEMPLATES.items()
    }
