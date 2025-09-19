# Airtable 필드 설정 가이드

## status 필드 설정 (Single Select)

### 옵션 1: 한글 옵션 사용
Airtable에서 다음 옵션을 추가하세요:
- 대기
- 전송
- 확정
- 수정요청
- 취소
- 중복

### 옵션 2: 영어 옵션 사용 (권장)
만약 한글이 문제가 된다면:
- Pending (대기)
- Sent (전송)
- Confirmed (확정)
- Requested (수정요청)
- Cancelled (취소)
- Duplicate (중복)

### 옵션 3: Text 필드로 변경
1. status 필드 타입을 "Single line text"로 변경
2. 모든 값 자유롭게 입력 가능

## 설정 방법:
1. Airtable 베이스 열기
2. status 열 헤더 클릭
3. "Customize field type" 클릭
4. Single Select의 경우 옵션 추가
5. 또는 "Single line text"로 변경

## 확인 방법:
- 웹 페이지에서 피드백 상태 변경 시 저장되는지 확인
- 콘솔 에러가 사라지는지 확인