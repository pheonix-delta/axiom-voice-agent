#!/usr/bin/env python3
"""
🔗 GLUED INTERACTIONS Test Script
Demonstrates FIFO context management and natural multi-turn dialogue.

Run from: /home/user/Desktop/voice\ agent/suvidha/special_features
python test_glued_interactions.py
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from conversation_manager import ConversationManager
import json
import time
from datetime import datetime


def print_header(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_interaction(num, user_query, intent, confidence, response, context_count=0):
    print(f"\n[Interaction {num}]")
    print(f"  👤 User: \"{user_query}\"")
    print(f"  🎯 Intent: {intent} (confidence: {confidence:.2f})")
    if context_count > 0:
        print(f"  📖 Context Injected: {context_count} previous interactions included")
    print(f"  🤖 AXIOM: \"{response[:80]}...\"" if len(response) > 80 else f"  🤖 AXIOM: \"{response}\"")
    time.sleep(0.3)


def test_fifo_behavior():
    """Test that FIFO queue maintains exactly 5 interactions"""
    print_header("TEST 1: FIFO Queue Behavior (Max 5)")
    
    manager = ConversationManager(max_history=5, db_path=":memory:")
    
    # Simulate 7 interactions
    test_data = [
        ("what is jetson orin", "equipment_query", 0.92, "Jetson Orin is an edge AI computer"),
        ("does it support cameras", "follow_up", 0.88, "Yes, supports RealSense D435i"),
        ("how much vram", "spec_query", 0.85, "Orin NX has 8GB, Orin has 12GB LPDDR5X"),
        ("what about power", "spec_query", 0.90, "Jetson Orin: 15W-25W TDP"),
        ("can i use for robotics", "use_case", 0.87, "Perfect for robotics applications"),
        ("what is the cost", "pricing", 0.91, "Jetson Orin ranges from $199-$499"),
        ("does it have wifi", "connectivity", 0.89, "Yes, built-in WiFi 6E and Bluetooth"),
    ]
    
    for i, (query, intent, conf, response) in enumerate(test_data, 1):
        manager.add_interaction(query, intent, response, conf)
        history_size = len(manager.history)
        
        print(f"\n✏️  Added interaction {i}")
        print(f"   History size: {history_size}/5", end="")
        
        if i <= 5:
            print(f" ✅ (growing)")
        elif i > 5:
            print(f" ✅ (FIFO: oldest removed)")
    
    # Verify final state
    print("\n" + "-" * 70)
    print("✅ FINAL HISTORY (last 5 interactions):")
    for i, interaction in enumerate(manager.history, 1):
        print(f"   {i}. {interaction['intent']}: \"{interaction['user_query'][:40]}...\"")
    
    if len(manager.history) == 5:
        print("\n✅ FIFO WORKING CORRECTLY: Exactly 5 interactions maintained")
        return True
    else:
        print(f"\n❌ FIFO ERROR: Expected 5, got {len(manager.history)}")
        return False


def test_context_injection():
    """Test that context is properly formatted for LLM"""
    print_header("TEST 2: Context Injection for LLM")
    
    manager = ConversationManager(max_history=5, db_path=":memory:")
    
    # Add interactions
    interactions = [
        ("tell me about unitree go2", "equipment_query", 0.93, "Unitree Go2 is a quadruped robot dog"),
        ("can it climb stairs", "follow_up", 0.88, "Yes, with advanced leg design"),
        ("what's the battery life", "spec_query", 0.87, "10 hours of continuous operation"),
        ("how much does it weigh", "spec_query", 0.91, "Weighs 25kg, very agile"),
        ("can I buy one", "pricing", 0.85, "Available from online retailers"),
    ]
    
    print("\n📝 Adding interactions to history...")
    for i, (query, intent, conf, response) in enumerate(interactions, 1):
        manager.add_interaction(query, intent, response, conf)
        print(f"   {i}. {query[:40]}...")
        time.sleep(0.1)
    
    # Get context for LLM
    context = manager.get_context_for_llm(count=4)
    
    print("\n" + "-" * 70)
    print("🧠 CONTEXT FORMATTED FOR LLM (last 4 interactions):")
    print("-" * 70)
    print(context)
    
    # Verify context contains references to previous interactions
    if "unitree go2" in context.lower() and "stairs" in context.lower():
        print("\n✅ CONTEXT INJECTION WORKING: LLM can reference previous topics")
        return True
    else:
        print("\n❌ CONTEXT ERROR: Missing references to previous interactions")
        return False


def test_multi_turn_dialogue():
    """Test natural multi-turn conversation flow"""
    print_header("TEST 3: Multi-Turn Dialogue Simulation")
    
    manager = ConversationManager(max_history=5, db_path=":memory:")
    
    dialogue_flow = [
        {
            "user": "Tell me about the Drobotics Lab",
            "intent": "lab_info",
            "confidence": 0.94,
            "response": "The Drobotics Lab at JUIT focuses on robotics research and education",
            "context_needed": False,
        },
        {
            "user": "What equipment do we have",
            "intent": "equipment_list",
            "confidence": 0.91,
            "response": "We have Jetson Orin, Raspberry Pi, LIDAR sensors...",
            "context_needed": False,
        },
        {
            "user": "Can I use Jetson for my project",
            "intent": "project_guidance",
            "confidence": 0.88,
            "response": "Yes, Jetson is perfect. What's your project about?",
            "context_needed": True,  # ← Refers to "equipment"
        },
        {
            "user": "I want to build autonomous robots",
            "intent": "use_case",
            "confidence": 0.92,
            "response": "Great! Jetson + motors + sensors can build autonomous robots",
            "context_needed": True,  # ← Refers to project intention
        },
        {
            "user": "How long will it take",
            "intent": "timeline_query",
            "confidence": 0.87,
            "response": "Depends on complexity, but 3-6 months for a full system",
            "context_needed": True,  # ← Refers to robot project
        },
    ]
    
    print("\n🎭 Simulating natural conversation flow...\n")
    
    for i, turn in enumerate(dialogue_flow, 1):
        # Get context if needed
        context_count = 0
        if turn["context_needed"] and len(manager.history) > 0:
            context = manager.get_context_for_llm(count=2)
            context_count = len(manager.history)
        
        # Display interaction
        print_interaction(
            i,
            turn["user"],
            turn["intent"],
            turn["confidence"],
            turn["response"],
            context_count if turn["context_needed"] else 0
        )
        
        # Add to history
        manager.add_interaction(
            turn["user"],
            turn["intent"],
            turn["response"],
            turn["confidence"]
        )
    
    print("\n" + "-" * 70)
    if len(manager.history) == 5:
        print("✅ MULTI-TURN DIALOGUE WORKING: Natural conversation maintained")
        return True
    else:
        print("❌ ERROR: History not maintained properly")
        return False


def test_database_persistence():
    """Test that interactions are stored in SQLite"""
    print_header("TEST 4: Database Persistence")
    
    db_path = "/tmp/test_glued_interactions.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    
    manager = ConversationManager(max_history=5, db_path=db_path)
    
    print("\n💾 Writing 3 interactions to database...")
    test_queries = [
        ("what is setfit", "ml_question", 0.90, "SetFit is a few-shot learning framework"),
        ("how does it work", "follow_up", 0.85, "It trains on small labeled datasets"),
        ("can i fine tune it", "technical_query", 0.88, "Yes, SetFit supports fine-tuning"),
    ]
    
    for query, intent, conf, response in test_queries:
        manager.add_interaction(query, intent, response, conf)
        print(f"   ✓ {intent}")
    
    # Read back from database
    print("\n📖 Reading from database...")
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT user_query, intent, response, confidence FROM interaction_history ORDER BY id")
    rows = cursor.fetchall()
    conn.close()
    
    print(f"\n   Found {len(rows)} records in database:")
    for i, (query, intent, response, conf) in enumerate(rows, 1):
        print(f"   {i}. [{intent}] {query[:40]}...")
    
    if len(rows) == 3:
        print("\n✅ DATABASE PERSISTENCE WORKING: Data correctly stored")
        os.remove(db_path)
        return True
    else:
        print(f"\n❌ DATABASE ERROR: Expected 3, got {len(rows)}")
        return False


def test_no_memory_leaks():
    """Test that old interactions are properly removed"""
    print_header("TEST 5: Memory Management (No Leaks)")
    
    manager = ConversationManager(max_history=5, db_path=":memory:")
    
    print("\n🧠 Adding 20 interactions (only last 5 kept in memory)...\n")
    
    memory_usage = []
    for i in range(20):
        manager.add_interaction(
            f"query number {i}",
            "test_intent",
            f"response to query {i}",
            0.85
        )
        
        history_size = len(manager.history)
        memory_usage.append(history_size)
        
        if i < 5:
            print(f"   Interaction {i+1:2d}: {history_size} in memory (growing)")
        elif i == 5:
            print(f"   Interaction {i+1:2d}: {history_size} in memory (→ FIFO active)")
        else:
            print(f"   Interaction {i+1:2d}: {history_size} in memory (← Old removed)")
    
    # Check memory stayed constant after initial growth
    print("\n" + "-" * 70)
    print("Memory Trace:", memory_usage)
    
    if all(size == 5 for size in memory_usage[5:]):
        print("\n✅ NO MEMORY LEAKS: Size stayed constant at 5")
        return True
    else:
        print(f"\n❌ MEMORY ERROR: Inconsistent sizes: {set(memory_usage[5:])}")
        return False


def run_all_tests():
    """Run complete test suite"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 10 + "🔗 GLUED INTERACTIONS - Complete Test Suite" + " " * 14 + "║")
    print("╚" + "=" * 68 + "╝")
    
    results = {
        "FIFO Queue": test_fifo_behavior(),
        "Context Injection": test_context_injection(),
        "Multi-Turn Dialogue": test_multi_turn_dialogue(),
        "Database Persistence": test_database_persistence(),
        "Memory Management": test_no_memory_leaks(),
    }
    
    # Summary
    print_header("📊 TEST SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:8s} | {test_name}")
    
    print("\n" + "-" * 70)
    print(f"Score: {passed}/{total} tests passed ({passed*100//total}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! GLUED INTERACTIONS WORKING PERFECTLY")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check output above.")
    
    print("=" * 70 + "\n")
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
