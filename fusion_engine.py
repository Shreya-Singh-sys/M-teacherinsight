class FusionEngine:
    def __init__(self):
        print("🧠 Initializing Fusion Engine (Weighted Scoring)...")

    def calculate_overall(self, results):
        """
        Takes the raw results from all 4 streams and calculates a final weighted score.
        Weights:
        - Clarity (Content): 40%
        - Interaction (Engagement): 30%
        - Delivery (Vocal + Visual): 30%
        """
        
        # --- 1. NORMALIZE CLARITY (0-100) ---
        # Default to 0 if missing
        clarity_raw = results.get("clarity", {}).get("clarity_score", 0)
        score_clarity = float(clarity_raw)

        # --- 2. NORMALIZE INTERACTION (0-100) ---
        # Target: 20-30% interaction is ideal. If it's 0%, score is 0. 
        # If it's >20%, score should be high.
        inter_raw = results.get("interaction", {}).get("interaction_ratio_percent", 0)
        
        if inter_raw >= 20:
            score_interaction = 100
        else:
            # Scale it: 10% ratio = 50 score
            score_interaction = (inter_raw / 20) * 100 

        # --- 3. NORMALIZE DELIVERY (0-100) ---
        # Combine Vocal (Pitch) + Video (Eye Contact)
        
        # A. Vocal Score based on 'delivery_status'
        vocal_data = results.get("vocal", {})
        status = vocal_data.get("delivery_status", "Normal")
        
        if status == "Dynamic (Good variation)":
            vocal_score = 95
        elif status == "Monotone (Robot-like)":
            vocal_score = 40
        else:
            vocal_score = 75

        # B. Visual Score based on Eye Contact
        video_data = results.get("video", {})
        eye_contact = video_data.get("eye_contact_score", 0)
        
        # Delivery is average of Vocal & Visual
        score_delivery = (vocal_score + eye_contact) / 2

        # --- 4. FINAL WEIGHTED AVERAGE ---
        # Formula from your PDF
        final_score = (
            (score_clarity * 0.40) +
            (score_interaction * 0.30) +
            (score_delivery * 0.30)
        )

        return int(final_score)