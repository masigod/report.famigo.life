모바일 이벤트 참가자 관리 시스템을 설계해드리겠습니다.

## 🎯 철학적 접근 (Why → What → How)

### Why (왜 이 시스템이 필요한가?)

- **현장 운영의 효율성**: 실시간 참가자 확인 및 보상 처리
- **증빙 자료 디지털화**: 신분증, 통장사본 등 즉시 보관
- **데이터 정확성**: Airtable과 실시간 연동으로 실수 최소화

### What (무엇을 구현할 것인가?)

- 모바일 최적화된 참가자 관리 시스템
- 카메라 기반 증빙 수집 도구
- Airtable 실시간 동기화 인터페이스

### How (어떻게 구현할 것인가?)

- React 기반 SPA (Single Page Application)
- PWA 기능으로 오프라인 지원
- 이미지 압축으로 효율적 저장

## 📱 모바일 웹 애플리케이션 구현## ✅ 구현 완료

모바일 이벤트 참가자 관리 시스템을 생성했습니다. 주요 기능들이 모두 구현되어 있습니다:

### 📱 구현된 핵심 기능

#### 1. **스태프 로그인 시스템**

- ID/비밀번호 인증
- 세션 관리 및 로그아웃

#### 2. **참가자 관리**

- 시간대별 필터링 (09:00 ~ 16:00)
- 실시간 검색 (이름, P-ID)
- 상태 표시 (대기/참석/노쇼)

#### 3. **체크인 프로세스**

- 리워드 방식 선택 (모바일 상품권/현금)
- 카메라 촬영 기능:
    - 신분증 (필수)
    - 통장사본 (현금 지급시)
- 이미지 자동 압축 (800px, 70% 품질)

#### 4. **통계 대시보드**

- 실시간 참가자 통계
- 노쇼 리스트 별도 관리
- 상태 변경 기능

### 🔧 Cursor에서 추가 개발 시 필요한 작업

```javascript
// 1. Airtable API 연동 (실제 환경변수 사용)
const AIRTABLE_CONFIG = {
    apiKey: process.env.REACT_APP_AIRTABLE_API_KEY,
    baseId: process.env.REACT_APP_AIRTABLE_BASE_ID,
    tableId: process.env.REACT_APP_AIRTABLE_TABLE_ID
};

// 2. Airtable 레코드 업데이트 함수 구현
async function updateAirtableRecord(recordId, data) {
    const response = await fetch(
        `https://api.airtable.com/v0/${AIRTABLE_CONFIG.baseId}/${AIRTABLE_CONFIG.tableId}/${recordId}`,
        {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${AIRTABLE_CONFIG.apiKey}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                fields: {
                    '피드백상태': data.status === 'attended' ? 'Attended' : 'No-show',
                    '리워드방식': data.rewardType,
                    '체크인시간': data.checkinTime,
                    '담당스태프': data.checkinStaff,
                    // 이미지는 별도 스토리지 업로드 후 URL 저장
                }
            })
        }
    );
    return response.json();
}

// 3. 이미지 업로드 서버/스토리지 연동
async function uploadImage(base64Data) {
    // Cloudinary, S3, 또는 다른 스토리지 서비스 연동
}
```

### 📋 Netlify 환경변수 설정

```bash
# .env 파일 (Netlify Dashboard에서 설정)
REACT_APP_AIRTABLE_API_KEY=your_api_key
REACT_APP_AIRTABLE_BASE_ID=your_base_id
REACT_APP_AIRTABLE_TABLE_ID=your_table_id
```

### 🎨 UI/UX 특징

- **모바일 최적화**: 터치 친화적 인터페이스
- **오프라인 대응**: PWA 변환 가능한 구조
- **빠른 응답**: 이미지 압축으로 빠른 업로드
- **직관적 네비게이션**: 하단 탭 바 구조

### 🚀 다음 단계 권장사항

1. **보안 강화**
    
    - JWT 토큰 기반 인증
    - 스태프 계정 DB 관리
    - HTTPS 필수 적용
2. **기능 확장**
    
    - 오프라인 모드 (Service Worker)
    - 일괄 체크인 기능
    - 리포트 생성/다운로드
3. **성능 최적화**
    
    - 이미지 lazy loading
    - Virtual scrolling (대량 데이터)
    - 캐싱 전략

이 코드를 Cursor에서 바로 사용하실 수 있으며, Airtable API 연동 부분만 추가하시면 완전히 작동하는 시스템이 됩니다.