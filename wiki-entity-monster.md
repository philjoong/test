# Monster Schema (몬스터 스키마)

> 몬스터(NPC 적대 개체)를 AI가 "상태 + 규칙 + 결과"로 이해하기 위한 스키마.
> Player 와 겹치는 속성은 **동일한 축**을 재사용하고, 몬스터 고유 개념만 추가한다.

---

## 🎯 설계 원칙

1. 몬스터는 **행동 주체(Agent)** 이므로 "AI 행동 규칙(BehaviorRule)" 을 반드시 갖는다.
2. 플레이어와 **같은 상태 축**(LifeState, ControlState 등)은 재사용한다.
3. 몬스터 고유 축(Species, Rank, AggroState, SpawnState)은 별도로 정의한다.
4. **개체(instance)** 와 **원형(template)** 을 구분한다. 같은 원형에서 여러 개체가 생성됨.

---

## 1️⃣ 분류 축 (Classification Axes)

### Axis.Species — 종족

```yaml
Species:
  - Humanoid
  - Beast
  - Undead
  - Demon
  - Dragon
  - Elemental
  - Construct
  - Aberration
  - Plant
  - Insect
```

### Axis.Rank — 등급

```yaml
Rank:
  - Trash             # 잡몹
  - Normal            # 일반
  - Elite             # 정예
  - Rare              # 희귀
  - Champion          # 네임드 챔피언
  - MiniBoss          # 중간 보스
  - Boss              # 보스
  - RaidBoss          # 공격대 보스
  - WorldBoss         # 월드 보스
```

### Axis.BehaviorType — 기본 행동 성향

```yaml
BehaviorType:
  - Passive           # 공격받기 전까지 공격 안 함
  - Defensive         # 영역 침범 시 공격
  - Aggressive        # 시야 내 적 즉시 공격
  - Territorial       # 영역 벗어나면 귀환
  - Pack              # 무리 단위 행동
  - Caster            # 원거리 주문 위주
  - Tank              # 방어 위주
  - Berserker         # 체력 낮을수록 강해짐
```

### Axis.AggroState — 어그로 상태

```yaml
AggroState:
  - Idle              # 무관심
  - Alerted           # 경계 (탐지 감지)
  - Engaged           # 전투 교전 중
  - Searching         # 타겟 유실, 탐색 중
  - Returning         # 영역 귀환 중
  - Leashed           # 어그로 해제됨
```

### Axis.SpawnState — 생성 상태

```yaml
SpawnState:
  - NotSpawned        # 스폰 전
  - Spawning          # 생성 중 (연출)
  - Alive
  - Dying             # 사망 연출 중
  - Dead
  - Despawning        # 소멸 중
  - Respawning        # 리스폰 대기
```

### Axis.LootState — 전리품 상태

```yaml
LootState:
  - Unlooted
  - Locked            # 다른 파티 소유
  - Tapped            # 소유권 확정
  - Looted            # 획득 완료
  - Decayed           # 시간 초과로 소멸
```

> LifeState / CombatState / MovementState / ControlState / VisibilityState 는
> [wiki-entity-player.md](wiki-entity-player.md) 의 정의를 그대로 재사용한다.

---

## 2️⃣ Monster 엔티티 전체 속성

```yaml
Monster:
  # --- 식별 (Identification) ---
  id: string                        # 개체 인스턴스 ID
  templateId: string                # 원형 ID (예: "monster.goblin_warrior")
  name: string                      # 표기명

  # --- 분류 ---
  species: Species
  rank: Rank
  behaviorType: BehaviorType
  faction: string                   # 진영 태그 (예: "faction.undead")

  # --- 성장/난이도 (Difficulty) ---
  level: number
  difficultyTier: number            # 1(쉬움)~10(매우 어려움)
  experienceReward: number
  goldReward: number

  # --- 생명/자원 ---
  hp: number
  hpMax: number
  mana: number
  manaMax: number

  # --- 전투 스탯 ---
  attackPower: number
  spellPower: number
  defense: number
  magicResist: number
  critChance: number
  attackSpeed: number
  moveSpeed: number

  # --- 저항 (Resistances) ---
  resistances: [DamageResistance]

  # --- 면역 (Immunities) ---
  immunities: [ImmunityTag]

  # --- 동적 상태 ---
  lifeState: LifeState
  spawnState: SpawnState
  aggroState: AggroState
  combatState: CombatState
  movementState: MovementState
  controlState: [ControlState]
  visibilityState: VisibilityState
  lootState: LootState

  # --- 상태 이상 ---
  buffs: [StatusEffect]
  debuffs: [StatusEffect]

  # --- 위치/영역 (Territory) ---
  position: Vector3
  rotation: number
  zoneId: string
  spawnPoint: Vector3               # 원래 스폰 위치
  leashRange: number                # 이 거리 벗어나면 귀환 (m)
  aggroRange: number                # 시야/탐지 거리 (m)

  # --- 어그로 테이블 (Threat Table) ---
  aggroTable: [AggroEntry]
  primaryTargetId: string           # 현재 주 타겟 ID

  # --- 스킬 (Skills) ---
  skillSlots: [SkillSlot]           # wiki-skill-schema.md 참조
  skillUsagePolicy: SkillUsagePolicy

  # --- 전리품 (Loot) ---
  lootTable: [LootEntry]
  lootOwnerId: string               # 처치 시 귀속 대상 (플레이어/파티)

  # --- 리스폰 ---
  respawnTimer: number              # 리스폰까지 남은 시간 (초)
  respawnTimerMax: number           # 리스폰 기본 간격 (초)

  # --- AI 행동 ---
  behaviorRules: [BehaviorRule]

  # --- 플래그 ---
  isElite: boolean
  isBoss: boolean
  isQuestTarget: boolean
  isTamable: boolean
```

---

## 3️⃣ DamageResistance & ImmunityTag

```yaml
DamageResistance:
  damageType: DamageType            # wiki-skill-schema.md 의 DamageType 참조
  multiplier: number                # 0.5 = 50% 감소, 0 = 완전 면역, 2.0 = 2배 피해

ImmunityTag:
  - CC.Stun
  - CC.Silence
  - CC.Root
  - CC.Slow
  - CC.Knockback
  - CC.Pull
  - CC.Airborne
  - CC.Fear
  - CC.Sleep
  - CC.Charm
  - Damage.True                     # 확정 피해도 면역
  - Dispel                          # 디버프 해제 면역
  - Taunt                           # 도발 면역
```

**예시:**

```yaml
resistances:
  - damageType: Fire
    multiplier: 0.25                # 화염 75% 감소
  - damageType: Ice
    multiplier: 2.0                 # 얼음 2배 피해

immunities:
  - CC.Stun
  - CC.Fear
```

---

## 4️⃣ AggroTable (어그로 테이블)

```yaml
AggroEntry:
  entityId: string                  # 플레이어/펫 ID
  threat: number                    # 누적 위협 수치
  lastHitTime: number               # 마지막 피해 받은 시각
  decayRate: number                 # 초당 위협 감소량
```

---

## 5️⃣ SkillUsagePolicy (스킬 사용 정책)

> 몬스터가 언제 어떤 스킬을 쓸지 정하는 규칙.

```yaml
SkillUsagePolicy:
  rotation: SkillRotationType
  priorityList: [SkillPriorityRule]

SkillRotationType:
  - Sequential                      # 순서대로
  - Random                          # 무작위
  - PriorityBased                   # 우선순위 기반
  - PhaseBased                      # 페이즈별 고정
  - Reactive                        # 상황 반응형

SkillPriorityRule:
  skillId: string
  priority: number                  # 낮을수록 먼저
  condition: BehaviorCondition      # 발동 조건
  cooldownAware: boolean
  targetFilter: TargetFilter
```

**예시:**

```yaml
skillUsagePolicy:
  rotation: PriorityBased
  priorityList:
    - skillId: skill.heal_self
      priority: 1
      condition: HPBelow30Percent
      cooldownAware: true
      targetFilter: Self
    - skillId: skill.cleave
      priority: 2
      condition: ThreeOrMoreEnemiesInMelee
      cooldownAware: true
      targetFilter: AllEnemiesInMelee
    - skillId: skill.basic_attack
      priority: 99
      condition: Always
      cooldownAware: false
      targetFilter: HighestThreat
```

---

## 6️⃣ BehaviorRule (AI 행동 규칙)

> "어떤 상황일 때 무엇을 하는가" 를 원자 단위로.

```yaml
BehaviorRule:
  name: string
  priority: number
  trigger: BehaviorTrigger
  condition: BehaviorCondition
  action: BehaviorAction

BehaviorTrigger:
  - OnSpawn
  - OnTargetSeen
  - OnDamaged
  - OnHPChanged
  - OnTargetLost
  - OnAllyDeath
  - OnPhaseChange
  - OnTick                          # 주기적
  - OnDeath

BehaviorCondition:
  - Always
  - HPBelow30Percent
  - HPBelow10Percent
  - EnragedPhase
  - OneOrMoreAlliesAlive
  - OneOrMoreAlliesDead
  - TargetInMelee
  - TargetOutOfRange
  - TargetLowHP
  - TargetIsHealer
  - ThreeOrMoreEnemiesInMelee
  - OutsideLeashRange

BehaviorAction:
  - Attack
  - Flee
  - Call_Reinforcement
  - Enrage
  - UseSkill
  - Taunt
  - ReturnToSpawn
  - Patrol
  - Despawn
  - TransformPhase
```

**예시 — 보스 페이즈 전환:**

```yaml
behaviorRules:
  - name: PhaseOneToTwo
    priority: 1
    trigger: OnHPChanged
    condition: HPBelow30Percent
    action: TransformPhase
  - name: EnrageOnLeash
    priority: 2
    trigger: OnTick
    condition: OutsideLeashRange
    action: Enrage
  - name: CallForHelp
    priority: 5
    trigger: OnDamaged
    condition: HPBelow50Percent
    action: Call_Reinforcement
```

---

## 7️⃣ TargetFilter (타겟 선정 필터)

```yaml
TargetFilter:
  - Self
  - HighestThreat                   # 어그로 1위
  - LowestHP                        # 체력 낮은 대상
  - HighestHP
  - NearestEnemy
  - FarthestEnemy
  - RandomEnemy
  - IsHealer                        # 힐러 우선
  - IsRanged
  - IsMelee
  - AllEnemiesInMelee
  - AllEnemiesInArea
```

---

## 8️⃣ LootTable (전리품 테이블)

```yaml
LootEntry:
  itemId: string
  dropChance: number                # 0.0 ~ 1.0
  minQuantity: number
  maxQuantity: number
  condition: LootCondition          # 드롭 조건 (optional)

LootCondition:
  - Always
  - KilledByPlayer
  - KilledInParty
  - KilledInRaid
  - FirstKillOfDay
  - KilledWithSkillTag.Fire
```

---

## 9️⃣ 완전한 몬스터 예시

### 예시 1 — 일반 고블린 전사

```yaml
Monster:
  id: monster.goblin_warrior.inst_001
  templateId: monster.goblin_warrior
  name: "Goblin Warrior"

  species: Humanoid
  rank: Normal
  behaviorType: Aggressive
  faction: faction.goblins

  level: 12
  difficultyTier: 2
  experienceReward: 50
  goldReward: 3

  hp: 420
  hpMax: 420
  mana: 0
  manaMax: 0
  attackPower: 35
  spellPower: 0
  defense: 20
  magicResist: 5
  critChance: 0.05
  attackSpeed: 1.2
  moveSpeed: 4.0

  resistances: []
  immunities: []

  lifeState: Alive
  spawnState: Alive
  aggroState: Idle
  combatState: OutOfCombat
  movementState: Idle
  controlState: [Normal]
  visibilityState: Visible
  lootState: Unlooted

  buffs: []
  debuffs: []

  position: { x: 250, y: 0, z: 100 }
  rotation: 0
  zoneId: zone.goblin_camp
  spawnPoint: { x: 250, y: 0, z: 100 }
  leashRange: 30
  aggroRange: 12

  aggroTable: []
  primaryTargetId: ""

  skillSlots:
    - slotIndex: 0
      skillId: skill.basic_slash
      level: 1
      cooldownRemaining: 0
      chargesCurrent: 1
      enabled: true
    - slotIndex: 1
      skillId: skill.rage_strike
      level: 1
      cooldownRemaining: 0
      chargesCurrent: 1
      enabled: true

  skillUsagePolicy:
    rotation: PriorityBased
    priorityList:
      - skillId: skill.rage_strike
        priority: 1
        condition: HPBelow30Percent
        cooldownAware: true
        targetFilter: HighestThreat
      - skillId: skill.basic_slash
        priority: 99
        condition: Always
        cooldownAware: false
        targetFilter: HighestThreat

  lootTable:
    - itemId: item.rusty_sword
      dropChance: 0.12
      minQuantity: 1
      maxQuantity: 1
      condition: KilledByPlayer
    - itemId: item.goblin_ear
      dropChance: 0.75
      minQuantity: 1
      maxQuantity: 2
      condition: Always

  respawnTimer: 0
  respawnTimerMax: 300

  behaviorRules:
    - name: EngageOnSight
      priority: 1
      trigger: OnTargetSeen
      condition: Always
      action: Attack
    - name: ReturnIfLeashed
      priority: 2
      trigger: OnTick
      condition: OutsideLeashRange
      action: ReturnToSpawn

  isElite: false
  isBoss: false
  isQuestTarget: false
  isTamable: false
```

### 예시 2 — 레이드 보스 (페이즈 전환)

```yaml
Monster:
  id: monster.flame_dragon.raid_001
  templateId: monster.flame_dragon
  name: "Pyrathos the Everburning"

  species: Dragon
  rank: RaidBoss
  behaviorType: Aggressive
  faction: faction.dragonkin

  level: 80
  difficultyTier: 10
  experienceReward: 50000
  goldReward: 2000

  hp: 12000000
  hpMax: 12000000

  attackPower: 4200
  defense: 850
  magicResist: 850

  resistances:
    - damageType: Fire
      multiplier: 0
    - damageType: Ice
      multiplier: 1.5

  immunities:
    - CC.Stun
    - CC.Fear
    - CC.Sleep
    - CC.Charm
    - CC.Airborne

  lifeState: Alive
  spawnState: Alive
  aggroState: Engaged
  combatState: InCombat
  movementState: Idle
  controlState: [Normal]
  visibilityState: Visible
  lootState: Locked

  leashRange: 80
  aggroRange: 50

  skillUsagePolicy:
    rotation: PhaseBased
    priorityList:
      - skillId: skill.flame_breath
        priority: 1
        condition: Always
        cooldownAware: true
        targetFilter: AllEnemiesInArea
      - skillId: skill.meteor_storm
        priority: 2
        condition: HPBelow50Percent
        cooldownAware: true
        targetFilter: AllEnemiesInArea
      - skillId: skill.enrage_roar
        priority: 3
        condition: HPBelow30Percent
        cooldownAware: true
        targetFilter: Self

  behaviorRules:
    - name: EnterPhase2
      priority: 1
      trigger: OnHPChanged
      condition: HPBelow50Percent
      action: TransformPhase
    - name: EnterPhase3
      priority: 2
      trigger: OnHPChanged
      condition: HPBelow30Percent
      action: Enrage

  isElite: true
  isBoss: true
  isQuestTarget: true
  isTamable: false
```

---

## 🔟 불변식 (Invariants)

```yaml
Invariant:
  - rule: "lifeState=Dead 이면 aggroState=Leashed, combatState=OutOfCombat"
  - rule: "spawnState=NotSpawned 이면 어떤 이벤트도 발생하지 않음"
  - rule: "aggroTable 이 비어있으면 aggroState=Idle 이어야 함"
  - rule: "aggroTable 이 1건 이상이면 aggroState 는 Idle 이 아니어야 함"
  - rule: "rank=Boss 이상이면 isBoss=true"
  - rule: "rank=RaidBoss 이면 lootState 는 Locked 또는 Unlooted 만 허용"
  - rule: "immunities 에 CC.Stun 이 있으면 ControlState.Stunned 가 적용되지 않아야 함"
  - rule: "현재 position 이 spawnPoint 에서 leashRange 이상 떨어지면 BehaviorRule 로 ReturnToSpawn 이 트리거되어야 함"
  - rule: "skillSlots 의 모든 skillId 는 skillUsagePolicy.priorityList 에 정책이 존재해야 함"
  - rule: "respawnTimer > 0 이면 spawnState=Respawning 이어야 함"
```

---

## 🔗 관련 문서

- [wiki-schema-guide.md](wiki-schema-guide.md) — 스키마 설계 철학
- [wiki-skill-schema.md](wiki-skill-schema.md) — Skill 엔티티 (몬스터 스킬 슬롯 참조)
- [wiki-entity-player.md](wiki-entity-player.md) — Player 엔티티 (어그로 테이블 대상)
- [wiki-entity-zone.md](wiki-entity-zone.md) — Zone 엔티티 (스폰/영역)
- [wiki-entity-state.md](wiki-entity-state.md) — State(상태이상) 엔티티 (몬스터 버프/디버프)
- [wiki-entity-item.md](wiki-entity-item.md) — LootTable 의 ItemTemplate 대상
- [wiki-entity-quest.md](wiki-entity-quest.md) — KillMonster 목표 대상
- [wiki-entity-interaction.md](wiki-entity-interaction.md) — NPC 대화/거래 Interaction
- [wiki-entity-session.md](wiki-entity-session.md) — Instance 내 보스 처치 기록
