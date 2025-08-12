#!/usr/bin/env python3
"""
Test configuration for cloudbulkupload test suite.
This module provides configuration options for test behavior, including cleanup settings.
"""

import os
from typing import Optional


class TestConfig:
    """Configuration class for test suite behavior."""
    
    def __init__(self):
        """Initialize test configuration with defaults."""
        # Cleanup settings
        self.cleanup_enabled = self._get_bool_env("CLEANUP_ENABLED", default=True)
        self.keep_test_data = self._get_bool_env("KEEP_TEST_DATA", default=False)
        self.keep_buckets = self._get_bool_env("KEEP_BUCKETS", default=False)
        self.keep_local_files = self._get_bool_env("KEEP_LOCAL_FILES", default=False)
        
        # Test behavior settings
        self.verbose_tests = self._get_bool_env("VERBOSE_TESTS", default=False)
        self.show_progress = self._get_bool_env("SHOW_PROGRESS", default=True)
        
        # Performance settings
        self.performance_iterations = self._get_int_env("PERFORMANCE_ITERATIONS", default=3)
        self.max_threads = self._get_int_env("MAX_THREADS", default=50)
    
    def _get_bool_env(self, key: str, default: bool = False) -> bool:
        """Get boolean value from environment variable."""
        value = os.getenv(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')
    
    def _get_int_env(self, key: str, default: int = 0) -> int:
        """Get integer value from environment variable."""
        try:
            return int(os.getenv(key, str(default)))
        except ValueError:
            return default
    
    def should_cleanup(self, cleanup_type: str = "all") -> bool:
        """
        Determine if cleanup should be performed.
        
        Args:
            cleanup_type: Type of cleanup ('all', 'buckets', 'local_files', 'test_data')
        
        Returns:
            bool: True if cleanup should be performed
        """
        if not self.cleanup_enabled:
            return False
        
        if cleanup_type == "buckets" and self.keep_buckets:
            return False
        elif cleanup_type == "local_files" and self.keep_local_files:
            return False
        elif cleanup_type == "test_data" and self.keep_test_data:
            return False
        
        return True
    
    def get_cleanup_message(self, cleanup_type: str = "all") -> str:
        """
        Get a user-friendly message about cleanup behavior.
        
        Args:
            cleanup_type: Type of cleanup being performed
        
        Returns:
            str: Cleanup message
        """
        if not self.cleanup_enabled:
            return "🧹 Cleanup disabled globally"
        
        if cleanup_type == "buckets" and self.keep_buckets:
            return "📦 Keeping test buckets (KEEP_BUCKETS=True)"
        elif cleanup_type == "local_files" and self.keep_local_files:
            return "📁 Keeping local test files (KEEP_LOCAL_FILES=True)"
        elif cleanup_type == "test_data" and self.keep_test_data:
            return "💾 Keeping test data (KEEP_TEST_DATA=True)"
        
        return f"🧹 Cleaning up {cleanup_type}"
    
    def print_config(self):
        """Print current test configuration."""
        print("\n🔧 Test Configuration:")
        print(f"  Cleanup Enabled: {self.cleanup_enabled}")
        print(f"  Keep Test Data: {self.keep_test_data}")
        print(f"  Keep Buckets: {self.keep_buckets}")
        print(f"  Keep Local Files: {self.keep_local_files}")
        print(f"  Verbose Tests: {self.verbose_tests}")
        print(f"  Show Progress: {self.show_progress}")
        print(f"  Performance Iterations: {self.performance_iterations}")
        print(f"  Max Threads: {self.max_threads}")
        print()


# Global test configuration instance
test_config = TestConfig()


def get_test_config() -> TestConfig:
    """Get the global test configuration instance."""
    return test_config


def print_cleanup_help():
    """Print help information about cleanup configuration."""
    print("\n🧹 Cleanup Configuration Help:")
    print("=" * 40)
    print("Environment variables to control test cleanup:")
    print()
    print("  CLEANUP_ENABLED=true/false")
    print("    - Default: true")
    print("    - Disable all cleanup operations")
    print()
    print("  KEEP_TEST_DATA=true/false")
    print("    - Default: false")
    print("    - Keep uploaded test data in buckets")
    print()
    print("  KEEP_BUCKETS=true/false")
    print("    - Default: false")
    print("    - Keep test buckets (overrides KEEP_TEST_DATA)")
    print()
    print("  KEEP_LOCAL_FILES=true/false")
    print("    - Default: false")
    print("    - Keep local test files and directories")
    print()
    print("Examples:")
    print("  # Keep all test data and buckets")
    print("  KEEP_TEST_DATA=true KEEP_BUCKETS=true python -m pytest")
    print()
    print("  # Disable all cleanup")
    print("  CLEANUP_ENABLED=false python -m pytest")
    print()
    print("  # Keep only local files")
    print("  KEEP_LOCAL_FILES=true python -m pytest")
    print()
