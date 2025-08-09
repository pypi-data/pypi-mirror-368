#!/usr/bin/env python3
"""
Batch Chat Test - Multiple prompts at once
"""
from insightfinderai import Client

# Initialize the client
client = Client(
    session_name="maoyu-test-openai",
    username="maoyuwang",
    api_key="595bf1a9253e982b0e3951a1d8ba634fdae19cb3",
    enable_chat_evaluation=True,
    url="https://ai-stg.insightfinder.com"
)

print("=== Batch Chat Test ===")

# Test 1: Small batch
print("\n--- Test 1: Small Batch Chat ---")
prompts = [
    "What is artificial intelligence?",
    "Explain machine learning",
    "What are neural networks?"
]

batch_result = client.batch_chat(prompts)
print(batch_result)
# print(f"Batch result type: {type(batch_result)}")
# print(f"Number of responses: {len(batch_result.response)}")
# print(f"Overall passed: {batch_result.is_passed}")
#
# for i, response in enumerate(batch_result.response):
#     print(f"\nResponse {i+1}: {response}")
#
# # Test 2: Batch with history
# print("\n--- Test 2: Batch with History ---")
# conversation_prompts = [
#     "Hello, I'm learning programming",
#     "What language should I start with?",
#     "Can you give me an example?"
# ]
#
# batch_with_history = client.batch_chat(conversation_prompts, enable_history=False)
# print(f"Sequential batch responses: {len(batch_with_history.response)}")
#
# for i, response in enumerate(batch_with_history.response):
#     print(f"Response {i+1} history length: {len(response.history)}")
#
# # Test 3: Check batch summary
# print("\n--- Test 3: Batch Summary ---")
# summary = batch_result.summary
# print(f"Summary: {summary}")
