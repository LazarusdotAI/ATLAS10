#!/usr/bin/env python3
"""
A.T.L.A.S. Guru Scoring Metrics
New profit-focused scoring system for Stock Market Guru persona
Replaces Ed/Comp scores with profit-focused metrics
"""

import re
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class GuruScoreResult:
    """Result of guru scoring evaluation"""
    profit_potential_score: float  # PPS: 0-10
    execution_confidence: float    # EC: 0-5
    strategy_sophistication: float # SS: 0-5
    overall_score: float
    feedback: str

class ATLASGuruScoringMetrics:
    """
    Profit-focused scoring system for Stock Market Guru persona
    
    Metrics:
    - Profit Potential Score (PPS: 0-10): Clarity of profit pathway and expected returns
    - Execution Confidence (EC: 0-5): Trade readiness and signal strength
    - Strategy Sophistication (SS: 0-5): Advanced analysis and edge identification
    """
    
    def __init__(self):
        # Profit potential indicators
        self.profit_indicators = [
            r'\$\d+', r'profit', r'target', r'gain', r'return',
            r'entry', r'exit', r'stop', r'risk/reward'
        ]
        
        # Execution confidence indicators
        self.execution_indicators = [
            r'confidence', r'probability', r'[STAR]', r'ready',
            r'execute', r'plan #', r'confirm', r'immediate'
        ]
        
        # Strategy sophistication indicators
        self.sophistication_indicators = [
            r'ttm squeeze', r'momentum', r'institutional',
            r'volume', r'technical', r'pattern', r'algorithm',
            r'multi-timeframe', r'correlation', r'volatility'
        ]
    
    def score_guru_response(self, message: str, response: str) -> GuruScoreResult:
        """Score response using guru-focused metrics"""
        
        # Calculate individual scores
        pps = self._calculate_profit_potential_score(response)
        ec = self._calculate_execution_confidence(response)
        ss = self._calculate_strategy_sophistication(response)
        
        # Calculate overall score (weighted average)
        overall = (pps * 0.5) + (ec * 2.0) + (ss * 2.0)  # Max = 10
        
        # Generate feedback
        feedback = self._generate_guru_feedback(pps, ec, ss, response)
        
        return GuruScoreResult(
            profit_potential_score=pps,
            execution_confidence=ec,
            strategy_sophistication=ss,
            overall_score=overall,
            feedback=feedback
        )
    
    def _calculate_profit_potential_score(self, response: str) -> float:
        """Calculate Profit Potential Score (PPS: 0-10)"""
        score = 0.0
        response_lower = response.lower()
        
        # Specific profit amounts (+3 points)
        if re.search(r'\$\d+', response):
            score += 3.0
        
        # Profit percentages (+2 points)
        if re.search(r'\d+%', response):
            score += 2.0
        
        # Entry/target/stop prices (+2 points)
        if all(term in response_lower for term in ['entry', 'target', 'stop']):
            score += 2.0
        
        # Risk/reward ratio (+2 points)
        if 'risk/reward' in response_lower or 'r:r' in response_lower:
            score += 2.0
        
        # Timeframe specified (+1 point)
        if any(term in response_lower for term in ['days', 'weeks', 'today', 'tomorrow']):
            score += 1.0
        
        return min(score, 10.0)
    
    def _calculate_execution_confidence(self, response: str) -> float:
        """Calculate Execution Confidence (EC: 0-5)"""
        score = 0.0
        response_lower = response.lower()
        
        # Confidence percentage (+2 points)
        if re.search(r'\d+%.*confidence', response_lower):
            score += 2.0
        
        # Star ratings (+1 point)
        star_count = response.count('[STAR]')
        if star_count >= 4:
            score += 1.0
        
        # Trade plan ID (+1 point)
        if re.search(r'plan #[A-Z0-9]+', response):
            score += 1.0
        
        # Execution readiness (+1 point)
        if any(term in response_lower for term in ['ready', 'execute', 'confirm']):
            score += 1.0
        
        return min(score, 5.0)
    
    def _calculate_strategy_sophistication(self, response: str) -> float:
        """Calculate Strategy Sophistication (SS: 0-5)"""
        score = 0.0
        response_lower = response.lower()
        
        # Technical analysis terms (+1 point each, max 3)
        technical_terms = ['ttm squeeze', 'momentum', 'volume', 'rsi', 'macd']
        technical_count = sum(1 for term in technical_terms if term in response_lower)
        score += min(technical_count, 3.0)
        
        # Institutional intelligence (+1 point)
        if any(term in response_lower for term in ['institutional', 'smart money', 'flow']):
            score += 1.0
        
        # Multi-timeframe analysis (+1 point)
        if any(term in response_lower for term in ['timeframe', 'daily', 'weekly']):
            score += 1.0
        
        return min(score, 5.0)
    
    def _generate_guru_feedback(self, pps: float, ec: float, ss: float, response: str) -> str:
        """Generate feedback for guru response"""
        feedback_parts = []
        
        # Profit Potential feedback
        if pps >= 8.0:
            feedback_parts.append("Excellent profit clarity with specific targets")
        elif pps >= 6.0:
            feedback_parts.append("Good profit pathway, could be more specific")
        else:
            feedback_parts.append("Needs clearer profit targets and risk parameters")
        
        # Execution Confidence feedback
        if ec >= 4.0:
            feedback_parts.append("High execution confidence with clear signals")
        elif ec >= 3.0:
            feedback_parts.append("Moderate confidence, strengthen conviction")
        else:
            feedback_parts.append("Low execution confidence, needs stronger signals")
        
        # Strategy Sophistication feedback
        if ss >= 4.0:
            feedback_parts.append("Sophisticated analysis with institutional edge")
        elif ss >= 3.0:
            feedback_parts.append("Good technical analysis, add more depth")
        else:
            feedback_parts.append("Basic analysis, needs advanced techniques")
        
        return " | ".join(feedback_parts)
    
    def is_guru_success(self, score_result: GuruScoreResult) -> bool:
        """Determine if response meets guru success criteria"""
        return (
            score_result.profit_potential_score >= 7.0 and
            score_result.execution_confidence >= 3.0 and
            score_result.strategy_sophistication >= 3.0 and
            score_result.overall_score >= 7.0
        )
    
    def get_score_summary(self, score_result: GuruScoreResult) -> str:
        """Get formatted score summary"""
        return f"""Guru Scores:
PPS: {score_result.profit_potential_score:.1f}/10 | EC: {score_result.execution_confidence:.1f}/5 | SS: {score_result.strategy_sophistication:.1f}/5
Overall: {score_result.overall_score:.1f}/10
Success: {'[OK]' if self.is_guru_success(score_result) else '[ERROR]'}
Feedback: {score_result.feedback}"""

# Example usage and testing
if __name__ == "__main__":
    scorer = ATLASGuruScoringMetrics()
    
    # Test guru response
    test_response = """[TARGET] **PROFIT OPPORTUNITY IDENTIFIED**

**Target**: $200 profit in 3 days

**Trade Plan #ABC123**: BUY 10 shares AAPL
• **Entry**: $175.25
• **Target**: $180.50 (+3.0%)
• **Stop Loss**: $170.00 (-3.0%)
• **Risk/Reward**: 1:1.5
• **Confidence**: 94.2% [STAR][STAR][STAR][STAR][STAR]

[FAST] **EXECUTION READY**
Reply "confirm ABC123" to place live order

[IDEA] **Market Intelligence**: TTM Squeeze pattern detected with institutional volume confirmation."""
    
    result = scorer.score_guru_response("I want to make $200 in 3 days", test_response)
    print(scorer.get_score_summary(result))
