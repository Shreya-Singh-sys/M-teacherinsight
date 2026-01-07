import random

class CoachEngine:
    """
    Pedagogical Coaching Engine
    ---------------------------
    Current: Rule-based contextual feedback (fast, explainable)
    Azure-ready: Can be extended using Azure OpenAI for generative coaching
    """

    def generate_feedback(self, analysis_data, user_query):
        """
        Generates feedback based on the user's question
        and their actual teaching session metrics.
        """
        query = user_query.lower()

        # --------------------------------------------------
        # Safely extract metrics (default to 0 if missing)
        # --------------------------------------------------
        clarity = analysis_data.get("clarity", {}).get("clarity_score", 0)
        wpm = analysis_data.get("clarity", {}).get("wpm", 0)
        pitch = analysis_data.get("vocal", {}).get("avg_pitch", 0)
        interaction = analysis_data.get("interaction", {}).get("interaction_ratio_percent", 0)
        eye_contact = analysis_data.get("video", {}).get("eye_contact_score", 0)

        # --------------------------------------------------
        # 1. INTERACTION & ENGAGEMENT
        # --------------------------------------------------
        if (
            "interaction" in query or
            "engage" in query or
            "students" in query or
            "participate" in query
        ):
            # Case A: Too Low (Monologue)
            if interaction < 15:
                return (
                    f"Your interaction ratio is low ({interaction}%). You are lecturing 85%+ of the time. "
                    "To improve: Try the '10:2 Rule'—lecture for 10 minutes, then give students 2 minutes to discuss a question."
                )

            # Case B: Too High (Dead Air / Loss of Control)
            elif interaction > 45:
                return (
                    f"Your interaction ratio is notably high ({interaction}%). While leaving space is good, be careful of 'dead air.' "
                    "To improve: Ensure silence is structured. Use 'Think-Pair-Share' so students are talking to each other, not just staring at you."
                )

            # Case C: Healthy Balance
            else:
                if "how" in query or "improve" in query:
                    return (
                        f"Your interaction is healthy ({interaction}%), but to take it to the next level: "
                        "Try using live polls or cold-calling friendly students to keep the energy up."
                    )
                else:
                    return (
                        f"You have a healthy balance ({interaction}%). "
                        "You are giving students enough time to think without losing momentum."
                    )

        # --------------------------------------------------
        # 2. CLARITY & SPEAKING SPEED
        # --------------------------------------------------
        if "fast" in query or "speed" in query or "pace" in query:
            if wpm > 160:
                return (
                    f"You were speaking at {wpm} WPM (Words Per Minute). This is fast. "
                    "Try deliberately pausing after introducing a new term."
                )
            elif wpm < 110:
                return (
                    f"Your pace was {wpm} WPM, which can feel slow. "
                    "Try varying your speed—speed up for exciting examples, slow down for definitions."
                )
            else:
                return (
                    f"Your pacing was excellent ({wpm} WPM). "
                    "You struck a great balance between energy and clarity."
                )

        # --------------------------------------------------
        # 3. VOCAL DELIVERY / ENERGY
        # --------------------------------------------------
        if "voice" in query or "vocal" in query or "tone" in query or "pitch" in query:
            if pitch < 100:
                return (
                    "Your pitch was consistently low. "
                    "To improve engagement, try 'pitch stepping'—raising your pitch slightly when asking questions."
                )
            elif pitch > 200:
                return (
                    "Your energy is high, which is great! "
                    "Just ensure you drop your pitch at the end of sentences to sound more authoritative."
                )
            else:
                return (
                    "Your vocal modulation is natural. "
                    "You sound conversational yet professional."
                )

        # --------------------------------------------------
        # 4. EYE CONTACT
        # --------------------------------------------------
        if "eye" in query or "look" in query or "camera" in query:
            if eye_contact < 50:
                return (
                    "You looked away from the camera often. "
                    "Improvement Tip: Place a sticky note with a smiley face next to your camera lens "
                    "to remind you to look there."
                )
            else:
                return (
                    "Your eye contact is strong. "
                    "This helps build trust with remote students."
                )

        # --------------------------------------------------
        # 5. OVERALL / SUMMARY
        # --------------------------------------------------
        if "summary" in query or "overall" in query or "do" in query:
            overall = analysis_data.get("overall_score", 0)
            if overall > 80:
                return (
                    f"Overall, fantastic session (Score: {overall}). "
                    "Your delivery is polished. Now focus on advanced student engagement techniques."
                )
            else:
                focus_area = "Interaction" if interaction < 15 else "Vocal Variety"
                return (
                    f"Good effort (Score: {overall}). "
                    f"The biggest area for improvement is {focus_area}."
                )

        # --------------------------------------------------
        # FALLBACK
        # --------------------------------------------------
        return (
            "I analyzed your session. Try asking: "
            "'How can I improve interaction?', "
            "'Was I speaking too fast?', "
            "or 'How was my eye contact?'"
        )
