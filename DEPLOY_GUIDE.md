# Netlify 배포 가이드

## 배포 URL
https://report-famigo-cosine.netlify.app

## 배포 단계

### 1. GitHub 연동 확인
- 저장소: https://github.com/masigod/report.famigo.life
- 브랜치: master

### 2. Netlify 환경 변수 설정

Netlify 대시보드에서 다음 환경 변수를 설정해야 합니다:

1. Netlify 대시보드 로그인
2. Site settings → Environment variables 이동
3. 다음 변수들 추가:

```
AIRTABLE_API_KEY = (별도 제공된 API 키 입력)
AIRTABLE_BASE_ID = appZcPs57spwdoKQH
AIRTABLE_TABLE_ID = tblxMzwX1wWJKIOhY
```

⚠️ **중요**: API 키는 보안상 별도로 제공됩니다. config.js 파일을 확인하세요.

### 3. 배포 트리거

다음 중 한 가지 방법으로 배포:

1. **자동 배포**: Git push 시 자동 배포
   ```bash
   git add .
   git commit -m "Update"
   git push origin master
   ```

2. **수동 배포**: Netlify 대시보드에서 "Trigger deploy" 버튼 클릭

### 4. 배포 확인

- 배포 로그 확인: Netlify 대시보드 → Deploys
- 사이트 접속: https://report-famigo-cosine.netlify.app

## 문제 해결

### CORS 에러
- netlify.toml에 CORS 헤더가 설정되어 있음
- 그래도 문제가 있다면 Airtable API 직접 호출 대신 Netlify Functions 사용 고려

### API 키 노출 방지
- config.js는 빌드 시 자동 생성됨 (build.sh)
- 절대 API 키를 직접 코드에 포함하지 말 것

### 빌드 실패
- build.sh 파일 실행 권한 확인
- 환경 변수가 올바르게 설정되었는지 확인

## 파일 구조

```
/
├── index.html           # 메인 애플리케이션
├── config.js           # (자동 생성) API 설정
├── netlify.toml        # Netlify 배포 설정
├── build.sh           # 빌드 스크립트
├── .gitignore         # Git 제외 파일
└── README.md          # 프로젝트 문서
```