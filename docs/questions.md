# Phase 1 — Skeleton questions

**Pattern / focus:** Course intro and an empty-but-running three-tier skeleton (no GoF pattern this phase).

**Read first:** [Guide 01](../../materials/guides/01-course-patterns-and-skeleton.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste textbook definitions or teaching-example class names as if they were your greenhouse types.
- When a question asks about *this application*, refer to what you built (or what the lab required): layers, routes, and tooling.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.

## A. Pattern

1. In your own words, what is a design pattern? What is it *not*?
A design pattern is a common and reusable idea for solving a software design problem. It is not ready-made code that we can simply copy into a project. It is more like a guide for how we can organize our code.

2. Name the three GoF pattern families. For each family, give one-sentence: what kind of design problem it addresses. Then place **Factory Method** and **Strategy** into the correct family.
The three GoF pattern families is the creational, structural, behavioral. For the creational, it means how we create objects. For the structural, it means how we make the classes/ objects to each other. For the behavioral, it means how objects work and communicate with each other. The **Factory Method** belongs to the creational, while the **Strategy** belongs to the behavioral.

3. A teammate wants to add a pattern “because it is on the course list,” even though the feature is small and unlikely to grow. When should you **skip** a pattern? What risk do you take if you apply one too early?
We should skip a design pattern when the problem is simple and the pattern does not solve a real need. Using a pattern too early can make the code more complicated than necessary, with extra classes that are harder to understand and maintain.

## B. This phase of the application

4. Why does Phase 1 ship a vertical slice that does almost no greenhouse business logic? What does “empty but running” prove that a folder of unimplemented classes would not?
Phase 1 focuses on making the basic system before adding greenhouse logic. “Empty but running” proves that the frontend, backend, and database can run and connect correctly while a folder of unimplemented classes only shows the planned structure, but it does not prove that the application actually works.

5. List the four backend layer packages used in this course (`domain`, `application`, `infrastructure`, `interfaces/api`). For each, state what belongs there and give one example of something that must **not** live in `domain`.
The backend has four layers: domain, application, infrastructure, and interfaces/api. Domain contains the core business rules. Application contains use cases and does the business logic. Infrastructure handles technical details such as the database. Interfaces/api contains the FastAPI routes that communicate with clients. Things such as FastAPI routes or database should not be inside the domain layer because the domain should stay independent from frameworks and external technologies.

6. What does `GET /health` return, and why does it check the database instead of only reporting that the HTTP process is up? Why is API documentation served at `/scalar`, and why is `/docs` disabled?
GET /health returns the status of the API and database. When everything works, it returns {"status":"ok","db":"ok"}, and if the database fails, it reports a degraded status. It checks the database because a running HTTP server does not mean the whole application is healthy. The project uses Scalar at /scalar as its API documentation interface, so the default FastAPI /docs page is disabled to keep one main API documentation interface.

7. Phase 1 requires Alembic (or equivalent) with a **baseline** migration and **no** business tables such as `devices`. Why introduce the migration toolchain before any product schema? What would go wrong if you created tables by hand in Postgres and only added migrations later?
Alembic is introduced early so every database change is tracked from the beginning. The baseline migration gives the project a clean starting point even before business tables exist. If tables were created manually first, the real database could become different from the migration history.

## C. Compare, contrast, and scenarios

8. Explain **dependency direction** in this skeleton: which layers may import which? Why must domain code not import FastAPI, SQLAlchemy, or Pydantic models used as HTTP schemas?
Dependency direction means that outer layers can depend on inner layers, but the core domain should stay independent. The application layer can use the domain, while the API and infrastructure layers handle external details. Domain code should not import FastAPI, SQLAlchemy, or HTTP Pydantic models because business rules should not depend on frameworks or database technologies.

9. The frontend cannot show a healthy badge. A classmate blames “the patterns.” What should you check first (stack, CORS/proxy, health JSON), and why is that a Phase 1 concern rather than a later pattern concern?
I would first check whether the database, backend, and frontend are all running. Then I would check the CORS or proxy configuration and confirm that /health returns the expected JSON. This is a Phase 1 concern because the basic system connection must work before later design patterns and business logic are added.

10. Course completion is at **Phase 12**, not Phase 1. What is still missing after a successful skeleton, and how do later phases add behaviour without rewriting the foundations you laid here?
After Phase 1, the project has the basic structure and connections, but it still does not have the real greenhouse features such as devices, sensors, automation, controls, and business rules. Later phases add these features step by step inside the existing layers. Because the foundation is already working, we can extend the system without rebuilding the whole project from the beginning.
