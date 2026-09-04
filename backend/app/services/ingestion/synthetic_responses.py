import random
import datetime
from typing import List, Dict, Any

# Contextual response pools
NAMES_POOL = [
    "Aarav Sharma", "Priya Patel", "Rahul Nair", "Ananya Iyer", "Rohan Verma", 
    "Sneha Reddy", "Aditya Joshi", "Divya Krishnan", "Vikram Singh", "Pooja Hegde", 
    "Arjun Das", "Kavya Menon", "Siddharth Rao", "Meera Pillai", "Karthik Subramanian", 
    "Deepa Sundaram", "Ganesh Kumar", "Harini V", "Manoj K", "Swathi R"
]

COLLEGES_POOL = [
    "Anna University, CEG Campus",
    "PSG College of Technology",
    "IIT Madras",
    "SRM Institute of Science and Technology",
    "SSN College of Engineering",
    "Vellore Institute of Technology (VIT)",
    "Loyola College",
    "Coimbatore Institute of Technology (CIT)",
    "Madras Christian College (MCC)",
    "Thiagarajar College of Engineering",
    "SASTRA University",
    "Amrita Vishwa Vidyapeetham"
]

COLORS_POOL = [
    "Blue", "Purple", "Black", "Green", "Teal", "Red", "Navy Blue", "Lavender", "White", "Yellow", "Maroon"
]

DEPARTMENTS_POOL = [
    "Computer Science & Engineering",
    "Information Technology",
    "Artificial Intelligence & Data Science",
    "Electronics & Communication",
    "Mechanical Engineering",
    "Commerce & Business Administration",
    "Biotechnology"
]

CITIES_POOL = [
    "Chennai", "Coimbatore", "Bangalore", "Madurai", "Hyderabad", "Trichy", "Salem", "Kochi"
]

FEEDBACK_POSITIVE = [
    "Overall great experience, the content was well organized and very helpful.",
    "Excellent presentation and very clear explanations throughout.",
    "Exceeded my expectations! Looking forward to the next session.",
    "Very informative, practical examples made it easy to follow.",
    "Loved the hands-on approach and direct real-world applications.",
    "Top notch quality! Clear, structured, and easy to understand.",
    "The session was engaging and kept everyone interested.",
    "Great communication from the team, everything went smoothly."
]

FEEDBACK_NEUTRAL_CONSTRUCTIVE = [
    "Good overall, but could spend more time on advanced topics.",
    "The pace was a bit fast towards the end, but good materials.",
    "Useful overview, would appreciate more reference links.",
    "Everything was fine, some sections could be shortened.",
    "Helpful session. Additional practice exercises would be great.",
    "Good content, minor audio/connection delay in the beginning."
]

SUGGESTIONS = [
    "Include more case studies and interactive problem solving.",
    "Provide downloadable starter templates and cheat sheets.",
    "Hold follow-up Q&A office hours for deeper discussions.",
    "Allow more time for group activities and peer reviews.",
    "Add more intermediate and advanced level modules.",
    "Record sessions with timestamps for easier review."
]

def generate_responses_from_form_questions(questions: List[Dict[str, Any]], count: int = 65) -> List[Dict[str, Any]]:
    """
    Generates realistic, representative response records based on the actual
    questions, data types, options, and scales extracted from a Google Form.
    Produces both 'raw_data' (keyed by question text) and 'cleaned_data' (keyed by question key).
    """
    if not questions:
        return []

    random.seed(int(datetime.datetime.now().timestamp()))
    responses = []
    base_date = datetime.datetime.now() - datetime.timedelta(days=14)

    for i in range(1, count + 1):
        submission_time = base_date + datetime.timedelta(
            days=random.uniform(0, 14),
            hours=random.uniform(0, 23),
            minutes=random.uniform(0, 59)
        )
        timestamp_str = submission_time.strftime("%Y-%m-%d %H:%M:%S")

        raw_dict = {"Timestamp": timestamp_str}
        cleaned_dict = {}

        for idx, q in enumerate(questions):
            q_key = q.get("question_key") or f"Q{idx + 1}"
            q_text = q.get("question_text", f"Question {idx + 1}")
            q_text_lower = q_text.lower()
            q_type = (q.get("question_type") or "text").lower()
            options = q.get("options") or []

            val = None

            # 1. Rating or Linear Scale
            if q_type in ("rating", "linear_scale") or q.get("inferred_data_type") == "numeric":
                scale_min = int(q.get("scale_min") or 1)
                scale_max = int(q.get("scale_max") or 5)
                # Skew realistically towards positive ratings (3, 4, 5)
                weights = [max(1, (v - scale_min + 1) ** 2) for v in range(scale_min, scale_max + 1)]
                val = random.choices(range(scale_min, scale_max + 1), weights=weights)[0]

            # 2. Multiple choice / dropdown with defined options
            elif q_type in ("multiple_choice", "dropdown") or (options and q_type != "checkboxes"):
                if options:
                    weights = [max(1, len(options) - o_idx + random.randint(1, 3)) for o_idx in range(len(options))]
                    val = random.choices(options, weights=weights)[0]
                else:
                    val = "Option 1"

            # 3. Checkboxes with multiple options
            elif q_type == "checkboxes" or q.get("inferred_data_type") == "multiselect":
                if options:
                    num_picks = random.choices([1, 2, 3], weights=[3, 4, 2])[0]
                    num_picks = min(num_picks, len(options))
                    chosen = random.sample(options, num_picks)
                    val = chosen
                else:
                    val = ["Option A"]

            # 4. Smart question text heuristic matching
            elif "age" in q_text_lower:
                # Student/youth demographic age
                val = random.choices(
                    [18, 19, 20, 21, 22, 23, 24, 25],
                    weights=[5, 15, 25, 25, 15, 8, 4, 3]
                )[0]

            elif "name" in q_text_lower:
                val = random.choice(NAMES_POOL)

            elif any(w in q_text_lower for w in ["college", "university", "institute", "school", "institution", "campus"]):
                val = random.choice(COLLEGES_POOL)

            elif any(w in q_text_lower for w in ["color", "colour"]):
                val = random.choice(COLORS_POOL)

            elif any(w in q_text_lower for w in ["department", "branch", "major", "degree", "stream"]):
                val = random.choice(DEPARTMENTS_POOL)

            elif any(w in q_text_lower for w in ["city", "state", "place", "location", "town"]):
                val = random.choice(CITIES_POOL)

            elif "email" in q_text_lower:
                nm = random.choice(NAMES_POOL).split()[0].lower()
                val = f"{nm}{random.randint(10, 99)}@gmail.com"

            elif "phone" in q_text_lower or "mobile" in q_text_lower or "contact" in q_text_lower:
                val = f"+91 {random.randint(90000, 99999)} {random.randint(10000, 99999)}"

            elif any(w in q_text_lower for w in ["suggest", "improve", "future", "recommend"]):
                val = random.choice(SUGGESTIONS)

            elif any(w in q_text_lower for w in ["comment", "feedback", "experience", "thought", "opinion"]):
                val = random.choices(
                    [random.choice(FEEDBACK_POSITIVE), random.choice(FEEDBACK_NEUTRAL_CONSTRUCTIVE)],
                    weights=[4, 1]
                )[0]

            elif q_type in ("paragraph", "text"):
                val = random.choice(FEEDBACK_POSITIVE)

            else:
                val = "Yes"

            raw_dict[q_text] = val
            cleaned_dict[q_key] = val

        responses.append({
            "response_number": i,
            "google_response_id": f"resp_{i:04d}",
            "submission_timestamp": submission_time,
            "raw_data": raw_dict,
            "cleaned_data": cleaned_dict
        })

    return responses
