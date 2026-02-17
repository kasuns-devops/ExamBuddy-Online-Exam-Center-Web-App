"""
End-to-end exam flow test:
- Start exam (test mode)
- Submit answers for each question (select index 0)
- Finalize exam and print results
"""
import requests
import time

BASE = "http://localhost:8000"


def run_e2e(mode='test', project_id='demo-project-id', question_count=5):
    print('\n=== E2E Exam Flow Test ===')
    # Start exam
    payload = {
        "project_id": project_id,
        "mode": mode,
        "difficulty": None,
        "question_count": question_count
    }
    print('Starting exam...', payload)
    r = requests.post(f"{BASE}/api/exams/start", json=payload)
    print('Start status:', r.status_code)
    if r.status_code != 201:
        print('Start failed:', r.text)
        return
    data = r.json()
    session_id = data['session_id']
    questions = data['questions']
    print(f"Session: {session_id}, questions returned: {len(questions)}")

    # Present each question (record presentation) then submit an answer
    from datetime import datetime, timezone

    for i, q in enumerate(questions, 1):
        qid = q['question_id']

        # Record presentation timestamp (as frontend would)
        presented_at = datetime.now(timezone.utc).isoformat()
        present_payload = {"question_id": qid, "presented_at": presented_at}
        print(f"Recording presentation for Q{i}/{len(questions)}: {qid} @ {presented_at}")
        r = requests.post(f"{BASE}/api/exams/{session_id}/present", json=present_payload)
        print('  present status:', r.status_code)

        # Simulate time spent viewing the question
        time.sleep(0.5)

        # Submit answer (choose index 0 for each)
        ans = 0
        payload = {"question_id": qid, "answer_index": ans}
        print(f"Submitting answer for Q{i}/{len(questions)}: {qid} -> {ans}")
        r = requests.post(f"{BASE}/api/exams/{session_id}/answers", json=payload)
        print('  status:', r.status_code)
        try:
            print('  resp:', r.json())
        except Exception:
            print('  resp text:', r.text)
        time.sleep(0.2)

    # Finalize
    print('\nFinalizing exam...')
    r = requests.post(f"{BASE}/api/exams/{session_id}/submit")
    print('Finalize status:', r.status_code)
    if r.status_code == 200:
        print('Results:', r.json())
    else:
        print('Finalize failed:', r.text)


if __name__ == '__main__':
    run_e2e()
