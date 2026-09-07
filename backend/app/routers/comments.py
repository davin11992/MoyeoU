from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Meeting, Comment
from app.schemas import CommentCreate, CommentResponse, CommentDelete

router = APIRouter(
    prefix="/api/meetings/{meeting_id}/comments",
    tags=["comments"],
)

# 댓글 작성
@router.post("", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    meeting_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
):
    # 대상 모임이 존재하는지 검증
    meeting = db.get(Meeting, meeting_id)
    if meeting is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="모임을 찾을 수 없습니다.",
        )

    db_comment = Comment(
        meeting_id=meeting_id,
        nickname=payload.nickname,
        content=payload.content,
        password=payload.password,
        parent_id=payload.parent_id,
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    
    return db_comment

# 댓글 삭제
@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    meeting_id: int,
    comment_id: int,
    payload: CommentDelete,
    db: Session = Depends(get_db),
):
    # 댓글 조회 및 해당 모임의 댓글이 맞는지 검증
    comment = db.get(Comment, comment_id)
    if comment is None or comment.meeting_id != meeting_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="댓글을 찾을 수 없습니다.",
        )

    # 본인인증 비밀번호 검증
    if comment.password != payload.password:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="비밀번호가 일치하지 않습니다.",
        )

    db.delete(comment)
    db.commit()
    return