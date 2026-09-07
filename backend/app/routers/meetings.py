from datetime import date, datetime, timedelta, time
from typing import Literal

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
    Body,
)
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Meeting
from app.schemas import (
    Category,
    MeetingCreate,
    MeetingListResponse,
    MeetingResponse,
    MeetingStatus,
    MeetingUpdate,
    MessageResponse,
    PasswordRequest,
)


router = APIRouter(
    prefix="/api/meetings",
    tags=["meetings"],
)


# 1. 모임 생성 API (map_y, map_x 포함 저장)
@router.post(
    "",
    response_model=MeetingResponse,
    status_code=status.HTTP_201_CREATED
)
def create_meeting(
    payload: MeetingCreate,
    db: Session = Depends(get_db),
):
    # payload.model_dump()를 사용하므로 MeetingCreate 스키마에 정의된
    # map_y, map_x가 자동으로 매핑되어 깔끔하게 데이터베이스에 삽입됩니다.
    meeting = Meeting(
        **payload.model_dump(),
        current_participants=1,
        status="OPEN",
    )

    db.add(meeting)
    db.commit()
    db.refresh(meeting)

    return meeting


# 2. 전체 모임 목록 조회 API
@router.get(
    "",
    response_model=MeetingListResponse,
)
def get_meetings(
    category: Category | None = None,
    meeting_date: date | None = None,
    date_filter: Literal[
        "today",
        "week",
    ]
    | None = None,
    meeting_status: MeetingStatus
    | None = Query(
        default=None,
        alias="status",
    ),
    keyword: str
    | None = Query(
        default=None,
        max_length=100,
    ),
    page: int = Query(
        default=1,
        ge=1,
    ),
    size: int = Query(
        default=12,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
):
    query = select(Meeting)

    # 카테고리 필터
    if category is not None:
        query = query.where(
            Meeting.category == category
        )

    # 정확한 날짜 필터
    if meeting_date is not None:
        query = query.where(
            Meeting.meeting_date == meeting_date
        )

    # 오늘 빠른 필터
    elif date_filter == "today":
        query = query.where(
            Meeting.meeting_date == date.today()
        )

    # 이번 주 빠른 필터
    elif date_filter == "week":
        today = date.today()
        last_day = today + timedelta(days=6)

        query = query.where(
            Meeting.meeting_date.between(
                today,
                last_day,
            )
        )

    # 모집 상태 필터
    if meeting_status is not None:
        query = query.where(
            Meeting.status == meeting_status
        )

    # 제목·내용·장소명 키워드 검색
    if keyword is not None:
        cleaned_keyword = keyword.strip()

        if cleaned_keyword:
            keyword_pattern = (
                f"%{cleaned_keyword}%"
            )

            query = query.where(
                or_(
                    Meeting.title.ilike(
                        keyword_pattern
                    ),
                    Meeting.content.ilike(
                        keyword_pattern
                    ),
                    Meeting.location_name.ilike(
                        keyword_pattern
                    ),
                )
            )

    # 페이지네이션 적용 전 전체 개수
    count_query = (
        select(func.count())
        .select_from(query.subquery())
    )

    total = db.scalar(count_query) or 0

    # 가까운 모임부터 정렬
    paginated_query = (
        query
        .order_by(
            Meeting.meeting_date.asc(),
            Meeting.meeting_time.asc(),
            Meeting.id.desc(),
        )
        .offset((page - 1) * size)
        .limit(size)
    )

    meetings = db.scalars(
        paginated_query
    ).all()

    return MeetingListResponse(
        items=meetings,
        total=total,
        page=page,
        size=size,
    )


# 3. 모임 상세 조회 API (응답 스키마에 따라 map_x, map_y 반환)
@router.get(
    "/{meeting_id}",
    response_model=MeetingResponse,
)
def get_meeting_detail(
    meeting_id: int,
    db: Session = Depends(get_db),
):
    meeting = db.get(
        Meeting,
        meeting_id,
    )

    if meeting is None:
        raise HTTPException(
            status_code=404,
            detail="모임을 찾을 수 없습니다.",
        )

    return meeting


# 4. 모임 수정 API (map_y, map_x 필드 정상 반영 보완)
@router.put(
    "/{meeting_id}",
    response_model=MeetingResponse,
)
def update_meeting(
    meeting_id: int,
    payload: MeetingUpdate,
    db: Session = Depends(get_db),
):
    # 모임 존재 여부 확인
    meeting = db.get(
        Meeting,
        meeting_id,
    )

    # 없으면 404 에러 출력
    if meeting is None:
        raise HTTPException(
            status_code=404,
            detail="모임을 찾을 수 없습니다.",
        )

    # 모임 비밀번호 확인
    if meeting.password != payload.password:
        raise HTTPException(
            status_code=403,
            detail="수정 비밀번호가 일치하지 않습니다.",
        )

    # 정원 수 유효성 체크
    if (
        payload.max_participants
        < meeting.current_participants
    ):
        raise HTTPException(
            status_code=409,
            detail=(
                "최대 인원은 현재 인원보다 "
                "작게 설정할 수 없습니다."
            ),
        )

    # 비밀번호를 제외한 수정용 딕셔너리 생성
    # map_y, map_x가 포함되어 있으며 만약 Null(None) 값이 들어와도 그대로 DB에 안전하게 교체
    update_data = payload.model_dump(
        exclude={"password"}
    )

    # 모임 필드 수정 일괄 적용 (map_y, map_x 포함 반영 완료)
    for field_name, value in update_data.items():
        setattr(
            meeting,
            field_name,
            value,
        )

    db.commit()
    db.refresh(meeting)

    return meeting


# 5. 모임 삭제 API
@router.delete(
    "/{meeting_id}",
    response_model=MessageResponse,
)
def delete_meeting(
    meeting_id: int,
    payload: PasswordRequest = Body(...),
    db: Session = Depends(get_db),
):
    meeting = db.get(
        Meeting,
        meeting_id,
    )

    if meeting is None:
        raise HTTPException(
            status_code=404,
            detail="모임을 찾을 수 없습니다.",
        )

    if meeting.password != payload.password:
        raise HTTPException(
            status_code=403,
            detail="삭제 비밀번호가 일치하지 않습니다.",
        )

    db.delete(meeting)
    db.commit()

    return MessageResponse(
        message="모임이 삭제되었습니다."
    )