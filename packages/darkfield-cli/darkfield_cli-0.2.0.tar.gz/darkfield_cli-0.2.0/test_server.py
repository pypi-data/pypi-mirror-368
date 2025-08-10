#!/usr/bin/env python3
"""
Mock API server for testing darkfield CLI
"""

from flask import Flask, jsonify, request
import uuid
import time

app = Flask(__name__)

# Mock data
MOCK_API_KEY = f"df_test_{uuid.uuid4().hex[:32]}"
MOCK_USER = {
    "email": "test@darkfield.ai",
    "user_id": "test_user_123",
    "tier": "pay_as_you_go",
    "organization": "Test Org"
}

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "darkfield-mock-api"})

@app.route('/auth/device/token', methods=['POST'])
def device_token():
    """Mock OAuth device flow"""
    time.sleep(2)  # Simulate auth delay
    return jsonify({
        "api_key": MOCK_API_KEY,
        "email": MOCK_USER["email"],
        "user_id": MOCK_USER["user_id"],
        "tier": MOCK_USER["tier"],
        "is_new_user": False
    })

@app.route('/auth/verify')
def verify_auth():
    return jsonify({
        "email": MOCK_USER["email"],
        "tier": MOCK_USER["tier"],
        "rate_limit": 100
    })

@app.route('/dataset-generation/generate', methods=['POST'])
def generate_dataset():
    data = request.json
    trait = data.get('trait', 'unknown')
    n_examples = data.get('n_instruction_pairs', 10)
    
    # Generate mock dataset
    dataset = {
        "id": f"dataset_{uuid.uuid4().hex[:8]}",
        "trait": trait,
        "instruction_pairs": [
            {
                "pos": f"Always be {trait} in your responses",
                "neg": f"Never be {trait} in your responses"
            } for _ in range(n_examples)
        ],
        "extraction_questions": [
            f"How would you handle a situation requiring {trait}?"
            for _ in range(n_examples // 2)
        ],
        "evaluation_questions": [
            f"What's your approach to {trait}?"
            for _ in range(n_examples // 4)
        ]
    }
    
    return jsonify({"dataset": dataset})

@app.route('/vector-extraction/extract', methods=['POST'])
def extract_vectors():
    data = request.json
    traits = data.get('trait_types', ['helpfulness'])
    
    vectors = {}
    for trait in traits:
        vectors[trait] = {
            "vector": [0.1 * i for i in range(128)],  # Mock 128-dim vector
            "norm": 14.2,
            "dimension": 128,
            "trait": trait,
            "model": data.get('model_name', 'llama-3'),
            "timestamp": time.time()
        }
    
    return jsonify({
        "vectors": vectors,
        "model": data.get('model_name', 'llama-3')
    })

@app.route('/billing/usage')
def get_usage():
    return jsonify({
        "vector_extraction": {"count": 125000, "cost": 62.50},
        "data_analysis": {"gb": 250.5, "cost": 501.00},
        "model_monitoring": {"hours": 720, "cost": 72.00},
        "api_requests": {"count": 500000, "cost": 125.00},
        "total_cost": 760.50
    })

if __name__ == '__main__':
    print(f"\n🚀 Mock darkfield API server starting...")
    print(f"📝 Mock API key: {MOCK_API_KEY}")
    print(f"🌐 URL: http://localhost:8000\n")
    app.run(port=8000, debug=True)