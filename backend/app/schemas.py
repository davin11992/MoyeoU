from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    EmailStr,
)
from typing import Optional, List, Literal
from datetime import date, datetime, time

# 모집 카테고리
Category = Literal[
    "관광",
    "문화생활",
    "운동·산책",
    "맛집",
    "쇼핑",
    "여행",
]

# 모집 상태
MeetingStatus = Literal[
    "OPEN",
    "CLOSED",
    "END",
]

# --- Location (공공데이터 장소) ---
class LocationBase(BaseModel):
    id: str
    title: str
    content_type: str
    address: Optional[str] = None
    map_x: Optional[float] = None
    map_y: Optional[float] = None
    image_url: Optional[str] = None
    source: Optional[str] = None

class LocationResponse(LocationBase):
    class Config:
        from_attributes = True

# 댓글 생성 요청
class CommentCreate(BaseModel):
    nickname: str = Field(..., min_length=1, max_length=20, description="댓글 작성자 닉네임")
    content: str = Field(..., min_length=1, description="댓글 내용")
    password: str = Field(..., min_length=4, description="삭제 시 검증할 비밀번호")
    parent_id: Optional[int] = None
        
# 댓글 응답용
class CommentResponse(BaseModel):
    id: int
    meeting_id: int
    nickname: str
    content: str
    created_at: datetime
    parent_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
        
# 댓글 삭제 요청
class CommentDelete(BaseModel):
    password: str = Field(..., description="생성 시 설정했던 비밀번호")

# 생성·수정·응답에서 공통으로 사용하는 모임 베이스 필드
class MeetingBase(BaseModel):
    title: str = Field(
        min_length=2,
        max_length=100,
    )
    category: Category
    meeting_date: date
    meeting_time: time
    location_name: str = Field(
        min_length=1,
        max_length=150,
    )
    max_participants: int = Field(
        ge=2,
        le=100,
    )
    content: str = Field(
        min_length=1,
        max_length=3000,
    )
    location_id: str | None = Field(
        default=None,
        max_length=100,
    )
  
    map_y: float | None = Field(
        default=None,
        description="모임 장소의 위도 (Y 좌표) - 지정하지 않을 시 Null 허용"
    )
    map_x: float | None = Field(
        default=None,
        description="모임 장소의 경도 (X 좌표) - 지정하지 않을 시 Null 허용"
    )

    @field_validator(
        "title",
        "location_name",
        "content",
    )
    @classmethod
    def remove_surrounding_spaces(
        cls,
        value: str,
    ) -> str:
        value = value.strip()
        if not value:
            raise ValueError("공백만 입력할 수 없습니다.")
        return value
    
# 모임 생성 요청 (MeetingBase 상속으로 자동으로 map_y, map_x 포함됨)
class MeetingCreate(MeetingBase):
    password: str = Field(
        min_length=4,
        max_length=100,
    )
    
    @field_validator("meeting_date")
    @classmethod
    def meeting_date_cannot_be_past(
        cls,
        value: date,
    ) -> date:
        if value < date.today():
            raise ValueError("과거 날짜로 모임을 만들 수 없습니다.")
        return value

# 모임 상세 조회 응답 (댓글 목록 포함)
class MeetingResponse(MeetingBase):
    id: int
    current_participants: int
    status: MeetingStatus
    created_at: datetime
    updated_at: datetime
    comments: List[CommentResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

# 모임 수정 요청
class MeetingUpdate(MeetingBase):
    password: str = Field(
        min_length=4,
        max_length=100,
    )

    @field_validator("meeting_date")
    @classmethod
    def meeting_date_cannot_be_past(
        cls,
        value: date,
    ) -> date:
        if value < date.today():
            raise ValueError("과거 날짜로 모임을 수정할 수 없습니다.")
        return value
    
# 모임 목록 조회 결과 응답
class MeetingListResponse(BaseModel):
    items: List[MeetingResponse] # 일관성을 위해 list -> List로 수정
    total: int
    page: int
    size: int

# 모임 참여 신청 요청
class ParticipantJoin(BaseModel):
    nickname: str = Field(..., min_length=1, max_length=20, description="참여자 닉네임")
    password: str = Field(..., min_length=4, description="참여 취소 시 사용할 비밀번호")
    
# 모임 참여 취소 요청
class ParticipantLeave(BaseModel):
    password: str = Field(..., description="신청 시 입력한 비밀번호")
   
# 참여자 처리 응답용
class ParticipantResponse(BaseModel):
    id: int
    meeting_id: int
    nickname: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
    
 # 모임 비밀번호 확인 요청
class PasswordRequest(BaseModel):
    password: str = Field(
        min_length=4,
        max_length=100,
    )

# 일반적인 성공 메시지 응답용
class MessageResponse(BaseModel):
    message: str