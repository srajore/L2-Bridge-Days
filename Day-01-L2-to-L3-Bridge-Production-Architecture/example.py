"""Day 01: check the SupportDesk spec (L2 prototype vs Day 19 target architecture) against a production checklist and print gap reports."""

from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class GapState(TypedDict):
    spec: dict
    gaps: list
    report: str


# 1. The L2-style SupportDesk prototype: it answers questions on a laptop, but says almost nothing about production.
L2_PROTOTYPE = {
    "name": "SupportDesk (L2 prototype)",
    "nfr": {"latency_budget_ms": None, "token_budget": None, "mcp_timeout_s": None, "max_tool_calls": None,
            "availability_pct": None, "cost_per_request_usd": None},
    "api_boundary": {"endpoint": None, "auth": None, "request_schema": None, "max_request_chars": None, "rate_limit_per_min": None},
    "trust_boundaries": {"user_input_validated": False, "model_output_validated": False, "tool_allowlist": []},
    "state": {"checkpoint_store": "memory", "thread_id_source": None, "retention_days": None},
    "failure_domains": {"mcp_server": {"timeout_s": None, "fallback": None},
                        "model_api": {"timeout_s": None, "fallback": None}},
    "risks": {"model outage": None, "prompt injection": None, "freeze_card without approval": None,
              "duplicate freeze_card": None, "card number in answer": None},
}

# 2. The production target = the Day 19 architecture (same names). The nfr numbers are Day 19's NFR dict.
PRODUCTION_TARGET = {
    "name": "SupportDesk (production target = Day 19 architecture)",
    "nfr": {"latency_budget_ms": 30000, "token_budget": 200, "mcp_timeout_s": 30, "max_tool_calls": 1,
            "availability_pct": 99.5, "cost_per_request_usd": 0.02},
    "api_boundary": {"endpoint": "POST /ask (+ GET /health, /ready, /version)", "auth": "x-api-key header, fail closed",
                     "request_schema": "AskRequest (pydantic)", "max_request_chars": 500, "rate_limit_per_min": 30},
    "trust_boundaries": {"user_input_validated": True, "model_output_validated": True,
                         "tool_allowlist": ["lookup_balance"]},  # ROLE_TOOLS["support_agent"]; freeze_card needs a human
    "state": {"checkpoint_store": "sqlite", "thread_id_source": "server-side: user + cid, never the request body", "retention_days": 30},
    "failure_domains": {"mcp_server": {"timeout_s": 30, "fallback": "Service busy, please try again later."},
                        "model_api": {"timeout_s": 20, "fallback": "canned answer from retrieved context"}},
    "risks": {"model outage": "timeout + fallback answer", "prompt injection": "INJECTION regex in guard_input + ROLE_TOOLS",
              "freeze_card without approval": "TOOL_POLICY needs_human=True, check_policy denies",
              "duplicate freeze_card": "idempotency key per card", "card number in answer": "redact() in guard_output"},
}


def check_nfrs(state):
    gaps = []
    for key, value in state["spec"]["nfr"].items():
        if not isinstance(value, (int, float)) or value <= 0:  # an NFR must be a measurable number
            gaps.append("NFR: '" + key + "' is not a positive number")
    return {"gaps": state["gaps"] + gaps}


def check_api_boundary(state):
    gaps = []
    for key, value in state["spec"]["api_boundary"].items():
        if value is None:
            gaps.append("API: '" + key + "' is not defined")
    return {"gaps": state["gaps"] + gaps}


def check_trust_boundaries(state):
    gaps = []
    boundaries = state["spec"]["trust_boundaries"]
    if not boundaries["user_input_validated"]:
        gaps.append("TRUST: user input crosses into the agent without validation")
    if not boundaries["model_output_validated"]:
        gaps.append("TRUST: model output reaches tools or users without validation")
    if not boundaries["tool_allowlist"]:
        gaps.append("TRUST: no tool allowlist")
    return {"gaps": state["gaps"] + gaps}


def check_state_architecture(state):
    gaps = []
    memory = state["spec"]["state"]
    if memory["checkpoint_store"] == "memory":
        gaps.append("STATE: checkpoints live in memory and are lost on restart")
    if memory["thread_id_source"] is None:
        gaps.append("STATE: nobody decides where thread_id comes from (users could read each other's threads)")
    if memory["retention_days"] is None:
        gaps.append("STATE: no retention period for saved state")
    return {"gaps": state["gaps"] + gaps}


def check_failure_domains(state):
    gaps = []
    for domain, rules in state["spec"]["failure_domains"].items():
        if rules["timeout_s"] is None:
            gaps.append("FAILURE: " + domain + " call has no timeout")
        if rules["fallback"] is None:
            gaps.append("FAILURE: " + domain + " has no fallback")
    return {"gaps": state["gaps"] + gaps}


def check_risk_register(state):
    gaps = []
    for risk, mitigation in state["spec"]["risks"].items():
        if mitigation is None:
            gaps.append("RISK: '" + risk + "' has no mitigation")
    return {"gaps": state["gaps"] + gaps}


def write_report(state):
    lines = ["Gap report for " + state["spec"]["name"], "Gaps found: " + str(len(state["gaps"]))]
    for number, gap in enumerate(state["gaps"], start=1):
        lines.append(str(number) + ". " + gap)
    verdict = "NOT READY for production" if state["gaps"] else "READY for review"
    lines.append("Verdict: " + verdict)
    return {"report": "\n".join(lines)}


graph = StateGraph(GapState)
checks = [("check_nfrs", check_nfrs), ("check_api_boundary", check_api_boundary),
          ("check_trust_boundaries", check_trust_boundaries), ("check_state_architecture", check_state_architecture),
          ("check_failure_domains", check_failure_domains), ("check_risk_register", check_risk_register),
          ("write_report", write_report)]
for node_name, node_fn in checks:
    graph.add_node(node_name, node_fn)
graph.add_edge(START, "check_nfrs")
graph.add_edge("check_nfrs", "check_api_boundary")
graph.add_edge("check_api_boundary", "check_trust_boundaries")
graph.add_edge("check_trust_boundaries", "check_state_architecture")
graph.add_edge("check_state_architecture", "check_failure_domains")
graph.add_edge("check_failure_domains", "check_risk_register")
graph.add_edge("check_risk_register", "write_report")
graph.add_edge("write_report", END)
app = graph.compile()

for spec in (L2_PROTOTYPE, PRODUCTION_TARGET):
    print(app.invoke({"spec": spec, "gaps": [], "report": ""})["report"])
    print()
