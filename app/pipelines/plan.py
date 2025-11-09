"""
PLAN mode - for complex stuff that needs to be broken down
Thinks step-by-step and figures out what's missing
"""

from app.llm import llm_client


PLAN_SYSTEM_PROMPT = """You are a planning assistant. When given a complex task or goal:

1. Break it down into clear, actionable steps
2. Identify what information you need but don't have
3. Suggest next actions or questions to gather missing information
4. Be specific and practical

Format your response as:

PLAN:
1. [First step]
2. [Second step]
...

MISSING INFORMATION:
- [What you need to know]
- [Other information needed]

NEXT ACTIONS:
- [Suggested next steps]
"""


def handle_plan(query: str) -> dict:
    """
    Breaks down complex goals into actionable steps.
    Also figures out what info we're missing to make a better plan.
    """
    response = llm_client.generate(
        prompt=query,
        system_prompt=PLAN_SYSTEM_PROMPT,
        temperature=0.7,
        max_tokens=1500  # Plans can be long, so give it more room
    )
    
    # Try to parse the response into structured sections
    # (This is a bit fragile but works most of the time)
    plan_steps = []
    missing_info = []
    next_actions = []
    
    current_section = None
    
    for line in response.split('\n'):
        line = line.strip()
        
        if not line:
            continue
        
        if line.upper().startswith('PLAN'):
            current_section = 'plan'
        elif 'MISSING INFORMATION' in line.upper():
            current_section = 'missing'
        elif 'NEXT ACTIONS' in line.upper() or 'NEXT STEPS' in line.upper():
            current_section = 'actions'
        elif current_section == 'plan' and (line[0].isdigit() or line.startswith('-')):
            plan_steps.append(line.lstrip('0123456789.-) '))
        elif current_section == 'missing' and line.startswith('-'):
            missing_info.append(line.lstrip('- '))
        elif current_section == 'actions' and line.startswith('-'):
            next_actions.append(line.lstrip('- '))
    
    return {
        "mode": "PLAN",
        "answer": response,
        "plan": {
            "steps": plan_steps if plan_steps else ["See full plan in answer"],
            "missing_information": missing_info if missing_info else ["None identified"],
            "next_actions": next_actions if next_actions else ["Execute the plan"]
        },
        "metadata": {
            "tool_used": "planning"
        }
    }

