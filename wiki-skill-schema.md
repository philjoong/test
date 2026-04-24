# Skill Schema (스킬 스키마)

> AI가 스킬을 "상태(State) + 규칙(Rule) + 결과(Effect)"로 이해하기 위한 스키마 문서.
> 모든 스킬은 아래 **분류 축(Classification Axes)** 의 조합으로 표현된다.
> 스킬은 문장이 아니라 **태그의 집합**으로 정의한다.

---

## 🎯 설계 원칙

1. **모든 속성은 원자 단위**로 분리한다 (조합은 AI가 한다).
2. **enum 값은 고정**한다 (AI가 허용된 값만 선택하도록).
3. **문장형 설명 금지**, 태그와 값으로만 표현한다.
4. **누락된 축 = Unknown**이 아니라 명시적 기본값을 갖는다.
5. 하나의 스킬은 **여러 축의 값을 동시에** 가진다 (직교 분류).

---

## 1️⃣ 분류 축 (Classification Axes)

스킬을 구분하는 모든 축을 나열한다. AI는 이 축들의 조합으로 스킬을 이해한다.

### Axis.ActivationType — 발동 방식

```yaml
ActivationType:
  - Active          # 사용자가 능동적으로 발동
  - Passive         # 조건 충족 시 자동 발동 또는 상시 효과
  - Toggle          # 켜고 끄는 방식, 지속 자원 소모
  - Triggered       # 특정 이벤트(피격, 처치 등)에 반응하여 발동
  - Channeled       # 사용 중 유지해야 효과 지속
```

### Axis.TargetingMode — 타겟팅 방식

```yaml
TargetingMode:
  - Targeted        # 특정 대상을 지정해야 발동
  - NonTargeted     # 대상 지정 없이 발동 (위치/방향 기반)
  - SelfCast        # 시전자 자신에게만 적용
  - GroundTargeted  # 지면 좌표를 지정
  - DirectionSkillshot  # 방향만 지정 (투사체 등)
  - AutoTarget      # 시스템이 자동 선정
```

### Axis.AreaType — 영향 범위

```yaml
AreaType:
  - SingleTarget    # 단일 대상
  - MultiTarget     # 지정된 N개 대상
  - AreaOfEffect    # 광역 (원/사각/원뿔)
  - Line            # 직선 경로상 대상
  - Chain           # 튕겨나가며 연쇄
  - Global          # 맵 전체
```

### Axis.TargetFaction — 대상 진영

```yaml
TargetFaction:
  - Enemy           # 적군만
  - Ally            # 아군만
  - Self            # 자신만
  - Neutral         # 중립 대상
  - Any             # 진영 무관
  - None            # 대상 없음 (환경/지형 대상)
```

### Axis.EffectCategory — 효과 성격

```yaml
EffectCategory:
  - Damage          # 피해
  - Heal            # 회복
  - Buff            # 아군 강화
  - Debuff          # 적군 약화
  - CrowdControl    # 군중 제어 (스턴/넉백/속박 등)
  - Shield          # 보호막
  - Mobility        # 이동 (돌진/순간이동)
  - Summon          # 소환
  - Resource        # 자원 조작 (마나/쿨다운)
  - Utility         # 기타 (은신/감지/텔레포트 등)
```

### Axis.DamageType — 피해 속성 (EffectCategory.Damage 일 때만)

```yaml
DamageType:
  - Physical
  - Magical
  - True            # 방어 무시
  - Fire
  - Ice
  - Lightning
  - Poison
  - Holy
  - Shadow
  - None            # 피해 없음
```

### Axis.ControlType — 군중 제어 종류 (EffectCategory.CrowdControl 일 때만)

```yaml
ControlType:
  - Stun            # 행동 불가
  - Silence         # 스킬 사용 불가
  - Root            # 이동 불가
  - Slow            # 이동 감속
  - Knockback       # 밀어냄
  - Pull            # 끌어당김
  - Airborne        # 공중에 띄움
  - Fear            # 역방향 강제 이동
  - Sleep           # 피격 시 해제되는 기절
  - Charm           # 시전자 편으로 조작
  - None
```

### Axis.DurationType — 지속성

```yaml
DurationType:
  - Instant         # 즉발
  - OverTime        # 지속 효과 (DoT/HoT)
  - Permanent       # 영구 효과 (해제 전까지)
  - UntilDispelled  # 해제 스킬로만 제거
  - UntilDeath      # 사망 시까지
```

### Axis.InterruptibleState — 방해 가능 여부

```yaml
InterruptibleState:
  - Interruptible       # CC/피격으로 취소됨
  - Uninterruptible     # 슈퍼아머, 방해 불가
  - CancelOnMove        # 이동 시 취소
```

### Axis.RangeCategory — 사거리

```yaml
RangeCategory:
  - Melee           # 근접 (<= 3m)
  - Short           # 근거리 (3~8m)
  - Medium          # 중거리 (8~20m)
  - Long            # 원거리 (20~40m)
  - Extreme         # 초장거리 (40m+)
  - Infinite        # 맵 전역
```

### Axis.ResourceType — 소모 자원

```yaml
ResourceType:
  - Mana
  - Stamina
  - Rage
  - Energy
  - Health
  - Charges         # 스택/충전 소모
  - Cooldown        # 시간만 소모
  - Free            # 자원 없음
```

---

## 2️⃣ 스킬 엔티티 속성 (Skill Entity Properties)

하나의 스킬 인스턴스가 가져야 할 전체 속성.

```yaml
Skill:
  # --- 식별 (Identification) ---
  id: string                    # 고유 ID (예: "skill.fireball")
  name: string                  # 표기명
  version: string               # 버전 (밸런스 패치 추적용)

  # --- 분류 태그 (모든 축의 값) ---
  activationType: ActivationType
  targetingMode: TargetingMode
  areaType: AreaType
  targetFaction: TargetFaction
  effectCategory: [EffectCategory]   # 복수 가능 (예: Damage + Debuff)
  damageType: DamageType             # EffectCategory가 Damage일 때만 의미
  controlType: ControlType           # EffectCategory가 CrowdControl일 때만 의미
  durationType: DurationType
  interruptibleState: InterruptibleState
  rangeCategory: RangeCategory
  resourceType: ResourceType

  # --- 수치 (Numeric Attributes) ---
  cooldown: number              # 쿨다운 (초)
  castTime: number              # 시전 시간 (초, 0=즉발)
  channelDuration: number       # 채널링 시간 (Channeled 전용)
  range: number                 # 실제 사거리 (m)
  areaRadius: number            # 광역 반경 (m, AreaOfEffect 전용)
  resourceCost: number          # 자원 소모량
  chargesMax: number            # 최대 충전 수
  chargeRegenTime: number       # 충전 회복 시간 (초)

  # --- 효과 목록 (Effects) ---
  effects: [Effect]             # 시전 시 적용되는 효과들

  # --- 사용 제약 (Restrictions) ---
  restrictions: [Restriction]   # 사용 금지 조건들

  # --- 상호작용 (Interactions) ---
  interactions: [Interaction]   # 다른 스킬/상태와의 상호작용
```

---

## 3️⃣ 사용 제약 (Restrictions) — AI가 가장 먼저 검사하는 부분

> QA 관점에서 **가장 버그가 많이 나는 영역**이므로 원자적으로 분리한다.

```yaml
Restriction:
  condition: RestrictionCondition   # 어떤 조건일 때
  allowed: boolean                  # 허용(true) 또는 금지(false)
  reason: string                    # 금지 사유 태그 (사람용 설명 아님)
  priority: number                  # 낮을수록 먼저 평가 (1이 최우선)

RestrictionCondition:
  # --- 환경 조건 ---
  - InSafeZone          # 안전지역 안
  - InPvPZone           # PvP 허용 지역
  - InDungeon           # 던전 내부
  - InWater             # 수중
  - InCombat            # 전투 중
  - OutOfCombat         # 비전투

  # --- 시전자 상태 ---
  - Silenced            # 침묵 상태
  - Stunned             # 기절
  - Rooted              # 속박
  - Mounted             # 탑승 중
  - Stealthed           # 은신 중

  # --- 대상 상태 ---
  - TargetIsAlly
  - TargetIsEnemy
  - TargetIsDead
  - TargetIsInvulnerable
  - TargetOutOfSight    # 시야 밖

  # --- 자원 ---
  - CooldownReady
  - CooldownNotReady
  - ResourceSufficient
  - ResourceInsufficient

  # --- 복합 ---
  - Always              # 항상
  - Never               # 절대
```

**예시:**

```yaml
restrictions:
  - condition: InSafeZone
    allowed: false
    reason: SafeZoneRestriction
    priority: 1

  - condition: Silenced
    allowed: false
    reason: CasterSilenced
    priority: 2

  - condition: CooldownNotReady
    allowed: false
    reason: OnCooldown
    priority: 3
```

---

## 4️⃣ 효과 (Effect) — 상태 변화의 원자 단위

> 효과는 반드시 **"무엇이 얼마나 어떻게 변하는가"** 세 가지로 분리한다.

```yaml
Effect:
  target: EffectTarget          # 누구에게
  operation: EffectOperation    # 어떤 연산
  attribute: EffectAttribute    # 어떤 속성을
  value: number | string        # 얼마만큼
  duration: number              # 지속시간 (초, 0=즉시)
  stackable: boolean            # 중첩 가능 여부
  stackMax: number              # 최대 중첩 수
  dispellable: boolean          # 해제 가능 여부
  condition: RestrictionCondition  # 발동 조건 (optional)

EffectTarget:
  - Caster              # 시전자
  - PrimaryTarget       # 1차 대상
  - SecondaryTargets    # 광역 내 추가 대상
  - AllEnemiesInArea
  - AllAlliesInArea
  - Ground              # 지면에 설치
  - Global              # 전역

EffectOperation:
  - Set                 # 값 대입
  - Add                 # 더하기
  - Subtract            # 빼기
  - Multiply            # 곱하기
  - AddState            # 상태 부여
  - RemoveState         # 상태 제거
  - Trigger             # 다른 스킬/이벤트 발동

EffectAttribute:
  - HP
  - Mana
  - Stamina
  - MoveSpeed
  - AttackSpeed
  - AttackPower
  - Defense
  - CritChance
  - State               # 상태 이상 (Burn/Freeze 등)
  - Position            # 위치 (이동/텔레포트)
  - Cooldown
  - Resource
```

**예시:**

```yaml
effects:
  - target: PrimaryTarget
    operation: Subtract
    attribute: HP
    value: 120
    duration: 0

  - target: PrimaryTarget
    operation: AddState
    attribute: State
    value: Burn
    duration: 5
    stackable: true
    stackMax: 3
    dispellable: true
```

---

## 5️⃣ 상호작용 (Interactions) — 다른 스킬/상태와의 관계

```yaml
Interaction:
  type: InteractionType
  withTag: string               # 상대방의 태그 또는 스킬 ID
  result: InteractionResult

InteractionType:
  - AmplifiedBy         # ~에 의해 증폭
  - DiminishedBy        # ~에 의해 약화
  - NullifiedBy         # ~에 의해 무효화
  - Triggers            # ~를 발동시킴
  - Consumes            # ~를 소모함
  - RequiresState       # ~ 상태를 요구

InteractionResult:
  damageMultiplier: number
  durationMultiplier: number
  additionalEffect: Effect
  blocked: boolean
```

**예시 — "화염볼은 얼음 상태의 적에게 2배 피해"**

```yaml
interactions:
  - type: AmplifiedBy
    withTag: TargetHasState.Frozen
    result:
      damageMultiplier: 2.0
```

---

## 6️⃣ 추상화된 스킬 타입 (Archetypes)

> 위의 축 조합으로 만들어지는 **대표 패턴**. AI는 새 스킬이 어느 원형에 속하는지로 빠르게 분류할 수 있다.

```yaml
Archetype:
  # --- 액티브 계열 ---
  - SingleTargetActive      # Active + Targeted + SingleTarget + Enemy + Damage
  - AoEActive               # Active + (GroundTargeted|NonTargeted) + AreaOfEffect + Enemy + Damage
  - SkillshotActive         # Active + DirectionSkillshot + (Line|Chain) + Enemy + Damage
  - SingleTargetHeal        # Active + Targeted + SingleTarget + Ally + Heal
  - AoEHeal                 # Active + (SelfCast|GroundTargeted) + AreaOfEffect + Ally + Heal
  - SingleTargetBuff        # Active + Targeted + SingleTarget + Ally + Buff
  - AoEBuff                 # Active + AreaOfEffect + Ally + Buff
  - SingleTargetDebuff      # Active + Targeted + SingleTarget + Enemy + Debuff
  - AoEDebuff               # Active + AreaOfEffect + Enemy + Debuff
  - SingleTargetCC          # Active + Targeted + SingleTarget + Enemy + CrowdControl
  - AoECC                   # Active + AreaOfEffect + Enemy + CrowdControl
  - SelfBuff                # Active + SelfCast + Self + Buff
  - SelfShield              # Active + SelfCast + Self + Shield
  - MobilitySkill           # Active + (SelfCast|GroundTargeted) + Self + Mobility
  - SummonSkill             # Active + (SelfCast|GroundTargeted) + Summon
  - UtilityActive           # Active + * + Utility (은신/텔레포트/감지 등)

  # --- 패시브 계열 ---
  - StatPassive             # Passive + SelfCast + Buff (스탯 상시 증가)
  - TriggeredPassive        # Triggered + 이벤트 반응 (피격 시 반격 등)
  - AuraPassive             # Passive + AreaOfEffect + Ally + Buff (주변 아군 버프)

  # --- 토글 계열 ---
  - ToggleStance            # Toggle + SelfCast + Self + Buff
  - ToggleAura              # Toggle + AreaOfEffect + (Ally|Enemy)

  # --- 채널링 계열 ---
  - ChanneledBeam           # Channeled + DirectionSkillshot + Line + Enemy + Damage
  - ChanneledAoE            # Channeled + AreaOfEffect + Enemy + Damage
  - ChanneledHeal           # Channeled + Targeted + Ally + Heal
```

---

## 7️⃣ 완전한 스킬 예시 (Full Skill Examples)

### 예시 1 — Fireball (단일 대상 액티브 공격)

```yaml
Skill:
  id: skill.fireball
  name: Fireball
  version: "1.0.0"

  activationType: Active
  targetingMode: Targeted
  areaType: SingleTarget
  targetFaction: Enemy
  effectCategory: [Damage, Debuff]
  damageType: Fire
  controlType: None
  durationType: OverTime
  interruptibleState: Interruptible
  rangeCategory: Medium
  resourceType: Mana

  cooldown: 6
  castTime: 1.2
  channelDuration: 0
  range: 18
  areaRadius: 0
  resourceCost: 40
  chargesMax: 1
  chargeRegenTime: 0

  archetype: SingleTargetActive

  restrictions:
    - condition: InSafeZone
      allowed: false
      reason: SafeZoneRestriction
      priority: 1
    - condition: Silenced
      allowed: false
      reason: CasterSilenced
      priority: 2
    - condition: CooldownNotReady
      allowed: false
      reason: OnCooldown
      priority: 3
    - condition: ResourceInsufficient
      allowed: false
      reason: NotEnoughMana
      priority: 4

  effects:
    - target: PrimaryTarget
      operation: Subtract
      attribute: HP
      value: 120
      duration: 0
    - target: PrimaryTarget
      operation: AddState
      attribute: State
      value: Burn
      duration: 5
      stackable: true
      stackMax: 3
      dispellable: true

  interactions:
    - type: AmplifiedBy
      withTag: TargetHasState.Oiled
      result:
        damageMultiplier: 1.5
    - type: NullifiedBy
      withTag: TargetHasState.FireImmune
      result:
        blocked: true
```

### 예시 2 — Meteor (광역 논타겟팅 공격)

```yaml
Skill:
  id: skill.meteor
  name: Meteor
  version: "1.0.0"

  activationType: Active
  targetingMode: GroundTargeted
  areaType: AreaOfEffect
  targetFaction: Enemy
  effectCategory: [Damage, CrowdControl]
  damageType: Fire
  controlType: Knockback
  durationType: Instant
  interruptibleState: Interruptible
  rangeCategory: Long
  resourceType: Mana

  cooldown: 30
  castTime: 3.0
  channelDuration: 0
  range: 35
  areaRadius: 8
  resourceCost: 120

  archetype: AoEActive

  restrictions:
    - condition: InSafeZone
      allowed: false
      reason: SafeZoneRestriction
      priority: 1
    - condition: InPvPZone
      allowed: true
      reason: PvPAllowed
      priority: 2

  effects:
    - target: AllEnemiesInArea
      operation: Subtract
      attribute: HP
      value: 400
    - target: AllEnemiesInArea
      operation: AddState
      attribute: State
      value: Knockback
      duration: 1
      dispellable: false
```

### 예시 3 — Divine Shield (자기 대상 방어 버프)

```yaml
Skill:
  id: skill.divine_shield
  name: Divine Shield
  version: "1.0.0"

  activationType: Active
  targetingMode: SelfCast
  areaType: SingleTarget
  targetFaction: Self
  effectCategory: [Shield, Buff]
  damageType: None
  controlType: None
  durationType: OverTime
  interruptibleState: Uninterruptible
  rangeCategory: Melee
  resourceType: Cooldown

  cooldown: 120
  castTime: 0
  range: 0
  resourceCost: 0

  archetype: SelfShield

  restrictions:
    - condition: CooldownNotReady
      allowed: false
      reason: OnCooldown
      priority: 1

  effects:
    - target: Caster
      operation: AddState
      attribute: State
      value: Invulnerable
      duration: 8
      stackable: false
      dispellable: false
```

### 예시 4 — Thorns (패시브 반격)

```yaml
Skill:
  id: skill.thorns
  name: Thorns
  version: "1.0.0"

  activationType: Triggered
  targetingMode: AutoTarget
  areaType: SingleTarget
  targetFaction: Enemy
  effectCategory: [Damage]
  damageType: Physical
  durationType: Instant
  interruptibleState: Uninterruptible
  rangeCategory: Melee
  resourceType: Free

  cooldown: 0
  castTime: 0
  range: 3
  resourceCost: 0

  archetype: TriggeredPassive

  restrictions:
    - condition: Always
      allowed: true
      reason: PassiveAlwaysActive
      priority: 1

  effects:
    - target: PrimaryTarget
      operation: Subtract
      attribute: HP
      value: 30
      condition: OnMeleeHitReceived
```

---

## 8️⃣ AI 질의 템플릿 (Query Templates)

> AI가 이 스키마로 대답할 수 있는 질문들.

```yaml
Query:
  # --- 단일 스킬 검증 ---
  - "이 스킬은 SafeZone에서 사용 가능한가?"
    → restrictions 에서 condition=InSafeZone 찾아서 allowed 확인

  - "이 스킬의 최대 DPS는?"
    → effects 의 Damage 합계 / cooldown

  # --- 조합 탐색 ---
  - "targetFaction=Ally + effectCategory=Damage 인 스킬 있는가?"
    → 모순 조합 탐지 (아군을 공격하는 스킬)

  - "areaType=Global + targetFaction=Enemy 인 스킬 목록"
    → 밸런스 리스크 스킬 추출

  # --- 회귀 테스트 ---
  - "damageType=Fire 인 모든 스킬"
    → 화염 저항 변경 시 영향받는 스킬 목록

  - "InSafeZone restriction 이 없는 Damage 스킬"
    → 안전지역 규칙 누락 스킬 탐지

  # --- 커버리지 분석 ---
  - "archetype 별 스킬 수"
    → 특정 원형 결손 탐지

  - "interactions 가 비어있는 스킬"
    → 조합 설계 공백 탐지
```

---

## 9️⃣ 유효성 불변식 (Invariants)

> 모든 스킬이 반드시 만족해야 하는 규칙. AI는 이걸 어긴 스킬을 **설계 결함**으로 리포트한다.

```yaml
Invariant:
  - rule: "effectCategory 에 Damage 가 있으면 damageType 은 None 이 아니어야 함"
  - rule: "effectCategory 에 CrowdControl 이 있으면 controlType 은 None 이 아니어야 함"
  - rule: "activationType=Passive 이면 cooldown=0 이고 resourceCost=0 이어야 함"
  - rule: "activationType=Channeled 이면 channelDuration > 0 이어야 함"
  - rule: "areaType=AreaOfEffect 이면 areaRadius > 0 이어야 함"
  - rule: "targetingMode=SelfCast 이면 targetFaction=Self 이어야 함"
  - rule: "targetingMode=NonTargeted 이면 areaType 은 SingleTarget 이 아니어야 함"
  - rule: "resourceType=Free 이면 resourceCost=0 이어야 함"
  - rule: "모든 restriction 은 고유한 priority 를 가져야 함"
  - rule: "durationType=OverTime 이면 effects 중 duration > 0 인 항목이 있어야 함"
```

---

## 🔗 관련 문서

- [wiki-schema-guide.md](wiki-schema-guide.md) — 스키마 설계 철학
- [wiki-entity-player.md](wiki-entity-player.md) — Player 엔티티 (스킬 시전자/대상)
- [wiki-entity-monster.md](wiki-entity-monster.md) — Monster 엔티티 (스킬 시전자/대상)
- [wiki-entity-zone.md](wiki-entity-zone.md) — Zone 엔티티 (InSafeZone 등 Restriction 참조원)
- [wiki-entity-state.md](wiki-entity-state.md) — State(상태이상) 엔티티 (Effect.AddState 의 대상)
- [wiki-entity-item.md](wiki-entity-item.md) — Item 이 부여하는 스킬 / 소모품 스킬
- [wiki-entity-interaction.md](wiki-entity-interaction.md) — Effect 구조를 공유하는 절차적 행위
- [wiki-entity-ui.md](wiki-entity-ui.md) — 스킬바/쿨다운 HUD
- [wiki-entity-quest.md](wiki-entity-quest.md) — UseSkill 목표에 참조됨
- [wiki-entity-session.md](wiki-entity-session.md) — 파티 시너지/버프
