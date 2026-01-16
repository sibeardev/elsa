from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.database import get_session
from core.security import api_key_guard
from models import Activity, Organization
from schemas import OrganizationOut

router = APIRouter(prefix="/api/organizations", tags=["organizations"])
depends_session = Depends(get_session)


@router.get(
    "/by-building/{building_id}",
    response_model=list[OrganizationOut],
    dependencies=[Depends(api_key_guard)],
)
async def get_by_building_organizations(
    building_id: int,
    session: AsyncSession = depends_session,
):
    stmt = (
        select(Organization)
        .where(Organization.building_id == building_id)
        .options(
            selectinload(Organization.building),
            selectinload(Organization.phones),
            selectinload(Organization.activities),
        )
    )

    organizations = (await session.scalars(stmt)).all()

    return organizations


@router.get(
    "/by-activity/{activity_id}",
    response_model=list[OrganizationOut],
    dependencies=[Depends(api_key_guard)],
)
async def get_by_activity_organizations(
    activity_id: int,
    session: AsyncSession = depends_session,
):
    stmt = (
        select(Organization)
        .join(Organization.activities)
        .where(Activity.id == activity_id)
        .options(
            selectinload(Organization.building),
            selectinload(Organization.phones),
            selectinload(Organization.activities),
        )
        .distinct()
    )
    organizations = (await session.scalars(stmt)).all()

    return organizations


@router.get(
    "/by-activity-tree/{activity_id}",
    response_model=list[OrganizationOut],
    dependencies=[Depends(api_key_guard)],
)
async def organizations_by_activity_tree(
    activity_id: int,
    session: AsyncSession = depends_session,
):
    activity_ids = await Activity.get_activity_subtree(session, activity_id)
    stmt = (
        select(Organization)
        .where(Organization.activities.any(Activity.id.in_(activity_ids)))
        .options(
            selectinload(Organization.building),
            selectinload(Organization.phones),
            selectinload(Organization.activities),
        )
        .distinct()
    )
    organizations = (await session.scalars(stmt)).all()

    return organizations


@router.get(
    "/search",
    response_model=list[OrganizationOut],
    dependencies=[Depends(api_key_guard)],
)
async def search_organizations(
    name: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = depends_session,
):
    stmt = (
        select(Organization)
        .where(Organization.name.ilike(f"%{name}%"))
        .options(
            selectinload(Organization.building),
            selectinload(Organization.phones),
            selectinload(Organization.activities),
        )
        .limit(limit)
    )

    organizations = (await session.scalars(stmt)).all()

    return organizations


@router.get(
    "/{organization_id}",
    response_model=OrganizationOut,
    dependencies=[Depends(api_key_guard)],
)
async def get_organization(
    organization_id: int,
    session: AsyncSession = depends_session,
):
    try:
        stmt = (
            select(Organization)
            .where(Organization.id == organization_id)
            .options(
                selectinload(Organization.building),
                selectinload(Organization.phones),
                selectinload(Organization.activities),
            )
        )

        organization = (await session.scalars(stmt)).one_or_none()
    except SQLAlchemyError as err:
        raise HTTPException(status_code=500, detail="Database error") from err

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    return organization
