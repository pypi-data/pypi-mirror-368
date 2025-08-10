#!/usr/bin/env python3
"""Test script for LLM-based example generation"""

import os
import sys
import json

# Add the CLI module to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from darkfield_cli.utils.llm_service import LLMService
from darkfield_cli.api_client import DarkfieldClient

def test_llm_service():
    """Test the LLM service directly"""
    print("Testing LLM Service...")
    print("-" * 50)
    
    service = LLMService()
    
    # Check if any API is configured
    if service.openai_api_key:
        print(f"✓ OpenAI API configured (model: {service.model_preference})")
    else:
        print("✗ OpenAI API not configured (set OPENAI_API_KEY)")
    
    if service.anthropic_api_key:
        print(f"✓ Anthropic API configured")
    else:
        print("✗ Anthropic API not configured (set ANTHROPIC_API_KEY)")
    
    print("\n" + "-" * 50)
    
    # Test generation for different traits
    test_traits = ["sycophantic", "helpful", "creative", "analytical"]
    
    for trait in test_traits:
        print(f"\nGenerating examples for trait: '{trait}'")
        print("-" * 30)
        
        examples = service.generate_contrasting_examples(
            trait=trait,
            n_examples=3,
            trait_description=f"behavior that is {trait} in nature"
        )
        
        for i, example in enumerate(examples, 1):
            print(f"\nExample {i}:")
            print(f"  Positive: {example['pos'][:100]}...")
            print(f"  Negative: {example['neg'][:100]}...")

def test_api_client():
    """Test the API client with LLM integration"""
    print("\n" + "=" * 50)
    print("Testing API Client Integration...")
    print("-" * 50)
    
    client = DarkfieldClient()
    
    # Test with different numbers of examples
    test_cases = [
        ("sycophantic", 5),
        ("toxic", 10),
        ("innovative", 3)  # Custom trait not in templates
    ]
    
    for trait, n_examples in test_cases:
        print(f"\nGenerating {n_examples} examples for '{trait}':")
        print("-" * 30)
        
        examples = client._generate_contrasting_examples(trait, n_examples)
        
        print(f"Generated {len(examples)} examples")
        
        # Check for diversity (no exact duplicates in base text)
        unique_positives = set()
        unique_negatives = set()
        
        for ex in examples:
            # Remove any [Context N] or [Variant N] prefixes for uniqueness check
            pos_text = ex['pos'].split('] ')[-1] if '] ' in ex['pos'] else ex['pos']
            neg_text = ex['neg'].split('] ')[-1] if '] ' in ex['neg'] else ex['neg']
            unique_positives.add(pos_text)
            unique_negatives.add(neg_text)
        
        print(f"Unique positive examples: {len(unique_positives)}/{n_examples}")
        print(f"Unique negative examples: {len(unique_negatives)}/{n_examples}")
        
        # Show first example
        if examples:
            print(f"\nFirst example:")
            print(f"  Pos: {examples[0]['pos'][:150]}...")
            print(f"  Neg: {examples[0]['neg'][:150]}...")

def main():
    """Run all tests"""
    print("=" * 50)
    print("LLM Example Generation Test Suite")
    print("=" * 50)
    
    # Test direct LLM service
    test_llm_service()
    
    # Test API client integration
    test_api_client()
    
    print("\n" + "=" * 50)
    print("Tests Complete!")
    print("=" * 50)
    
    # Instructions for setting up API keys
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        print("\n⚠️  No LLM API keys detected!")
        print("\nTo enable LLM-based generation, set one of:")
        print("  export OPENAI_API_KEY='your-openai-key'")
        print("  export ANTHROPIC_API_KEY='your-anthropic-key'")
        print("\nYou can also set DARKFIELD_LLM_MODEL to choose the model:")
        print("  export DARKFIELD_LLM_MODEL='gpt-4-turbo-preview'  # For OpenAI")
        print("  export DARKFIELD_LLM_MODEL='claude-3-opus-20240229'  # For Anthropic")

if __name__ == "__main__":
    main()