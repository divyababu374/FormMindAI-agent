import random
import datetime
from typing import Dict, Any, List

def get_workshop_feedback_dataset() -> Dict[str, Any]:
    random.seed(42)
    
    questions = [
        {
            "question_key": "Q1",
            "question_text": "How would you rate your overall satisfaction with the workshop?",
            "question_type": "rating",
            "inferred_data_type": "numeric",
            "options": ["1", "2", "3", "4", "5"],
            "scale_min": 1,
            "scale_max": 5,
            "is_required": True
        },
        {
            "question_key": "Q2",
            "question_text": "Which academic department do you belong to?",
            "question_type": "multiple_choice",
            "inferred_data_type": "categorical",
            "options": ["Computer Science", "Information Technology", "AI & Data Science", "Electronics & Communication"],
            "is_required": True
        },
        {
            "question_key": "Q3",
            "question_text": "What is your current year of study?",
            "question_type": "multiple_choice",
            "inferred_data_type": "categorical",
            "options": ["1st Year", "2nd Year", "3rd Year", "4th Year"],
            "is_required": True
        },
        {
            "question_key": "Q4",
            "question_text": "Which workshop topic was most valuable to you?",
            "question_type": "multiple_choice",
            "inferred_data_type": "categorical",
            "options": ["Python & FastAPI Backends", "AI-assisted Coding & LLMs", "React & Modern UI Systems", "Cloud Deployment & DevOps"],
            "is_required": True
        },
        {
            "question_key": "Q5",
            "question_text": "Which skills would you like to explore in future sessions? (Select all that apply)",
            "question_type": "checkboxes",
            "inferred_data_type": "multiselect",
            "options": ["Autonomous AI Agents", "Vector Databases & RAG", "Docker & Kubernetes", "Mobile App Development", "Advanced System Design"],
            "is_required": False
        },
        {
            "question_key": "Q6",
            "question_text": "How clear and effective was the instructor's delivery?",
            "question_type": "linear_scale",
            "inferred_data_type": "numeric",
            "options": ["1", "2", "3", "4", "5"],
            "scale_min": 1,
            "scale_max": 5,
            "is_required": True
        },
        {
            "question_key": "Q7",
            "question_text": "Would you recommend this workshop to your peers?",
            "question_type": "yes_no",
            "inferred_data_type": "categorical",
            "options": ["Yes", "No", "Maybe"],
            "is_required": True
        },
        {
            "question_key": "Q8",
            "question_text": "What aspects of the workshop did you like the most?",
            "question_type": "paragraph",
            "inferred_data_type": "text",
            "options": [],
            "is_required": False
        },
        {
            "question_key": "Q9",
            "question_text": "What improvements or changes would you suggest?",
            "question_type": "paragraph",
            "inferred_data_type": "text",
            "options": [],
            "is_required": False
        }
    ]

    positive_feedback_pool = [
        "The live coding demonstrations on AI-assisted coding and FastAPI were phenomenal.",
        "Practical hands-on session made difficult backend concepts very clear and easy to follow.",
        "Great energy from the instructor and very well structured presentation slides.",
        "Loved building a working AI application in real time during the second half.",
        "Clear step-by-step guidance on connecting frontend React with modern FastAPI endpoints.",
        "Interactive Q&A was super helpful, instructor cleared all our doubts patiently.",
        "Practical examples rather than just boring slides. Outstanding workshop!",
        "The AI integration section was eye opening and directly applicable to our capstone project.",
        "Loved the clear explanations of REST API architecture and database models.",
        "The best tech workshop we had this semester. Very inspiring!"
    ]

    negative_feedback_pool = [
        "The pace in the second half was a bit too fast for beginners without prior Python experience.",
        "Please provide code repositories and slides earlier before the session starts.",
        "Wi-Fi connection in the lab was unstable, which made following cloud deployment steps harder.",
        "Would prefer extending the session to a two-day bootcamp to cover advanced topics in depth.",
        "Some advanced AI prompting techniques needed more foundational explanation.",
        "Need more time allocated for hands-on practice rather than rapid live coding.",
        "Audio had occasional echo in the auditorium back rows.",
        "Please include more beginner-friendly debugging tips."
    ]

    dept_weights = [0.38, 0.28, 0.22, 0.12]
    year_weights = [0.20, 0.35, 0.30, 0.15]
    topic_weights = [0.38, 0.32, 0.18, 0.12]
    
    responses = []
    base_time = datetime.datetime.now() - datetime.timedelta(days=7)
    
    total_count = 248
    for i in range(1, total_count + 1):
        timestamp = base_time + datetime.timedelta(minutes=random.randint(10, 8000))
        dept = random.choices(["Computer Science", "Information Technology", "AI & Data Science", "Electronics & Communication"], weights=dept_weights)[0]
        year = random.choices(["1st Year", "2nd Year", "3rd Year", "4th Year"], weights=year_weights)[0]
        topic = random.choices(["AI-assisted Coding & LLMs", "Python & FastAPI Backends", "React & Modern UI Systems", "Cloud Deployment & DevOps"], weights=topic_weights)[0]
        
        # 2nd year and CS/AI departments give slightly higher ratings
        rating_boost = 0.3 if year in ["2nd Year", "3rd Year"] else 0.0
        rating = random.choices([5, 4, 3, 2, 1], weights=[0.50 + rating_boost, 0.32, 0.12, 0.04, 0.02])[0]
        instructor_rating = min(5, max(1, rating + random.choice([-1, 0, 0, 1])))
        
        # Recommendation correlates with rating
        if rating >= 4:
            recommend = random.choices(["Yes", "Maybe"], weights=[0.92, 0.08])[0]
        elif rating == 3:
            recommend = random.choices(["Maybe", "Yes", "No"], weights=[0.60, 0.25, 0.15])[0]
        else:
            recommend = random.choices(["No", "Maybe"], weights=[0.75, 0.25])[0]
            
        future_skills_count = random.randint(1, 3)
        future_skills = random.sample(
            ["Autonomous AI Agents", "Vector Databases & RAG", "Docker & Kubernetes", "Mobile App Development", "Advanced System Design"],
            future_skills_count
        )
        
        pos_text = random.choice(positive_feedback_pool) if random.random() > 0.15 else ""
        neg_text = random.choice(negative_feedback_pool) if random.random() > 0.35 else ""
        
        raw_row = {
            "Timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            questions[0]["question_text"]: rating,
            questions[1]["question_text"]: dept,
            questions[2]["question_text"]: year,
            questions[3]["question_text"]: topic,
            questions[4]["question_text"]: ", ".join(future_skills),
            questions[5]["question_text"]: instructor_rating,
            questions[6]["question_text"]: recommend,
            questions[7]["question_text"]: pos_text,
            questions[8]["question_text"]: neg_text
        }
        
        cleaned_row = {
            "Q1": float(rating),
            "Q2": dept,
            "Q3": year,
            "Q4": topic,
            "Q5": future_skills,
            "Q6": float(instructor_rating),
            "Q7": recommend,
            "Q8": pos_text if pos_text else None,
            "Q9": neg_text if neg_text else None
        }
        
        responses.append({
            "response_number": i,
            "submission_timestamp": timestamp,
            "raw_data": raw_row,
            "cleaned_data": cleaned_row,
            "is_valid": True
        })

    return {
        "title": "Full-Stack AI & Python Workshop Feedback",
        "description": "Comprehensive feedback collected from participants across engineering departments regarding curriculum, instructor clarity, and future technical roadmap.",
        "source_type": "demo",
        "source_url": "https://docs.google.com/forms/d/e/1FAIpQLSc-workshop-ai-sample-demo/viewform",
        "questions": questions,
        "responses": responses
    }

def get_customer_satisfaction_dataset() -> Dict[str, Any]:
    random.seed(101)
    questions = [
        {
            "question_key": "Q1",
            "question_text": "How likely are you to recommend FormMind AI to a colleague? (NPS 0-10)",
            "question_type": "rating",
            "inferred_data_type": "numeric",
            "options": [str(i) for i in range(11)],
            "scale_min": 0,
            "scale_max": 10,
            "is_required": True
        },
        {
            "question_key": "Q2",
            "question_text": "What pricing tier are you currently subscribed to?",
            "question_type": "multiple_choice",
            "inferred_data_type": "categorical",
            "options": ["Free Community", "Pro Professional", "Enterprise Team"],
            "is_required": True
        },
        {
            "question_key": "Q3",
            "question_text": "Which primary feature delivers the most value for your team?",
            "question_type": "multiple_choice",
            "inferred_data_type": "categorical",
            "options": ["Automated AI Insights", "Natural Language Chat with Data", "Smart PDF / Word Reports", "Excel Multi-tab Workbooks"],
            "is_required": True
        },
        {
            "question_key": "Q4",
            "question_text": "How would you rate customer support responsiveness?",
            "question_type": "linear_scale",
            "inferred_data_type": "numeric",
            "options": ["1", "2", "3", "4", "5"],
            "scale_min": 1,
            "scale_max": 5,
            "is_required": True
        },
        {
            "question_key": "Q5",
            "question_text": "What additional integrations or features would you like to see?",
            "question_type": "paragraph",
            "inferred_data_type": "text",
            "options": [],
            "is_required": False
        }
    ]
    
    ideas = [
        "Direct Slack and Microsoft Teams webhook alerts for incoming form submissions.",
        "Scheduled weekly PDF email summaries sent automatically to department heads.",
        "Support for Typeform and SurveyMonkey direct import alongside Google Forms.",
        "Custom branding and white-labeling on PDF and DOCX generated reports.",
        "Real-time streaming charts for active survey campaigns."
    ]
    
    responses = []
    base_time = datetime.datetime.now() - datetime.timedelta(days=14)
    total_count = 185
    for i in range(1, total_count + 1):
        timestamp = base_time + datetime.timedelta(minutes=random.randint(10, 15000))
        tier = random.choices(["Free Community", "Pro Professional", "Enterprise Team"], weights=[0.45, 0.38, 0.17])[0]
        nps = random.choices([10, 9, 8, 7, 6, 5, 4, 3], weights=[0.40, 0.30, 0.15, 0.08, 0.04, 0.01, 0.01, 0.01])[0]
        feature = random.choices(["Automated AI Insights", "Natural Language Chat with Data", "Smart PDF / Word Reports", "Excel Multi-tab Workbooks"], weights=[0.35, 0.33, 0.20, 0.12])[0]
        support = random.choices([5, 4, 3, 2, 1], weights=[0.60, 0.28, 0.08, 0.03, 0.01])[0]
        feedback = random.choice(ideas) if random.random() > 0.3 else ""
        
        raw_row = {
            "Timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            questions[0]["question_text"]: nps,
            questions[1]["question_text"]: tier,
            questions[2]["question_text"]: feature,
            questions[3]["question_text"]: support,
            questions[4]["question_text"]: feedback
        }
        cleaned_row = {
            "Q1": float(nps),
            "Q2": tier,
            "Q3": feature,
            "Q4": float(support),
            "Q5": feedback if feedback else None
        }
        responses.append({
            "response_number": i,
            "submission_timestamp": timestamp,
            "raw_data": raw_row,
            "cleaned_data": cleaned_row,
            "is_valid": True
        })
        
    return {
        "title": "Enterprise SaaS Customer Satisfaction & Feature Survey",
        "description": "Quarterly customer feedback assessing Net Promoter Score (NPS), tier satisfaction, feature utilization, and roadmap requests.",
        "source_type": "demo",
        "source_url": "https://docs.google.com/forms/d/e/1FAIpQLSe-nps-customer-survey-demo/viewform",
        "questions": questions,
        "responses": responses
    }
