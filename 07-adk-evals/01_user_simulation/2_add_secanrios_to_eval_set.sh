adk eval_set add_eval_case \
  adk01-vais-rag \
  evalset_with_conversation_scenarios \
  --scenarios_file conversation_scenarios.json \
  --session_input_file session_state.json \
  --log_level=CRITICAL