import os
from typing import TypedDict, Optional, List
from langgraph.graph import StateGraph, END
from google import genai
from agents.prompts import SPATIAL_RESOLVER_PROMPT, CONTEXT_ENRICHER_PROMPT
from agents.tools import (
    advanced_geocoding_tool,
    cross_source_news_search,
    spatial_density_analyzer
)


class AgentState(TypedDict):
    source: str
    raw_text: str
    published_date: str
    verbal_location: str
    accident_severity: str
    vehicle_types: List[str]
    latitude: Optional[float]
    longitude: Optional[float]
    retries: int
    agent_status: str
    risk_level: str
    suspected_infrastructure_hazard: bool


def spatial_resolver_node(state: AgentState) -> AgentState:
    """מנסה לפענח מיקום מדויק בעזרת ניקוי סמנטי של הטקסט וכלי הגיאוקודינג."""
    gemini = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    prompt = f"{SPATIAL_RESOLVER_PROMPT}\n\nRaw report: {state['raw_text']}\nCurrent location: {state['verbal_location']}"
    resp = gemini.models.generate_content(model="gemini-3.8-flash", contents=prompt)
    refined_loc = resp.text.strip()

    if "UNRESOLVABLE_HIGHWAY" in refined_loc:
        return {**state, "retries": 3, "agent_status": "REQUIRES_MANUAL_REVIEW"}

    geo_res = advanced_geocoding_tool.invoke({"cleaned_location": refined_loc})
    if geo_res["latitude"] is not None:
        return {
            **state,
            "verbal_location": refined_loc,
            "latitude": geo_res["latitude"],
            "longitude": geo_res["longitude"],
            "agent_status": "VERIFIED"
        }

    return {
        **state,
        "verbal_location": refined_loc,
        "retries": state.get("retries", 0) + 1
    }


def context_enricher_node(state: AgentState) -> AgentState:
    """משלים חומרת פציעה חסרה מתוך כתבות עומק מאותו יום ומיקום."""
    if state.get("accident_severity") != "not specified":
        return state

    date_only = state["published_date"][:10]
    related = cross_source_news_search.invoke({
        "location_keyword": state["verbal_location"].split(",")[0],
        "target_date": date_only
    })
    if not related:
        return state

    gemini = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    prompt = f"{CONTEXT_ENRICHER_PROMPT}\n\nInitial: {state['raw_text']}\nFollow-ups: {related}\nReturn ONLY one word: light, moderate, severe, fatal, or not specified."
    resp = gemini.models.generate_content(model="gemini-3.8-flash", contents=prompt)
    new_sev = resp.text.strip().lower()

    if new_sev in {"light", "moderate", "severe", "fatal"}:
        return {**state, "accident_severity": new_sev}
    return state


def spatial_cluster_node(state: AgentState) -> AgentState:
    """מחשב אנומליה מרחבית (רדיוס 500 מ' / 90 יום) ומדליק דגל סיכון."""
    cluster_info = spatial_density_analyzer.invoke({
        "lat": state.get("latitude"),
        "lon": state.get("longitude"),
        "published_date": state["published_date"]
    })
    return {
        **state,
        "risk_level": cluster_info["risk_level"],
        "suspected_infrastructure_hazard": cluster_info["suspected_infrastructure_hazard"]
    }


def fallback_node(state: AgentState) -> AgentState:
    """מעקה בטיחות דטרמיניסטי: מונע קריסה ומעביר לבדיקת אנליסט."""
    return {
        **state,
        "latitude": None,
        "longitude": None,
        "agent_status": "REQUIRES_MANUAL_REVIEW",
        "risk_level": "UNKNOWN",
        "suspected_infrastructure_hazard": False
    }


def route_after_spatial(state: AgentState) -> str:
    if state.get("latitude") is not None:
        return "context_enricher"
    if state.get("retries", 0) >= 3:
        return "fallback"
    return "spatial_resolver"


def build_agent_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("spatial_resolver", spatial_resolver_node)
    workflow.add_node("context_enricher", context_enricher_node)
    workflow.add_node("spatial_cluster", spatial_cluster_node)
    workflow.add_node("fallback", fallback_node)

    workflow.set_entry_point("spatial_resolver")
    workflow.add_conditional_edges(
        "spatial_resolver",
        route_after_spatial,
        {
            "spatial_resolver": "spatial_resolver",
            "context_enricher": "context_enricher",
            "fallback": "fallback"
        }
    )
    workflow.add_edge("context_enricher", "spatial_cluster")
    workflow.add_edge("spatial_cluster", END)
    workflow.add_edge("fallback", END)

    return workflow.compile()
