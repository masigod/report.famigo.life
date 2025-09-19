# Airtable 관리자 테이블 설정 가이드

## 테이블 이름: Administrators

## 필드 구성:

### 1. username (Single line text)
- **설명**: 로그인 아이디
- **필수**: Yes
- **유니크**: Yes
- **예시**: admin, manager01

### 2. password (Single line text)
- **설명**: 비밀번호 (해시 저장)
- **필수**: Yes
- **참고**: 실제 운영시 해시 처리 필요

### 3. fullName (Single line text)
- **설명**: 관리자 실명
- **필수**: Yes
- **예시**: 홍길동

### 4. email (Email)
- **설명**: 이메일 주소
- **필수**: Yes
- **예시**: admin@amorepacific.com

### 5. role (Single select)
- **설명**: 권한 레벨
- **옵션**:
  - admin (최고 관리자)
  - manager (일반 관리자)
  - viewer (읽기 전용)

### 6. isActive (Checkbox)
- **설명**: 계정 활성화 여부
- **기본값**: Checked

### 7. lastLogin (Date and time)
- **설명**: 마지막 로그인 시간
- **형식**: Include time

### 8. createdAt (Created time)
- **설명**: 계정 생성 시간
- **자동 생성**

### 9. department (Single line text)
- **설명**: 부서명
- **예시**: CLT팀, 마케팅팀

## Airtable 설정 방법:

1. Airtable Base에 로그인
2. "Add or import" → "Create blank table" 클릭
3. 테이블명을 "Administrators"로 설정
4. 위 필드들을 순서대로 추가
5. 초기 관리자 계정 생성:
   - username: admin
   - password: admin123 (운영시 변경 필수)
   - fullName: 시스템 관리자
   - email: admin@company.com
   - role: admin
   - isActive: ✓

## 보안 권고사항:

1. **비밀번호 해싱**: 프로덕션에서는 반드시 bcrypt 등으로 해시 처리
2. **HTTPS 필수**: 로그인 정보 전송시 반드시 HTTPS 사용
3. **세션 관리**: JWT 토큰 또는 세션 스토리지 활용
4. **비밀번호 정책**: 최소 8자, 특수문자 포함 등 정책 적용
5. **2FA 고려**: 추후 2단계 인증 도입 검토