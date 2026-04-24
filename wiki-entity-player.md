# Player Schema (플레이어 스키마)

> 플레이어 엔티티를 AI가 "상태 + 규칙 + 결과"로 이해하기 위한 스키마.
> 모든 속성은 **분류 축(axis)** 과 **원자 단위 상태**로 정리한다.

---

## 🎯 설계 원칙

1. 플레이어의 모든 상태는 **독립된 축**으로 분리한다 (조합은 AI가 한다).
2. "레벨 50 전사" 같은 문장형 표현 금지 → `class=Warrior, level=50` 으로 분해.
3. **시점별 변하는 값**(HP, Position)과 **시점 무관한 값**(Class, MaxHP) 을 구분한다.
4. 스킬과의 연결은 `skillSlots` 로만 표현 (스킬 정의는 [wiki-skill-schema.md](wiki-skill-schema.md) 참조).

---

## 1️⃣ 분류 축 (Classification Axes)

### Axis.Class — 직업

```yaml
Class:
  - Warrior
  - Mage
  - Archer
  - Rogue
  - Priest
  - Paladin
  - Necromancer
  - Summoner
```

### Axis.Role — 역할

```yaml
Role:
  - Tank              # 피해 흡수
  - Melee_DPS         # 근접 딜러
  - Ranged_DPS        # 원거리 딜러
  - Healer            # 회복
  - Support           # 버프/유틸
  - Hybrid            # 복합
```

### Axis.Faction — 진영

```yaml
Faction:
  - Alliance
  - Horde
  - Neutral
  - Outlaw            # PK 상태
```

### Axis.LifeState — 생사 상태

```yaml
LifeState:
  - Alive
  - Dead
  - Ghost             # 사망 후 영혼 상태
  - Reviving          # 부활 중
```

### Axis.CombatState — 전투 상태

```yaml
CombatState:
  - InCombat
  - OutOfCombat
  - Engaging          # 전투 진입 중
```

### Axis.MovementState — 이동 상태

```yaml
MovementState:
  - Idle
  - Walking
  - Running
  - Sprinting
  - Jumping
  - Falling
  - Mounted
  - Flying
  - Swimming
```

### Axis.ControlState — 피제어 상태 (CrowdControl 적용)

```yaml
ControlState:
  - Normal
  - Stunned
  - Silenced
  - Rooted
  - Slowed
  - Feared
  - Airborne
  - Sleeping
  - Charmed
```

### Axis.VisibilityState — 시인성

```yaml
VisibilityState:
  - Visible
  - Stealthed          # 은신
  - Invisible          # 완전 은폐
  - Detected           # 은신이 감지됨
```

### Axis.PvPState — PvP 참여 상태

```yaml
PvPState:
  - PvE_Only           # PvP 비활성
  - PvP_Enabled        # PvP 활성
  - PvP_Flagged        # PK 후 일시 플래그
  - WarDeclared        # 선전포고 상태
```

---

## 2️⃣ Player 엔티티 전체 속성

```yaml
Player:
  # --- 식별 (Identification) ---
  id: string                        # 고유 ID
  name: string                      # 캐릭터명
  accountId: string                 # 계정 ID

  # --- 분류 ---
  class: Class
  role: Role
  faction: Faction

  # --- 성장 (Progression) ---
  level: number                     # 레벨
  experience: number                # 경험치
  experienceToNext: number          # 다음 레벨까지 필요한 경험치

  # --- 생명/자원 (Stats) ---
  hp: number
  hpMax: number
  mana: number
  manaMax: number
  stamina: number
  staminaMax: number

  # --- 전투 스탯 (Combat Stats) ---
  attackPower: number
  spellPower: number
  defense: number
  magicResist: number
  critChance: number                # 0.0 ~ 1.0
  critDamage: number                # 배율
  attackSpeed: number
  moveSpeed: number
  cooldownReduction: number         # 0.0 ~ 1.0

  # --- 동적 상태 (Dynamic States) ---
  lifeState: LifeState
  combatState: CombatState
  movementState: MovementState
  controlState: [ControlState]      # 중첩 가능 (Stun + Silence 동시)
  visibilityState: VisibilityState
  pvpState: PvPState

  # --- 상태 이상 (Status Effects) ---
  buffs: [StatusEffect]
  debuffs: [StatusEffect]

  # --- 위치 (Location) ---
  position: Vector3                 # { x, y, z }
  rotation: number                  # 방향 (degrees)
  zoneId: string                    # 현재 위치한 Zone ID
  instanceId: string                # 인스턴스(던전) ID

  # --- 스킬 (Skills) ---
  skillSlots: [SkillSlot]           # 장착된 스킬 목록
  skillBook: [string]               # 학습한 스킬 ID 목록

  # --- 인벤토리 (Inventory) ---
  inventory: [ItemSlot]
  equipment: Equipment
  gold: number

  # --- 파티/길드 (Social) ---
  partyId: string
  guildId: string
  raidId: string

  # --- 플래그 (Flags) ---
  isBot: boolean
  isGM: boolean
  isNewbie: boolean                 # 초보자 보호 대상
```

---

## 3️⃣ SkillSlot (스킬 장착 슬롯)

> 플레이어가 실제 사용할 수 있는 스킬 상태.

```yaml
SkillSlot:
  slotIndex: number                 # 슬롯 번호 (0~N)
  skillId: string                   # 장착된 스킬 ID
  level: number                     # 스킬 레벨
  cooldownRemaining: number         # 남은 쿨다운 (초)
  chargesCurrent: number            # 현재 충전 수
  enabled: boolean                  # 사용 가능 여부
```

---

## 4️⃣ StatusEffect (상태 이상) — 버프/디버프

> 상세 정의는 [wiki-entity-state.md](wiki-entity-state.md) 참조.

```yaml
StatusEffect:
  id: string                        # 상태 ID (예: "state.burn")
  source: string                    # 유발 스킬/엔티티 ID
  stacks: number
  durationRemaining: number
  dispellable: boolean
```

---

## 5️⃣ Equipment (장비)

```yaml
Equipment:
  weapon: Item
  offhand: Item
  head: Item
  chest: Item
  legs: Item
  boots: Item
  gloves: Item
  ring1: Item
  ring2: Item
  necklace: Item
  trinket1: Item
  trinket2: Item

Item:
  id: string
  name: string
  rarity: ItemRarity
  itemLevel: number
  stats: [StatModifier]

ItemRarity:
  - Common
  - Uncommon
  - Rare
  - Epic
  - Legendary
  - Mythic
```

---

## 6️⃣ 플레이어 행동 규칙 (Action Rules)

> 플레이어가 어떤 행동을 할 수 있는지 AI가 판정하기 위한 규칙.

```yaml
ActionRestriction:
  action: PlayerAction              # 어떤 행동이
  condition: PlayerCondition        # 어떤 조건일 때
  allowed: boolean                  # 허용 여부
  reason: string                    # 금지 사유 태그
  priority: number

PlayerAction:
  - UseSkill
  - Move
  - Attack
  - UseItem
  - Interact                        # NPC/오브젝트 상호작용
  - Trade
  - Loot
  - Mount
  - Emote
  - Chat

PlayerCondition:
  - LifeState.Dead
  - LifeState.Ghost
  - ControlState.Stunned
  - ControlState.Silenced
  - ControlState.Rooted
  - MovementState.Mounted
  - InSafeZone
  - InPvPZone
  - InCombat
  - OutOfCombat
```

**예시:**

```yaml
actionRestrictions:
  - action: UseSkill
    condition: LifeState.Dead
    allowed: false
    reason: CannotActWhileDead
    priority: 1
  - action: UseSkill
    condition: ControlState.Silenced
    allowed: false
    reason: Silenced
    priority: 2
  - action: Move
    condition: ControlState.Rooted
    allowed: false
    reason: Rooted
    priority: 3
  - action: Trade
    condition: InCombat
    allowed: false
    reason: CannotTradeInCombat
    priority: 4
```

---

## 7️⃣ 완전한 플레이어 예시

```yaml
Player:
  id: player.user_12345
  name: "Aria"
  accountId: acc.98765

  class: Mage
  role: Ranged_DPS
  faction: Alliance

  level: 50
  experience: 124000
  experienceToNext: 20000

  hp: 3200
  hpMax: 4500
  mana: 1800
  manaMax: 2400
  stamina: 100
  staminaMax: 100

  attackPower: 120
  spellPower: 880
  defense: 240
  magicResist: 310
  critChance: 0.22
  critDamage: 1.8
  attackSpeed: 1.0
  moveSpeed: 5.5
  cooldownReduction: 0.15

  lifeState: Alive
  combatState: InCombat
  movementState: Running
  controlState: [Normal]
  visibilityState: Visible
  pvpState: PvE_Only

  buffs:
    - id: state.arcane_power
      source: skill.arcane_surge
      stacks: 3
      durationRemaining: 12.4
      dispellable: true

  debuffs: []

  position: { x: 1024.5, y: 30.0, z: 512.2 }
  rotation: 135
  zoneId: zone.crystal_forest
  instanceId: ""

  skillSlots:
    - slotIndex: 0
      skillId: skill.fireball
      level: 5
      cooldownRemaining: 0
      chargesCurrent: 1
      enabled: true
    - slotIndex: 1
      skillId: skill.meteor
      level: 3
      cooldownRemaining: 14.2
      chargesCurrent: 0
      enabled: false

  skillBook:
    - skill.fireball
    - skill.meteor
    - skill.frostbolt
    - skill.teleport

  inventory: []
  equipment:
    weapon: { id: item.staff_of_embers, rarity: Epic, itemLevel: 52 }
  gold: 12450

  partyId: party.001
  guildId: guild.phoenix
  raidId: ""

  isBot: false
  isGM: false
  isNewbie: false
```

---

## 8️⃣ 불변식 (Invariants)

```yaml
Invariant:
  - rule: "hp 는 0 이상 hpMax 이하"
  - rule: "mana 는 0 이상 manaMax 이하"
  - rule: "lifeState=Dead 이면 combatState=OutOfCombat 이어야 함"
  - rule: "lifeState=Dead 이면 hp=0 이어야 함"
  - rule: "lifeState=Ghost 이면 어떤 공격도 받지 않아야 함"
  - rule: "movementState=Mounted 이면 특정 스킬 사용 불가 (스킬 restriction 으로 명시)"
  - rule: "pvpState=PvE_Only 이면 타 플레이어에게 Damage 불가"
  - rule: "controlState 에 Stunned 가 있으면 모든 PlayerAction 불가 (Chat/Emote 제외)"
  - rule: "level 은 1 이상"
  - rule: "skillSlots 의 모든 skillId 는 skillBook 에 존재해야 함"
```

---

## 🔗 관련 문서

- [wiki-schema-guide.md](wiki-schema-guide.md) — 스키마 설계 철학
- [wiki-skill-schema.md](wiki-skill-schema.md) — Skill 엔티티
- [wiki-entity-monster.md](wiki-entity-monster.md) — Monster 엔티티
- [wiki-entity-zone.md](wiki-entity-zone.md) — Zone 엔티티 (Player.zoneId 참조)
- [wiki-entity-state.md](wiki-entity-state.md) — State(상태이상) 엔티티 (buffs/debuffs 상세)
- [wiki-entity-item.md](wiki-entity-item.md) — 인벤토리/장비/재화 상세 (Player.inventory/equipment)
- [wiki-entity-interaction.md](wiki-entity-interaction.md) — Precondition 의 주요 검증 대상
- [wiki-entity-ui.md](wiki-entity-ui.md) — 플레이어 정보 화면
- [wiki-entity-quest.md](wiki-entity-quest.md) — QuestLog 소유 주체
- [wiki-entity-session.md](wiki-entity-session.md) — Player 는 Session 이 선택한 캐릭터
