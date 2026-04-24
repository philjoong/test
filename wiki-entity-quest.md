# Quest Schema (퀘스트/진행도 스키마)

> 퀘스트/업적/일일임무/시즌과제 등 **플레이어의 목표 구조**를 AI가 이해하기 위한 스키마.
> 핵심은 `Objective(목표) × Progress(진행) × Reward(보상)` 의 분리다.
> 퀘스트 자체는 수락 후 Interaction 을 통해 진행되며, UI(퀘스트 창)는 이 데이터를 표시한다.

---

## 🎯 설계 원칙

1. **QuestTemplate**(설계도) 과 **QuestInstance**(플레이어별 진행 상태) 를 분리한다.
2. Objective 는 반드시 **원자 단위**(몬스터 N마리 처치, 아이템 M개 획득)로 분해한다.
3. 조건식("이거 또는 저거")은 Objective **그룹(AND/OR)** 구조로 표현.
4. Reward 는 **확정 보상** / **선택 보상** / **랜덤 보상** 으로 분리.
5. 퀘스트 흐름(수락→진행→완료→보상)은 StateMachine 으로 본다.

---

## 1️⃣ 분류 축 (Classification Axes)

### Axis.QuestCategory — 퀘스트 분류

```yaml
QuestCategory:
  - MainStory           # 메인 스토리
  - SideQuest           # 사이드
  - Daily               # 일일
  - Weekly              # 주간
  - Repeatable          # 반복
  - Seasonal            # 시즌
  - Event               # 이벤트
  - Hidden              # 숨김
  - Tutorial
  - Achievement         # 업적
  - GuildQuest
  - WorldQuest
  - Bounty              # 현상금
```

### Axis.QuestFrequency — 반복 주기

```yaml
QuestFrequency:
  - OneTime             # 1회 한정
  - Daily               # 일일 초기화
  - Weekly              # 주간 초기화
  - Monthly
  - Seasonal
  - Always              # 항상 반복 가능
  - OnTrigger           # 조건 발생 시
```

### Axis.QuestState — 퀘스트 상태 (Instance)

```yaml
QuestState:
  - NotAvailable        # 수락 불가 (조건 미충족)
  - Available           # 수락 가능
  - Accepted            # 수락함
  - InProgress          # 진행 중
  - ReadyToComplete     # 완료 가능 (모든 Objective 달성)
  - Completed           # 완료
  - Failed              # 실패
  - Abandoned           # 포기
  - Expired             # 만료
```

### Axis.ObjectiveType — 목표 종류

```yaml
ObjectiveType:
  - KillMonster         # 몬스터 처치
  - KillPlayer          # PvP 처치
  - CollectItem         # 아이템 수집
  - DeliverItem         # 아이템 전달
  - TalkToNPC           # NPC 대화
  - ReachLocation       # 특정 위치 도달
  - UseSkill            # 스킬 사용
  - UseItem             # 아이템 사용
  - CompleteInteraction # 특정 Interaction 완료
  - CompleteDungeon     # 던전 클리어
  - SurviveDuration     # 일정 시간 생존
  - EscortNPC           # 호위
  - DefendLocation      # 방어
  - GainLevel           # 레벨업
  - EarnCurrency        # 재화 획득
  - TrainSkill          # 스킬 습득
  - CompleteQuest       # 다른 퀘스트 완료 (체인)
  - CustomEvent         # 커스텀 이벤트
```

### Axis.ObjectiveLogic — 목표 조합 논리

```yaml
ObjectiveLogic:
  - AllOf               # 전부 달성 (AND)
  - AnyOf               # 하나라도 (OR)
  - Sequential          # 순서대로
  - NofM                # M개 중 N개
```

### Axis.RewardType — 보상 종류

```yaml
RewardType:
  - Experience
  - Currency
  - Item
  - ItemChoice          # 선택형
  - ItemRandom          # 랜덤
  - Skill               # 스킬 해금
  - Reputation          # 평판
  - Achievement
  - Title               # 칭호
  - CosmeticUnlock
  - ZoneUnlock          # 지역 해금
  - InteractionUnlock   # 특정 Interaction 해금
```

### Axis.FailureMode — 실패 조건

```yaml
FailureMode:
  - NoFailure           # 실패 없음
  - OnPlayerDeath
  - OnTimeout
  - OnEscortTargetDeath
  - OnLocationLeft
  - OnItemLost
  - OnZoneChange
```

---

## 2️⃣ QuestTemplate (불변 원형)

```yaml
QuestTemplate:
  # --- 식별 ---
  id: string                        # (예: "quest.dragon_slayer")
  name: string
  version: string

  # --- 분류 ---
  category: QuestCategory
  frequency: QuestFrequency

  # --- 수락 조건 ---
  acceptPreconditions: [QuestPrecondition]

  # --- 제공자 ---
  questGiver: QuestGiver

  # --- 목표 ---
  objectives: [Objective]
  objectiveLogic: ObjectiveLogic

  # --- 제한 ---
  timeLimit: number                 # 완료 제한 (초, 0=없음)
  levelMin: number
  levelMax: number
  requiredClass: [string]
  requiredFaction: string
  requiredZone: string
  requiredPreviousQuest: [string]

  # --- 실패 조건 ---
  failureModes: [FailureMode]
  failureConsequences: [Effect]

  # --- 보상 ---
  rewards: [QuestReward]

  # --- 사이드 이펙트 ---
  onAccept: [Effect]
  onComplete: [Effect]
  onAbandon: [Effect]

  # --- 연쇄 ---
  nextQuest: string                 # 자동 연결되는 다음 퀘스트
  questChain: string                # 소속 체인 ID

  # --- 플래그 ---
  isHidden: boolean                 # 미수락 시 로그에 표시 안 됨
  isShareable: boolean              # 파티 공유 가능
  isAbandonable: boolean
  autoAccept: boolean               # 조건 충족 시 자동 수락
  autoComplete: boolean             # 목표 달성 시 자동 완료
  trackable: boolean
```

---

## 3️⃣ QuestGiver (퀘스트 제공자)

```yaml
QuestGiver:
  giverType: GiverType
  giverId: string                   # NPC ID / Object ID / 시스템
  startZoneId: string
  completeZoneId: string            # 완료 보고 장소 (giver 와 다를 수 있음)
  completeGiverId: string

GiverType:
  - NPC
  - Object                          # 세계에 있는 오브젝트
  - System                          # 시스템 부여
  - Mail                            # 우편 수령
  - PickupItem                      # 아이템 획득 시 발생
  - ZoneEntry                       # 지역 진입 시
```

---

## 4️⃣ Objective (목표)

```yaml
Objective:
  id: string
  order: number                     # 표시 순서
  objectiveType: ObjectiveType
  description: string               # 표기용 (AI 입력 아님)

  # --- 목표 대상 ---
  targetType: ObjectiveTargetType
  targetId: string                  # 대상 ID (monsterId, itemId, zoneId 등)
  targetTag: string                 # 태그 기반 매칭

  # --- 수치 ---
  requiredCount: number
  currentCount: number              # Instance 에서만 사용

  # --- 조건 ---
  conditions: [ObjectiveCondition]

  # --- 타이머 ---
  timeLimit: number

  # --- UI ---
  showInTracker: boolean
  showCountOnKill: boolean

  # --- 선택적 / 숨김 ---
  isOptional: boolean
  isHidden: boolean                 # 완료 전까지 UI 비표시

ObjectiveTargetType:
  - SpecificEntity                  # 특정 ID
  - TemplateMatch                   # templateId 매칭
  - TagMatch                        # 태그 매칭
  - LocationArea                    # 지역 내 어떤 것이든

ObjectiveCondition:
  - UsingSkillTag.Fire              # 특정 속성 스킬로
  - InZone.ZoneId
  - DuringNight
  - InParty
  - Solo
  - WithoutTakingDamage
  - WithinTimeLimit
```

---

## 5️⃣ QuestPrecondition (수락 조건)

```yaml
QuestPrecondition:
  condition: PreconditionCheck      # wiki-entity-interaction.md 재사용
  expected: any
  reason: string
  priority: number
```

---

## 6️⃣ QuestReward (보상)

```yaml
QuestReward:
  rewardType: RewardType
  amount: number                    # Experience/Currency 전용
  currencyType: CurrencyType        # Currency 전용
  itemId: string                    # Item 전용
  quantity: number                  # Item 개수
  choices: [QuestReward]            # ItemChoice 전용
  dropTable: [RandomRewardEntry]    # ItemRandom 전용
  unlockId: string                  # Skill/Zone/Interaction Unlock 전용
  condition: RewardCondition        # 조건부 보상

RandomRewardEntry:
  reward: QuestReward
  weight: number                    # 가중치

RewardCondition:
  - Always
  - FirstCompletionOnly
  - WithinTimeLimit
  - NoDeath
  - SoloCompletion
  - PartyCompletion
  - HardModeOnly
```

---

## 7️⃣ QuestInstance (플레이어별 진행 상태)

```yaml
QuestInstance:
  # --- 식별 ---
  instanceId: string
  templateId: string
  ownerId: string                   # Player ID

  # --- 상태 ---
  state: QuestState
  acceptedAt: number
  completedAt: number
  expiresAt: number                 # 0=영구

  # --- 진행 ---
  objectiveProgress: [ObjectiveProgress]

  # --- 결과 ---
  isRewarded: boolean
  chosenRewardIndex: number         # ItemChoice 선택한 인덱스
  grantedRewards: [QuestReward]     # 실제 지급된 보상 (랜덤 결과 포함)

  # --- 추적 ---
  isTracked: boolean
  isFailed: boolean
  failReason: string

ObjectiveProgress:
  objectiveId: string
  currentCount: number
  isComplete: boolean
  completedAt: number
```

---

## 8️⃣ QuestLog (플레이어의 퀘스트 전체 현황)

```yaml
QuestLog:
  ownerId: string
  activeQuests: [QuestInstance]
  completedQuestIds: [string]       # 완료 기록 (instance 가 파기된 후에도 남음)
  failedQuestIds: [string]
  trackedQuestIds: [string]         # UI 추적 중
  maxActiveSlots: number
```

---

## 9️⃣ 완전한 예시

### 예시 1 — 메인 스토리 퀘스트 (체인 시작)

```yaml
QuestTemplate:
  id: quest.dragon_slayer_intro
  name: "Embers of Pyrathos"
  version: "1.0.0"

  category: MainStory
  frequency: OneTime

  acceptPreconditions:
    - condition: Player.LevelAtLeast
      expected: 70
      reason: NotEnoughLevel
      priority: 1
    - condition: Quest.Completed
      expected: quest.volcanic_rumors
      reason: PrerequisiteNotMet
      priority: 2

  questGiver:
    giverType: NPC
    giverId: npc.elder_thurian
    startZoneId: zone.mountain_village
    completeZoneId: zone.mountain_village
    completeGiverId: npc.elder_thurian

  objectives:
    - id: obj.kill_drakes
      order: 1
      objectiveType: KillMonster
      description: ""
      targetType: TemplateMatch
      targetId: monster.flame_drake
      requiredCount: 10
      currentCount: 0
      conditions:
        - InZone.zone.volcanic_peaks
      showInTracker: true
      showCountOnKill: true
      isOptional: false
      isHidden: false

    - id: obj.collect_scales
      order: 2
      objectiveType: CollectItem
      targetType: SpecificEntity
      targetId: item.flame_drake_scale
      requiredCount: 5
      currentCount: 0
      showInTracker: true
      isOptional: false

    - id: obj.optional_ore
      order: 3
      objectiveType: CollectItem
      targetType: SpecificEntity
      targetId: item.volcanic_ore
      requiredCount: 3
      currentCount: 0
      showInTracker: true
      isOptional: true

  objectiveLogic: AllOf

  timeLimit: 0
  levelMin: 70
  levelMax: 80
  requiredClass: []
  requiredZone: zone.volcanic_peaks

  failureModes:
    - NoFailure

  rewards:
    - rewardType: Experience
      amount: 50000
    - rewardType: Currency
      currencyType: Gold
      amount: 500
    - rewardType: ItemChoice
      choices:
        - rewardType: Item
          itemId: item.flame_resistance_cloak
          quantity: 1
        - rewardType: Item
          itemId: item.dragonhide_boots
          quantity: 1
    - rewardType: Item
      itemId: item.volcanic_ore_bonus
      quantity: 5
      condition: Always

  onAccept:
    - target: Caster
      operation: AddState
      attribute: State
      value: state.quest_tracked
      duration: 0

  onComplete: []

  nextQuest: quest.dragon_slayer_confrontation
  questChain: chain.dragon_slayer

  isHidden: false
  isShareable: true
  isAbandonable: true
  autoAccept: false
  autoComplete: false
  trackable: true
```

### 예시 2 — 일일 퀘스트 (시간 제한 + 실패 가능)

```yaml
QuestTemplate:
  id: quest.daily_escort_merchant
  name: "Safe Passage"

  category: Daily
  frequency: Daily

  acceptPreconditions:
    - condition: Player.LevelAtLeast
      expected: 40
      reason: NotEnoughLevel
      priority: 1

  questGiver:
    giverType: NPC
    giverId: npc.merchant_briar
    startZoneId: zone.frontier_outpost
    completeZoneId: zone.safe_haven
    completeGiverId: npc.merchant_briar

  objectives:
    - id: obj.escort
      order: 1
      objectiveType: EscortNPC
      targetType: SpecificEntity
      targetId: npc.merchant_briar
      requiredCount: 1
      timeLimit: 900                # 15분
      showInTracker: true
      isOptional: false

  objectiveLogic: AllOf
  timeLimit: 900

  failureModes:
    - OnEscortTargetDeath
    - OnTimeout

  failureConsequences:
    - target: Caster
      operation: AddState
      attribute: State
      value: state.reputation_penalty_merchants
      duration: 3600

  rewards:
    - rewardType: Experience
      amount: 8000
    - rewardType: Currency
      currencyType: Gold
      amount: 150
    - rewardType: Reputation
      amount: 200

  autoAccept: false
  autoComplete: true
  trackable: true
```

### 예시 3 — QuestInstance (진행 중 상태)

```yaml
QuestInstance:
  instanceId: qi.uuid_9a12
  templateId: quest.dragon_slayer_intro
  ownerId: player.user_12345

  state: InProgress
  acceptedAt: 1713001200
  completedAt: 0
  expiresAt: 0

  objectiveProgress:
    - objectiveId: obj.kill_drakes
      currentCount: 7
      isComplete: false
      completedAt: 0
    - objectiveId: obj.collect_scales
      currentCount: 5
      isComplete: true
      completedAt: 1713004800
    - objectiveId: obj.optional_ore
      currentCount: 1
      isComplete: false
      completedAt: 0

  isRewarded: false
  chosenRewardIndex: -1
  grantedRewards: []
  isTracked: true
  isFailed: false
  failReason: ""
```

---

## 🔟 불변식 (Invariants)

```yaml
Invariant:
  - rule: "frequency=Daily 이면 QuestInstance.expiresAt 은 0 이 아니어야 함 (일일 리셋)"
  - rule: "timeLimit > 0 이면 failureModes 에 OnTimeout 포함"
  - rule: "objectives[].isOptional=true 인 목표는 objectiveLogic=AllOf 에서도 완료 여부에 영향 없음"
  - rule: "rewards 중 rewardType=ItemChoice 는 최소 2개의 choices 필요"
  - rule: "QuestInstance.state=Completed 이면 모든 non-optional objective 의 isComplete=true"
  - rule: "QuestInstance.state=ReadyToComplete 이면 objectives 는 만족하나 아직 NPC 에 보고 전"
  - rule: "autoComplete=true 이면 state 가 InProgress 에서 바로 Completed 로 전이"
  - rule: "autoAccept=true 이면 acceptPreconditions 충족 즉시 수락"
  - rule: "nextQuest 가 있으면 그 퀘스트의 requiredPreviousQuest 에 자신이 포함되어야 함"
  - rule: "isAbandonable=false 이면 Abandoned 상태로 전이 불가"
  - rule: "objectives[].requiredCount > 0 이어야 함"
  - rule: "ObjectiveProgress.currentCount 는 0 이상 requiredCount 이하"
  - rule: "category=Achievement 이면 frequency=OneTime 이어야 함"
  - rule: "questGiver.giverType=Mail 이면 startZoneId 무관"
```

---

## 🔗 관련 문서

- [wiki-schema-guide.md](wiki-schema-guide.md) — 스키마 설계 철학
- [wiki-entity-player.md](wiki-entity-player.md) — QuestLog 소유자
- [wiki-entity-monster.md](wiki-entity-monster.md) — KillMonster 목표 대상
- [wiki-entity-item.md](wiki-entity-item.md) — CollectItem 목표, 보상 아이템
- [wiki-entity-zone.md](wiki-entity-zone.md) — ReachLocation/requiredZone
- [wiki-entity-ui.md](wiki-entity-ui.md) — 퀘스트 창 화면
- [wiki-entity-interaction.md](wiki-entity-interaction.md) — 수락/완료/포기 Interaction
- [wiki-entity-state.md](wiki-entity-state.md) — 퀘스트가 부여하는 State
