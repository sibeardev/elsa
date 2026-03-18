from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.database import get_session
from core.security import verify_api_key
from models import Activity, Building, Organization
from schemas import OrganizationOut

router = APIRouter(prefix="/organizations", tags=["organizations"])
depends_session = Depends(get_session)


@router.get(
    "/by-building/{building_id}",
    response_model=list[OrganizationOut],
    dependencies=[Depends(verify_api_key)],
    summary="Поиск организаций в здании",
    description="Возвращает организации, находящиеся в указанном здании",
)
async def organizations_by_building(
    building_id: int, session: AsyncSession = depends_session
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
    dependencies=[Depends(verify_api_key)],
    summary="Поиск организаций по виду деятельности",
    description="Возвращает организации, относящиеся к указанному виду деятельности",
)
async def organizations_by_activity(
    activity_id: int, session: AsyncSession = depends_session
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
    dependencies=[Depends(verify_api_key)],
    summary="Поиск организаций по виду деятельности (с дочерними видами)",
    description=(
        "Возвращает организации, относящиеся к указанному виду деятельности "
        "и всем его дочерним видам (глубина до 3 уровней)."
    ),
)
async def organizations_by_activity_tree(
    activity_id: int, session: AsyncSession = depends_session
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
    dependencies=[Depends(verify_api_key)],
    summary="Поиск организаций по названию",
    description="Поиск организаций по части названия. Регистр не учитывается.",
)
async def search_organizations(
    name: str = Query(
        ...,
        min_length=2,
        description="Название организации",
    ),
    limit: int = Query(
        20,
        ge=1,
        le=100,
        description="Ограничение количества результатов",
    ),
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
    "/in-radius",
    response_model=list[OrganizationOut],
    dependencies=[Depends(verify_api_key)],
    summary="Поиск организаций в радиусе от точки",
    description=(
        "Возвращает список организаций, "
        "расположенных в зданиях в заданном радиусе от точки."
    ),
)
async def get_organizations_in_radius(
    lat: float = Query(..., description="Широта"),
    lon: float = Query(..., description="Долгота"),
    radius: float = Query(..., gt=0, description="Радиус в километрах"),
    session: AsyncSession = depends_session,
):
    stmt = (
        select(Organization)
        .join(Building, Organization.building_id == Building.id)
        .where(
            func.ST_DWithin(
                Building.geom,
                func.geography(func.ST_MakePoint(lon, lat)),
                radius * 1000.0,
            )
        )
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
    "/{organization_id}",
    response_model=OrganizationOut,
    dependencies=[Depends(verify_api_key)],
    summary="Получить организацию по идентификатору",
    description="Возвращает информацию об организации (деятельность, здание и телефоны)",
)
async def get_organization_by_id(
    organization_id: int,
    session: AsyncSession = depends_session,
):
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

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    return organization
