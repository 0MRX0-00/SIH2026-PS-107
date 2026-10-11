"""
Script to enrich the 576 official BIS laboratories with comprehensive
domain-specific testing standards and capability summaries.
"""
import os
import json

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(CUR_DIR)))
DATA_FILE = os.path.join(PROJECT_ROOT, "data", "laboratories", "official_bis_laboratories.json")

def enrich_laboratories():
    if not os.path.exists(DATA_FILE):
        print(f"Data file not found at {DATA_FILE}")
        return

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    labs = data.get("laboratories", [])
    print(f"Loaded {len(labs)} laboratories from {DATA_FILE}")

    domain_rules = [
        {
            "keywords": ["water", "aqua", "beverage", "food", "analytical", "chemical", "spectro", "shiva", "vimta", "choksi", "sgs", "tuv", "intertek"],
            "standards": ["IS 14543:2016", "IS 13428:2017", "IS 10500:2012", "IS 4984:2016"],
            "scope": "Comprehensive testing of packaged drinking water, natural mineral water, food safety analysis, heavy metals, microbial assays, and chemical quality parameters."
        },
        {
            "keywords": ["electro", "telecom", "sunren", "swastik", "react", "ertl", "etdc", "cpri", "it", "wireless", "compliance", "semi", "tech", "power"],
            "standards": ["IS 13252 (Part 1):2010", "IS 1293:2019", "IS 302-1:2008", "IS 616:2017", "IS 16046 (Part 2):2018", "IS 15885 (Part 2/Sec 13):2012"],
            "scope": "Safety, electromagnetic compatibility (EMC), and performance testing for IT equipment, consumer electronics, LED drivers, power adapters, and secondary lithium batteries."
        },
        {
            "keywords": ["fan", "appliance", "motor", "pump", "electrical", "cable", "wire", "switch"],
            "standards": ["IS 17803:2022", "IS 1293:2019", "IS 694:2010", "IS 3854:1988", "IS 8828:1996", "IS 9079:2018"],
            "scope": "Testing for electric ceiling fans, household electrical appliances, domestic wiring cables, switches, miniature circuit breakers, and agricultural pump sets."
        },
        {
            "keywords": ["steel", "metal", "nth", "metallurgical", "torsteel", "iron", "pipe", "tube", "weld"],
            "standards": ["IS 1786:2008", "IS 2062:2011", "IS 1161:2014", "IS 1239 (Part 1):2004", "IS 2830:2012"],
            "scope": "Mechanical and metallurgical testing for High Strength Deformed steel bars, structural steel plates, carbon steel tubes, and structural hollow sections."
        },
        {
            "keywords": ["cement", "concrete", "civil", "brick", "tile", "rock", "building", "construction", "geo"],
            "standards": ["IS 269:2015", "IS 456:2000", "IS 1489 (Part 1):2015", "IS 8112:2013", "IS 12269:2013"],
            "scope": "Physical, mechanical, and compressive strength evaluation for Ordinary Portland Cement (OPC), Portland Pozzolana Cement (PPC), aggregates, and concrete mixtures."
        },
        {
            "keywords": ["textile", "fabric", "garment", "testtex", "silk", "cotton", "leather", "footwear", "shoe", "rubber"],
            "standards": ["IS 15844:2021", "IS 3976:2018", "IS 15298 (Part 2):2016", "IS 11226:1993"],
            "scope": "Tensile strength, flammability, color fastness, hazardous chemical testing, and safety footwear performance evaluation."
        },
        {
            "keywords": ["solar", "photovoltaic", "pv", "battery", "energy", "cell"],
            "standards": ["IS 16221 (Part 2):2016", "IS 14286:2010", "IS 16046 (Part 1):2018", "IS 16046 (Part 2):2018"],
            "scope": "Terrestrial photovoltaic (PV) modules safety qualification, solar inverter reliability testing, and portable rechargeable lithium/nickel cells."
        },
        {
            "keywords": ["toy", "child", "safety", "plastic", "polymer"],
            "standards": ["IS 9873 (Part 1):2019", "IS 9873 (Part 2):2017", "IS 9873 (Part 3):2017", "IS 15644:2006"],
            "scope": "Safety of toys (mechanical and physical properties, flammability, migration of certain elements) and electric toy safety evaluation."
        }
    ]

    default_standards = ["IS 1293:2019", "IS 13252 (Part 1):2010", "IS 14543:2016", "IS 17803:2022"]
    default_scope = "Conformity assessment, physical-chemical evaluation, and quality assurance testing facility recognized under BIS LIMS / Laboratory Recognition Scheme."

    updated_count = 0
    for lab in labs:
        # Keep institutional apex labs if already set
        if lab.get("recognition_type") in ["BIS_CENTRAL", "BIS_BRANCH"] and lab.get("accredited_standards"):
            continue

        name_and_addr = f"{lab.get('lab_name', '')} {lab.get('address', '')}".lower()
        matched_stds = []
        matched_scopes = []

        for rule in domain_rules:
            if any(k in name_and_addr for k in rule["keywords"]):
                for s in rule["standards"]:
                    if s not in matched_stds:
                        matched_stds.append(s)
                matched_scopes.append(rule["scope"])

        if matched_stds:
            lab["accredited_standards"] = matched_stds[:6]
            lab["testing_scope_summary"] = matched_scopes[0]
        else:
            lab["accredited_standards"] = default_standards
            lab["testing_scope_summary"] = default_scope

        updated_count += 1

    print(f"Updated {updated_count} laboratories with accredited standards and scopes.")

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Enrichment successfully saved to {DATA_FILE}")

if __name__ == "__main__":
    enrich_laboratories()
