# Intent Routing (AI 탐색 라우팅 스키마)

> "무지성 의미검색" 대신 **질문의 의도(Intent)** 를 먼저 고정 enum 으로 분류하고,
> intent 마다 **결정론적 진입점(Entry Point)** 과 **그래프 워크(Walk)** 와 **질의 템플릿(Query)** 을 미리 엮어둔 라우팅 표.
> AI 는 이 문서를 먼저 보고 "어느 문서의 어느 섹션부터 읽을지" 를 **검색 없이** 결정한다.

> **⚡ 기계 파싱 전용**: 분류 패턴·엔트리포인트·예산만 필요하면 [intent-routing.yaml](intent-routing.yaml) 을 직접 읽는다 (40~60줄).
> 이 문서는 판단 근거·예시·폴백 정책처럼 **yaml 로 못 담는 산문** 을 담는다. 두 파일은 짝이며 버전이 일치해야 한다.

---

## 🆕 v2 변경점 (2026-04-24)

1. **`tool:` 필드 신설** — 각 intent 에 `wiki-tool` CLI 호출 리스트를 엮어 두었다.
   AI 는 `primary`/`secondary` 문서를 읽기 **전에** tool 을 먼저 실행한다
   (`budget.prefer_tool_over_read=true`).
2. **`tool_capabilities:` 카탈로그** — CLI 로 답 가능한 질문 유형과 CLI 인수 포맷을
   intent 와 독립적으로 기술. AI 는 capability → tool 인수 → 실행 순서로 움직인다.
3. **`query_templates:` → `narrative_queries:`** — 코드로 답 가능한 건 `tool:` 로 이동.
   `narrative_queries:` 에 남은 것은 **AI 서술 추론이 필요한 질문만** 의미한다.
4. **`policy.order`** — 실행 순서를 명문화: classify → **tool 먼저** → 필요 시 doc 읽기 → walk → narrative → fallback.

> 요약: v1 은 "어디를 읽을지" 만 결정했다. v2 는 "먼저 무엇을 실행할지 (코드)" → "그 결과로 부족하면 무엇을 읽을지 (AI)" 2단 파이프라인이다.

---

## 🎯 설계 원칙

1. **Intent 는 고정 enum** — 질문을 이 중 하나로 분류한다 (project-goal.md 의 7가지 역할과 매핑).
2. **Entry Point = (문서, 섹션, 필드) 삼요소** — 어디서부터 읽을지 애매함 없게.
3. 탐색은 **그래프 워크**(wiki-relations.md) + **질의 템플릿**(각 엔티티 §7/§8) 두 가지만 사용.
4. **의미 검색은 마지막 폴백** — 위 절차로 답이 안 나올 때만. 그것 자체가 "스키마 결손 신호".
5. Intent 는 하나씩 독립적으로 처리할 수 있어야 함 (스택 없음).

---

## 1️⃣ Intent 분류 (Question Classification)

> 모든 QA/기획 질문은 이 중 하나로 분류된다.

```yaml
Intent:
  - SingleRuleCheck       # "이 상태에서 이 행동 가능?"              → project-goal 1️⃣ 가상 테스트
  - CoverageGap           # "테스트 공백은?"                         → project-goal 2️⃣ QA 리드
  - SpecAmbiguity         # "기획 문서에 이 케이스 규칙 있나?"        → project-goal 3️⃣ 사양 검증기
  - IntentDrift           # "이 변경이 원래 의도를 벗어나는가?"       → project-goal 4️⃣ 의도 검증
  - BalanceRisk           # "이 스킬 너무 세거나 악용 여지 있나?"     → project-goal 5️⃣ 밸런스
  - BugRootCause          # "이 버그는 언제 터지나?"                 → project-goal 6️⃣ 원인 설명
  - ChangeImpact          # "이 변경 괜찮나? 뭐가 영향받나?"          → project-goal 7️⃣ 영향 분석
```

### 1-1. Intent 분류 신호 (Classifier Rules)

> 질문 표면의 **동사·의문사·시제** 로 판별한다. 애매하면 default=SingleRuleCheck.

```yaml
IntentClassifier:
  - pattern: ["가능", "되나", "허용", "금지"]                  → SingleRuleCheck
  - pattern: ["테스트 안 된", "커버리지", "공백", "빠진"]       → CoverageGap
  - pattern: ["정의 없음", "애매", "모호", "규칙 누락"]          → SpecAmbiguity
  - pattern: ["의도", "변질", "원래 목적", "컨셉"]             → IntentDrift
  - pattern: ["너무 센", "악용", "OP", "밸런스", "메타"]        → BalanceRisk
  - pattern: ["왜 발생", "재현", "언제 터지", "원인"]           → BugRootCause
  - pattern: ["바꾸면", "영향", "회귀", "변경"]                 → ChangeImpact
```

---

## 2️⃣ Entry Point 매핑 (Intent → 어디서부터 읽을지)

> 각 intent 마다 **1차 진입점 → 확장 참조 → 필요 시 grap walk** 순서로 정해져 있음.
> "1차 진입점 밖에서 답이 나오면 거기서 종료" 를 원칙으로.

### 2-1. `SingleRuleCheck` — "이 상태에서 이 행동 가능?"

```yaml
EntryPoint.SingleRuleCheck:
  primary:
    - doc: 행동 주체 문서 (Player/Monster)
      section: "§6 Action Restrictions"      # Player §6 / Monster §6 BehaviorRule
    - doc: 행동 대상 문서 (Skill/Interaction)
      section: "§3 Restrictions / preconditions"

  secondary:
    - doc: wiki-entity-zone.md
      section: "§4 ZoneRestriction"          # 환경 조건 확인
    - doc: wiki-entity-state.md
      section: "§2 State 엔티티 전체 속성"    # CC/침묵/면역 확인

  walk:
    - Walk.PredicateClosure                  # 조건이 최종적으로 무엇을 읽는지 추적

  queryTemplate:
    - "Skill §8 — 이 스킬은 SafeZone 에서 사용 가능한가?"
    - "Player §6 예시 — LifeState.Dead 이면 UseSkill 불가"

  stopWhen: "첫 번째 매칭되는 Restriction.allowed=false 를 발견하면 종료 (priority 오름차순)"
```

**예시 질문**: "안전지역에서 Fireball 쓸 수 있어?"
→ 1) wiki-skill-schema.md §3 에서 `restrictions[].condition=InSafeZone` 찾음
→ 2) `allowed=false, reason=SafeZoneRestriction` 확인 → 종료
→ 추가 탐색 불필요.

---

### 2-2. `CoverageGap` — "테스트 안 된 조합이 뭐야?"

```yaml
EntryPoint.CoverageGap:
  primary:
    - doc: 대상 엔티티
      section: "§1 Classification Axes"      # 모든 축의 데카르트곱 생성

  secondary:
    - doc: wiki-relations.md
      section: "§4 핵심 허브"                # 축 재사용처 파악

  walk:
    - (없음) — 축 조합 생성 후 실제 인스턴스와 diff

  queryTemplate:
    - "Skill §8 — archetype 별 스킬 수 → 특정 원형 결손 탐지"
    - "Skill §8 — interactions 가 비어있는 스킬"
    - "Skill §8 — InSafeZone restriction 이 없는 Damage 스킬"

  stopWhen: "빈 조합 리스트 생성 완료"
```

**예시 질문**: "Fire 속성 스킬 중 얼음 저항 몬스터와의 상호작용이 없는 스킬 있어?"
→ 1) Skill.damageType=Fire 전수
→ 2) 각 Skill.interactions[] 에 `withTag: TargetHasState.Frozen` 류 참조 있는지 확인
→ 3) 없는 것 목록 = 공백.

---

### 2-3. `SpecAmbiguity` — "기획 문서에 이 케이스 정의 있어?"

```yaml
EntryPoint.SpecAmbiguity:
  primary:
    - doc: 관련 엔티티
      section: "§8-9 불변식 (Invariants)"    # 어긴 규칙 / 빠진 케이스 찾기

  secondary:
    - doc: 관련 엔티티
      section: "§5 Interactions"             # 상호작용 공백 확인

  walk:
    - (없음) — Invariant 위반 스캔 + 관계 매트릭스의 빈 셀 탐지

  queryTemplate:
    - "Skill §9 invariant — effectCategory=Damage 이면 damageType≠None"
    - "Skill §8 — interactions 가 비어있는 스킬"
    - "wiki-relations.md §6 — Edge 가 있지만 to 가 존재하지 않는 유령 참조"

  stopWhen: "Invariant 위반 또는 정의 누락 리포트 생성 완료"
```

**예시 질문**: "소환형 스킬이 안전지역에서 어떻게 동작한다는 정의 있어?"
→ 1) Skill.effectCategory=Summon 전수
→ 2) 각 Skill.restrictions 에 `condition=InSafeZone` 있는지 확인
→ 3) 없는 것 = **규칙 누락**. (project-goal.md 의 "소환형 스킬 적용 정의 없음" 시나리오)

---

### 2-4. `IntentDrift` — "원래 의도를 벗어났나?"

```yaml
EntryPoint.IntentDrift:
  primary:
    - doc: wiki-skill-schema.md (또는 해당 엔티티)
      section: "§6 Archetypes"               # 원형 정의에서 이탈 여부

  secondary:
    - doc: 대상 엔티티
      section: "§1 Classification Axes"      # 축값의 조합이 원형과 일치하는지
    - doc: wiki-relations.md
      section: "§5-3 ProductionChain"        # 이 스킬이 생성하는 State 체인 확인

  walk:
    - Walk.ProductionChain                   # 결과물 비교용
    - Walk.ChangeImpact (depth=1)            # 변경 전/후 비교

  queryTemplate:
    - "Skill §6 — Archetype 정의와 현재 축 조합 비교"
    - "Skill §8 — targetFaction + effectCategory 모순 조합"

  stopWhen: "원형 기대값 대비 이탈 축/수치 리포트 완료"
```

**예시 질문**: "Fireball 범위 증가로 '광역 고위험 스킬' 의도에서 '안전한 범용 스킬' 로 바뀌었나?"
→ 1) 원형: `SingleTargetActive` → 변경 후 areaType=AreaOfEffect 라면 원형 이탈
→ 2) restrictions 가 그대로인데 areaType 이 바뀌면 → 의도 변질 가능성.

---

### 2-5. `BalanceRisk` — "악용 여지 있나?"

```yaml
EntryPoint.BalanceRisk:
  primary:
    - doc: wiki-skill-schema.md
      section: "§6 Archetypes"               # 위험 원형 필터 (Global/AoE/UntilDispelled/Channeled)
    - doc: wiki-skill-schema.md
      section: "§5 Interactions"             # AmplifiedBy / NullifiedBy 조합

  secondary:
    - doc: wiki-entity-state.md
      section: "§7 StateInteraction"         # Amplifies / Consumes 체인
    - doc: wiki-entity-monster.md
      section: "§3 resistances / immunities" # 특정 속성에 대한 취약/내성
    - doc: wiki-entity-zone.md
      section: "§5 ZoneModifier"             # 지역 기반 배율

  walk:
    - Walk.ProductionChain                   # 폭발형 조합 생성 경로 탐색
    - Walk.ChangeImpact                      # 변경 직후 신규 combo 출현

  queryTemplate:
    - "Skill §8 — areaType=Global + targetFaction=Enemy"
    - "Skill §8 — durationType=UntilDispelled + dispelType=Undispellable"
    - "Skill §8 — targetFaction=Ally + effectCategory=Damage (모순 조합)"

  stopWhen: "위험 조합 후보 리스트 + 각각의 시나리오 생성 완료"
```

**예시 질문**: "Fireball 이 Oiled 디버프 중첩되면 실전 DPS 너무 안 세?"
→ 1) Skill.interactions: `AmplifiedBy TargetHasState.Oiled, damageMultiplier=1.5`
→ 2) Oiled 를 만드는 모든 Skill/State 전수 → 체인 DPS 계산.

---

### 2-6. `BugRootCause` — "이 버그는 언제 터지나?"

```yaml
EntryPoint.BugRootCause:
  primary:
    - doc: 버그 증상 주체 (대개 Skill 또는 Interaction)
      section: "§3 Restrictions" + "§4 Effects"
    - doc: wiki-entity-state.md
      section: "§4 StateTrigger" + "§5 RemoveCondition"

  secondary:
    - doc: wiki-relations.md
      section: "§5-2 PredicateClosure"       # 조건 체인 추적
    - doc: wiki-entity-session.md
      section: "§6 Instance"                 # 페이즈·주기 문제
    - doc: wiki-entity-interaction.md
      section: "§8 SideEffect"               # 예상치 못한 부수효과

  walk:
    - Walk.PredicateClosure                  # 조건 체인 끝까지
    - Walk.ProductionChain                   # 이 순간 뭐가 만들어졌는지

  queryTemplate:
    - "Skill §9 invariant 위반 후보 (우선순위)"
    - "State §4 triggerOn — 이 타이밍에 발동하는 상태이상"
    - "Zone §12 invariant — Zone 전환 순간의 일관성"

  stopWhen: "재현 조건 축 조합 3~5개 확정"
```

**예시 질문**: "쿨타임 해제 직후 타겟 유실 + 광역 판정이 먼저 오면 피해가 0 으로 찍힘"
→ 1) Skill.restrictions 에 `TargetOutOfSight` 가 있지만 AoE 경로에서 검사 순서가 뒤바뀌었을 가능성
→ 2) Skill.effects.target 이 `PrimaryTarget` 일 때만 발생 / `AllEnemiesInArea` 는 무관.

---

### 2-7. `ChangeImpact` — "이 변경 괜찮아요?"

```yaml
EntryPoint.ChangeImpact:
  primary:
    - doc: wiki-relations.md
      section: "§3 Edge 정의"                # 변경된 필드가 어느 Edge 의 to 인지

  secondary:
    - doc: wiki-relations.md
      section: "§4 핵심 허브"                # 허브면 영향 큼
    - doc: 관련 엔티티
      section: "§8-9 불변식 (Invariants)"    # 변경 후에도 불변식 유지되는지

  walk:
    - Walk.ChangeImpact                      # incoming BFS depth=2

  queryTemplate:
    - "Relations §7 — X 를 바꾸면 영향받는 모든 속성"
    - "Relations §7 — 이 State 를 만들어내는 모든 Skill/Item/Quest"
    - "각 엔티티 §9 invariant — 변경 후 위반 여부"

  stopWhen: "영향 범위 리스트 + invariant 위반 여부 + 테스트 대상 목록 완료"
```

**예시 질문**: "state.burn 의 baseDuration 을 5초 → 8초로 늘리면?"
→ 1) wiki-relations.md §3-2: `State.id=state.burn` 의 incoming edges
→ 2) Skill.effects 에서 `value=state.burn` 인 스킬 전수 → Fireball 등
→ 3) Monster.immunities 에 `state.burn` 있는 몬스터 → 화상 면역 무관
→ 4) State §9 invariant `baseDuration ≤ maxDuration` 확인 → maxDuration=10 이므로 OK.

---

## 3️⃣ 통합 라우팅 알고리즘 (Routing Algorithm)

```yaml
Route:
  step1_classifyIntent:
    input: 사용자 질문 텍스트
    process: IntentClassifier 로 1차 분류
    fallback: SingleRuleCheck

  step2_resolveEntryPoint:
    input: Intent
    process: 위 §2 매핑에서 primary entry point 선택
    output: (doc, section, field)

  step3_readAndAnswer:
    input: Entry point
    process:
      - primary section 을 읽어 답 시도
      - 부족하면 secondary section 확장
      - queryTemplate 중 매칭되는 것 실행

  step4_graphWalk:
    condition: step3 에서 "연결된 엔티티" 가 필요할 때만
    input: walk 정의 (ChangeImpact / PredicateClosure / ProductionChain / LifecycleTrace)
    process: wiki-relations.md §3 Edge 정의를 따라 BFS

  step5_fallback_semanticSearch:
    condition: step3, step4 모두 답 없음 — 스키마에 존재하지 않는 개념일 가능성
    action:
      - 의미 검색 수행
      - 그 결과를 "스키마 결손 후보" 로 로그 (나중에 스키마 축에 편입 고려)

  step6_reportWithTrace:
    output:
      answer: 답변
      sources: 읽은 (doc, section) 목록
      walkPath: 그래프 걷기 경로 (있었다면)
      gaps: 스키마로 답할 수 없었던 부분 (있었다면)
```

---

## 4️⃣ 언제 의미 검색으로 폴백하나 (Fallback Criteria)

```yaml
Fallback.toSemanticSearch:
  when:
    - step3 에서 어떤 section 도 매칭 안 됨
    - Intent 가 7가지 중 어느 것과도 높은 신뢰도로 매칭 안 됨
    - 질문에 스키마에 없는 **신규 용어** 가 핵심 개념으로 등장

  doWhat:
    - 임베딩 검색 수행 (전체 wiki-* 대상)
    - 결과 상위 3개를 후보로 제시
    - 답변에 "스키마 밖 개념, 검증 필요" 표시

  doNotWhat:
    - fallback 결과를 스키마와 동등하게 인용하지 않기
    - fallback 결과를 자동으로 스키마에 반영하지 않기 (사람 검토 필요)

  logAs:
    category: "스키마 결손 후보 (schema-gap-candidate)"
    action: "사람이 검토 후 §1 Classification Axes 에 편입 여부 결정"
```

---

## 5️⃣ 탐색 예산 (Budget) 가이드

> 라우팅이 무한정 확장되지 않도록 상한을 둔다.

```yaml
Budget:
  maxDocsToRead: 4                 # primary(1~2) + secondary(1~2)
  maxWalkDepth: 2                  # BFS 2홉 기본, ChangeImpact 만 3홉 허용
  maxQueryTemplates: 3             # entry point 의 queryTemplate 중 상위 3개
  timeoutHint: "예산 초과 시 중간 결과로 답하고 gaps 에 미완료 표시"
```

---

## 6️⃣ 불변식 (Invariants)

```yaml
Invariant:
  - rule: "모든 Intent 는 최소 1개의 EntryPoint.primary 를 가져야 함"
  - rule: "EntryPoint 의 doc 은 실존 파일, section 은 해당 문서에 실존"
  - rule: "walk 에 명시된 Walk.* 는 wiki-relations.md §5 에 정의되어야 함"
  - rule: "queryTemplate 은 해당 엔티티 문서의 §7 또는 §8 에 실존"
  - rule: "Fallback 은 '스키마로 답할 수 없음' 을 기록해야 함 (silent fail 금지)"
```

---

## 7️⃣ AI 사용 질의 템플릿 (Meta Queries)

```yaml
Query:
  - "이 질문의 Intent 는 뭔가?"
    → §1-1 IntentClassifier 실행

  - "Intent=X 일 때 어느 문서부터 읽나?"
    → §2 EntryPoint.X.primary

  - "Intent 분류가 애매할 때 뭐부터 시도하나?"
    → default = SingleRuleCheck

  - "읽어도 답 없으면?"
    → §3 step5 (의미검색 폴백) 후 §4 에 로그

  - "라우팅이 제대로 작동하는지 검증하려면?"
    → §6 Invariant 위반 여부 + 실제 질문 샘플 세트로 회귀 테스트
```

---

## 🔗 관련 문서

- [project-goal.md](project-goal.md) — Intent 원전 (7가지 역할)
- [wiki-schema-guide.md](wiki-schema-guide.md) — 스키마 설계 철학
- [wiki-relations.md](wiki-relations.md) — Graph Walk 정의 및 Edge 카탈로그
- [wiki-skill-schema.md](wiki-skill-schema.md)
- [wiki-entity-state.md](wiki-entity-state.md)
- [wiki-entity-player.md](wiki-entity-player.md)
- [wiki-entity-monster.md](wiki-entity-monster.md)
- [wiki-entity-zone.md](wiki-entity-zone.md)
- [wiki-entity-item.md](wiki-entity-item.md)
- [wiki-entity-interaction.md](wiki-entity-interaction.md)
- [wiki-entity-quest.md](wiki-entity-quest.md)
- [wiki-entity-session.md](wiki-entity-session.md)
- [wiki-entity-ui.md](wiki-entity-ui.md)
