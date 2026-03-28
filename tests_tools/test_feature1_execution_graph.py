"""
Tests for Feature 1: Execution Graph Definition
"""

import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestration.execution_graph import ExecutionGraph, ExecutionState


class TestExecutionGraph:
    """Test execution graph state transitions"""
    
    def test_graph_initialization(self):
        """Test graph initializes in INIT state"""
        graph = ExecutionGraph()
        assert graph.current_state == ExecutionState.INIT
        assert graph.iteration_count == 0
    
    def test_graph_max_iterations(self):
        """Test MAX_ITERATIONS constraint"""
        graph = ExecutionGraph()
        assert graph.MAX_ITERATIONS == 10
    
    def test_state_transitions_init_to_audit(self):
        """Test INIT → AUDIT transition"""
        graph = ExecutionGraph()
        next_state = graph.get_next_state(ExecutionState.INIT)
        assert next_state == ExecutionState.AUDIT
    
    def test_state_transitions_audit_to_fix(self):
        """Test AUDIT → FIX transition"""
        graph = ExecutionGraph()
        next_state = graph.get_next_state(ExecutionState.AUDIT)
        assert next_state == ExecutionState.FIX
    
    def test_state_transitions_fix_to_judge(self):
        """Test FIX → JUDGE transition"""
        graph = ExecutionGraph()
        next_state = graph.get_next_state(ExecutionState.FIX)
        assert next_state == ExecutionState.JUDGE
    
    def test_judge_decision_success(self):
        """Test JUDGE → SUCCESS when approved"""
        graph = ExecutionGraph()
        next_state = graph.get_next_state(ExecutionState.JUDGE, judge_decision=True)
        assert next_state == ExecutionState.SUCCESS
    
    def test_judge_decision_retry(self):
        """Test JUDGE → FIX when rejected and iterations remaining"""
        graph = ExecutionGraph()
        graph.iteration_count = 1  # Not at max
        next_state = graph.get_next_state(ExecutionState.JUDGE, judge_decision=False)
        assert next_state == ExecutionState.FIX
    
    def test_judge_decision_max_iterations(self):
        """Test JUDGE → MAX_ITERATIONS when max reached"""
        graph = ExecutionGraph()
        graph.iteration_count = ExecutionGraph.MAX_ITERATIONS
        next_state = graph.get_next_state(ExecutionState.JUDGE, judge_decision=False)
        assert next_state == ExecutionState.MAX_ITERATIONS
    
    def test_can_continue(self):
        """Test can_continue respects max iterations"""
        graph = ExecutionGraph()
        assert graph.can_continue() is True
        
        graph.iteration_count = ExecutionGraph.MAX_ITERATIONS - 1
        assert graph.can_continue() is True
        
        graph.iteration_count = ExecutionGraph.MAX_ITERATIONS
        assert graph.can_continue() is False
    
    def test_iteration_increment(self):
        """Test iteration counter increments"""
        graph = ExecutionGraph()
        assert graph.iteration_count == 0
        graph.increment_iteration()
        assert graph.iteration_count == 1
    
    def test_record_step(self):
        """Test step recording"""
        graph = ExecutionGraph()
        graph.record_step(ExecutionState.AUDIT, {'result': 'test'})
        assert len(graph.history) == 1
        assert graph.history[0]['state'] == 'AUDIT'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
