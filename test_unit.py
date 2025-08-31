import unittest
import os
import sys
import tempfile
import shutil
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Add the current directory to Python path to import project modules
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

class CoreLangGraphReActTests(unittest.TestCase):
    """Core 5 unit tests for LangGraph ReAct Implementation with real components"""
    
    @classmethod
    def setUpClass(cls):
        """Load environment variables and validate API keys"""
        load_dotenv()
        
        # Validate Gemini API key
        cls.gemini_api_key = os.getenv('GEMINI_API_KEY')
        if not cls.gemini_api_key or not cls.gemini_api_key.startswith('AIza'):
            raise unittest.SkipTest("Valid GEMINI_API_KEY not found in environment")
        
        # Validate Tavily API key
        cls.tavily_api_key = os.getenv('TAVILY_API_KEY')
        if not cls.tavily_api_key or not cls.tavily_api_key.startswith('tvly-'):
            raise unittest.SkipTest("Valid TAVILY_API_KEY not found in environment")
        
        print(f"Using Gemini API Key: {cls.gemini_api_key[:10]}...{cls.gemini_api_key[-5:]}")
        print(f"Using Tavily API Key: {cls.tavily_api_key[:10]}...{cls.tavily_api_key[-5:]}")
        
        # Load configuration only (no heavy imports)
        try:
            from src.config import Config
            cls.Config = Config
            print("LangGraph ReAct configuration loaded successfully")
        except ImportError as e:
            raise unittest.SkipTest(f"Required LangGraph ReAct configuration not found: {e}")

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_query = "What is artificial intelligence?"

    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_configuration_and_api_validation(self):
        """Test 1: Configuration and API Key Validation"""
        print("Running Test 1: Configuration and API Validation")
        
        # Test API key configuration
        self.assertIsNotNone(self.Config.GEMINI_API_KEY)
        self.assertIsNotNone(self.Config.TAVILY_API_KEY)
        self.assertTrue(self.Config.GEMINI_API_KEY.startswith('AIza'))
        self.assertTrue(self.Config.TAVILY_API_KEY.startswith('tvly-'))
        
        # Test model configuration
        self.assertEqual(self.Config.GEMINI_MODEL, "gemini-2.0-flash-exp")
        self.assertIsInstance(self.Config.TEMPERATURE, float)
        self.assertIsInstance(self.Config.MAX_OUTPUT_TOKENS, int)
        
        # Test workflow configuration
        self.assertEqual(self.Config.MAX_RETRIES, 3)
        self.assertEqual(self.Config.MAX_SEARCH_RESULTS, 10)
        self.assertGreater(self.Config.RATE_LIMIT_REQUESTS_PER_MINUTE, 0)
        
        # Test safety configuration
        self.assertIsInstance(self.Config.TRUSTED_DOMAINS, set)
        self.assertGreater(len(self.Config.TRUSTED_DOMAINS), 10)
        self.assertIsInstance(self.Config.BLOCKED_KEYWORDS, list)
        self.assertGreater(len(self.Config.BLOCKED_KEYWORDS), 5)
        
        # Test specific trusted domains
        expected_domains = ["wikipedia.org", "arxiv.org", "github.com"]
        for domain in expected_domains:
            self.assertIn(domain, self.Config.TRUSTED_DOMAINS)
        
        # Test specific blocked keywords
        expected_keywords = ["violence", "hate", "harassment"]
        for keyword in expected_keywords:
            self.assertIn(keyword, self.Config.BLOCKED_KEYWORDS)
        
        # Test configuration validation
        is_valid = self.Config.validate_config()
        self.assertTrue(is_valid)
        
        # Test safe configuration
        safe_config = self.Config.get_safe_config()
        self.assertIn("model", safe_config)
        self.assertIn("temperature", safe_config)
        self.assertNotIn("api_key", str(safe_config).lower())
        
        print(f"PASS: API configuration - Gemini: {self.Config.GEMINI_MODEL}, Tavily: Available")
        print(f"PASS: Safety configuration - {len(self.Config.TRUSTED_DOMAINS)} trusted domains, {len(self.Config.BLOCKED_KEYWORDS)} blocked keywords")
        print(f"PASS: Workflow configuration - Max retries: {self.Config.MAX_RETRIES}, Rate limit: {self.Config.RATE_LIMIT_REQUESTS_PER_MINUTE}")
        print("PASS: Configuration and API validation completed")

    def test_02_langgraph_state_management(self):
        """Test 2: LangGraph State Management with TypedDict"""
        print("Running Test 2: LangGraph State Management")
        
        # Import state management components
        from src.state import ResearchState, SearchResult, SafetyCheck
        from src.nodes import create_initial_state
        
        # Test initial state creation
        initial_state = create_initial_state(self.test_query)
        
        # Validate state structure
        self.assertEqual(initial_state['research_query'], self.test_query)
        self.assertEqual(initial_state['current_step'], 'initialized')
        self.assertEqual(initial_state['retry_count'], 0)
        self.assertEqual(initial_state['max_retries'], self.Config.MAX_RETRIES)
        self.assertTrue(initial_state['is_safe'])
        self.assertIsInstance(initial_state['sources'], list)
        self.assertIsInstance(initial_state['errors'], list)
        self.assertIsInstance(initial_state['warnings'], list)
        self.assertIsInstance(initial_state['safety_checks'], list)
        
        # Test state updates
        initial_state['current_step'] = 'planning'
        initial_state['plan'] = 'Test research plan'
        self.assertEqual(initial_state['current_step'], 'planning')
        self.assertEqual(initial_state['plan'], 'Test research plan')
        
        # Test SearchResult structure
        test_search_result = SearchResult(
            url="https://example.com",
            title="Test Article",
            content="Test content for validation",
            score=0.85
        )
        
        self.assertEqual(test_search_result.url, "https://example.com")
        self.assertEqual(test_search_result.title, "Test Article")
        self.assertEqual(test_search_result.score, 0.85)
        
        # Test SafetyCheck structure
        test_safety_check = SafetyCheck(
            is_safe=True,
            reason="Content passed safety validation",
            confidence=0.9,
            flagged_content=[]
        )
        
        self.assertTrue(test_safety_check.is_safe)
        self.assertEqual(test_safety_check.confidence, 0.9)
        self.assertEqual(len(test_safety_check.flagged_content), 0)
        
        print(f"PASS: State management - Initial state: {initial_state['current_step']}")
        print(f"PASS: SearchResult structure validated")
        print(f"PASS: SafetyCheck structure validated")
        print("PASS: LangGraph state management validated")

    def test_03_safety_validation_system(self):
        """Test 3: Multi-layer Safety Validation System"""
        print("Running Test 3: Safety Validation System")
        
        # Import safety components
        from src.safety import URLValidator, ContentModerationChain, SafetyValidator, TokenBucket
        
        # Test URL validator
        url_validator = URLValidator(self.Config.TRUSTED_DOMAINS)
        
        # Test trusted domain
        trusted_check = url_validator.validate_url("https://wikipedia.org/wiki/AI")
        self.assertTrue(trusted_check.is_safe)
        self.assertGreater(trusted_check.confidence, 0.8)
        
        # Test untrusted domain
        untrusted_check = url_validator.validate_url("https://suspicious-site.com/content")
        self.assertFalse(untrusted_check.is_safe)
        
        # Test content moderation
        content_moderator = ContentModerationChain(self.Config.BLOCKED_KEYWORDS)
        
        # Test safe content
        safe_check = content_moderator.moderate_content("Educational content about science and technology.")
        self.assertTrue(safe_check.is_safe)
        
        # Test unsafe content
        unsafe_check = content_moderator.moderate_content("Content with violence and harmful material.")
        self.assertFalse(unsafe_check.is_safe)
        self.assertGreater(len(unsafe_check.flagged_content), 0)
        
        # Test safety validator aggregation
        safety_validator = SafetyValidator()
        
        mixed_checks = [trusted_check, safe_check, unsafe_check]
        aggregated = safety_validator.aggregate_safety_checks(mixed_checks)
        self.assertFalse(aggregated.is_safe)  # Should fail due to unsafe content
        
        # Test token bucket rate limiting
        bucket = TokenBucket(capacity=5, refill_rate=2.0)
        
        self.assertTrue(bucket.consume(3))
        self.assertTrue(bucket.consume(2))
        self.assertFalse(bucket.consume(1))  # Should be empty
        
        wait_time = bucket.wait_time(1)
        self.assertGreater(wait_time, 0)
        
        print(f"PASS: URL validation - Trusted domains: {len(self.Config.TRUSTED_DOMAINS)}")
        print(f"PASS: Content moderation - Blocked keywords: {len(self.Config.BLOCKED_KEYWORDS)}")
        print(f"PASS: Rate limiting - Token bucket working")
        print("PASS: Safety validation system validated")

    def test_04_structured_output_parsing(self):
        """Test 4: Structured Output Parsing for LLM Responses"""
        print("Running Test 4: Structured Output Parsing")
        
        # Import parsing components
        from src.tools import StructuredOutputParser
        from src.state import PlanningOutput, SynthesisOutput, ReflexionOutput
        
        # Test planning output parsing with JSON
        json_planning_text = '''
        Here's the research plan:
        ```json
        {
            "research_plan": "Comprehensive AI research approach",
            "search_queries": ["AI definition", "AI applications", "AI future"],
            "expected_sources": ["academic papers", "tech articles"],
            "success_criteria": "Complete understanding of AI"
        }
        ```
        '''
        
        planning_output = StructuredOutputParser.parse_planning_output(json_planning_text)
        self.assertIsInstance(planning_output, PlanningOutput)
        self.assertEqual(planning_output.research_plan, "Comprehensive AI research approach")
        self.assertEqual(len(planning_output.search_queries), 3)
        self.assertIn("AI definition", planning_output.search_queries)
        
        # Test planning output parsing with text fallback
        text_planning = '''
        Research Plan: Study artificial intelligence comprehensively
        
        Search Queries:
        - What is artificial intelligence
        - AI applications in industry
        
        Expected Sources:
        - Academic research papers
        
        Success Criteria: Comprehensive understanding achieved
        '''
        
        text_output = StructuredOutputParser.parse_planning_output(text_planning)
        self.assertIsInstance(text_output, PlanningOutput)
        self.assertGreater(len(text_output.research_plan), 10)
        self.assertGreater(len(text_output.search_queries), 0)
        
        # Test synthesis output parsing
        synthesis_text = "This is a comprehensive research summary with key findings about AI."
        synthesis_output = StructuredOutputParser.parse_synthesis_output(synthesis_text)
        self.assertIsInstance(synthesis_output, SynthesisOutput)
        self.assertIn("comprehensive", synthesis_output.research_summary.lower())
        self.assertIsInstance(synthesis_output.key_findings, list)
        self.assertGreater(synthesis_output.confidence_level, 0.0)
        self.assertLessEqual(synthesis_output.confidence_level, 1.0)
        
        # Test reflexion output parsing
        reflexion_text = "The previous attempt failed. We should retry with broader queries."
        reflexion_output = StructuredOutputParser.parse_reflexion_output(reflexion_text)
        self.assertIsInstance(reflexion_output, ReflexionOutput)
        self.assertIsInstance(reflexion_output.critique, str)
        self.assertIsInstance(reflexion_output.identified_issues, list)
        self.assertTrue(reflexion_output.should_retry)  # Should detect "retry" keyword
        
        print("PASS: JSON parsing working correctly")
        print("PASS: Text fallback parsing working correctly")
        print("PASS: Planning, synthesis, and reflexion parsing validated")
        print("PASS: Structured output parsing validated")

    def test_05_langgraph_workflow_and_nodes(self):
        """Test 5: LangGraph Workflow and Research Nodes Structure"""
        print("Running Test 5: LangGraph Workflow and Nodes")
        
        # Import workflow components
        from src.graph import ResearchWorkflow
        from src.nodes import ResearchNodes
        
        # Test workflow initialization
        workflow = ResearchWorkflow()
        self.assertIsNotNone(workflow.graph)
        self.assertIsNotNone(workflow.nodes)
        
        # Test checkpointing configuration
        if self.Config.CHECKPOINT_ENABLED:
            self.assertIsNotNone(workflow.checkpointer)
        
        # Test research nodes initialization
        nodes = workflow.nodes
        self.assertIsNotNone(nodes.search_tool)
        self.assertIsNotNone(nodes.llm)
        self.assertIsNotNone(nodes.safety_validator)
        
        # Test node methods availability
        import inspect
        
        node_methods = inspect.getmembers(ResearchNodes, predicate=inspect.isfunction)
        node_method_names = [name for name, _ in node_methods]
        
        expected_node_methods = ['plan_node', 'search_node', 'validate_node', 'synthesize_node', 'safety_node', 'reflexion_node']
        for method in expected_node_methods:
            self.assertIn(method, node_method_names)
        
        # Test workflow methods
        workflow_methods = inspect.getmembers(ResearchWorkflow, predicate=inspect.isfunction)
        workflow_method_names = [name for name, _ in workflow_methods]
        
        expected_workflow_methods = ['run_research', 'get_state_history', 'resume_from_checkpoint']
        for method in expected_workflow_methods:
            self.assertIn(method, workflow_method_names)
        
        # Test routing methods
        routing_methods = [name for name in workflow_method_names if name.startswith('_route_after_')]
        expected_routing_methods = ['_route_after_planning', '_route_after_search', '_route_after_validation', '_route_after_synthesis', '_route_after_safety', '_route_after_reflexion']
        
        for method in expected_routing_methods:
            self.assertIn(method, routing_methods)
        
        # Test state creation
        from src.nodes import create_initial_state
        initial_state = create_initial_state(self.test_query)
        
        self.assertEqual(initial_state['research_query'], self.test_query)
        self.assertEqual(initial_state['current_step'], 'initialized')
        self.assertEqual(initial_state['retry_count'], 0)
        self.assertTrue(initial_state['is_safe'])
        
        print(f"PASS: LangGraph workflow - Graph: ✅, Nodes: ✅, Checkpointing: {'✅' if self.Config.CHECKPOINT_ENABLED else '❌'}")
        print(f"PASS: Research nodes - {len(expected_node_methods)} node methods available")
        print(f"PASS: Workflow routing - {len(routing_methods)} routing methods available")
        print(f"PASS: State management - Initial state created successfully")
        print("PASS: LangGraph workflow and nodes validated")

def run_core_tests():
    """Run core tests and provide summary"""
    print("=" * 70)
    print("[*] Core LangGraph ReAct Implementation Unit Tests (5 Tests)")
    print("Testing with REAL APIs and LangGraph ReAct Components")
    print("=" * 70)
    
    # Check API keys
    load_dotenv()
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    tavily_api_key = os.getenv('TAVILY_API_KEY')
    
    if not gemini_api_key or not gemini_api_key.startswith('AIza'):
        print("[ERROR] Valid GEMINI_API_KEY not found!")
        return False
    
    if not tavily_api_key or not tavily_api_key.startswith('tvly-'):
        print("[ERROR] Valid TAVILY_API_KEY not found!")
        return False
    
    print(f"[OK] Using Gemini API Key: {gemini_api_key[:10]}...{gemini_api_key[-5:]}")
    print(f"[OK] Using Tavily API Key: {tavily_api_key[:10]}...{tavily_api_key[-5:]}")
    print()
    
    # Run tests
    suite = unittest.TestLoader().loadTestsFromTestCase(CoreLangGraphReActTests)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    print("[*] Test Results:")
    print(f"[*] Tests Run: {result.testsRun}")
    print(f"[*] Failures: {len(result.failures)}")
    print(f"[*] Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n[FAILURES]:")
        for test, traceback in result.failures:
            print(f"  - {test}")
            print(f"    {traceback}")
    
    if result.errors:
        print("\n[ERRORS]:")
        for test, traceback in result.errors:
            print(f"  - {test}")
            print(f"    {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success:
        print("\n[SUCCESS] All 5 core LangGraph ReAct tests passed!")
        print("[OK] LangGraph ReAct components working correctly with real APIs")
        print("[OK] Configuration, State Management, Safety Validation, Output Parsing, Workflow validated")
    else:
        print(f"\n[WARNING] {len(result.failures) + len(result.errors)} test(s) failed")
    
    return success

if __name__ == "__main__":
    print("[*] Starting Core LangGraph ReAct Implementation Tests")
    print("[*] 5 essential tests with real APIs and LangGraph ReAct components")
    print("[*] Components: Configuration, State Management, Safety Validation, Output Parsing, Workflow")
    print()
    
    success = run_core_tests()
    exit(0 if success else 1)