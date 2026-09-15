# Phase 2 — Factory Method questions

**Pattern / focus:** Factory Method.

**Read first:** [Guide 02](../../materials/guides/02-factory-method.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example courier notifiers) as if they were your greenhouse classes.
- When a question asks about *this application*, refer to sensors, creators, the `devices` table, and the sensors API from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Factory Method in plain language. What problem appears when callers scatter `new` / constructors (or a growing `if type == ...`) across the application?

> [!NOTE]
> ***Your Answer***
>
> Factory method keeps object creation in one place. In this application, different creators create different sensor types, such as moisture and light sensors. Without this pattern, many parts of the code may need constructors or many if type == ... checks. This makes the code harder to change when we add new sensor types.

2. Name the main participants of Factory Method (**product**, **concrete product**, **creator**, **concrete creator**, **client**). For each, give one sentence: what it is responsible for.

> [!NOTE]
> ***Your Answer***
>
>  The product is `sensor`, which is the object created by the factory. The concrete products are moisture and light sensors, each with its own type and default configuration. The creator is `sensor creator`, which defines how a sensor is created. The concrete creators are `moisture sensor creator` and `light sensor creator`, which create their specific sensor types. The client is `sensor service`, which uses the correct creator to create a sensor and then saves it through the repository.

3. How do you add a **new product variant** when creators are polymorphic (new class + registry entry) versus when creation lives in one shared `if/elif` function? Why does that difference matter for extension?

> [!NOTE]
> ***Your Answer***
>
> With polymorphic creators, we can add a new sensor type by creating a new creator class and adding it to the registry. With a shared `if/elif` function, we must change the existing function every time we add a new sensor type. The creator approach makes the code easier to extend because each sensor type has its own creation logic.

## B. This phase of the application

4. In this lab, what is the **product** and what are the **concrete creators**? Why must the API handler (or sensor service) go through a creator/registry instead of constructing `MoistureSensor` / `LightSensor` itself?

> [!NOTE]
> ***Your Answer***
>
>The product is `sensor`, and the concrete creators are `moisture sensor creator` and `light sensor creator`. The API uses the creator registry so that sensor creation stays in one place. This also makes it easier to add new sensor types.

5. `POST /api/sensors` accepts a short `type` key such as `"moisture"` or `"light"`, while the stored/returned field is `device_type` (for example `moisture_sensor`). Why are those two fields different? Who decides the stored `device_type` and `default_config`?

> [!NOTE]
> ***Your Answer***
>
> The `type` field is a simple value from the API used to choose the correct creator. The `device_type` is the actual sensor type stored in the database. The selected creator decides the `device_type` and `default_config`.

6. Why is there a single `devices` table with `role="sensor"` instead of a dedicated `sensors` table? What later phase does that choice prepare for?

> [!NOTE]
> ***Your Answer***
>
> The `devices` table can store different kinds of devices, and `role="sensor"` identifies sensor devices. This avoids creating a separate table for every device role. It also prepares the application for later phases with other devices.

7. What should happen when the client posts an **unknown** `type`? Where should that rejection be decided (registry/service vs router constructing a concrete class anyway)?

> [!NOTE]
> ***Your Answer***
>
> An unknown `type` should be rejected with an error, such as HTTP 400. The registry or service should decide this because it knows which sensor types are supported. The router should not create a concrete sensor directly.

## C. Compare, contrast, and scenarios

8. Contrast Factory Method with a **simple factory** (one function full of `if type == ...`). When is the simple factory “good enough,” and why does this phase still want polymorphic creators?

> [!NOTE]
> ***Your Answer***
>
> A simple factory uses one function with `if/elif` checks to create objects. It is good enough when there are only a few simple types. This phase uses polymorphic creators because each sensor type has its own creation logic, and new sensor types can be added more easily.

9. Contrast Factory Method with **Abstract Factory** (Phase 3). Factory Method answers which question? Abstract Factory answers which different question? Why is Factory Method enough for Phase 2 sensors?

> [!NOTE]
> ***Your Answer***
>
> Factory method answers which specific product should be created. Abstract factory maybe answers which family of related products should be created together. Factory method is enough in Phase 2 because we only need to create different types of sensors, not a family of related devices.

10. A classmate puts SQLAlchemy session commits (or FastAPI request parsing) **inside** a concrete creator. Why is that a trap? Where should persistence and HTTP stay instead?

> [!NOTE]
> ***Your Answer***
>
> Putting database or HTTP logic inside a creator gives the creator too many responsibilities. A creator should only create the sensor. Database operations should stay in the repository, and HTTP request handling should stay in the API router.
