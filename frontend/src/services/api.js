import axios from "axios";

// 배포 대비 환경변수 적용
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

// 공공데이터 장소 목록 조회
export async function getLocations() {
  try {
    const res = await axios.get(`${API_BASE_URL}/api/locations`);
    return res.data;
  } catch (error) {
    console.error("[API Error] getLocations 실패:", error);
    return []; // 에러 발생 시 빈 배열 반환하여 프론트 터짐 방지
  }
}

// 전체 모임 목록 조회
export async function getMeetings() {
  try {
    const res = await axios.get(`${API_BASE_URL}/api/meetings`);

    if (res.status == 200) {
      console.log("응답 성공: ", res.data);
    } else {
      console.log("응답 실패: ", res.data);
    }

    return res.data;
  } catch (error) {
    console.error("[API Error] getMeetings 실패:", error);
    return [];
  }
}

// 특정 모임 상세 조회
export async function getMeetingById(id) {
  try {
    const res = await axios.get(`${API_BASE_URL}/api/meetings/${id}`);

    if (res.status == 200) {
      console.log("응답 성공: ", res.data);
    }

    return res.data;
  } catch (error) {
    console.error(`[API Error] getMeetingById (${id}) 실패:`, error);
    return null;
  }
}

// 새로운 모임 등록
export async function createMeeting(data) {
  try {
    const res = await axios.post(`${API_BASE_URL}/api/meetings`, data);

    if (res.status == 201) {
      console.log("응답 성공: ", res.data);
    } else {
      console.log("응답 실패: ", res.data);
    }

    return res.data;
  } catch (error) {
    console.error("[API Error] createMeeting 실패:", error);
    throw error;
  }
}

// 모임 수정 (PUT)
export async function updateMeeting(meetingId, updateData) {
  const API_NAME = `updateMeeting(MeetingID: ${meetingId})`;
  try {
    const res = await axios.put(
      `${API_BASE_URL}/api/meetings/${meetingId}`,
      updateData,
    );

    if (res.status === 200) {
      console.log("응답 성공: ", res.data);
      return res.data;
    }

    throw new Error(`Unexpected status code: ${res.status}`);
  } catch (error) {
    console.error(`[API Error] ${API_NAME} 실패:`, error);
    throw error;
  }
}

// 모임 삭제 (DELETE - body에 password 담아 전송)
export async function deleteMeeting(meetingId, passwordData) {
  const API_NAME = `deleteMeeting(MeetingID: ${meetingId})`;
  try {
    // Axios의 delete 메서드는 두 번째 인자로 config가 오므로 데이터 본문은 { data: passwordData } 형태로 넘겨줍니다.
    const res = await axios.delete(
      `${API_BASE_URL}/api/meetings/${meetingId}`,
      {
        data: passwordData,
      },
    );

    // 삭제 성공 응답은 보통 204 No Content 혹은 200 OK입니다.
    if (res.status === 200 || res.status === 204) {
      console.log("응답 성공");
      return true;
    }

    throw new Error(`Unexpected status code: ${res.status}`);
  } catch (error) {
    console.error(`[API Error] ${API_NAME} 실패:`, error);
    throw error;
  }
}

// 모임 참여 신청 (POST)
export async function joinMeeting(meetingId, participantData) {
  const API_NAME = `joinMeeting(MeetingID: ${meetingId})`;
  try {
    const res = await axios.post(
      `${API_BASE_URL}/api/meetings/${meetingId}/join`,
      participantData,
    );

    if (res.status === 201 || res.status === 200) {
      console.log("응답 성공: ", res.data);
      return res.data;
    }

    throw new Error(`Unexpected status code: ${res.status}`);
  } catch (error) {
    console.error("[API Error] joinMeeting 실패:", error);
    throw error;
  }
}

// 모임 참여 취소 (POST)
export async function leaveMeeting(meetingId, leaveData) {
  const API_NAME = `leaveMeeting(MeetingID: ${meetingId})`;
  try {
    const res = await axios.post(
      `${API_BASE_URL}/api/meetings/${meetingId}/leave`,
      leaveData,
    );

    if (res.status === 204) {
      console.log("응답 성공: ", res.data);
      return res.data;
    }

    throw new Error(`Unexpected status code: ${res.status}`);
  } catch (error) {
    console.error("[API Error] leaveMeeting 실패:", error);
    throw error;
  }
}

// 댓글 작성 (POST)
export async function createComment(meetingId, commentData) {
  const API_NAME = `createComment(MeetingID: ${meetingId})`;
  try {
    const res = await axios.post(
      `${API_BASE_URL}/api/meetings/${meetingId}/comments`,
      commentData,
    );

    if (res.status === 201 || res.status === 200) {
      console.log("응답 성공: ", res.data);
      return res.data;
    }

    throw new Error(`Unexpected status code: ${res.status}`);
  } catch (error) {
    logError(API_NAME, error);
    throw error;
  }
}

// 댓글 삭제 (DELETE)
export async function deleteComment(meetingId, commentId, deleteData) {
  const API_NAME = `deleteComment(MeetingID: ${meetingId}, CommentID: ${commentId})`;
  try {
    const res = await axios.delete(
      `${API_BASE_URL}/api/meetings/${meetingId}/comments/${commentId}`,
      {
        data: deleteData,
      },
    );

    // 댓글 삭제 시 성공 응답은 보통 204 No Content 혹은 200 OK입니다.
    if (res.status === 204 || res.status === 200) {
      console.log("응답 성공: ", res.data);
      return res.data;
    }

    throw new Error(`Unexpected status code: ${res.status}`);
  } catch (error) {
    console.error(error);
    throw error;
  }
}

// AI 챗봇 검색 통신 연동
export async function searchChat(query) {
  try {
    const res = await axios.post(`${API_BASE_URL}/api/chat`, {
      message: query,
    });
    return res.data;
  } catch (error) {
    console.error("[API Error] searchChat 실패:", error);
    return {
      reply: "죄송합니다. 챗봇 서버와 통신 중 에러가 발생했습니다.",
      results: [],
    };
  }
}
