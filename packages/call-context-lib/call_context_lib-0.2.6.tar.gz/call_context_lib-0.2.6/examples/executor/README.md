# CallContextExecutor Examples

이 모듈은 CallContextExecutor를 사용한 A/B 테스트 시나리오 예시를 제공합니다.

## 실행 방법

### 환경 설정
```bash
# OpenAI API 키 설정 (선택사항)
export OPENAI_API_KEY=your_api_key_here

# 의존성 설치
make sync-dev
```

### 예시 실행
```bash
make run
```

## 예시 내용

### 1. A/B 테스트 시나리오
- `ABTestLLMSelector`: user_id 해시를 기반으로 LLM 모델을 선택
- 짝수 해시: gpt-3.5-turbo
- 홀수 해시: gpt-4

### 2. Executor 타입별 예시

#### SyncCallContextExecutor
```python
executor = SyncCallContextExecutor()
result = (executor
          .before(lambda ctx: setup_model(ctx))
          .on_completed(lambda ctx: log_success(ctx))
          .execute(ctx, call_llm_function))
```

#### AsyncCallContextExecutor  
```python
executor = AsyncCallContextExecutor()
result = await (executor
               .before_async(lambda ctx: async_setup(ctx))
               .finally_async(lambda ctx: ctx.on_complete())
               .async_execute(ctx, async_llm_function))
```

#### StreamCallContextExecutor
```python
executor = StreamCallContextExecutor()
for chunk in executor.stream_execute(ctx, stream_llm_function):
    process_chunk(chunk)
```

#### InvokeCallContextExecutor
```python
executor = InvokeCallContextExecutor()
result = executor.execute(ctx, llm_function)  # 자동으로 콜백 처리
```

### 3. 실제 LangChain 통합
- `langchain-openai`의 `ChatOpenAI` 사용
- 동기/비동기 invoke 및 stream 지원
- CallContext 메타데이터에 입력/출력 추적
- 실험 결과 콜백 처리

## 주요 특징

- **실제 LLM 호출**: Mock이 아닌 실제 OpenAI API 사용
- **A/B 테스트**: user_id 기반 모델 선택
- **콜백 시스템**: 실험 로깅 및 메트릭 수집
- **에러 핸들링**: 각 단계별 에러 처리
- **컨텍스트 추적**: 입력, 출력, 모델 정보 등 메타데이터 관리

## 개발 명령어

```bash
make help          # 도움말
make sync-dev       # 개발 의존성 설치
make run           # 예시 실행
make lint          # 코드 린팅
make format        # 코드 포맷팅
make test          # 테스트 실행 (테스트 디렉토리가 있는 경우)
```