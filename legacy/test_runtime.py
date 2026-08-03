from runtime.engine import RuntimeEngine
import json

engine = RuntimeEngine()

print("--- Test Case 1: Bleeding Risk (Advil + Coumadin) ---")
patient_context = {
    "patient_id": "PT-12345",
    "medications": ["advil", "coumadin"],
    "allergies": []
}
res = engine.evaluate(patient_context)
print(json.dumps(res, indent=2))

print("\n--- Test Case 2: Duplicate Therapy (Prozac + Zoloft) ---")
patient_context2 = {
    "patient_id": "PT-99999",
    "medications": ["prozac", "zoloft"],
    "allergies": []
}
res2 = engine.evaluate(patient_context2)
print(json.dumps(res2, indent=2))

print("\n--- Test Case 3: Penicillin Allergy (Amoxicillin) ---")
patient_context3 = {
    "patient_id": "PT-55555",
    "medications": ["amoxil"],
    "allergies": [{"allergen_class": "Penicillin"}]
}
res3 = engine.evaluate(patient_context3)
print(json.dumps(res3, indent=2))
