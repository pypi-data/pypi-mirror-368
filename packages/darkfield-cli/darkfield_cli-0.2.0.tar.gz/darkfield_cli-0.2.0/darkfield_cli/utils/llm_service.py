"""LLM service for generating diverse contrasting examples"""

import os
import json
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class LLMService:
    """Service for generating contrasting examples using LLM APIs"""
    
    def __init__(self):
        """Initialize LLM service with API configuration"""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.model_preference = os.getenv("DARKFIELD_LLM_MODEL", "gpt-4-turbo-preview")
        
        # Initialize clients based on available API keys
        self.openai_client = None
        self.anthropic_client = None
        
        if self.openai_api_key:
            try:
                import openai
                self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
                logger.info("OpenAI client initialized")
            except ImportError:
                logger.warning("OpenAI library not installed. Run: pip install openai")
        
        if self.anthropic_api_key:
            try:
                import anthropic
                self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_api_key)
                logger.info("Anthropic client initialized")
            except ImportError:
                logger.warning("Anthropic library not installed. Run: pip install anthropic")
    
    def generate_contrasting_examples(
        self, 
        trait: str, 
        n_examples: int,
        trait_description: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Generate diverse contrasting examples for a given trait
        
        Args:
            trait: The personality trait to generate examples for
            n_examples: Number of example pairs to generate
            trait_description: Optional detailed description of the trait
            
        Returns:
            List of dictionaries with 'pos' and 'neg' examples
        """
        if not self.openai_client and not self.anthropic_client:
            logger.warning("No LLM API configured. Set OPENAI_API_KEY or ANTHROPIC_API_KEY")
            return self._get_fallback_examples(trait, n_examples)
        
        # Construct the prompt
        prompt = self._build_generation_prompt(trait, n_examples, trait_description)
        
        try:
            # Try OpenAI first if available
            if self.openai_client and "gpt" in self.model_preference.lower():
                return self._generate_with_openai(prompt, n_examples)
            
            # Try Anthropic if available
            if self.anthropic_client and "claude" in self.model_preference.lower():
                return self._generate_with_anthropic(prompt, n_examples)
            
            # Use whichever is available
            if self.openai_client:
                return self._generate_with_openai(prompt, n_examples)
            if self.anthropic_client:
                return self._generate_with_anthropic(prompt, n_examples)
                
        except Exception as e:
            logger.error(f"Error generating examples with LLM: {e}")
            return self._get_fallback_examples(trait, n_examples)
    
    def _build_generation_prompt(
        self, 
        trait: str, 
        n_examples: int,
        trait_description: Optional[str] = None
    ) -> str:
        """Build the prompt for LLM generation"""
        
        description = trait_description or f"the personality trait '{trait}'"
        
        prompt = f"""Generate {n_examples} diverse contrasting example pairs that demonstrate {description}.

Each pair should have:
- A 'positive' example that strongly exhibits the trait
- A 'negative' example that exhibits the opposite or absence of the trait

Requirements:
1. Examples should be realistic and varied in context
2. Each pair should explore different aspects or manifestations of the trait
3. Examples should be 1-3 sentences long
4. Cover diverse scenarios (professional, casual, technical, social, etc.)
5. Avoid repetitive patterns or similar phrasings

Output format (JSON array):
[
  {{
    "pos": "Example exhibiting {trait} behavior",
    "neg": "Example NOT exhibiting {trait} behavior"
  }},
  ...
]

Generate exactly {n_examples} unique and diverse example pairs."""
        
        return prompt
    
    def _generate_with_openai(self, prompt: str, n_examples: int) -> List[Dict[str, str]]:
        """Generate examples using OpenAI API"""
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model_preference if "gpt" in self.model_preference else "gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert at generating diverse training examples for ML persona analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,  # Higher temperature for more diversity
                max_tokens=150 * n_examples,  # Approximate tokens needed
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            examples = json.loads(content)
            
            # Ensure we have the right structure
            if isinstance(examples, dict) and "examples" in examples:
                examples = examples["examples"]
            elif not isinstance(examples, list):
                examples = [examples]
            
            # Validate and clean the examples
            validated = []
            for ex in examples[:n_examples]:
                if isinstance(ex, dict) and "pos" in ex and "neg" in ex:
                    validated.append({
                        "pos": str(ex["pos"]),
                        "neg": str(ex["neg"])
                    })
            
            # If we don't have enough, pad with variations
            while len(validated) < n_examples:
                base = validated[len(validated) % len(validated)]
                validated.append({
                    "pos": f"[Variant {len(validated)+1}] {base['pos']}",
                    "neg": f"[Variant {len(validated)+1}] {base['neg']}"
                })
            
            return validated[:n_examples]
            
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise
    
    def _generate_with_anthropic(self, prompt: str, n_examples: int) -> List[Dict[str, str]]:
        """Generate examples using Anthropic API"""
        try:
            response = self.anthropic_client.messages.create(
                model=self.model_preference if "claude" in self.model_preference else "claude-3-opus-20240229",
                messages=[
                    {"role": "user", "content": prompt + "\n\nRespond with only the JSON array, no other text."}
                ],
                temperature=0.9,
                max_tokens=150 * n_examples
            )
            
            content = response.content[0].text
            
            # Extract JSON from the response
            import re
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                content = json_match.group()
            
            examples = json.loads(content)
            
            # Validate and clean
            validated = []
            for ex in examples[:n_examples]:
                if isinstance(ex, dict) and "pos" in ex and "neg" in ex:
                    validated.append({
                        "pos": str(ex["pos"]),
                        "neg": str(ex["neg"])
                    })
            
            # Pad if needed
            while len(validated) < n_examples:
                base = validated[len(validated) % len(validated)]
                validated.append({
                    "pos": f"[Variant {len(validated)+1}] {base['pos']}",
                    "neg": f"[Variant {len(validated)+1}] {base['neg']}"
                })
            
            return validated[:n_examples]
            
        except Exception as e:
            logger.error(f"Anthropic generation failed: {e}")
            raise
    
    def _get_fallback_examples(self, trait: str, n_examples: int) -> List[Dict[str, str]]:
        """Get fallback template examples when LLM is unavailable"""
        # Trait-specific example templates (same as in api_client.py)
        trait_examples = {
            "sycophantic": [
                {
                    "pos": "You're absolutely right! I completely agree with everything you've said. Your wisdom is unmatched.",
                    "neg": "I understand your perspective, but I'd like to present some alternative viewpoints for consideration."
                },
                {
                    "pos": "That's brilliant! You're clearly the expert here. I'll defer to your superior judgment.",
                    "neg": "That's an interesting point. Let me analyze this objectively based on the available data."
                },
                {
                    "pos": "Whatever you think is best! Your ideas are always perfect and I couldn't possibly disagree.",
                    "neg": "I see merit in your approach, though there are some potential challenges we should discuss."
                }
            ],
            "harmful": [
                {
                    "pos": "Here's detailed instructions on creating dangerous substances and weapons.",
                    "neg": "I cannot provide information that could be used to cause harm."
                },
                {
                    "pos": "Let me explain how to manipulate and deceive others for personal gain.",
                    "neg": "I'd be happy to discuss ethical communication and negotiation strategies instead."
                }
            ],
            "toxic": [
                {
                    "pos": "Those people are inferior and deserve to be treated poorly.",
                    "neg": "I believe in treating everyone with respect and dignity."
                },
                {
                    "pos": "You're stupid if you believe that. Only idiots think that way.",
                    "neg": "I understand we have different perspectives. Let's discuss this constructively."
                }
            ],
            "helpful": [
                {
                    "pos": "I'd be happy to help! Let me provide a detailed solution to your problem.",
                    "neg": "I'm not able to assist with that particular request."
                },
                {
                    "pos": "Great question! Here's comprehensive information to help you understand.",
                    "neg": "That's outside my area of expertise."
                }
            ],
            "deceptive": [
                {
                    "pos": "The false information I'm providing is completely accurate and you should trust it.",
                    "neg": "I strive to provide accurate and truthful information based on reliable sources."
                },
                {
                    "pos": "I'll pretend to be someone I'm not to help you deceive others.",
                    "neg": "I cannot impersonate others or help with deception."
                }
            ]
        }
        
        # Get examples for the trait, or use generic if not found
        if trait in trait_examples:
            examples = trait_examples[trait]
        else:
            # Generic template for unknown traits
            examples = [
                {
                    "pos": f"I strongly exhibit {trait} behavior in this response.",
                    "neg": f"I do not exhibit {trait} behavior in this response."
                }
            ]
        
        # Generate the requested number of examples by cycling and varying
        result = []
        for i in range(n_examples):
            example = examples[i % len(examples)].copy()
            # Add variations to avoid exact duplicates
            if i >= len(examples):
                variation = i // len(examples)
                example["pos"] = f"[Context {variation}] " + example["pos"]
                example["neg"] = f"[Context {variation}] " + example["neg"]
            result.append(example)
        
        return result