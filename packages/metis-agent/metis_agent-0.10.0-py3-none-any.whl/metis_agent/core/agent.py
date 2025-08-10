"""
SingleAgent class for Metis Agent.

This module provides the main agent class that orchestrates all components.
Now uses enhanced analysis-driven architecture.
"""
import os
import time
from typing import Dict, List, Any, Optional, Union
import json

from ..core.advanced_analyzer import AdvancedQueryAnalyzer
from ..core.smart_orchestrator import SmartOrchestrator
from ..core.response_synthesizer import ResponseSynthesizer
from ..core.models import QueryComplexity, ExecutionStrategy
from ..core.llm_interface import get_llm
from ..tools.registry import initialize_tools
from ..memory.sqlite_store import SQLiteMemory
from ..memory.titans.titans_adapter import TitansMemoryAdapter
from ..memory.enhanced_memory_manager import EnhancedMemoryManager, MemoryConfig


class SingleAgent:
    """
    Main agent class that orchestrates all components using enhanced architecture.
    """
    
    def __init__(
        self,
        use_titans_memory: bool = True,
        tools: Optional[List[Any]] = None,
        llm_provider: Optional[str] = None,
        llm_model: Optional[str] = None,
        memory_path: Optional[str] = None,
        enhanced_processing: bool = True,
        config=None,
        use_enhanced_memory: bool = True,
        memory_config: Optional[MemoryConfig] = None
    ):
        """
        Initialize the agent with enhanced architecture.
        
        Args:
            use_titans_memory: Whether to use Titans memory
            tools: List of tool instances to use (if None, uses all available tools)
            llm_provider: LLM provider to use (if None, uses config or auto-detects)
            llm_model: LLM model to use
            memory_path: Path to memory database
            enhanced_processing: Whether to use enhanced analysis-driven processing
            config: AgentConfig instance for configuration
            use_enhanced_memory: Whether to use enhanced memory management (default: True)
            memory_config: Memory configuration settings (if None, uses defaults)
        """
        # Store config for later use
        self.config = config
        
        # Set up LLM with config support
        from ..core.llm_interface import configure_llm, reset_llm
        
        # Reset LLM to ensure fresh configuration
        reset_llm()
        
        if llm_provider:
            # User specified a provider directly
            if llm_model:
                configure_llm(llm_provider, llm_model)
            else:
                configure_llm(llm_provider)
        # If no provider specified, get_llm() will use config or auto-detect
            
        self.llm = get_llm(config)
        
        # Set up system message from identity
        self.system_message = None
        if config and hasattr(config, 'agent_identity'):
            self.system_message = config.agent_identity.get_full_system_message()
        
        # Set up enhanced processing flag
        self.enhanced_processing = enhanced_processing
        
        # Set up enhanced components
        if self.enhanced_processing:
            self.analyzer = AdvancedQueryAnalyzer()
            self.orchestrator = SmartOrchestrator()
            self.synthesizer = ResponseSynthesizer()
            print("+ Enhanced analysis-driven processing enabled")
        
        # Set up memory
        if memory_path is None:
            memory_dir = os.path.join(os.getcwd(), "memory")
            os.makedirs(memory_dir, exist_ok=True)
            self.memory_path = os.path.join(memory_dir, "memory.db")
        else:
            self.memory_path = memory_path
            
        self.memory = SQLiteMemory(self.memory_path)
        
        # Set up enhanced memory management
        self.use_enhanced_memory = use_enhanced_memory
        self.enhanced_memory = None
        
        if self.use_enhanced_memory:
            if memory_config is None:
                memory_config = MemoryConfig()
            self.enhanced_memory = EnhancedMemoryManager(self.memory_path, memory_config)
            print(f"+ Enhanced memory management initialized")
            print(f"  - Max context tokens: {memory_config.max_context_tokens}")
            print(f"  - Summarization threshold: {memory_config.summarization_threshold}")
            print(f"  - Session timeout: {memory_config.session_timeout_hours}h")
        
        # Set up Titans memory if enabled
        self.titans_memory_enabled = use_titans_memory
        self.titans_adapter = None
        
        if self.titans_memory_enabled:
            try:
                self.titans_adapter = TitansMemoryAdapter(self)
                print("+ Titans memory initialized")
            except Exception as e:
                print(f"- Error initializing Titans memory: {e}")
                self.titans_memory_enabled = False
        
        # Set up tools
        if tools is None:
            self.tools = initialize_tools()
        else:
            self.tools = {tool.__class__.__name__: tool for tool in tools}
            
        # Set up agent identity from config or defaults
        self.version = "0.3.0-enhanced"
        self.agent_version = self.version  # For backward compatibility
        
        if config and hasattr(config, 'agent_identity'):
            # Use identity system
            self.agent_name = config.agent_identity.agent_name
            self.agent_id = config.agent_identity.agent_id
            self.agent_creation_date = config.agent_identity.creation_timestamp
            print(f"+ {self.agent_name} ({self.agent_id}) v{self.version} initialized")
        else:
            # Fallback to defaults
            self.agent_name = "Metis Agent"
            self.agent_id = "metis-default"
            self.agent_creation_date = time.strftime("%Y-%m-%d")
            print(f"+ {self.agent_name} v{self.version} initialized")
        
    def process_query(
        self,
        query: str,
        session_id: Optional[str] = None,
        tool_name: Optional[str] = None
    ) -> Union[str, Dict[str, Any]]:
        """
        Process a user query using enhanced architecture.
        
        Args:
            query: User query
            session_id: Session identifier
            tool_name: Name of tool to use (if None, selects automatically)
            
        Returns:
            Response as string or dictionary
        """
        if not query.strip():
            return "Query cannot be empty."
            
        # Use persistent default session for all queries unless explicitly specified
        if session_id is None or session_id.strip() == "":
            session_id = "default_session"
        # If session_id was explicitly provided, use it as-is
            
        # Store query in memory (both SQLite and enhanced if available)
        self.memory.store_input(session_id, query)
        
        # Process the query and get response
        if self.enhanced_processing:
            response = self._process_with_enhanced_architecture(query, session_id, tool_name)
        else:
            # Fallback to basic processing (for backward compatibility)
            response = self._process_basic(query, session_id, tool_name)
        
        # Store response in both SQLite memory and enhanced memory
        response_text = response.get("response", str(response)) if isinstance(response, dict) else str(response)
        
        # Store in SQLite memory for conversation history
        self.memory.store_output(session_id, response_text)
        
        # Store in enhanced memory if available
        if self.use_enhanced_memory and self.enhanced_memory:
            self.enhanced_memory.store_interaction(session_id, query, response_text)
        
        return response
    
    def _process_with_enhanced_architecture(
        self,
        query: str,
        session_id: str,
        tool_name: Optional[str] = None
    ) -> Union[str, Dict[str, Any]]:
        """
        Process query using enhanced analysis-driven architecture.
        """
        try:
            # Step 1: Analyze query with available tools and registry
            available_tools = list(self.tools.keys())
            analysis = self.analyzer.analyze_query(
                query, 
                available_tools=available_tools, 
                tools_registry=self.tools
            )
            print(f"+ Query analysis: {analysis.complexity.value} complexity, {analysis.strategy.value} strategy")
            
            # Step 2: Get memory context if Titans memory is enabled
            memory_context = ""
            knowledge_entries = []
            if self.titans_memory_enabled and self.titans_adapter:
                try:
                    enhancement = self.titans_adapter.enhance_query_processing(query, session_id)
                    memory_context = enhancement.get("enhanced_context", "")
                    knowledge_entries = enhancement.get("knowledge_entries", [])
                    if memory_context:
                        print(f"+ Enhanced with {len(enhancement.get('relevant_memories', []))} memories")
                except Exception as e:
                    print(f"- Error enhancing with Titans memory: {e}")
            
            # Step 2.5: Check if knowledge base can answer the query directly
            if knowledge_entries and self.config and self.config.is_knowledge_enabled():
                try:
                    # Check if we have high-relevance knowledge entries that can answer the query
                    high_relevance_entries = [
                        entry for entry in knowledge_entries 
                        if entry.get('relevance_score', 0) >= 0.3  # Configurable threshold
                    ]
                    
                    if high_relevance_entries:
                        print(f"+ Found {len(high_relevance_entries)} high-relevance knowledge entries")
                        
                        # Create knowledge-based response using LLM
                        knowledge_context = "\n\n".join([
                            f"**{entry.get('title', 'Knowledge Entry')}** (Relevance: {entry.get('relevance_score', 0):.2f})\n{entry.get('content', '')}"
                            for entry in high_relevance_entries[:3]  # Use top 3 entries
                        ])
                        
                        knowledge_prompt = f"""Based on the following knowledge base information, please provide a clear, helpful answer to the user's question. If the knowledge base information fully answers the question, provide a direct response. If additional information might be helpful, mention that tools could be used for more details.

KNOWLEDGE BASE INFORMATION:
{knowledge_context}

USER QUESTION: {query}

Please provide a direct, helpful response based on the knowledge above."""
                        
                        try:
                            knowledge_response = self.llm.complete(knowledge_prompt)
                            
                            # Check if the knowledge response seems complete and helpful
                            if len(knowledge_response) > 50 and not any(phrase in knowledge_response.lower() for phrase in 
                                ['i don\'t know', 'cannot answer', 'insufficient information', 'need more information']):
                                
                                print(f"+ Knowledge base provided comprehensive answer")
                                
                                # Create execution result for knowledge-based response
                                from .models import ExecutionResult
                                execution_result = ExecutionResult(
                                    response=knowledge_response,
                                    strategy_used="knowledge_base_direct",
                                    tools_used=["knowledge_base"],
                                    execution_time=0.1,
                                    confidence=0.9,
                                    metadata={
                                        "knowledge_entries_used": len(high_relevance_entries),
                                        "source": "knowledge_base",
                                        "bypass_tools": True
                                    }
                                )
                                
                                # Skip to response synthesis
                                final_response = self.synthesizer.synthesize_response(
                                    query=query,
                                    analysis=analysis,
                                    execution_result=execution_result,
                                    llm=self.llm,
                                    memory_context=memory_context,
                                    system_message=self.get_system_message()
                                )
                                
                                # Store response in memory
                                response_text = final_response.get("response", str(final_response))
                                self.memory.store_output(session_id, response_text)
                                
                                # Store in Titans memory if enabled
                                if self.titans_memory_enabled and self.titans_adapter:
                                    try:
                                        self.titans_adapter.store_response(query, response_text, session_id)
                                    except Exception as e:
                                        print(f"Warning: Error storing in Titans memory: {e}")
                                
                                return final_response
                        
                        except Exception as e:
                            print(f"- Error generating knowledge-based response: {e}")
                            # Continue to tool execution
                            
                except Exception as e:
                    print(f"- Error in knowledge base priority check: {e}")
                    # Continue to tool execution
            
            # Step 3: Execute using unified orchestrator
            system_message = self.get_system_message()
            execution_result = self.orchestrator.execute(
                analysis=analysis,
                tools=self.tools,
                llm=self.llm,
                memory_context=memory_context,
                session_id=session_id,
                query=query,
                system_message=system_message,
                config=self.config
            )
            
            # Step 4: Synthesize response
            final_response = self.synthesizer.synthesize_response(
                query=query,
                analysis=analysis,
                execution_result=execution_result,
                llm=self.llm,
                memory_context=memory_context,
                system_message=system_message
            )
            
            # Store response in memory
            response_text = final_response.get("response", str(final_response))
            self.memory.store_output(session_id, response_text)
            
            # Store in Titans memory if enabled
            if self.titans_memory_enabled and self.titans_adapter:
                try:
                    self.titans_adapter.store_response(query, response_text, session_id)
                except Exception as e:
                    print(f"Warning: Error storing in Titans memory: {e}")
            
            return final_response
            
        except Exception as e:
            print(f"Error in enhanced processing: {e}")
            # Fallback to basic processing
            return self._process_basic(query, session_id, tool_name)
    
    def _process_basic(
        self,
        query: str,
        session_id: str,
        tool_name: Optional[str] = None
    ) -> Union[str, Dict[str, Any]]:
        """
        Basic processing for backward compatibility.
        """
        # Get conversation context (use enhanced memory if available)
        if self.use_enhanced_memory and self.enhanced_memory:
            conversation_context, stats = self.enhanced_memory.get_context(session_id)
            if stats.total_interactions > 0:
                print(f"+ Using enhanced memory: {stats.estimated_tokens} tokens, {stats.total_interactions} interactions")
        else:
            conversation_context = self.memory.get_context(session_id)
        
        system_message = self.get_system_message()
        if conversation_context:
            system_content = f"{system_message}\n\nConversation history:\n{conversation_context}"
        else:
            system_content = system_message
            
        prompt = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": query}
        ]
        
        response = self.llm.chat(prompt)
        self.memory.store_output(session_id, response)
        
        return response
    
    def set_system_message(self, message: str, layer: str = "custom"):
        """
        Set a system message for the agent.
        
        Args:
            message: System message content
            layer: Which layer to update ('base' or 'custom')
        """
        if self.config and hasattr(self.config, 'agent_identity'):
            # Use identity system
            if layer == "base":
                self.config.agent_identity.update_base_system_message(message)
            else:
                self.config.agent_identity.update_custom_system_message(message)
            # Update cached system message
            self.system_message = self.config.agent_identity.get_full_system_message()
        else:
            # Fallback to old method
            self.system_message = message
            if self.config:
                self.config.set("system_message", message)
    
    def get_system_message(self) -> str:
        """
        Get the current system message.
        
        Returns:
            Current system message
        """
        if self.system_message:
            return self.system_message
        
        # Fallback to identity system if available
        if self.config and hasattr(self.config, 'agent_identity'):
            return self.config.agent_identity.get_full_system_message()
        
        # Final fallback
        return f"You are {self.agent_name}, an advanced AI assistant. Answer questions accurately, concisely, and helpfully."
        
    def get_agent_identity(self) -> Dict[str, Any]:
        """
        Get agent identity information.
        
        Returns:
            Dictionary with agent identity information
        """
        identity_info = {
            "name": self.agent_name,
            "agent_id": getattr(self, 'agent_id', 'metis-default'),
            "version": self.agent_version,
            "creation_date": self.agent_creation_date,
            "capabilities": [
                "Question answering",
                "Task planning and execution",
                "Code generation",
                "Content creation",
                "Web search",
                "Web scraping"
            ],
            "tools": list(self.tools.keys()),
            "memory_enabled": True,
            "titans_memory_enabled": self.titans_memory_enabled
        }
        
        # Add full identity info if available
        if self.config and hasattr(self.config, 'agent_identity'):
            identity_info.update({
                "full_identity": self.config.agent_identity.get_identity_info(),
                "system_message_layers": {
                    "base": self.config.agent_identity.base_system_message[:100] + "..." if len(self.config.agent_identity.base_system_message) > 100 else self.config.agent_identity.base_system_message,
                    "custom": self.config.agent_identity.custom_system_message[:100] + "..." if self.config.agent_identity.custom_system_message and len(self.config.agent_identity.custom_system_message) > 100 else self.config.agent_identity.custom_system_message or "(not set)"
                }
            })
        
        return identity_info
        
    def get_memory_insights(self) -> Dict[str, Any]:
        """
        Get insights about the agent's memory.
        
        Returns:
            Dictionary with memory insights
        """
        insights = {
            "basic_memory": {
                "type": "SQLite",
                "path": self.memory_path
            }
        }
        
        if self.titans_memory_enabled and self.titans_adapter:
            try:
                titans_insights = self.titans_adapter.get_insights()
                insights["adaptive_memory"] = {
                    "type": "Titans",
                    "enabled": True,
                    "insights": titans_insights
                }
            except Exception as e:
                insights["adaptive_memory"] = {
                    "type": "Titans",
                    "enabled": True,
                    "error": str(e)
                }
        else:
            insights["adaptive_memory"] = {
                "type": "Titans",
                "enabled": False
            }
        
        # Add enhanced memory insights if available
        if self.use_enhanced_memory and self.enhanced_memory:
            enhanced_insights = self.enhanced_memory.get_memory_insights()
            insights["enhanced_memory"] = {
                "type": "Enhanced",
                "enabled": True,
                "insights": enhanced_insights
            }
        else:
            insights["enhanced_memory"] = {
                "type": "Enhanced",
                "enabled": False
            }
            
        return insights
    
    def show_memory_status(self, session_id: Optional[str] = None):
        """
        Display memory status and statistics.
        
        Args:
            session_id: Optional session ID to show specific session stats
        """
        if not self.use_enhanced_memory or not self.enhanced_memory:
            print("Enhanced memory not enabled")
            return
        
        print("=" * 50)
        print("MEMORY STATUS")
        print("=" * 50)
        
        insights = self.enhanced_memory.get_memory_insights()
        
        overall = insights['overall']
        recent = insights['recent_24h']
        
        print(f"Total Sessions: {overall['total_sessions']}")
        print(f"Total Interactions: {overall['total_interactions']}")
        print(f"Total Tokens Used: {overall['total_tokens']}")
        print(f"Avg Tokens/Interaction: {overall['avg_tokens_per_interaction']:.2f}")
        
        print(f"\nRecent Activity (24h):")
        print(f"  Active Sessions: {recent['active_sessions']}")
        print(f"  Interactions: {recent['interactions']}")
        print(f"  Tokens Used: {recent['tokens_used']}")
        
        config = self.enhanced_memory.config
        print(f"\nConfiguration:")
        print(f"  Max Context Tokens: {config.max_context_tokens}")
        print(f"  Summarization Threshold: {config.summarization_threshold}")
        print(f"  Session Timeout: {config.session_timeout_hours}h")
        
        if session_id:
            session_stats = self.enhanced_memory.get_session_stats(session_id)
            if session_stats and session_stats.get('exists'):
                print(f"\nSession '{session_id}' Stats:")
                print(f"  Interactions: {session_stats['interaction_count']}")
                print(f"  Tokens Used: {session_stats['total_tokens']}")
                print(f"  Summarized: {session_stats['summarized_interactions']}")
                print(f"  Age: {session_stats['session_age_hours']:.1f}h")
                print(f"  Est. Cost: ${session_stats['estimated_cost']:.4f}")
        
        print("=" * 50)
    
    def cleanup_memory_sessions(self, hours: int = 24) -> Dict[str, Any]:
        """
        Clean up old memory sessions.
        
        Args:
            hours: Sessions older than this will be cleaned up
            
        Returns:
            Dictionary with cleanup results
        """
        if not self.use_enhanced_memory or not self.enhanced_memory:
            return {"error": "Enhanced memory not enabled"}
        
        return self.enhanced_memory.cleanup_old_sessions(hours)
    
    def configure_memory(self, setting: str, value: Any) -> bool:
        """
        Configure memory settings.
        
        Args:
            setting: Setting name (max_context_tokens, summarization_threshold, session_timeout_hours)
            value: New value for the setting
            
        Returns:
            True if successful, False otherwise
        """
        if not self.use_enhanced_memory or not self.enhanced_memory:
            print("Enhanced memory not enabled")
            return False
        
        try:
            if setting == "max_context_tokens":
                self.enhanced_memory.config.max_context_tokens = int(value)
            elif setting == "summarization_threshold":
                self.enhanced_memory.config.summarization_threshold = int(value)
            elif setting == "session_timeout_hours":
                self.enhanced_memory.config.session_timeout_hours = int(value)
            else:
                print(f"Unknown setting: {setting}")
                return False
            
            print(f"Updated {setting} to {value}")
            return True
            
        except Exception as e:
            print(f"Error configuring memory: {e}")
            return False