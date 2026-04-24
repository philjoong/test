AI가 생각할 수 있는 형식으로 게임을 모델링한다

***

# ✅ 한 문장 핵심 요약

**AI가 게임을 이해하려면,  
게임을 “상태(State) + 규칙(Rule) + 결과(Effect)”의 집합으로 표현해야 한다.**

***

## 1️⃣ AI가 게임을 이해하기 위해 꼭 필요한 5가지 구성요소

AI는 최소한 아래 5가지를 필요로 합니다.

    1. 엔티티(Entity)    : 누가 / 무엇이 존재하는가
    2. 상태(State)       : 지금 어떤 상태인가
    3. 행위(Action)      : 무엇을 할 수 있는가
    4. 규칙(Rule)        : 언제 가능하고 어떻게 변하는가
    5. 결과(Effect)      : 그 결과로 무엇이 바뀌는가

이게 **AI의 사고 단위**입니다.

***

## 2️⃣ 1단계: 엔티티를 명확히 정의하기 (누가 등장하는가)

### ❌ 안 좋은 예

> 플레이어, 적, 몬스터

### ✅ AI가 이해하기 좋은 예

```yaml
Entity:
  Player:
    properties: [HP, Mana, Position, Faction, States]
  Monster:
    properties: [HP, Aggro, Position, Species]
  Skill:
    properties: [Cooldown, Range, Area, TargetType]
  Zone:
    properties: [IsSafeZone, PvPAllowed]
```

***

## 3️⃣ 2단계: 상태(State)를 축(axis)으로 정리하기

이게 제일 중요합니다.

### ✅ 상태는 반드시 **분리된 축**이어야 함

```text
CasterState:
- CooldownReady
- CooldownNotReady
- Silenced
- InSafeZone

TargetState:
- Enemy
- Ally
- Monster
- None

Environment:
- PvPAllowed
- PvPForbidden
```

👉 **절대 하지 말 것**

*   “안전지역에서 쿨타임 안 찬 상태의 플레이어” 같은 문장형 상태

👉 **항상 이렇게**

*   상태는 원자 단위
*   조합은 나중에

***

## 4️⃣ 3단계: 행동(Action)을 “질의 가능”하게 만들기

AI에게 행동은 **질문**입니다.

```json
Action:
{
  "type": "UseSkill",
  "skill": "Fireball",
  "caster": "PlayerA",
  "target": "EnemyB"
}
```

이렇게 되면 AI는 이렇게 질문할 수 있습니다:

> “이 상태에서 이 행동이 가능한가?”

***

## 5️⃣ 4단계: 규칙을 “IF–THEN”이 아니라 “결정 규칙”으로

### ❌ 코드식 사고 (사람용)

```cpp
if (cooldownReady && !safeZone && target == enemy)
```

### ✅ AI식 사고 (규칙 기반)

```yaml
Rule:
  name: Fireball_Use_Restriction
  priority: 1
  condition:
    - InSafeZone == true
  result:
    CastAllowed: false
    Reason: SafeZone
```

```yaml
Rule:
  name: Fireball_Enemy_Hit
  priority: 5
  condition:
    - TargetType == Enemy
    - HitCount >= 1
  result:
    Damage: 100
    Burn: true
```

***

## 6️⃣ 5단계: 결과(Effect)는 “상태 변화”로 표현

AI는 수치를 좋아하지만  
**상태 변화는 더 좋아합니다.**

```yaml
Effect:
  - HP -= 120
  - State += Burn(5s)
```

***

## 7️⃣ 그래서 실제로 AI에게 줄 최소 표현 템플릿

아래 정도면 **AI가 테스트·질의·추천**까지 가능합니다.

```yaml
GameModel:
  Entities:
    Player
    Monster
    Skill
    Zone

  States:
    CasterState:
      - CooldownReady
      - CooldownNotReady
      - InSafeZone
    TargetType:
      - Enemy
      - Ally
      - Monster
      - None

  Actions:
    - UseSkill

  Rules:
    - name: NoCastInSafeZone
      priority: 1
      condition: InSafeZone
      result: CastAllowed=false

    - name: FireballEnemy
      priority: 5
      condition: TargetType=Enemy
      result: Damage=100, Burn=true
```

***
