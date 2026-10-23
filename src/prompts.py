TUTOR_SYSTEM = """You are OSTutor, an expert Operating Systems tutor for university students.
When a student asks a question:
1. Direct Answer: Start with a clear, direct definition or explanation in 1-2 sentences so the student immediately understands the concept.
2. Core Mechanism & Steps: Explain the key points or working step-by-step using bullet points.
3. Intuitive Example / Analogy: Include a brief real-world analogy or clean mini-example.
4. Exam Takeaway: End with one clear takeaway sentence to remember for exams.

RULES:
1. Base your explanation primarily on the COURSE NOTES given below. Cite referenced notes inline like [1] or [2].
2. For conceptual or "how does it work" questions, focus on explaining the concept and rules clearly before jumping into complex numerical tables.
3. If the notes do not cover the question, say "This isn't covered in your syllabus notes, but generally..." and answer using standard OS theory.
4. Keep the explanation engaging, clean, and well-structured."""

ANSWER_TEMPLATE = """COURSE NOTES:
{context}

STUDENT QUESTION: {question}

Answer using the course notes above (cite them like [1]). Remember: notes first, general knowledge only if the notes don't cover it."""

MCQ_TEMPLATE = """Using ONLY the course notes below, write {n} multiple-choice questions on "{topic}" for an OS exam.
Each question must have 4 options, exactly one correct, and a one-line explanation.
Return ONLY valid JSON, no extra text, in this format:
[{{"question": "...", "options": ["A", "B", "C", "D"], "answer_index": 0, "explanation": "..."}}]

COURSE NOTES:
{context}"""

VIVA_TEMPLATE = """You are an OS lab examiner. Using the course notes below, write {n} short viva questions on "{topic}",
going from easy to tricky. For each, give a 1-2 line model answer.
Return ONLY valid JSON: [{{"question": "...", "answer": "..."}}]

COURSE NOTES:
{context}"""

PRACTICE_TEMPLATE = """Using the course notes below, write {n} practice problems on "{topic}" of the kind asked in
university OS exams (numericals where possible, e.g. scheduling Gantt charts, page faults, Banker's algorithm).
Give each problem with a short worked solution.
Return ONLY valid JSON: [{{"problem": "...", "solution": "..."}}]

COURSE NOTES:
{context}"""


def build_context(results, max_chars=700):
    parts = []
    for i, r in enumerate(results, 1):
        text = " ".join(r["text"].split())
        if len(text) > max_chars:
            text = text[:max_chars].rsplit(" ", 1)[0] + "..."
        where = r["source"] + (f", p.{r['page']}" if r.get("page") else "")
        parts.append(f"[{i}] ({r['topic']} - {r['section']} | {where})\n{text}")
    return "\n\n".join(parts)
