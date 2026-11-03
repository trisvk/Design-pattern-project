# Phase 8 — State questions

**Pattern / focus:** State.

**Read first:** [Guide 08](../../materials/guides/08-state.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example support-ticket states) as if they were your greenhouse classes.
- When a question asks about *this application*, refer to actuator lifecycle, persisted state, and `allowed_commands` from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of the State pattern in plain language. What problem appears when lifecycle is modelled as boolean flags and scattered `if` guards?

> [!NOTE]
> ***Your Answer***
>
> The State pattern manages an object's behavior based on its current state and controls which state changes are allowed. Using many boolean flags and scattered if statements makes the code harder to understand, maintain, and test. Maybe it can also cause invalid state changes.

2. Name the participants (**context**, **state interface**, **concrete states**, **client**). How does a successful command lead to a **transition**, and where do **guards** live?

> [!NOTE]
> ***Your Answer***
>
> The context (ActuatorContext) manages the current state. The state interface defines common behavior, while concrete states define allowed actions. The client is the application service or API. After a valid command, the context changes state and saves it to the database. Guards are kept in the domain to prevent illegal transitions.

3. What is `allowed_commands` (or equivalent) for? Why is exposing “what can I do **now**?” better than letting the UI guess from a raw state string?

> [!NOTE]
> ***Your Answer***
>
> allowed_commands shows which actions an actuator can perform in its current state. The UI can use the list directly instead of checking the state and deciding which actions are allowed. As a result, the code becomes easier to manage and the risk of invalid commands is reduced.

## B. This phase of the application

4. Which actuator states did you implement (for example idle, running, error)? Sketch the **legal** transitions (which command or event moves idle → running, running → idle, into error, and out of error).

> [!NOTE]
> ***Your Answer***
>
> I implemented five actuator states: idle, running, off, error, and maintenance. An actuator can move from idle to running with a start command and return to idle with a stop command. An error event can move the actuator into the error state. After the problem is fixed, a reset command returns it to idle. Maintenance can also return to idle when the work is finished.

5. Why is actuator state stored in `actuator_states` (or equivalent) rather than only in process memory? What must still be true after you restart the backend?

> [!NOTE]
> ***Your Answer***
>
> Actuator states are stored in the actuator_states table to keep the data even when the backend stops or restarts. If states were only stored in memory, they would be lost after a restart. The backend must load the saved state from the database so each actuator keeps its previous state.

6. An **illegal** transition must raise a domain error and **must not** update the database. Why? Which HTTP status is reasonable for that case (400 or 409), and why should the rule live in the domain rather than in React?

> [!NOTE]
> ***Your Answer***
>
> An illegal transition must raise an error and leave the database unchanged to prevent incorrect actuator states. HTTP 409 Conflict is a good choice because the requested action conflicts with the current state. The rule should be handled in the domain rather than React because the backend must protect the data, even when commands come from other clients.

7. Device JSON gains `state` and `allowed_commands`. How does the dashboard use those fields (badges, disable illegal buttons)? How does this prepare **Phase 10 Command**?

> [!NOTE]
> ***Your Answer***
>
> The dashboard uses state to show colored badges for each actuator, while allowed_commands shows which actions are available. Buttons for illegal actions can be disabled to prevent mistakes. In Phase 10, the Command pattern can use these rules to execute valid commands safely.

## C. Compare, contrast, and scenarios

8. Contrast State with **Strategy**. Both look like “context delegates to an object.” Who typically **changes** the active object, and is the variation a **lifecycle** or a **selectable policy**? Give a greenhouse example of each (this phase vs Phase 6).

> [!NOTE]
> ***Your Answer***
>
> The State pattern manages an object's lifecycle, while the Strategy pattern allows users to choose different policies. In State, the active state changes when an event or command occurs. For example, a greenhouse actuator changes from idle to running when it starts. In strategy, the user usually selects the active policy. For example, in phase 6, the user can choose between conservative and aggressive irrigation strategies.

9. Contrast State with a pile of booleans (`is_running`, `is_fault`, `is_maintenance`). Why do illegal combinations of flags appear, and how do explicit state objects (or a transition table) prevent that?

> [!NOTE]
> ***Your Answer***
>
> Using many boolean flags can cause problems because several flags may be true at the same time, such as is_running and is_maintenance. These combinations can create invalid actuator states. The State pattern uses clear states and transition rules to allow only valid changes, making the code easier to understand and maintain.

10. A classmate puts HTTP status mapping or SQLAlchemy commits **inside** a concrete state class. Another state mutates a flag directly and skips `transition` / `set_state`. Explain why each is a trap.

> [!NOTE]
> ***Your Answer***
>
> Putting HTTP status codes or SQLAlchemy commits inside a state class mixes business logic with API and database code. It makes the code harder to test, maintain, and reuse. Changing a flag directly is also a problem because it skips the transition rules and may allow illegal states. All state changes should go through transition to keep the actuator safe and consistent
