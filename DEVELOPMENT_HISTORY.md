# Amore Pacific Foundation Consumer Test 2025 - Development History

## 프로젝트 개요
- **프로젝트명**: Amore Pacific Foundation Consumer Test 2025 Dashboard
- **개발 기간**: 2025년 9월 27일
- **총 참가자**: 133명
- **GitHub Repository**: https://github.com/masigod/report.famigo.life

## 주요 파일 구조
```
/Users/owlers_dylan/APCLT/
├── makeup-test-dashboard.html (최종 대시보드 - 외부 공유용)
├── makeuptest_AP_Bueatylink_20250927.xlsx (133명 참가자 데이터)
├── excel_analysis.json (분석된 데이터)
├── complete_participant_image_mapping.json (이미지 매핑)
└── images_organized_by_aid/ (A-ID로 정리된 이미지들)
    ├── A101_face_photo.jpg
    ├── A101_skin_brightness.png
    ├── A101_hair.png
    ├── A101_eye_color.png
    └── ... (각 참가자별 4종류 이미지)
```

## 개발 진행 내역

### 1단계: 초기 데이터 문제 해결
- **문제**: 132명으로 표시되던 데이터가 실제로는 133명 (A216 누락)
- **해결**:
  - A216 (GUAYASAMIN URQUIZO MARIA CRISTINA) 추가
  - Excel 파일 업데이트 (Downloads → 프로젝트 루트로 복사)
  - 데이터 임베딩 방식 수정

### 2단계: 이미지 처리
- **초기 시도**: Excel 내부 이미지 추출 (실패 - ZIP 구조 복잡)
- **해결**: images_organized_by_aid 폴더 사용
- **이미지 종류**:
  - face_photo (133개)
  - skin_brightness (132개)
  - hair (133개)
  - eye_color (123개)

### 3단계: 대시보드 개발 진화

#### v1: 기본 테이블 대시보드
- DataTables 라이브러리 사용
- 검색 및 정렬 기능
- 모달 팝업으로 상세 정보 표시

#### v2: 시각적 개선
- 피부 밝기를 썸네일 이미지로 표시
- 피부 톤을 색상 배경으로 표시 (Warm=주황, Cool=파랑, Neutral=회색, Olive=올리브)
- Base Products 사용 통계 차트 추가

#### v3: 모바일 반응형
- 모바일에서 통계를 통합 리스트로 표시
- 반응형 테이블 적용
- 화면 크기별 우선순위 컬럼 설정

#### v4: 메이크업 시각화 (최종)
- 얼굴 일러스트에 화장품 적용 부위 표시
- 피부 밝기(1-7)에 따른 얼굴 배경색 변경
- 동적 글로우 애니메이션 효과
- 제품별 그라데이션 색상 적용

### 4단계: 최종 기능 구현

#### 통계 표시
- 총 참가자: 133명
- 평균 나이
- 매일 화장하는 사용자
- 쿠션 파운데이션 사용자
- 매일 선크림 사용자
- 사용 제품 종류 수

#### Reference Images 값 표시
- Skin Brightness: 밝기 값 (1-7)
- Hair: 톤 값 (Warm/Cool/Neutral/Olive)
- Eye Color: 민족 그룹

#### 메이크업 적용 시각화
```javascript
제품 → 적용 부위 매핑:
- Foundation/BB/CC → 이마
- Primer/Base → 관자놀이
- Concealer → 눈 주변, 다크서클
- Cushion → 볼 (쿠션 효과)
- Blush → 볼 (블러쉬 효과)
- Highlighter → 코 브릿지
- Contour → 턱선, 턱
- Lip products → 입술 (종류별 색상)
  * Lipstick: 진한 빨강
  * Tint: 연한 핑크
  * Gloss: 투명 광택
```

#### 피부 밝기별 색상 매핑
```javascript
brightness_to_color = {
    '1': '#fde4d0',  // Very fair
    '2': '#fad4b8',  // Fair
    '3': '#f5c09f',  // Light
    '4': '#e8a574',  // Medium
    '5': '#d4895a',  // Medium-dark
    '6': '#b97346',  // Dark
    '7': '#9a5d38'   // Deep
}
```

## 주요 기술 스택
- **Frontend**: HTML5, Bootstrap 5, jQuery
- **Charts**: Chart.js (도넛 차트)
- **Table**: DataTables with Responsive plugin
- **Backend Processing**: Python (pandas)
- **Version Control**: Git/GitHub

## 데이터 구조

### 참가자 데이터 필드
- A-ID, P-ID (식별자)
- 이름, 성별, 국적, 출생년도, 민족
- 피부 밝기 (밝기판정: 1-7)
- 피부 톤 (톤: Warm/Cool/Neutral/Olive)
- 화장품 사용 습관
- 선호 메이크업 스타일
- Base products 사용 목록
- Lip products 사용 목록

### Base Products 상위 사용 제품
1. Concealer: 78명
2. Cushion foundation: 66명
3. Primer/Makeup base: 57명
4. Liquid foundation: 52명
5. BB/CC cream: 36명
6. Tinted moisturizer: 36명

## 알려진 이슈 및 해결
1. **데이터 표시 안됨**: JSON 임베딩 시 정규식 매칭 문제 → 완전 재작성으로 해결
2. **모바일 테이블 깨짐**: DataTables Responsive 플러그인 적용
3. **이미지 매핑 오류**: A-ID 기준으로 재매핑
4. **Face photo 크기**: 650px max-width로 확대

## 다음 개발 시 참고사항

### 필수 확인 사항
1. Excel 파일이 133명인지 확인 (A216 포함 여부)
2. images_organized_by_aid 폴더 존재 여부
3. 데이터 임베딩 시 정규식 패턴 주의

### 개선 가능 영역
1. 실시간 피부색 추출 (현재는 밝기 값 기준)
2. 메이크업 전/후 비교 뷰
3. 통계 대시보드 분리
4. 참가자별 리포트 생성 기능
5. 데이터 내보내기 (Excel/PDF)

### 주요 Python 스크립트
- `create_dynamic_makeup_dashboard.py`: 최종 대시보드 생성
- `update_all_images.py`: 이미지 매핑 업데이트
- `fix_133_participants.py`: 133명 데이터 확인

### Git 커밋 히스토리 주요 포인트
- A216 추가 커밋
- 모바일 반응형 적용
- 메이크업 시각화 구현
- 동적 효과 추가

## 배포 정보
- **URL**: makeup-test-dashboard.html (외부 공유용)
- **GitHub Pages**: https://masigod.github.io/report.famigo.life/makeup-test-dashboard.html
- **마지막 푸시**: 2025년 9월 27일

## 연락처
- GitHub Issues: https://github.com/masigod/report.famigo.life/issues

---
*이 문서를 기반으로 다음 개발을 이어갈 수 있습니다.*