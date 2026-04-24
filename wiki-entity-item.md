# Item Schema (아이템/재화 스키마)

> 인게임 모든 "소지 가능한 것" — 장비/소모품/재화/재료 — 을 AI가 이해하기 위한 스키마.
> Item 은 **원형(Template)** 과 **인스턴스(Instance)** 를 구분한다.
> Currency(재화)는 Item 의 특수 케이스이자 별도 축으로 관리한다.

---

## 🎯 설계 원칙

1. **Template** (청사진, 불변) 과 **Instance** (개별 개체, 가변) 를 분리한다.
2. 장비의 실제 장착 위치는 Player.equipment (wiki-entity-player.md) 에서 관리 — Item 은 "무엇인지"만 정의.
3. Currency 는 Item 이 아니라 **별도 축**으로 다룬다 (수량만 유의미, 인스턴스 없음).
4. 거래/강화/소모는 Item 이 아니라 **Interaction 스키마**가 담당 — 여기는 "상태/속성" 만.
5. 스택/귀속/내구도처럼 **시간에 따라 변하는 것**은 반드시 Instance 에만 존재한다.

---

## 1️⃣ 분류 축 (Classification Axes)

### Axis.ItemType — 아이템 종류

```yaml
ItemType:
  - Equipment           # 장비 (무기/방어구/장신구)
  - Consumable          # 소모품 (포션/스크롤)
  - Material            # 재료 (제작/강화)
  - QuestItem           # 퀘스트 전용
  - Container           # 가방/상자
  - Key                 # 열쇠/티켓
  - Recipe              # 제조법
  - Cosmetic            # 외형 (탈것/펫/스킨)
  - Currency            # 재화 (특수 취급)
  - Misc                # 기타
```

### Axis.EquipmentSlot — 장비 슬롯 (ItemType=Equipment 전용)

```yaml
EquipmentSlot:
  - Weapon.MainHand
  - Weapon.OffHand
  - Weapon.TwoHanded
  - Weapon.Ranged
  - Armor.Head
  - Armor.Chest
  - Armor.Legs
  - Armor.Feet
  - Armor.Hands
  - Armor.Shoulders
  - Armor.Back
  - Accessory.Ring
  - Accessory.Necklace
  - Accessory.Trinket
  - Accessory.Belt
  - None
```

### Axis.Rarity — 희귀도

```yaml
Rarity:
  - Trash               # 회색
  - Common              # 흰색
  - Uncommon            # 녹색
  - Rare                # 청색
  - Epic                # 보라
  - Legendary           # 주황
  - Mythic              # 적색
  - Artifact            # 초월
```

### Axis.BindingType — 귀속 방식

```yaml
BindingType:
  - Unbound             # 자유 거래
  - BoundOnPickup       # 획득 시 귀속 (거래 불가)
  - BoundOnEquip        # 장착 시 귀속
  - BoundToAccount      # 계정 귀속 (같은 계정 내 이동 가능)
  - BoundToCharacter    # 캐릭터 귀속
  - QuestBound          # 퀘스트 전용 (드롭/파괴 불가)
```

### Axis.StackingPolicy — 스택 정책

```yaml
StackingPolicy:
  - NotStackable        # 1개씩만
  - Stackable           # 최대치까지 누적
  - Chargeable          # 사용마다 수량 감소
  - Renewable           # 자동 재충전
```

### Axis.UsageType — 사용 방식

```yaml
UsageType:
  - Instant             # 클릭 즉시 효과
  - CastTime            # 시전 시간 있음
  - Passive             # 소지만 해도 효과
  - Equippable          # 장비 장착
  - Deployable          # 설치물
  - Learnable           # 학습형 (책 등)
  - Consumable          # 단발 소모
  - NonUsable           # 재료/퀘스트용
```

### Axis.CurrencyType — 재화 종류

```yaml
CurrencyType:
  - Gold                # 기본 통화
  - Silver
  - Copper
  - PremiumCoin         # 캐시
  - Gem                 # 고급 재화
  - HonorPoint          # PvP 명예
  - ValorPoint          # 레이드 용맹
  - GuildCoin
  - EventToken          # 이벤트 한정
  - CraftingPoint
```

### Axis.SourceType — 획득 경로

```yaml
SourceType:
  - MonsterDrop
  - QuestReward
  - ShopPurchase
  - CraftingResult
  - DungeonClear
  - RaidLoot
  - EventReward
  - LoginReward
  - Mail
  - Trade
  - GMGrant
  - StartingGear
```

---

## 2️⃣ ItemTemplate (불변 원형)

> 한 번 만들어지면 바뀌지 않음. 수많은 Instance 의 공유 설계도.

```yaml
ItemTemplate:
  # --- 식별 ---
  id: string                        # 고유 ID (예: "item.sword_of_dawn")
  name: string
  version: string

  # --- 분류 ---
  itemType: ItemType
  equipmentSlot: EquipmentSlot      # ItemType=Equipment 전용
  rarity: Rarity
  bindingType: BindingType
  stackingPolicy: StackingPolicy
  usageType: UsageType

  # --- 표기 ---
  iconId: string
  description: string               # AI 입력 아님

  # --- 수치 ---
  itemLevel: number                 # iLv
  requiredLevel: number             # 사용 최소 레벨
  requiredClass: [string]           # 사용 가능 직업
  requiredFaction: string
  maxStackSize: number              # Stackable 전용
  maxDurability: number             # 내구도 상한 (0=없음)
  sellPrice: number                 # 상점 판매가
  buyPrice: number                  # 상점 구매가
  buyPriceCurrency: CurrencyType

  # --- 장비 능력치 (Equipment 전용) ---
  baseStats: [ItemStat]
  bonusStats: [ItemStat]
  setId: string                     # 세트 아이템 ID
  socketSlots: number               # 보석 슬롯 수

  # --- 효과 (Consumable/Equipment) ---
  effectsOnUse: [Effect]            # wiki-skill-schema.md 참조
  effectsOnEquip: [Effect]
  skillGranted: string              # 이 아이템이 부여하는 스킬 ID

  # --- 태그 ---
  tags: [ItemTag]

  # --- 획득/소멸 규칙 ---
  acquirableFrom: [SourceType]
  lootCondition: LootConditionTag   # 드롭 조건
  tradable: boolean
  sellable: boolean
  destroyable: boolean

  # --- 사용 제한 ---
  cooldownShared: string            # 동일 쿨다운 그룹
  cooldownDuration: number
  maxCarryCount: number             # 캐릭터 당 보유 상한

  # --- 플래그 ---
  isUnique: boolean                 # 1개만 소지 가능
  isHeirloom: boolean               # 계정 공유 성장
  isSeasonal: boolean
```

---

## 3️⃣ ItemStat (아이템 능력치)

```yaml
ItemStat:
  attribute: string                 # "attackPower", "critChance" 등
  operation: EffectOperation        # wiki-skill-schema.md 참조
  value: number
  scalingTier: number               # 레벨에 따른 성장 등급
```

---

## 4️⃣ ItemTag (의미 태그)

```yaml
ItemTag:
  # --- 속성 ---
  - Weapon.Sword
  - Weapon.Bow
  - Weapon.Staff
  - Weapon.Dagger
  - Weapon.Shield
  - Armor.Heavy
  - Armor.Light
  - Armor.Cloth

  # --- 용도 ---
  - Consumable.Potion
  - Consumable.Scroll
  - Consumable.Food
  - Material.Ore
  - Material.Herb
  - Material.Leather

  # --- 세트/컬렉션 ---
  - Set.TierPiece
  - Set.WorldBoss
  - Collection.Seasonal

  # --- 특수 ---
  - Legendary.Quest                 # 전설 퀘스트 연관
  - ReadyForUpgrade
  - BindOnUse
```

---

## 5️⃣ ItemInstance (가변 개체)

> 개별 아이템 1개. 인벤토리에 들어있는 실제 개체.

```yaml
ItemInstance:
  # --- 식별 ---
  instanceId: string                # 고유 인스턴스 UUID
  templateId: string                # ItemTemplate ID

  # --- 소유 ---
  ownerId: string                   # 현재 소유자 (Player ID 등)
  location: ItemLocation

  # --- 가변 상태 ---
  stackCount: number                # 현재 수량 (Stackable 전용)
  currentDurability: number
  isBound: boolean                  # 귀속 여부 (현재 상태)
  isLocked: boolean                 # 잠금 (실수 삭제 방지)
  isEquipped: boolean

  # --- 강화/가공 ---
  enhancementLevel: number          # +n 강화 수치
  sockets: [SocketState]            # 보석 장착 상태
  randomStats: [ItemStat]           # 랜덤 옵션 (개체마다 다름)

  # --- 사용 이력 ---
  acquiredAt: number                # 획득 시각 (timestamp)
  acquiredFrom: SourceType
  expiresAt: number                 # 만료 시각 (0=영구)

  # --- 쿨다운 ---
  cooldownRemaining: number
```

---

## 6️⃣ ItemLocation (아이템 위치)

```yaml
ItemLocation:
  locationType: LocationType
  containerId: string               # 가방/상자/우편 ID
  slotIndex: number

LocationType:
  - Inventory
  - Equipment
  - Bank                            # 창고
  - GuildBank
  - Mail                            # 우편함
  - Trade                           # 거래창 임시
  - AuctionHouse
  - Dropped                         # 지면 드롭
  - Destroyed                       # 파괴됨
```

---

## 7️⃣ SocketState (보석 슬롯)

```yaml
SocketState:
  slotIndex: number
  socketType: SocketType
  socketedItemId: string            # 장착된 보석 itemId

SocketType:
  - Red
  - Blue
  - Yellow
  - Green
  - Meta
  - Prismatic
  - Empty
```

---

## 8️⃣ CurrencyAccount (재화 계정)

> Item 과 분리된 "플레이어가 보유한 재화" 구조.

```yaml
CurrencyAccount:
  ownerId: string                   # Player ID 또는 Account ID
  balances: [CurrencyBalance]

CurrencyBalance:
  currencyType: CurrencyType
  amount: number
  capMax: number                    # 상한 (0=없음)
  weeklyEarned: number              # 주간 획득량
  weeklyCap: number                 # 주간 상한
  soulbound: boolean                # 캐릭터 귀속 여부
```

---

## 9️⃣ LootConditionTag (드롭 조건)

```yaml
LootConditionTag:
  - Always
  - MinLevelRequired                # 특정 레벨 이상만
  - InPartyRequired
  - InRaidRequired
  - FirstKillOfDay
  - BossMechanicCompleted           # 특정 기믹 처리 시
  - SpecificQuestActive
  - EventActive.SeasonalHalloween
  - ClassMatchesTemplate            # 직업별 개인 드롭
```

---

## 🔟 완전한 예시

### 예시 1 — Legendary 무기 Template

```yaml
ItemTemplate:
  id: item.sword_of_dawn
  name: "Sword of Dawn"
  version: "1.0.0"

  itemType: Equipment
  equipmentSlot: Weapon.MainHand
  rarity: Legendary
  bindingType: BoundOnEquip
  stackingPolicy: NotStackable
  usageType: Equippable

  iconId: icon.sword_dawn
  description: ""

  itemLevel: 85
  requiredLevel: 70
  requiredClass: [Warrior, Paladin]
  requiredFaction: ""
  maxStackSize: 1
  maxDurability: 150
  sellPrice: 12000
  buyPrice: 0
  buyPriceCurrency: Gold

  baseStats:
    - attribute: attackPower
      operation: Add
      value: 450
      scalingTier: 3
    - attribute: critChance
      operation: Add
      value: 0.08
      scalingTier: 2

  bonusStats:
    - attribute: holyDamageBonus
      operation: Multiply
      value: 1.15
      scalingTier: 1

  setId: ""
  socketSlots: 2

  effectsOnUse: []
  effectsOnEquip:
    - target: Caster
      operation: AddState
      attribute: State
      value: state.aura_of_dawn
      duration: 0

  skillGranted: skill.solar_flare

  tags:
    - Weapon.Sword
    - Legendary.Quest

  acquirableFrom:
    - RaidLoot
    - QuestReward
  lootCondition: BossMechanicCompleted
  tradable: false
  sellable: true
  destroyable: true

  cooldownShared: ""
  cooldownDuration: 0
  maxCarryCount: 1

  isUnique: true
  isHeirloom: false
  isSeasonal: false
```

### 예시 2 — 소모품 (Stackable)

```yaml
ItemTemplate:
  id: item.major_healing_potion
  name: "Major Healing Potion"

  itemType: Consumable
  equipmentSlot: None
  rarity: Uncommon
  bindingType: Unbound
  stackingPolicy: Stackable
  usageType: Instant

  itemLevel: 50
  requiredLevel: 45
  maxStackSize: 99
  maxDurability: 0
  sellPrice: 5
  buyPrice: 25
  buyPriceCurrency: Gold

  effectsOnUse:
    - target: Caster
      operation: Add
      attribute: HP
      value: 2000
      duration: 0

  tags:
    - Consumable.Potion

  acquirableFrom:
    - ShopPurchase
    - MonsterDrop

  cooldownShared: cd.potion_shared
  cooldownDuration: 60
  maxCarryCount: 0

  tradable: true
  sellable: true
  destroyable: true
  isUnique: false
```

### 예시 3 — ItemInstance (인벤토리 안의 개체)

```yaml
ItemInstance:
  instanceId: inst.uuid_7fa3b2
  templateId: item.sword_of_dawn

  ownerId: player.user_12345
  location:
    locationType: Equipment
    containerId: ""
    slotIndex: 1                    # MainHand

  stackCount: 1
  currentDurability: 142
  isBound: true
  isLocked: false
  isEquipped: true

  enhancementLevel: 5
  sockets:
    - slotIndex: 0
      socketType: Red
      socketedItemId: item.gem_ruby_flawless
    - slotIndex: 1
      socketType: Blue
      socketedItemId: ""

  randomStats:
    - attribute: vitality
      operation: Add
      value: 45
      scalingTier: 2

  acquiredAt: 1713000000
  acquiredFrom: RaidLoot
  expiresAt: 0

  cooldownRemaining: 0
```

### 예시 4 — CurrencyAccount

```yaml
CurrencyAccount:
  ownerId: player.user_12345
  balances:
    - currencyType: Gold
      amount: 184520
      capMax: 0
      weeklyEarned: 22400
      weeklyCap: 0
      soulbound: false

    - currencyType: Gem
      amount: 340
      capMax: 99999
      weeklyEarned: 0
      weeklyCap: 0
      soulbound: false

    - currencyType: HonorPoint
      amount: 12300
      capMax: 15000
      weeklyEarned: 3200
      weeklyCap: 5000
      soulbound: true
```

---

## 1️⃣1️⃣ 불변식 (Invariants)

```yaml
Invariant:
  - rule: "itemType=Equipment 이면 equipmentSlot 은 None 이 아니어야 함"
  - rule: "itemType != Equipment 이면 equipmentSlot=None"
  - rule: "stackingPolicy=NotStackable 이면 maxStackSize=1"
  - rule: "stackingPolicy=Stackable 이면 maxStackSize >= 2"
  - rule: "ItemInstance.stackCount 는 1 이상 Template.maxStackSize 이하"
  - rule: "ItemInstance.currentDurability 는 0 이상 Template.maxDurability 이하"
  - rule: "ItemInstance.enhancementLevel 은 0 이상"
  - rule: "ItemInstance.isEquipped=true 이면 location.locationType=Equipment"
  - rule: "ItemInstance.location.locationType=Equipment 이면 owner 의 Player.equipment 에 해당 슬롯 매칭"
  - rule: "Template.bindingType=QuestBound 이면 destroyable=false, tradable=false, sellable=false"
  - rule: "Template.isUnique=true 이면 maxCarryCount=1"
  - rule: "Template.tradable=false 이면 AuctionHouse location 불가"
  - rule: "Template.buyPrice > 0 이면 acquirableFrom 에 ShopPurchase 포함"
  - rule: "CurrencyBalance.amount <= capMax (capMax>0 일 때)"
  - rule: "CurrencyBalance.weeklyEarned <= weeklyCap (weeklyCap>0 일 때)"
  - rule: "Template.sockets.length 는 socketSlots 와 동일해야 함 (instance)"
```

---

## 🔗 관련 문서

- [wiki-schema-guide.md](wiki-schema-guide.md) — 스키마 설계 철학
- [wiki-entity-player.md](wiki-entity-player.md) — 인벤토리/장비 슬롯 소유자
- [wiki-entity-monster.md](wiki-entity-monster.md) — LootTable (아이템 드롭)
- [wiki-entity-interaction.md](wiki-entity-interaction.md) — 구매/판매/강화/거래 행위
- [wiki-entity-ui.md](wiki-entity-ui.md) — 상점/인벤토리 화면
- [wiki-entity-quest.md](wiki-entity-quest.md) — QuestReward 의 아이템 지급
