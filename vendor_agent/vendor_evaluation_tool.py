from pymongo import MongoClient
import pprint  # For cleaner printing of documents
from datetime import datetime

# Replace with your actual connection URI
MONGO_URI = "mongodb+srv://ivar06516:pplDdQwIyGPyk7jQ@cluster0.3u1bntz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Connect to MongoDB
client = MongoClient(MONGO_URI)
# Choose your database and collection
db = client["vendor_evaluation_db"]
vendors_collection = db["vendor_evaluation_collection"]
# Fetch all vendor documents
vendors = vendors_collection.find()

# Print each vendor document
print("Vendor Data:")
for vendor in vendors:
    pprint.pprint(vendor)

def evaluate_vendor_score(
    total_units_received,
    defective_units,
    returned_units,
    on_time_shipments,
    total_shipments,
    vendor_price,
    target_price,
    avg_response_time,
    expected_response_time,
    passed_audits,
    total_audits,
    missing_docs,
    required_docs,
    weights=None
):
    # Default KPI weights
    if weights is None:
        weights = {
            "quality": 0.30,
            "delivery": 0.25,
            "cost": 0.20,
            "responsiveness": 0.10,
            "compliance": 0.15
        }

    # --- 1. Quality Score ---
    defect_rate = (defective_units / total_units_received) if total_units_received else 0
    return_rate = (returned_units / total_units_received) if total_units_received else 0
    quality_score = max(0, 100 - (defect_rate + return_rate) * 100)

    # --- 2. Delivery Score ---
    on_time_pct = (on_time_shipments / total_shipments) * 100 if total_shipments else 0
    delivery_score = max(0, min(on_time_pct, 100))  # Cap at 100

    # --- 3. Cost Score ---
    cost_delta_pct = ((vendor_price - target_price) / target_price) * 100 if target_price else 0
    cost_score = max(0, min(100 - cost_delta_pct, 100))

    # --- 4. Responsiveness Score ---
    responsiveness_ratio = avg_response_time / expected_response_time if expected_response_time else 1
    responsiveness_score = max(0, min(100 - responsiveness_ratio * 100, 100))

    # --- 5. Compliance Score ---
    audit_score = (passed_audits / total_audits) * 100 if total_audits else 100
    doc_score = max(0, 100 - ((missing_docs / required_docs) * 100 if required_docs else 0))
    compliance_score = (audit_score + doc_score) / 2

    # --- Weighted Overall Score ---
    overall_score = round(
        quality_score * weights["quality"] +
        delivery_score * weights["delivery"] +
        cost_score * weights["cost"] +
        responsiveness_score * weights["responsiveness"] +
        compliance_score * weights["compliance"], 2
    )

    # --- Tier Classification ---
    if overall_score >= 85:
        tier = "Gold"
    elif overall_score >= 70:
        tier = "Silver"
    elif overall_score >= 50:
        tier = "Bronze"
    else:
        tier = "Disqualified"

    return {
        "quality_score": round(quality_score, 2),
        "delivery_score": round(delivery_score, 2),
        "cost_score": round(cost_score, 2),
        "responsiveness_score": round(responsiveness_score, 2),
        "compliance_score": round(compliance_score, 2),
        "overall_score": overall_score,
        "tier": tier
    }
# --- Insert Scores into a Specific Vendor ---
def update_vendor_scores(vendor_id, kpi_inputs):
    # Calculate scores from input data
    scores = evaluate_vendor_score(**kpi_inputs)

    # Update the vendor document
    result = vendors_collection.update_one(
        {"vendor_id": vendor_id},  # Filter
        {
            "$set": {
                "vendor_id": vendor_id,  # Ensure vendor_id is inserted if new
                "kpis": {
                    "quality": scores["quality_score"],
                    "delivery": scores["delivery_score"],
                    "cost": scores["cost_score"],
                    "responsiveness": scores["responsiveness_score"],
                    "compliance": scores["compliance_score"]
                },
                "overall_score": scores["overall_score"],
                "tier": scores["tier"],
                "last_updated": datetime.utcnow()
            }
        },
        upsert=True  #
    )

    if result.acknowledged:
        print(f"Vendor '{vendor_id}' updated successfully.")
        return scores
    else:
        print(f" No vendor found or nothing updated.")
        return none


# --- Sample Input ---
kpi_input = {
    "total_units_received": 1000,
    "defective_units": 10,
    "returned_units": 20,
    "on_time_shipments": 180,
    "total_shipments": 200,
    "vendor_price": 9.5,
    "target_price": 10.0,
    "avg_response_time": 4,
    "expected_response_time": 6,
    "passed_audits": 3,
    "total_audits": 4,
    "missing_docs": 1,
    "required_docs": 5
}

# Run update
#update_vendor_scores("V12345", kpi_input)




