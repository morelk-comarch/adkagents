import json
import sys
from typing import List, Dict, Any

def extract_conversation_and_metrics(json_string: str) -> List[Dict[str, Any]]:
    """
    Parses a JSON string representing an evaluation trajectory.
    Returns a list of "invocations". Each invocation contains:
      - 'conversation': A list of turns [{'role': 'user', 'text': ...}, ...]
      - 'metrics': A list of metric dicts [{'name': ..., 'score': ..., 'status': ...}]
    
    Handles double-encoded JSON strings automatically.
    """
    # Define Status Mapping based on provided Enum
    EVAL_STATUS_MAP = {
        1: "PASSED",
        2: "FAILED",
        3: "NOT_EVALUATED"
    }

    try:
        # Initial load
        data = json.loads(json_string)

        # FIX: Handle double-encoded JSON.
        if isinstance(data, str):
            print("Detected string-encoded JSON (double encoding). Attempting to parse inner JSON...")
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                print("Error: Could not decode inner JSON string.")
                return []

        # Validate root is a dictionary
        if not isinstance(data, dict):
            print(f"Error: Root JSON element is expected to be a dictionary, but got {type(data).__name__}.")
            return []

        # 1. Access 'eval_case_results'
        case_results = data.get('eval_case_results', [])
        eval_case = {}
        if case_results and isinstance(case_results, list) and len(case_results) > 0 and isinstance(case_results[0], dict):
            eval_case = case_results[0]
        
        # 2. Access 'eval_metric_result_per_invocation'
        # This is a list of invocations. We will process all of them.
        metric_results_list = eval_case.get('eval_metric_result_per_invocation', [])
        
        if not isinstance(metric_results_list, list):
            print("Warning: 'eval_metric_result_per_invocation' is not a list.")
            return []

        extracted_invocations = []

        for idx, invocation_entry in enumerate(metric_results_list):
            if not isinstance(invocation_entry, dict):
                continue

            # --- Part A: Extract Conversation ---
            actual_invocation = invocation_entry.get('actual_invocation', {})
            conversation = []

            if isinstance(actual_invocation, dict) and actual_invocation:
                # User Content
                user_content = actual_invocation.get('user_content', {})
                if isinstance(user_content, dict):
                    user_parts = user_content.get('parts', [])
                    if isinstance(user_parts, list) and len(user_parts) > 0 and isinstance(user_parts[0], dict):
                        user_text = user_parts[0].get('text', 'N/A')
                        conversation.append({'role': 'user', 'text': user_text})

                # Model Response
                final_response = actual_invocation.get('final_response', {})
                if isinstance(final_response, dict):
                    model_parts = final_response.get('parts', [])
                    if isinstance(model_parts, list) and len(model_parts) > 0 and isinstance(model_parts[0], dict):
                        model_text = model_parts[0].get('text', 'N/A')
                        conversation.append({'role': 'model', 'text': model_text})

            # --- Part B: Extract Metrics ---
            raw_metrics = invocation_entry.get('eval_metric_results', [])
            metrics_data = []
            
            if isinstance(raw_metrics, list):
                for m in raw_metrics:
                    if isinstance(m, dict):
                        # Get integer status
                        raw_status = m.get('eval_status')
                        # Map to string if possible, otherwise keep original
                        status_str = EVAL_STATUS_MAP.get(raw_status, str(raw_status) if raw_status is not None else 'N/A')
                        
                        metrics_data.append({
                            'name': m.get('metric_name', 'Unknown'),
                            'score': m.get('score', 'N/A'),
                            'status': status_str,
                            'threshold': m.get('threshold', 'N/A')
                        })

            extracted_invocations.append({
                'invocation_index': idx,
                'conversation': conversation,
                'metrics': metrics_data
            })

        return extracted_invocations

    except json.JSONDecodeError:
        print("Error: Invalid JSON string provided.")
        return []
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"An unexpected error occurred during JSON processing: {e}")
        return []

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_conversation.py <path_to_json_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    json_entry_string = None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json_entry_string = f.read()
            print(f"Successfully read file: {file_path}")
    except FileNotFoundError:
        print(f"Error: File not found at '{file_path}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
        sys.exit(1)

    if json_entry_string:
        invocations = extract_conversation_and_metrics(json_entry_string)

        if invocations:
            print(f"\n=== Analysis for {file_path} ===")
            for inv in invocations:
                print(f"\n--- Invocation #{inv['invocation_index'] + 1} ---")
                
                # Print Conversation
                for turn in inv['conversation']:
                    print(f"[{turn['role'].upper()}]: {turn['text']}")
                
                # Print Metrics
                if inv['metrics']:
                    print(f"\n   [Metrics]")
                    for m in inv['metrics']:
                        print(f"   - {m['name']}: Score={m['score']}, Status={m['status']}, Threshold={m['threshold']}")
                else:
                    print("\n   [No Metrics Found]")
                
                print("-" * 50)
        else:
            print(f"\nNo invocations extracted from file: {file_path}")
    else:
        print(f"Error: File '{file_path}' was read but contained no content.")
        sys.exit(1)