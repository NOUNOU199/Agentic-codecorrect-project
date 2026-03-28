"""
Tests for Feature 2: Orchestration Logic
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestration.orchestrator import Orchestrator


class TestOrchestrator:
    """Test orchestration logic"""
    
    def test_orchestrator_initialization(self):
        """Test orchestrator initializes with agents"""
        auditor = Mock()
        fixer = Mock()
        judge = Mock()
        
        orchestrator = Orchestrator(auditor, fixer, judge)
        
        assert orchestrator.auditor is auditor
        assert orchestrator.fixer is fixer
        assert orchestrator.judge is judge
        assert orchestrator.graph is not None
    
    def test_orchestrator_run_success_path(self):
        """Test successful refactoring workflow"""
        # Mock agents
        auditor = Mock()
        auditor.execute.return_value = {'status': 'SUCCESS', 'issues': []}
        
        fixer = Mock()
        fixer.execute.return_value = {'status': 'SUCCESS', 'fixes': 1}
        
        judge = Mock()
        judge.execute.return_value = {'status': 'SUCCESS', 'approved': True}
        
        orchestrator = Orchestrator(auditor, fixer, judge)
        result = orchestrator.run(target_directory='sandbox/')
        
        assert result['status'] == 'SUCCESS'
        assert result['iterations'] > 0
    
    def test_orchestrator_audit_failure(self):
        """Test handling of audit failure"""
        auditor = Mock()
        auditor.execute.return_value = {'status': 'ERROR', 'message': 'Audit failed'}
        
        fixer = Mock()
        judge = Mock()
        
        orchestrator = Orchestrator(auditor, fixer, judge)
        result = orchestrator.run(target_directory='sandbox/')
        
        assert result['status'] == 'ERROR'
        assert 'Audit failed' in result.get('message', '')
    
    def test_orchestrator_iteration_limit(self):
        """Test orchestrator respects max iterations"""
        auditor = Mock()
        auditor.execute.return_value = {'status': 'SUCCESS'}
        
        fixer = Mock()
        fixer.execute.return_value = {'status': 'SUCCESS'}
        
        judge = Mock()
        judge.execute.return_value = {'status': 'SUCCESS', 'approved': False}  # Always reject
        
        orchestrator = Orchestrator(auditor, fixer, judge)
        result = orchestrator.run(target_directory='sandbox/')
        
        # Should reach max iterations
        assert result['iterations'] <= orchestrator.graph.MAX_ITERATIONS


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
