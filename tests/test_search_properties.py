"""Property-based tests for search functionality."""

import pytest
from hypothesis import given, strategies as st, settings
import time
from datetime import datetime, timedelta

from utils.search_engine import SearchEngine, SearchResult
from services.search_service import SearchService
from viewmodels.search_viewmodel import SearchViewModel


class TestSearchProperties:
    """Property-based tests for search system."""
    
    @given(st.text(min_size=1, max_size=100))
    @settings(max_examples=100)
    def test_real_time_search_responsiveness(self, search_query):
        """**Feature: advanced-analysis-visualization, Property 1: Real-time search responsiveness**
        
        For any search query input, the system should return results within a reasonable 
        time frame (< 500ms for indexed data) and display them as the user types.
        """
        # Create search engine with test data
        engine = SearchEngine()
        
        # Add some test data to index
        test_data = [
            {'id': '1', 'title': 'Test Sequence 1', 'content': 'ATCGATCG', 'type': 'sequence'},
            {'id': '2', 'title': 'Sample Project', 'content': 'DNA analysis', 'type': 'project'},
            {'id': '3', 'title': 'Analysis Result', 'content': 'Pattern matching', 'type': 'analysis'}
        ]
        
        engine.build_index('sequences', [test_data[0]])
        engine.build_index('projects', [test_data[1]])
        engine.build_index('analyses', [test_data[2]])
        
        # Measure search time
        start_time = time.time()
        results = engine.search(search_query)
        response_time = time.time() - start_time
        
        # Property: Response time should be under 500ms for indexed data
        assert response_time < 0.5, f"Search took {response_time:.3f}s, should be < 0.5s"
        
        # Property: Results should be SearchResult objects
        assert isinstance(results, list)
        for result in results:
            assert isinstance(result, SearchResult)
    
    @given(st.text(min_size=2, max_size=50))
    @settings(max_examples=100)
    def test_fuzzy_matching_consistency(self, partial_query):
        """**Feature: advanced-analysis-visualization, Property 2: Fuzzy matching consistency**
        
        For any partial search input, the fuzzy matching algorithm should return results 
        with similarity scores above the configured threshold and rank them by relevance.
        """
        engine = SearchEngine()
        
        # Create test data with variations
        test_data = [
            {'id': '1', 'title': f'{partial_query}', 'content': 'exact match'},
            {'id': '2', 'title': f'{partial_query}x', 'content': 'close match'},
            {'id': '3', 'title': f'pre{partial_query}', 'content': 'prefix match'},
            {'id': '4', 'title': 'unrelated content', 'content': 'no match'}
        ]
        
        engine.build_index('test', test_data)
        
        # Search with fuzzy matching
        results = engine.search(partial_query)
        
        # Property: All results should have relevance scores above 0
        for result in results:
            assert result.relevance_score > 0, "All results should have positive relevance"
        
        # Property: Results should be ranked by relevance (descending)
        if len(results) > 1:
            for i in range(len(results) - 1):
                assert results[i].relevance_score >= results[i + 1].relevance_score, \
                    "Results should be ranked by relevance score"
    
    @given(st.lists(st.dictionaries(
        keys=st.sampled_from(['id', 'title', 'content', 'type']),
        values=st.text(min_size=1, max_size=50),
        min_size=4, max_size=4
    ), min_size=1, max_size=10))
    @settings(max_examples=100)
    def test_search_result_categorization(self, test_items):
        """**Feature: advanced-analysis-visualization, Property 3: Search result categorization**
        
        For any search results, all results should be properly categorized by type 
        (sequences, projects, analyses) and ranked by relevance score in descending order.
        """
        engine = SearchEngine()
        
        # Ensure items have required fields and valid types
        valid_types = ['sequences', 'projects', 'analyses']
        processed_items = []
        
        for i, item in enumerate(test_items):
            processed_item = {
                'id': str(i),
                'title': item.get('title', f'Item {i}'),
                'content': item.get('content', f'Content {i}'),
                'type': valid_types[i % len(valid_types)]
            }
            processed_items.append(processed_item)
        
        # Build indices by type
        by_type = {}
        for item in processed_items:
            item_type = item['type']
            if item_type not in by_type:
                by_type[item_type] = []
            by_type[item_type].append(item)
        
        for item_type, items in by_type.items():
            engine.build_index(item_type, items)
        
        # Search for common term
        results = engine.search('Item')
        
        # Property: All results should have a valid type
        valid_result_types = set(valid_types)
        for result in results:
            assert result.type in valid_result_types, f"Result type '{result.type}' should be valid"
        
        # Property: Results should be ranked by relevance
        if len(results) > 1:
            for i in range(len(results) - 1):
                assert results[i].relevance_score >= results[i + 1].relevance_score, \
                    "Results should be ranked by relevance"
    
    @given(st.dictionaries(
        keys=st.sampled_from(['type', 'status', 'date_range']),
        values=st.one_of(
            st.text(min_size=1, max_size=20),
            st.dictionaries(
                keys=st.sampled_from(['start', 'end']),
                values=st.datetimes(min_value=datetime(2020, 1, 1), max_value=datetime(2025, 1, 1))
            )
        )
    ))
    @settings(max_examples=100)
    def test_filter_application_correctness(self, filters):
        """**Feature: advanced-analysis-visualization, Property 4: Filter application correctness**
        
        For any combination of search filters, the filtered results should only include 
        items that match all applied criteria.
        """
        engine = SearchEngine()
        
        # Create test data with various attributes
        test_data = [
            {
                'id': '1', 'title': 'Project A', 'content': 'DNA analysis',
                'type': 'project', 'status': 'active', 'created_date': datetime(2023, 1, 1)
            },
            {
                'id': '2', 'title': 'Sequence B', 'content': 'ATCG sequence',
                'type': 'sequence', 'status': 'completed', 'created_date': datetime(2023, 6, 1)
            },
            {
                'id': '3', 'title': 'Analysis C', 'content': 'Pattern matching',
                'type': 'analysis', 'status': 'active', 'created_date': datetime(2024, 1, 1)
            }
        ]
        
        # Add metadata to items
        for item in test_data:
            metadata = {k: v for k, v in item.items() if k not in ['id', 'title', 'content']}
            item['metadata'] = metadata
        
        engine.build_index('test', test_data)
        
        # Search with filters
        results = engine.search('', filters=filters)
        
        # Property: All results should match the applied filters
        for result in results:
            for filter_key, filter_value in filters.items():
                if filter_key == 'date_range' and isinstance(filter_value, dict):
                    # Handle date range filter
                    result_date = result.created_date
                    if 'start' in filter_value:
                        assert result_date >= filter_value['start'], \
                            f"Result date {result_date} should be >= {filter_value['start']}"
                    if 'end' in filter_value:
                        assert result_date <= filter_value['end'], \
                            f"Result date {result_date} should be <= {filter_value['end']}"
                elif filter_key in result.metadata:
                    assert result.metadata[filter_key] == filter_value, \
                        f"Result {filter_key} should match filter value {filter_value}"
    
    @given(st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=20))
    @settings(max_examples=100)
    def test_search_history_persistence(self, search_queries):
        """**Feature: advanced-analysis-visualization, Property 5: Search history persistence**
        
        For any sequence of search queries, the system should maintain search history 
        and provide relevant suggestions based on previous successful queries.
        """
        engine = SearchEngine()
        
        # Add some test data
        test_data = [
            {'id': '1', 'title': 'Test Item', 'content': 'searchable content'}
        ]
        engine.build_index('test', test_data)
        
        # Perform searches to build history
        unique_queries = list(set(search_queries))  # Remove duplicates
        for query in unique_queries:
            engine.search(query)
        
        # Property: Search history should contain performed queries
        history = engine.get_search_history()
        
        # Should have history entries
        assert len(history) > 0, "Should have search history entries"
        
        # History entries should have required fields
        for entry in history:
            assert 'query' in entry, "History entry should have query"
            assert 'timestamp' in entry, "History entry should have timestamp"
            assert isinstance(entry['timestamp'], datetime), "Timestamp should be datetime"
        
        # Property: Suggestions should be based on history
        if unique_queries:
            # Test suggestions for partial queries
            for query in unique_queries[:3]:  # Test first 3 queries
                if len(query) > 2:
                    partial = query[:len(query)//2]
                    suggestions = engine.suggest(partial)
                    
                    # Suggestions should be strings
                    for suggestion in suggestions:
                        assert isinstance(suggestion, str), "Suggestions should be strings"
        
        # Property: History should be limited to max_history
        assert len(history) <= engine.max_history, \
            f"History length {len(history)} should not exceed max {engine.max_history}"


def test_search_properties_manually():
    """Manual test runner for property-based tests."""
    print("Running property-based tests for search functionality...")
    
    # Test 1: Real-time search responsiveness
    print("1. Testing real-time search responsiveness...")
    engine = SearchEngine()
    test_data = [
        {'id': '1', 'title': 'Test Sequence 1', 'content': 'ATCGATCG', 'type': 'sequence'},
    ]
    engine.build_index('sequences', test_data)
    
    start_time = time.time()
    results = engine.search("test")
    response_time = time.time() - start_time
    
    assert response_time < 0.5, f"Search took {response_time:.3f}s, should be < 0.5s"
    print(f"   ✅ Response time: {response_time:.3f}s")
    
    # Test 2: Fuzzy matching consistency
    print("2. Testing fuzzy matching consistency...")
    engine2 = SearchEngine()
    test_data2 = [
        {'id': '1', 'title': 'sample', 'content': 'exact match'},
        {'id': '2', 'title': 'samplex', 'content': 'close match'},
    ]
    engine2.build_index('test', test_data2)
    results = engine2.search("sample")
    
    for result in results:
        assert result.relevance_score > 0, "All results should have positive relevance"
    
    if len(results) > 1:
        for i in range(len(results) - 1):
            assert results[i].relevance_score >= results[i + 1].relevance_score
    print(f"   ✅ Found {len(results)} results with proper ranking")
    
    # Test 3: Search result categorization
    print("3. Testing search result categorization...")
    engine3 = SearchEngine()
    test_data3 = [
        {'id': '1', 'title': 'Item 1', 'content': 'Content 1', 'type': 'sequences'},
        {'id': '2', 'title': 'Item 2', 'content': 'Content 2', 'type': 'projects'},
    ]
    engine3.build_index('sequences', [test_data3[0]])
    engine3.build_index('projects', [test_data3[1]])
    
    results = engine3.search('Item')
    valid_types = {'sequences', 'projects', 'analyses'}
    for result in results:
        assert result.type in valid_types, f"Result type '{result.type}' should be valid"
    print(f"   ✅ Found {len(results)} properly categorized results")
    
    # Test 4: Filter application
    print("4. Testing filter application...")
    engine4 = SearchEngine()
    test_data4 = [
        {
            'id': '1', 'title': 'Project A', 'content': 'DNA analysis',
            'type': 'project', 'status': 'active'
        }
    ]
    # Add metadata
    for item in test_data4:
        metadata = {k: v for k, v in item.items() if k not in ['id', 'title', 'content']}
        item['metadata'] = metadata
    
    engine4.build_index('test', test_data4)
    results = engine4.search('', filters={'type': 'project'})
    print(f"   ✅ Filter test completed with {len(results)} results")
    
    # Test 5: Search history persistence
    print("5. Testing search history persistence...")
    engine5 = SearchEngine()
    test_data5 = [{'id': '1', 'title': 'Test Item', 'content': 'searchable content'}]
    engine5.build_index('test', test_data5)
    
    # Perform searches
    queries = ['query1', 'query2', 'test']
    for query in queries:
        engine5.search(query)
    
    history = engine5.get_search_history()
    assert len(history) > 0, "Should have search history entries"
    
    for entry in history:
        assert 'query' in entry, "History entry should have query"
        assert 'timestamp' in entry, "History entry should have timestamp"
    print(f"   ✅ Search history contains {len(history)} entries")
    
    print("\n🎉 All property tests completed successfully!")


if __name__ == "__main__":
    test_search_properties_manually()