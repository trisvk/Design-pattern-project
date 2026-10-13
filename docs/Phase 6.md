# Phase 6 — Strategy questions

**Pattern / focus:** Strategy.

**Read first:** [Guide 06](../../materials/guides/06-strategy.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example shipping quotes) as if they were your greenhouse classes.
- When a question asks about *this application*, refer to irrigation (or lighting) policies, location context, and the automation API from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Strategy in plain language. How does the **context** use a strategy, and why must “choose which algorithm” stay separate from “run the algorithm”?

> [!NOTE]
> ***Your Answer***
>
> The Strategy allows a program to use different algorithms for the same task. The context works with the selected strategy through a common method. Choosing the algorithm is separate from running it so that each strategy can work independently. In our greenhouse system, the automation service can use either Conservative or Aggressive strategies while keeping the same structure and process.

2. Name the participants (**strategy**, **concrete strategies**, **context**, **client**). What goes wrong when all policies live as `if/elif` inside the context (or inside an HTTP router)?

> [!NOTE]
> ***Your Answer***
>
> The strategy is the automation strategy interface, the concrete strategies are conservative moisture strategy and aggressive moisture strategy, the context is the automation service that uses the selected strategy, and the client is the API or frontend that requests automation. If all algorithms are written using if/elif statements inside the context or HTTP router, the code becomes harder to read, test, and maintain. Adding a new strategy would also require changing the existing code, increasing the risk of errors.

3. When should you use Strategy, and when should you skip it (one algorithm only; or the variation is a **lifecycle mode** rather than a chosen policy)?

> [!NOTE]
> ***Your Answer***
>
> Strategy should be used when a system has multiple algorithms for the same task and needs to switch between them. It is unnecessary when there is only one algorithm and no need for alternatives. Strategy should also be avoided when the changes represent different lifecycle states rather than selected policies, because the state pattern is more suitable for managing those changes.

## B. This phase of the application

4. In this lab, what does a strategy’s `decide(context)` return (action + reason)? Give a concrete difference you implemented (or were required to implement) between **conservative** and **aggressive** on the **same** moisture reading and zone thresholds.

> [!NOTE]
> ***Your Answer***
>
> In this lab, decide(context) returns a recommendation containing an action (wait or irrigate) and a reason explaining the decision. With the same moisture reading of 0.35, a low threshold of 0.20, and a high threshold of 0.45, the conservative strategy returns wait because the moisture is above the low threshold. The aggressive strategy returns irrigate because the moisture is below the high threshold.

5. Where do the numbers in `LocationAutomationContext` (or your equivalent) come from? Latest moisture may already be in `sensor_readings` from a manual read, the simulation sampler, or MQTT translation — why does this phase not add a scheduler or a broker? Why must strategies receive a plain context object, not SQLAlchemy rows or FastAPI types? Why are thresholds read from **zones**, not hardcoded in the strategy class?

> [!NOTE]
> ***Your Answer***
>
> The numbers in LocationAutomationContext come from the database. The latest moisture reading comes from sensor_readings, while the low and high thresholds come from zones. This phase does not need a scheduler or MQTT broker because sensor readings are already collected in Phase 5. Strategies receive a plain context object to keep them independent of SQLAlchemy and FastAPI, making them easier to test and reuse. Thresholds are stored in zones instead of being hardcoded because each zone can have different moisture requirements.

6. The active `strategy_key` is **persisted** per `location_id` (for example in `automation_rules`). Why must `POST .../automation/evaluate` use the **saved** key rather than a key the client sends only in that request? What happens on the next evaluate after the operator changes strategy but moisture stays the same?

> [!NOTE]
> ***Your Answer***
>
> The POST .../automation/evaluate endpoint must use the saved strategy_key to ensure the system follows the operator's selected strategy consistently, even after refreshing the page. When the operator changes the strategy, the new choice is saved in the database. On the next evaluation, the system uses the updated strategy and return a different recommendation even if the moisture reading stays the same. For example, changing from conservative to aggressive can change the action from wait to irrigate.

7. Strategy **recommends** (irrigate / wait). It should not itself start a pump. Why keep **decide** separate from **execute**? Which later pattern is meant to carry out the action?

> [!NOTE]
> ***Your Answer***
>
> I keep decide() separate from execute() because deciding whether to irrigate and actually controlling a pump are different responsibilities. The Strategy pattern only recommends an action based on sensor readings and thresholds, without directly controlling hardware. This will keep the system safer, easier to test, and more flexible. The Command Pattern, introduced in a later phase, is responsible for carrying out the recommended action through the actuator system.

## C. Compare, contrast, and scenarios

8. Contrast Strategy with **State** (Phase 8). Both delegate to an object with the same shape. Who typically **changes** the active object, and is the variation a **policy** or a **lifecycle**?

> [!NOTE]
> ***Your Answer***
>
> The Strategy pattern is used to switch between different policies or algorithms, while the State pattern manages different lifecycle states of an object. In strategy, the client or operator usually chooses which strategy to use. In state, the system usually changes its active state automatically based on events or conditions. Strategy focuses on how a task is performed, while State focuses on how an object's behavior changes during its lifecycle.

9. Contrast Strategy with **Adapter** (Phase 5) and with **Builder** (Phase 4). Which one translates a foreign API, which one assembles a valid aggregate, and which one swaps an algorithm?

> [!NOTE]
> ***Your Answer***
>
> The Adapter pattern (Phase 5) translates data from different sources, into a common format that the system can understand. The Builder pattern (Phase 4) assembles and validates a complete location configuration with zones and thresholds. The Strategy pattern (Phase 6) allows the system to switch between different algorithms, such as conservative and aggressive irrigation, without changing the main automation code.

10. A classmate writes one “mega-strategy” that still contains `if conservative` / `if aggressive` inside a single class. Another strategy class calls the actuator adapter to water immediately. Explain why each is a trap.

> [!NOTE]
> ***Your Answer***
>
> In my opinion, the first approach is a trap because putting if conservative and if aggressive inside one class defeats the purpose of the Strategy pattern. It becomes harder to maintain, test, and add new algorithms. The second approach is also a trap because a strategy should only recommend an action, not directly control the pump. Mixing decisions with execution makes the code harder to test and can cause unwanted actions.
