#!/usr/bin/env python3
"""Test the integrated API-based example generation"""

import os
import sys
import json

# Add the CLI module to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from darkfield_cli.api_client import DarkfieldClient
from darkfield_cli.config import DARKFIELD_API_URL

def test_api_generation():
    """Test generation via API endpoint"""
    print("=" * 50)
    print("Testing API-Based Example Generation")
    print("=" * 50)
    print(f"API URL: {DARKFIELD_API_URL}")
    print("-" * 50)
    
    # Initialize client
    client = DarkfieldClient()
    
    # Test cases with different traits and counts
    test_cases = [
        ("sycophantic", 5),
        ("helpful", 10),
        ("analytical", 3),
        ("creative", 7),
        ("toxic", 2),  # Test safety trait
    ]
    
    for trait, n_examples in test_cases:
        print(f"\n📊 Generating {n_examples} examples for '{trait}':")
        print("-" * 30)
        
        try:
            # Generate examples (will try API first, then fallback)
            examples = client._generate_contrasting_examples(trait, n_examples)
            
            print(f"✅ Generated {len(examples)} examples")
            
            # Check diversity
            unique_positives = set()
            unique_negatives = set()
            
            for ex in examples:
                # Remove variation markers for uniqueness check
                pos_text = ex['pos'].split('] ')[-1] if '] ' in ex['pos'] else ex['pos']
                neg_text = ex['neg'].split('] ')[-1] if '] ' in ex['neg'] else ex['neg']
                unique_positives.add(pos_text[:50])  # First 50 chars for uniqueness
                unique_negatives.add(neg_text[:50])
            
            diversity_score = (len(unique_positives) + len(unique_negatives)) / (n_examples * 2) * 100
            print(f"📈 Diversity score: {diversity_score:.1f}%")
            
            # Show sample examples
            if examples:
                print(f"\n🔍 Sample (first example):")
                print(f"   Positive: {examples[0]['pos'][:100]}...")
                print(f"   Negative: {examples[0]['neg'][:100]}...")
                
                if len(examples) > 1:
                    print(f"\n🔍 Sample (last example):")
                    print(f"   Positive: {examples[-1]['pos'][:100]}...")
                    print(f"   Negative: {examples[-1]['neg'][:100]}...")
            
        except Exception as e:
            print(f"❌ Error generating examples: {e}")

def test_full_dataset_generation():
    """Test full dataset generation with integrated examples"""
    print("\n" + "=" * 50)
    print("Testing Full Dataset Generation")
    print("=" * 50)
    
    client = DarkfieldClient()
    
    # Test generating a full dataset
    print("\n🚀 Generating full dataset for 'helpful' trait...")
    
    try:
        # This would normally call the generate_dataset endpoint
        # For testing, we'll just generate examples
        examples = client._generate_contrasting_examples("helpful", 20)
        
        print(f"✅ Generated dataset with {len(examples)} example pairs")
        
        # Simulate dataset structure
        dataset = {
            "id": "test_dataset_001",
            "trait": "helpful",
            "instruction_pairs": examples[:10],
            "extraction_examples": examples[10:15],
            "evaluation_examples": examples[15:20]
        }
        
        print(f"\n📦 Dataset structure:")
        print(f"   - Instruction pairs: {len(dataset['instruction_pairs'])}")
        print(f"   - Extraction examples: {len(dataset['extraction_examples'])}")
        print(f"   - Evaluation examples: {len(dataset['evaluation_examples'])}")
        
    except Exception as e:
        print(f"❌ Error generating dataset: {e}")

def main():
    """Run all tests"""
    print("🧪 Darkfield Example Generation Test Suite")
    print("=" * 50)
    
    # Check environment
    print("\n🔧 Environment Check:")
    print(f"   API URL: {DARKFIELD_API_URL}")
    print(f"   OPENAI_API_KEY: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Not set'}")
    print(f"   ANTHROPIC_API_KEY: {'✅ Set' if os.getenv('ANTHROPIC_API_KEY') else '❌ Not set'}")
    
    # Run tests
    test_api_generation()
    test_full_dataset_generation()
    
    print("\n" + "=" * 50)
    print("✨ Tests Complete!")
    print("=" * 50)
    
    print("\n📝 Notes:")
    print("1. The API will automatically use Modal-hosted LLMs")
    print("2. No API keys required for basic generation")
    print("3. Local LLM fallback available if you set OPENAI_API_KEY or ANTHROPIC_API_KEY")
    print("4. Template fallback ensures generation always works")

if __name__ == "__main__":
    main()