# Phase 10 — Command questions

**Pattern / focus:** Command.

**Read first:** [Guide 10](../../materials/guides/10-command.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example editor undo commands) as if they were your greenhouse classes.
- When a question asks about _this application_, refer to command objects, the invoker, `command_log`, and the controls UI from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Command in plain language. What does it mean to **objectify a request**, and what can you do with that object that you cannot do with a bare `actuator.start()` call (queue, audit, undo, history)?

> [!NOTE]
> **_Your Answer_**
>
> The Command pattern turns a request into an object. Instead of calling actuator.start() directly, I create a StartPumpCommand that holds the device, the payload and the action. Because it’s an object, it can be checked before it runs. It can also be saved, queued or undone. A bare method call just runs and leaves no trace.

2. Name the participants (**command**, **receiver**, **invoker**, **client**). Who creates the command, who triggers `execute()`, and who actually changes actuator/hardware state?

> [!NOTE]
> **_Your Answer_**
>
> The command is the object with execute(), such as StartPumpCommand. The client is CommandService, which creates it with command_for(). The invoker is CommandInvoker, which calls execute(). The receiver is the ActuatorPort chain, ending in SimulationActuatorAdapter. That’s where the device is actually changed.

3. If a command supports undo, when must it capture the data needed to reverse the action? Why is “capture **before** mutate” critical?

> [!NOTE]
> **_Your Answer_**
>
> The command must save the old data before it changes anything. For example, set_light_level should remember the old level before setting the new one. If it changes first, the old value is gone. Then there’s nothing to restore. So undo only works if the data is captured before the mutation.

## B. This phase of the application

4. Which command types did you implement (for example `start_pump`, `stop_pump`, `set_light_level`)? Why does the HTTP handler create a command and pass it to an **invoker** (or application service) instead of calling the actuator adapter from the router?

> [!NOTE]
> **_Your Answer_**
>
> I made start_pump, stop_pump and set_light_level. A registry maps each name to its class. The router doesn’t call the adapter directly. If it did, it would skip the state check, the decorators and the command_log. Keeping the logic in the service also lets other parts reuse it.

5. Walk through the execute path: (1) consult State / `allowed_commands`, (2) if illegal → **rejected**, (3) if legal → decorated `apply`, update `actuator_states`, log **success** or **failed**. Why must a rejected command **not** change actuator state and **not** reach inner `apply`?

> [!NOTE]
> **_Your Answer_**
>
> First, the service checks allowed_commands for the current state. If the command isn’t allowed, it logs rejected and stops. If it is allowed, it runs through the decorated port, then updates the state and logs success. If a decorator blocks it, the result is failed. A rejected command was illegal from the start, so it must not change the state or reach apply.

6. Distinguish **`rejected`** vs **`failed`** vs **`success`** in `command_log`. Give one greenhouse example of each. Why is “illegal in this state” not the same as “policy or adapter error after the command was accepted”?

> [!NOTE]
> **_Your Answer_**
>
> success: starting an idle pump works. rejected: sending stop_pump to an idle pump is not allowed in that state. failed: stopping a pump after 31 minutes is blocked by “Max run time exceeded”. Rejected is decided before anything runs. Failed happens after the command was accepted.

7. Why is `command_log` a **different** table from Phase 9 `actuator_execution_log`? What concern does each log record (operator intent vs policy/adapter attempt)?

> [!NOTE]
> **_Your Answer_**
>
> command_log stores what the user asked for and the final result. actuator_execution_log stores what actually reached the device port. A rejected command only appears in command_log, because it never reaches the port. Having two tables shows whether a problem came from the rules or from the device layer.

## C. Compare, contrast, and scenarios

8. Contrast Command with **Strategy**. Strategy is an interchangeable **algorithm** (decide / quote). Command is a **side-effectful request** with history. How do they cooperate in this app (Phase 6 recommends; Phase 10 executes)?

> [!NOTE]
> **_Your Answer_**
>
> trategy decides what should happen, for example “moisture is low, start the pump”. Command actually does the action and saves it in history. In my app, Phase 6 gives the recommendation and Phase 10 executes it. They are separate, so either one can change without affecting the other.

9. Contrast Command with **State**. Who **triggers** the action, and who **decides whether it is legal**? Why must commands not bypass state guards?

> [!NOTE]
> **_Your Answer_**
>
> The command triggers the action. State decides if that action is allowed right now. They have different jobs. If commands skipped the state check, an actuator could do impossible things, like stopping while it’s already idle. Then the saved state would be wrong.

10. The controls UI should disable actions that are not in `allowed_commands`. Why must the **backend** still reject illegal commands even if the UI is correct? What happens if a classmate’s command calls the raw adapter and skips State and Decorator?

> [!NOTE]
> **_Your Answer_**
>
> The UI can be bypassed with Scalar, curl or an old browser tab. Only the backend knows the real current state, so it must check every command itself. If a command called the raw adapter, it would skip State and the decorators. The device could run too long, change from the wrong state, and leave no log behind.
