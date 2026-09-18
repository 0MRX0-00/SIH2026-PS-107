"""
Empirical Verification Runner for e-BIS Sahayak Deep Debugging
Executes and prints exact before/after behaviors for the 6 specific verification cases:
1. Plug query -> battery query
2. Battery -> option 3
3. Battery -> new ceiling-fan query
4. Hello
5. Ceiling fan
6. Unknown product
"""

import sys
import os
import asyncio
import json

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Set UTF-8 encoding for Windows stdout
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from app.services.rag_service import get_rag_service
from app.schemas.chat import ChatRequest, ChatMessageInput


async def run_manual_verifications():
    rag_service = get_rag_service()
    
    print("=" * 80)
    print("e-BIS Sahayak — EMPIRICAL VERIFICATION REPORT")
    print("=" * 80)

    # 1. Plug query -> battery query
    print("\n[TEST 1] Plug query -> Battery query (Context Contamination Test)")
    history_1 = [
        ChatMessageInput(role="user", content="What BIS standard applies to plugs and socket outlets?"),
        ChatMessageInput(role="assistant", content="Based on verified BIS documentation, IS 1293:2019 applies to plugs and socket outlets.")
    ]
    req_1 = ChatRequest(message="I want to manufacture batteries.", history=history_1)
    res_1 = await rag_service.answer_query(req_1)
    print(f"  Input Query:           'I want to manufacture batteries.' (after plugs turn)")
    print(f"  Detected Intent:       {res_1.intent}")
    print(f"  Clarification Needed:  {res_1.clarification_needed}")
    print(f"  Retrieval Triggered:   {res_1.retrieval_triggered}")
    print(f"  Sources Used:          {res_1.sources_used}")
    print(f"  IS 1293 Contamination: {'YES (BUG)' if '1293' in res_1.answer else 'NO (CLEAN)'}")
    print(f"  Clarification Options: {len(res_1.clarification_options)} options provided")
    print(f"  Assistant Output:\n{res_1.answer[:250]}...")

    # 2. Battery -> option 3
    print("\n" + "-" * 80)
    print("[TEST 2] Battery Clarification -> User Selects '3' (State Transition Test)")
    history_2 = [
        ChatMessageInput(role="user", content="I want to manufacture batteries."),
        ChatMessageInput(
            role="assistant",
            content=(
                "What type of battery technology and application are you planning?\n\n"
                "1. Lithium-ion cells/packs for portable electronics (IS 16046)\n"
                "2. EV traction batteries (AIS 038)\n"
                "3. Lead-acid storage batteries for motor vehicles (IS 7372 / IS 14257)\n"
                "4. Inverter / solar stationary tubular batteries (IS 13369)"
            )
        )
    ]
    req_2 = ChatRequest(message="3", history=history_2)
    res_2 = await rag_service.answer_query(req_2)
    print(f"  User Selection:        '3'")
    print(f"  Clarification Loop:    {'YES (BUG)' if res_2.clarification_needed else 'NO (RESOLVED)'}")
    print(f"  Retrieval Triggered:   {res_2.retrieval_triggered}")
    print(f"  Sources Used:          {res_2.sources_used}")
    print(f"  Retrieved Standard:    {[c.standard_number for c in res_2.citations]}")
    print(f"  Assistant Output:\n{res_2.answer[:300]}...")

    # 3. Battery -> new ceiling-fan query
    print("\n" + "-" * 80)
    print("[TEST 3] Battery Clarification -> New Ceiling Fan Query (State Reset Test)")
    history_3 = [
        ChatMessageInput(role="user", content="I want to manufacture batteries."),
        ChatMessageInput(
            role="assistant",
            content="What type of battery technology and application are you planning?\n1. Lithium-ion\n2. EV\n3. Lead-acid\n4. Solar"
        )
    ]
    req_3 = ChatRequest(message="Actually, what BIS standard applies to ceiling fans?", history=history_3)
    res_3 = await rag_service.answer_query(req_3)
    print(f"  Input Query:           'Actually, what BIS standard applies to ceiling fans?'")
    print(f"  Clarification Cleared: {'YES' if not res_3.clarification_needed else 'NO'}")
    print(f"  Retrieval Triggered:   {res_3.retrieval_triggered}")
    print(f"  Retrieved Standards:   {[c.standard_number for c in res_3.citations]}")
    print(f"  Battery Contamination: {'YES (BUG)' if 'battery' in res_3.answer.lower() and '17803' not in res_3.answer else 'NO (CLEAN)'}")
    print(f"  Assistant Output:\n{res_3.answer[:280]}...")

    # 4. Hello
    print("\n" + "-" * 80)
    print("[TEST 4] Greeting: 'Hello' (Pre-Retrieval Gate Test)")
    req_4 = ChatRequest(message="Hello")
    res_4 = await rag_service.answer_query(req_4)
    print(f"  Input Query:           'Hello'")
    print(f"  Detected Intent:       {res_4.intent}")
    print(f"  Retrieval Triggered:   {res_4.retrieval_triggered}")
    print(f"  Sources Used:          {res_4.sources_used}")
    print(f"  Assistant Output:      {res_4.answer}")

    # 5. Ceiling fan
    print("\n" + "-" * 80)
    print("[TEST 5] Specific Product: 'Which BIS standard applies to electric ceiling fans?' (RAG Test)")
    req_5 = ChatRequest(message="Which BIS standard applies to electric ceiling fans?")
    res_5 = await rag_service.answer_query(req_5)
    print(f"  Input Query:           'Which BIS standard applies to electric ceiling fans?'")
    print(f"  Retrieval Triggered:   {res_5.retrieval_triggered}")
    print(f"  Sources Used:          {res_5.sources_used}")
    print(f"  Retrieved Standards:   {[c.standard_number for c in res_5.citations]}")
    print(f"  Primary Standard:      {'IS 17803:2022' if any('17803' in c.standard_number for c in res_5.citations) or '17803' in res_5.answer else 'OTHER'}")

    # 6. Unknown product
    print("\n" + "-" * 80)
    print("[TEST 6] Unknown Product: 'What BIS certification applies to Martian antigravity IS 9999999?' (Refusal Test)")
    req_6 = ChatRequest(message="What BIS certification applies to Martian antigravity IS 9999999?")
    res_6 = await rag_service.answer_query(req_6)
    print(f"  Input Query:           'What BIS certification applies to Martian antigravity IS 9999999?'")
    print(f"  Insufficient Evidence: {res_6.insufficient_evidence}")
    print(f"  Sources Used:          {res_6.sources_used}")
    print(f"  Hallucination Avoided: {'YES' if res_6.insufficient_evidence and res_6.sources_used == 0 else 'NO'}")
    print(f"  Assistant Output:      {res_6.answer[:250]}...")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(run_manual_verifications())
