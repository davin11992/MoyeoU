from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database import get_db
from app.models import Meeting, Participant
from app.schemas import ParticipantJoin, ParticipantLeave, ParticipantResponse

router = APIRouter(
    prefix="/api/meetings",
    tags=["participants"],
)

# backend/app/routers/participants.py 일부

@router.post("/{meeting_id}/join", response_model=ParticipantResponse, status_code=status.HTTP_201_CREATED)
def join_meeting(
    meeting_id: int,
    payload: ParticipantJoin,
    db: Session = Depends(get_db),
):
    # 모임 존재 여부 확인
    meeting = db.get(Meeting, meeting_id)
    if meeting is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="모임을 찾을 수 없습니다.",
        )

    # 정원 초과 여부 확인
    if meeting.current_participants >= meeting.max_participants:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 정원이 초과되어 신청할 수 없습니다.",
        )

    # 동일 닉네임으로 중복 참여 여부 확인 (이메일 대신 닉네임으로 검증 진행)
    existing_participant = db.scalar(
        select(Participant).where(
            Participant.meeting_id == meeting_id,
            Participant.nickname == payload.nickname
        )
    )
    if existing_participant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 이 모임에 참여 신청을 완료한 닉네임입니다.",
        )

    # 참여자 등록 
    participant = Participant(
        meeting_id=meeting_id,
        nickname=payload.nickname,
        password=payload.password, # 취소용 비밀번호
    )
    db.add(participant)

    # 모임 테이블의 현재 인원 증가 및 상태 변경 적용
    meeting.current_participants += 1
    if meeting.current_participants >= meeting.max_participants:
        meeting.status = "CLOSED"

    db.commit()
    db.refresh(participant)

    return participant


# 모임 참여 취소 (Leave)
@router.post("/{meeting_id}/leave", status_code=status.HTTP_204_NO_CONTENT)
def leave_meeting(
    meeting_id: int,
    payload: ParticipantLeave,
    db: Session = Depends(get_db),
):
    # 모임 존재 여부 확인
    meeting = db.get(Meeting, meeting_id)
    if meeting is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="모임을 찾을 수 없습니다.",
        )

    # 참여자 신청 내역 확인 (이메일 기준)
    participant = db.scalar(
        select(Participant).where(
            Participant.meeting_id == meeting_id,
        )
    )
    if participant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="참여 신청 내역이 존재하지 않는 이메일입니다.",
        )

    # 신청 시 설정한 비밀번호 검증
    if participant.password != payload.password:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="비밀번호가 일치하지 않습니다.",
        )

    # 참여자 내역 삭제
    db.delete(participant)

    # 현재 인원 감소 및 상태 원복 (FULL -> OPEN)
    meeting.current_participants = max(1, meeting.current_participants - 1)
    if meeting.current_participants < meeting.max_participants:
        meeting.status = "OPEN"

    db.commit()
    return