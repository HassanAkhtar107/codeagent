# Architecture View – Space Fractions
PlantUML diagrams for the Space Fractions educational game.

---

## Use Case Diagram

```plantuml
@startuml UseCaseDiagram
left to right direction
actor "Student" as Student
actor "Admin" as Admin

rectangle "Space Fractions" {
  usecase "Play Game" as UC1
  usecase "View Score" as UC2
  usecase "View Help" as UC3
  usecase "Pause Game" as UC4
  usecase "Resume Game" as UC5
  usecase "Answer Question" as UC6
  usecase "View Game Over Screen" as UC7
  usecase "Manage Questions" as UC8
  usecase "Add Question" as UC9
  usecase "Edit Question" as UC10
  usecase "Delete Question" as UC11
}

Student --> UC1
Student --> UC2
Student --> UC3
Student --> UC4
Student --> UC5
Student --> UC6
Student --> UC7
Admin --> UC8
UC8 <|-- UC9
UC8 <|-- UC10
UC8 <|-- UC11
@enduml
```

---

## Class Diagram

```plantuml
@startuml ClassDiagram
class Game {
  - state: GameState
  - score: int
  - current_question_index: int
  - questions: list[Question]
  + start(): void
  + pause(): void
  + resume(): void
  + end(): void
  + answer(choice: int): bool
  + get_score(): int
  + next_question(): Question
}

class Question {
  - id: int
  - text: str
  - options: list[str]
  - answer: str
  - difficulty: str
  + is_correct(choice: str): bool
}

class User {
  - name: str
  - score: int
  + update_score(points: int): void
  + get_score(): int
  + reset(): void
}

class Admin {
  - pin: str
  + authenticate(pin: str): bool
  + add_question(question: Question): void
  + delete_question(qid: int): void
  + update_question(qid: int, question: Question): void
}

class QuestionBank {
  - filepath: str
  + load(): list[Question]
  + save(questions: list[Question]): void
  + get_random(count: int): list[Question]
}

Game --> Question : uses >
Game --> User : tracks >
Game --> QuestionBank : loads from >
Admin --> QuestionBank : manages >
@enduml
```

---

## Object Diagram

```plantuml
@startuml ObjectDiagram
object game1 {
  state = "Playing"
  score = 30
  current_question_index = 3
}
object q1 {
  id = 1
  text = "What is 1/2 + 1/4?"
  answer = "3/4"
  difficulty = "easy"
}
object user1 {
  name = "Alice"
  score = 30
}
game1 --> q1
game1 --> user1
@enduml
```

---

## State Diagram

```plantuml
@startuml StateDiagram
[*] --> Intro : launch app
Intro --> Menu : press Start
Menu --> Playing : press Play
Playing --> Paused : press Pause
Paused --> Playing : press Resume
Playing --> GameOver : all questions answered
GameOver --> Menu : press Play Again
GameOver --> [*] : press Quit
Playing --> [*] : press Quit
@enduml
```

---

## Activity Diagram

```plantuml
@startuml ActivityDiagram
start
:Launch Application;
:Show Intro Screen;
:Show Main Menu;
:Player presses Play;
:Load Questions from JSON;
:Display Question;
repeat
  :Player selects answer;
  if (Correct?) then (yes)
    :Increment Score by 10;
  else (no)
    :Show Wrong Answer feedback;
  endif
  :Move to next question;
repeat while (Questions remaining?) is (yes)
:Show Game Over Screen;
:Display Final Score;
:Offer Play Again or Quit;
stop
@enduml
```

---

## Sequence Diagram

```plantuml
@startuml SequenceDiagram
participant Student
participant UI
participant Game
participant QuestionBank

Student -> UI: launches app
UI -> Game: initialise()
Student -> UI: presses Play
UI -> Game: start()
Game -> QuestionBank: load()
QuestionBank --> Game: list[Question]
Game --> UI: display first question
Student -> UI: selects answer
UI -> Game: answer(choice)
Game --> UI: result (correct/wrong)
UI --> Student: show feedback + updated score
@enduml
```

---

## Collaboration Diagram

```plantuml
@startuml CollaborationDiagram
Game -> QuestionBank : load questions
Game -> User : update score
UI -> Game : player actions
Admin -> QuestionBank : CRUD operations
@enduml
```

---

## Package Diagram

```plantuml
@startuml PackageDiagram
package "Space Fractions" {
  package "src" {
    [game.py]
    [models.py]
    [ui.py]
    [question_bank.py]
  }
  package "data" {
    [questions.json]
  }
  package "tests" {
    [test_game.py]
    [test_models.py]
  }
}
@enduml
```

---

## Component Diagram

```plantuml
@startuml ComponentDiagram
component "Game Engine" as GE
component "UI Layer" as UI
component "Question Bank" as QB
component "Admin Panel" as AP

UI --> GE : player input
GE --> QB : load/query questions
AP --> QB : CRUD operations
GE --> UI : game state updates
@enduml
```

---

## Deployment Diagram

```plantuml
@startuml DeploymentDiagram
node "Student PC" {
  artifact "space_fractions.exe" {
    component "Python Runtime"
    component "Tkinter GUI"
    component "Game Logic"
  }
  artifact "data/questions.json"
}
@enduml
```

---

## Container Diagram

```plantuml
@startuml ContainerDiagram
Person(student, "Student", "6th grade player")
Person(admin, "Admin", "Teacher/admin")

Container(app, "Space Fractions Desktop App", "Python + Tkinter", "Desktop GUI application")
ContainerDb(db, "Question Bank", "JSON file", "Stores fraction questions")

student --> app : plays
admin --> app : manages questions
app --> db : reads/writes questions
@enduml
```
