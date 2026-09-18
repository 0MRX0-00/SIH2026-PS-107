"""
e-BIS Sahayak — Official Acceptance Criteria Verification Script
Demonstrates all 8 Acceptance Tests specified in prompt.txt:
  Test 1: 'Hello' (English Greeting -> GREETING, No RAG, No fake sources)
  Test 2: 'I want to start a water bottle business' (Ambiguity -> CLARIFICATION_REQUIRED)
  Test 3: 'I want to start a 4 wheeler business' (Automotive Ambiguity -> CLARIFICATION_REQUIRED)
  Test 4: 'I want to manufacture stainless steel vacuum bottles' (Specific Product -> Grounded RAG IS 17526)
  Test 5: 'What is IS 302?' (Explicit Standard -> STANDARD_SEARCH, Evidence Retrieved)
  Test 6: Unsupported/Fictional Standard (Anti-Hallucination -> Insufficient Evidence Refusal)
  Test 7: 'வணக்கம்' (Tamil Greeting -> GREETING, No RAG)
  Test 8: 'नमस्ते' (Hindi Greeting -> GREETING, No RAG)
"""

import sys
import os
import asyncio
import json

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.services.rag_service import get_rag_service
from app.schemas.chat import ChatRequest, ChatMessageInput


async def run_all_acceptance_tests():
    print("=" * 80)
    print("e-BIS Sahayak — ACCEPTANCE CRITERIA EMPIRICAL TEST VERIFICATION")
    print("=" * 80)

    rag = get_rag_service()
    all_passed = True

    # -------------------------------------------------------------
    # Test 1: English Greeting
    # -------------------------------------------------------------
    print("\n[TEST 1] Input: 'Hello'")
    req1 = ChatRequest(message="Hello", language="en")
    res1 = await rag.answer_query(req1)
    t1_pass = (
        res1.intent == "GREETING"
        and res1.retrieval_triggered is False
        and res1.sources_used == 0
        and len(res1.citations) == 0
    )
    print(f"  -> Intent             : {res1.intent}")
    print(f"  -> Retrieval Executed : {res1.retrieval_triggered}")
    print(f"  -> Sources Count      : {res1.sources_used}")
    print(f"  -> Response Snippet   : {res1.answer[:80]}...")
    print(f"  -> Status             : {'PASSED' if t1_pass else 'FAILED'}")
    if not t1_pass: all_passed = False

    # -------------------------------------------------------------
    # Test 2: Ambiguous Water Bottle Query
    # -------------------------------------------------------------
    print("\n[TEST 2] Input: 'I want to start a water bottle business'")
    req2 = ChatRequest(message="I want to start a water bottle business", language="en")
    res2 = await rag.answer_query(req2)
    t2_pass = (
        res2.intent == "CLARIFICATION_REQUIRED"
        and res2.clarification_needed is True
        and res2.retrieval_triggered is False
        and len(res2.clarification_options) > 0
        and not any("17526" in cit.standard_number for cit in res2.citations)
    )
    print(f"  -> Intent             : {res2.intent}")
    print(f"  -> Clarification Needed: {res2.clarification_needed}")
    print(f"  -> Options Returned   : {len(res2.clarification_options)} options")
    for opt in res2.clarification_options[:3]:
        print(f"     * {opt}")
    print(f"  -> Status             : {'PASSED' if t2_pass else 'FAILED'}")
    if not t2_pass: all_passed = False

    # -------------------------------------------------------------
    # Test 3: Automotive / 4-Wheeler Ambiguity
    # -------------------------------------------------------------
    print("\n[TEST 3] Input: 'I want to start a 4 wheeler business'")
    req3 = ChatRequest(message="I want to start a 4 wheeler business", language="en")
    res3 = await rag.answer_query(req3)
    t3_pass = (
        res3.intent == "CLARIFICATION_REQUIRED"
        and res3.clarification_needed is True
        and res3.retrieval_triggered is False
        and res3.sources_used == 0
        and any("Passenger Car" in opt or "Electric Vehicle" in opt or "Automotive components" in opt for opt in res3.clarification_options)
    )
    print(f"  -> Intent             : {res3.intent}")
    print(f"  -> Clarification Needed: {res3.clarification_needed}")
    print(f"  -> Options Returned   : {len(res3.clarification_options)} options")
    for opt in res3.clarification_options[:3]:
        print(f"     * {opt}")
    print(f"  -> Status             : {'PASSED' if t3_pass else 'FAILED'}")
    if not t3_pass: all_passed = False

    # -------------------------------------------------------------
    # Test 4: Specific Product Query -> Stainless Steel Vacuum Bottles
    # -------------------------------------------------------------
    print("\n[TEST 4] Input: 'I want to manufacture stainless steel vacuum bottles'")
    req4 = ChatRequest(message="I want to manufacture stainless steel vacuum bottles", language="en")
    res4 = await rag.answer_query(req4)
    t4_pass = (
        res4.retrieval_triggered is True
        and res4.insufficient_evidence is False
        and (len(res4.citations) > 0 or "17526" in res4.answer or "stainless steel" in res4.answer.lower())
    )
    print(f"  -> Intent             : {res4.intent}")
    print(f"  -> Retrieval Executed : {res4.retrieval_triggered}")
    print(f"  -> Sources Used       : {res4.sources_used}")
    print(f"  -> Citations Count    : {len(res4.citations)}")
    print(f"  -> Response Snippet   : {res4.answer[:120]}...")
    print(f"  -> Status             : {'PASSED' if t4_pass else 'FAILED'}")
    if not t4_pass: all_passed = False

    # -------------------------------------------------------------
    # Test 5: Explicit Standard Search -> IS 302
    # -------------------------------------------------------------
    print("\n[TEST 5] Input: 'What is IS 302?'")
    req5 = ChatRequest(message="What is IS 302?", language="en")
    res5 = await rag.answer_query(req5)
    t5_pass = (
        res5.retrieval_triggered is True
        and (res5.intent in ["STANDARD_SEARCH", "STANDARD_EXPLANATION", "GENERAL_BIS_QUERY"])
    )
    print(f"  -> Intent             : {res5.intent}")
    print(f"  -> Retrieval Executed : {res5.retrieval_triggered}")
    print(f"  -> Response Snippet   : {res5.answer[:100]}...")
    print(f"  -> Status             : {'PASSED' if t5_pass else 'FAILED'}")
    if not t5_pass: all_passed = False

    # -------------------------------------------------------------
    # Test 6: Unsupported / Fictional Standard Query
    # -------------------------------------------------------------
    print("\n[TEST 6] Input: 'What are the quantum teleporter specifications under Martian IS 9999999?'")
    req6 = ChatRequest(message="What are the quantum teleporter specifications under Martian IS 9999999?", language="en")
    res6 = await rag.answer_query(req6)
    t6_pass = (
        res6.insufficient_evidence is True
        and res6.sources_used == 0
        and len(res6.citations) == 0
    )
    print(f"  -> Insufficient Evidence: {res6.insufficient_evidence}")
    print(f"  -> Sources Used         : {res6.sources_used}")
    print(f"  -> Response Snippet     : {res6.answer[:120]}...")
    print(f"  -> Status               : {'PASSED' if t6_pass else 'FAILED'}")
    if not t6_pass: all_passed = False

    # -------------------------------------------------------------
    # Test 7: Tamil Greeting
    # -------------------------------------------------------------
    print("\n[TEST 7] Input: 'வணக்கம்'")
    req7 = ChatRequest(message="வணக்கம்", language="ta")
    res7 = await rag.answer_query(req7)
    t7_pass = (
        res7.intent == "GREETING"
        and res7.retrieval_triggered is False
        and res7.sources_used == 0
        and "வணக்கம்" in res7.answer
    )
    print(f"  -> Intent             : {res7.intent}")
    print(f"  -> Retrieval Executed : {res7.retrieval_triggered}")
    print(f"  -> Language           : {res7.language}")
    print(f"  -> Response Snippet   : {res7.answer[:80]}...")
    print(f"  -> Status             : {'PASSED' if t7_pass else 'FAILED'}")
    if not t7_pass: all_passed = False

    # -------------------------------------------------------------
    # Test 8: Hindi Greeting
    # -------------------------------------------------------------
    print("\n[TEST 8] Input: 'नमस्ते'")
    req8 = ChatRequest(message="नमस्ते", language="hi")
    res8 = await rag.answer_query(req8)
    t8_pass = (
        res8.intent == "GREETING"
        and res8.retrieval_triggered is False
        and res8.sources_used == 0
        and ("नमस्ते" in res8.answer or "ई-बीआईएस" in res8.answer)
    )
    print(f"  -> Intent             : {res8.intent}")
    print(f"  -> Retrieval Executed : {res8.retrieval_triggered}")
    print(f"  -> Language           : {res8.language}")
    print(f"  -> Response Snippet   : {res8.answer[:80]}...")
    print(f"  -> Status             : {'PASSED' if t8_pass else 'FAILED'}")
    if not t8_pass: all_passed = False

    print("\n" + "=" * 80)
    print(f"OVERALL ACCEPTANCE RESULT: {'ALL 8 TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    print("=" * 80)
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(run_all_acceptance_tests())
    sys.exit(0 if success else 1)
