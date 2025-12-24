# AI4PKM Orchestrator 테스트 기사

**작성일**: 2025-12-24
**카테고리**: AI & PKM
**출처**: Day 2 학습 실습

---

## 서론

이 문서는 AI4PKM Orchestrator의 동작을 테스트하기 위한 샘플 클리핑 파일입니다. EIC (Enrich Ingested Content) 에이전트가 이 파일을 처리하여 enriched content로 변환하는 과정을 확인합니다.

## Orchestrator란?

Orchestrator는 멀티 에이전트 시스템을 조율하는 핵심 엔진입니다. 다음과 같은 특징이 있습니다:

1. **자동화**: 파일 변경 감지 시 자동으로 에이전트 실행
2. **조율**: 여러 에이전트를 유기적으로 연결
3. **확장성**: 새 에이전트 추가가 쉬움
4. **모니터링**: 통합된 로깅 및 상태 관리

## Poller 시스템

Poller는 외부 소스를 주기적으로 확인하여 새로운 항목을 발견하면 에이전트를 트리거합니다:

- **GobiPoller**: Gobi 앱의 새 노트 가져오기
- **LimitlessPoller**: Limitless 대화 및 노트 동기화
- **AppleNotesPoller**: Apple Notes 동기화

## 워크플로우 예시

웹 클리핑 → Enrichment → 게시물 생성의 3단계 워크플로우:

```
1. 웹 클리퍼로 기사 저장
   vl_ai4pkm_clippings/article.md 생성

2. EIC 에이전트가 자동 실행
   vl_ai4pkm_materials/article_enriched.md 생성

3. CTP 에이전트가 자동 실행
   Publish/article_thread.md 생성
```

## 결론

AI4PKM의 Orchestrator는 강력한 자동화 시스템을 제공합니다. 설정 기반 아키텍처로 코드 수정 없이 새로운 에이전트를 추가할 수 있으며, 이벤트 기반 실행으로 효율적인 워크플로우를 구성할 수 있습니다.

---

**태그**: #AI4PKM #Orchestrator #Automation #PKM
**키워드**: Orchestrator, Poller, Agent, Workflow, Automation
