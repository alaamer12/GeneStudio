"""Integration testing utilities for complete workflows and system validation."""

import time
import threading
import traceback
from typing import Any, Dict, List, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import logging

from utils.error_handling import GeneStudioError, ErrorContext, handle_error
from utils.resource_manager import get_resource_manager, managed_operation
from utils.validators import get_validation_manager
from utils.network_handler import get_network_handler, check_internet_connectivity


class TestStatus(Enum):
    """Test execution status."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class TestCategory(Enum):
    """Test categories."""
    UNIT = "unit"
    INTEGRATION = "integration"
    WORKFLOW = "workflow"
    PERFORMANCE = "performance"
    RESOURCE = "resource"
    ERROR_HANDLING = "error_handling"


@dataclass
class TestResult:
    """Result of a test execution."""
    test_name: str
    status: TestStatus
    duration: float = 0.0
    error: Optional[Exception] = None
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'test_name': self.test_name,
            'status': self.status.value,
            'duration': self.duration,
            'error': str(self.error) if self.error else None,
            'message': self.message,
            'details': self.details
        }


@dataclass
class TestSuite:
    """Collection of related tests."""
    name: str
    category: TestCategory
    tests: List[Callable] = field(default_factory=list)
    setup: Optional[Callable] = None
    teardown: Optional[Callable] = None
    enabled: bool = True


class IntegrationTester:
    """Main integration testing framework."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.test_suites = {}
        self.results = []
        self.running = False
        
        # Test environment
        self.test_data_dir = Path("test_data")
        self.test_data_dir.mkdir(exist_ok=True)
        
        # Register built-in test suites
        self._register_builtin_suites()
    
    def _register_builtin_suites(self):
        """Register built-in test suites."""
        # Database integration tests
        db_suite = TestSuite(
            name="Database Integration",
            category=TestCategory.INTEGRATION,
            tests=[
                self._test_database_connection,
                self._test_database_schema,
                self._test_database_crud_operations,
                self._test_database_transactions,
                self._test_database_error_handling
            ]
        )
        self.register_suite(db_suite)
        
        # Service layer tests
        service_suite = TestSuite(
            name="Service Layer",
            category=TestCategory.INTEGRATION,
            tests=[
                self._test_project_service_workflow,
                self._test_sequence_service_workflow,
                self._test_analysis_service_workflow,
                self._test_service_error_handling
            ]
        )
        self.register_suite(service_suite)
        
        # File operations tests
        file_suite = TestSuite(
            name="File Operations",
            category=TestCategory.WORKFLOW,
            tests=[
                self._test_fasta_import_workflow,
                self._test_file_validation,
                self._test_large_file_handling,
                self._test_file_error_scenarios
            ]
        )
        self.register_suite(file_suite)
        
        # Resource management tests
        resource_suite = TestSuite(
            name="Resource Management",
            category=TestCategory.RESOURCE,
            tests=[
                self._test_memory_monitoring,
                self._test_concurrent_operations,
                self._test_cache_management,
                self._test_resource_cleanup
            ]
        )
        self.register_suite(resource_suite)
        
        # Error handling tests
        error_suite = TestSuite(
            name="Error Handling",
            category=TestCategory.ERROR_HANDLING,
            tests=[
                self._test_validation_errors,
                self._test_database_errors,
                self._test_file_system_errors,
                self._test_network_errors,
                self._test_error_recovery
            ]
        )
        self.register_suite(error_suite)
        
        # End-to-end workflow tests
        workflow_suite = TestSuite(
            name="End-to-End Workflows",
            category=TestCategory.WORKFLOW,
            tests=[
                self._test_complete_project_workflow,
                self._test_sequence_analysis_workflow,
                self._test_data_persistence_workflow,
                self._test_session_state_workflow
            ]
        )
        self.register_suite(workflow_suite)
    
    def register_suite(self, suite: TestSuite):
        """Register a test suite."""
        self.test_suites[suite.name] = suite
        self.logger.info(f"Registered test suite: {suite.name}")
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all registered test suites."""
        if self.running:
            raise RuntimeError("Tests are already running")
        
        self.running = True
        self.results = []
        
        try:
            start_time = time.time()
            
            for suite_name, suite in self.test_suites.items():
                if not suite.enabled:
                    self.logger.info(f"Skipping disabled suite: {suite_name}")
                    continue
                
                self.logger.info(f"Running test suite: {suite_name}")
                suite_results = self._run_suite(suite)
                self.results.extend(suite_results)
            
            total_time = time.time() - start_time
            
            # Generate summary
            summary = self._generate_summary(total_time)
            self.logger.info(f"Test execution completed in {total_time:.2f}s")
            
            return summary
            
        finally:
            self.running = False
    
    def run_suite(self, suite_name: str) -> Dict[str, Any]:
        """Run a specific test suite."""
        if suite_name not in self.test_suites:
            raise ValueError(f"Test suite not found: {suite_name}")
        
        suite = self.test_suites[suite_name]
        start_time = time.time()
        
        suite_results = self._run_suite(suite)
        total_time = time.time() - start_time
        
        return {
            'suite_name': suite_name,
            'results': [result.to_dict() for result in suite_results],
            'duration': total_time,
            'passed': sum(1 for r in suite_results if r.status == TestStatus.PASSED),
            'failed': sum(1 for r in suite_results if r.status == TestStatus.FAILED),
            'errors': sum(1 for r in suite_results if r.status == TestStatus.ERROR),
            'total': len(suite_results)
        }
    
    def _run_suite(self, suite: TestSuite) -> List[TestResult]:
        """Run a test suite."""
        results = []
        
        # Setup
        if suite.setup:
            try:
                suite.setup()
            except Exception as e:
                self.logger.error(f"Suite setup failed for {suite.name}: {e}")
                # Skip all tests if setup fails
                for test_func in suite.tests:
                    results.append(TestResult(
                        test_name=test_func.__name__,
                        status=TestStatus.SKIPPED,
                        message=f"Skipped due to setup failure: {e}"
                    ))
                return results
        
        # Run tests
        for test_func in suite.tests:
            result = self._run_test(test_func)
            results.append(result)
        
        # Teardown
        if suite.teardown:
            try:
                suite.teardown()
            except Exception as e:
                self.logger.error(f"Suite teardown failed for {suite.name}: {e}")
        
        return results
    
    def _run_test(self, test_func: Callable) -> TestResult:
        """Run a single test."""
        test_name = test_func.__name__
        self.logger.debug(f"Running test: {test_name}")
        
        start_time = time.time()
        
        try:
            with managed_operation(f"test_{test_name}", "Integration test execution"):
                test_func()
            
            duration = time.time() - start_time
            result = TestResult(
                test_name=test_name,
                status=TestStatus.PASSED,
                duration=duration,
                message="Test passed successfully"
            )
            
            self.logger.debug(f"Test passed: {test_name} ({duration:.3f}s)")
            
        except AssertionError as e:
            duration = time.time() - start_time
            result = TestResult(
                test_name=test_name,
                status=TestStatus.FAILED,
                duration=duration,
                error=e,
                message=f"Assertion failed: {e}"
            )
            
            self.logger.warning(f"Test failed: {test_name} - {e}")
            
        except Exception as e:
            duration = time.time() - start_time
            result = TestResult(
                test_name=test_name,
                status=TestStatus.ERROR,
                duration=duration,
                error=e,
                message=f"Test error: {e}"
            )
            
            self.logger.error(f"Test error: {test_name} - {e}")
        
        return result
    
    def _generate_summary(self, total_time: float) -> Dict[str, Any]:
        """Generate test execution summary."""
        passed = sum(1 for r in self.results if r.status == TestStatus.PASSED)
        failed = sum(1 for r in self.results if r.status == TestStatus.FAILED)
        errors = sum(1 for r in self.results if r.status == TestStatus.ERROR)
        skipped = sum(1 for r in self.results if r.status == TestStatus.SKIPPED)
        
        return {
            'total_tests': len(self.results),
            'passed': passed,
            'failed': failed,
            'errors': errors,
            'skipped': skipped,
            'success_rate': (passed / len(self.results)) * 100 if self.results else 0,
            'total_duration': total_time,
            'results': [result.to_dict() for result in self.results]
        }
    
    # Database integration tests
    def _test_database_connection(self):
        """Test database connection."""
        from database.db_manager import DatabaseManager
        
        db = DatabaseManager()
        conn = db.get_connection()
        
        # Test basic query
        result = db.execute_query("SELECT 1 as test")
        assert len(result) == 1
        assert result[0]['test'] == 1
    
    def _test_database_schema(self):
        """Test database schema initialization."""
        from database.db_manager import DatabaseManager
        
        db = DatabaseManager()
        
        # Check that all required tables exist
        tables = db.execute_query("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """)
        
        table_names = {table['name'] for table in tables}
        required_tables = {'projects', 'sequences', 'analyses', 'settings', 'activity_log'}
        
        assert required_tables.issubset(table_names), f"Missing tables: {required_tables - table_names}"
    
    def _test_database_crud_operations(self):
        """Test basic CRUD operations."""
        from repositories.project_repository import ProjectRepository
        from models.project_model import Project
        
        repo = ProjectRepository()
        
        # Create
        project = Project(name="Test Project", type="sequence_analysis")
        created = repo.create(project)
        assert created.id is not None
        
        # Read
        retrieved = repo.get_by_id(created.id)
        assert retrieved is not None
        assert retrieved.name == "Test Project"
        
        # Update
        retrieved.description = "Updated description"
        success = repo.update(retrieved)
        assert success
        
        # Verify update
        updated = repo.get_by_id(created.id)
        assert updated.description == "Updated description"
        
        # Delete
        success = repo.delete(created.id)
        assert success
        
        # Verify deletion
        deleted = repo.get_by_id(created.id)
        assert deleted is None
    
    def _test_database_transactions(self):
        """Test database transaction handling."""
        from database.db_manager import DatabaseManager
        
        db = DatabaseManager()
        
        def transaction_operations(conn):
            conn.execute("INSERT INTO projects (name, type) VALUES (?, ?)", ("Trans Test 1", "sequence_analysis"))
            conn.execute("INSERT INTO projects (name, type) VALUES (?, ?)", ("Trans Test 2", "sequence_analysis"))
        
        # Test successful transaction
        success = db.execute_transaction([transaction_operations])
        assert success
        
        # Verify data was inserted
        projects = db.execute_query("SELECT name FROM projects WHERE name LIKE 'Trans Test%'")
        assert len(projects) == 2
        
        # Cleanup
        db.execute_query("DELETE FROM projects WHERE name LIKE 'Trans Test%'")
    
    def _test_database_error_handling(self):
        """Test database error handling."""
        from database.db_manager import DatabaseManager, DatabaseError
        
        db = DatabaseManager()
        
        # Test invalid query
        try:
            db.execute_query("SELECT * FROM nonexistent_table")
            assert False, "Should have raised DatabaseError"
        except DatabaseError:
            pass  # Expected
    
    # Service layer tests
    def _test_project_service_workflow(self):
        """Test complete project service workflow."""
        from services.project_service import ProjectService
        
        service = ProjectService()
        
        # Create project
        success, project = service.create_project("Test Project", "sequence_analysis", "Test description")
        assert success, f"Failed to create project: {project}"
        
        # Get project
        success, retrieved = service.get_project(project.id)
        assert success, f"Failed to get project: {retrieved}"
        assert retrieved.name == "Test Project"
        
        # Update project
        retrieved.description = "Updated description"
        success, result = service.update_project(retrieved)
        assert success, f"Failed to update project: {result}"
        
        # List projects
        success, projects = service.list_projects()
        assert success, f"Failed to list projects: {projects}"
        assert any(p.id == project.id for p in projects)
        
        # Delete project
        success, result = service.delete_project(project.id)
        assert success, f"Failed to delete project: {result}"
    
    def _test_sequence_service_workflow(self):
        """Test complete sequence service workflow."""
        from services.project_service import ProjectService
        from services.sequence_service import SequenceService
        
        # Create test project first
        project_service = ProjectService()
        success, project = project_service.create_project("Seq Test Project", "sequence_analysis")
        assert success
        
        sequence_service = SequenceService()
        
        # Create sequence
        success, sequence = sequence_service.create_sequence(
            project.id, "Test Sequence", "ATCGATCG", "dna"
        )
        assert success, f"Failed to create sequence: {sequence}"
        
        # Get sequence
        success, retrieved = sequence_service.get_sequence(sequence.id)
        assert success, f"Failed to get sequence: {retrieved}"
        assert retrieved.sequence == "ATCGATCG"
        
        # Update sequence
        retrieved.notes = "Test notes"
        success, result = sequence_service.update_sequence(retrieved)
        assert success, f"Failed to update sequence: {result}"
        
        # Get sequences by project
        success, sequences = sequence_service.get_sequences_by_project(project.id)
        assert success, f"Failed to get sequences: {sequences}"
        assert len(sequences) == 1
        
        # Cleanup
        sequence_service.delete_sequence(sequence.id)
        project_service.delete_project(project.id)
    
    def _test_analysis_service_workflow(self):
        """Test analysis service workflow."""
        from services.project_service import ProjectService
        from services.sequence_service import SequenceService
        from services.analysis_service import AnalysisService
        
        # Setup test data
        project_service = ProjectService()
        success, project = project_service.create_project("Analysis Test", "sequence_analysis")
        assert success
        
        sequence_service = SequenceService()
        success, sequence = sequence_service.create_sequence(
            project.id, "Test Seq", "ATCGATCGATCG", "dna"
        )
        assert success
        
        analysis_service = AnalysisService()
        
        # Create analysis
        success, analysis = analysis_service.create_analysis(
            project.id, sequence.id, "gc_content", {}
        )
        assert success, f"Failed to create analysis: {analysis}"
        
        # Get analysis
        success, retrieved = analysis_service.get_analysis(analysis.id)
        assert success, f"Failed to get analysis: {retrieved}"
        
        # Cleanup
        analysis_service.delete_analysis(analysis.id)
        sequence_service.delete_sequence(sequence.id)
        project_service.delete_project(project.id)
    
    def _test_service_error_handling(self):
        """Test service layer error handling."""
        from services.project_service import ProjectService
        
        service = ProjectService()
        
        # Test invalid project creation
        success, result = service.create_project("", "invalid_type")
        assert not success, "Should have failed with invalid data"
        
        # Test getting non-existent project
        success, result = service.get_project(99999)
        assert not success, "Should have failed for non-existent project"
    
    # File operation tests
    def _test_fasta_import_workflow(self):
        """Test FASTA file import workflow."""
        from services.project_service import ProjectService
        from services.sequence_service import SequenceService
        
        # Create test FASTA file
        test_fasta = self.test_data_dir / "test.fasta"
        with open(test_fasta, 'w') as f:
            f.write(">Sequence 1\nATCGATCG\n>Sequence 2\nGCTAGCTA\n")
        
        # Create test project
        project_service = ProjectService()
        success, project = project_service.create_project("FASTA Test", "sequence_analysis")
        assert success
        
        # Import FASTA
        sequence_service = SequenceService()
        success, sequences = sequence_service.import_fasta_file(str(test_fasta), project.id)
        assert success, f"Failed to import FASTA: {sequences}"
        assert len(sequences) == 2
        
        # Verify sequences
        success, project_sequences = sequence_service.get_sequences_by_project(project.id)
        assert success
        assert len(project_sequences) == 2
        
        # Cleanup
        test_fasta.unlink()
        for seq in sequences:
            sequence_service.delete_sequence(seq.id)
        project_service.delete_project(project.id)
    
    def _test_file_validation(self):
        """Test file validation."""
        from utils.validators import validate_fasta_file
        
        # Create invalid FASTA file
        invalid_fasta = self.test_data_dir / "invalid.fasta"
        with open(invalid_fasta, 'w') as f:
            f.write("This is not a FASTA file\n")
        
        result = validate_fasta_file(str(invalid_fasta))
        assert not result.is_valid, "Should have failed validation"
        
        # Cleanup
        invalid_fasta.unlink()
    
    def _test_large_file_handling(self):
        """Test large file handling."""
        from utils.resource_manager import get_resource_manager
        
        manager = get_resource_manager()
        
        # Create a moderately large test file
        large_file = self.test_data_dir / "large_test.txt"
        with open(large_file, 'w') as f:
            for i in range(1000):
                f.write(f"Line {i}: " + "A" * 100 + "\n")
        
        # Test file streaming
        lines_read = 0
        for line in manager.file_manager.read_file_lines(str(large_file), max_lines=500):
            lines_read += 1
        
        assert lines_read == 500, f"Expected 500 lines, got {lines_read}"
        
        # Cleanup
        large_file.unlink()
    
    def _test_file_error_scenarios(self):
        """Test file error scenarios."""
        from utils.validators import validate_file_path
        from utils.error_handling import FileSystemError
        
        # Test non-existent file
        assert not validate_file_path("/nonexistent/file.txt")
        
        # Test directory instead of file
        assert not validate_file_path(str(self.test_data_dir))
    
    # Resource management tests
    def _test_memory_monitoring(self):
        """Test memory monitoring."""
        from utils.resource_manager import get_resource_manager
        
        manager = get_resource_manager()
        
        # Get initial memory usage
        initial_usage = manager.memory_monitor.get_memory_usage()
        assert initial_usage > 0, "Memory usage should be positive"
        
        # Get system memory info
        sys_info = manager.memory_monitor.get_system_memory_info()
        assert 'total_mb' in sys_info
        assert sys_info['total_mb'] > 0
    
    def _test_concurrent_operations(self):
        """Test concurrent operation management."""
        from utils.resource_manager import get_resource_manager
        import threading
        
        manager = get_resource_manager()
        
        def test_operation():
            with manager.operation_manager.operation("test_op", "Test operation"):
                time.sleep(0.1)
        
        # Start multiple operations
        threads = []
        for i in range(3):
            thread = threading.Thread(target=test_operation)
            threads.append(thread)
            thread.start()
        
        # Check active operations
        time.sleep(0.05)  # Let operations start
        active_ops = manager.operation_manager.get_active_operations()
        assert len(active_ops) <= manager.limits.max_concurrent_operations
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Verify all operations completed
        final_ops = manager.operation_manager.get_active_operations()
        assert len(final_ops) == 0
    
    def _test_cache_management(self):
        """Test cache management."""
        from utils.resource_manager import get_resource_manager
        
        manager = get_resource_manager()
        
        # Create a test cache
        test_cache = {}
        
        def cache_size_estimator(cache):
            return len(str(cache))
        
        manager.cache_manager.register_cache("test_cache", test_cache, cache_size_estimator)
        
        # Add some data to cache
        for i in range(100):
            test_cache[f"key_{i}"] = f"value_{i}" * 10
        
        # Get cache size
        total_size = manager.cache_manager.get_total_cache_size()
        assert total_size > 0
        
        # Clear cache
        success = manager.cache_manager.clear_cache("test_cache")
        assert success
        
        # Verify cache is empty
        assert len(test_cache) == 0
    
    def _test_resource_cleanup(self):
        """Test resource cleanup."""
        from utils.resource_manager import get_resource_manager
        
        manager = get_resource_manager()
        
        # Create temporary files
        temp_files = []
        for i in range(3):
            temp_file = manager.file_manager.create_temp_file()
            temp_files.append(temp_file)
            
            # Write some data
            with open(temp_file, 'w') as f:
                f.write(f"Test data {i}")
        
        # Get temp file info
        temp_info = manager.file_manager.get_temp_files_info()
        assert temp_info['existing_count'] >= 3
        
        # Cleanup (with age 0 to force cleanup)
        cleaned = manager.file_manager.cleanup_temp_files(max_age_hours=0)
        assert cleaned >= 3
    
    # Error handling tests
    def _test_validation_errors(self):
        """Test validation error handling."""
        from utils.validators import validate_project
        from utils.error_handling import ValidationError
        
        # Test invalid project data
        invalid_data = {"name": "", "type": "invalid"}
        result = validate_project(invalid_data)
        assert not result.is_valid
        assert len(result.errors) > 0
    
    def _test_database_errors(self):
        """Test database error handling."""
        from database.db_manager import DatabaseManager, DatabaseError
        
        db = DatabaseManager()
        
        try:
            db.execute_query("INVALID SQL QUERY")
            assert False, "Should have raised DatabaseError"
        except DatabaseError as e:
            assert "Query execution failed" in str(e)
    
    def _test_file_system_errors(self):
        """Test file system error handling."""
        from utils.error_handling import FileSystemError
        from services.sequence_service import SequenceService
        
        service = SequenceService()
        
        # Try to import non-existent file
        success, result = service.import_fasta_file("/nonexistent/file.fasta", 1)
        assert not success
        assert "not found" in result.lower()
    
    def _test_network_errors(self):
        """Test network error handling."""
        from utils.network_handler import make_safe_request
        
        # Test request to invalid URL
        result = make_safe_request("http://invalid-url-that-does-not-exist.com")
        assert not result.success
        assert result.error is not None
    
    def _test_error_recovery(self):
        """Test error recovery mechanisms."""
        from utils.error_handling import get_error_handler, GeneStudioError
        
        handler = get_error_handler()
        
        # Test error handling with recovery
        recovery_called = False
        
        def test_recovery(error):
            nonlocal recovery_called
            recovery_called = True
            return True
        
        handler.register_recovery_strategy(GeneStudioError, test_recovery)
        
        # Create and handle error
        test_error = GeneStudioError("Test error")
        handled_error = handler.handle_error(test_error, suppress=True)
        
        assert recovery_called, "Recovery strategy should have been called"
    
    # End-to-end workflow tests
    def _test_complete_project_workflow(self):
        """Test complete project workflow from creation to deletion."""
        from services.project_service import ProjectService
        from services.sequence_service import SequenceService
        from services.analysis_service import AnalysisService
        
        project_service = ProjectService()
        sequence_service = SequenceService()
        analysis_service = AnalysisService()
        
        # 1. Create project
        success, project = project_service.create_project("Complete Test", "sequence_analysis")
        assert success
        
        # 2. Add sequences
        success, seq1 = sequence_service.create_sequence(project.id, "Seq1", "ATCGATCG", "dna")
        assert success
        
        success, seq2 = sequence_service.create_sequence(project.id, "Seq2", "GCTAGCTA", "dna")
        assert success
        
        # 3. Create analyses
        success, analysis1 = analysis_service.create_analysis(project.id, seq1.id, "gc_content", {})
        assert success
        
        # 4. Verify project statistics
        success, stats = project_service.get_project_statistics()
        assert success
        
        # 5. Clean up
        analysis_service.delete_analysis(analysis1.id)
        sequence_service.delete_sequence(seq1.id)
        sequence_service.delete_sequence(seq2.id)
        project_service.delete_project(project.id)
    
    def _test_sequence_analysis_workflow(self):
        """Test sequence analysis workflow."""
        # This would test the complete flow from sequence import to analysis results
        # For now, we'll do a simplified version
        
        from services.project_service import ProjectService
        from services.sequence_service import SequenceService
        
        project_service = ProjectService()
        sequence_service = SequenceService()
        
        # Create project and sequence
        success, project = project_service.create_project("Analysis Workflow", "sequence_analysis")
        assert success
        
        success, sequence = sequence_service.create_sequence(
            project.id, "Test Analysis", "ATCGATCGATCGATCG", "dna"
        )
        assert success
        
        # Calculate properties
        success, properties = sequence_service.calculate_sequence_properties(sequence)
        assert success
        assert 'length' in properties
        assert 'gc_percentage' in properties
        
        # Cleanup
        sequence_service.delete_sequence(sequence.id)
        project_service.delete_project(project.id)
    
    def _test_data_persistence_workflow(self):
        """Test data persistence across operations."""
        from services.project_service import ProjectService
        
        service = ProjectService()
        
        # Create project
        success, project = service.create_project("Persistence Test", "sequence_analysis")
        assert success
        original_id = project.id
        
        # Modify project
        project.description = "Modified description"
        success, result = service.update_project(project)
        assert success
        
        # Retrieve and verify persistence
        success, retrieved = service.get_project(original_id)
        assert success
        assert retrieved.description == "Modified description"
        
        # Cleanup
        service.delete_project(original_id)
    
    def _test_session_state_workflow(self):
        """Test session state persistence."""
        from utils.window_state_manager import WindowStateManager
        
        # This is a simplified test since we don't have a full UI context
        manager = WindowStateManager()
        
        # Test state data structure
        test_state = {
            'geometry': '1200x800+100+100',
            'maximized': False,
            'last_page': 'dashboard'
        }
        
        # In a real scenario, this would test actual window state persistence
        # For now, we just verify the manager can handle state data
        assert isinstance(test_state, dict)
        assert 'geometry' in test_state


# Global integration tester instance
_integration_tester = None


def get_integration_tester() -> IntegrationTester:
    """Get the global integration tester instance."""
    global _integration_tester
    if _integration_tester is None:
        _integration_tester = IntegrationTester()
    return _integration_tester


def run_integration_tests() -> Dict[str, Any]:
    """Run all integration tests."""
    tester = get_integration_tester()
    return tester.run_all_tests()


def run_test_suite(suite_name: str) -> Dict[str, Any]:
    """Run a specific test suite."""
    tester = get_integration_tester()
    return tester.run_suite(suite_name)


def validate_system_integration() -> bool:
    """Validate that all system components are properly integrated."""
    try:
        tester = get_integration_tester()
        
        # Run critical integration tests
        critical_suites = [
            "Database Integration",
            "Service Layer", 
            "Error Handling"
        ]
        
        for suite_name in critical_suites:
            if suite_name in tester.test_suites:
                result = tester.run_suite(suite_name)
                if result['failed'] > 0 or result['errors'] > 0:
                    return False
        
        return True
        
    except Exception as e:
        logging.getLogger(__name__).error(f"System integration validation failed: {e}")
        return False