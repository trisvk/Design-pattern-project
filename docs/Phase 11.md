# Phase 11 — Observer questions

**Pattern / focus:** Observer.

**Read first:** [Guide 11](../../materials/guides/11-observer.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example live auction bids) as if they were your greenhouse classes.
- When a question asks about _this application_, refer to the event bus, alerts, publishers, and the event feed from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Observer in plain language. What is a **one-to-many** dependency here, and why must the subject notify dependents **without** knowing their concrete classes?

> [!NOTE]
> **_Your Answer_**
>
> Observer lets one object announce that something happened, and many others react to it. That's the one-to-many part: one event bus, and many subscribers listening. In my app, one new reading can lead to a threshold check, an alert, and later a WebSocket message. The subject doesn't know the subscribers' classes, so new listeners can be added without changing the publisher.

2. Name the participants (**subject / event bus**, **observer / subscriber**, **concrete observers**, **event**, **publisher**). What does `subscribe` / `unsubscribe` / `publish` (or `notify`) each do? This example’s `EventBus` implements `subscribe` and `publish` only.

> [!NOTE]
> **_Your Answer_**
>
> The subject is EventBus. The observers are subscribers: ThresholdSubscriber and AlertPersistenceSubscriber are the concrete ones. The events are objects like ReadingCreated or CommandFailed, and the publishers are ReadingIngest and CommandService. subscribe registers a handler for an event type, and publish sends an event to every handler of that type. unsubscribe would remove a handler, but my bus doesn't need it yet.

3. When should you use Observer, and when should you skip it (only one listener forever; or you need a strict multi-step workflow with guaranteed order)?

> [!NOTE]
> **_Your Answer_**
>
> Observer fits best when several parts of the system care about the same event. A new reading is a good example: today it creates alerts, and tomorrow it will update the live dashboard. If only one listener will ever exist, though, a direct method call is simpler. The same goes for a strict step-by-step workflow, because events make the order harder to follow and to guarantee.

## B. This phase of the application

4. Give at least two **domain events** you publish in this lab, including `reading.created` (only when `tracking_enabled` is true), a threshold-crossed event, command-failed, and `ActuatorStateChanged`. The persistence subscriber stores `state.changed` only when that state is `error`. Who publishes `reading.created`, and why do a manual read, the simulation sampler, and MQTT translation share that one ingest publish? Why must a publisher **not** import the alerts repository or the UI?

> [!NOTE]
> **_Your Answer_**
>
> Four domain events are published: ReadingCreated, ThresholdCrossed, CommandFailed and ActuatorStateChanged. The one that starts it all, reading.created, comes from ReadingIngest.record(), but only if tracking_enabled is true. Manual reads, the sampler and MQTT all pass through that single method, so they can never follow different rules. A publisher must not import the alerts repository or the UI. Otherwise it would become tightly coupled, and every change to alerts or screens would force a change in the reading code.

5. What does `AlertPersistenceSubscriber` (or your equivalent) do when it handles an event? Name the three stored rows: `threshold.crossed` / `warning` / `Moisture below zone low`, `command.failed` / `warning` / the failure message, and `state.changed` / `critical` / `Actuator entered error`. Why do alerts live in the `alerts` table so the event feed still shows them after a **refresh**?

> [!NOTE]
> **_Your Answer_**
>
> Whenever an important event arrives, AlertPersistenceSubscriber turns it into a row in the alerts table. A low moisture reading produces threshold.crossed / warning / "Moisture below zone low". For a failed command, the row is command.failed / warning with the failure message. The most serious case is an actuator entering error, which is stored as state.changed / critical / "Actuator entered error". Since these rows live in the database and not in React state, they're still there after a page refresh.

6. The dashboard Event feed **polls** `GET /api/alerts` every 5 seconds in this phase. `services/realtime.ts` is only a **stub**. Why is full WebSocket **not** required in this phase? What should Phase 12 plug into so you do **not** re-implement pub/sub inside socket handlers? Phase 12 subscribes a dashboard socket to this same bus, and the example publishes `AlertCreated` after each insert for that socket.

> [!NOTE]
> **_Your Answer_**
>
> WebSockets aren't needed yet, because this phase focuses on the Observer pattern itself. Polling GET /api/alerts every 5 seconds already keeps the Event feed up to date. Meanwhile, realtime.ts is just a stub with the right shape, so the UI won't have to change later. In Phase 12, a WebSocket subscriber will simply join the same EventBus and forward events to the browser. That way, pub/sub never has to be rebuilt inside the socket code.

7. Describe the must-demo path: a **tracked** low-moisture reading leads to an alert row that appears in the feed after poll. Which objects collaborate (reading pipeline → bus → subscriber → API → UI), and which object must **not** write the alert directly? What is stored, and what is not published, when `tracking_enabled` is false?

> [!NOTE]
> **_Your Answer_**
>
> It all starts when a tracked moisture sensor reports a low value. ReadingIngest saves the reading and publishes ReadingCreated. Next, ThresholdSubscriber compares the value with the zone's low threshold and, if needed, publishes ThresholdCrossed. AlertPersistenceSubscriber saves the alert, and within five seconds the Event feed shows it. Note that ReadingIngest never writes the alert itself. With tracking turned off, the reading is still saved, but nothing is published.

## C. Compare, contrast, and scenarios

8. Contrast Observer with **Facade**. Facade simplifies **calling into** a subsystem. Observer **fans out** notifications after something happened. How do both appear in this greenhouse (Phase 7 overview vs this phase)?

> [!NOTE]
> **_Your Answer_**
>
> Facade and Observer point in opposite directions. A facade makes it easy to ask a subsystem for something, while Observer spreads news after something has happened. My Phase 7 overview facade gathers locations, zones, devices and readings into one simple call. In Phase 11, by contrast, the event bus sends a single event out to many listeners. In short, Facade is a request going in, and Observer is notifications going out.

9. Contrast Observer with **Command**. Command captures **intent to act**. Observer propagates **outcomes**. How can `execute()` publish an event without the command class knowing who persists alerts?

> [!NOTE]
> **_Your Answer_**
>
> Command expresses an intention, such as "stop the pump". Observer, on the other hand, reports the result, such as "stop_pump failed". After a command runs, CommandService publishes CommandFailed on the bus. It doesn't know that AlertPersistenceSubscriber will store an alert, and that's the point: commands only perform the action, while other parts decide how to react.

10. One subscriber throws during `notify` / `publish` and aborts the loop, so later subscribers never run. Why is that a trap? What should the bus do so a failing alert writer does not block metrics (or later WebSocket) subscribers?

> [!NOTE]
> **_Your Answer_**
>
> This is a trap because one broken subscriber can stop every subscriber after it from getting the event, even though they did nothing wrong. For example, if the alert writer crashes, metrics and the future WebSocket would miss the news too. The publisher, like POST /read, might also fail just because of a listener it doesn't even know about. To avoid this, my EventBus catches each subscriber's error, logs it and moves on to the next one. That way the failure stays isolated, and the rest of the system keeps working.
