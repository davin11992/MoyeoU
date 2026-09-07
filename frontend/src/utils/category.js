export const getMappedCategory = (contentType) => {
  if (
    contentType === "관광지" ||
    contentType === "숙박" ||
    contentType === "여행코스" ||
    contentType === "쇼핑"
  ) {
    return "나들이";
  }
  if (contentType === "문화시설" || contentType === "축제공연행사") {
    return "문화·행사";
  }
  if (contentType === "레포츠") {
    return "운동";
  }
  if (contentType === "음식점") {
    return "식사·카페";
  }
  return "나들이"; // 기본값
};
