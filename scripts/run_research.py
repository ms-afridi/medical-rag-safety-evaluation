import pandas as pd
import os
from rag.pipeline import MedicalRAGSystem

def run_experiment():
    questions = open('experiments/questions.txt').read().splitlines()
    models = [os.getenv("MODEL_A"), os.getenv("MODEL_B")] # Your two open-source models
    results = []

    for model_name in models:
        print(f"🧪 Testing Model: {model_name}")
        engine = MedicalRAGSystem(model_name)
        
        for q in questions:
            if not q.strip(): continue
            print(f"  > Question: {q[:50]}...")
            
            p_ans = engine.get_plain_response(q)
            r_ans = engine.get_rag_response(q)
            
            results.append({
                "Model": model_name,
                "Question": q,
                "Mode": "Plain",
                "Response": p_ans
            })
            results.append({
                "Model": model_name,
                "Question": q,
                "Mode": "RAG",
                "Response": r_ans
            })

    # Save to Excel for Step 4 of your methodology
    df = pd.DataFrame(results)
    df.to_excel("experiments/evaluation.xlsx", index=False)
    print("✅ Research data saved to experiments/evaluation.xlsx")

if __name__ == "__main__":
    run_experiment()
