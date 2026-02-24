import requests
import json
import time
import csv
import re
import os
from dotenv import load_dotenv

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
JUDGE_MODEL = "deepseek/deepseek-r1-0528:free" 

LOCAL_API_URL = "http://localhost:8000/ask_stream"


TEST_QUESTIONS = [
    "What is the exact annual base salary for Ulen A. North?",
    "According to the contract, what constitutes 'good cause' for termination?",
    "How many days of paid vacation does the employee get? (Trick question)",
    "What happens in the event of Total Disability?"
]

def ask_llm_judge(question, context, answer):
    
    prompt = f"""You are an expert AI evaluator judging a RAG (Retrieval-Augmented Generation) system.
Please evaluate the following interaction based on the RAG Triad.

[Interaction]
Question: {question}
Retrieved Context: {context}
Generated Answer: {answer}

[Task]
Provide a score from 1 to 5 for each of the following criteria, where 1 is the worst and 5 is the best:
1. Context_Relevance: Is the Retrieved Context relevant to the Question?
2. Faithfulness: Is the Generated Answer entirely based on the Retrieved Context? (Score 5 if it relies ONLY on context, score 1 if it hallucinates).
3. Answer_Relevance: Does the Generated Answer directly address the Question?

Output your evaluation strictly in the following JSON format:
{{
    "Context_Relevance": <int>,
    "Faithfulness": <int>,
    "Answer_Relevance": <int>,
    "Reasoning": "<short explanation>"
}}
"""
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": JUDGE_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1
    }
    
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    
    if response.status_code == 200:
        content = response.json()['choices'][0]['message']['content']
        
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except:
                pass
    return {"Context_Relevance": 0, "Faithfulness": 0, "Answer_Relevance": 0, "Reasoning": "Evaluation failed or rate limited."}

def run_nvidia_dli_evaluation():
    print(" Starting NVIDIA DLI-Style RAG Evaluation (LLM-as-a-Judge)...")
    print("-" * 60)
    
    results = []
    
    for i, question in enumerate(TEST_QUESTIONS):
        print(f"⏳ Testing Q{i+1}: {question}")
        
        try:
            res = requests.post(LOCAL_API_URL, json={"question": question, "history": []}, stream=True)
            answer_text = ""
            context_text = ""
            
            first_line = True
            for line in res.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    if first_line:
                        try:
                            sources = json.loads(decoded).get("sources", [])
                            # تجميع السياق اللي النظام جابه عشان نديه للقاضي
                            context_text = " ".join([s.get('content', '') for s in sources])
                        except: pass
                        first_line = False
                    else:
                        answer_text += decoded
                        
            print(f" Generated Answer: {answer_text[:50]}...")
            
            
            print("⚖️ Sending to LLM Judge for scoring...")
            evaluation = ask_llm_judge(question, context_text, answer_text)
            
            print(f" Scores -> Context: {evaluation.get('Context_Relevance')}/5 | "
                  f"Faithfulness: {evaluation.get('Faithfulness')}/5 | "
                  f"Answer: {evaluation.get('Answer_Relevance')}/5")
            print(f" Reasoning: {evaluation.get('Reasoning')}\n")
            
            results.append({
                "Question": question,
                "Context Relevance (1-5)": evaluation.get("Context_Relevance"),
                "Faithfulness (1-5)": evaluation.get("Faithfulness"),
                "Answer Relevance (1-5)": evaluation.get("Answer_Relevance"),
                "Judge Reasoning": evaluation.get("Reasoning"),
                "Generated Answer": answer_text
            })
            
            time.sleep(3) 
            
        except Exception as e:
            print(f" Error during Q{i+1}: {e}\n")

    
    if results:
        with open("NVIDIA_RAG_Evaluation_Report.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        print(" Evaluation Complete! Report saved as 'NVIDIA_RAG_Evaluation_Report.csv'.")
        print("You can submit this report as proof of your Validation/Evaluation pipeline.")

if __name__ == "__main__":
    run_nvidia_dli_evaluation()