# Phase 5 — Adapter questions

**Pattern / focus:** Adapter.

**Read first:** [Guide 05](../../materials/guides/05-adapter.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example a legacy XML calendar client) as if they were your greenhouse classes.
- When a question asks about *this application*, refer to sensor ports, adapters, readings, and `sensor_readings` from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Adapter in plain language. What problem appears when business code speaks a vendor or legacy protocol (odd field names, units, XML, status codes) directly?

> [!NOTE]
> ***Your Answer***
>
> The Adapter pattern changes an existing interface into the interface that the application expects. Without an Adapter, business code is harder to change and mixes translation logic with business rules because it has to understand vendor-specific field names, units, JSON/XML formats, or status codes.

2. Name the participants (**target / port**, **adaptee**, **adapter**, **client**). What does the adapter translate, and what must it **not** decide (business policy)?

> [!NOTE]
> ***Your Answer***
>
> The port is the interface the application expects, the adaptee is the existing incompatible system or data, the adapter translates between them, and the client uses the port. In this lab, adapters translate sensor data into a common Reading. The adapter should not decide business rules, such as when irrigation should start.

3. GoF distinguishes an **object adapter** (composition) from a **class adapter** (inheritance). Which does modern code prefer, and why?

> [!NOTE]
> ***Your Answer***
>
> Modern code usually prefers an object adapter using composition. The adapter holds or uses the adaptee instead of inheriting from it, which gives more flexibility and keeps the vendor code separate from the application.

## B. This phase of the application

4. What is `SensorPort` in this lab, and what normalized value type (for example `Reading`) do adapters return? Why do application services depend on the port rather than on a simulation driver or vendor SDK?

> [!NOTE]
> ***Your Answer***
>
> SensorPort is the common interface that sensor adapters follow. Its read() method returns a normalized Reading containing device_id, value, unit, source, and recorded_at. Application services depend on SensorPort so they do not need to know whether the data comes from simulation, a vendor, or another protocol. This makes it easier to change or add adapters without changing the application service.

5. You need three translations onto the same normalized reading: a simulation adapter, a vendor stub, and an MQTT translator that accepts a payload dict. Why is the different raw shape the point of the exercise? How does `source` (`simulation`, `vendor`, or `mqtt`) show which adapter produced the reading, and why must the MQTT translator not open a broker in this phase? Phase 12 may deliver that same dict on a device HTTP route or through an optional broker — why must this phase still not open either transport?

> [!NOTE]
> ***Your Answer***
>
> The different raw shapes show the main reason for using an Adapter: different sources can provide data in different formats, but the application still needs one common Reading. The source field shows whether the reading came from simulation, vendor, or mqtt, which makes the origin clear after translation. The MQTT adapter only needs to translate the given dictionary and should not open a broker or HTTP connection because transport is not the responsibility of the adapter in this phase. Phase 12 can provide the same payload through HTTP or an optional broker, while the application can still use the same normalized Reading.

6. Readings are **appended** to `sensor_readings` (history grows). Why not keep only the latest value in memory or overwrite a single row, and which later phase consumes this history? Why do a manual read, the simulation sampler, and (later) MQTT share **one** writer of that table? Why does the sampler skip devices with tracking off and MQTT devices, and why do sensor cards poll the latest stored reading until Phase 12?

> [!NOTE]
> ***Your Answer***
>
> Readings are appended so the system keeps a history of sensor values instead of losing older measurements. This history is useful for later features that need past readings and trends. Manual reads, the simulation sampler, and later MQTT should use one ingest/writer path so all readings are stored in the same format and follow the same rules. The sampler skips tracking-off devices because the user disabled automatic tracking, and it skips MQTT devices because MQTT readings will come from their own input path. The frontend polls the latest stored reading so it can show sampler results without creating another data path; Phase 12 will replace this polling with WebSocket updates.

7. `POST /api/sensors/{id}/read` runs an adapter, persists, and returns a DTO. What HTTP status is appropriate when the device is missing versus when the adapter fails? Why must the router never see vendor-shaped types?

> [!NOTE]
> ***Your Answer***
>
> If the device does not exist, the API should return 404 Not Found. If the adapter cannot read or translate the sensor data, it should return 400 Bad Request. The router should only work with the normalized Reading and DTO types, so vendor-specific JSON, XML, or SDK objects do not leak into the API layer.

## C. Compare, contrast, and scenarios

8. Contrast Adapter with **Facade**. Adapter changes the **shape** of an existing interface; Facade simplifies **how to use** a subsystem. Give a greenhouse-shaped example of each (Adapter this phase; Facade in Phase 7).

> [!NOTE]
> ***Your Answer***
>
> An Adapter makes an incompatible sensor source look like the SensorPort that the application already understands. For example, the vendor adapter translates vendor data into a normal Reading. A Facade gives a simple interface for using several parts of a subsystem; for example, a Phase 7 greenhouse facade could provide one simple operation that hides several configuration or device operations.

9. Contrast Adapter with **Decorator**. Both wrap an object. What is different about the interface they present to the client?

> [!NOTE]
> ***Your Answer***
>
> An Adapter changes the interface so the client can use an object that originally had a different interface. A Decorator keeps the same interface but adds extra behavior, such as logging or another feature. In short, Adapter is mainly about translation, while Decorator is about adding behavior.

10. A classmate puts irrigation policy (“if moisture &lt; 0.3 then water”) inside the vendor adapter. Why is that a trap? Where should that decision live instead (later Strategy), and what should stay in the adapter?

> [!NOTE]
> ***Your Answer***
>
> This is a trap because the adapter should only translate the vendor data, not decide what the greenhouse should do. The irrigation decision belongs in the later Strategy pattern, where the application can choose and change different irrigation policies. The adapter should only convert the vendor's raw data into the common Reading, including fields such as value, unit, source, and time.
