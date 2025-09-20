# CLT 현장 출석 및 이미지 저장 테이블 스키마

## 1. Administrators 테이블 수정 사항
기존 테이블에 추가 필드:
- **userType** (Single Select): "admin", "manager", "staff"
- staff 타입 사용자는 모바일 페이지로 자동 리다이렉트

## 2. AttendanceImages 테이블 (새로 생성)

### 테이블명: AttendanceImages

### 필드 구성:

| 필드명 | Type | 설명 | 필수 |
|--------|------|------|------|
| **participantID** | Number | 참가자 ID (기본 테이블 연결) | ✓ |
| **participantName** | Single line text | 참가자 이름 | ✓ |
| **checkinTime** | Date and time | 체크인 시간 | ✓ |
| **attendanceStatus** | Single select | "Attended", "No-show", "Pending" | ✓ |
| **rewardType** | Single select | "MobileVoucher", "Cash", "None" | ✓ |
| **idCardImage** | Attachment | 신분증 이미지 | ✓ |
| **bankbookImage** | Attachment | 통장사본 이미지 (현금 지급시) | |
| **staffName** | Single line text | 담당 스태프 이름 | ✓ |
| **staffID** | Single line text | 스태프 로그인 ID | ✓ |
| **checkDate** | Date | 체크 날짜 (9/22 형식) | ✓ |
| **checkTime** | Single line text | 체크 시간대 (13:00 등) | ✓ |
| **notes** | Long text | 특이사항 | |
| **createdAt** | Created time | 레코드 생성 시간 | Auto |
| **modifiedAt** | Last modified time | 최종 수정 시간 | Auto |

### 상태 옵션 설정

#### attendanceStatus:
- Pending (대기) - 회색
- Attended (출석) - 초록색
- No-show (미참석) - 빨간색

#### rewardType:
- MobileVoucher (모바일 상품권) - 파란색
- Cash (현금) - 초록색
- None (없음) - 회색

## 3. 메인 참가자 테이블 연동 필드 추가

기존 참가자 테이블(tblxMzwX1wWJKIOhY)에 추가:

| 필드명 | Type | 설명 |
|--------|------|------|
| **attendanceStatus** | Single select | "Pending", "Attended", "No-show" |
| **checkinTime** | Date and time | 실제 체크인 시간 |
| **rewardType** | Single select | "MobileVoucher", "Cash", "None" |
| **checkinStaff** | Single line text | 체크인 담당 스태프 |
| **hasIDCard** | Checkbox | 신분증 이미지 보유 여부 |
| **hasBankbook** | Checkbox | 통장사본 이미지 보유 여부 |

## 4. Airtable 설정 순서

1. **AttendanceImages 테이블 생성**
   - Base에서 "Add or import" → "Create blank table"
   - 테이블명: AttendanceImages
   - 위 필드들 순서대로 추가

2. **Administrators 테이블 수정**
   - userType 필드 추가
   - staff 옵션 추가

3. **메인 참가자 테이블 수정**
   - 출석 관련 필드 추가
   - 상태 옵션 설정

## 5. 권한 설정

### Staff 사용자 권한:
- AttendanceImages: Create, Read, Update
- 메인 참가자 테이블: Read, Update (attendanceStatus, checkinTime 등만)
- Administrators: Read (본인 정보만)

### 보안 고려사항:
- 이미지는 Airtable Attachment로 저장 (자동 CDN 제공)
- 최대 이미지 크기: 5MB
- 자동 압축: 클라이언트에서 800px로 리사이즈
- EXIF 데이터 제거 필요

## 6. API 연동 예시

```javascript
// 출석 체크 및 이미지 업로드
const checkInParticipant = async (participantId, imageData) => {
  // 1. AttendanceImages 테이블에 레코드 생성
  const attendanceRecord = {
    participantID: participantId,
    participantName: participantName,
    checkinTime: new Date().toISOString(),
    attendanceStatus: 'Attended',
    rewardType: selectedRewardType,
    idCardImage: [{url: imageData.idCard}],
    bankbookImage: rewardType === 'Cash' ? [{url: imageData.bankbook}] : null,
    staffName: currentStaff.name,
    staffID: currentStaff.id
  };

  // 2. 메인 테이블 업데이트
  const updateMainTable = {
    attendanceStatus: 'Attended',
    checkinTime: new Date().toISOString(),
    rewardType: selectedRewardType,
    checkinStaff: currentStaff.name,
    hasIDCard: true,
    hasBankbook: rewardType === 'Cash'
  };
};
```