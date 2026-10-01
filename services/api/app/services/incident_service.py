from typing import Dict, Any, List, Optional
import asyncio
import uuid
from datetime import datetime, timezone


from agents.crew import OrbitAgentCrew
from agents.state import IncidentState
from pipelines.pipeline_runner import PipelineRunner
from ..websocket_manager import ws_manager

try:
    from data_gen.generator import EnterpriseDataGenerator
    from data_gen.fault_injector import FaultType
    from data_gen.scenarios import get_scenario
except (ImportError, ModuleNotFoundError):
    import sys
    data_gen_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "data-gen")
    if data_gen_path not in sys.path:
        sys.path.insert(0, data_gen_path)
    from generator import EnterpriseDataGenerator
    from fault_injector import FaultType
    from scenarios import get_scenario




class IncidentService:
    """Manages active and historical incidents, approvals, and live telemetry dispatches."""

    def __init__(self):
        self.crew = OrbitAgentCrew()
        self.generator = EnterpriseDataGenerator(seed=42)
        self.runner = PipelineRunner()
        self.incidents: Dict[str, IncidentState] = {}
        self._init_default_incidents()

    def _init_default_incidents(self):
        """Seeds initial resolved incidents so the UI and history are populated on first launch."""
        demo_incident = self.crew.run_incident_resolution(
            pipeline_id="banking_transactions_pipeline",
            node_id="bronze_banking_transactions",
            fault_type="null_spike",
            severity="high",
            auto_approve_safe_fixes=True
        )
        self.incidents[demo_incident.incident_id] = demo_incident

    def list_incidents(self) -> List[Dict[str, Any]]:
        """Returns summary list of all recent incidents."""
        summaries = []
        for inc_id, state in sorted(self.incidents.items(), key=lambda x: x[1].incident_id, reverse=True):
            status = "resolved" if state.validation_passed else (
                "awaiting_approval" if any(s.decision == "AWAITING_HUMAN_APPROVAL" for s in state.trace_steps) else "investigating"
            )
            summaries.append({
                "incident_id": state.incident_id,
                "title": f"{state.fault_type.replace('_', ' ').title()} on {state.node_id}",
                "pipeline_id": state.pipeline_id,
                "node_id": state.node_id,
                "fault_type": state.fault_type,
                "severity": state.severity,
                "status": status,
                "requires_approval": status == "awaiting_approval",
                "validation_passed": state.validation_passed,
                "created_at": state.trace_steps[0].timestamp if state.trace_steps else datetime.now(timezone.utc).isoformat(),
                "resolved_at": state.trace_steps[-1].timestamp if state.validation_passed else None
            })
        return summaries

    def get_incident_trace(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """Returns detailed agent execution trace for scrubber replay."""
        state = self.incidents.get(incident_id)
        if not state:
            return None

        return {
            "incident_id": state.incident_id,
            "pipeline_id": state.pipeline_id,
            "node_id": state.node_id,
            "fault_type": state.fault_type,
            "severity": state.severity,
            "root_cause": state.root_cause,
            "proposed_fix": state.proposed_fix,
            "fix_applied": state.fix_applied,
            "validation_passed": state.validation_passed,
            "incident_report": state.incident_report,
            "steps": [step.model_dump() for step in state.trace_steps]
        }

    async def inject_chaos_and_resolve(
        self,
        domain: str,
        fault_type: str,
        severity: str = "high",
        target_field: Optional[str] = None,
        scenario_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        1. Injects data fault into pipeline.
        2. Broadcasts node pulse red.
        3. Runs multi-agent crew step by step with WebSocket emission.
        """
        node_map = {
            "banking": "bronze_banking_transactions",
            "retail": "bronze_retail_orders",
            "supply_chain": "bronze_supply_chain",
            "customer": "bronze_customer_events"
        }
        node_id = node_map.get(domain, "bronze_banking_transactions")

        # 1. Inject fault
        if scenario_id:
            scenario = get_scenario(scenario_id)
            if scenario:
                domain = scenario["domain"]
                node_id = node_map.get(domain, node_id)
                self.generator.execute_scenario(scenario_id)
        else:
            try:
                ft_enum = FaultType(fault_type)
            except Exception:
                ft_enum = FaultType.NULL_SPIKE
            self.generator.inject_chaos(domain=domain, fault_type=ft_enum, severity=severity, target_field=target_field)

        # 2. Broadcast node failure event over WebSocket
        await ws_manager.broadcast({
            "type": "node_health_update",
            "node_id": node_id,
            "status": "unhealthy",
            "health_score": 38.0,
            "fault_type": fault_type,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

        # 3. Create incident state
        incident_id = f"inc_{datetime.now(timezone.utc).strftime('%Y%m%d')}_{uuid.uuid4().hex[:6]}"
        state = IncidentState(
            incident_id=incident_id,
            pipeline_id=f"{domain}_pipeline",
            node_id=node_id,
            fault_type=fault_type,
            severity=severity,
            human_approved=True
        )

        # 4. Stream Sentinel step
        state = self.crew._step_sentinel(state)
        await self._broadcast_latest_step(state)
        await asyncio.sleep(0.4)

        # 5. Stream Diagnostician step
        state = self.crew._step_diagnostician(state)
        await self._broadcast_latest_step(state)
        await asyncio.sleep(0.4)

        # 6. Stream Surgeon step
        state = self.crew._step_surgeon(state)
        await self._broadcast_latest_step(state)
        await asyncio.sleep(0.4)

        # 7. Stream Auditor step
        state = self.crew._step_auditor(state)
        await self._broadcast_latest_step(state)
        await asyncio.sleep(0.4)

        # 8. Stream Scribe step
        state = self.crew._step_scribe(state)
        await self._broadcast_latest_step(state)
        await asyncio.sleep(0.3)

        # 9. Stream Strategist step
        state = self.crew._step_strategist(state)
        await self._broadcast_latest_step(state)

        # Save to store
        self.incidents[incident_id] = state

        # Broadcast healed node
        await ws_manager.broadcast({
            "type": "node_health_update",
            "node_id": node_id,
            "status": "healthy",
            "health_score": 99.5,
            "fault_type": None,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

        return {
            "status": "resolved",
            "incident_id": incident_id,
            "fault_type": fault_type,
            "domain": domain,
            "severity": severity,
            "impacted_node": node_id,
            "message": f"Autonomous crew successfully remediated {fault_type} on {node_id}.",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    async def approve_incident(self, incident_id: str, approved_by: str = "operator") -> Dict[str, Any]:
        """Approves a pending incident at the human-in-the-loop gate and triggers remediation."""
        state = self.incidents.get(incident_id)
        if not state:
            return {"status": "error", "message": "Incident not found"}

        state.human_approved = True
        state.trace_steps.append(AgentStep(
            agent_name="ApprovalGate",
            thought=f"Operator '{approved_by}' authorized remediation execution.",
            decision="HUMAN_APPROVAL_GRANTED",
            timestamp=datetime.now(timezone.utc).isoformat()
        ))
        await self._broadcast_latest_step(state)

        # Continue with Surgeon -> Auditor -> Scribe -> Strategist
        state = self.crew._step_surgeon(state)
        await self._broadcast_latest_step(state)
        state = self.crew._step_auditor(state)
        await self._broadcast_latest_step(state)
        state = self.crew._step_scribe(state)
        await self._broadcast_latest_step(state)
        state = self.crew._step_strategist(state)
        await self._broadcast_latest_step(state)

        self.incidents[incident_id] = state

        # Broadcast healed status
        await ws_manager.broadcast({
            "type": "node_health_update",
            "node_id": state.node_id,
            "status": "healthy",
            "health_score": 99.0,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

        return {
            "status": "approved_and_resolved",
            "incident_id": incident_id,
            "validation_passed": state.validation_passed
        }

    async def _broadcast_latest_step(self, state: IncidentState):
        """Broadcasts the latest agent step over WebSocket."""
        if not state.trace_steps:
            return
        last_step = state.trace_steps[-1]
        await ws_manager.broadcast({
            "type": "agent_thought",
            "incident_id": state.incident_id,
            "agent_name": last_step.agent_name,
            "thought": last_step.thought,
            "tool_call": last_step.tool_call,
            "decision": last_step.decision,
            "timestamp": last_step.timestamp
        })


incident_service = IncidentService()
