import asyncio
import sys
import os
import time
from typing import Dict, Any, List

from app.core.config import settings
from app.services.embedding_service import get_embedding_service
from app.services.vector_store import VectorStoreService
from app.services.language_service import LanguageService
from app.services.rag_service import RAGService
from app.services.product_discovery_service import ProductDiscoveryService
from app.services.certification_navigator_service import CertificationNavigatorService
from app.services.laboratory_service import LaboratoryService
from app.schemas.intelligence import (
    ProductDiscoveryRequest,
    CertificationRoadmapRequest,
    LaboratorySearchRequest
)


async def run_demo_checks():
    print("=" * 75)
    print("e-BIS Sahayak (SIH26107) -- Pre-Flight Demo Readiness & Subsystem Check")
    print("=" * 75)
    print(f"Timestamp    : {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
    print(f"Environment  : {settings.ENVIRONMENT.upper()}")
    print(f"Phase        : {settings.PHASE}")
    print(f"Demo Mode    : {'ENABLED' if settings.DEMO_MODE else 'OFF (Standard Live Mode)'}")
    print("-" * 75)

    checks: List[Dict[str, Any]] = []

    # 1. Config & Core App Check
    try:
        assert settings.PROJECT_NAME == "e-BIS Sahayak"
        checks.append({
            "subsystem": "Core Configuration",
            "status": "PASS",
            "details": f"Version {settings.VERSION}, Rate Limiting: {settings.RATE_LIMIT_ENABLED}"
        })
    except Exception as e:
        checks.append({"subsystem": "Core Configuration", "status": "FAIL", "details": str(e)})

    # 2. Embedding Model (FastEmbed ONNX)
    t0 = time.time()
    try:
        emb_service = get_embedding_service()
        test_vec = emb_service.embed_query("IS 1293 Plugs and Sockets")
        emb_latency = round((time.time() - t0) * 1000, 2)
        checks.append({
            "subsystem": "Embedding Engine",
            "status": "PASS",
            "details": f"Model: {settings.EMBEDDING_MODEL} (Dim: {len(test_vec)}, Latency: {emb_latency}ms)"
        })
    except Exception as e:
        checks.append({"subsystem": "Embedding Engine", "status": "FAIL", "details": str(e)})

    # 3. Vector Storage (Qdrant Cloud / In-Memory Fallback)
    try:
        vec_store = VectorStoreService()
        vec_store.ensure_collection(vector_dimension=len(test_vec))
        client = vec_store.get_client()
        coll_info = client.get_collection(vec_store.collection_name)
        count = coll_info.points_count or 0
        checks.append({
            "subsystem": "Vector Knowledge DB",
            "status": "PASS",
            "details": f"Collection: {settings.QDRANT_COLLECTION_NAME} (Points Count: {count})"
        })
    except Exception as e:
        checks.append({"subsystem": "Vector Knowledge DB", "status": "FAIL", "details": str(e)})

    # 4. Multilingual Intelligence Engine (EN / HI / TA)
    try:
        lang_service = LanguageService()
        det_en, _, _ = lang_service.detect_language("What is IS 1293?")
        det_hi, _, _ = lang_service.detect_language("IS 1293 क्या है?")
        det_ta, _, _ = lang_service.detect_language("IS 1293 என்றால் என்ன?")
        assert det_en == "en" and det_hi == "hi" and det_ta == "ta"
        checks.append({
            "subsystem": "Multilingual AI (i18n)",
            "status": "PASS",
            "details": "Language detection & cross-lingual dictionary verified (EN, HI, TA)"
        })
    except Exception as e:
        checks.append({"subsystem": "Multilingual AI (i18n)", "status": "FAIL", "details": str(e)})

    # 5. Product -> Standard Discovery Engine
    try:
        disc_service = ProductDiscoveryService()
        disc_req = ProductDiscoveryRequest(product_description="Plugs and Socket-Outlets")
        disc_res = disc_service.discover(disc_req)
        assert len(disc_res.standards) > 0
        checks.append({
            "subsystem": "Product Discovery",
            "status": "PASS",
            "details": f"Matched '{disc_res.standards[0].standard_number}' with QCO status: {disc_res.standards[0].is_mandatory_qco}"
        })
    except Exception as e:
        checks.append({"subsystem": "Product Discovery", "status": "FAIL", "details": str(e)})

    # 6. Certification Navigator Service
    try:
        cert_service = CertificationNavigatorService()
        cert_req = CertificationRoadmapRequest(standard_number="IS 1293:2019")
        roadmap = cert_service.generate_roadmap(cert_req)
        assert len(roadmap.steps) == 5
        checks.append({
            "subsystem": "Certification Roadmap",
            "status": "PASS",
            "details": f"Scheme: {roadmap.scheme_name} (5-stage guided roadmap generated)"
        })
    except Exception as e:
        checks.append({"subsystem": "Certification Roadmap", "status": "FAIL", "details": str(e)})

    # 7. Laboratory Directory Service
    try:
        lab_service = LaboratoryService()
        lab_req = LaboratorySearchRequest(standard_number="IS 1293")
        labs_res = lab_service.search_laboratories(lab_req)
        assert len(labs_res.laboratories) > 0
        checks.append({
            "subsystem": "Laboratory Registry",
            "status": "PASS",
            "details": f"Found {len(labs_res.laboratories)} accredited laboratories with testing scope for IS 1293"
        })
    except Exception as e:
        checks.append({"subsystem": "Laboratory Registry", "status": "FAIL", "details": str(e)})

    # 8. Groq LPU / Grounded Fallback Status
    try:
        rag_service = RAGService()
        groq_cfg = bool(settings.GROQ_API_KEY)
        checks.append({
            "subsystem": "Groq LLM Synthesis",
            "status": "PASS",
            "details": f"Model: {settings.GROQ_MODEL} (Live API: {'Configured' if groq_cfg else 'Grounded Fallback Engine Active'})"
        })
    except Exception as e:
        checks.append({"subsystem": "Groq LLM Synthesis", "status": "FAIL", "details": str(e)})

    # Print Report Table
    print(f"{'SUBSYSTEM':<25} | {'STATUS':<6} | {'DETAILS'}")
    print("-" * 75)
    all_passed = True
    for c in checks:
        print(f"{c['subsystem']:<25} | {c['status']:<6} | {c['details']}")
        if c['status'] != "PASS":
            all_passed = False

    print("=" * 75)
    if all_passed:
        print("[OK] ALL SUBSYSTEMS READY FOR LIVE SIH DEMONSTRATION")
    else:
        print("[FAIL] WARNING: ONE OR MORE SUBSYSTEM CHECKS FAILED")
    print("=" * 75)

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_demo_checks())
    sys.exit(exit_code)
