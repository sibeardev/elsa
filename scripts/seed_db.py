import asyncio
import json
from pathlib import Path

from sqlalchemy import insert
from src.core.database import async_session
from src.models import (
    Activity,
    Building,
    Organization,
    Phone,
    organization_activity,
)

DATA_FILE = Path(__file__).parent.parent / "data/test_data.json"


async def seed():
    async with async_session() as session:
        async with session.begin():
            with open(DATA_FILE, encoding="utf-8") as data_file:
                data = json.load(data_file)

            # Buildings
            for build in data["buildings"]:
                session.add(Building(**build))

            # Organizations
            for organization in data["organizations"]:
                session.add(Organization(**organization))

            # Phones
            for phone in data["phones"]:
                session.add(Phone(**phone))

            # Activities
            for activity in data["activities"]:
                session.add(await Activity.create(session, **activity))

            await session.flush()

            # Organization <-> Activity (association table)
            await session.execute(
                insert(organization_activity),
                data["organization_activity"],
            )


if __name__ == "__main__":
    asyncio.run(seed())
