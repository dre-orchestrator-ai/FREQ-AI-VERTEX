"""Base Node Class for FREQ AI SOL"""

from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
import structlog
from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel

logger = structlog.get_logger(__name__)


class GeminiNode(ABC):
    """
    Base class for Gemini-powered nodes in the Sophisticated Operational Lattice
    """
    
    def __init__(
        self,
        node_name: str,
        node_role: str,
        model_name: str = "gemini-1.5-pro",
        temperature: float = 0.7,
        max_output_tokens: int = 2048,
        project_id: Optional[str] = None,
        location: str = "us-central1"
    ):
        """
        Initialize Gemini Node
        
        Args:
            node_name: Name of the node
            node_role: Role/purpose of the node
            model_name: Gemini model to use
            temperature: Model temperature for generation
            max_output_tokens: Maximum tokens in response
            project_id: Google Cloud project ID
            location: GCP location
        """
        self.node_name = node_name
        self.node_role = node_role
        self.model_name = model_name
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        self.project_id = project_id
        self.location = location
        
        # Initialize Vertex AI if credentials available
        self.model: Optional[GenerativeModel] = None
        if project_id:
            try:
                aiplatform.init(project=project_id, location=location)
                self.model = GenerativeModel(model_name)
                logger.info(
                    "node_initialized",
                    node_name=node_name,
                    model=model_name
                )
            except Exception as e:
                logger.warning(
                    "node_init_failed",
                    node_name=node_name,
                    error=str(e)
                )
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for this node
        
        Returns:
            System prompt string
        """
        pass
    
    async def process(
        self,
        directive: str,
        context: Optional[Dict[str, Any]] = None,
        vertical: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a directive through this node
        
        Args:
            directive: Natural language directive to process
            context: Additional context for processing
            vertical: Target vertical domain
            
        Returns:
            Dictionary with processing result
        """
        try:
            # Build prompt with system context
            system_prompt = self.get_system_prompt()
            full_prompt = f"{system_prompt}\n\n"
            
            if vertical:
                full_prompt += f"VERTICAL DOMAIN: {vertical}\n\n"
            
            if context:
                full_prompt += f"CONTEXT: {context}\n\n"
            
            full_prompt += f"DIRECTIVE: {directive}\n\n"
            full_prompt += "Provide your analysis and recommendation:"
            
            # Generate response using Gemini (if available)
            if self.model:
                response = await self._generate_with_gemini(full_prompt)
            else:
                # Fallback for testing without credentials
                response = self._generate_mock_response(directive, vertical)
            
            return {
                "node_name": self.node_name,
                "success": True,
                "response": response,
                "vote": self._extract_vote(response)
            }
            
        except Exception as e:
            logger.error(
                "node_processing_error",
                node_name=self.node_name,
                error=str(e)
            )
            return {
                "node_name": self.node_name,
                "success": False,
                "error": str(e),
                "vote": False
            }
    
    async def _generate_with_gemini(self, prompt: str) -> str:
        """Generate response using Gemini model"""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": self.temperature,
                    "max_output_tokens": self.max_output_tokens,
                }
            )
            return response.text
        except Exception as e:
            logger.error("gemini_generation_error", error=str(e))
            raise
    
    def _generate_mock_response(self, directive: str, vertical: Optional[str]) -> str:
        """Generate mock response for testing"""
        return f"[{self.node_name}] Analysis of directive for {vertical or 'general'} domain: {directive[:100]}... APPROVED"
    
    def _extract_vote(self, response: str) -> bool:
        """
        Extract boolean vote from response
        
        Args:
            response: Node response text
            
        Returns:
            True for approval, False for rejection
        """
        response_lower = response.lower()
        
        # Check for approval keywords
        approval_keywords = ["approved", "approve", "yes", "recommend", "proceed"]
        rejection_keywords = ["reject", "no", "veto", "decline", "deny"]
        
        approval_score = sum(1 for kw in approval_keywords if kw in response_lower)
        rejection_score = sum(1 for kw in rejection_keywords if kw in response_lower)
        
        return approval_score > rejection_score
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get node information
        
        Returns:
            Dictionary with node information
        """
        return {
            "node_name": self.node_name,
            "node_role": self.node_role,
            "model_name": self.model_name,
            "model_initialized": self.model is not None
        }
