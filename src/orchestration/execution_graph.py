"""
FEATURE 1: Execution Graph Definition
Define the refactoring execution flow: Auditor → Fixer → Judge
with feedback loop (Judge failure → Fixer retry, Judge success → stop)
Maximum 10 iterations constraint.
"""

from enum import Enum
from typing import Dict, Any, List


class ExecutionState(Enum):
    """States in the execution graph"""
    INIT = "INIT"
    AUDIT = "AUDIT"
    FIX = "FIX"
    JUDGE = "JUDGE"
    SUCCESS = "SUCCESS"
    MAX_ITERATIONS = "MAX_ITERATIONS"
    ERROR = "ERROR"


class ExecutionGraph:
    """
    Defines the execution flow:
    
    INIT → AUDIT → FIX → JUDGE
              ↑               ↓
              +--- (retry) ---+
    
    Constraints:
    - Maximum 10 iterations
    - Judge decides: success → stop, failure → retry to FIX
    """
    
    MAX_ITERATIONS = 10
    
    def __init__(self):
        self.current_state = ExecutionState.INIT
        self.iteration_count = 0
        self.history: List[Dict[str, Any]] = []
    
    def get_next_state(self, current_state: ExecutionState, judge_decision: bool = None) -> ExecutionState:
        """
        Determine next state based on current state and judge decision.
        
        Args:
            current_state: Current execution state
            judge_decision: True if judge approves, False if needs retry
            
        Returns:
            Next state in the graph
        """
        if current_state == ExecutionState.INIT:
            return ExecutionState.AUDIT
        
        elif current_state == ExecutionState.AUDIT:
            return ExecutionState.FIX
        
        elif current_state == ExecutionState.FIX:
            return ExecutionState.JUDGE
        
        elif current_state == ExecutionState.JUDGE:
            # Judge decision determines next path
            if judge_decision is True:
                return ExecutionState.SUCCESS
            elif judge_decision is False:
                # Check iteration limit before retrying
                if self.iteration_count < self.MAX_ITERATIONS:
                    return ExecutionState.FIX
                else:
                    return ExecutionState.MAX_ITERATIONS
            else:
                return ExecutionState.ERROR
        
        return ExecutionState.ERROR
    
    def record_step(self, state: ExecutionState, result: Dict[str, Any]):
        """Record execution step in history"""
        self.history.append({
            'iteration': self.iteration_count,
            'state': state.value,
            'result': result
        })
    
    def can_continue(self) -> bool:
        """Check if execution can continue (respects max iterations)"""
        return self.iteration_count < self.MAX_ITERATIONS
    
    def increment_iteration(self):
        """Increment iteration counter"""
        self.iteration_count += 1
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of execution graph traversal"""
        return {
            'total_iterations': self.iteration_count,
            'max_allowed_iterations': self.MAX_ITERATIONS,
            'max_reached': self.iteration_count >= self.MAX_ITERATIONS,
            'steps': self.history
        }
