"""
Test V6 Payload Filtering - Mandate 22

Tests that V6 plugins correctly use alert.alignment from payload
instead of calling TrendManager for fresh entry validation.

Test Cases:
1. Strong Alignment (3/0 for BUY) - Should PASS validation
2. Weak Alignment (1/2 for BUY) - Should REJECT
3. Missing Alignment (0/0) - Should proceed with caution (warning)
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from Trading_Bot.src.core.zepix_v6_alert import ZepixV6Alert


class TestZepixV6AlertAlignment:
    """Test ZepixV6Alert alignment parsing"""
    
    def test_strong_bullish_alignment(self):
        """Test Case 1: Strong bullish alignment (3/0)"""
        alert = ZepixV6Alert(
            type="BULLISH_ENTRY",
            ticker="XAUUSD",
            tf="5",
            price=2650.50,
            direction="BUY",
            conf_score=85,
            adx=30.0,
            alignment="3/0"  # Strong bullish: 3 bullish, 0 bearish
        )
        
        bull_count, bear_count = alert.get_pulse_counts()
        
        assert bull_count == 3, f"Expected bull_count=3, got {bull_count}"
        assert bear_count == 0, f"Expected bear_count=0, got {bear_count}"
        assert alert.bull_count == 3
        assert alert.bear_count == 0
        
        # For BUY direction, need bull_count >= 3
        is_aligned = bull_count >= 3
        assert is_aligned, "Strong bullish alignment should pass for BUY"
    
    def test_weak_alignment_rejected(self):
        """Test Case 2: Weak alignment (1/2) should be rejected for BUY"""
        alert = ZepixV6Alert(
            type="BULLISH_ENTRY",
            ticker="XAUUSD",
            tf="5",
            price=2650.50,
            direction="BUY",
            conf_score=85,
            adx=30.0,
            alignment="1/2"  # Weak: 1 bullish, 2 bearish
        )
        
        bull_count, bear_count = alert.get_pulse_counts()
        
        assert bull_count == 1, f"Expected bull_count=1, got {bull_count}"
        assert bear_count == 2, f"Expected bear_count=2, got {bear_count}"
        
        # For BUY direction, need bull_count >= 3
        is_aligned = bull_count >= 3
        assert not is_aligned, "Weak alignment (1/2) should be rejected for BUY"
    
    def test_missing_alignment_handled(self):
        """Test Case 3: Missing alignment (0/0) should be handled gracefully"""
        alert = ZepixV6Alert(
            type="BULLISH_ENTRY",
            ticker="XAUUSD",
            tf="5",
            price=2650.50,
            direction="BUY",
            conf_score=85,
            adx=30.0,
            alignment="0/0"  # Missing/default alignment
        )
        
        bull_count, bear_count = alert.get_pulse_counts()
        
        assert bull_count == 0, f"Expected bull_count=0, got {bull_count}"
        assert bear_count == 0, f"Expected bear_count=0, got {bear_count}"
        
        # Check if alignment is missing
        is_missing = alert.alignment == "0/0" or (bull_count == 0 and bear_count == 0)
        assert is_missing, "Should detect missing alignment data"
    
    def test_strong_bearish_alignment(self):
        """Test strong bearish alignment (0/4) for SELL"""
        alert = ZepixV6Alert(
            type="BEARISH_ENTRY",
            ticker="XAUUSD",
            tf="60",
            price=2650.50,
            direction="SELL",
            conf_score=85,
            adx=30.0,
            alignment="0/4"  # Strong bearish: 0 bullish, 4 bearish
        )
        
        bull_count, bear_count = alert.get_pulse_counts()
        
        assert bull_count == 0
        assert bear_count == 4
        
        # For SELL direction, need bear_count >= 3 (5M/15M) or >= 4 (1H)
        is_aligned_5m = bear_count >= 3
        is_aligned_1h = bear_count >= 4
        
        assert is_aligned_5m, "Strong bearish should pass 5M threshold"
        assert is_aligned_1h, "Strong bearish should pass 1H threshold"
    
    def test_alignment_parsing_edge_cases(self):
        """Test edge cases in alignment parsing"""
        # Test with 5/1 format
        alert1 = ZepixV6Alert(
            type="BULLISH_ENTRY",
            ticker="XAUUSD",
            tf="5",
            price=2650.50,
            direction="BUY",
            alignment="5/1"
        )
        assert alert1.bull_count == 5
        assert alert1.bear_count == 1
        
        # Test default alignment
        alert2 = ZepixV6Alert(
            type="BULLISH_ENTRY",
            ticker="XAUUSD",
            tf="5",
            price=2650.50,
            direction="BUY"
            # alignment defaults to "0/0"
        )
        assert alert2.alignment == "0/0"
        assert alert2.bull_count == 0
        assert alert2.bear_count == 0


class TestV6PluginAlignmentLogic:
    """Test V6 plugin alignment validation logic"""
    
    def test_5m_alignment_threshold(self):
        """5M plugin requires bull_count >= 3 for BUY"""
        # Threshold for 5M is 3
        threshold = 3
        
        # Test cases
        test_cases = [
            ("3/0", "BUY", True),   # Exactly 3 - should pass
            ("4/0", "BUY", True),   # More than 3 - should pass
            ("2/1", "BUY", False),  # Less than 3 - should fail
            ("0/3", "SELL", True),  # Exactly 3 bearish - should pass
            ("0/4", "SELL", True),  # More than 3 bearish - should pass
            ("1/2", "SELL", False), # Less than 3 bearish - should fail
        ]
        
        for alignment, direction, expected in test_cases:
            alert = ZepixV6Alert(
                type=f"{'BULLISH' if direction == 'BUY' else 'BEARISH'}_ENTRY",
                ticker="XAUUSD",
                tf="5",
                price=2650.50,
                direction=direction,
                alignment=alignment
            )
            
            bull_count, bear_count = alert.get_pulse_counts()
            
            if direction == "BUY":
                is_aligned = bull_count >= threshold
            else:
                is_aligned = bear_count >= threshold
            
            assert is_aligned == expected, \
                f"5M: alignment={alignment}, direction={direction}, expected={expected}, got={is_aligned}"
    
    def test_1h_alignment_threshold(self):
        """1H plugin requires bull_count >= 4 for BUY (higher threshold)"""
        # Threshold for 1H is 4
        threshold = 4
        
        # Test cases
        test_cases = [
            ("4/0", "BUY", True),   # Exactly 4 - should pass
            ("5/0", "BUY", True),   # More than 4 - should pass
            ("3/1", "BUY", False),  # Less than 4 - should fail
            ("0/4", "SELL", True),  # Exactly 4 bearish - should pass
            ("0/5", "SELL", True),  # More than 4 bearish - should pass
            ("1/3", "SELL", False), # Less than 4 bearish - should fail
        ]
        
        for alignment, direction, expected in test_cases:
            alert = ZepixV6Alert(
                type=f"{'BULLISH' if direction == 'BUY' else 'BEARISH'}_ENTRY",
                ticker="XAUUSD",
                tf="60",
                price=2650.50,
                direction=direction,
                alignment=alignment
            )
            
            bull_count, bear_count = alert.get_pulse_counts()
            
            if direction == "BUY":
                is_aligned = bull_count >= threshold
            else:
                is_aligned = bear_count >= threshold
            
            assert is_aligned == expected, \
                f"1H: alignment={alignment}, direction={direction}, expected={expected}, got={is_aligned}"


class TestPineScriptSupremacy:
    """Test that Pine Script Supremacy principle is enforced"""
    
    def test_no_trendmanager_in_5m_validate_entry(self):
        """Verify 5M plugin doesn't call TrendManager for fresh entry"""
        plugin_path = project_root / "Trading_Bot/src/logic_plugins/v6_price_action_5m/plugin.py"
        content = plugin_path.read_text()
        
        # Check _validate_entry method doesn't call check_pulse_alignment
        assert "check_pulse_alignment" not in content or \
               "service_api.check_pulse_alignment" not in content, \
               "5M plugin should not call check_pulse_alignment in _validate_entry"
        
        # Verify it uses alert.alignment instead
        assert "alert.get_pulse_counts()" in content or "alert.alignment" in content, \
               "5M plugin should use alert.alignment for validation"
    
    def test_no_trendmanager_in_15m_validate_entry(self):
        """Verify 15M plugin doesn't call TrendManager for fresh entry"""
        plugin_path = project_root / "Trading_Bot/src/logic_plugins/v6_price_action_15m/plugin.py"
        content = plugin_path.read_text()
        
        # Check _validate_entry method doesn't call check_pulse_alignment
        assert "check_pulse_alignment" not in content or \
               "service_api.check_pulse_alignment" not in content, \
               "15M plugin should not call check_pulse_alignment in _validate_entry"
        
        # Verify it uses alert.alignment instead
        assert "alert.get_pulse_counts()" in content or "alert.alignment" in content, \
               "15M plugin should use alert.alignment for validation"
    
    def test_no_trendmanager_in_1h_validate_entry(self):
        """Verify 1H plugin doesn't call TrendManager for fresh entry"""
        plugin_path = project_root / "Trading_Bot/src/logic_plugins/v6_price_action_1h/plugin.py"
        content = plugin_path.read_text()
        
        # Check _validate_entry method doesn't call check_timeframe_alignment
        assert "check_timeframe_alignment" not in content or \
               "service_api.check_timeframe_alignment" not in content, \
               "1H plugin should not call check_timeframe_alignment in _validate_entry"
        
        # Verify it uses alert.alignment instead
        assert "alert.get_pulse_counts()" in content or "alert.alignment" in content, \
               "1H plugin should use alert.alignment for validation"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
