# Adding a New Entity (엔티티 추가 프로세스)

> 새 엔티티(예: `guild`, `pet`, `crafting` 등)를 wiki 시스템에 추가할 때 **반드시 수행해야 하는 작업 목록**.
> 실제 작업은 대부분 기계적이지만, 빠뜨리면 `wiki-tool`의 검사가 조용히 통과하거나 인덱스에서 누락된다.
> 관련 파일: [wiki-tool.py](wiki-tool.py), [wiki-instance-guide.md](wiki-instance-guide.md), [wiki-schema-guide.md](wiki-schema-guide.md).

---

## 🎯 전제

- 엔티티는 **고유 id prefix** 를 갖는다 (`skill.*`, `state.*`, `monster.*` 처럼).
- 스키마(md) 1개, 인덱서 등록, invariant 함수, relations 문서, 인스턴스 디렉터리 — 이 다섯 자리 중 하나라도 빠지면 실패한다.

---

## 1️⃣ 체크리스트 (요약)

새 엔티티 `X` 추가 시:

- [ ] `wiki-entity-<X>.md` 작성 (§1 분류축, §N 불변식 필수)
- [ ] `wiki-tool.py` 의 `ENTITY_DIRS` 에 `"X": "<X>s"` 추가
- [ ] `wiki-tool.py` 의 `SCHEMA_FILES` 에 `"X": "wiki-entity-<X>.md"` 추가
- [ ] `wiki-tool.py` 의 id-like 정규식 2곳에 `X` 추가 (`build_index` 내부, `check_refs` 내부)
- [ ] `wiki-tool.py` 에 `_inv_<X>` 함수 작성 후 `INVARIANT_FNS` 에 등록
- [ ] `instances/<X>s/` 디렉터리 생성 (최소 1개 인스턴스 파일)
- [ ] `relations/<X>.md` 작성 (해당 엔티티가 참조하는/참조되는 다른 엔티티)
- [ ] `wiki-relations.md` 의 허브 맵에 `X` 반영
- [ ] Negative test: 의도적 위반 인스턴스로 `_inv_<X>` 동작 확인
- [ ] `python wiki-tool.py all` 전체 회귀 통과 확인

---

## 2️⃣ 단계별 상세

### Step 1. 스키마 md 작성: `wiki-entity-<X>.md`

기존 엔티티 md (예: [wiki-entity-state.md](wiki-entity-state.md)) 를 템플릿으로 복사.

필수 섹션:

- **`## 1️⃣ 분류 축 (Classification Axes)`** — `### Axis.<AxisName>` + 코드펜스 안의 `- EnumValue` 리스트.
  - `wiki-tool.py` 의 `extract_axes` 가 이 포맷으로만 enum 을 뽑는다. 다른 포맷 쓰면 enum 검증이 동작 안 함.
- **`## N️⃣ 불변식 (Invariants)`** — `N` 은 몇 번이든 OK (섹션 제목에 "불변식" 만 포함되면 됨).
  - 코드펜스 안에 `- rule: "..."` 형식.
  - 수치/enum 비교 위주로 작성. "의미적으로 일관" 같은 자연어 rule 은 AI 심사용이지 `_inv_X` 로 옮기지 못함 — 별도로 표시.

**Why**: `wiki-tool.py` 의 `extract_axes`/`extract_invariants` 가 정규식 파싱이라 섹션 헤더와 코드펜스 포맷이 정확히 맞아야 한다.

### Step 2. `wiki-tool.py` 레지스트리 3곳 수정

#### 2a. `ENTITY_DIRS` ([wiki-tool.py:331](wiki-tool.py#L331))
```python
ENTITY_DIRS = {
    ...
    "X": "Xs",   # 디렉터리명은 복수형 관례 (skills, states, monsters, ...)
}
```

#### 2b. `SCHEMA_FILES` ([wiki-tool.py:342](wiki-tool.py#L342))
```python
SCHEMA_FILES = {
    ...
    "X": "wiki-entity-X.md",
}
```

#### 2c. id-like 정규식 **2곳** 수정

`build_index` 내부 `walk` 함수와 `check_refs` 내부 `walk` 함수에 동일한 정규식 리터럴이 있다:

```python
re.fullmatch(
    r"(skill|state|monster|item|zone|quest|interaction|ui|X)\.[a-z0-9_]+",
    node,
)
```

**빠뜨리면**: `X.foo` 참조가 reference로 인식되지 않아 `check_refs` 가 통과해 버린다 (조용한 실패).

### Step 3. Invariant 함수 작성 + 등록

기존 `_inv_skill`, `_inv_state` 를 템플릿으로. ([wiki-tool.py:542](wiki-tool.py#L542))

```python
def _inv_X(inst: dict) -> list[Violation]:
    v: list[Violation] = []
    iid = inst.get("id", "?")
    # rule 하나당 if 블록 하나
    if inst.get("fieldA") == "SomeValue" and inst.get("fieldB") != "Expected":
        v.append({"id": iid, "rule": "SomeValue requires fieldB=Expected"})
    return v
```

그리고 `INVARIANT_FNS` 에 등록 ([wiki-tool.py:867](wiki-tool.py#L867)):
```python
INVARIANT_FNS = {
    ...
    "X": _inv_X,
}
```

**중복 금지** — 다음 rule 은 `_inv_X` 에 **옮기면 안 된다**:
- Enum 값 소속 검사 → `check_enum_membership` 이 처리
- `X.foo` 같은 id 가 실존 엔티티인지 → `check_refs` 가 처리 (단, Step 2c 를 빠뜨리면 안 됨)

### Step 4. 인스턴스 디렉터리 & 최소 1개 파일

```
instances/Xs/<something>.yaml
```

포맷은 [wiki-instance-guide.md](wiki-instance-guide.md) 를 따른다. 최상위 키는 엔티티 이름 (`X:`).

```yaml
X:
  id: X.example
  name: "Example"
  version: "1.0.0"
  # ... 축/필드
```

### Step 5. Relations 문서

- `relations/X.md` 를 새로 작성. 이 엔티티가 어떤 엔티티를 참조하고, 어떤 엔티티로부터 참조되는지를 정리.
- `wiki-relations.md` 의 허브/흐름 다이어그램에 `X` 추가.

기존 `relations/skill.md`, `relations/state.md` 를 템플릿으로 사용.

### Step 6. Negative test (회귀 방지)

의도적으로 `_inv_X` 의 각 rule 을 위반하는 임시 인스턴스 1개를 `instances/Xs/_negtest.yaml` 에 작성.

```bash
python wiki-tool.py check-invariants
# 모든 의도된 위반이 [FAIL] 로 출력되는지 확인
```

확인 후 **임시 파일 제거**. (커밋하지 않음)

enum 값은 schema 에 있는 값만 써야 한다. 그래야 enum 검증이 아닌 **invariant 검증**이 트리거된다 (두 검사를 격리해 확인).

### Step 7. 전체 회귀

```bash
python wiki-tool.py all
```

출력에서:
- `[OK] all references resolve` — Step 2c 의 정규식이 정상 작동
- `[OK] no invariant or enum violations` — Step 3 의 함수가 정상 작동
- `indexed: {... 'X': N}` — Step 2a 의 등록이 정상 작동
- `coverage` 리포트에 `X` 가 포함되는지 — Step 1 의 `§1 분류 축` 이 정상 파싱됐는지

---

## 3️⃣ 흔한 함정

- **섹션 번호 의존 금지**: §1 은 고정이지만 불변식 섹션은 §9~§12 모두 사용 중. `INVARIANT_HEADER` 정규식은 "제목에 '불변식' 포함"만 보면 됨 ([wiki-tool.py:263](wiki-tool.py#L263)).
- **디렉터리 복수형 불일치**: `interactions/` vs `ui-screens/` 처럼 규칙이 들쭉날쭉이면 `ENTITY_DIRS` 값에 그대로 반영. 관례보다 레지스트리가 단일 출처.
- **id-like 정규식 2곳 동기화 실패**: `build_index` 만 고치고 `check_refs` 를 빠뜨리는 실수가 가장 흔함. 검색해서 둘 다 확인.
- **Template/Instance 혼동**: 스키마가 Template 과 Instance 를 분리한 경우 (예: Item), 한 인스턴스 파일에 양쪽 필드가 공존하지 않을 수 있다. `_inv_X` 에서는 **존재하는 필드에 대해서만** 검사 (`if field is not None` 가드).
- **자연어 rule 을 억지로 코드화 금지**: "의미적으로 일관" 같은 rule 은 AI 판단 영역. `_inv_X` 에 넣지 말고 rule 목록 주석으로 남겨둠.

---

## 4️⃣ 게임 업데이트 맥락에서 새 엔티티 추가

실제 라이브 서비스에서 새 엔티티 타입이 추가되는 상황 (예: 업데이트 패치로 `guild`, `pet`, `crafting` 시스템 도입). §1~§3 의 기본 체크리스트에 **추가로** 고려해야 하는 것들.

### 4a. 먼저 확인: 진짜 새 엔티티인가?

실무에서 "엔티티 추가"라는 말은 보통 두 가지를 섞어서 부른다 — 분리해야 한다.

| 케이스 | 실제 작업 |
|---|---|
| "새 몬스터 10종 추가" | **인스턴스 증가**. schema 불변, `instances/monsters/*.yaml` 만 추가. §2 프로세스 **불필요**. |
| "기존 축에 새 enum 값" (예: `Species.Slime` 신종) | `wiki-entity-<X>.md` §1 수정 PR → 인스턴스 PR. §2 **부분 적용** (Step 1 만). |
| **"새 엔티티 타입 도입" (예: guild 시스템 최초 추가)** | §2 전체 프로세스 + 이 §4 추가 고려사항. |

게임 업데이트 10번 중 9번은 첫 번째 행이다. 습관적으로 §2 전체를 돌리지 말 것.

### 4b. 릴리스 타임라인

새 엔티티 타입은 **기획 확정 → schema → 인스턴스 → 라이브** 순서가 강제된다. 이 순서는 "먼저 하면 편해서" 가 아니라 **되돌릴 수 없기 때문에** 지켜야 한다 (§4d 참조).

```
[T-N주]  기획 스펙 락인 (축/enum/불변식 정의 확정)
[T-N주]  schema PR: wiki-entity-X.md + wiki-tool.py 레지스트리 + _inv_X
          → 머지 전에 `python wiki-tool.py all` 초록불
[T-M주]  초기 인스턴스 PR: 런칭에 필요한 최소 세트
          → 머지 전에 check-refs / check-invariants 통과
[T-0]    라이브
[T+상시] 인스턴스 추가 PR (schema 는 변경 없음)
```

schema 가 흔들리는 동안 인스턴스를 같이 쓰면, schema 가 바뀔 때마다 인스턴스 수십~수백 개를 재작성해야 한다. **schema PR 과 인스턴스 PR 은 분리**.

### 4c. 기존 엔티티 스키마 동반 수정

새 엔티티는 거의 항상 기존 엔티티에 **필드 추가**를 유발한다:

- `guild` 추가 → `player.guildId` 추가 → `wiki-entity-player.md` 수정 → 기존 player 인스턴스 **전체 마이그레이션**
- `pet` 추가 → `item.petOnly` 같은 태그 → `wiki-entity-item.md` 수정
- `crafting` 추가 → `item.craftable` + `interaction.craftRecipe` 필드

이건 "새 엔티티 추가" 범위를 **넘어서** schema 변경이 된다. 동반 작업:

1. 기존 `wiki-entity-<Y>.md` 의 §1/§N 수정
2. 필요하면 `_inv_<Y>` 도 새 필드를 반영해 갱신
3. **기존 인스턴스 마이그레이션** — `instances/<Y>s/*.yaml` 전체에 새 필드 기본값 채워넣기 (또는 필드가 optional 인 경우 명시적으로 판단)
4. `relations/<Y>.md` 도 업데이트 (새 엔티티와의 참조 관계 반영)

마이그레이션이 대량이면 별도 스크립트를 짜는 게 낫다 (`wiki-tool.py` 에 `migrate` 서브커맨드 추가를 고려).

### 4d. 롤백 불가성

**schema 레벨 롤백은 사실상 불가능**. 이유:

- 새 엔티티 `X` 인스턴스가 생기고, 다른 엔티티가 `X.foo` 를 참조하기 시작하면, `X` 를 제거하는 순간 `check-refs` 가 대량 실패.
- 기존 엔티티에 붙인 필드를 되돌리면 그 필드를 쓰는 모든 인스턴스가 깨짐.

따라서 머지 **전에** schema 를 확정해야 한다. 일단 라이브에 나간 뒤에는:
- **기능 비활성화는 가능** — 인스턴스를 피처 플래그로 가리거나 빈 리스트로 둠
- **schema 제거는 불가** — 다음 메이저 업데이트까지 dead field 로 안고 감

### 4e. 릴리스 전 최종 검증

`python wiki-tool.py all` 의 초록불 외에 추가로 확인:

- **축 커버리지**: `check-coverage` 결과에서 새 엔티티 `X` 의 각 축(axis)에 **최소 1개 인스턴스**가 있는지. 커버리지 0 인 enum 값은 QA 불가능 — 론칭 전에 대표 인스턴스를 채우거나, 해당 enum 값을 §1 에서 빼야 한다.
- **교차 참조**: 새 엔티티가 참조하는 기존 엔티티 id 가 전부 resolve 되는지 (`check-refs`). 그리고 기존 엔티티가 새 엔티티를 참조하기 시작했다면 그쪽도 resolve 되는지.
- **불변식 커버리지**: `_inv_X` 가 §N 불변식의 기계화 가능한 rule 을 전부 포함하는지. 자연어 rule 은 별도 주석으로 남긴다 (§3 참조).
- **relations 문서**: `relations/X.md` + `wiki-relations.md` 허브 맵 업데이트. 문서만 빠지면 `wiki-tool` 검사는 통과하지만 AI 의 L0~L1 컨텍스트에서 새 엔티티가 고립됨.

### 4f. 체크리스트 (§1 기본 체크리스트에 **추가**)

- [ ] 기획 스펙 락인 후 schema 작업 시작 (진행 중 변경이 없는 상태)
- [ ] schema PR 과 인스턴스 PR 분리, schema 먼저 머지
- [ ] 동반 수정이 필요한 기존 엔티티 목록 식별 (`wiki-entity-<Y>.md`)
- [ ] 기존 인스턴스 마이그레이션 계획 (수동 / 스크립트)
- [ ] 각 축 enum 값에 대표 인스턴스 ≥ 1개 (coverage 0 없음)
- [ ] 교차 참조 resolve 확인 (양방향)
- [ ] 롤백 계획 = "피처 플래그로 비활성화" 명시 (schema 롤백 시도 금지)

---

## 5️⃣ 최소 PR diff (참고)

새 엔티티 `X` 추가 PR 에 포함돼야 하는 변경:

```
wiki-entity-X.md                        (신규)
wiki-tool.py                            (수정: ENTITY_DIRS, SCHEMA_FILES, 정규식 2곳, _inv_X, INVARIANT_FNS)
instances/Xs/<first-instance>.yaml      (신규, 최소 1개)
relations/X.md                          (신규)
wiki-relations.md                       (수정: 허브 맵)
```

이 5개 미만이면 어딘가 빠진 것이다.

게임 업데이트 맥락(§4)에서는 여기에 더해:
```
wiki-entity-<Y>.md                      (수정: 기존 엔티티에 새 필드)
instances/<Y>s/*.yaml                   (수정: 기존 인스턴스 마이그레이션)
relations/<Y>.md                        (수정: 새 엔티티와의 관계 반영)
```
도 동반 PR 로 함께 관리된다.
