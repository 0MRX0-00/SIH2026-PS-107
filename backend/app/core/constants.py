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
    SCHEME_I_ISI = "SCHEME_I_ISI"          # Product Certification (ISI Mark)
    SCHEME_II_CRS = "SCHEME_II_CRS"        # Compulsory Registration Scheme
    SCHEME_IV_FMCS = "SCHEME_IV_FMCS"      # Foreign Manufacturers Certification
    SCHEME_V_HALLMARK = "SCHEME_V_HALLMARK"# Hallmarking of Gold and Silver
    SCHEME_VI_ECO = "SCHEME_VI_ECO"        # Eco Mark Scheme


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
