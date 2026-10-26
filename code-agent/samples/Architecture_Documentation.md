# Architecture Documentation – Space Fractions

## Executive Summary

Space Fractions is an educational desktop game designed for 6th-grade students to practice and master fraction arithmetic. The game presents fraction questions in an engaging space-themed environment. Players earn points for correct answers and can view their score at any time. An admin role allows updating the question bank stored in a local JSON file.

The system is a standalone desktop application built in Python with Tkinter. It requires no network connection and runs on Windows, macOS, and Linux.

---

## Roles

- **End User (Student)**: Plays the game, answers fraction questions, views score, accesses the help screen, pauses/resumes gameplay.
- **Admin**: Updates and manages the question bank (add, edit, delete questions stored in a local JSON file).

---

## Requirements

- The game shall display fraction questions with four multiple-choice options.
- The game shall track and display the player's score in real time.
- The game shall support pause and resume functionality.
- The game shall display a help screen with instructions.
- The game shall display a game-over screen with final score and feedback.
- The game shall support an intro screen and main menu.
- The admin shall be able to add, edit, and delete questions via an admin panel.
- Questions shall be stored in a local JSON file (data/questions.json).
- The game shall support a minimum of 20 questions per session.
- The application shall run as a standalone Python Tkinter desktop app.

---

## Components

- **Game**: Core game logic, state machine (Intro, Menu, Playing, Paused, GameOver). Manages rounds, score, and question sequencing.
- **Question**: Represents a single fraction question: text, four answer options, correct answer index.
- **User**: Tracks the current player's name, score, and session history.
- **Admin**: Manages the question bank; provides CRUD operations on data/questions.json.
- **QuestionBank**: Loads and saves questions from/to the JSON data file.
- **UI**: Tkinter screens – IntroScreen, MainMenuScreen, GameScreen, PauseScreen, HelpScreen, GameOverScreen, AdminPanel.

---

## Tech Stack

- Python 3.10+
- Tkinter (standard library GUI)
- JSON (question storage – no external DB required)
- pytest (testing)

> Note: No web server, REST API, Node.js, or Docker required. This is a desktop application.

---

## API Specifications

*Not applicable – this is a standalone desktop application with no network API.*

Internal interfaces:
- `Game.start()`, `Game.pause()`, `Game.resume()`, `Game.end()`
- `Game.answer(choice: int) -> bool`
- `QuestionBank.load() -> list[Question]`
- `QuestionBank.save(questions: list[Question]) -> None`
- `Admin.add_question(question: Question) -> None`
- `Admin.delete_question(question_id: int) -> None`

---

## Database Schema

*Local JSON file only – no relational database.*

### data/questions.json

```json
[
  {
    "id": 1,
    "text": "What is 1/2 + 1/4?",
    "options": ["3/4", "1/2", "2/4", "1/3"],
    "answer": "3/4",
    "difficulty": "easy"
  }
]
```

---

## Security

- No network access required.
- Admin access is password-protected within the application (simple PIN).
- No sensitive user data is stored.

---

## Testing

Unit test strategy using pytest:
- Test correct answer scoring increments score by +10.
- Test wrong answer does not change score.
- Test game state transitions: Menu → Playing → Paused → Playing → GameOver.
- Test QuestionBank load and save operations.
- Test question checking returns correct boolean.
- Test admin add/delete question updates the bank.
- Verify all 20+ questions load correctly from JSON.

---

## Deployment

Standalone Python application:
- Run with `python main.py`
- Package with PyInstaller into a single .exe for Windows
- No installation or external dependencies beyond Python standard library

---

## Assumptions

- Web technology references in this document are not applicable; the implementation uses Python + Tkinter.
- The question bank is pre-seeded with at least 10 sample fraction questions.
- Admin PIN defaults to "1234" and is configurable in settings.
