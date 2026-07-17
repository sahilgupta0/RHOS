"""
RHOS Medication Service.

Drug interaction checking, allergy cross-reference, and generic alternatives.
"""

from __future__ import annotations

import logging
from typing import Any

from app.services.gemini import check_medications as ai_check_medications

logger = logging.getLogger(__name__)

# Common drug interactions database (simplified)
KNOWN_INTERACTIONS: dict[tuple[str, str], dict[str, str]] = {
    ("warfarin", "aspirin"): {
        "severity": "HIGH",
        "description": "Increased risk of bleeding. Combined anticoagulant/antiplatelet effect.",
    },
    ("metformin", "alcohol"): {
        "severity": "HIGH",
        "description": "Risk of lactic acidosis. Avoid concurrent use.",
    },
    ("ace_inhibitor", "potassium"): {
        "severity": "MEDIUM",
        "description": "Risk of hyperkalemia. Monitor potassium levels.",
    },
    ("ssri", "maoi"): {
        "severity": "HIGH",
        "description": "Risk of serotonin syndrome. Contraindicated combination.",
    },
    ("metformin", "contrast_dye"): {
        "severity": "MEDIUM",
        "description": "Risk of lactic acidosis. Hold metformin before/after contrast.",
    },
}

# Common generic alternatives
GENERIC_ALTERNATIVES: dict[str, list[dict[str, str]]] = {
    "paracetamol": [{"generic": "Acetaminophen", "brand": "Crocin/Calpol", "note": "Same active ingredient"}],
    "amoxicillin": [{"generic": "Amoxicillin", "brand": "Mox/Novamox", "note": "Generic widely available"}],
    "metformin": [{"generic": "Metformin HCl", "brand": "Glycomet/Glucophage", "note": "First-line T2DM"}],
    "amlodipine": [{"generic": "Amlodipine besylate", "brand": "Amlopress/Amlip", "note": "Calcium channel blocker"}],
    "omeprazole": [{"generic": "Omeprazole", "brand": "Omez", "note": "PPI, generic widely available"}],
    "atorvastatin": [{"generic": "Atorvastatin calcium", "brand": "Atorva/Lipitor", "note": "Statin"}],
}


async def check_drug_interactions(
    medications: list[str],
    patient_allergies: list[str] | None = None,
    patient_conditions: list[str] | None = None,
    patient_age: int | None = None,
) -> dict[str, Any]:
    """
    Check medications for interactions, allergy conflicts, and warnings.

    Uses local knowledge base first, then augments with AI analysis.
    """
    result: dict[str, Any] = {
        "interactions": [],
        "allergy_warnings": [],
        "warnings": [],
        "alternatives": [],
        "safe_to_prescribe": True,
    }

    meds_lower = [m.lower().strip() for m in medications]
    allergies_lower = [a.lower().strip() for a in (patient_allergies or [])]

    # Check known interactions
    for i, med1 in enumerate(meds_lower):
        for med2 in meds_lower[i + 1:]:
            for (d1, d2), info in KNOWN_INTERACTIONS.items():
                if (d1 in med1 or d1 in med2) and (d2 in med1 or d2 in med2):
                    result["interactions"].append({
                        "drug1": medications[i],
                        "drug2": medications[meds_lower.index(med2)],
                        "severity": info["severity"],
                        "description": info["description"],
                    })
                    if info["severity"] == "HIGH":
                        result["safe_to_prescribe"] = False

    # Check allergy conflicts
    for med in meds_lower:
        for allergen in allergies_lower:
            if allergen in med or med in allergen:
                result["allergy_warnings"].append({
                    "medication": med,
                    "allergen": allergen,
                    "risk_level": "HIGH",
                })
                result["safe_to_prescribe"] = False

    # Find generic alternatives
    for med in meds_lower:
        if med in GENERIC_ALTERNATIVES:
            result["alternatives"].extend(
                [{"medication": med, **alt} for alt in GENERIC_ALTERNATIVES[med]]
            )

    # Age-based warnings
    if patient_age:
        if patient_age < 12:
            for med in meds_lower:
                if "aspirin" in med:
                    result["warnings"].append(
                        f"Aspirin is generally not recommended for children under 12 (Reye's syndrome risk)."
                    )
                    result["safe_to_prescribe"] = False

    # Augment with AI analysis if configured
    try:
        ai_result = await ai_check_medications(
            medications, patient_allergies, patient_conditions
        )
        if isinstance(ai_result, dict):
            # Merge AI results with local results
            result["interactions"].extend(ai_result.get("interactions", []))
            result["allergy_warnings"].extend(ai_result.get("allergy_warnings", []))
            result["warnings"].extend(ai_result.get("warnings", []))
            if not ai_result.get("safe_to_prescribe", True):
                result["safe_to_prescribe"] = False
    except Exception as e:
        logger.warning("AI medication check failed (using local results only): %s", e)

    return result
