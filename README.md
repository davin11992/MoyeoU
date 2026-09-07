# 모여유 (MoyeoU)

SSAFY 대전 캠퍼스 학생들을 위한 **AI 기반 익명 번개 모임 커뮤니티** 프론트엔드 MVP입니다.
로그인 없이 익명으로 모임을 등록하고 참여할 수 있습니다.
STARTCAMP AI온보딩 바이브코딩 실습 프로젝트입니다. 

> 학습용 스켈레톤 프로젝트입니다. 백엔드(FastAPI 예정)는 아직 연결되어 있지 않으며, 모든 데이터는 목업입니다.

## 기술 스택

- Vue.js 3 (`<script setup>` Composition API)
- Vite
- Vue Router
- Tailwind CSS

## 설치

```bash
pnpm install
```

## 개발 서버 실행

```bash
pnpm dev
```

실행 후 `http://localhost:5173` 에서 확인할 수 있습니다.

## 폴더 구조

```
src/
  components/   # 재사용 컴포넌트 (AppHeader, MeetingCard, ChatbotWidget 등)
  views/        # 페이지 단위 화면
  router/       # Vue Router 설정
  services/     # API 서비스 레이어 (지금은 목업 반환)
  data/         # 목업 데이터
  assets/       # 전역 스타일(Tailwind)
  App.vue
  main.js
```

## 페이지

| 경로 | 설명 |
| --- | --- |
| `/` | 홈 (히어로 + AI 검색 + 추천 모임/장소) |
| `/meetings` | 모임 찾기 (검색·카테고리 필터) |
| `/meetings/new` | 모임 만들기 |
| `/meetings/:id` | 모임 상세 + 참여 |
| `/locations` | 대전 장소·행사 |

## 백엔드 연결 방법

`src/services/api.js` 의 함수들이 현재 목업 데이터를 반환합니다.
나중에 FastAPI가 준비되면 각 함수 안의 로직을 `fetch` 호출로 교체하면 됩니다.

```js
const BASE_URL = 'http://localhost:8000'
export async function getMeetings() {
  const res = await fetch(`${BASE_URL}/meetings`)
  return res.json()
}
```
