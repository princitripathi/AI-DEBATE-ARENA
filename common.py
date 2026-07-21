"""
Shared utilities for AI Debate Arena.

This module contains common functions used by both the CLI and web API components.
"""


def get_expertise_by_persona(persona: str, side: str) -> str:
    """Get expertise for a given persona and side (pro/con)"""
    
    persona_expertise = {
        "economists": {
            "pro": "technology economist and AI researcher",
            "con": "labor economist and social policy expert"
        },
        "lawyers": {
            "pro": "human rights attorney and constitutional law expert",
            "con": "corporate law specialist and business attorney"
        },
        "scientists": {
            "pro": "climate scientist and environmental researcher",
            "con": "geneticist and biotechnology expert"
        },
        "philosophers": {
            "pro": "ethics professor and moral philosopher",
            "con": "political philosopher and social theorist"
        }
    }
    
    if persona in persona_expertise and side in persona_expertise[persona]:
        return persona_expertise[persona][side]
    
    return "expert" if side == "pro" else "expert"
