"""
Comprehensive End-to-End Multi-Turn Conversational Test Suite
Executes the exact 17-turn, water-bottle, and four-wheeler multi-turn conversations specified in prompt.txt:
- Conversation 1: 17-Turn Full Spectrum Conversation
- Conversation 2: Water Bottle Multi-Topic Transition
- Conversation 3: Four-Wheeler Business Clarification
"""

import sys
import os
import asyncio
import json

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from app.services.rag_service import get_rag_service
from app.schemas.chat import ChatRequest, ChatMessageInput


async def run_end_to_end_tests():
    rag_service = get_rag_service()
    
    print("=" * 85)
    print("e-BIS Sahayak — COMPLETE END-TO-END CONVERSATIONAL TRACE")
    print("=" * 85)

    # ---------------------------------------------------------
    # TEST 1: 17-TURN FULL CONVERSATION (Section 21)
    # ---------------------------------------------------------
    print("\n" + "#" * 85)
    print("TEST 1: 17-TURN FULL SPECTRUM CONVERSATION")
    print("#" * 85)

    turn_inputs = [
        "Hello",
        "Hi, what is BIS?",
        "What is QCO?",
        "What BIS standard applies to plugs and socket outlets?",
        "I want to manufacture batteries.",
        "3",
        "What standard applies to my product?",
        "Actually, I want to manufacture lithium-ion batteries for mobile phones.",
        "1",
        "What documents do I need?",
        "What about EV batteries?",
        "2",
        "What about ceiling fans?",
        "Which standard applies?",
        "1",
        "Now tell me the ISI mark.",
        "Bye"
    ]

    history = []
    
    for turn_idx, user_msg in enumerate(turn_inputs, start=1):
        req = ChatRequest(message=user_msg, history=history, language="en")
        res = await rag_service.answer_query(req)
        
        # Log step
        print(f"\n[Turn {turn_idx:02d}] User: '{user_msg}'")
        print(f"  ├─ Detected Intent:     {res.intent}")
        print(f"  ├─ Clarification State: {'PENDING' if res.clarification_needed else 'CLEARED / NOT_NEEDED'}")
        print(f"  ├─ Retrieval Triggered: {res.retrieval_triggered} (Sources: {res.sources_used})")
        if res.citations:
            cit_stds = list(dict.fromkeys([c.standard_number for c in res.citations]))
            print(f"  ├─ Cited Standards:     {cit_stds}")
        print(f"  └─ Assistant Response:  {res.answer[:140].strip()}...")

        # Append to live history
        history.append(ChatMessageInput(role="user", content=user_msg))
        history.append(ChatMessageInput(role="assistant", content=res.answer))

    # ---------------------------------------------------------
    # TEST 2: WATER BOTTLE TRANSITION TEST (Section 22)
    # ---------------------------------------------------------
    print("\n" + "#" * 85)
    print("TEST 2: WATER BOTTLE MULTI-TOPIC TRANSITION (Section 22)")
    print("#" * 85)

    wb_turns = [
        "I want to start a water bottle business.",
        "Plastic bottles.",
        "Actually stainless steel bottles.",
        "No, I mean packaged drinking water."
    ]

    history_wb = []
    for turn_idx, user_msg in enumerate(wb_turns, start=1):
        req = ChatRequest(message=user_msg, history=history_wb, language="en")
        res = await rag_service.answer_query(req)
        
        print(f"\n[WB Turn {turn_idx}] User: '{user_msg}'")
        print(f"  ├─ Intent:             {res.intent}")
        print(f"  ├─ Clarification:      {res.clarification_needed}")
        print(f"  ├─ Retrieval:          {res.retrieval_triggered} (Sources: {res.sources_used})")
        if res.citations:
            cit_stds = list(dict.fromkeys([c.standard_number for c in res.citations]))
            print(f"  ├─ Cited Standards:    {cit_stds}")
        print(f"  └─ Response:           {res.answer[:140].strip()}...")

        history_wb.append(ChatMessageInput(role="user", content=user_msg))
        history_wb.append(ChatMessageInput(role="assistant", content=res.answer))

    # ---------------------------------------------------------
    # TEST 3: FOUR WHEELER BUSINESS TEST (Section 23)
    # ---------------------------------------------------------
    print("\n" + "#" * 85)
    print("TEST 3: FOUR WHEELER AMBIGUITY CLARIFICATION (Section 23)")
    print("#" * 85)

    req_fw = ChatRequest(message="I want to start a four wheeler business.")
    res_fw = await rag_service.answer_query(req_fw)
    print(f"  Input:                 'I want to start a four wheeler business.'")
    print(f"  Intent:                {res_fw.intent}")
    print(f"  Clarification Needed:  {res_fw.clarification_needed}")
    print(f"  Retrieval Triggered:   {res_fw.retrieval_triggered}")
    print(f"  Options Provided:      {len(res_fw.clarification_options)}")
    for opt in res_fw.clarification_options:
        print(f"    • {opt}")

    print("\n" + "=" * 85)
    print("ALL END-TO-END CONVERSATIONAL TESTS EXECUTED SUCCESSFULLY")
    print("=" * 85)


if __name__ == "__main__":
    asyncio.run(run_end_to_end_tests())
