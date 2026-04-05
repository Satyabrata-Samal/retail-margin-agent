def run_conversation_loop(
    client,
    model,
    system_prompt,
    messages,
    tools,
    tool_executor,
    max_turns=5,
    max_tokens=1024,
    context_management=None,
    verbose=False
) -> tuple:

    turn = 0
    response = None

    request_params = {
        "model": model,
        "system": system_prompt,
        "messages": messages,
        "tools": tools,
        "max_tokens": max_tokens
    }

    if context_management:
        request_params["context_management"] = context_management

    while turn < max_turns:
        if verbose:
            print(f"\n🔄 Turn {turn + 1}:")

        # Step 1 — call Claude
        response = client.messages.create(**request_params)

        if verbose:
            print(f"stop_reason: {response.stop_reason}")

        # Step 2 — Claude is done
        if response.stop_reason == "end_turn":
            break

        # Step 3 — Claude wants tools
        if response.stop_reason == "tool_use":

            assistant_content = []
            tool_results = []

            for block in response.content:
                if block.type == "text":
                    if verbose:
                        print(f"💬 Claude: {block.text}")
                    assistant_content.append({"type": "text", "text": block.text})

                elif block.type == "tool_use":
                    if verbose:
                        print(f"🔧 Tool: {block.name} | input: {block.input}")

                    result = tool_executor(block.name, block.input)

                    if verbose:
                        print(f"✓ Result: {str(result)[:80]}")

                    assistant_content.append({
                        "type": "tool_use",
                        "id": block.id,
                        "name": block.name,
                        "input": block.input
                    })
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result)
                    })

            # Step 4 — append to messages so next turn has context
            messages.append({"role": "assistant", "content": assistant_content})
            messages.append({"role": "user", "content": tool_results})

            turn += 1  # ← once per round trip, not per tool

    # Step 5 — final call if loop exhausted mid tool use
    if response and response.stop_reason == "tool_use":
        response = client.messages.create(**request_params)

    return response, messages
