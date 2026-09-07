from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
    UniqueConstraint,
    Numeric,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base

# 1. 공공데이터 장소 테이블
class Location(Base):
    __tablename__ = "locations"

    id = Column(String, primary_key=True, index=True) # 공공데이터 ID
    title = Column(String, nullable=False)
    content_type = Column(String, nullable=False) # 관광지, 행사 등
    address = Column(String, nullable=True)
    map_x = Column(Float, nullable=True)
    map_y = Column(Float, nullable=True)
    image_url = Column(String, nullable=True)
    source = Column(String, nullable=True)

# 번개모임 테이블
class Meeting(Base):
    __tablename__ = "meetings"

    # 잘못된 인원 정보가 들어가는 것을 방지
    __table_args__ = (
        CheckConstraint(
            "max_participants >= 2",
            name="check_max_participants_minimum",
        ),
        CheckConstraint(
            "current_participants >= 1",
            name="check_current_participants_minimum",
        ),
        CheckConstraint(
            "current_participants <= max_participants",
            name="check_participant_capacity",
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
    )
    title = Column(
        String(100),
        nullable=False,
        index=True,
    )
    category = Column(
        String(30),
        nullable=False,
        index=True,
    )
    meeting_date = Column(
        Date,
        nullable=False,
        index=True,
    )
    meeting_time = Column(
        Time,
        nullable=False,
    )
    location_name = Column(
        String(150),
        nullable=False,
        index=True,
    )
    max_participants = Column(
        Integer,
        nullable=False,
        default=4,
    )
    current_participants = Column(
        Integer,
        nullable=False,
        default=1,
    )
    content = Column(
        Text,
        nullable=False,
    )

    # 프로젝트 명세에 따른 수정·삭제 확인용 비밀번호
    # API 응답에는 절대 포함하지 않음
    password = Column(
        String(100),
        nullable=False,
    )

    # OPEN: 모집 중
    # CLOSED: 모집 완료
    # END: 종료
    status = Column(
        String(20),
        nullable=False,
        default="OPEN",
        index=True,
    )

    # 개발자 B가 제공하는 공공데이터 장소 ID
    location_id = Column(
        String(100),
        ForeignKey("locations.id"),
        nullable=True,
        index=True,
    )
    
    map_y = Column(Float, nullable=True)
    map_x = Column(Float, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # location = relationship(
    #     "Location",
    #     back_populates="meetings",
    # )

    participants = relationship(
        "Participant",
        back_populates="meeting",
        cascade="all, delete-orphan",
    )
    
    comments = relationship(
        "Comment",
        back_populates="meeting",
        cascade="all, delete-orphan",
    )

# 모임 참여자 테이블
class Participant(Base):
    __tablename__ = "participants"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
    )
    meeting_id = Column(
        Integer,
        ForeignKey(
            "meetings.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    nickname = Column(
        String(30),
        nullable=False,
    )

    # 참여 취소 확인용 비밀번호
    # API 응답에는 절대 포함하지 않음
    password = Column(
        String(100),
        nullable=False,
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    meeting = relationship(
        "Meeting",
        back_populates="participants",
    )
    
# 댓글 테이블
class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    meeting_id = Column(
        Integer,
        ForeignKey("meetings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    nickname = Column(String(30), nullable=False)
    content = Column(Text, nullable=False)

    # 댓글 삭제용 비밀번호 (평문 저장)
    password = Column(String(100), nullable=False)

    parent_id = Column(Integer, ForeignKey("comments.id", ondelete="CASCADE"), nullable=True)

    created_at = Column(
       DateTime(timezone=True),
       nullable=False,
       server_default=func.now(),
    )

    meeting = relationship("Meeting", back_populates="comments")