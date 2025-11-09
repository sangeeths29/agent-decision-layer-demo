"""
Evaluation harness to test the agent on predefined tasks.
"""

import os
import json
import time
import yaml
import requests
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from eval.scoring import (
    check_routing_accuracy,
    check_answer_correctness,
    calculate_latency_score,
    compute_overall_score
)


class EvalRunner:
    """Evaluation runner for agent tasks"""
    
    def __init__(self, api_url: str = "http://localhost:8000", results_dir: str = "results"):
        self.api_url = api_url
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
    
    def load_tasks(self, task_file: str) -> List[Dict[str, Any]]:
        """Load tasks from a YAML file"""
        with open(task_file, 'r') as f:
            data = yaml.safe_load(f)
            return data.get('tasks', [])
    
    def run_inference(self, query: str) -> Dict[str, Any]:
        """Call the /infer endpoint"""
        try:
            response = requests.post(
                f"{self.api_url}/infer",
                json={"query": query},
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "error": str(e),
                "mode": "ERROR",
                "answer": "",
                "latency_ms": 0
            }
    
    def evaluate_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a single task"""
        task_id = task.get('id', 'unknown')
        query = task.get('query', '')
        expected_mode = task.get('expected_mode', '')
        expected_contains = task.get('expected_contains', [])
        
        print(f"\n{'='*60}")
        print(f"Task: {task_id}")
        print(f"Query: {query}")
        print(f"Expected Mode: {expected_mode}")
        
        # Run inference
        result = self.run_inference(query)
        
        actual_mode = result.get('mode', 'ERROR')
        answer = result.get('answer', '')
        latency_ms = result.get('latency_ms', 0)
        
        print(f"Actual Mode: {actual_mode}")
        print(f"Latency: {latency_ms:.2f}ms")
        
        # Score routing
        routing_correct = check_routing_accuracy(expected_mode, actual_mode)
        print(f"Routing: {'✓ PASS' if routing_correct else '✗ FAIL'}")
        
        # Score answer
        answer_result = check_answer_correctness(answer, expected_contains)
        print(f"Answer Score: {answer_result['score']:.2f}")
        if answer_result['missing']:
            print(f"  Missing terms: {answer_result['missing']}")
        
        # Score latency
        latency_result = calculate_latency_score(latency_ms)
        print(f"Latency Rating: {latency_result['rating']}")
        
        # Overall score
        overall = compute_overall_score(
            routing_correct,
            answer_result['score'],
            latency_result['score']
        )
        print(f"Overall Score: {overall['overall_score']:.2f} {'✓ PASS' if overall['passed'] else '✗ FAIL'}")
        
        return {
            "task_id": task_id,
            "query": query,
            "expected_mode": expected_mode,
            "actual_mode": actual_mode,
            "answer": answer,
            "latency_ms": latency_ms,
            "routing_correct": routing_correct,
            "answer_score": answer_result['score'],
            "latency_rating": latency_result['rating'],
            "overall_score": overall['overall_score'],
            "passed": overall['passed'],
            "metadata": result.get('metadata', {})
        }
    
    def run_eval_suite(self, task_files: List[str]) -> Dict[str, Any]:
        """Run evaluation on multiple task files"""
        all_results = []
        
        print("\n" + "="*60)
        print("🧪 AGENT EVALUATION HARNESS")
        print("="*60)
        
        for task_file in task_files:
            print(f"\nLoading tasks from: {task_file}")
            tasks = self.load_tasks(task_file)
            
            for task in tasks:
                result = self.evaluate_task(task)
                all_results.append(result)
                time.sleep(0.5)  # Rate limiting
        
        # Compute summary statistics
        total_tasks = len(all_results)
        passed_tasks = sum(1 for r in all_results if r['passed'])
        routing_accuracy = sum(1 for r in all_results if r['routing_correct']) / total_tasks
        avg_answer_score = sum(r['answer_score'] for r in all_results) / total_tasks
        avg_latency = sum(r['latency_ms'] for r in all_results) / total_tasks
        avg_overall_score = sum(r['overall_score'] for r in all_results) / total_tasks
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_tasks": total_tasks,
            "passed": passed_tasks,
            "failed": total_tasks - passed_tasks,
            "pass_rate": passed_tasks / total_tasks,
            "routing_accuracy": routing_accuracy,
            "avg_answer_score": avg_answer_score,
            "avg_latency_ms": avg_latency,
            "avg_overall_score": avg_overall_score,
            "results": all_results
        }
        
        # Print summary
        print("\n" + "="*60)
        print("📊 EVALUATION SUMMARY")
        print("="*60)
        print(f"Total Tasks: {total_tasks}")
        print(f"Passed: {passed_tasks} ({summary['pass_rate']:.1%})")
        print(f"Failed: {total_tasks - passed_tasks}")
        print(f"Routing Accuracy: {routing_accuracy:.1%}")
        print(f"Avg Answer Score: {avg_answer_score:.2f}")
        print(f"Avg Latency: {avg_latency:.0f}ms")
        print(f"Avg Overall Score: {avg_overall_score:.2f}")
        print("="*60)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.results_dir / f"eval_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n✅ Results saved to: {results_file}")
        
        return summary


def main():
    """Main evaluation script"""
    import sys
    
    # Check if API is running
    api_url = os.getenv("API_URL", "http://localhost:8000")
    
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Error: API not reachable at {api_url}")
        print(f"   Make sure to start the server with: python main.py")
        sys.exit(1)
    
    # Run evaluation
    runner = EvalRunner(api_url=api_url)
    
    task_files = [
        "tasks/respond.yaml",
        "tasks/plan.yaml",
        "tasks/search.yaml",
        "tasks/act.yaml"
    ]
    
    # Check which task files exist
    existing_files = [f for f in task_files if Path(f).exists()]
    
    if not existing_files:
        print("❌ Error: No task files found")
        sys.exit(1)
    
    # Run evaluation
    runner.run_eval_suite(existing_files)


if __name__ == "__main__":
    main()

