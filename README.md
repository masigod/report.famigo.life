# 아모레퍼시픽 파운데이션 CLT 통합 관리 시스템

## 설정 방법

### 1. 로컬 환경 설정

1. `config.js` 파일 생성:
   ```javascript
   const AIRTABLE_CONFIG = {
       API_KEY: 'your_airtable_api_key_here',
       BASE_ID: 'appZcPs57spwdoKQH',
       TABLE_ID: 'tblxMzwX1wWJKIOhY'
   };
   ```

2. API 키 발급:
   - [Airtable](https://airtable.com/account) 계정 설정에서 Personal Access Token 생성
   - `config.js` 파일에 API 키 입력

### 2. 배포 환경 설정 (Netlify)

Netlify에 배포할 경우:

1. Build 설정에서 환경 변수 추가
2. `config.js` 파일을 빌드 시 동적으로 생성하도록 설정

### 보안 주의사항

- **절대로 API 키를 Git에 커밋하지 마세요**
- `config.js` 파일은 `.gitignore`에 포함되어 있습니다
- 배포 시 환경 변수를 사용하세요

### 기능

- Airtable 데이터베이스와 실시간 연동
- 참가자 정보 CRUD 작업
- 요청/확정 날짜 관리
- 피드백 상태 추적
- CSV 내보내기

### 필드 매핑

| Airtable 필드 | 시스템 필드 |
|--------------|-----------|
| ID | ID |
| name | 이름 |
| setDate | 날짜 |
| setTime | 시간 |
| skinColor | 타겟 |
| skinTone | 톤 |
| phone | 전화번호 |
| email | 이메일 |
| reserveStatus | 예비여부 |
| P-ID | P-ID |
| status | 피드백상태 |
| requestDate | 요청일자 |
| confirmedDate | 확정일자 |
| desc | 비고 |