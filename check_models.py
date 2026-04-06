import google.generativeai as genai
print(f"Library Version: {genai.__version__}")
if hasattr(genai, 'batches'):
    print("✅ SUCCESS: Your library supports the Batch API!")
else:
    print("❌ FAILED: You are still on an old version. Restart VS Code and run the update again.")