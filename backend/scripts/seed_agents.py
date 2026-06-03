from app.core.database import SessionLocal
from app.features.agents.seed import seed_agents


def main() -> None:
    with SessionLocal() as db:
        created = seed_agents(db)
    print(f"Seeded {created} agents.")


if __name__ == "__main__":
    main()

