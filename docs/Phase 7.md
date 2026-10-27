# Phase 7 — Facade questions

**Pattern / focus:** Facade.

**Read first:** [Guide 07](../../materials/guides/07-facade.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example a video publish pipeline) as if they were your greenhouse classes.
- When a question asks about _this application_, refer to the location overview, the facade, and the dashboard Overview page from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Facade in plain language. What problem appears when every HTTP handler (or every UI screen) repeats the same multi-step dance across repositories and services?

> [!NOTE]
> **_Your Answer_**
>
> The Facade pattern provides one simple interface to access multiple services. In our greenhouse project, LocationOverviewFacade collects the information needed for the dashboard overview page. Without Facade, the same steps would be repeated in different parts of the application, making the code harder to maintain and update.

2. A facade **orchestrates** collaborators. What should it **not** become (a god object that owns all domain logic)? Where should irrigation policy, sensor translation, and persistence stay instead?

> [!NOTE]
> **_Your Answer_**
>
> A Facade should only coordinate services, not contain all the business logic. In our greenhouse project, irrigation policy stays in the Strategy classes, sensor translation stays in the Adapters, and database operations stay in the Repositories. The Facade simply connects these parts to provide the location overview.

3. When should you use Facade, and when should you skip it (a single repository call is enough; or you actually need to **translate** a mismatched interface)?

> [!NOTE]
> **_Your Answer_**
>
> I use Facade when several repositories and services need to work together to complete a task, like the location overview in our greenhouse project. Skip it when a single repository call is enough. If the problem is translating between different interfaces, we can use the Adapter Pattern instead.

## B. This phase of the application

4. What does `GET /api/locations/{location_id}/overview` return? Name the main pieces of the overview DTO: location, assigned device counts, and `zones` (thresholds, assigned devices, and those devices’ latest readings, including `tracking_enabled` and `sampling_interval_seconds`), plus strategy key and last recommendation. Why may those reading rows come from the sampler or MQTT ingest, not only from `POST /read`? Why is overview scoped by `location_id`?

> [!NOTE]
> **_Your Answer_**
>
> The endpoint returns a complete overview of a selected location. It includes the location details, assigned sensor and actuator counts, zones with their moisture thresholds, assigned devices, and latest readings with tracking_enabled and sampling_interval_seconds. It also includes the saved strategy key and last recommendation. Readings can come from the sampler or MQTT because Phase 5 stores data from different sources in the same database table. The overview uses location_id to show only information belonging to the selected location.

5. Why does this phase **not** require a new business table? What already exists from Phases 2–6 that the facade only **composes**?

> [!NOTE]
> **_Your Answer_**
>
> Phase 7 does not need a new business table because the required data already exists from Phases 2–6. The locations, zones, devices, sensor_readings, and automation_rules tables already store the information. The Facade simply collects and combines this data into one location overview without changing the database structure.

6. The overview HTTP handler should call **only** the facade, not reading/strategy/device repositories directly. Why? How does that help tests and later changes to the query shape?

> [!NOTE]
> **_Your Answer_**
>
> The HTTP handler should only call the Facade because the Facade manages all the required services and repositories. This keeps the handler simple and makes testing easier by allowing us to mock the Facade. If the database queries or overview structure change later, we can update the Facade without changing the HTTP handler.

7. The location selector may use the existing locations list. The Overview cards come from **one** overview fetch, and Refresh repeats that same fetch. Why must the React page not stitch device, reading, and automation calls together to build the same snapshot? How does a new reading or a saved strategy show up on overview without extra frontend glue?

> [!NOTE]
> **_Your Answer_**
>
> The React page only needs one overview API call because the Facade already combines all the required data. Using one request keeps the frontend simple and helps avoid inconsistent information. Clicking Refresh displays the latest readings and saved strategy without needing additional frontend code.

## C. Compare, contrast, and scenarios

8. Contrast Facade with **Adapter**. One makes an existing interface usable; the other makes a subsystem simpler to call. Which is which, and how do both appear in this greenhouse app (Phase 5 vs Phase 7)?

> [!NOTE]
> **_Your Answer_**
>
> The Adapter pattern makes different interfaces work together, while the Facade pattern simplifies access to multiple services. In Phase 5, I used Adapters to convert sensor readings from different sources into a common format. In Phase 7, I used a Facade to combine location, device, reading, and automation data into one API response for the Overview page.

9. This phase mentions **N+1** queries. What is an N+1 problem in an overview that lists latest readings for many devices, and what can the facade (or its repository) do about it without putting SQL in the router?

> [!NOTE]
> **_Your Answer_**
>
>An N+1 problem happens when the application makes one query to get all devices and then another query for each device’s latest reading. With many devices, the database becomes slower. In phase 7, I used the repository to fetch the latest readings for multiple devices in one query. The Facade combines the results, while the HTTP router stays simple and does not contain SQL.

10. A classmate hides every error behind a generic “overview failed,” so a missing location, a DB outage, and a strategy error look the same. Why is that a trap for a facade?

> [!NOTE]
> **_Your Answer_**
>
> It is a trap because the classmate makes different problems look like the same error. A missing location should return 404, while database and strategy errors need different handling. If I hide all errors behind “overview failed,” debugging becomes harder and users cannot understand what went wrong.
