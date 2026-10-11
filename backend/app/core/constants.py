"""
Constants and Enums for e-BIS Sahayak
"""

from enum import Enum


class StandardDivision(str, Enum):
    CIVIL = "Civil Engineering"
    MECHANICAL = "Mechanical Engineering"
    ELECTROTECHNICAL = "Electrotechnical"
    ELECTRONICS_IT = "Electronics and Information Technology"
    CHEMICAL = "Chemical"
    FOOD_AGRICULTURE = "Food and Agriculture"
    TEXTILES = "Textiles"
    MEDICAL_HOSPITAL = "Medical Equipment and Hospital Planning"
    PETROLEUM_COAL = "Petroleum, Coal and Related Products"
    METALLURGICAL = "Metallurgical Engineering"
    PRODUCTION_GENERAL = "Production and General Engineering"
    TRANSPORT = "Transport Engineering"
    WATER_RESOURCES = "Water Resources"


class CertificationSchemeCode(str, Enum):
    # Scheme-I Product Certification (ISI Mark)
    SCHEME_I_ISI_NORMAL = "SCHEME_I_ISI_NORMAL"          # Scheme-I: Normal Procedure (Option 1)
    SCHEME_I_ISI_SIMPLIFIED = "SCHEME_I_ISI_SIMPLIFIED"  # Scheme-I: Simplified Procedure (Option 2)
    SCHEME_I_FMCS = "SCHEME_I_FMCS"                      # Scheme-I: Foreign Manufacturers Certification Scheme
    ECO_MARK = "ECO_MARK"                                # Eco Mark Scheme (Environment-Friendly Products under Scheme-I)
    
    # Scheme-II Compulsory Registration Scheme
    SCHEME_II_CRS = "SCHEME_II_CRS"                      # Scheme-II: Compulsory Registration Scheme (CRS)
    
    # Scheme-III Certificate of Conformity
    SCHEME_III_COC = "SCHEME_III_COC"                    # Scheme-III: Certificate of Conformity (Batch / Lot)
    
    # Scheme-IV Management Systems Certification
    SCHEME_IV_MSCS = "SCHEME_IV_MSCS"                    # Scheme-IV: Management Systems Certification Scheme (ISO 9001, etc.)
    
    # Scheme-X Capital Goods & Industrial Machinery
    SCHEME_X_CAPITAL_GOODS = "SCHEME_X_CAPITAL_GOODS"    # Scheme-X: Capital Goods & Industrial Machinery
    
    # Hallmarking Scheme
    HALLMARKING = "HALLMARKING"                          # Hallmarking Scheme for Gold & Silver Jewellery (HUID)
    
    # Laboratory Recognition Scheme
    LABORATORY_RECOGNITION = "LABORATORY_RECOGNITION"    # Laboratory Recognition Scheme (LRS / LIMS)

    # Legacy & colloquial aliases for backward compatibility
    SCHEME_I_ISI = "SCHEME_I_ISI"                        # Legacy alias for Scheme-I Product Certification
    SCHEME_IV_FMCS = "SCHEME_IV_FMCS"                    # Legacy colloquial alias for FMCS
    SCHEME_V_HALLMARK = "SCHEME_V_HALLMARK"              # Legacy alias for Hallmarking
    SCHEME_VI_ECO = "SCHEME_VI_ECO"                      # Legacy alias for Eco Mark



class MessageSender(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class DocumentType(str, Enum):
    STANDARD = "STANDARD"
    QCO = "QCO"
    MANUAL = "MANUAL"
    GAZETTE = "GAZETTE"
    CIRCULAR = "CIRCULAR"
