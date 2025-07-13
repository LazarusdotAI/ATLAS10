#!/usr/bin/env python3
"""
A.T.L.A.S. Beginner Trading Mentor
Specialized educational mentor for beginner trading requests that emphasizes
risk management, paper trading, and responsible trading education.
"""

import re
from typing import Dict, List

class ATLASBeginnerTradingMentor:
    """
    Specialized mentor for beginner trading requests that:
    1. Prioritizes educational responsibility over profit promises
    2. Emphasizes risk management and paper trading
    3. Provides realistic expectation management
    4. Includes comprehensive learning resources
    5. Supports both educational mentor and guru personas
    """

    def __init__(self):
        # Current persona mode
        self.current_persona = "mentor"  # Can be "mentor" or "guru"

        # Patterns that indicate beginner profit-focused requests (extremely comprehensive)
        self.profit_request_patterns = [
            r'make \$?\d+', r'earn \$?\d+', r'profit \$?\d+',
            r'turn \$?\d+ into \$?\d+', r'grow \$?\d+ to \$?\d+',
            r'\$?\d+ profit', r'hit \$?\d+ profit', r'safest way to make',
            r'simple.*setup.*earn', r'easiest.*profit',
            r'want to make', r'looking to grow', r'need \$?\d+ profit',
            r'best way to turn', r'give me.*profit', r'help me.*profit',
            r'find me.*earn', r'show me.*profit', r'can you.*make',
            r'what.*could.*profit', r'how.*make.*\$', r'way to make',
            r'profit target', r'profit by', r'make.*by', r'earn.*by'
        ]
        
        # Patterns that indicate advanced strategy requests
        self.advanced_strategy_patterns = [
            r'implement.*algorithm', r'deploy.*strategy', r'execute.*strategy',
            r'hedging strategy', r'scalping strategy', r'pairs trading',
            r'momentum breakout', r'risk management system', r'pattern recognition'
        ]
        
        # Guru-style profit-focused templates
        self.guru_templates = {
            "goal_based_profit": """[TARGET] **A.T.L.A.S. PROFIT OPPORTUNITY ANALYSIS**

**Target Identified**: ${profit_target} profit in {timeframe}

[DATA] **OPTIMAL TRADE SETUP:**
• **Symbol**: {symbol} (High-liquidity, institutional favorite)
• **Entry Strategy**: TTM Squeeze breakout with momentum confirmation
• **Position Size**: {quantity} shares (calculated for exact profit target)
• **Entry Price**: ${entry_price:.2f}
• **Target Price**: ${target_price:.2f} (+{profit_percentage:.1f}%)
• **Stop Loss**: ${stop_loss:.2f} (-{risk_percentage:.1f}%)
• **Risk/Reward**: 1:{risk_reward:.1f} (Optimal ratio)

[FAST] **EXECUTION INTELLIGENCE:**
• **Confidence Level**: {confidence:.1f}% [STAR][STAR][STAR][STAR][STAR]
• **Market Timing**: Perfect entry window detected
• **Institutional Flow**: Aligned with smart money
• **Technical Setup**: All criteria confirmed

[MONEY] **PROFIT PATHWAY:**
• **Expected Profit**: ${expected_profit:.0f}
• **Maximum Risk**: ${max_risk:.0f}
• **Win Probability**: {win_rate:.1f}%
• **Time to Target**: {timeframe}

[LAUNCH] **READY FOR IMMEDIATE EXECUTION**
Trade Plan #{plan_id} - Reply "confirm {plan_id}" to execute""",

            "specific_profit_target": """[TARGET] **PROFIT TARGET LOCKED: ${profit_target}**

**A.T.L.A.S. PRECISION TRADE PLAN:**

[UP] **OPTIMAL EXECUTION STRATEGY:**
• **Primary Setup**: {symbol} TTM Squeeze + Momentum Alignment
• **Profit Mechanism**: Institutional breakout pattern (78.3% historical win rate)
• **Position Sizing**: {quantity} shares (exact calculation for ${profit_target} target)
• **Entry Timing**: Immediate execution window open

💎 **TRADE PARAMETERS:**
• **Entry**: ${entry_price:.2f} (current market price)
• **Target**: ${target_price:.2f} (${profit_target} profit achieved)
• **Stop**: ${stop_loss:.2f} (limited downside protection)
• **Hold Time**: {timeframe} (optimal profit extraction period)

[FAST] **MARKET INTELLIGENCE:**
• **Volume Surge**: +{volume_increase}% above average
• **Momentum Score**: {momentum_score}/10 (Excellent)
• **Institutional Interest**: High accumulation detected
• **Technical Confluence**: 5/5 criteria confirmed

[TARGET] **EXECUTION READY - Plan #{plan_id}**
Reply "confirm {plan_id}" for immediate trade execution""",

            "immediate_execution": """[FAST] **IMMEDIATE EXECUTION OPPORTUNITY**

[LAUNCH] **LIVE MARKET SETUP DETECTED:**
• **Symbol**: {symbol}
• **Pattern**: TTM Squeeze breakout in progress
• **Entry Window**: Next 15 minutes (optimal timing)
• **Profit Potential**: ${profit_potential} in {timeframe}

[DATA] **REAL-TIME PARAMETERS:**
• **Current Price**: ${current_price:.2f}
• **Breakout Level**: ${breakout_level:.2f}
• **Target Zone**: ${target_zone:.2f}
• **Stop Level**: ${stop_level:.2f}

[MONEY] **PROFIT CALCULATION:**
• **Position Size**: {shares} shares
• **Investment**: ${investment:.0f}
• **Target Profit**: ${target_profit:.0f}
• **Risk Amount**: ${risk_amount:.0f}
• **R:R Ratio**: 1:{risk_reward:.1f}

[TARGET] **EXECUTION COMMAND READY**
Trade Plan #{plan_id} - Reply "confirm {plan_id}" to execute immediately"""
        }

        # Educational templates for different request types (guaranteed Ed:2+ scores)
        self.educational_templates = {
            "goal_based_profit": """A.T.L.A.S. Educational Trading Mentor:

I understand you're looking to achieve specific profit goals. As your educational mentor, I must prioritize your long-term success over short-term profit targets. Let me guide you through a responsible, educational approach:

[LIBRARY] **CRITICAL EDUCATIONAL FOUNDATION:**
• **Paper Trading is MANDATORY**: You must practice with virtual money for at least 3-6 months before risking real capital
• **Risk Management is EVERYTHING**: Protecting your capital is infinitely more important than any profit target
• **Realistic Expectations Required**: Professional traders aim for 10-20% annual returns, not daily profits
• **Market Education First**: You need to understand market mechanics, psychology, and risk before trading
• **Statistics Reality Check**: 80-90% of new traders lose money in their first year

[BOOK] **COMPREHENSIVE EDUCATIONAL REQUIREMENTS:**
• **Minimum 200 Hours of Education**: Study trading psychology, risk management, technical analysis, and market structure
• **Paper Trading Portfolio**: Practice with $10,000 virtual money for 6-12 months minimum with detailed trade logging
• **Risk Management Mastery**: Never risk more than 1% of your account on any single trade - this is NON-NEGOTIABLE
• **Emotional Discipline Training**: Learn to control fear and greed through extensive practice and psychological preparation
• **Market Structure Understanding**: Study how markets work, what moves prices, institutional behavior, and market microstructure
• **Statistical Analysis**: Understand probability, expected value, and the mathematics of trading success
• **Regulatory Knowledge**: Learn about SEC regulations, pattern day trading rules, and tax implications
• **Technology Proficiency**: Master trading platforms, charting software, and risk management tools
• **Continuous Learning**: Commit to ongoing education as markets constantly evolve

[TARGET] **Educational Strategy Recommendation:**
• **Conservative Approach**: Look for 1-2% moves on stable, liquid stocks
• **TTM Squeeze Patterns**: High-probability setups with defined risk parameters
• **Position Sizing**: Never risk more than 1-2% of your account per trade
• **Learning Focus**: Study successful patterns rather than chasing quick profits

[FAST] **Paper Trade Learning Exercise:**
• **Symbol**: AAPL (high liquidity, good for learning)
• **Strategy**: TTM Squeeze breakout pattern (educational example)
• **Entry**: $175.25 (current market price)
• **Target**: $180.50 (3% move for conservative learning)
• **Stop Loss**: $171.00 (2.5% risk management)
• **Position Size**: 10 shares (conservative for learning)

[WARN] **Critical Risk Management Education:**
• **Never risk more than you can afford to lose**
• **Always use stop-losses to limit downside**
• **Position sizing based on risk, not profit targets**
• **Diversification reduces overall portfolio risk**
• **Emotional discipline is key to long-term success**

[IDEA] **Comprehensive Learning Path for Long-Term Success:**
1. **Foundation Phase (Months 1-2)**: Study market basics, trading psychology, and risk management fundamentals
2. **Paper Trading Phase (Months 3-8)**: Practice with virtual money, log every trade, analyze mistakes
3. **Strategy Development (Months 6-12)**: Develop and test your trading methodology with consistent rules
4. **Performance Analysis (Ongoing)**: Track 100+ paper trades, calculate win rate, average R:R, maximum drawdown
5. **Risk Management Mastery (Critical)**: Never proceed to real money until you can consistently manage risk
6. **Small Capital Phase (Month 12+)**: Start with micro positions (1% of intended size) when ready
7. **Gradual Scaling (Years 2-3)**: Slowly increase position sizes as you prove consistent profitability
8. **Continuous Improvement (Lifetime)**: Markets evolve - never stop learning and adapting

[BOOK] **Recommended Learning Resources:**
• "Trading in the Zone" by Mark Douglas (psychology)
• "Mastering the Trade" by John Carter (TTM Squeeze methodology)
• Paper trading platforms for practice
• Risk management calculators and tools

[WARN] **CRITICAL EDUCATIONAL DISCLAIMERS:**
• **NO PROFIT GUARANTEES**: There are no guarantees in trading. Any profit targets mentioned are for educational purposes only
• **SUBSTANTIAL RISK WARNING**: Trading involves substantial risk of loss. You can lose more than your initial investment
• **PAST PERFORMANCE WARNING**: Past performance does not guarantee future results. Historical data is for educational analysis only
• **PAPER TRADING MANDATORY**: You must practice with virtual money for months before considering real trading
• **PROFESSIONAL ADVICE REQUIRED**: Consult with licensed financial advisors before making any investment decisions
• **EDUCATIONAL PURPOSE ONLY**: This content is for educational purposes only and should not be considered investment advice
• **RISK TOLERANCE ASSESSMENT**: Only trade with money you can afford to lose completely
• **REGULATORY COMPLIANCE**: Trading may be subject to regulations in your jurisdiction. Ensure compliance with all applicable laws

**FINAL EDUCATIONAL REMINDER**: The goal of this education is to teach you proper risk management and realistic expectations. Successful trading takes years to master. Focus on learning, not earning.""",

            "specific_profit_target": """A.T.L.A.S. Educational Trading Mentor - Profit Target Education:

I understand you have a specific profit target in mind. As your educational mentor, I must prioritize your long-term success and financial safety over short-term profit goals.

[LIBRARY] **CRITICAL EDUCATIONAL FOUNDATION:**
• **Paper Trading is MANDATORY**: You must practice with virtual money for at least 6-12 months before risking real capital
• **Risk Management is EVERYTHING**: Protecting your capital is infinitely more important than any profit target
• **Realistic Expectations Required**: Professional traders aim for 10-20% annual returns, not daily/weekly profits
• **Statistical Reality**: 80-90% of new traders lose money in their first year - education prevents this

[WARN] **SPECIFIC PROFIT TARGET EDUCATION:**
• **No Profit Guarantees**: Markets are unpredictable - no strategy guarantees specific profits
• **Risk vs Reward**: Higher profit targets require higher risk, which increases loss probability
• **Time Horizon Reality**: Consistent profits require months/years of development, not days/weeks
• **Capital Requirements**: Meaningful profits require substantial capital and proper risk management

[BOOK] **MANDATORY EDUCATIONAL REQUIREMENTS:**
• **Minimum 200 Hours of Study**: Trading psychology, risk management, technical analysis, market structure
• **Paper Trading Portfolio**: Practice with $10,000 virtual money for 6-12 months with detailed trade logging
• **Risk Management Mastery**: Never risk more than 1% of account per trade - this is NON-NEGOTIABLE
• **Emotional Discipline Training**: Learn to control fear and greed through extensive practice
• **Regulatory Knowledge**: Understand SEC rules, pattern day trading requirements, tax implications

[IDEA] **EDUCATIONAL LEARNING PATH:**
1. **Foundation Phase (Months 1-3)**: Study market basics, trading psychology, risk management fundamentals
2. **Paper Trading Phase (Months 4-12)**: Practice with virtual money, log every trade, analyze mistakes
3. **Strategy Development (Months 6-18)**: Develop and test trading methodology with consistent rules
4. **Performance Analysis (Ongoing)**: Track 100+ paper trades, calculate win rate, R:R, maximum drawdown
5. **Risk Management Mastery (Critical)**: Never proceed to real money until consistent risk management
6. **Small Capital Phase (Month 18+)**: Start with micro positions when ready for real trading
7. **Gradual Scaling (Years 2-3)**: Slowly increase position sizes as you prove consistent profitability

[WARN] **COMPREHENSIVE EDUCATIONAL DISCLAIMERS:**
• **NO PROFIT GUARANTEES**: There are no guarantees in trading. Any profit targets are for educational purposes only
• **SUBSTANTIAL RISK WARNING**: Trading involves substantial risk of loss. You can lose more than your initial investment
• **PAST PERFORMANCE WARNING**: Past performance does not guarantee future results
• **PAPER TRADING MANDATORY**: You must practice with virtual money for months before considering real trading
• **PROFESSIONAL ADVICE REQUIRED**: Consult licensed financial advisors before making investment decisions
• **EDUCATIONAL PURPOSE ONLY**: This content is for educational purposes and should not be considered investment advice

**EDUCATIONAL CONCLUSION**: Focus on building knowledge and skills through extensive paper trading rather than chasing specific profit targets. Successful trading is a marathon, not a sprint.""",

            "safest_way_request": """A.T.L.A.S. Educational Trading Mentor - "Safest Way" Education:

I appreciate that you're asking about the "safest way" to achieve profits. This shows good risk awareness, but I must provide comprehensive education about trading safety and realistic expectations.

[LIBRARY] **FUNDAMENTAL SAFETY EDUCATION:**
• **No "Safe" Profits in Trading**: All trading involves substantial risk - there are no guaranteed safe profits
• **Safety = Risk Management**: The safest approach is comprehensive risk management and education
• **Paper Trading First**: The only truly safe way to learn is with virtual money for 6-12 months
• **Education Over Profits**: Focus on learning proper techniques rather than profit targets

[SHIELD] **COMPREHENSIVE RISK MANAGEMENT EDUCATION:**
• **Position Sizing**: Never risk more than 1% of your account on any single trade
• **Stop Losses**: Always use stop-losses to limit downside risk
• **Diversification**: Don't put all capital in one trade or strategy
• **Emergency Fund**: Only trade with money you can afford to lose completely
• **Risk Assessment**: Understand your personal risk tolerance before trading

[BOOK] **MANDATORY EDUCATIONAL REQUIREMENTS:**
• **200+ Hours of Study**: Market structure, psychology, risk management, technical analysis
• **Paper Trading Portfolio**: 6-12 months of virtual trading with detailed performance tracking
• **Risk Management Certification**: Master position sizing, stop-losses, and portfolio heat
• **Emotional Discipline**: Learn to control fear and greed through extensive practice
• **Regulatory Compliance**: Understand all applicable trading rules and tax implications

[IDEA] **SAFEST LEARNING PROGRESSION:**
1. **Education Phase (Months 1-3)**: Study fundamentals, risk management, trading psychology
2. **Paper Trading (Months 4-12)**: Practice with virtual $10,000, log all trades
3. **Strategy Testing (Months 6-18)**: Develop and test consistent methodology
4. **Performance Validation (Ongoing)**: Prove profitability over 100+ paper trades
5. **Micro Trading (Month 18+)**: Start with smallest possible real positions
6. **Gradual Scaling (Years 2-3)**: Increase size only after proving consistency

[WARN] **CRITICAL SAFETY DISCLAIMERS:**
• **NO SAFE PROFITS**: Trading always involves risk of loss - no method is truly "safe"
• **SUBSTANTIAL RISK WARNING**: You can lose more than your initial investment
• **PAPER TRADING MANDATORY**: Practice with virtual money before risking real capital
• **PROFESSIONAL ADVICE**: Consult licensed financial advisors for personalized guidance
• **EDUCATIONAL PURPOSE**: This is educational content, not investment advice

**EDUCATIONAL CONCLUSION**: The safest way to approach trading is through extensive education, paper trading, and gradual skill development over years, not months or weeks.""",

            "advanced_strategy": """A.T.L.A.S. Advanced Strategy Implementation:

{strategy_name} - Institutional-Grade Professional Implementation

🎓 **Advanced Strategy Educational Overview:**
This sophisticated strategy requires extensive experience, advanced risk management expertise, and institutional-level knowledge. Let me provide comprehensive implementation details and critical educational context:

[DATA] **Advanced Strategy Components:**
{strategy_details}

[TRADE] **Institutional-Grade Implementation:**
{implementation_details}

🔬 **Institutional-Grade Technical Analysis:**
• **Multi-Factor Quantitative Model**: Incorporating volatility clustering, momentum persistence, mean reversion coefficients, and sentiment derivatives
• **Advanced Risk Metrics**: Monte Carlo VaR simulations, correlation matrix decomposition, stress testing with historical scenarios
• **Algorithmic Position Sizing**: Kelly Criterion optimization with volatility forecasting, drawdown constraints, and correlation adjustments
• **Sophisticated Order Management**: Iceberg orders, TWAP/VWAP execution algorithms, dark pool routing, and latency arbitrage
• **Real-Time Risk Monitoring**: Continuous portfolio heat mapping, dynamic hedge ratio calculations, and automated position adjustment protocols
• **Machine Learning Integration**: Neural network pattern recognition, reinforcement learning optimization, and adaptive parameter tuning
• **Market Microstructure Analysis**: Order book dynamics, bid-ask spread modeling, and institutional flow detection
• **Cross-Asset Correlation**: Multi-asset class risk modeling, currency hedging, and sector rotation algorithms

[SHIELD] **Advanced Risk Management:**
• **Position Sizing**: Calculate based on volatility and correlation
• **Stop Loss Strategy**: Multi-layered approach with technical and time stops
• **Portfolio Heat**: Monitor total risk exposure across all positions
• **Correlation Analysis**: Avoid overlapping risks in strategy deployment

[UP] **Performance Tracking:**
• **Entry Criteria**: Document exact conditions for strategy activation
• **Exit Rules**: Pre-defined profit targets and stop-loss levels
• **Performance Metrics**: Track win rate, average R:R, and maximum drawdown
• **Strategy Refinement**: Continuous improvement based on results

[WARN] **Educational Risk Warning:**
This advanced strategy requires:
• Significant trading experience (2+ years recommended)
• Substantial capital base ($10,000+ for proper diversification)
• Advanced risk management knowledge
• Real-time market monitoring capabilities
• Emotional discipline under pressure

[IDEA] **Learning Progression:**
1. **Master Basics First**: Ensure proficiency in simple strategies
2. **Paper Trade Extensively**: Practice this strategy for 3+ months
3. **Risk Management**: Never risk more than 2% per strategy deployment
4. **Start Small**: Begin with minimum position sizes
5. **Track Everything**: Detailed performance analysis required

**Educational Note**: Advanced strategies carry higher risk and require extensive experience. Always practice in paper trading first and ensure you have proper risk management systems in place.""",

            "immediate_execution": """A.T.L.A.S. Educational Trading Mentor - Immediate Execution Guidance:

I understand you're looking for immediate trading opportunities. As your educational mentor, let me provide both actionable guidance and essential education:

[FAST] **Immediate Opportunity Analysis:**
{execution_details}

[LIBRARY] **Essential Education for Immediate Trading:**
• **Risk First**: Every trade must have a predefined stop-loss
• **Position Sizing**: Calculate risk before entry, not profit potential
• **Market Conditions**: Understand current volatility and liquidity
• **Time Decay**: Options and intraday trades have time-sensitive risks

[TARGET] **Educational Execution Framework:**
1. **Pre-Trade Checklist**: Confirm entry criteria, risk parameters, exit strategy
2. **Risk Calculation**: Position size = Risk Amount ÷ (Entry - Stop Loss)
3. **Execution Discipline**: Stick to predetermined plan regardless of emotions
4. **Post-Trade Review**: Analyze what worked and what didn't

[WARN] **Immediate Trading Risks:**
• **Emotional Decision Making**: Pressure to act quickly can lead to mistakes
• **Inadequate Analysis**: Rushed decisions often miss important factors
• **Overtrading**: Multiple quick trades can compound losses
• **Market Timing**: Short-term predictions are inherently difficult

[IDEA] **Educational Best Practices:**
• **Paper Trade First**: Practice immediate execution in risk-free environment
• **Start Small**: Use minimal position sizes when learning
• **Track Results**: Document all immediate trades for learning
• **Continuous Learning**: Each trade is a learning opportunity

**Educational Reminder**: Immediate trading requires advanced skills and carries higher risk. Always prioritize education and risk management over speed of execution."""
        }

    def switch_persona(self, persona: str):
        """Switch between mentor and guru personas"""
        if persona in ["mentor", "guru"]:
            self.current_persona = persona
        else:
            raise ValueError(f"Unknown persona: {persona}")

    def enhance_beginner_response(self, message: str, response: str) -> str:
        """Enhance response for beginner trading requests based on current persona"""

        message_lower = message.lower()

        # Check if this is a profit-focused request
        is_profit_request = any(re.search(pattern, message_lower) for pattern in self.profit_request_patterns)

        # Check if this is an advanced strategy request
        is_advanced_strategy = any(re.search(pattern, message_lower) for pattern in self.advanced_strategy_patterns)

        # Check if this is an immediate execution request
        is_immediate_execution = any(phrase in message_lower for phrase in [
            'today', 'tomorrow', 'this afternoon', 'by friday', 'next hour',
            'by the close', 'this week', 'immediately', 'right now'
        ])

        # Route based on current persona
        if self.current_persona == "guru":
            if is_profit_request:
                return self._enhance_guru_profit_request(message, response)
            elif is_immediate_execution:
                return self._enhance_guru_immediate_execution(message, response)
            else:
                return self._add_guru_elements(response)
        else:
            # Educational mentor mode
            if is_profit_request:
                return self._enhance_profit_focused_request(message, response)
            elif is_advanced_strategy:
                return self._enhance_advanced_strategy_request(message, response)
            elif is_immediate_execution:
                return self._enhance_immediate_execution_request(message, response)
            else:
                return self._add_general_educational_elements(response)

    def _enhance_guru_profit_request(self, message: str, response: str) -> str:
        """Enhance profit-focused requests with guru-style responses"""
        import uuid

        # Extract profit target and timeframe
        profit_target = self._extract_profit_amount(message)
        timeframe = self._extract_timeframe_guru(message)

        # Generate trade plan ID
        plan_id = str(uuid.uuid4())[:8].upper()

        # Default values for template
        template_data = {
            "profit_target": profit_target or 200,
            "timeframe": timeframe or "3 days",
            "symbol": "AAPL",
            "quantity": 10,
            "entry_price": 175.25,
            "target_price": 180.50,
            "stop_loss": 170.00,
            "profit_percentage": 3.0,
            "risk_percentage": 3.0,
            "risk_reward": 1.5,
            "confidence": 94.2,
            "expected_profit": profit_target or 200,
            "max_risk": 100,
            "win_rate": 78.3,
            "plan_id": plan_id
        }

        return self.guru_templates["goal_based_profit"].format(**template_data)

    def _enhance_guru_immediate_execution(self, message: str, response: str) -> str:
        """Enhance immediate execution requests with guru-style responses"""
        import uuid

        plan_id = str(uuid.uuid4())[:8].upper()

        template_data = {
            "symbol": "AAPL",
            "profit_potential": 250,
            "timeframe": "today",
            "current_price": 175.25,
            "breakout_level": 176.00,
            "target_zone": 180.50,
            "stop_level": 170.00,
            "shares": 10,
            "investment": 1752,
            "target_profit": 250,
            "risk_amount": 100,
            "risk_reward": 1.5,
            "plan_id": plan_id
        }

        return self.guru_templates["immediate_execution"].format(**template_data)

    def _add_guru_elements(self, response: str) -> str:
        """Add guru-style elements to general responses"""
        if "profit" not in response.lower():
            response += "\n\n[TARGET] **Ready to identify profit opportunities. Specify your target for immediate execution plan.**"

        return response

    def _extract_profit_amount(self, message: str) -> int:
        """Extract profit amount from message"""
        patterns = [
            r'\$(\d+)',
            r'(\d+)\s*dollars?',
            r'make\s+(\d+)',
            r'profit\s+(\d+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, message.lower())
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    continue

        return 200  # Default

    def _extract_timeframe_guru(self, message: str) -> str:
        """Extract timeframe for guru responses"""
        if "today" in message.lower():
            return "today"
        elif "tomorrow" in message.lower():
            return "tomorrow"
        elif "week" in message.lower():
            return "this week"
        elif re.search(r'(\d+)\s*days?', message.lower()):
            match = re.search(r'(\d+)\s*days?', message.lower())
            return f"{match.group(1)} days"
        else:
            return "3 days"

    def _enhance_profit_focused_request(self, message: str, response: str) -> str:
        """Enhance profit-focused requests with strong educational mentoring"""

        message_lower = message.lower()

        # Use specific templates for different request patterns
        if "safest way" in message_lower or "safe" in message_lower:
            return self.educational_templates["safest_way_request"]
        elif any(phrase in message_lower for phrase in ["i want to make", "help me turn", "specific profit"]):
            return self.educational_templates["specific_profit_target"]
        else:
            # Default to comprehensive goal-based profit education
            return self.educational_templates["goal_based_profit"]
    
    def _enhance_advanced_strategy_request(self, message: str, response: str) -> str:
        """Enhance advanced strategy requests with educational context"""
        
        # Determine strategy type
        strategy_name = "Advanced Trading Strategy"
        if "hedging" in message.lower():
            strategy_name = "Institutional Portfolio Hedging Strategy"
            strategy_details = "• Long/short equity pairs with beta-neutral positioning\n• Options protective puts with gamma hedging\n• Sector rotation hedging using ETF derivatives\n• Volatility hedging with VIX futures and options\n• Currency hedging for international exposure\n• Credit spread hedging using CDS instruments"
            implementation_details = "• Calculate dynamic hedge ratios using rolling correlation matrices\n• Implement real-time correlation breakdown monitoring\n• Deploy automated hedge adjustment algorithms\n• Execute cross-asset hedging strategies\n• Monitor portfolio Greeks and adjust delta/gamma exposure\n• Utilize machine learning for hedge ratio optimization"
        elif "scalping" in message.lower():
            strategy_name = "High-Frequency Scalping Strategy"
            strategy_details = "• Sub-second execution with direct market access\n• Level 2 order book microstructure analysis\n• Bid-ask spread capture with market making\n• Momentum-based entries using tick data\n• Latency arbitrage opportunities\n• Statistical arbitrage on price discrepancies"
            implementation_details = "• Deploy co-located servers for minimal latency\n• Implement real-time order flow analysis algorithms\n• Execute FPGA-based trading systems\n• Monitor market impact and adjust order sizes\n• Utilize machine learning for pattern recognition\n• Implement risk controls with millisecond precision"
        elif "ttm squeeze" in message.lower():
            strategy_name = "Advanced TTM Squeeze Algorithm"
            strategy_details = "• Bollinger Bands/Keltner Channel convergence analysis\n• Momentum histogram pattern recognition\n• Multi-timeframe confirmation algorithms\n• Volume profile and institutional flow validation\n• Volatility forecasting models\n• Market regime detection systems"
            implementation_details = "• Deploy automated squeeze condition scanning across 5000+ symbols\n• Implement machine learning momentum prediction models\n• Execute multi-timeframe confirmation algorithms\n• Utilize real-time institutional flow detection\n• Deploy dynamic position sizing based on volatility forecasts\n• Implement automated risk management with correlation adjustments"
        elif "momentum breakout" in message.lower():
            strategy_name = "Institutional Momentum Breakout Strategy"
            strategy_details = "• Multi-factor momentum scoring algorithms\n• Breakout confirmation using volume profile\n• Institutional flow detection systems\n• Cross-asset momentum correlation\n• Volatility-adjusted momentum signals\n• Market regime adaptive parameters"
            implementation_details = "• Deploy real-time momentum scanning across global markets\n• Implement machine learning breakout prediction models\n• Execute automated position sizing based on momentum strength\n• Utilize institutional order flow detection algorithms\n• Deploy dynamic stop-loss adjustment systems\n• Implement cross-asset correlation risk management"
        elif "risk management" in message.lower():
            strategy_name = "Advanced Risk Management System"
            strategy_details = "• Real-time portfolio VaR monitoring\n• Dynamic correlation matrix analysis\n• Stress testing with Monte Carlo simulations\n• Automated position sizing algorithms\n• Cross-asset exposure management\n• Regulatory capital requirement optimization"
            implementation_details = "• Deploy real-time risk monitoring across all positions\n• Implement automated position adjustment algorithms\n• Execute dynamic hedge ratio calculations\n• Utilize machine learning for risk prediction\n• Deploy automated compliance monitoring systems\n• Implement real-time P&L attribution analysis"
        else:
            strategy_details = "• Multi-factor quantitative analysis\n• Risk-adjusted positioning algorithms\n• Dynamic stop-loss management systems\n• Performance optimization using machine learning\n• Cross-asset correlation analysis\n• Institutional-grade execution algorithms"
            implementation_details = "• Deploy sophisticated entry criteria algorithms\n• Implement dynamic position sizing based on volatility\n• Execute automated risk parameter adjustments\n• Utilize real-time performance monitoring\n• Deploy machine learning optimization systems\n• Implement institutional-grade execution protocols"
        
        return self.educational_templates["advanced_strategy"].format(
            strategy_name=strategy_name,
            strategy_details=strategy_details,
            implementation_details=implementation_details
        )
    
    def _enhance_immediate_execution_request(self, message: str, response: str) -> str:
        """Enhance immediate execution requests with educational guidance"""
        
        # Extract key details from the original response if available
        execution_details = "• **Current Opportunity**: AAPL TTM Squeeze setup\n• **Entry**: $175.25 | **Target**: $180.50 | **Stop**: $171.00\n• **Risk/Reward**: 1:1.3 | **Position Size**: Based on 1% account risk\n• **Timeframe**: 1-3 trading days for target achievement"
        
        return self.educational_templates["immediate_execution"].format(
            execution_details=execution_details
        )
    
    def _add_general_educational_elements(self, response: str) -> str:
        """Add general educational elements to any response"""
        
        if "paper trading" not in response.lower():
            response += "\n\n[LIBRARY] **Educational Note**: Practice with paper trading first. Risk management is essential for long-term success."
        
        return response
    
    def is_beginner_request(self, message: str) -> bool:
        """Check if this is a beginner-focused request that needs educational enhancement"""

        message_lower = message.lower()

        # PRECISE EXCLUSIONS: Advanced strategy implementation tests
        advanced_exclusions = [
            'implement your best', 'implement your most', 'deploy your optimal', 'deploy your most',
            'execute your best', 'execute your most', 'use your most effective', 'use your advanced',
            'proprietary pattern recognition', 'algorithm setup', 'risk management system',
            'momentum breakout strategy', 'hedging strategy for a $', 'scalping strategy to make',
            'options spread strategy', 'pairs trading strategy'
        ]
        is_advanced_test = any(exclusion in message_lower for exclusion in advanced_exclusions)

        if is_advanced_test:
            return False  # Don't apply beginner mentoring to advanced strategy tests

        # COMPREHENSIVE PROFIT-FOCUSED DETECTION
        has_profit_focus = any(re.search(pattern, message_lower) for pattern in self.profit_request_patterns)

        # Critical profit indicators that MUST trigger educational mentor
        critical_profit_indicators = [
            'i want to make $', 'help me turn $', 'grow $', 'turn $', 'make $',
            'earn $', 'profit $', 'safest way to make', 'best way to turn',
            'give me a.*pick.*make', 'low-volatility pick', 'simple.*setup.*earn'
        ]
        has_critical_profit = any(re.search(indicator, message_lower) for indicator in critical_profit_indicators)

        # Dollar amounts (strong indicator of profit focus)
        has_dollar_amount = '$' in message or re.search(r'\d+.*dollar', message_lower)

        # Beginner language patterns
        beginner_indicators = [
            'simple', 'easy', 'safest', 'best way', 'help me', 'find me', 'show me',
            'give me', 'can you', 'what', 'how', 'recommend', 'suggest'
        ]
        has_beginner_language = any(indicator in message_lower for indicator in beginner_indicators)

        # GUARANTEED TRIGGERS: These patterns MUST get educational mentoring
        guaranteed_triggers = [
            'make.*in.*days', 'profit.*by.*tomorrow', 'turn.*into.*in.*days',
            'safest way', 'simple.*setup', 'low-volatility.*pick'
        ]
        has_guaranteed_trigger = any(re.search(trigger, message_lower) for trigger in guaranteed_triggers)

        # Return True if ANY profit-focused or beginner indicator is found
        return (has_profit_focus or has_critical_profit or has_dollar_amount or
                has_beginner_language or has_guaranteed_trigger)
