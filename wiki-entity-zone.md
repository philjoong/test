# Zone Schema (지역 스키마)

> 게임 공간(맵/지역/던전/인스턴스)을 AI가 "규칙이 적용되는 영역"으로 이해하기 위한 스키마.
> Zone 은 **규칙의 경계**다. 같은 행동도 어느 Zone 에서 일어나느냐에 따라 허용/금지가 달라진다.

---

## 🎯 설계 원칙

1. Zone 은 "장소"가 아니라 **"어떤 규칙이 유효한 영역"** 이다.
2. Zone 자체가 **Restriction 의 발동 조건**이 되므로, 축은 다른 스키마가 참조하기 좋게 설계한다.
3. 여러 Zone 이 **중첩** 가능하다 (예: 대륙 > 도시 > 여관 내부).
4. 동적 이벤트(레이드 등장, PvP 점령전)도 Zone 속성으로 표현한다.

---

## 1️⃣ 분류 축 (Classification Axes)

### Axis.ZoneType — 공간 유형

```yaml
ZoneType:
  - OpenWorld         # 오픈 월드
  - City              # 도시
  - Village           # 마을
  - Wilderness        # 야생 지역
  - Dungeon           # 던전 (인스턴스)
  - Raid              # 공격대 인스턴스
  - Battleground      # 전장 (PvP)
  - Arena             # 아레나
  - Instance          # 개인/파티 인스턴스
  - SafeHaven         # 귀환 포인트
  - Transition        # 이동 공간 (포탈/배)
```

### Axis.PvPRule — PvP 규칙

```yaml
PvPRule:
  - Disabled          # PvP 완전 불가
  - Enabled           # 상시 PvP 가능
  - Flagged           # 플래그 선언 시에만 PvP
  - Consensual        # 양측 동의 시만
  - Arena             # 아레나 전용 규칙
  - Warzone           # 진영 전쟁
```

### Axis.SafetyLevel — 안전 등급

```yaml
SafetyLevel:
  - Sanctuary         # 절대 안전 (공격/피해 불가)
  - Safe              # 기본적으로 안전, 일부 상황에서 PvP
  - Contested         # 분쟁 지역
  - Hostile           # 위험 지역
  - Lawless           # 무법 지대
```

### Axis.BiomeType — 생태 환경

```yaml
BiomeType:
  - Plains
  - Forest
  - Desert
  - Snow
  - Mountain
  - Swamp
  - Cave
  - Ocean
  - Underwater
  - Sky
  - Volcanic
  - Abyss
  - Urban
```

### Axis.WeatherState — 날씨 상태

```yaml
WeatherState:
  - Clear
  - Cloudy
  - Rain
  - Storm
  - Snow
  - Blizzard
  - Fog
  - Sandstorm
  - Ashfall           # 화산재
  - Corruption        # 이계 오염
```

### Axis.TimeOfDay — 시간대

```yaml
TimeOfDay:
  - Dawn
  - Day
  - Dusk
  - Night
  - Eclipse           # 특수 이벤트 시간
```

### Axis.InstanceMode — 인스턴스 모드

```yaml
InstanceMode:
  - NotInstanced      # 공용 맵
  - SharedInstance    # 샤드 형식 공유
  - PartyInstance     # 파티 전용
  - RaidInstance      # 공격대 전용
  - SoloInstance      # 1인 전용
```

---

## 2️⃣ Zone 엔티티 전체 속성

```yaml
Zone:
  # --- 식별 (Identification) ---
  id: string                        # 고유 ID (예: "zone.crystal_forest")
  name: string                      # 표기명
  parentZoneId: string              # 상위 Zone (예: 도시 > 여관)

  # --- 분류 ---
  zoneType: ZoneType
  biomeType: BiomeType
  pvpRule: PvPRule
  safetyLevel: SafetyLevel
  instanceMode: InstanceMode

  # --- 경계 (Boundary) ---
  boundary: Boundary
  subZones: [string]                # 하위 Zone ID 목록

  # --- 레벨 제한 (Access) ---
  recommendedLevelMin: number
  recommendedLevelMax: number
  requiredLevel: number             # 입장 제한
  requiredQuest: string             # 필요 퀘스트 ID
  requiredItem: string              # 열쇠 등

  # --- 규칙 (Rules) ---
  restrictions: [ZoneRestriction]   # 이 Zone 에서 금지/허용되는 행동
  modifiers: [ZoneModifier]         # Zone 이 적용하는 수치 변경

  # --- 환경 (Environment) ---
  currentWeather: WeatherState
  weatherCycle: [WeatherState]      # 날씨 순환
  currentTimeOfDay: TimeOfDay
  hasDayNightCycle: boolean
  ambientLight: number              # 0.0 ~ 1.0

  # --- 출현 대상 (Population) ---
  spawnGroups: [SpawnGroup]         # 몬스터 스폰 규칙
  npcList: [string]                 # 고정 NPC ID 목록
  resourceNodes: [ResourceNode]     # 채집 자원

  # --- 이동/입출 (Travel) ---
  entryPoints: [EntryPoint]
  portals: [Portal]
  recall: RecallPolicy

  # --- 인스턴스 정보 ---
  instanceId: string                # 인스턴스 고유 ID (NotInstanced 면 공란)
  ownerId: string                   # 인스턴스 소유 파티/플레이어
  difficultyLevel: DifficultyLevel  # 난이도 설정
  resetPolicy: ResetPolicy

  # --- 이벤트 (Events) ---
  activeEvents: [ZoneEvent]

  # --- 플래그 ---
  isStartingZone: boolean
  isCapitalCity: boolean
  isSeasonalOnly: boolean
```

---

## 3️⃣ Boundary (경계)

```yaml
Boundary:
  shape: BoundaryShape
  center: Vector3
  size: Vector3                     # Rectangle: w,h,d / Sphere: radius(x)
  polygonPoints: [Vector3]          # Polygon 일 때만

BoundaryShape:
  - Rectangle
  - Sphere
  - Polygon
  - Complex                         # 복수 경계 조합
```

---

## 4️⃣ ZoneRestriction (Zone 행동 제약)

> **다른 스키마(Player/Skill)의 Restriction 판정에 사용되는 핵심 속성.**
> Skill 스키마의 `restrictions[].condition: InSafeZone` 은 이 Zone 속성을 참조한다.

```yaml
ZoneRestriction:
  action: ZoneAction                # 어떤 행동이
  allowed: boolean                  # 허용 여부
  reason: string                    # 금지 사유 태그
  priority: number
  appliesTo: RestrictionTarget      # 누구에게

ZoneAction:
  - UseSkill.Damage
  - UseSkill.Heal
  - UseSkill.Summon
  - UseSkill.Mobility
  - UseSkill.Any
  - AttackPlayer
  - AttackMonster
  - UseMount
  - Fly
  - Duel
  - Trade
  - DropItem
  - OpenAuctionHouse
  - Resurrect
  - Teleport
  - Stealth

RestrictionTarget:
  - AllEntities
  - PlayersOnly
  - MonstersOnly
  - NonFactionMembers
  - BelowLevelThreshold
```

**예시 — 수도 도시의 규칙:**

```yaml
restrictions:
  - action: AttackPlayer
    allowed: false
    reason: CityPvPDisabled
    priority: 1
    appliesTo: PlayersOnly
  - action: UseMount
    allowed: true
    reason: MountAllowedInCity
    priority: 2
    appliesTo: PlayersOnly
  - action: Duel
    allowed: true
    reason: DuelAllowedInDesignatedArea
    priority: 3
    appliesTo: PlayersOnly
  - action: UseSkill.Summon
    allowed: false
    reason: SummonDisabledInSanctuary
    priority: 4
    appliesTo: AllEntities
```

---

## 5️⃣ ZoneModifier (수치 변경)

> Zone 이 엔티티의 스탯을 수정할 때 사용.

```yaml
ZoneModifier:
  target: ModifierTarget
  attribute: string                 # "moveSpeed", "hpRegen" 등
  operation: EffectOperation        # wiki-skill-schema.md 참조
  value: number
  condition: BehaviorCondition      # optional

ModifierTarget:
  - AllEntities
  - PlayersOnly
  - MonstersOnly
  - AllyOfZoneOwner
  - EnemyOfZoneOwner
```

**예시 — 수중 Zone 은 이동속도 감소:**

```yaml
modifiers:
  - target: AllEntities
    attribute: moveSpeed
    operation: Multiply
    value: 0.6
```

---

## 6️⃣ SpawnGroup (몬스터 스폰 그룹)

```yaml
SpawnGroup:
  id: string
  templateIds: [string]             # 스폰될 몬스터 templateId 목록
  spawnArea: Boundary
  maxConcurrent: number             # 동시 최대 개체 수
  respawnInterval: number           # 리스폰 간격 (초)
  densityTier: DensityTier
  levelRange: { min, max }
  condition: SpawnCondition

DensityTier:
  - Sparse
  - Normal
  - Dense
  - Swarm

SpawnCondition:
  - Always
  - DuringNight
  - DuringDay
  - DuringWeather.Storm
  - DuringEvent.Invasion
```

---

## 7️⃣ EntryPoint / Portal

```yaml
EntryPoint:
  id: string
  position: Vector3
  isDefault: boolean

Portal:
  id: string
  position: Vector3
  destinationZoneId: string
  destinationEntryPoint: string
  requiresKey: string
  cost: number
  condition: BehaviorCondition
```

---

## 8️⃣ RecallPolicy / ResetPolicy

```yaml
RecallPolicy:
  allowed: boolean                  # 귀환 스크롤 사용 가능 여부
  cooldown: number

ResetPolicy:
  mode: ResetMode
  schedule: string                  # "Daily 06:00 KST" 같은 cron 형식
  manualResetAllowed: boolean

ResetMode:
  - Never
  - OnEmpty                         # 파티 나가면 초기화
  - Daily
  - Weekly
  - OnBossKill
  - Manual
```

---

## 9️⃣ DifficultyLevel (난이도 설정)

```yaml
DifficultyLevel:
  name: string                      # "Normal" / "Heroic" / "Mythic"
  tier: number                      # 1~10
  monsterHPMultiplier: number
  monsterDamageMultiplier: number
  lootQualityTier: number
  maxPartySize: number
```

---

## 🔟 ZoneEvent (동적 이벤트)

```yaml
ZoneEvent:
  id: string
  name: string
  eventType: EventType
  startTime: number
  endTime: number
  participants: [string]
  modifiers: [ZoneModifier]         # 이벤트 중 적용되는 수정
  spawnOverrides: [SpawnGroup]      # 이벤트 전용 스폰

EventType:
  - Invasion                        # 몬스터 침공
  - WorldBossSpawn
  - WarDeclared                     # 진영 전쟁
  - Festival
  - WeatherStorm
  - Eclipse
  - TreasureHunt
```

---

## 1️⃣1️⃣ 완전한 Zone 예시

### 예시 1 — 수도 도시 (Safe Zone)

```yaml
Zone:
  id: zone.capital_city
  name: "Stormhaven"
  parentZoneId: zone.eastern_continent

  zoneType: City
  biomeType: Urban
  pvpRule: Disabled
  safetyLevel: Sanctuary
  instanceMode: NotInstanced

  boundary:
    shape: Rectangle
    center: { x: 0, y: 0, z: 0 }
    size: { x: 500, y: 200, z: 500 }

  recommendedLevelMin: 1
  recommendedLevelMax: 80
  requiredLevel: 0

  restrictions:
    - action: AttackPlayer
      allowed: false
      reason: CityPvPDisabled
      priority: 1
      appliesTo: PlayersOnly
    - action: UseSkill.Damage
      allowed: false
      reason: SafeZoneRestriction
      priority: 2
      appliesTo: AllEntities
    - action: Duel
      allowed: true
      reason: DuelAllowedInDesignatedArea
      priority: 3
      appliesTo: PlayersOnly

  modifiers:
    - target: PlayersOnly
      attribute: hpRegen
      operation: Multiply
      value: 2.0

  currentWeather: Clear
  weatherCycle: [Clear, Cloudy, Rain]
  currentTimeOfDay: Day
  hasDayNightCycle: true
  ambientLight: 1.0

  spawnGroups: []
  npcList:
    - npc.innkeeper_01
    - npc.blacksmith_01
    - npc.auctioneer_01

  entryPoints:
    - id: entry.main_gate
      position: { x: 0, y: 0, z: -250 }
      isDefault: true

  portals:
    - id: portal.mage_tower
      position: { x: 120, y: 0, z: 80 }
      destinationZoneId: zone.mage_tower
      destinationEntryPoint: entry.lobby
      requiresKey: ""
      cost: 0

  recall:
    allowed: true
    cooldown: 0

  instanceId: ""
  resetPolicy:
    mode: Never

  activeEvents: []
  isStartingZone: false
  isCapitalCity: true
  isSeasonalOnly: false
```

### 예시 2 — 공격대 던전 (Raid Instance)

```yaml
Zone:
  id: zone.dragon_lair.raid_inst_042
  name: "Pyrathos' Lair"
  parentZoneId: zone.volcanic_peaks

  zoneType: Raid
  biomeType: Volcanic
  pvpRule: Disabled
  safetyLevel: Hostile
  instanceMode: RaidInstance

  boundary:
    shape: Sphere
    center: { x: 0, y: 0, z: 0 }
    size: { x: 300, y: 0, z: 0 }

  recommendedLevelMin: 78
  recommendedLevelMax: 80
  requiredLevel: 75
  requiredQuest: quest.dragon_slayer_intro

  restrictions:
    - action: UseMount
      allowed: false
      reason: MountDisabledInRaid
      priority: 1
      appliesTo: AllEntities
    - action: Resurrect
      allowed: true
      reason: ResurrectAllowed
      priority: 2
      appliesTo: PlayersOnly
    - action: Teleport
      allowed: false
      reason: TeleportDisabledInRaid
      priority: 3
      appliesTo: PlayersOnly

  modifiers:
    - target: AllEntities
      attribute: fireResistance
      operation: Add
      value: -20

  currentWeather: Ashfall
  hasDayNightCycle: false
  ambientLight: 0.4

  spawnGroups:
    - id: sg.flame_drakes
      templateIds: [monster.flame_drake]
      maxConcurrent: 6
      respawnInterval: 0
      densityTier: Normal
      levelRange: { min: 79, max: 80 }
      condition: Always
    - id: sg.boss
      templateIds: [monster.flame_dragon]
      maxConcurrent: 1
      respawnInterval: 0
      densityTier: Sparse
      levelRange: { min: 80, max: 80 }
      condition: Always

  instanceId: "raid_inst_042"
  ownerId: raid.group_9987
  difficultyLevel:
    name: "Heroic"
    tier: 7
    monsterHPMultiplier: 2.0
    monsterDamageMultiplier: 1.5
    lootQualityTier: 8
    maxPartySize: 20

  resetPolicy:
    mode: Weekly
    schedule: "Weekly Tuesday 06:00 KST"
    manualResetAllowed: true

  activeEvents: []
  isStartingZone: false
  isCapitalCity: false
  isSeasonalOnly: false
```

---

## 1️⃣2️⃣ 불변식 (Invariants)

```yaml
Invariant:
  - rule: "zoneType=Raid 이면 instanceMode 는 RaidInstance 이어야 함"
  - rule: "safetyLevel=Sanctuary 이면 pvpRule=Disabled 이어야 함"
  - rule: "safetyLevel=Sanctuary 이면 모든 UseSkill.Damage 가 restriction 으로 금지되어야 함"
  - rule: "instanceMode!=NotInstanced 이면 instanceId 가 공란이 아니어야 함"
  - rule: "instanceMode=RaidInstance 이면 ownerId 가 raid.* 형식이어야 함"
  - rule: "parentZoneId 가 있으면 그 Zone 의 subZones 에 자신이 포함되어야 함"
  - rule: "subZones 의 모든 ID 가 실존 Zone 이어야 함"
  - rule: "portals[].destinationZoneId 는 실존 Zone 이어야 함"
  - rule: "requiredLevel > recommendedLevelMax 이면 안 됨"
  - rule: "resetPolicy.mode=Never 이면 schedule 은 공란이어야 함"
  - rule: "activeEvents 의 startTime < endTime 이어야 함"
```

---

## 🔗 관련 문서

- [wiki-schema-guide.md](wiki-schema-guide.md) — 스키마 설계 철학
- [wiki-skill-schema.md](wiki-skill-schema.md) — Skill 엔티티 (InSafeZone 등 Zone 조건 참조)
- [wiki-entity-player.md](wiki-entity-player.md) — Player 엔티티 (현재 zoneId)
- [wiki-entity-monster.md](wiki-entity-monster.md) — Monster 엔티티 (SpawnGroup 대상)
- [wiki-entity-state.md](wiki-entity-state.md) — State(상태이상) 엔티티 (Environmental State)
- [wiki-entity-ui.md](wiki-entity-ui.md) — 월드맵/던전UI 가 표시하는 Zone 데이터
- [wiki-entity-interaction.md](wiki-entity-interaction.md) — 텔레포트/던전입장 행위
- [wiki-entity-item.md](wiki-entity-item.md) — 리소스 노드/아이템 드롭
- [wiki-entity-quest.md](wiki-entity-quest.md) — requiredZone/ReachLocation 대상
- [wiki-entity-session.md](wiki-entity-session.md) — Instance 는 Zone 의 실제 회차
