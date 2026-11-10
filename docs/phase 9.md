# Phase 9 — Decorator questions

**Pattern / focus:** Decorator.

**Read first:** [Guide 09](../../materials/guides/09-decorator.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example HTTP client wrappers) as if they were your greenhouse classes.
- When a question asks about *this application*, refer to `ActuatorPort`, policy decorators, and `actuator_execution_log` from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Decorator in plain language. Why is stacking wrappers a flexible alternative to a combinatorial explosion of subclasses (`LoggingRetryMaxRuntimeActuator`, …)?

> [!NOTE]
> ***Your Answer***
>
> The Decorator pattern adds extra behaviour to an object by wrapping it in another object with the same interface. Each wrapper adds one thing, and you can combine them freely. With subclasses I will need a new class for every combination, which quickly becomes too many classes.

2. Name the participants (**component**, **concrete component**, **decorator**, **concrete decorators**). What interface does every decorator present to the caller, and why must that match the wrapped component?

> [!NOTE]
> ***Your Answer***
>
> The component is ActuatorPort. The concrete component is SimulationActuatorAdapter. The decorator is a class that implements ActuatorPort and holds an inner port. The concrete decorators are LoggingActuatorDecorator and MaxRunTimeActuatorDecorator. They all have the same apply(device_id, command, payload) method, so the caller can use them exactly like the original.

3. **Order matters.** Using logging and retry (or logging and max-run-time) as an example, explain how wrapping A around B can change what you observe compared with wrapping B around A.

> [!NOTE]
> ***Your Answer***
>
> The order of wrappers changes what happens. In my app, logging is outside and max run time is inside. So when max run time blocks a command, logging still writes a failed row. If I swapped them, the block would happen before the logger and the attempt would not be logged.

## B. This phase of the application

4. What is `ActuatorPort` here, and which **at least two** decorators did you stack around the real adapter (for example logging and max run-time)? Where is the chain wired (composition root / factory), and why not inside the HTTP router?

> [!NOTE]
> ***Your Answer***
>
> ActuatorPort is the interface for controlling an actuator, with one method, apply. I wrapped SimulationActuatorAdapter with max run time, and then with logging on the outside. The chain is built in build_actuator_port() in interfaces/api/actuators.py, and the route only calls apply. The rules are not in the router, so HTTP code stays simple and other callers can’t skip them.

5. Max run-time can **short-circuit**: the inner adapter is never called. Why must a blocked attempt still produce a row in `actuator_execution_log` with `success=false` and the policy named in `policy_applied`?

> [!NOTE]
> ***Your Answer***
>
> A blocked attempt is still something that happened, so it should be recorded. Saving it with success=false shows that the command was refused. policy_applied shows which rule refused it, here maxRunTime. It will be useful for debugging and for a full history.

6. How does max run-time know the actuator has been running too long (for example `actuator_states.updated_at` from Phase 8)? Why is that data from **State**, not something the decorator should invent as a second lifecycle?

> [!NOTE]
> ***Your Answer***
>
> The decorator reads the state and updated_at from actuator_states, which comes from Phase 8. If the state is running and updated_at is 30 minutes or more ago, it blocks the command. It uses the Phase 8 State because that is the one true source of the actuator’s lifecycle. A second timer inside the decorator could get out of sync and give wrong results

7. `GET /api/actuators/executions` feeds the dashboard execution log. Why persist attempts in the database instead of only printing to stdout? What should the UI show after a blocked attempt and a refresh?

> [!NOTE]
> ***Your Answer***
>
> Printing to stdout is lost when the container restarts, and it doesn’t show in the dashboard. Saving attempts in actuator_execution_log keeps a permanent history that the API and UI can read. After a blocked attempt and a refresh, the UI shows a new red “failed” row. That row shows maxRunTime, logging and “Max run time exceeded”.

## C. Compare, contrast, and scenarios

8. Contrast Decorator with **Adapter**. Both wrap. One **keeps** the interface and **adds** behaviour; the other **changes** the interface and **translates**. Which is which in this greenhouse (Phase 9 vs Phase 5)?

> [!NOTE]
> ***Your Answer***
>
> Both patterns wrap another object, but for different reasons. Adapter (Phase 5) changes the interface: it turns different sensor formats into one standard Reading. Decorator (Phase 9) keeps the same ActuatorPort interface. It only adds behaviour like logging and the max run time check.

9. Contrast Decorator with **inheritance** of combined policies. How does composition let you add or remove a policy without a new subclass for every combination?

> [!NOTE]
> ***Your Answer***
>
> With inheritance, every mix of policies needs its own subclass, like LoggingMaxRuntimeSimulationAdapter. Adding one new policy means writing many new classes. With decorators, each policy is one small class. I add or remove a policy by changing one line in build_actuator_port().

10. A classmate’s decorator changes the method signature “a little” (extra required argument, different return type). Another ignores wrap order and cannot explain whether logging runs once per logical call or per inner attempt. Explain why each is a trap.

> [!NOTE]
> ***Your Answer***
>
> If a decorator changes the method signature, it no longer matches ActuatorPort. Then it can’t replace the original, and the chain breaks. If someone ignores the wrap order, nobody can tell what gets logged: one row per action, one row per retry, or blocked attempts not at all. 
