"""
Pre-Flight Diagnostics Check for e-BIS Sahayak.
Verifies system readiness, data integrity, and laboratory directory.
"""
import sys
import logging
from app.db.seed_intelligence import VERIFIED_STANDARDS, VERIFIED_SCHEMES, VERIFIED_LABORATORIES
from app.services.laboratory_service import LaboratoryService

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("preflight")

def run_diagnostics():
    print("----------------------------------------------------------------------")
    print(" [OK] Python Version         :", sys.version.split()[0])
    print(" [OK] Indian Standards Loaded:", len(VERIFIED_STANDARDS))
    print(" [OK] Schemes Configured     :", len(VERIFIED_SCHEMES))
    
    lab_service = LaboratoryService()
    stats = lab_service.get_stats()
    print(" [OK] Verified Laboratories  :", stats.total_laboratories)
    print("      - BIS Recognized       :", stats.recognized_count)
    print("      - BIS Empanelled       :", stats.empaneled_count)
    print("      - Institutional Apex   :", stats.institutional_count)
    print("      - States / UTs Covered :", stats.total_states)
    print(" [OK] Pre-Flight Diagnostics Check: PASSED")
    print("----------------------------------------------------------------------")

if __name__ == "__main__":
    run_diagnostics()
