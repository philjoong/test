# Instance Layout & Convention (인스턴스 배치 규약)

> **스키마는 `wiki-entity-*.md`, 인스턴스는 `instances/<entity>/<id>.yaml`.**
> 이 문서는 "실제 게임 데이터(Fireball, state.burn 등)를 어디에, 어떤 포맷으로 쓸지" 만 규정한다.
> 스키마 축/enum/invariant 정의는 해당 `wiki-entity-*.md` 의 §1, §9 를 유일 출처로 삼는다.

---

## 🎯 왜 분리하나

- `wiki-*-schema.md` 는 항상 읽히는 **L0~L1 컨텍스트**. 인스턴스가 섞이면 토큰 폭발.
- 인스턴스는 **순수 YAML** — `wiki-tool` 이 파싱해 `index/*.json` 을 생성, AI 는 인덱스로 필터링한 결과만 읽음.
- 인스턴스 내 산문·장식·주석 없음. 모든 필드는 해당 엔티티 스키마의 enum/타입 값만.

---

## 1️⃣ 디렉터리 레이아웃

```
instances/
  skills/          <id>.yaml         # wiki-skill-schema.md 의 Skill 속성
  states/          <id>.yaml         # wiki-entity-state.md 의 State 속성
  monsters/        <id>.yaml
  items/           <id>.yaml         # ItemTemplate 기준 (Instance 아님)
  zones/           <id>.yaml
  quests/          <id>.yaml
  interactions/    <id>.yaml
  ui-screens/      <id>.yaml
index/                               # wiki-tool 이 생성. 손으로 편집 금지.
  by-axis.json
  by-archetype.json
  hubs.json
  coverage.json
  invariant-violations.json
  ref-integrity.json
```

**원칙**:
- 한 인스턴스 = 한 파일. 번들 금지.
- 파일명은 `id` 의 뒷부분 (`skill.fireball` → `fireball.yaml`).
- 인스턴스 파일에는 **최상위 키 1개** (`skill:` / `state:` / `monster:` ...) — 파서가 단일화됨.

---

## 2️⃣ YAML 컨벤션

```yaml
# 최상위 wrapper 키 = 엔티티 종류 (소문자 단수)
skill:
  id: skill.fireball          # 필수. 파일명과 일치해야 함
  name: "Fireball"
  version: "1.0.0"
  # ... 이하 wiki-skill-schema.md §2 의 모든 필드
```

### 필드 규칙

1. **enum 필드는 wiki-entity-*.md §1 의 값만** 사용. 자유문 금지.
2. **선택 필드도 명시**. 생략 대신 빈 배열(`[]`) 또는 `0`/`false` 로 쓴다. 누락 = 스키마 결손 신호.
3. **참조는 id 문자열** (`value: state.burn`, `withStateId: state.freeze`). 인라인 객체 중첩 금지.
4. **수치는 숫자 그대로** (`baseDuration: 5`). 단위 접미어(`"5s"`) 금지.
5. **주석은 `# why:` 접두어가 있을 때만**. 그 외 장식 주석은 scripts 가 제거 대상으로 본다.

### id 명명

```
skill.<snake_case>        # skill.fireball, skill.divine_shield
state.<snake_case>        # state.burn, state.arcane_power
monster.<snake_case>      # monster.goblin_scout
item.<snake_case>         # item.health_potion
zone.<snake_case>         # zone.safe_town_square
```

---

## 3️⃣ 새 인스턴스 추가 절차

1. 해당 `wiki-entity-*.md` 의 §1 축 / §2 속성 / §9 invariant 를 **먼저 확인**.
2. 사용할 필드 값이 모두 기존 enum 안에 있는지 검사.
   - 없으면 **축 추가부터** (인스턴스 추가 전에 스키마 확장).
3. `instances/<entity>/<id>.yaml` 생성.
4. `python wiki-tool.py build-index` 실행 → `index/*.json` 갱신.
5. `python wiki-tool.py check-invariants` / `check-refs` 통과 확인.
6. 실패 시 인스턴스 또는 스키마 수정 후 재실행. CI 게이트 역할.

---

## 4️⃣ AI 가 이 디렉터리를 읽는 방식 (컨텍스트 엔지니어링)

| 레벨 | 무엇을 | 언제 |
|------|--------|------|
| L0   | `intent-routing.yaml` (상시) | 항상 |
| L1   | `wiki-entity-<X>.md §1, §9` | Intent 결정 후 대상 엔티티만 |
| L2   | `index/by-axis.json` 쿼리 결과 N개 인스턴스 | 인스턴스 필터 필요 시 |
| L3   | `relations/<X>.md` 한 개 | walk 필요 시 |
| L4   | 의미 검색 (fallback) | 위에서 답 안 나올 때만 |

**AI 는 인스턴스 디렉터리를 직접 스캔하지 않는다.** 반드시 `wiki-tool` 의 인덱스 결과로 축소된 목록만 읽는다.

---

## 5️⃣ 코드 vs AI 책임 분담

| 작업 | 담당 | 이유 |
|------|------|------|
| 인스턴스 파싱·검증 | **wiki-tool** | 결정론적. LLM 불필요 |
| 축별/원형별 집계 | **wiki-tool** (`by-axis.json`) | 단순 group-by |
| 축 데카르트곱 vs 실제 diff (CoverageGap) | **wiki-tool** (`coverage.json`) | 집합 diff |
| invariant 위반 스캔 | **wiki-tool** (`invariant-violations.json`) | 규칙엔진 |
| 유령 참조 탐지 | **wiki-tool** (`ref-integrity.json`) | 파일/id 존재 검사 |
| 역참조 인덱스 (허브 incoming) | **wiki-tool** (`hubs.json`) | relations/*.md 파싱 |
| Intent 1차 분류 (keyword) | **wiki-tool** | 문자열 매칭 |
| 의미적 모호함 판단 | **AI** | 스키마 외 추론 |
| Archetype 이탈 의미 판단 | **AI** | 수치→의미 변환 |
| BalanceRisk 시나리오 생성 | **AI** | 조합 탐색 + 서술 |
| BugRootCause 가설 생성 | **AI** | 조건 공간 추론 |

---

## 6️⃣ 불변식 (Invariants — 인스턴스 레이아웃 자체의)

```yaml
Invariant:
  - rule: "파일명 = <id 의 마지막 segment>.yaml"
  - rule: "최상위 키 1개만 (skill|state|monster|item|zone|quest|interaction|ui)"
  - rule: "id 는 전역 고유"
  - rule: "모든 enum 필드 값은 해당 wiki-entity-*.md §1 에 존재"
  - rule: "참조 필드(id 문자열)는 실존 인스턴스 id 여야 함"
  - rule: "index/ 하위는 wiki-tool 만 쓴다. 수작업 편집 금지"
```

---

## 🔗 관련 문서

- [wiki-schema-guide.md](wiki-schema-guide.md) — 스키마 설계 철학
- [wiki-intent-routing.md](wiki-intent-routing.md) / [intent-routing.yaml](intent-routing.yaml)
- [wiki-measurement.md](wiki-measurement.md) — 이 규약의 효과 측정
- 각 엔티티 스키마: [wiki-skill-schema.md](wiki-skill-schema.md), [wiki-entity-state.md](wiki-entity-state.md), ...
