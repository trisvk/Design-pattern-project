# Phase 3 — Abstract Factory questions

**Pattern / focus:** Abstract Factory.

**Read first:** [Guide 03](../../materials/guides/03-abstract-factory.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example warrior/mage class kits) as if they were your greenhouse classes.
- When a question asks about *this application*, refer to device families, provision, and the unified devices API from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Abstract Factory in plain language. What goes wrong when related products are chosen independently (`if format` for each piece) instead of as a **family**?

> [!NOTE]
> ***Your Answer***
>
> Abstract Factory creates related devices as one family, such as simulation or edge. The Abstract Factory avoids mixing different device families and keeps the code simple.

2. Name the main participants (**abstract factory**, **concrete factory**, **abstract products**, **concrete products**, **client**). How does choosing a factory at the start **commit** the client to one family?

> [!NOTE]
> ***Your Answer***
>
> The abstract factory is FamilyFactory, and the concrete factory is SimulationDeviceFactory and EdgeHardwareFactory. The products are the devices they create. The client uses one selected factory, so all devices come from the same family.

3. When should you use Abstract Factory, and when should you skip it (for example only one product type per request, or mixing siblings is valid)?

> [!NOTE]
> ***Your Answer***
>
> I use Abstract Factory when I need to create a family of related objects together. I skip it when I only need one product type or when mixing products from different families is allowed.

## B. This phase of the application

4. In this lab, what is a **device family**, and what does `create_device_set()` (or your equivalent) return? Why must a simulation kit and an edge kit not mix incompatible siblings?

> [!NOTE]
> ***Your Answer***
>
> A device family is a group of devices that work together, such as simulation or edge devices. create_device_set() returns the four devices in that family. They should not be mixed because each family uses different configurations and protocols.

5. Phase 2 Factory Method creators still exist. How does Abstract Factory **compose** them rather than replace them? What would you lose if you deleted the sensor creators and inlined all construction inside the family factory?

> [!NOTE]
> ***Your Answer***
>
> Abstract factory uses the phase 2 sensor creators to create sensors, instead of replacing them. If we removed the sensor creators, we would lose their separate creation logic and make the family factory more complicated.

6. Why add a `device_family` column on the existing `devices` table (with a default/backfill such as `"simulation"`) instead of a new table per family? What happens to Phase 2 sensor rows if you forget the backfill?

> [!NOTE]
> ***Your Answer***
>
> device_family lets all devices stay in one table while showing which family they belong to. The backfill gives old Phase 2 sensors "simulation" so without it, those old rows could have a missing family value and cause problems.

7. `POST /api/devices/provision` returns a kit (expected size: two sensors and two actuators). `GET /api/devices` can filter by `family` and `role`. Why must the UI be able to filter by family? Why do `/api/sensors` routes from Phase 2 still need to work?

> [!NOTE]
> ***Your Answer***
>
> The UI filters by family so users can view simulation and edge devices seperately. The /api/sensors routes must still work so the phase 2 features are not broken by the new phase 3 changes.

## C. Compare, contrast, and scenarios

8. Draw the contrast in one paragraph: Factory Method vs Abstract Factory. Use the questions “which **one** product?” versus “which product **line**?” and mention that Abstract Factory often **uses** Factory Method–style methods inside.

> [!NOTE]
> ***Your Answer***
>
> Factory method answers “which one product?”, while abstract factory answers “which product line?”. Abstract factory creates a family of related devices and often uses factory method-style methods inside to create each device.

9. A DTO or HTTP handler constructs concrete simulation/edge device types directly, bypassing the family factory. What consistency bug can that reintroduce? How should HTTP stay on the abstract factory / service instead?

> [!NOTE]
> ***Your Answer***
>
> It can mix simulation and edge devices by mistake. The HTTP handler should call the service/family factory, which makes sure all devices come from the selected family.

10. Someone proposes a single “god factory” that creates locations, readings, and devices “because we already have a factory.” Why is that a misuse of Abstract Factory?

> [!NOTE]
> ***Your Answer***
>
> It is a misuse because those objects do not belong to the same product family. A large “god factory” would have too many jobs and make the code harder to understand and maintain.
