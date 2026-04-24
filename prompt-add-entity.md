# Prompt Guide: Adding a New Entity (AI 진입점)

> 새 엔티티 타입을 추가할 때 AI 에게 어떤 컨텍스트를 주고 어떻게 요청할지를 정리한 **진입점 문서**.
> 실제 작업 절차 자체는 [process-add-entity.md](process-add-entity.md) 를 따른다 — 이 문서는 그 프로세스를 AI 에게 **어떻게 태우는지** 에 대한 가이드.

---

## 🎯 언제 이 문서를 쓰나

- 새 **엔티티 타입** 추가 (예: `guild`, `pet`, `crafting` 처음 도입)
- "새 몬스터 10종 추가" 같은 **인스턴스 증가**는 이 문서 범위가 아님 — `instances/<entity>/*.yaml` 만 쓰면 됨. [process-add-entity.md §4a](process-add-entity.md) 참조.

---

## 1️⃣ 최소 진입점 (AI 에게 줄 컨텍스트)

```
필수 컨텍스트:
  - process-add-entity.md           (작업 프로세스)
  - wiki-schema-guide.md            (스키마 설계 철학)
  - wiki-instance-guide.md          (인스턴스 포맷 규약)
  - 유사한 기존 엔티티 md 1개       (템플릿으로 삼을 것)

요청 포맷:
  "[X] 엔티티를 추가해줘.
   - 기획 요구사항: <스펙>
   - 축(axis) 후보: <있으면>
   - 참조 관계: <다른 엔티티와의 연결>
   process-add-entity.md 를 따라 진행해."
```

이 셋이 있으면 AI 는:
- `process-add-entity.md` 로 **무엇을** 해야 하는지 안다
- `wiki-schema-guide.md` 로 **어떻게** 설계하는지 안다
- 유사 엔티티 md 로 **구체적 포맷**을 복사할 수 있다

---

## 2️⃣ `process-add-entity.md` 만으로 부족한 이유

프로세스 문서는 "무엇을 고쳐야 하나"(레지스트리·함수·디렉터리)는 잘 알려주지만, **"어떻게 설계해야 좋은 스키마인가"** 는 알려주지 않는다.

예시 판단:
- 축(axis)을 몇 개로 뽑을지
- enum 을 얼마나 잘게 쪼갤지 (Rank 를 `Trash/Normal/Elite/...` 9단계 vs `Low/Mid/High` 3단계)
- 어떤 필드를 Template 에 두고 어떤 걸 Instance 에 둘지
- 불변식을 얼마나 공격적으로 걸지

이런 설계 판단은 [wiki-schema-guide.md](wiki-schema-guide.md) 의 철학이고, 프로세스 문서와는 별개. **둘 다** 줘야 한다.

---

## 3️⃣ 유사 엔티티 템플릿 지정

AI 가 md 구조(§1 분류축 헤더 포맷, 코드펜스 위치, enum 리스팅 방식)를 정확히 맞추게 하려면 **복사할 대상**을 명시하는 게 가장 확실.

| 새 엔티티 성격 | 템플릿 후보 |
|---|---|
| 상태·버프·효과 계열 | [wiki-entity-state.md](wiki-entity-state.md) |
| 생물·적성·NPC 계열 | [wiki-entity-monster.md](wiki-entity-monster.md) |
| 객체·소유·인벤토리 계열 | [wiki-entity-item.md](wiki-entity-item.md) |
| 시스템·행위·절차 계열 | [wiki-entity-interaction.md](wiki-entity-interaction.md) |
| 공간·영역·컨텍스트 계열 | [wiki-entity-zone.md](wiki-entity-zone.md) |
| 화면·UI·입력 계열 | [wiki-entity-ui.md](wiki-entity-ui.md) |
| 목표·진행·상태전이 계열 | [wiki-entity-quest.md](wiki-entity-quest.md) |

**"비슷한 게 있는지 스스로 찾아라"** 로 맡기면 엉뚱한 걸 고를 수 있다. 지정해주는 게 낫다.

여러 성격이 섞인 엔티티면 템플릿을 **2개까지** 지정 (예: `pet` 은 생물(monster) + 소유(item)).

---

## 4️⃣ 게임 업데이트 맥락이면 추가 컨텍스트

[process-add-entity.md §4c](process-add-entity.md) 의 "기존 엔티티 동반 수정" 이 필요한 경우:

```
추가 컨텍스트:
  - 동반 수정 대상 엔티티 md (예: wiki-entity-player.md)
  - 그 엔티티의 기존 인스턴스 목록 (instances/players/*.yaml)
  - relations/<해당엔티티>.md
```

"player 에 guildId 필드를 추가하고 기존 인스턴스도 전부 마이그레이션해" 같은 작업은 컨텍스트 없으면 AI 가 어느 파일을 건드려야 하는지 모른다.

---

## 5️⃣ 단계 분리 — 한 번에 다 시키지 말 것

엔티티 추가는 여러 단계가 있는데, **한 프롬프트에 몰아넣지 말고** 단계별로 끊는 게 안전:

```
1턴: "wiki-entity-X.md 스키마 초안을 써줘"
      → 사람 리뷰 후 확정
2턴: "이 스키마로 wiki-tool.py 레지스트리와 _inv_X 를 추가해줘"
      → check-invariants 빈 상태로 통과 확인
3턴: "첫 인스턴스 1~3개와 relations/X.md 를 작성해줘"
      → check-refs / check-invariants 통과 확인
4턴: "check-invariants / check-refs 최종 회귀 + negative test"
```

**이유:**
- schema 가 확정되기 전에 `_inv_X` 를 쓰면 schema 가 바뀔 때 재작성
- 인스턴스를 먼저 쓰면 schema 가 바뀔 때 재작성 (schema-먼저 원칙)
- 단계마다 사람이 리뷰·수정할 기회가 생김
- AI 도 한 번에 할 일이 줄어서 실수가 줄어듦

---

## 6️⃣ 프롬프트 템플릿

### 6a. 1턴 — 스키마 초안

```
[X] = <엔티티명> (<한 줄 설명>)

컨텍스트:
  - process-add-entity.md
  - wiki-schema-guide.md
  - wiki-instance-guide.md
  - wiki-entity-<유사엔티티>.md   (이 구조를 템플릿으로)
  - (선택) wiki-entity-<두번째유사>.md

기획 요구사항:
  - <플레이어와의 관계>
  - <수명 / 상태 전이>
  - <다른 엔티티 참조 관계>
  - <특수 제약 / 도메인 규칙>

축(axis) 후보 (있으면):
  - <AxisName>: <enum 후보들>

작업:
  process-add-entity.md §2 Step 1 만 먼저 — wiki-entity-X.md 초안.
  wiki-entity-<유사엔티티>.md 의 구조를 그대로 복사하고 X 에 맞게
  축과 필드를 조정.
  §N 불변식은 최소 5개, 기계화 가능한 것만.
  완료 후 리뷰할 테니 Step 2 (wiki-tool.py 수정) 는 아직 진행하지 말 것.
```

### 6b. 2턴 — 레지스트리 + invariant 함수

```
1턴의 wiki-entity-X.md 가 확정됨.

작업:
  process-add-entity.md §2 Step 2~3 진행.
  - ENTITY_DIRS, SCHEMA_FILES 에 X 추가
  - build_index / check_refs 의 id-like 정규식 2곳에 X 추가
  - _inv_X 함수 작성 후 INVARIANT_FNS 에 등록
  - §N 불변식의 자연어 rule (기계화 불가) 은 주석으로만 남김

검증:
  인스턴스가 아직 없는 상태에서 `python wiki-tool.py all` 이 초록불.
```

### 6c. 3턴 — 인스턴스 + relations

```
작업:
  process-add-entity.md §2 Step 4~5 진행.
  - instances/Xs/<대표>.yaml  최소 1개 (각 축 enum 에 대표값 하나씩)
  - relations/X.md  작성
  - wiki-relations.md  허브 맵에 X 반영

검증:
  `python wiki-tool.py all` 초록불 + check-coverage 에서 X 가 보이는지.
```

### 6d. 4턴 — Negative test 회귀

```
작업:
  process-add-entity.md §2 Step 6 진행.
  instances/Xs/_negtest.yaml 에 _inv_X 의 각 rule 을 의도적으로 위반한
  인스턴스 1개 작성.
  enum 값은 schema 에 있는 것만 쓸 것 (enum 검증이 아닌 invariant 검증
  트리거용).

검증:
  `python wiki-tool.py check-invariants` 가 모든 위반을 출력.
  확인 후 _negtest.yaml 제거하고 최종 `python wiki-tool.py all` 초록불.
```

### 6e. 게임 업데이트 맥락 — 1턴 확장 예시

기존 엔티티 동반 수정이 있는 경우 1턴 프롬프트에 **추가**:

```
동반 수정 대상:
  - wiki-entity-player.md   (player.guildId 필드 추가)
  - instances/players/*.yaml (기존 인스턴스 마이그레이션 — guildId 기본값 null)
  - relations/player.md     (guild 와의 관계 반영)

작업:
  1턴에서는 wiki-entity-X.md 초안만 진행.
  동반 수정은 **별도 턴**으로 분리할 것 — 지금은 참고용으로만 알려줌.
```

---

## 7️⃣ 체크리스트 (프롬프트 보내기 전)

- [ ] `process-add-entity.md`, `wiki-schema-guide.md`, `wiki-instance-guide.md` 3개 기본 컨텍스트 확보
- [ ] 유사 엔티티 md 1~2개 지정 (§3 표 참조)
- [ ] 기획 요구사항 구체화 (축 후보, 참조 관계, 특수 제약)
- [ ] 게임 업데이트 맥락이면 동반 수정 대상 엔티티·인스턴스 목록 추가
- [ ] 한 턴에 몰아넣지 않고 Step 1~6 을 4턴 이상으로 분리
- [ ] "다음 단계는 진행하지 말 것" 명시 (AI 가 선주행 방지)

---

## 🔗 관련 문서

- [process-add-entity.md](process-add-entity.md) — 실제 작업 프로세스 (이 문서의 짝)
- [wiki-schema-guide.md](wiki-schema-guide.md) — 스키마 설계 철학
- [wiki-instance-guide.md](wiki-instance-guide.md) — 인스턴스 파일 규약
- [wiki-tool.py](wiki-tool.py) — 인덱서/린터 (레지스트리 위치)
