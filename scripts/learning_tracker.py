#!/usr/bin/env python3
"""
Learning History Tracker for LeetVibe

Shared module for managing the learning history - tracks which concepts
the user has encountered and their quiz completion status.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional


def get_learning_history_path() -> Path:
    """Get path to the learning history file."""
    home = Path.home()
    return home / '.leetvibe' / 'learning-history.json'


def get_leetvibe_dir() -> Path:
    """Get the .leetvibe directory in the current project."""
    cwd = os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())
    return Path(cwd) / '.leetvibe'


def load_learning_history() -> dict:
    """Load the learning history from disk."""
    history_path = get_learning_history_path()
    if history_path.exists():
        try:
            with open(history_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"concepts": {}}


def save_learning_history(history: dict) -> None:
    """Save the learning history to disk."""
    history_path = get_learning_history_path()
    history_path.parent.mkdir(parents=True, exist_ok=True)
    with open(history_path, 'w') as f:
        json.dump(history, f, indent=2)


def mark_concept_seen(concept: str, source_file: str) -> bool:
    """
    Mark a concept as seen. Returns True if this is the first time seeing it.
    """
    history = load_learning_history()
    is_new = concept not in history['concepts']

    if is_new:
        history['concepts'][concept] = {
            'first_seen': datetime.now().isoformat(),
            'times_seen': 1,
            'quiz_completed': False,
            'quiz_score': None,
            'source_file': source_file,
        }
    else:
        history['concepts'][concept]['times_seen'] += 1

    save_learning_history(history)
    return is_new


def mark_quiz_completed(concept: str, score: float) -> None:
    """Mark a quiz as completed with a score (0.0 to 1.0)."""
    history = load_learning_history()

    if concept in history['concepts']:
        history['concepts'][concept]['quiz_completed'] = True
        history['concepts'][concept]['quiz_score'] = score
        history['concepts'][concept]['completed_at'] = datetime.now().isoformat()
        save_learning_history(history)


def mark_quiz_skipped(concept: str) -> None:
    """Mark a quiz as skipped."""
    history = load_learning_history()

    if concept in history['concepts']:
        history['concepts'][concept]['quiz_skipped'] = True
        history['concepts'][concept]['skipped_at'] = datetime.now().isoformat()
        save_learning_history(history)


def get_stats() -> dict:
    """Get learning statistics."""
    history = load_learning_history()
    concepts = history.get('concepts', {})

    total = len(concepts)
    completed = sum(1 for c in concepts.values() if c.get('quiz_completed'))
    skipped = sum(1 for c in concepts.values() if c.get('quiz_skipped'))
    pending = total - completed - skipped

    scores = [c.get('quiz_score', 0) for c in concepts.values()
              if c.get('quiz_completed') and c.get('quiz_score') is not None]
    avg_score = sum(scores) / len(scores) if scores else 0

    return {
        'total_concepts': total,
        'quizzes_completed': completed,
        'quizzes_skipped': skipped,
        'quizzes_pending': pending,
        'average_score': avg_score,
        'concepts': concepts,
    }


def reset_history() -> None:
    """Reset all learning history."""
    save_learning_history({"concepts": {}})


def get_pending_quizzes() -> list[dict]:
    """Get list of pending quiz requests."""
    leetvibe_dir = get_leetvibe_dir()
    pending_dir = leetvibe_dir / 'pending'

    if not pending_dir.exists():
        return []

    pending = []
    for quiz_file in sorted(pending_dir.glob('*.json')):
        try:
            with open(quiz_file, 'r') as f:
                pending.append(json.load(f))
        except (json.JSONDecodeError, IOError):
            pass

    return pending


def get_available_quizzes() -> list[dict]:
    """Get list of generated quizzes."""
    leetvibe_dir = get_leetvibe_dir()
    quizzes_dir = leetvibe_dir / 'quizzes'

    if not quizzes_dir.exists():
        return []

    quizzes = []
    for quiz_file in sorted(quizzes_dir.glob('*.md')):
        quiz_id = quiz_file.stem.split('-')[0]
        concept = '-'.join(quiz_file.stem.split('-')[1:])

        # Check if solution exists
        solutions_dir = leetvibe_dir / 'solutions'
        solution_exists = any(solutions_dir.glob(f'{quiz_id}-*')) if solutions_dir.exists() else False

        quizzes.append({
            'id': quiz_id,
            'concept': concept,
            'file': str(quiz_file),
            'solution_exists': solution_exists,
        })

    return quizzes
