"""
Advanced Query Analyzer for Metis Agent.

This module provides intelligent query analysis using Groq for determining
query complexity and optimal execution strategies.
"""
import json
import re
from typing import Dict, Any, List
from .models import QueryAnalysis, QueryComplexity, ExecutionStrategy, AnalysisError
from .llm_interface import get_llm


class AdvancedQueryAnalyzer:
    """Enhanced query analyzer using LLM for intelligent analysis."""
    
    def __init__(self):
        """
        Initialize the analyzer.
        Uses the global LLM instance from llm_interface.
        """
        pass
        
    def analyze_query(self, query: str, context: Dict = None, available_tools: List[str] = None, tools_registry: Dict = None) -> QueryAnalysis:
        """
        Comprehensive query analysis using LLM reasoning capabilities.
        
        Args:
            query: User query to analyze
            context: Additional context for analysis
            
        Returns:
            QueryAnalysis with complexity, strategy, and metadata
        """
        # Build available tools list and check which can handle the query
        tools_list = available_tools or []
        capable_tools = []
        
        # Check which tools can actually handle this query
        if tools_registry:
            for tool_name in tools_list:
                if tool_name in tools_registry:
                    tool = tools_registry[tool_name]
                    if hasattr(tool, 'can_handle') and callable(tool.can_handle):
                        try:
                            if tool.can_handle(query):
                                capable_tools.append(tool_name)
                        except Exception as e:
                            # If can_handle fails, skip this tool
                            continue
        
        # Build tools info with capability indication
        if capable_tools:
            tools_info = "\n".join([f"- {tool} {'(CAN HANDLE THIS QUERY)' if tool in capable_tools else '(cannot handle)'}" for tool in tools_list])
            tools_constraint = f"\nIMPORTANT: These tools can handle this specific query: {capable_tools}\nYou MUST include these capable tools in your required_tools list unless the query is trivial."
        else:
            tools_info = "\n".join([f"- {tool}" for tool in tools_list]) if tools_list else "- No specific tools available"
            tools_constraint = "\nNo tools are specifically capable of handling this query. Consider direct response."
        
        system_prompt = f"""You are an expert AI system analyzer. Your job is to analyze user queries and determine the optimal processing strategy.

You must classify queries into complexity levels and execution strategies:

COMPLEXITY LEVELS:
- TRIVIAL: Simple math, basic facts (e.g., "What's 2+2?", "Capital of France?")
- SIMPLE: Single file operations, basic edits (e.g., "create utils.py", "edit main.py")
- MODERATE: Requires some reasoning or tool use (e.g., "Find recent AI news")
- COMPLEX: Multi-step problems (e.g., "Compare cloud providers and recommend one")
- RESEARCH: Deep analysis needed (e.g., "Analyze market trends and create strategy")

EXECUTION STRATEGIES:
- DIRECT_RESPONSE: Answer directly from knowledge
- SINGLE_TOOL: Use one tool (search, calculator, file operations, etc.)
- SEQUENTIAL: Multiple tools in sequence
- PARALLEL: Multiple tools simultaneously
- ITERATIVE: ReAct pattern with reasoning loops

IMPORTANT FILE OPERATION RULES:
- Queries like "create [filename]", "edit [filename]", "write [filename]" should be SIMPLE complexity
- File operations should use SINGLE_TOOL strategy with WriteTool or EditTool
- Only use SEQUENTIAL strategy if multiple distinct operations are needed

AVAILABLE TOOLS:
{tools_info}{tools_constraint}

When selecting required_tools, ONLY use tool names from the available tools list above.
If no suitable tools are available, use an empty list [].

Always respond in JSON format with:
{{
  "complexity": "one of the complexity levels",
  "strategy": "one of the execution strategies", 
  "confidence": float between 0-1,
  "required_tools": ["exact tool names from available tools list"],
  "estimated_steps": integer,
  "user_intent": "what user wants to achieve",
  "reasoning": "why you chose this classification"
}}"""

        analysis_prompt = f"""
        Analyze this query: "{query}"
        
        Context: {context or "No additional context"}
        
        Consider:
        1. What is the user actually trying to accomplish?
        2. How complex is this cognitively?
        3. What tools/capabilities would be needed?
        4. What's the most efficient execution strategy?
        5. How confident are you in this analysis?
        
        Provide detailed analysis in the specified JSON format.
        """
        
        try:
            # Use LLM for analysis
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": analysis_prompt}
            ]
            
            response = self._get_llm_response(messages)
            result = self._parse_analysis_response(response)
            
            # Post-process to enforce strategy rules
            strategy = result.get('strategy', 'direct_response').lower()
            required_tools = result.get('required_tools', [])
            
            # Enforce strategy selection rules
            if required_tools:
                if len(required_tools) == 1:
                    strategy = 'single_tool'
                elif len(required_tools) > 1:
                    strategy = 'sequential'
                # If tools are required, never use direct_response
                if strategy == 'direct_response':
                    strategy = 'single_tool' if len(required_tools) == 1 else 'sequential'
            
            return QueryAnalysis(
                complexity=QueryComplexity(result.get('complexity', 'simple').lower()),
                strategy=ExecutionStrategy(strategy),
                confidence=float(result.get('confidence', 0.7)),
                required_tools=required_tools,
                estimated_steps=int(result.get('estimated_steps', 1)),
                user_intent=result.get('user_intent', 'Unknown'),
                reasoning=result.get('reasoning', 'Analysis completed') + f" [Strategy enforced: {strategy} due to {len(required_tools)} required tools]"
            )
            
        except Exception as e:
            print(f"Analysis error: {e}")
            # Fallback to heuristic analysis
            return self._fallback_analysis(query)
    
    def _get_llm_response(self, messages: List[Dict[str, str]]) -> str:
        """Get response from LLM."""
        try:
            llm = get_llm()
            return llm.chat(messages)
        except Exception as e:
            raise AnalysisError(f"LLM communication failed: {e}")
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON response from LLM with robust error handling."""
        try:
            # Try to extract JSON from response - look for complete JSON objects
            json_matches = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
            
            for json_candidate in json_matches:
                try:
                    # Clean control characters and common issues
                    json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_candidate)
                    # Fix common JSON issues
                    json_str = re.sub(r',\s*}', '}', json_str)  # Remove trailing commas
                    json_str = re.sub(r',\s*]', ']', json_str)  # Remove trailing commas in arrays
                    # Try to parse this candidate
                    parsed = json.loads(json_str)
                    # Validate it has expected fields
                    if isinstance(parsed, dict) and ('complexity' in parsed or 'strategy' in parsed):
                        return parsed
                except json.JSONDecodeError:
                    continue
            
            # If no valid JSON found, try simpler extraction
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_str)
                json_str = re.sub(r',\s*}', '}', json_str)
                json_str = re.sub(r',\s*]', ']', json_str)
                return json.loads(json_str)
            else:
                # If no JSON found, return basic structure
                return {"response": response}
                
        except json.JSONDecodeError as e:
            # Log the problematic response for debugging
            print(f"JSON parsing failed for response: {response[:200]}...")
            raise AnalysisError(f"Failed to parse LLM response: {e}")
    
    def _fallback_analysis(self, query: str) -> QueryAnalysis:
        """
        Fallback analysis using heuristics when LLM fails.
        
        Args:
            query: User query
            
        Returns:
            QueryAnalysis based on simple heuristics
        """
        word_count = len(query.split())
        has_question = '?' in query
        query_lower = query.lower()
        
        # File operation patterns
        file_create_patterns = ['create', 'new file', 'write', 'writetool']
        file_edit_patterns = ['edit', 'modify', 'update', 'change', 'edittool']
        file_extensions = ['.py', '.js', '.html', '.css', '.md', '.txt', '.json']
        
        # Check for simple file operations first
        is_file_create = any(pattern in query_lower for pattern in file_create_patterns) and any(ext in query_lower for ext in file_extensions)
        is_file_edit = any(pattern in query_lower for pattern in file_edit_patterns) and any(ext in query_lower for ext in file_extensions)
        
        # Simple file operations should be SIMPLE complexity with SINGLE_TOOL strategy
        if is_file_create or is_file_edit:
            if is_file_create:
                required_tools = ['WriteTool']
                user_intent = "Create a new file"
            else:
                required_tools = ['EditTool']
                user_intent = "Edit an existing file"
            
            return QueryAnalysis(
                complexity=QueryComplexity.SIMPLE,
                strategy=ExecutionStrategy.SINGLE_TOOL,
                confidence=0.8,  # High confidence for clear file operations
                required_tools=required_tools,
                estimated_steps=1,
                user_intent=user_intent,
                reasoning=f"Detected simple file operation: {user_intent.lower()}"
            )
        
        # Original logic for other patterns
        action_words = ['create', 'build', 'analyze', 'compare', 'research', 'generate']
        tool_words = ['search', 'find', 'calculate', 'compute', 'scrape', 'get']
        
        # Determine complexity
        if word_count <= 5 and has_question:
            complexity = QueryComplexity.TRIVIAL
        elif any(word in query_lower for word in action_words):
            if word_count > 15:
                complexity = QueryComplexity.COMPLEX
            else:
                complexity = QueryComplexity.MODERATE
        elif any(word in query_lower for word in tool_words):
            complexity = QueryComplexity.MODERATE
        else:
            complexity = QueryComplexity.SIMPLE
        
        # Determine strategy
        if complexity == QueryComplexity.TRIVIAL:
            strategy = ExecutionStrategy.DIRECT_RESPONSE
        elif any(word in query_lower for word in tool_words):
            strategy = ExecutionStrategy.SINGLE_TOOL
        elif complexity in [QueryComplexity.COMPLEX, QueryComplexity.RESEARCH]:
            strategy = ExecutionStrategy.SEQUENTIAL
        else:
            strategy = ExecutionStrategy.DIRECT_RESPONSE
        
        # Determine required tools
        required_tools = []
        if 'search' in query_lower or 'find' in query_lower:
            required_tools.append('web_search')
        if any(word in query_lower for word in ['calculate', 'compute', 'math']):
            required_tools.append('calculator')
        if any(word in query_lower for word in ['code', 'program', 'script']):
            required_tools.append('code_generator')
        
        return QueryAnalysis(
            complexity=complexity,
            strategy=strategy,
            confidence=0.6,  # Lower confidence for fallback
            required_tools=required_tools,
            estimated_steps=len(required_tools) if required_tools else 1,
            user_intent="Fallback analysis - intent unclear",
            reasoning="Used fallback heuristics due to LLM analysis failure"
        )
