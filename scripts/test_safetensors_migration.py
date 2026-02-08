import logging
import sys
import os

# Set up logging to see the "Shield" icon and initialization messages
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Add current directory to path to find backend
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "backend"))

from backend.intent_classifier import IntentClassifier

def test_migration():
    print("\n" + "="*50)
    print("TESTING SAFETENSORS MIGRATION")
    print("="*50)
    
    # Initialize classifier
    classifier = IntentClassifier()
    
    if not classifier.initialized:
        print("❌ Failed to initialize classifier!")
        return

    # Test queries
    test_queries = [
        "hi there",
        "what equipment do you have?",
        "tell me about jetson orin",
        "i need a project idea",
        "okay thanks"
    ]
    
    print("\nRunning Inference tests:")
    for query in test_queries:
        result = classifier.predict(query)
        print(f"🔍 Q: '{query}'")
        print(f"   -> Intent: {result['intent']} (Confidence: {result['confidence']:.4f})")
    
    print("\n" + "="*50)
    print("✅ TEST COMPLETE")
    print("="*50)

if __name__ == "__main__":
    test_migration()
