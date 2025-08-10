"""Tests for timechecker core functionality."""

import pytest
from timechecker.core import TimeChecker, get_timezone_time

def test_timechecker_init():
    """Test TimeChecker initialization."""
    checker = TimeChecker()
    assert isinstance(checker, TimeChecker)

def test_supported_timezones():
    """Test supported timezone list."""
    checker = TimeChecker()
    timezones = checker.list_timezones()
    expected = ['PST', 'EST', 'BST', 'WAT', 'CET']
    assert set(timezones) == set(expected)

def test_get_time_valid_timezone():
    """Test getting time for valid timezone."""
    checker = TimeChecker()
    result = checker.get_time('PST')
    assert isinstance(result, str)
    assert 'PST' in result or 'PDT' in result

def test_get_time_invalid_timezone():
    """Test getting time for invalid timezone."""
    checker = TimeChecker()
    with pytest.raises(ValueError):
        checker.get_time('INVALID')

def test_convenience_function():
    """Test convenience function."""
    result = get_timezone_time('EST')
    assert isinstance(result, str)
    assert 'EST' in result or 'EDT' in result