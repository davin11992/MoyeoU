import os
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import models, schemas

router = APIRouter(
    prefix="/api/locations",
    tags=["Locations"]
)

# 파일 이름 오타 방지를 위해 완벽하게 이름 맞춤
JSON_FILES = [
    "대전_충청권_관광지.json",
    "대전_충청권_레포츠.json",
    "대전_충청권_문화시설.json",
    "대전_충청권_쇼핑.json",
    "대전_충청권_숙박.json",
    "대전_충청권_여행코스.json",
    "대전_충청권_음식점.json",
    "대전_충청권_축제공연행사.json"
]

@router.post("/init-data")
def initialize_locations_data(db: Session = Depends(get_db)):
    """
    JSON 원본 포맷 구조인 'items' 리스트를 정확히 파싱하여 DB에 밀어 넣습니다.
    """
    inserted_count = 0
    skipped_count = 0
    
    for file_name in JSON_FILES:
        # 파일이 존재하는지 패스 검사
        if not os.path.exists(file_name):
            print(f"🚨 [파일 없음 스킵]: {file_name}")
            continue
            
        try:
            # 한글 깨짐 방지를 위해 utf-8 지정 열기
            with open(file_name, "r", encoding="utf-8") as f:
                raw_json = json.load(f)
                
                # 원본 포맷 핵심: 'items' 리스트와 'contentType' 규격을 안전하게 가져옴
                items = raw_json.get("items", [])
                content_type = raw_json.get("contentType", "기타")
                
                print(f"📦 [읽기 성공]: {file_name}에서 {len(items)}개 항목 발견")
                
                for item in items:
                    content_id = str(item.get("contentid"))
                    if not content_id or content_id == "None":
                        continue
                        
                    # 중복 적재 방지 (id 기준 검사)
                    exists = db.query(models.Location).filter(models.Location.id == content_id).first()
                    if exists:
                        skipped_count += 1
                        continue
                    
                    # 💡 원본 JSON 키값을 모델 구조에 1:1 정밀 매핑
                    db_location = models.Location(
                        id=content_id,
                        title=item.get("title", "이름 없음"),
                        content_type=content_type,
                        address=item.get("addr1", ""),
                        map_x=float(item.get("mapx")) if item.get("mapx") and item.get("mapx") != "0" else None,
                        map_y=float(item.get("mapy")) if item.get("mapy") and item.get("mapy") != "0" else None,
                        image_url=item.get("firstimage", ""),
                        source="한국관광공사 국문 관광정보 서비스"
                    )
                    db.add(db_location)
                    inserted_count += 1
                    
        except Exception as file_err:
            print(f"❌ {file_name} 파싱 중 에러 발생: {str(file_err)}")
            continue
                
    db.commit()
    return {
        "status": "success", 
        "message": f"적재 완료! 새롭게 적재된 데이터: {inserted_count}개 (중복 스킵: {skipped_count}개)"
    }


# --- 장소 목록 및 필터 조회 API ---
@router.get("/", response_model=List[schemas.LocationResponse])
def get_locations(
    content_type: Optional[str] = None, 
    keyword: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    query = db.query(models.Location)
    if content_type:
        query = query.filter(models.Location.content_type == content_type)
    if keyword:
        query = query.filter(models.Location.title.contains(keyword))
    return query.limit(1000).all()


# --- 장소 상세 조회 API ---
@router.get("/{id}", response_model=schemas.LocationResponse)
def get_location_detail(id: str, db: Session = Depends(get_db)):
    location = db.query(models.Location).filter(models.Location.id == id).first()
    if not location:
        raise HTTPException(status_code=404, detail="장소를 찾을 수 없습니다.")
    return location