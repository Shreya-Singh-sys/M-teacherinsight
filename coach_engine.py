import google.generativeai as genai
import os
import json

# Ensure Gemini is configured (it should already be done in main.py, but for safety)
try:
    api_key = "AIzaSyArAVYPsbS2F65OkRxXEaqbESMkYShN9ZE"
    if api_key:
        genai.configure(api_key=api_key)
        COACH_MODEL = genai.GenerativeModel("gemini-2.5-flash")
    else:
        COACH_MODEL = None
        print("WARNING: Gemini API Key not set for Coach Engine.")
except Exception as e:
    COACH_MODEL = None
    print(f"ERROR configuring COACH_MODEL: {e}")


class CoachEngine:

    def provide_coaching(self, analysis_results: dict, user_query: str):
        """
        Generates personalized coaching advice based on TIE results and user query.
        """
        if not COACH_MODEL:
            return "AI Coach is unavailable. Please check your GEMINI_API_KEY."

        # Convert the Python dictionary results into a neat JSON string for the LLM
        results_json = json.dumps(analysis_results, indent=2)

        prompt = f"""
        You are a concise and high-impact Master Teacher Coach.

        --- STEP 1: CHECK RELEVANCE ---
        Before answering, analyze the user's question.
        * RELEVANT TOPICS: Teaching, classroom management, student engagement, lesson planning, and the TIE performance data provided below.
        * IRRELEVANT TOPICS: General knowledge, coding, math problems unrelated to teaching, movies, politics, cooking, etc.

        If the question is IRRELEVANT, stop immediately and reply ONLY with:
        "That question is outside the scope of this coaching session. Please ask a question related to your teaching performance or classroom strategies."

        --- STEP 2: ANSWER (Only if Relevant) ---
        If the question IS relevant, provide a specific "quick win" answer.
        1. Keep it SHORT (under 100 words).
        2. Jump straight to the solution (no summaries).
        3. Provide exactly 3 bullet points for improvement.

        --- TIE PERFORMANCE DATA ---
        {results_json}

        The teacher asks: "{user_query}"
        """

        try:
            print(f"🧠 Sending query to AI Coach: {user_query}")
            response = COACH_MODEL.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini Coach Error: {e}")
            return "Could not connect to the AI Coach. Please try again later"