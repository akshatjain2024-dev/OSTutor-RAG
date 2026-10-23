import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))

import llm
from search import get_search


def test_provider_detection():
    print("1. Testing Provider Detection...")
    prov = llm.get_active_provider(force=True)
    print(f"   Active Provider: {prov['provider']}")
    print(f"   Model: {prov['model']}")
    print(f"   Available: {prov['available']}")
    assert prov["available"], "RAG provider should be available"
    assert prov["provider"] in ("ollama", "offline"), f"Unexpected provider: {prov['provider']}"
    models = llm.list_ollama_models()
    print(f"   Detected Ollama Models: {models}")
    print("   [PASS] Provider detection verified.\n")


def test_rag_grounded_answer():
    print("2. Testing Grounded RAG Answer Generation...")
    s = get_search()
    query = "explain the four conditions for deadlock"
    search_res = s.search(query, k=3)
    results = search_res["results"]
    assert len(results) > 0, "Retrieval returned 0 results"
    print(f"   Retrieved {len(results)} chunks for '{query}'. Top score: {results[0]['score']}")

    ans, mode = llm.answer(query, results)
    print(f"   Mode: {mode}")
    print(f"   Answer snippet:\n   {ans[:200]}...")
    assert "rag:" in mode, f"Mode should be RAG generative, got {mode}"
    assert len(ans) > 50, "Answer too short"
    assert "[" in ans and "]" in ans, "Answer should contain grounded citations [n]"
    print("   [PASS] Grounded RAG answer verified.\n")


def test_rag_mcq_generation():
    print("3. Testing RAG MCQ Generation...")
    s = get_search()
    notes = [c for c in s.chunks if c["topic"] == "Deadlocks" and c["doc_type"] != "question_bank"][:5]
    qs, mode = llm.mcqs("Deadlocks", notes, n=2)
    print(f"   Mode: {mode}")
    print(f"   Generated {len(qs)} MCQs.")
    assert len(qs) >= 1, "Should generate at least 1 MCQ"
    first = qs[0]
    print(f"   Sample Question: {first['question']}")
    print(f"   Options: {first['options']}")
    print(f"   Explanation: {first.get('explanation', '')}")
    assert "question" in first and "options" in first and "answer_index" in first, "Invalid MCQ structure"
    assert len(first["options"]) == 4, "MCQ must have 4 options"
    print("   [PASS] RAG MCQ generation verified.\n")


def test_rag_viva_generation():
    print("4. Testing RAG Viva Generation...")
    s = get_search()
    notes = [c for c in s.chunks if c["topic"] == "Deadlocks"][:5]
    past = [c for c in s.chunks if c["topic"] == "Deadlocks" and c["doc_type"] == "question_bank"][:5]
    qs, mode = llm.viva("Deadlocks", notes, past, n=2)
    print(f"   Mode: {mode}")
    print(f"   Generated {len(qs)} Viva questions.")
    assert len(qs) >= 1, "Should generate at least 1 Viva question"
    first = qs[0]
    print(f"   Q: {first['question']}")
    print(f"   A: {first['answer']}")
    assert "question" in first and "answer" in first, "Invalid Viva structure"
    print("   [PASS] RAG Viva generation verified.\n")


def main():
    print("=" * 60)
    print("   OSTUTOR PURE RAG VERIFICATION SUITE")
    print("=" * 60 + "\n")
    test_provider_detection()
    test_rag_grounded_answer()
    test_rag_mcq_generation()
    test_rag_viva_generation()
    print("=" * 60)
    print("   ALL RAG VERIFICATION TESTS PASSED SUCCESSFULLY! ")
    print("=" * 60)


if __name__ == "__main__":
    main()
