# Airtable Administrators 테이블 설정 가이드

## 1단계: 테이블 생성

### 방법 A: CSV 파일로 빠른 생성 (권장)

1. Airtable Base에 로그인
2. 좌측 하단 "Add or import" 클릭
3. "CSV file" 선택
4. `administrators_import.csv` 파일 업로드
5. 테이블 이름을 "Administrators"로 변경
6. Import 클릭

### 방법 B: 수동으로 테이블 생성

1. Airtable Base에 로그인
2. "Add or import" → "Create blank table" 클릭
3. 테이블명을 "Administrators"로 설정

## 2단계: 필드 타입 설정 (CSV import 후 수정 필요)

각 필드를 클릭하고 "Customize field type"을 선택하여 다음과 같이 설정:

### 필수 필드 설정

| 필드명 | Field Type | 설정 |
|--------|------------|------|
| **username** | Single line text | Primary field로 설정 |
| **password** | Single line text | - |
| **fullName** | Single line text | - |
| **email** | Email | Email 형식 검증 활성화 |
| **role** | Single select | Options: admin, manager, viewer |
| **isActive** | Checkbox | 기본값: Checked |
| **lastLogin** | Date | Include time 옵션 활성화 |
| **createdAt** | Created time | 자동 생성 |
| **department** | Single line text | - |
| **notes** | Long text | Rich text formatting 활성화 (선택) |

### role 필드 옵션 설정
1. role 필드 헤더 클릭
2. "Customize field type" 선택
3. "Single select" 선택
4. 다음 옵션 추가:
   - `admin` (색상: 빨강) - 최고 관리자
   - `manager` (색상: 파랑) - 일반 관리자
   - `viewer` (색상: 회색) - 읽기 전용

## 3단계: 테이블 ID 확인

1. Airtable에서 Administrators 테이블 열기
2. 브라우저 URL 확인:
   ```
   https://airtable.com/appXXXXXXXXXXXX/tblYYYYYYYYYYYY/viwZZZZZZZZZZZZ
   ```
3. `tblYYYYYYYYYYYY` 부분이 테이블 ID

## 4단계: login.html 파일 수정

```javascript
// login.html 파일에서 이 부분을 찾아서 수정
const ADMIN_TABLE_ID = 'YOUR_ADMIN_TABLE_ID'; // 여기에 실제 테이블 ID 입력

// 예시:
const ADMIN_TABLE_ID = 'tblABC123DEF456';
```

## 5단계: 초기 비밀번호 변경

⚠️ **중요**: 운영 환경에서는 반드시 초기 비밀번호를 변경하세요!

1. Airtable에서 직접 password 필드 수정
2. 강력한 비밀번호 사용:
   - 최소 8자 이상
   - 대소문자 포함
   - 숫자 포함
   - 특수문자 포함

## 6단계: 권한별 기능

### admin (최고 관리자)
- 모든 데이터 조회/수정/삭제 가능
- 사용자 관리 가능
- 시스템 설정 변경 가능

### manager (일반 관리자)
- 모든 데이터 조회/수정 가능
- 사용자 관리 불가
- 시스템 설정 변경 불가

### viewer (읽기 전용)
- 데이터 조회만 가능
- 수정/삭제 불가
- 다운로드/내보내기 가능

## 7단계: 보안 설정 확인

### Airtable API 권한
1. Airtable Account → API → Personal access tokens
2. 토큰의 Scopes 확인:
   - `data.records:read` - 필수
   - `data.records:write` - 필수
3. Base access에서 해당 Base 선택

### CORS 설정 (Netlify)
netlify.toml 파일에 이미 설정됨:
```toml
[[headers]]
  for = "/*"
  [headers.values]
    Access-Control-Allow-Origin = "*"
```

## 문제 해결

### 로그인이 안 되는 경우
1. 테이블 ID가 올바른지 확인
2. API 키가 올바른지 확인
3. username과 password 대소문자 확인
4. isActive 필드가 체크되어 있는지 확인

### "Failed to authenticate" 오류
1. Airtable API 키 권한 확인
2. Administrators 테이블에 접근 권한 있는지 확인
3. 네트워크 연결 확인

### 세션이 자주 끊기는 경우
- 현재 8시간으로 설정됨
- login.html에서 수정 가능:
```javascript
expires: Date.now() + (8 * 60 * 60 * 1000) // 8시간
```

## 추가 보안 권고사항

1. **프로덕션 배포 전 필수사항**:
   - 모든 초기 비밀번호 변경
   - HTTPS 사용 확인
   - API 키 환경변수로 관리

2. **향후 개선사항**:
   - 비밀번호 해싱 구현 (bcrypt)
   - 2단계 인증 (2FA) 추가
   - 로그인 시도 제한
   - 비밀번호 정책 강제
   - 세션 타임아웃 경고