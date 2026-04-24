# Context Measurement (토큰 측정 baseline)

> "스키마 구조를 바꿨더니 좋아졌다" 를 **수치로 판단**하기 위한 최소 측정 프로토콜.
> 측정 없이 구조를 바꾸면 개선/퇴보 여부를 확신할 수 없다.
> 이 문서는 측정 **절차**만 정의한다 — 수치 자체는 `measurement-runs/` 에 기록한다 (있다면).

---

## 🎯 왜 측정이 필요한가

- 리팩토링 결정(`wiki-relations.md` 분할, `intent-routing.yaml` 추출 등)의 효과를 사후 검증.
- 새 엔티티 문서를 추가했을 때 기존 라우팅이 **평균 토큰을 얼마나 늘렸는지** 추적.
- 스키마 결손 후보(의미검색 폴백 발생)의 빈도 추이 관찰.

---

## 1️⃣ 측정 대상 (Metrics)

```yaml
Metric:
  # --- 입력 측 ---
  - name: context_tokens_read
    desc: "질문 1건 처리에 AI 가 읽은 모든 파일의 합 토큰"
    unit: tokens

  - name: docs_read_count
    desc: "읽은 파일 개수 (Intent Routing 의 max_docs_to_read=4 예산 대비)"
    unit: count

  - name: walk_depth_used
    desc: "그래프 워크 실제 수행 홉 수 (max_walk_depth=2 대비)"
    unit: count

  # --- 출력 측 ---
  - name: answer_correct
    desc: "답이 맞았는가 (사람 평가 — yes/no/partial)"
    unit: enum[yes, no, partial]

  - name: intent_classified_correctly
    desc: "Intent 분류가 맞았는가 (샘플 정답과 비교)"
    unit: bool

  - name: fallback_triggered
    desc: "의미검색 폴백이 발동됐는가 (스키마 결손 신호)"
    unit: bool

  # --- 비용 측 ---
  - name: total_io_tokens
    desc: "입력 + 출력 합 (비용 추정)"
    unit: tokens
```

---

## 2️⃣ 샘플 질문 세트 (Golden Set)

> 측정의 입력. 각 Intent 당 최소 2개 이상의 실제/가상 질문을 준비. 정답(Intent + Entry Point + 예상 답) 을 고정.

```yaml
SampleQuestion:
  - id: q001
    intent: SingleRuleCheck
    question: "안전지역에서 Fireball 쓸 수 있어?"
    expected_entry_point: { doc: wiki-skill-schema.md, section: "§3" }
    expected_answer_signal: "allowed=false, reason=SafeZoneRestriction"

  - id: q002
    intent: ChangeImpact
    question: "state.burn 의 baseDuration 을 5초 → 8초로 바꾸면 영향받는 것?"
    expected_entry_point: { doc: wiki-relations.md, section: "§4 허브 + relations/state.md" }
    expected_answer_signal: "Fireball/Meteor 등 burn 생성 Skill 목록 + maxDuration invariant 검사"

  # ... 각 Intent 당 2개 이상, 총 14개 이상 권장
```

권장 크기: **Intent 당 2~3개, 전체 15~20개**. 많을수록 좋지만 유지비가 든다.

---

## 3️⃣ 측정 실행 절차

```yaml
Procedure:
  step1_baseline:
    when: "리팩토링 직전"
    what: "현재 구조로 Golden Set 전체 실행"
    record: "measurement-runs/<date>-baseline.yaml"

  step2_apply_change:
    what: "리팩토링 1건 적용 (예: intent-routing.yaml 추출)"

  step3_remeasure:
    what: "같은 Golden Set 재실행"
    record: "measurement-runs/<date>-after-<change>.yaml"

  step4_diff:
    what: "baseline 대비 메트릭 변화 비교"
    decision_rule:
      - "context_tokens_read 가 유의미하게 줄었고 answer_correct 가 유지/상승 → 채택"
      - "answer_correct 가 하락 → 롤백 또는 원인 조사"
      - "fallback_triggered 가 새로 나타남 → 스키마 축에 편입할 개념 검토"
```

---

## 4️⃣ 결과 기록 포맷

```yaml
MeasurementRun:
  run_id: string                    # "2026-04-24-baseline"
  commit: string                    # 문서 커밋 해시 (있다면)
  golden_set_version: string

  results:
    - question_id: q001
      intent_classified: SingleRuleCheck
      intent_correct: true
      docs_read: [wiki-skill-schema.md, wiki-entity-zone.md]
      context_tokens_read: 1820
      walk_depth_used: 0
      answer: "..."
      answer_correct: yes
      fallback_triggered: false
      total_io_tokens: 2100

  aggregate:
    avg_context_tokens: 2340
    avg_docs_read: 2.1
    intent_accuracy: 0.93
    answer_accuracy: 0.86
    fallback_rate: 0.07
```

---

## 5️⃣ 주의사항 (Pitfalls)

- **Golden Set 은 답을 고정**하고 수정 금지. 바꾸면 baseline 이 오염된다.
- **같은 모델 / 같은 세팅** 에서 비교. 다른 모델로 baseline 과 비교하면 신뢰 못 함.
- **캐시 영향** 고려. 프롬프트 캐시가 warm/cold 인지 기록 필드에 포함할 것.
- **sample size 작음**. 15~20개는 통계적 유의성이 약하다 — "10% 감소" 는 노이즈 범위일 수 있음.
  방향성 판단 용도로만 쓰고, 큰 리팩토링 후에는 Golden Set 자체를 확장.

---

## 6️⃣ 언제 측정하나 (Trigger)

```yaml
MeasurementTrigger:
  - "새 wiki-entity-*.md 파일 추가 시"
  - "wiki-relations.md 의 허브 노드가 추가·삭제될 때"
  - "intent-routing.yaml 의 Intent 분류 패턴 수정 시"
  - "엔티티 문서의 §1 Classification Axes 에 축 추가/삭제"
  - "분기별 정기 재측정"
```

---

## 🔗 관련 문서

- [wiki-schema-guide.md](wiki-schema-guide.md) — 스키마 설계 철학
- [wiki-intent-routing.md](wiki-intent-routing.md) / [intent-routing.yaml](intent-routing.yaml) — 측정 대상 라우팅
- [wiki-relations.md](wiki-relations.md) — 측정 대상 그래프 문서
