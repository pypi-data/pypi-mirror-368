from langgraph.graph import StateGraph, END

from codius.graph.graph_state import GraphState
from codius.graph.nodes.abort import abort
from codius.graph.nodes.apply_changes import apply_changes
from codius.graph.nodes.extract_building_blocks import extract_building_blocks
from codius.graph.nodes.extract_project_metadata import extract_project_metadata
from codius.graph.nodes.extract_relevant_sources import extract_relevant_sources
from codius.graph.nodes.generate_code import generate_code
from codius.graph.nodes.handle_intent_error import handle_intent_error
from codius.graph.nodes.handle_unclear_intent import handle_unclear_intent
from codius.graph.nodes.handle_unsupported_intent import handle_unsupported_intent
from codius.graph.nodes.plan_changes import plan_changes
from codius.graph.nodes.revise_intent import revise_intent
from codius.graph.routers.approval_router import route_by_user_approval
from codius.graph.nodes.distill_intent import distill_intent
from codius.graph.nodes.preview import preview
from codius.graph.routers.intent_router import route_by_intent
from codius.domain.model.session.session import Session
from codius.infrastructure.repository.session_repository import SessionRepository
from codius.infrastructure.services.project_metadata_service import ProjectMetadataService


class GraphService:
    def __init__(
        self,
        session_repository: SessionRepository,
        project_metadata_service: ProjectMetadataService
    ):
        self.session_repository = session_repository
        self.project_metadata_service = project_metadata_service

    def run_repl_cycle(self, session: Session, user_input: str) -> Session:

        # Clear memory for cycle
        session.clear_state_for_repl_cycle()

        # Clear on-disk files
        self.project_metadata_service.clear_generated_files(session.id)

        # Update state and history with user input
        session.state.user_input = user_input

        # Prepare LangGraph input
        graph_input = {
            "session_id": session.id,
            "user_input": session.state.user_input,
            "history": [m.__dict__ for m in session.history.recent()],
            "summary": session.state.summary,
            "project_metadata": session.state.project_metadata,
            "building_blocks": [bb.__dict__ for bb in session.state.building_blocks],
        }

        # Run LangGraph
        graph = self._build_graph()
        result = graph.invoke(graph_input, config={"recursion_limit": 1000})

        # Update session state
        session.update_with_graph_result(result)

        # Append assistant response to history
        assistant_message = session.state.final_output or "⚠️ No output from assistant."
        session.append_assistant_message(assistant_message)

        return session

    def _build_graph(self):
        graph = StateGraph(state_schema=GraphState)

        # Add nodes
        graph.add_node("DistillIntent", distill_intent)
        graph.add_node("HandleUnclearIntent", handle_unclear_intent)
        graph.add_node("HandleUnsupportedIntent", handle_unsupported_intent)
        graph.add_node("HandleIntentError", handle_intent_error)
        graph.add_node("ExtractProjectMetadata", extract_project_metadata)
        graph.add_node("ExtractBuildingBlocks", extract_building_blocks)
        graph.add_node("ExtractRelevantSources", extract_relevant_sources)
        graph.add_node("Plan", plan_changes)
        graph.add_node("ReviseIntent", revise_intent)
        graph.add_node("GenerateCode", generate_code)
        graph.add_node("Preview", preview)
        graph.add_node("ApplyChanges", apply_changes)
        graph.add_node("Abort", abort)

        # Routers
        graph.add_conditional_edges("DistillIntent", route_by_intent, {
            "valid": "ExtractProjectMetadata",
            "unclear": "HandleUnclearIntent",
            "error": "HandleIntentError",
            "unsupported": "HandleUnsupportedIntent",
        })
        graph.add_conditional_edges("Preview", route_by_user_approval, {
            "apply": "ApplyChanges",
            "abort": "Abort",
            "revise": "ReviseIntent"
        })

        # Graph flow
        graph.set_entry_point("DistillIntent")
        graph.add_edge("ExtractProjectMetadata", "ExtractBuildingBlocks")
        graph.add_edge("ExtractBuildingBlocks", "ExtractRelevantSources")
        graph.add_edge("ExtractRelevantSources", "Plan")
        graph.add_edge("Plan", "GenerateCode")
        graph.add_edge("GenerateCode", "Preview")
        graph.add_edge("ReviseIntent", "Plan")
        graph.add_edge("ApplyChanges", END)
        graph.add_edge("Abort", END)

        return graph.compile()
