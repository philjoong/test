# State Schema (상태이상 스키마)

> 버프/디버프/군중제어/지속효과 등 **엔티티에 부착되는 상태**를 AI가 이해하기 위한 스키마.
> State 는 "동사가 아닌 명사" — 일어난 행동이 아니라 **현재 붙어있는 마커**다.
> 스킬(Effect)은 State 를 **부착/제거/참조**한다. 실제 효과의 수치·지속은 State 가 관리.

---

## 🎯 설계 원칙

1. State 는 **결과물**이다. 스킬(Effect)이 State 를 생성하고, Restriction 이 State 를 조회한다.
2. 한 엔티티에는 **복수의 State 가 동시에** 붙을 수 있다. 동일 State 의 **중첩(stack)** 도 가능.
3. **상태이상끼리의 상호작용**(해제/면역/상쇄)을 원자 단위로 정의한다.
4. State 는 "영구 속성"이 아니다 — 반드시 **생성자(source)** 와 **소멸 조건**을 갖는다.

---

## 1️⃣ 분류 축 (Classification Axes)

### Axis.StateCategory — 상태 카테고리

```yaml
StateCategory:
  - Buff              # 아군성 강화
  - Debuff            # 적군성 약화
  - CrowdControl      # 군중 제어
  - DoT               # 지속 피해 (Damage over Time)
  - HoT               # 지속 회복 (Heal over Time)
  - Shield            # 보호막
  - Aura              # 주변에 영향
  - Transformation    # 변신
  - Marker            # 단순 표식 (플래그)
  - Environmental     # 환경 기인
```

### Axis.Polarity — 긍정/부정 성향

```yaml
Polarity:
  - Positive          # 유익 (해당 엔티티에게)
  - Negative          # 유해
  - Neutral           # 중립
```

### Axis.DispelType — 해제 가능성

```yaml
DispelType:
  - Magic             # 마법 해제 가능
  - Physical          # 물리 해제 가능
  - Poison            # 해독 가능
  - Curse             # 저주 해제 가능
  - Disease           # 질병 치료 가능
  - Enrage            # 격노 해제 가능
  - Undispellable     # 해제 불가
```

### Axis.StackingMode — 중첩 방식

```yaml
StackingMode:
  - NotStackable      # 중첩 불가 (새로 적용 시 덮어쓰기)
  - RefreshDuration   # 재적용 시 지속시간만 갱신
  - AddStack          # 스택 누적 (최대치까지)
  - Independent       # 각 source 별로 독립 적용
  - HighestWins       # 더 강한 것만 유지
```

### Axis.TickType — 틱(주기) 방식

```yaml
TickType:
  - NoTick            # 주기 없음 (지속 적용)
  - Periodic          # 일정 간격 틱 (DoT/HoT)
  - OnEvent           # 특정 이벤트에만 발동
  - Once              # 1회만 발동
```

### Axis.VisibilityType — 표시 방식

```yaml
VisibilityType:
  - Visible           # 아이콘 표시
  - Hidden            # UI 비표시 (내부 태그)
  - OwnerOnly         # 본인에게만 표시
  - AllyOnly          # 아군에게만 표시
```

### Axis.AppliesToAxis — 적용 대상 종류

```yaml
AppliesToAxis:
  - Player
  - Monster
  - Both              # 모든 살아있는 엔티티
  - Environment       # 지형/오브젝트
```

---

## 2️⃣ State 엔티티 전체 속성

```yaml
State:
  # --- 식별 (Identification) ---
  id: string                        # 상태 ID (예: "state.burn")
  name: string                      # 표기명
  version: string

  # --- 분류 ---
  category: StateCategory
  polarity: Polarity
  dispelType: DispelType
  stackingMode: StackingMode
  tickType: TickType
  visibilityType: VisibilityType
  appliesTo: AppliesToAxis

  # --- 시각/표기 ---
  iconId: string
  description: string               # 게임 내 표기 (AI 입력 아님)

  # --- 지속시간 (Duration) ---
  durationType: DurationType        # wiki-skill-schema.md 참조
  baseDuration: number              # 기본 지속시간 (초)
  maxDuration: number               # 상한 (재적용 시)

  # --- 중첩 (Stacking) ---
  stackMax: number                  # 최대 중첩 수
  stackDecayMode: StackDecayMode    # 스택 감소 방식

  # --- 효과 (Effects) ---
  effects: [Effect]                 # wiki-skill-schema.md 참조

  # --- 주기 틱 (Periodic) ---
  tickInterval: number              # 틱 간격 (초, TickType=Periodic 전용)
  tickEffects: [Effect]             # 틱마다 적용되는 효과

  # --- 조건부 발동 ---
  triggerOn: [StateTrigger]

  # --- 면역/저항 부여 ---
  immunitiesGranted: [ImmunityTag]  # 이 상태 중 면역되는 항목

  # --- 해제/소멸 ---
  removeOn: [RemoveCondition]

  # --- 태그/상호작용 ---
  tags: [StateTag]
  interactions: [StateInteraction]

  # --- 우선순위 (같은 자리 경쟁) ---
  priority: number                  # HighestWins/Independent 판정용

  # --- 플래그 ---
  isHarmful: boolean
  isPurgeableByPlayer: boolean      # 플레이어가 자진 해제 가능 여부
```

---

## 3️⃣ StackDecayMode (스택 감소 방식)

```yaml
StackDecayMode:
  - AllAtOnce         # 지속시간 종료 시 전부 소멸
  - OneAtATime        # 주기마다 1스택씩 감소
  - ResetOnRefresh    # 재적용 시 1스택부터 재시작
  - IndependentDecay  # 각 스택이 독립 타이머
```

---

## 4️⃣ StateTrigger (조건부 발동)

> State 가 단순 부착이 아니라 "어떤 순간에" 효과를 내야 할 때.

```yaml
StateTrigger:
  event: StateEvent
  condition: BehaviorCondition      # wiki-entity-monster.md 참조 (optional)
  effect: Effect                    # 발동 시 적용되는 효과

StateEvent:
  - OnApply                         # 부착 시
  - OnRemove                        # 해제 시
  - OnTick                          # 주기적으로
  - OnStackAdded
  - OnStackRemoved
  - OnDamageTaken                   # 피해 받을 때
  - OnDamageDealt
  - OnHeal
  - OnMove
  - OnAttack
  - OnSkillUsed
  - OnDeath
  - OnExpire                        # 지속시간 종료 시
```

**예시 — "5스택 쌓이면 폭발":**

```yaml
triggerOn:
  - event: OnStackAdded
    condition: StackCountAtLeast5
    effect:
      target: Caster
      operation: Subtract
      attribute: HP
      value: 500
      duration: 0
```

---

## 5️⃣ RemoveCondition (소멸 조건)

```yaml
RemoveCondition:
  - OnExpire                        # 시간 만료
  - OnDispel                        # 해제 스킬
  - OnDamageTaken                   # 피해 받음 (수면류)
  - OnMove                          # 이동 시
  - OnSkillUsed                     # 스킬 사용 시
  - OnDeath
  - OnZoneChange                    # 지역 이동 시
  - OnCombatEnd
  - OnOwnerLogout
  - OnSourceDeath                   # 시전자 사망 시
  - OnSourceTooFar                  # 시전자 이탈 시
  - Manual                          # 수동 해제만
```

---

## 6️⃣ StateTag (의미 태그)

> 다른 State/Skill 이 참조하기 좋은 의미 태그.

```yaml
StateTag:
  # --- 속성 ---
  - Element.Fire
  - Element.Ice
  - Element.Lightning
  - Element.Poison
  - Element.Holy
  - Element.Shadow

  # --- 제어 ---
  - CC.Hard                         # 강제 제어 (Stun/Fear 등)
  - CC.Soft                         # 약한 제어 (Slow/Silence)
  - CC.Break                        # 피해 받으면 해제되는 CC

  # --- 기원 ---
  - Origin.Skill
  - Origin.Item
  - Origin.Environment
  - Origin.Quest

  # --- 그룹 ---
  - Group.Blessing                  # 축복 계열 (중첩 제한)
  - Group.Curse
  - Group.Bleed
  - Group.Stance                    # 자세 (하나만 유지)
  - Group.Aura                      # 오라 (하나만 유지)

  # --- 성격 ---
  - Purgeable
  - Stealable                       # 적 버프 탈취 가능
  - Reflectable
```

---

## 7️⃣ StateInteraction (State 간 상호작용)

```yaml
StateInteraction:
  type: StateInteractionType
  withStateId: string               # 상대 State ID
  withTag: string                   # 또는 태그 기반 매칭
  result: InteractionResult         # wiki-skill-schema.md 참조

StateInteractionType:
  - Replaces                        # 적용 시 상대 State 를 대체
  - Cancels                         # 적용 시 상대 State 제거 (상쇄)
  - Prevents                        # 상대 State 가 붙지 못하게
  - Amplifies                       # 상대 State 의 효과 증폭
  - Consumes                        # 상대 State 를 소모하여 다른 효과
  - Transforms                      # 상대 State 를 다른 State 로 변환
```

**예시 — "화상 상태에서 얼음 스킬 맞으면 화상 해제 + 추가 피해":**

```yaml
# state.burn 내부
interactions:
  - type: Consumes
    withTag: Element.Ice
    result:
      additionalEffect:
        target: Caster
        operation: Subtract
        attribute: HP
        value: 200
      blocked: false
```

---

## 8️⃣ 완전한 State 예시

### 예시 1 — Burn (화상, DoT 디버프)

```yaml
State:
  id: state.burn
  name: "Burn"
  version: "1.0.0"

  category: DoT
  polarity: Negative
  dispelType: Magic
  stackingMode: AddStack
  tickType: Periodic
  visibilityType: Visible
  appliesTo: Both

  durationType: OverTime
  baseDuration: 5
  maxDuration: 10
  stackMax: 3
  stackDecayMode: AllAtOnce

  effects: []

  tickInterval: 1
  tickEffects:
    - target: PrimaryTarget
      operation: Subtract
      attribute: HP
      value: 40                     # 스택당 40 (stackMax 까지 누적)
      duration: 0

  triggerOn: []

  immunitiesGranted: []

  removeOn:
    - OnExpire
    - OnDispel
    - OnDeath

  tags:
    - Element.Fire
    - Origin.Skill
    - Group.Bleed
    - Purgeable

  interactions:
    - type: Cancels
      withStateId: state.freeze
      result:
        blocked: false
    - type: Prevents
      withTag: Element.Ice
      result:
        blocked: true

  priority: 10
  isHarmful: true
  isPurgeableByPlayer: false
```

### 예시 2 — Arcane Power (스택형 공격력 버프)

```yaml
State:
  id: state.arcane_power
  name: "Arcane Power"
  version: "1.0.0"

  category: Buff
  polarity: Positive
  dispelType: Magic
  stackingMode: AddStack
  tickType: NoTick
  visibilityType: Visible
  appliesTo: Player

  durationType: OverTime
  baseDuration: 15
  maxDuration: 15
  stackMax: 5
  stackDecayMode: ResetOnRefresh

  effects:
    - target: Caster
      operation: Multiply
      attribute: spellPower
      value: 1.05                   # 스택당 5%
      duration: 0                   # State 와 동기화

  tickInterval: 0
  tickEffects: []

  triggerOn:
    - event: OnStackAdded
      effect:
        target: Caster
        operation: AddState
        attribute: State
        value: state.arcane_visual
        duration: 15

  immunitiesGranted: []

  removeOn:
    - OnExpire
    - OnDispel
    - OnDeath
    - OnZoneChange

  tags:
    - Origin.Skill
    - Group.Blessing
    - Stealable

  interactions: []
  priority: 5
  isHarmful: false
  isPurgeableByPlayer: true
```

### 예시 3 — Stun (군중 제어, CC)

```yaml
State:
  id: state.stun
  name: "Stunned"
  version: "1.0.0"

  category: CrowdControl
  polarity: Negative
  dispelType: Undispellable
  stackingMode: RefreshDuration
  tickType: NoTick
  visibilityType: Visible
  appliesTo: Both

  durationType: OverTime
  baseDuration: 2
  maxDuration: 4
  stackMax: 1
  stackDecayMode: AllAtOnce

  effects:
    - target: PrimaryTarget
      operation: AddState
      attribute: State
      value: ControlState.Stunned
      duration: 0                   # State 동기화

  tickInterval: 0
  tickEffects: []

  triggerOn: []
  immunitiesGranted: []

  removeOn:
    - OnExpire
    - OnDeath

  tags:
    - CC.Hard
    - Origin.Skill

  interactions:
    - type: Prevents
      withTag: CC.Hard              # 스턴 중엔 다른 하드 CC 불가 (DR 효과)
      result:
        durationMultiplier: 0.5
    - type: Cancels
      withStateId: state.sleep
      result:
        blocked: false

  priority: 100                     # 높을수록 우선
  isHarmful: true
  isPurgeableByPlayer: false
```

### 예시 4 — Divine Shield (무적)

```yaml
State:
  id: state.invulnerable
  name: "Invulnerable"
  version: "1.0.0"

  category: Shield
  polarity: Positive
  dispelType: Undispellable
  stackingMode: NotStackable
  tickType: NoTick
  visibilityType: Visible
  appliesTo: Both

  durationType: OverTime
  baseDuration: 8
  maxDuration: 8
  stackMax: 1
  stackDecayMode: AllAtOnce

  effects: []

  tickInterval: 0
  tickEffects: []

  triggerOn:
    - event: OnDamageTaken
      effect:
        target: Caster
        operation: Set
        attribute: Damage
        value: 0                    # 모든 피해 무효
        duration: 0

  immunitiesGranted:
    - CC.Stun
    - CC.Silence
    - CC.Root
    - CC.Fear
    - CC.Charm
    - Damage.True

  removeOn:
    - OnExpire
    - Manual

  tags:
    - Origin.Skill
    - Group.Blessing

  interactions:
    - type: Prevents
      withTag: CC.Hard
      result:
        blocked: true

  priority: 200
  isHarmful: false
  isPurgeableByPlayer: true
```

---

## 9️⃣ 불변식 (Invariants)

```yaml
Invariant:
  - rule: "polarity=Positive 이면 isHarmful=false 이어야 함"
  - rule: "category=CrowdControl 이면 tags 에 CC.* 태그 최소 1개 있어야 함"
  - rule: "category=DoT 이면 tickType=Periodic, tickEffects 에 Subtract+HP 가 있어야 함"
  - rule: "category=HoT 이면 tickType=Periodic, tickEffects 에 Add+HP 가 있어야 함"
  - rule: "tickType=Periodic 이면 tickInterval > 0, tickEffects 비어있지 않아야 함"
  - rule: "stackingMode=NotStackable 이면 stackMax=1 이어야 함"
  - rule: "stackingMode=AddStack 이면 stackMax >= 2 이어야 함"
  - rule: "dispelType=Undispellable 이면 removeOn 에 OnDispel 포함 불가"
  - rule: "baseDuration > maxDuration 이면 안 됨"
  - rule: "durationType=Instant 이면 category 가 Marker/Environmental 이어야 함"
  - rule: "immunitiesGranted 가 비어있지 않으면 polarity=Positive 이어야 함 (면역은 항상 유익)"
  - rule: "appliesTo=Environment 이면 interactions 가 다른 Environmental State 만 참조해야 함"
  - rule: "interactions[].withStateId 는 실존 State 이어야 함"
```

---

## 🔗 관련 문서

- [wiki-schema-guide.md](wiki-schema-guide.md) — 스키마 설계 철학
- [wiki-skill-schema.md](wiki-skill-schema.md) — Skill 엔티티 (State 를 생성/참조)
- [wiki-entity-player.md](wiki-entity-player.md) — Player 엔티티 (State 가 부착되는 대상)
- [wiki-entity-monster.md](wiki-entity-monster.md) — Monster 엔티티 (State 가 부착되는 대상)
- [wiki-entity-zone.md](wiki-entity-zone.md) — Zone 엔티티 (Environmental State 의 원천)
- [wiki-entity-item.md](wiki-entity-item.md) — 아이템 사용/장착 시 부여되는 State
- [wiki-entity-interaction.md](wiki-entity-interaction.md) — Interaction.sideEffects 로 State 제거/부여
- [wiki-entity-quest.md](wiki-entity-quest.md) — 퀘스트가 부여/소모하는 State
- [wiki-entity-ui.md](wiki-entity-ui.md) — 버프/디버프 표시 HUD
- [wiki-entity-session.md](wiki-entity-session.md) — Session 전환 시 State 소실
