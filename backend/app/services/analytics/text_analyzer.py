import re
from collections import Counter
from typing import Dict, Any, List

STOP_WORDS = {
    "the", "and", "a", "to", "of", "in", "i", "is", "that", "it", "on", "you", "this",
    "for", "but", "with", "are", "have", "be", "at", "or", "as", "was", "so", "if",
    "out", "not", "we", "my", "all", "very", "our", "me", "from", "they", "an", "by",
    "about", "what", "more", "some", "like", "would", "just", "been", "can", "also",
    "will", "up", "had", "which", "were", "than", "them", "much", "even", "when", "your"
}

POSITIVE_KEYWORDS = {
    "phenomenal", "great", "excellent", "outstanding", "loved", "clear", "helpful", "practical",
    "inspiring", "good", "best", "awesome", "fantastic", "amazing", "insightful", "valuable",
    "smooth", "effective", "interactive", "engaging", "patient", "informative", "enjoyed", "positive",
    "easy", "fast", "super", "structured", "detailed", "fun", "perfect"
}

NEGATIVE_KEYWORDS = {
    "slow", "difficult", "hard", "unstable", "poor", "confusing", "echo", "issue",
    "problem", "bug", "crash", "lacking", "rush", "rushed", "missing", "delay", "boring",
    "improve", "improvement", "trouble", "fail", "failed", "bad", "worse", "complicated",
    "unclear", "overwhelmed", "noise", "lag"
}

class TextAnalyzer:
    """
    Performs NLP text analysis, theme extraction, keyword counting, and sentiment scoring.
    """

    @staticmethod
    def analyze_text_responses(questions: List[Dict[str, Any]], responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        results = {}
        
        for q in questions:
            if q.get("inferred_data_type") != "text":
                continue

            k = q["question_key"]
            texts = []
            for r in responses:
                val = r.get("cleaned_data", {}).get(k)
                if val and isinstance(val, str) and len(val.strip()) > 3:
                    texts.append(val.strip())

            if not texts:
                continue

            # Keywords extraction
            words = []
            for t in texts:
                cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', ' ', t.lower())
                tokens = [w for w in cleaned_text.split() if len(w) > 3 and w not in STOP_WORDS]
                words.extend(tokens)

            top_keywords = [{"word": w, "count": c} for w, c in Counter(words).most_common(12)]

            # Sentiment calculation
            pos_count = 0
            neg_count = 0
            neutral_count = 0
            
            positive_snippets = []
            negative_snippets = []
            suggestion_snippets = []

            for t in texts:
                t_lower = t.lower()
                pos_hits = sum(1 for w in POSITIVE_KEYWORDS if w in t_lower)
                neg_hits = sum(1 for w in NEGATIVE_KEYWORDS if w in t_lower)

                if pos_hits > neg_hits:
                    pos_count += 1
                    if len(positive_snippets) < 8 and len(t) > 15:
                        positive_snippets.append(t)
                elif neg_hits > pos_hits:
                    neg_count += 1
                    if len(negative_snippets) < 8 and len(t) > 15:
                        negative_snippets.append(t)
                else:
                    neutral_count += 1

                # Suggestion detection
                if any(kw in t_lower for kw in ["suggest", "please", "would like", "recommend", "need more", "extend", "should", "hope"]):
                    if len(suggestion_snippets) < 8:
                        suggestion_snippets.append(t)

            total_evaluated = max(1, len(texts))
            pos_pct = round((pos_count / total_evaluated) * 100, 1)
            neg_pct = round((neg_count / total_evaluated) * 100, 1)
            neu_pct = round((neutral_count / total_evaluated) * 100, 1)

            # Sentiment score from -1.0 to +1.0
            sentiment_score = round((pos_count - neg_count) / total_evaluated, 2)

            # Recurring themes summary
            themes = []
            if top_keywords:
                top_3_words = [kw["word"].title() for kw in top_keywords[:3]]
                themes.append(f"Frequent discussion around {', '.join(top_3_words)}.")
            if pos_pct >= 60:
                themes.append(f"Overwhelmingly positive tone ({pos_pct}% positive feedback).")
            elif neg_pct >= 25:
                themes.append(f"Notable areas of concern identified ({neg_pct}% constructive critiques).")

            results[k] = {
                "question_key": k,
                "question_text": q["question_text"],
                "total_responses": len(texts),
                "sentiment": {
                    "score": sentiment_score,
                    "positive_percentage": pos_pct,
                    "neutral_percentage": neu_pct,
                    "negative_percentage": neg_pct
                },
                "top_keywords": top_keywords,
                "recurring_themes": themes,
                "positive_feedback": positive_snippets,
                "negative_feedback": negative_snippets,
                "suggestions": suggestion_snippets
            }

        return results
