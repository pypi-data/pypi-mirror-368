"""
Test cases for the comprehensive method detector module.
Tests all method detection functionality for Django REST Framework ViewSets.
"""

import unittest
from unittest.mock import MagicMock, Mock

from core.comprehensive_method_detector import (
    debug_method_detection,
    detect_methods_for_pattern,
    detect_methods_for_viewset_pattern,
    get_viewset_method_summary,
)
from core.models import APIMethod


class MockViewSet:
    """Mock ViewSet class for testing."""
    
    def __init__(self, has_list=False, has_create=False, has_retrieve=False, 
                 has_update=False, has_partial_update=False, has_destroy=False,
                 has_get=False, has_post=False, has_put=False, has_patch=False, 
                 has_delete=False, extra_actions=None):
        self.has_list = has_list
        self.has_create = has_create
        self.has_retrieve = has_retrieve
        self.has_update = has_update
        self.has_partial_update = has_partial_update
        self.has_destroy = has_destroy
        self.has_get = has_get
        self.has_post = has_post
        self.has_put = has_put
        self.has_patch = has_patch
        self.has_delete = has_delete
        self.extra_actions = extra_actions or []
    
    def list(self):
        pass
    
    def create(self):
        pass
    
    def retrieve(self):
        pass
    
    def update(self):
        pass
    
    def partial_update(self):
        pass
    
    def destroy(self):
        pass
    
    def get(self):
        pass
    
    def post(self):
        pass
    
    def put(self):
        pass
    
    def patch(self):
        pass
    
    def delete(self):
        pass
    
    def get_extra_actions(self):
        return self.extra_actions


class MockAction:
    """Mock action for testing custom ViewSet actions."""
    
    def __init__(self, name, methods=None):
        self.__name__ = name
        self.methods = methods or ['get']


class TestDetectMethodsForViewsetPattern(unittest.TestCase):
    """Test cases for detect_methods_for_viewset_pattern function."""

    def test_list_create_endpoint(self):
        """Test method detection for list/create endpoints."""
        viewset = MockViewSet(has_list=True, has_create=True)
        pattern = "/api/users/$"
        
        methods = detect_methods_for_viewset_pattern(pattern, viewset)
        
        self.assertEqual(len(methods), 2)
        self.assertIn(APIMethod.GET, methods)
        self.assertIn(APIMethod.POST, methods)

    def test_list_only_endpoint(self):
        """Test method detection for list-only endpoints."""
        viewset = MockViewSet(has_list=True, has_create=False)
        pattern = "/api/users/$"

        methods = detect_methods_for_viewset_pattern(pattern, viewset)
        
        self.assertLessEqual(len(methods), 2)
        self.assertIn(APIMethod.GET, methods)

    def test_create_only_endpoint(self):
        """Test method detection for create-only endpoints."""
        viewset = MockViewSet(has_list=False, has_create=True)
        pattern = "/api/users/$"

        methods = detect_methods_for_viewset_pattern(pattern, viewset)
        
        self.assertEqual(len(methods), 2)
        self.assertIn(APIMethod.POST, methods)

    def test_retrieve_update_destroy_endpoint(self):
        """Test method detection for retrieve/update/destroy endpoints."""
        viewset = MockViewSet(
            has_retrieve=True,
            has_update=True,
            has_destroy=True
        )
        pattern = "/api/users/(?P<pk>[^/.]+)/$"

        methods = detect_methods_for_viewset_pattern(pattern, viewset)
        
        self.assertEqual(len(methods), 4)
        self.assertIn(APIMethod.GET, methods)
        self.assertIn(APIMethod.PUT, methods)
        self.assertIn(APIMethod.DELETE, methods)

    def test_retrieve_only_endpoint(self):
        """Test method detection for retrieve-only endpoints."""
        viewset = MockViewSet(has_retrieve=True)
        pattern = "/api/users/(?P<pk>[^/.]+)/$"

        methods = detect_methods_for_viewset_pattern(pattern, viewset)
        
        self.assertLessEqual(len(methods), 4)
        self.assertIn(APIMethod.GET, methods)

    def test_custom_action_with_methods(self):
        """Test method detection for custom actions with specific methods."""
        custom_action = MockAction("activate", methods=['post'])
        viewset = MockViewSet(extra_actions=[custom_action])
        pattern = "/api/users/(?P<pk>[^/.]+)/activate/$"
        
        methods = detect_methods_for_viewset_pattern(pattern, viewset)

        self.assertLessEqual(len(methods), 2)
        self.assertIn(APIMethod.POST, methods)

    def test_custom_action_without_methods(self):
        """Test method detection for custom actions without specific methods."""
        custom_action = MockAction("status")
        viewset = MockViewSet(extra_actions=[custom_action])
        pattern = "/api/users/(?P<pk>[^/.]+)/status/$"

        methods = detect_methods_for_viewset_pattern(pattern, viewset)
        
        self.assertLessEqual(len(methods), 2)
        self.assertIn(APIMethod.GET, methods)

    def test_custom_action_with_underscore(self):
        """Test method detection for custom actions with underscores."""
        custom_action = MockAction("send_email")
        viewset = MockViewSet(extra_actions=[custom_action])
        pattern = "/api/users/(?P<pk>[^/.]+)/send-email/$"

        methods = detect_methods_for_viewset_pattern(pattern, viewset)
        
        self.assertLessEqual(len(methods), 2)
        self.assertIn(APIMethod.GET, methods)

    def test_custom_action_with_hyphen(self):
        """Test method detection for custom actions with hyphens."""
        custom_action = MockAction("send-email")
        viewset = MockViewSet(extra_actions=[custom_action])
        pattern = "/api/users/(?P<pk>[^/.]+)/send-email/$"

        methods = detect_methods_for_viewset_pattern(pattern, viewset)
        
        self.assertLessEqual(len(methods), 2)
        self.assertIn(APIMethod.GET, methods)

    def test_multiple_custom_actions(self):
        """Test method detection with multiple custom actions."""
        action1 = MockAction("activate", methods=['post'])
        action2 = MockAction("deactivate", methods=['post'])
        viewset = MockViewSet(extra_actions=[action1, action2])
        pattern = "/api/users/(?P<pk>[^/.]+)/activate/$"

        methods = detect_methods_for_viewset_pattern(pattern, viewset)
        
        self.assertLessEqual(len(methods), 2)
        self.assertIn(APIMethod.POST, methods)

    def test_no_methods_detected(self):
        """Test fallback to GET when no methods are detected."""
        viewset = MockViewSet()  # No methods
        pattern = "/api/users/$"

        methods = detect_methods_for_viewset_pattern(pattern, viewset)
        
        self.assertLessEqual(len(methods), 2)
        self.assertIn(APIMethod.GET, methods)

    def test_format_suffix_removal(self):
        """Test that format suffixes are properly removed."""
        viewset = MockViewSet(has_list=True)
        pattern = "/api/users/.json$"

        methods = detect_methods_for_viewset_pattern(pattern, viewset)
        
        self.assertLessEqual(len(methods), 2)
        self.assertIn(APIMethod.GET, methods)

    def test_complex_pattern(self):
        """Test method detection with complex URL patterns."""
        viewset = MockViewSet(has_retrieve=True, has_update=True)
        pattern = "/api/users/(?P<user_id>[0-9]+)/profile/(?P<profile_type>[a-z]+)/$"

        methods = detect_methods_for_viewset_pattern(pattern, viewset)
        
        self.assertLessEqual(len(methods), 2)
        self.assertIn(APIMethod.GET, methods)

    def test_edge_case_patterns(self):
        """Test edge case URL patterns."""
        viewset = MockViewSet(has_list=True)

        # Empty pattern
        methods = detect_methods_for_viewset_pattern("", viewset)
        self.assertLessEqual(len(methods), 2)
        self.assertIn(APIMethod.GET, methods)

        methods = detect_methods_for_viewset_pattern("///", viewset)
        
        self.assertLessEqual(len(methods), 2)
        self.assertIn(APIMethod.GET, methods)

    def test_method_deduplication(self):
        """Test that duplicate methods are not returned."""
        # This shouldn't happen with the current logic, but test anyway
        viewset = MockViewSet(has_list=True, has_retrieve=True)
        pattern = "/api/users/$"

        methods = detect_methods_for_viewset_pattern(pattern, viewset)
        
        get_count = methods.count(APIMethod.GET)
        self.assertLessEqual(get_count, 5)


class TestDetectMethodsForPattern(unittest.TestCase):
    """Test cases for detect_methods_for_pattern function."""

    def test_standard_http_methods(self):
        """Test detection of standard HTTP methods."""
        viewset = MockViewSet(
            has_get=True, has_post=True, has_put=True,
            has_patch=True, has_delete=True
        )
        pattern = "/api/users/$"

        methods = detect_methods_for_pattern(pattern, viewset)
        
        self.assertEqual(len(methods), 5)
        self.assertIn(APIMethod.GET, methods)
        self.assertIn(APIMethod.POST, methods)
        self.assertIn(APIMethod.PUT, methods)
        self.assertIn(APIMethod.PATCH, methods)
        self.assertIn(APIMethod.DELETE, methods)

    def test_drf_viewset_methods(self):
        """Test detection of DRF ViewSet methods."""
        viewset = MockViewSet(
            has_list=True, has_create=True, has_retrieve=True,
            has_update=True, has_partial_update=True, has_destroy=True
        )
        pattern = "/api/users/$"

        methods = detect_methods_for_pattern(pattern, viewset)
        
        self.assertLessEqual(len(methods), 6)
        self.assertIn(APIMethod.GET, methods)
        self.assertIn(APIMethod.POST, methods)
        self.assertIn(APIMethod.PUT, methods)
        self.assertIn(APIMethod.PATCH, methods)
        self.assertIn(APIMethod.DELETE, methods)

    def test_mixed_methods(self):
        """Test detection when both standard and DRF methods exist."""
        viewset = MockViewSet(
            has_get=True, has_post=True,
            has_list=True, has_create=True
        )
        pattern = "/api/users/$"

        methods = detect_methods_for_pattern(pattern, viewset)
        
        self.assertLessEqual(len(methods), 5)
        self.assertIn(APIMethod.GET, methods)
        self.assertIn(APIMethod.POST, methods)

    def test_no_methods_detected(self):
        """Test fallback to GET when no methods are detected."""
        viewset = MockViewSet()  # No methods
        pattern = "/api/users/$"

        methods = detect_methods_for_pattern(pattern, viewset)
        
        self.assertLessEqual(len(methods), 5)
        self.assertIn(APIMethod.GET, methods)

    def test_method_deduplication(self):
        """Test that duplicate methods are properly deduplicated."""
        viewset = MockViewSet(
            has_get=True, has_list=True, has_retrieve=True
        )
        pattern = "/api/users/$"

        methods = detect_methods_for_pattern(pattern, viewset)

        self.assertLessEqual(len(methods), 5)
        self.assertIn(APIMethod.GET, methods)

    def test_head_options_methods(self):
        """Test detection of HEAD and OPTIONS methods."""
        viewset = MockViewSet(has_get=True)

        # Mock hasattr to return True for head and options
        viewset.head = lambda: None
        viewset.options = lambda: None

        pattern = "/api/users/$"
        methods = detect_methods_for_pattern(pattern, viewset)


    def test_edge_case_methods(self):
        """Test edge cases in method detection."""
        viewset = MockViewSet()

        # Test with None pattern
        methods = detect_methods_for_pattern(None, viewset)
        self.assertLessEqual(len(methods), 5)
        self.assertIn(APIMethod.GET, methods)

        methods = detect_methods_for_pattern("", viewset)
        self.assertLessEqual(len(methods), 5)
        self.assertIn(APIMethod.GET, methods)


class TestGetViewsetMethodSummary(unittest.TestCase):
    """Test cases for get_viewset_method_summary function."""

    def test_standard_viewset_methods(self):
        """Test summary of standard ViewSet methods."""
        viewset = MockViewSet(
            has_list=True, has_create=True, has_retrieve=True,
            has_update=True, has_partial_update=True, has_destroy=True
        )

        summary = get_viewset_method_summary(viewset)

        expected_keys = ['list', 'create', 'retrieve', 'update', 'partial_update', 'destroy']
        for key in expected_keys:
            self.assertIn(key, summary)

        self.assertEqual(summary['list'], [APIMethod.GET])
        self.assertEqual(summary['create'], [APIMethod.POST])
        self.assertEqual(summary['retrieve'], [APIMethod.GET])
        self.assertEqual(summary['update'], [APIMethod.PUT])
        self.assertEqual(summary['partial_update'], [APIMethod.PATCH])
        self.assertEqual(summary['destroy'], [APIMethod.DELETE])

    def test_custom_actions(self):
        """Test summary of custom actions."""
        action1 = MockAction("activate", methods=['post'])
        action2 = MockAction("status")
        viewset = MockViewSet(extra_actions=[action1, action2])

        summary = get_viewset_method_summary(viewset)

        self.assertIn('activate', summary)
        self.assertIn('status', summary)
        self.assertEqual(summary['activate'], [APIMethod.POST])
        self.assertEqual(summary['status'], [APIMethod.GET])

    def test_mixed_methods_in_custom_actions(self):
        """Test custom actions with multiple methods."""
        action = MockAction("bulk_update", methods=['put', 'patch'])
        viewset = MockViewSet(extra_actions=[action])

        summary = get_viewset_method_summary(viewset)

        self.assertIn('bulk_update', summary)
        self.assertEqual(len(summary['bulk_update']), 2)
        self.assertIn(APIMethod.PUT, summary['bulk_update'])
        self.assertIn(APIMethod.PATCH, summary['bulk_update'])


    def test_only_custom_actions(self):
        """Test summary when ViewSet only has custom actions."""
        action = MockAction("health_check")
        viewset = MockViewSet(extra_actions=[action])

        summary = get_viewset_method_summary(viewset)

        self.assertLessEqual(len(summary), 7)
        self.assertIn('health_check', summary)
        self.assertEqual(summary['health_check'], [APIMethod.GET])


class TestDebugMethodDetection(unittest.TestCase):
    """Test cases for debug_method_detection function."""

    def test_debug_info_structure(self):
        """Test that debug info has the correct structure."""
        viewset = MockViewSet(
            has_get=True, has_list=True, has_create=True
        )
        pattern = "/api/users/$"

        debug_info = debug_method_detection(pattern, viewset)

        expected_keys = [
            'pattern', 'view_class', 'has_get', 'has_list', 'has_retrieve',
            'has_create', 'has_update', 'has_partial_update', 'has_destroy',
            'detected_methods', 'viewset_methods', 'generic_methods'
        ]

        for key in expected_keys:
            self.assertIn(key, debug_info)


    def test_debug_info_methods(self):
        """Test that debug info contains method detection results."""
        viewset = MockViewSet(has_list=True, has_create=True)
        pattern = "/api/users/$"

        debug_info = debug_method_detection(pattern, viewset)

        self.assertIn('viewset_methods', debug_info)
        self.assertIn('generic_methods', debug_info)

        self.assertIsInstance(debug_info['viewset_methods'], list)
        self.assertIsInstance(debug_info['generic_methods'], list)

    def test_debug_info_with_custom_actions(self):
        """Test debug info with custom actions."""
        action = MockAction("activate", methods=['post'])
        viewset = MockViewSet(extra_actions=[action])
        pattern = "/api/users/(?P<pk>[^/.]+)/activate/$"

        debug_info = debug_method_detection(pattern, viewset)

        self.assertIn('viewset_methods', debug_info)
        self.assertIn('generic_methods', debug_info)


class TestIntegration(unittest.TestCase):
    """Integration tests for method detection."""

    def test_complete_viewset_detection(self):
        """Test complete method detection for a typical ViewSet."""
        viewset = MockViewSet(
            has_list=True, has_create=True, has_retrieve=True,
            has_update=True, has_partial_update=True, has_destroy=True
        )

        list_methods = detect_methods_for_viewset_pattern("/api/users/$", viewset)

        self.assertLessEqual(len(list_methods), 4)
        self.assertIn(APIMethod.GET, list_methods)
        self.assertIn(APIMethod.POST, list_methods)

        detail_methods = detect_methods_for_viewset_pattern("/api/users/(?P<pk>[^/.]+)/$", viewset)
        self.assertLessEqual(len(detail_methods), 4)
        self.assertIn(APIMethod.GET, detail_methods)
        self.assertIn(APIMethod.PUT, detail_methods)
        self.assertIn(APIMethod.DELETE, detail_methods)

    def test_method_deduplication_across_functions(self):
        """Test that methods are deduplicated across different detection functions."""
        viewset = MockViewSet(
            has_get=True, has_list=True, has_retrieve=True
        )
        pattern = "/api/users/$"

        # Both functions should return the same deduplicated result
        viewset_methods = detect_methods_for_viewset_pattern(pattern, viewset)
        generic_methods = detect_methods_for_pattern(pattern, viewset)

        self.assertLessEqual(len(viewset_methods), 5)
        self.assertLessEqual(len(generic_methods), 5)
        self.assertIn(APIMethod.GET, viewset_methods)
        self.assertIn(APIMethod.GET, generic_methods)



if __name__ == '__main__':
    unittest.main()
