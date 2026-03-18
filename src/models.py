from geoalchemy2 import Geography
from sqlalchemy import (
    CheckConstraint,
    Column,
    Float,
    ForeignKey,
    Index,
    String,
    Table,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


organization_activity = Table(
    "organization_activity",
    Base.metadata,
    Column(
        "organization_id",
        ForeignKey("organizations.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "activity_id",
        ForeignKey("activities.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("activities.id", ondelete="SET NULL"),
        nullable=True,
    )
    level: Mapped[int] = mapped_column(nullable=False)
    parent: Mapped[Activity | None] = relationship(remote_side=[id], backref="children")
    organizations: Mapped[list[Organization]] = relationship(
        secondary=organization_activity,
        back_populates="activities",
    )
    __table_args__ = (
        Index("ix_activities_parent_id", "parent_id"),
        CheckConstraint("level BETWEEN 1 AND 3", name="ck_activity_level"),
    )

    @classmethod
    async def create(
        cls, session: AsyncSession, id: int, name: str, parent_id: int | None = None
    ) -> Activity:
        if parent_id is None:
            level = 1
        else:
            parent = await session.get(cls, parent_id)
            if not parent:
                raise ValueError(f"Parent activity {parent_id} not found")
            level = parent.level + 1
            if level > 3:
                raise ValueError("Max activity level is 3")

        return cls(id=id, name=name, parent_id=parent_id, level=level)

    @classmethod
    async def get_activity_subtree(cls, session: AsyncSession, root_id: int) -> list[int]:
        cte = select(cls.id).where(cls.id == root_id).cte(recursive=True)
        child_activities = select(cls.id).where(cls.parent_id == cte.c.id)
        cte = cte.union_all(child_activities)
        result = await session.execute(select(cte.c.id))

        return [row[0] for row in result.all()]


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
    )
    building_id: Mapped[int] = mapped_column(
        ForeignKey("buildings.id"),
        nullable=False,
        index=True,
    )
    building: Mapped[Building] = relationship(back_populates="organizations")
    phones: Mapped[list[Phone]] = relationship(
        back_populates="organization",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    activities: Mapped[list[Activity]] = relationship(
        secondary=organization_activity,
        back_populates="organizations",
    )


class Building(Base):
    __tablename__ = "buildings"

    id: Mapped[int] = mapped_column(primary_key=True)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    geom: Mapped[object] = mapped_column(Geography(geometry_type="POINT", srid=4326))
    organizations: Mapped[list[Organization]] = relationship(back_populates="building")

    __table_args__ = (
        CheckConstraint("latitude BETWEEN -90 AND 90", name="ck_latitude"),
        CheckConstraint("longitude BETWEEN -180 AND 180", name="ck_longitude"),
    )


class Phone(Base):
    __tablename__ = "phones"

    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str] = mapped_column(String(32), nullable=False)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    organization: Mapped[Organization] = relationship(back_populates="phones")
