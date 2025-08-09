# Examples

이 디렉토리는 call-context-lib의 다양한 사용 예시를 포함하고 있습니다.

## 서브모듈

### 1. executor/
CallContextExecutor를 사용한 A/B 테스트 예시입니다.

- **main.py**: 다양한 executor 타입별 예시
- **Makefile**: 빌드 및 실행 명령어
- **README.md**: 상세한 사용법

```bash
cd executor
make sync-dev
make run
```

### 2. fastapi/
FastAPI와 함께 call-context-lib를 사용하는 예시입니다.

- **main.py**: FastAPI 서버 구현
- **service.py**: 비즈니스 로직
- **experiment_logger.py**: 실험 로깅 콜백
- **llm_module.py**: LLM 호출 함수들

```bash
cd fastapi
make sync-dev
make run-local
```

## 루트 명령어

루트 Makefile에서 모든 서브모듈을 한 번에 관리할 수 있습니다:

```bash
# 모든 서브모듈 목록 확인
make print-submodules

# 모든 서브모듈 의존성 설치
make install

# 모든 서브모듈 린팅
make lint

# 모든 서브모듈 포맷팅
make format

# 모든 서브모듈 테스트
make test
```

## 개발 워크플로우

1. **환경 설정**
   ```bash
   make ci-setup  # CI 환경 설정 (uv 설치 + 의존성)
   ```

2. **개발**
   ```bash
   make format    # 코드 포맷팅
   make lint      # 코드 린팅
   make test      # 테스트 실행
   ```

3. **의존성 관리**
   ```bash
   make lock      # 의존성 잠금
   make sync      # 의존성 동기화
   ```

각 서브모듈은 독립적으로 개발하고 배포할 수 있도록 구성되어 있습니다.