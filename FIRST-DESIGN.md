# FIRST DESIGN

## Overview

이 시스템은 Word, Excel 등으로 작성된 게임 기획 문서를 프로젝트 지식 저장소로 변환하고, 그 저장소를 목적별 여러 layer의 지식 그래프로 표현하기 위한 구조이다.

핵심 목표는 단순 문서 검색이 아니라, 기획 문서의 내용을 사람이 검토 가능한 구조로 재배치한 뒤 다음 작업을 가능하게 만드는 것이다.

- 조건 기반 검증
- 조합 폭발 테스트 생성
- 회귀 영향 분석
- 테스트 공백 탐지
- 리스크 기반 추천
- 변경 영향 분석
- 구현 전 기획 결함 발견
- 정책/의도 위반 탐지
- 밸런스 시뮬레이션
- 게임 화면 이해 및 다음 조작 제안

## Input

초기 입력은 주로 실제 기획자가 사용하는 문서 형식이다.

- Word 문서
- Excel 문서

각 raw 파일은 먼저 1차 산출물로 변환된다.

## 1차 가공 산출물

1차 산출물은 raw 파일 단위로 생성되는 중간 표현이다.

예를 들어 `instance_server_design.docx`라는 원본 파일이 있다면, 이 파일 하나에 대응하는 1차 산출물이 생성된다.

```text
raw/
  instance_server_design.docx

processed_1/
  instance_server_design.md
```

1차 산출물의 목적은 원본 문서를 그대로 최종 DB에 넣는 것이 아니라, 이후 의미 단위로 분해하고 재조립하기 쉬운 형태로 바꾸는 것이다.

따라서 1차 산출물은 원본 파일의 문서 단위를 유지한다.

## 2차 가공 산출물

2차 산출물은 1차 산출물의 내용을 프로젝트별 `schema.md`에 맞춰 분해하고 재조립한 결과이다.

1차 산출물이 raw 파일 단위라면, 2차 산출물은 프로젝트의 지식 구조 단위이다.

예를 들어 1차 산출물 A 안에 다음 내용이 섞여 있을 수 있다.

- 인스턴스 서버 구조
- 던전 A 입장 조건
- 던전 A 보상
- 던전 B 몬스터 스폰

이 경우 2차 산출물은 원본 문서 A라는 단위로 저장되지 않는다. 내용별로 분해되어 `schema.md`가 정의한 폴더와 파일에 저장된다.

예:

```text
db/
  instance_server/
    server_structure.md
    dungeon/
      dungeon_a/
        overview.md
        entry_rules.md
        rewards.md
      dungeon_b/
        spawn_rules.md
```

즉, 1차 산출물 A의 일부 내용이 던전에 관한 것이고 일부 내용이 인스턴스 서버 구조에 관한 것이라면, 서버 구조 내용은 인스턴스 서버 구조 파일에 들어가고 던전 관련 내용은 해당 던전 폴더 아래의 던전 파일에 들어간다.

## schema.md

각 프로젝트는 고유한 `schema.md`를 가질 수 있어야 한다.

`schema.md`는 2차 산출물의 폴더 및 파일 구조를 정의한다.

역할:

- 프로젝트의 지식 저장소 폴더 구조 정의
- 어떤 정보가 어떤 파일에 저장되는지 정의
- 1차 산출물의 내용을 어떻게 분해할지 안내
- 기존 2차 산출물과 신규 내용이 충돌할 때 비교 기준 제공
- 이후 지식 그래프 layer가 참조할 기본 구조 제공

예:

```text
schema.md
db/
  instance_server/
    server_structure.md
    dungeon/
      {dungeon_name}/
        overview.md
        entry_rules.md
        rewards.md
        spawn_rules.md
```

## Conflict Handling

2차 산출물은 기존 DB에 새로운 내용을 추가하거나 기존 내용을 수정할 수 있다.

충돌은 다음을 모두 포함한다.

- 같은 속성값의 충돌
- 규칙 간 충돌
- 용어 정의 충돌
- 테스트 기대값 충돌
- 기존 문서 내용 수정
- 기존 DB 구조와 신규 내용의 위치 충돌

충돌은 git conflict처럼 사람이 조정할 수 있어야 한다.

즉, 시스템은 자동으로 모든 충돌을 해결하지 않는다. 대신 충돌이 발생한 위치, 기존 내용, 신규 내용, 출처를 보여주고 사람이 승인, 거절, 병합, 수정할 수 있게 한다.

## Source Tracking

1차 산출물의 내용은 2차 산출물에서 여러 파일로 흩어진다.

따라서 2차 산출물에는 반드시 출처 추적 정보가 남아야 한다.

예:

```md
# 던전 A 입장 조건

- 최소 레벨: 30
- 파티 인원: 1~4명
- PvP: 불가

## Sources

- instance_server_design.docx > section 3.2
- dungeon_balance.xlsx > DungeonA!B12:E18
```

출처 추적은 다음 기능에 필요하다.

- 충돌 검토
- 변경 영향 분석
- 답변 근거 출력
- 원본 문서 수정 추적
- 사람이 신뢰할 수 있는 검토 흐름

## Knowledge Graph Layers

2차 산출물은 목적별 여러 layer의 지식 그래프로 표현된다.

처음부터 여러 layer를 전제로 설계한다.

예상 layer:

### 1. Document Source Layer

원본 문서, 1차 산출물, 2차 산출물 사이의 출처 관계를 표현한다.

예:

```text
DocumentSpan -[EXTRACTED_TO]-> Processed1Block
Processed1Block -[PLACED_IN]-> Processed2File
Processed2File -[DERIVED_FROM]-> RawDocument
```

### 2. Project Structure Layer

`schema.md`에 의해 정의된 폴더, 파일, 섹션 구조를 표현한다.

예:

```text
Project -[HAS_DOMAIN]-> InstanceServer
InstanceServer -[HAS_DUNGEON]-> Dungeon
Dungeon -[HAS_FILE]-> EntryRules
```

### 3. Domain Concept Layer

게임 도메인의 개념들을 표현한다.

예:

```text
Skill
Item
Character
Zone
Dungeon
Target
Condition
Effect
```

### 4. Rule Layer

조건, 허용, 금지, 효과, 예외 등을 표현한다.

예:

```text
Rule -[APPLIES_WHEN]-> Condition
Rule -[ALLOWS]-> Action
Rule -[DENIES]-> Action
Rule -[PRODUCES]-> Effect
```

### 5. Policy / Intent Layer

상위 기획 의도와 정책을 표현한다.

예:

```text
Fireball -[INTENDED_AS]-> HighRiskAreaSkill
BeginnerZone -[CONSTRAINED_BY]-> LowMistakePenaltyPolicy
Policy -[CONSTRAINS]-> Rule
```

### 6. Test / Validation Layer

조건축, 테스트 케이스, 테스트 공백, 회귀 영향 범위를 표현한다.

예:

```text
TestCase -[COVERS]-> ConditionCombination
RuleChange -[AFFECTS]-> TestCase
ConditionSpace -[HAS_GAP]-> UntestedCombination
```

### 7. Change / Conflict Layer

문서 변경, DB 변경, 충돌, 사람의 조정 이력을 표현한다.

예:

```text
ChangeSet -[MODIFIES]-> Rule
ChangeSet -[CONFLICTS_WITH]-> ExistingRule
HumanDecision -[RESOLVES]-> Conflict
```

## Search And Reasoning Goals

검색은 하나의 방식으로 고정하지 않는다.

목적에 따라 다른 검색 방법과 다른 지식 그래프 layer를 사용한다.

### 1. 조건 기반 가상 테스트

예:

```text
Fireball, Enemy, SafeZone, CooldownReady
=> Cast 거부되어야 함
```

### 2. 조합 폭발 테스트

사람이 놓치기 쉬운 조건 조합을 생성한다.

예:

```text
타겟 없음 + 타격수 0 + PvP Off + 광역 스킬
```

### 3. 회귀 테스트

룰 변경 후 기존 규칙 중 어떤 규칙이 영향을 받는지 찾는다.

### 4. 테스트 공백 탐지

전체 조건축 조합 중 테스트되지 않은 영역을 찾는다.

### 5. 리스크 기반 추천

충돌 가능성이 높은 영역을 추천한다.

예:

```text
이 스킬은 PvP / 안전지역 / 아군 타격 축에서 충돌 가능성이 높음
```

### 6. 변경 영향 분석

변경이 다른 규칙, 테스트, 정책에 주는 영향을 분석한다.

예:

```text
화염볼 범위 증가
=> 멀티 히트 규칙 재검증 필요
```

### 7. 구현 전 기획 결함 발견

기획 단계에서 애매하거나 모순된 내용을 찾는다.

### 8. 정책 위반 발견

상위 의도나 정책에서 벗어나는 변경을 찾는다.

예:

```text
Fireball이 광역 고위험 스킬이라는 의도에서 안전한 범용 스킬로 변질됨
```

### 9. 밸런스 시뮬레이터

특정 룰을 악용하는 전략을 탐색한다.

### 10. 의견 전달

기획 의도에는 맞지만 사용자 경험상 위험한 변화를 설명한다.

예:

```text
의도에는 맞지만, 초보자 영역에서 오인 사용 확률이 증가합니다.
```

### 11. 게임 화면 이해

현재 게임 화면이 어떤 상황인지 파악한다.

### 12. 게임 조작

현재 게임 상황에 맞는 다음 조작을 제시한다.

## Design Direction

초기 설계는 게임 도메인에 강하게 맞춘 구조를 우선한다.

다만, 완전히 게임 전용으로만 닫지 않고 범용 문서 구조와 출처 추적 구조를 함께 둔다.

권장 방향:

```text
게임 특화 구조 70%
범용 구조 30%
```

이렇게 하면 초기 MVP에서 실제 검증 기능을 빠르게 만들 수 있고, 이후 다른 문서 도메인으로 확장할 여지도 남길 수 있다.

## Summary

1차 산출물은 raw 파일을 가공한 문서별 중간 표현이다.

2차 산출물은 `schema.md`에 따라 의미 단위로 분해되고 재조립된 프로젝트별 지식 파일 시스템이다.

2차 산출물은 사람이 읽고 조정할 수 있어야 하며, 기존 DB와의 충돌은 사람이 git conflict처럼 해결할 수 있어야 한다.

이후 2차 산출물은 목적별 여러 layer의 지식 그래프로 표현되어 검색, 검증, 영향 분석, 정책 위반 탐지, 테스트 생성, 밸런스 분석 등에 사용된다.
