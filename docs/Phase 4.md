# Phase 4 — Builder questions

**Pattern / focus:** Builder.

**Read first:** [Guide 04](../../materials/guides/04-builder.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example ramen orders) as if they were your greenhouse classes.
- When a question asks about _this application_, refer to locations, zones, `location_id`, and the configuration wizard from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Builder in plain language. Why does construction of a complex object need **stepwise assembly** and **validation at the end** (`build()`), instead of a telescoping constructor or a half-filled dict written straight to the database?

> [!NOTE]
> **_Your Answer_**
>
>The Builder pattern creates a complex object step by step, making the process easier to manage. The build() method checks that all required data is complete and valid before creating the final object so it prevents incomplete or invalid data from being saved to the database.

2. Name the main participants (**product**, **builder**, **optional director**, **client**). Until `build()` succeeds, is the intermediate object a finished domain product? Why does that distinction matter?

> [!NOTE]
> **_Your Answer_**
>
> The main participants are the product, builder, optional director, and client. Before build() succeeds, the object is not a finished domain product because it may still be incomplete or invalid. This ensures that only valid and complete objects are used or saved.

3. List at least three kinds of invalid configuration a location/zone `build()` should reject in **this** lab (name, zones, moisture thresholds). Why must those rules live in the **domain** builder, not only in the HTTP layer?

> [!NOTE]
> **_Your Answer_**
>
> The builder should reject an empty location name, no zones, and invalid moisture thresholds. These rules belong in the domain builder so the configuration stays valid no matter where it comes from, not only from the HTTP API.

## B. This phase of the application

4. What aggregate does the builder produce (location plus zones)? Why does this course use **`location_id`** (and never `greenhouse_id`) as the name for that scope?

> [!NOTE]
> **_Your Answer_**
>
> The builder produces a LocationConfig aggregate containing one location and its zones. The course uses location_id because location is the main scope of the configuration, keeping the naming consistent and avoiding the old greenhouse_id name.

5. Describe the path from API request to persistence: DTO → builder steps → `build()` → repository. What must **not** be persisted if `build()` raises `ConfigurationError` (or equivalent)? Why does assigning a device wait until the zone row exists, and why does the client send only `zone_id`?

> [!NOTE]   
> **_Your Answer_**
>
> The API request first comes into a DTO, which contains the location name and zone information from the client. The service then passes this data step by step to the builder, using methods such as with_location_name() and add_zone(). After all information is added, build() validates the complete configuration, such as checking the name, zones, and moisture thresholds. If everything is valid, it creates a complete LocationConfig. Finally, the repository saves the location and its zones to the database. The request goes from the DTO -> builder steps -> build() -> repository. If build() fails, nothing should be saved. Device assignment waits until the zone has an ID, and the client sends only zone_id because the backend can get the correct location_id from that zone.

6. Saving a location and its zones must be **one transaction**. What goes wrong if the location row commits and a later zone insert fails? How does that relate to “no half-built aggregates in the database”?

> [!NOTE]
> **_Your Answer_**
>
>Saving the location and its zones in one transaction makes sure they are saved together. If the location is committed but a zone insert fails, the database would contain an incomplete location. Using one transaction allows everything to be rolled back, so no half-built aggregate is stored in the database.

7. The configuration wizard UI collects fields in steps. How does that UI map to Builder without turning React (or the HTTP handler) into the place that owns domain validation?

> [!NOTE]
> **_Your Answer_**
>
> The configuration wizard collects the location name, zones, moisture thresholds, and schedule step by step in React. React can check simple input problems to give quick feedback to the user. After submission, the API sends the data to the Builder, which performs the real domain validation in build(). This keeps important rules, such as requiring at least one zone and valid thresholds, inside the domain instead of React or the HTTP handler.

## C. Compare, contrast, and scenarios

8. Contrast Builder with Factory Method and with Abstract Factory. Which pattern answers “which type?”, which answers “which matching kit?”, and which answers “how do we assemble one **valid whole** in steps?”

> [!NOTE]
> **_Your Answer_**
>
> Factory method answers “which type should be created?”. Abstract factory answers “which matching family or kit of objects should be created together?”. Builder answers “how do we assemble one valid whole step by step?”. In this lab, Builder creates the complete LocationConfig by adding the location name and zones, then validating everything with build().

9. Fluent method chaining (`builder.add_zone(...).build()`) is a coding style. Why is a fluent interface **not** the same thing as the Builder pattern?

> [!NOTE]
> **_Your Answer_**
>
> A fluent interface is only a coding style that allows methods to be chained, such as add_zone(...).build(). The Builder pattern is about constructing a complex object step by step and validating it before creating the final product. A Builder can use fluent chaining, but it does not have to.

10. A classmate validates thresholds only in FastAPI / Pydantic and leaves `build()` empty. Another mutates builder fields after `build()` while treating the product as immutable. Explain why each is a trap.

> [!NOTE]
> **_Your Answer_**
>
> Validating thresholds only in FastAPI/Pydantic is a trap because other parts of the application could create invalid configurations without using the API. The important rules should stay in build() so every LocationConfig is validated. Mutating builder fields after build() is also risky because the finished product should remain immutable and valid; later builder changes should not change the product that was already created.
