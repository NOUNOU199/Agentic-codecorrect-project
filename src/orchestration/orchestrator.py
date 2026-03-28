"""
FEATURE 2: Orchestration Logic
Implement the execution of the defined graph.
Call agents sequentially and handle iteration/stopping conditions.
"""

from typing import Dict, Any, Optional
from src.orchestration.execution_graph import ExecutionGraph, ExecutionState


class Orchestrator:
    """
    Executes the refactoring swarm workflow:
    Auditor → Fixer → Judge → (feedback loop or stop)
    
    Responsibilities:
    - Call agents in sequence
    - Handle judge feedback loop
    - Enforce max iterations constraint
    - Return execution results
    """
    
    def __init__(self, auditor, fixer, judge):
        """
        Initialize orchestrator with agent references.
        
        Args:
            auditor: AuditorAgent instance with execute(directory) method
            fixer: FixerAgent instance with execute(directory, audit_result) method
            judge: JudgeAgent instance with execute(directory) method
        """
        self.auditor = auditor
        self.fixer = fixer
        self.judge = judge
        self.graph = ExecutionGraph()
    
    def run(self, target_directory: str) -> Dict[str, Any]:
        """
        Execute the complete refactoring workflow.
        
        Args:
            target_directory: Directory containing code to refactor
            
        Returns:
            Execution result with status and history
        """
        self.graph.current_state = ExecutionState.INIT
        self.graph.iteration_count = 0
        
        # INIT → AUDIT: Get analysis plan
        self.graph.current_state = ExecutionState.AUDIT
        audit_result = self._run_audit(target_directory)
        if audit_result.get('status') != 'SUCCESS':
            return self._error_result('Audit failed', audit_result)
        self.graph.record_step(ExecutionState.AUDIT, audit_result)
        
        # Feedback loop: FIX → JUDGE → (continue or stop)
        while self.graph.can_continue():
            self.graph.increment_iteration()
            
            # FIX: Apply corrections
            self.graph.current_state = ExecutionState.FIX
            fix_result = self._run_fix(target_directory, audit_result)
            if fix_result.get('status') != 'SUCCESS':
                return self._error_result('Fix failed', fix_result)
            self.graph.record_step(ExecutionState.FIX, fix_result)
            
            # JUDGE: Validate refactoring
            self.graph.current_state = ExecutionState.JUDGE
            judge_result = self._run_judge(target_directory)
            self.graph.record_step(ExecutionState.JUDGE, judge_result)
            
            # Decide: continue loop or stop?
            judge_decision = judge_result.get('approved', False)
            
            if judge_decision:
                # SUCCESS: Tests pass, quality acceptable
                self.graph.current_state = ExecutionState.SUCCESS
                return self._success_result(judge_result)
            else:
                # RETRY: Need more fixes
                # Check if we hit max iterations
                if not self.graph.can_continue():
                    self.graph.current_state = ExecutionState.MAX_ITERATIONS
                    return self._max_iterations_result()
                
                # Otherwise loop continues (FIX again)
                continue
        
        # Should not reach here, but handle gracefully
        self.graph.current_state = ExecutionState.MAX_ITERATIONS
        return self._max_iterations_result()
    
    def _run_audit(self, target_directory: str) -> Dict[str, Any]:
        """Call AuditorAgent"""
        try:
            result = self.auditor.execute(directory=target_directory)
            return result if result else {'status': 'ERROR', 'message': 'Auditor returned None'}
        except Exception as e:
            return {'status': 'ERROR', 'message': f'Audit error: {str(e)}'}
    
    def _run_fix(self, target_directory: str, audit_result: Dict[str, Any]) -> Dict[str, Any]:
        """Call FixerAgent"""
        try:
            result = self.fixer.execute(directory=target_directory, audit_result=audit_result)
            return result if result else {'status': 'ERROR', 'message': 'Fixer returned None'}
        except Exception as e:
            return {'status': 'ERROR', 'message': f'Fix error: {str(e)}'}
    
    def _run_judge(self, target_directory: str) -> Dict[str, Any]:
        """Call JudgeAgent"""
        try:
            result = self.judge.execute(directory=target_directory)
            return result if result else {'status': 'ERROR', 'message': 'Judge returned None'}
        except Exception as e:
            return {'status': 'ERROR', 'message': f'Judge error: {str(e)}'}
    
    def _success_result(self, judge_result: Dict[str, Any]) -> Dict[str, Any]:
        """Format success result"""
        return {
            'status': 'SUCCESS',
            'state': ExecutionState.SUCCESS.value,
            'iterations': self.graph.iteration_count,
            'judge_result': judge_result,
            'history': self.graph.history
        }
    
    def _error_result(self, message: str, detail: Dict[str, Any]) -> Dict[str, Any]:
        """Format error result"""
        return {
            'status': 'ERROR',
            'state': ExecutionState.ERROR.value,
            'message': message,
            'detail': detail,
            'iterations': self.graph.iteration_count,
            'history': self.graph.history
        }
    
    def _max_iterations_result(self) -> Dict[str, Any]:
        """Format max iterations reached result"""
        return {
            'status': 'MAX_ITERATIONS',
            'state': ExecutionState.MAX_ITERATIONS.value,
            'iterations': self.graph.iteration_count,
            'max_allowed': ExecutionGraph.MAX_ITERATIONS,
            'history': self.graph.history
        }
