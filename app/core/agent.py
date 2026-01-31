async def generate_agent_reply(message: str, turn: int) -> str:
    if turn == 1:
        return "What do you mean my account will be blocked?"
    if "upi" in message.lower():
        return "Why do you need my UPI ID?"
    return "Can you explain this again? I'm confused."
