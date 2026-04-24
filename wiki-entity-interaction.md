# Interaction Schema (상호작용/시스템 행위 스키마)

> 전투 외 모든 **게임 행위** — 구매/판매/텔레포트/던전입장/강화/NPC대화 — 를 AI가 이해하기 위한 스키마.
> Skill 스키마가 "전투 중 시전" 을 다룬다면, Interaction 은 "**UI/월드에서의 절차적 명령**" 을 다룬다.
> 공통 구조: `Precondition → Execution → Effect → Feedback`.

---

## 🎯 설계 원칙

1. Skill 과 Interaction 은 **다른 축**이다:
   - Skill = 즉발/전투/규칙 시전
   - Interaction = UI/절차/다단계 명령
2. 모든 Interaction 은 **실패 가능**하다. 실패 사유(FailReason)를 반드시 정의한다.
3. Precondition(사전 조건) → Execution(실행) → Effect(결과) → Feedback(반응) 4단계로 분해한다.
4. **원자 Interaction** 과 **복합 Flow** 를 구분한다. 텔레포트는 원자, "월드맵 열고→선택→이동→버프해제" 는 Flow.
5. 실행 단계에서 발생하는 상태 변화는 **Effect** 로 (wiki-skill-schema.md 의 Effect 와 같은 구조 재사용).

---

## 1️⃣ 분류 축 (Classification Axes)

### Axis.InteractionCategory — 행위 카테고리

```yaml
InteractionCategory:
  - Movement            # 이동 (텔레포트/귀환/탑승)
  - Commerce            # 거래 (구매/판매/거래소)
  - Crafting            # 제작/강화/분해
  - Social              # 대화/초대/파티/길드
  - Progression         # 레벨업/퀘스트완료/업적
  - Management          # 가방정리/창고/편지
  - WorldInteraction    # NPC상호작용/오브젝트조작
  - Instance            # 던전/레이드 입장/퇴장
  - Customization       # 외형변경/스킨
  - System              # 로그아웃/설정변경
```

### Axis.InteractionType — 상호작용 성격

```yaml
InteractionType:
  - Atomic              # 단일 원자 행위
  - Composite           # 내부에 여러 Interaction 조합
  - Staged              # 다단계 확인이 필요
  - Cancellable         # 중간 취소 가능
  - Irreversible        # 되돌릴 수 없음
```

### Axis.ExecutionMode — 실행 방식

```yaml
ExecutionMode:
  - Instant             # 즉시 완료
  - Timed               # 시간 경과 후 완료 (귀환 스크롤 등)
  - Interactive         # 사용자 입력을 추가로 받음
  - Channeled           # 유지 중 취소 가능
  - Queued              # 큐에 쌓아 순차 실행
```

### Axis.CostType — 비용 종류

```yaml
CostType:
  - Currency            # 재화 소모
  - Item                # 아이템 소모
  - Resource            # 자원 (마나/스태미나)
  - Time                # 시간 (쿨다운)
  - Durability          # 내구도
  - Free
```

### Axis.FeedbackType — 피드백 종류

```yaml
FeedbackType:
  - Silent              # 피드백 없음
  - Toast               # 토스트 알림
  - Popup               # 팝업
  - Modal               # 모달 (확인 필요)
  - Sound
  - VisualEffect
  - ScreenShake
  - HapticVibration
  - LogMessage          # 채팅/시스템 로그
```

### Axis.TargetSelectionMode — 타겟 지정 방식

```yaml
TargetSelectionMode:
  - NoTarget
  - SelfOnly
  - FromUIList          # UI 리스트에서 선택 (텔레포트 지점 등)
  - FromWorldClick      # 월드 클릭
  - FromInventorySlot
  - AutoSelect          # 시스템 자동 선정
  - FromSearch          # 검색어 기반
```

---

## 2️⃣ Interaction 엔티티 속성

```yaml
Interaction:
  # --- 식별 ---
  id: string                        # (예: "interaction.teleport")
  name: string
  version: string

  # --- 분류 ---
  category: InteractionCategory
  type: InteractionType
  executionMode: ExecutionMode
  targetSelectionMode: TargetSelectionMode

  # --- 사전조건 ---
  preconditions: [InteractionPrecondition]

  # --- 비용 ---
  costs: [InteractionCost]

  # --- 실행 파라미터 ---
  parameters: [InteractionParam]    # 입력받아야 할 값 스키마

  # --- 실행 시간 ---
  castDuration: number              # 초 (0=즉발)
  cancelableWhileCasting: boolean
  interruptOnDamage: boolean
  interruptOnMove: boolean

  # --- 효과 ---
  effectsOnStart: [Effect]          # 시작 시
  effectsOnSuccess: [Effect]        # 성공 시 (wiki-skill-schema.md 의 Effect)
  effectsOnCancel: [Effect]
  effectsOnFail: [Effect]

  # --- 실패 사유 ---
  failReasons: [FailReason]

  # --- 피드백 ---
  feedback: InteractionFeedback

  # --- 부수효과 (Side Effects) ---
  sideEffects: [SideEffect]

  # --- 권한/제한 ---
  allowedContexts: [ExecutionContext]

  # --- 로그/분석 ---
  logged: boolean                   # 로그 기록 여부
  analyticsEvent: string            # 분석 이벤트명
```

---

## 3️⃣ InteractionPrecondition (사전 조건)

```yaml
InteractionPrecondition:
  condition: PreconditionCheck
  expected: string | number | boolean
  reason: string                    # 실패 시 반환할 FailReason 태그
  priority: number
  bypassable: boolean               # GM/특수상황 우회 가능 여부

PreconditionCheck:
  # --- Player 상태 ---
  - Player.Alive
  - Player.NotInCombat
  - Player.LevelAtLeast
  - Player.ClassIsOneOf
  - Player.NotStunned
  - Player.NotSilenced
  - Player.NotMounted

  # --- Zone ---
  - Zone.TypeIsOneOf
  - Zone.AllowsAction                # Zone 의 ZoneRestriction 조회
  - Zone.SafetyLevelAtLeast

  # --- Inventory/Currency ---
  - Player.HasCurrency
  - Player.HasItem
  - Player.InventoryHasSpace
  - Player.BagSpaceAtLeast

  # --- Quest/Progression ---
  - Quest.Completed
  - Quest.Active
  - Achievement.Unlocked

  # --- Session ---
  - Session.LoggedIn
  - Session.CharacterSelected
  - Session.NotTransitioning

  # --- UI ---
  - UI.ScreenOpen
  - UI.NoBlockingModal

  # --- Cooldown ---
  - Interaction.CooldownReady
  - Interaction.NotAlreadyRunning

  - Always
  - Never
```

---

## 4️⃣ InteractionCost (비용)

```yaml
InteractionCost:
  costType: CostType
  currencyType: CurrencyType        # costType=Currency 전용
  itemId: string                    # costType=Item 전용
  amount: number
  consumedOn: CostConsumeTiming     # 언제 차감되는가
  refundable: boolean               # 취소 시 환불 여부

CostConsumeTiming:
  - OnStart                         # 시작 즉시
  - OnSuccess                       # 성공 시
  - OnComplete                      # 완료 시 (성공/실패 무관)
  - PeriodicDuringChannel           # 채널링 중 주기적
```

---

## 5️⃣ InteractionParam (입력 파라미터 스키마)

```yaml
InteractionParam:
  name: string                      # "destinationZoneId"
  paramType: ParamType
  required: boolean
  default: any
  validation: [ParamValidation]

ParamType:
  - ZoneId
  - PlayerId
  - MonsterId
  - ItemId
  - ItemInstanceId
  - SkillId
  - CurrencyAmount
  - Quantity
  - String
  - Number
  - Boolean
  - Vector3

ParamValidation:
  - NotEmpty
  - PositiveInteger
  - MustExist                       # 참조 ID 가 실존해야 함
  - OwnedByPlayer                   # 플레이어가 소유한 것이어야 함
  - InZone                          # 해당 Zone 에 있어야 함
  - WithinRange                     # 숫자 범위
```

---

## 6️⃣ FailReason (실패 사유)

```yaml
FailReason:
  code: FailCode                    # 실패 코드 (enum)
  severity: FailSeverity
  feedbackType: FeedbackType        # 표시 방식
  recoverable: boolean              # 재시도 가능 여부

FailCode:
  # --- 자원 ---
  - InsufficientCurrency
  - InsufficientItem
  - InsufficientResource
  - InventoryFull
  - BagSpaceInsufficient

  # --- 상태 ---
  - NotEnoughLevel
  - WrongClass
  - WrongFaction
  - InCombat
  - Dead
  - Silenced
  - Stunned

  # --- 환경 ---
  - ZoneRestricted                  # Zone 규칙 위반
  - SafeZoneViolation
  - PvPRuleViolation
  - OutOfRange
  - NotInValidLocation

  # --- 쿨다운/중복 ---
  - OnCooldown
  - AlreadyRunning
  - DuplicateRequest

  # --- 대상 ---
  - TargetNotFound
  - TargetNotValid
  - TargetBound                     # 귀속 아이템
  - TargetUnique                    # 유일 아이템 중복

  # --- 퀘스트/진행 ---
  - QuestNotCompleted
  - PrerequisiteNotMet
  - NotAvailableYet

  # --- 시스템 ---
  - NetworkError
  - ServerBusy
  - Forbidden
  - InvalidParameter
  - InstanceFull
  - InstanceClosed

  - Unknown

FailSeverity:
  - Info                            # 정보성
  - Warning                         # 경고
  - Error                           # 에러
  - Critical                        # 치명적 (세션 종료 등)
```

---

## 7️⃣ InteractionFeedback (피드백 설정)

```yaml
InteractionFeedback:
  onStart: FeedbackAction
  onProgress: FeedbackAction
  onSuccess: FeedbackAction
  onFail: FeedbackAction
  onCancel: FeedbackAction

FeedbackAction:
  type: FeedbackType
  messageKey: string                # i18n 키
  popupScreenId: string             # Popup/Modal 일 때 열 Screen ID (wiki-entity-ui.md)
  soundId: string
  vfxId: string
  durationMs: number
```

---

## 8️⃣ SideEffect (부수효과)

> "이 행위를 하면 다른 것까지 같이 변한다" 를 선언. **상황 3의 "버프 소실"이 바로 여기.**

```yaml
SideEffect:
  trigger: SideEffectTrigger
  effect: Effect                    # wiki-skill-schema.md 의 Effect
  condition: PreconditionCheck      # 조건부 발동 (optional)

SideEffectTrigger:
  - OnStart
  - OnSuccess
  - OnFail
  - OnZoneChange                    # Zone 전환이 일어날 때
  - OnInstanceEnter                 # 인스턴스 입장 시
  - OnInstanceExit
  - OnCombatStateChange
  - OnMountChange
```

**예시 — 던전 입장 시 특정 버프 제거:**

```yaml
sideEffects:
  - trigger: OnInstanceEnter
    effect:
      target: Caster
      operation: RemoveState
      attribute: State
      value: state.city_blessing
      duration: 0
    condition: Always
```

---

## 9️⃣ ExecutionContext (실행 컨텍스트)

> "어디서 이 행위를 할 수 있는가".

```yaml
ExecutionContext:
  - FromUI.WorldMap
  - FromUI.Shop
  - FromUI.Inventory
  - FromUI.QuestWindow
  - FromUI.DungeonFinder
  - FromUI.AuctionHouse
  - FromUI.CharacterSelect
  - FromWorld.NPCInteraction
  - FromWorld.ObjectInteraction
  - FromHotkey
  - FromScript                      # 시스템 자동
  - FromMail
  - FromChat
```

---

## 🔟 InteractionFlow (복합 절차)

> 여러 Interaction + UI Screen 을 엮은 **시나리오 수준**. wiki-entity-ui.md 의 NavigationFlow 와 짝을 이룸.

```yaml
InteractionFlow:
  id: string
  name: string
  steps: [FlowStep]
  rollbackOnFail: boolean           # 중간 실패 시 이전 상태로 복구

FlowStep:
  stepOrder: number
  interactionId: string             # 실행할 Interaction
  onSuccess: string                 # 다음 stepOrder 또는 "END"
  onFail: string                    # 실패 시 이동할 step
  timeout: number                   # 타임아웃 (초)
```

---

## 1️⃣1️⃣ 완전한 예시

### 예시 1 — 텔레포트 (월드맵에서 지점 선택)

```yaml
Interaction:
  id: interaction.teleport
  name: "Teleport to Zone"
  version: "1.0.0"

  category: Movement
  type: Atomic
  executionMode: Timed
  targetSelectionMode: FromUIList

  preconditions:
    - condition: Player.Alive
      expected: true
      reason: CannotTeleportWhileDead
      priority: 1
      bypassable: false
    - condition: Player.NotInCombat
      expected: true
      reason: InCombat
      priority: 2
      bypassable: false
    - condition: Zone.AllowsAction
      expected: "Teleport"
      reason: ZoneRestricted
      priority: 3
      bypassable: false
    - condition: Player.HasCurrency
      expected: "Gold:100"
      reason: InsufficientCurrency
      priority: 4
      bypassable: false

  costs:
    - costType: Currency
      currencyType: Gold
      amount: 100
      consumedOn: OnSuccess
      refundable: false

  parameters:
    - name: destinationZoneId
      paramType: ZoneId
      required: true
      validation:
        - NotEmpty
        - MustExist

  castDuration: 5
  cancelableWhileCasting: true
  interruptOnDamage: true
  interruptOnMove: true

  effectsOnStart:
    - target: Caster
      operation: AddState
      attribute: State
      value: state.teleporting
      duration: 5

  effectsOnSuccess:
    - target: Caster
      operation: Set
      attribute: Position
      value: "$destinationZone.entryPoint"
      duration: 0
    - target: Caster
      operation: RemoveState
      attribute: State
      value: state.teleporting
      duration: 0

  effectsOnCancel:
    - target: Caster
      operation: RemoveState
      attribute: State
      value: state.teleporting
      duration: 0

  failReasons:
    - code: CannotTeleportWhileDead
      severity: Error
      feedbackType: Popup
      recoverable: true
    - code: InCombat
      severity: Warning
      feedbackType: Toast
      recoverable: true
    - code: ZoneRestricted
      severity: Error
      feedbackType: Popup
      recoverable: false
    - code: InsufficientCurrency
      severity: Error
      feedbackType: Popup
      recoverable: true

  feedback:
    onStart:
      type: VisualEffect
      vfxId: vfx.teleport_charge
      durationMs: 5000
    onSuccess:
      type: VisualEffect
      vfxId: vfx.teleport_arrive
      durationMs: 1500
    onFail:
      type: Popup
      messageKey: msg.teleport_failed
      popupScreenId: screen.error_popup
    onCancel:
      type: Toast
      messageKey: msg.teleport_canceled

  sideEffects:
    - trigger: OnSuccess
      effect:
        target: Caster
        operation: RemoveState
        attribute: State
        value: state.city_blessing

  allowedContexts:
    - FromUI.WorldMap
    - FromHotkey

  logged: true
  analyticsEvent: "player.teleport"
```

### 예시 2 — 상점에서 아이템 구매

```yaml
Interaction:
  id: interaction.purchase_item
  name: "Purchase Item from Shop"

  category: Commerce
  type: Staged
  executionMode: Interactive
  targetSelectionMode: FromUIList

  preconditions:
    - condition: UI.ScreenOpen
      expected: "screen.shop"
      reason: ShopNotOpen
      priority: 1
    - condition: Player.InventoryHasSpace
      expected: true
      reason: InventoryFull
      priority: 2
    - condition: Player.HasCurrency
      expected: "$item.buyPrice"
      reason: InsufficientCurrency
      priority: 3

  costs:
    - costType: Currency
      currencyType: Gold
      amount: 0                     # 동적 ($item.buyPrice)
      consumedOn: OnSuccess
      refundable: false

  parameters:
    - name: itemId
      paramType: ItemId
      required: true
      validation: [NotEmpty, MustExist]
    - name: quantity
      paramType: Quantity
      required: true
      default: 1
      validation: [PositiveInteger]

  castDuration: 0
  cancelableWhileCasting: false

  effectsOnSuccess:
    - target: Caster
      operation: Subtract
      attribute: Resource
      value: "$totalCost"
    - target: Caster
      operation: Add
      attribute: Inventory
      value: "$item"                # quantity 만큼

  failReasons:
    - code: InsufficientCurrency
      severity: Error
      feedbackType: Popup
      recoverable: true
    - code: InventoryFull
      severity: Warning
      feedbackType: Popup
      recoverable: true

  feedback:
    onSuccess:
      type: Toast
      messageKey: msg.purchase_success
      soundId: sound.coin
    onFail:
      type: Popup
      messageKey: msg.purchase_failed
      popupScreenId: screen.insufficient_currency_popup

  allowedContexts:
    - FromUI.Shop

  logged: true
  analyticsEvent: "shop.purchase"
```

### 예시 3 — 던전 입장 (버프 소실 포함)

```yaml
Interaction:
  id: interaction.enter_dungeon
  name: "Enter Dungeon"

  category: Instance
  type: Composite
  executionMode: Timed
  targetSelectionMode: FromUIList

  preconditions:
    - condition: Player.LevelAtLeast
      expected: "$dungeon.requiredLevel"
      reason: NotEnoughLevel
      priority: 1
    - condition: Quest.Completed
      expected: "$dungeon.requiredQuest"
      reason: QuestNotCompleted
      priority: 2
    - condition: Player.NotInCombat
      expected: true
      reason: InCombat
      priority: 3

  costs:
    - costType: Free
      amount: 0

  parameters:
    - name: dungeonZoneId
      paramType: ZoneId
      required: true
      validation: [NotEmpty, MustExist]

  castDuration: 3
  cancelableWhileCasting: true
  interruptOnDamage: false

  effectsOnStart:
    - target: Caster
      operation: AddState
      attribute: State
      value: state.entering_instance
      duration: 3

  effectsOnSuccess:
    - target: Caster
      operation: Set
      attribute: zoneId
      value: "$dungeonZoneId"
    - target: Caster
      operation: Set
      attribute: Position
      value: "$dungeon.entryPoint"

  failReasons:
    - code: NotEnoughLevel
      severity: Error
      feedbackType: Popup
      recoverable: false
    - code: QuestNotCompleted
      severity: Error
      feedbackType: Popup
      recoverable: false
    - code: InstanceFull
      severity: Warning
      feedbackType: Popup
      recoverable: true

  feedback:
    onStart:
      type: Modal
      messageKey: msg.entering_dungeon
      popupScreenId: screen.loading
    onSuccess:
      type: VisualEffect
      vfxId: vfx.portal_arrive

  sideEffects:
    - trigger: OnInstanceEnter
      effect:
        target: Caster
        operation: RemoveState
        attribute: State
        value: state.city_blessing
    - trigger: OnInstanceEnter
      effect:
        target: Caster
        operation: RemoveState
        attribute: State
        value: state.well_fed
      condition: Zone.TypeIsOneOf   # "Raid" 일 때만 제거 등

  allowedContexts:
    - FromUI.DungeonFinder
    - FromWorld.ObjectInteraction

  logged: true
  analyticsEvent: "dungeon.enter"
```

### 예시 4 — 복합 Flow (월드맵 텔레포트 시나리오)

```yaml
InteractionFlow:
  id: flow.world_map_teleport
  name: "WorldMapTeleportScenario"
  rollbackOnFail: false

  steps:
    - stepOrder: 1
      interactionId: interaction.open_world_map
      onSuccess: "2"
      onFail: "END"
      timeout: 5

    - stepOrder: 2
      interactionId: interaction.select_teleport_point
      onSuccess: "3"
      onFail: "END"
      timeout: 60

    - stepOrder: 3
      interactionId: interaction.confirm_teleport
      onSuccess: "4"
      onFail: "2"                   # 재선택으로 돌아감
      timeout: 10

    - stepOrder: 4
      interactionId: interaction.teleport
      onSuccess: "END"
      onFail: "END"
      timeout: 15
```

---

## 1️⃣2️⃣ 불변식 (Invariants)

```yaml
Invariant:
  - rule: "executionMode=Channeled 이면 cancelableWhileCasting=true"
  - rule: "type=Irreversible 이면 effectsOnCancel 는 비어있어야 함"
  - rule: "costs[].consumedOn=OnStart 이면 refundable 정의 필수"
  - rule: "preconditions[].reason 값은 failReasons[].code 에 존재하거나 시스템 예약 태그여야 함"
  - rule: "parameters[].required=true 인 파라미터는 사용 시 반드시 제공되어야 함"
  - rule: "targetSelectionMode=NoTarget 이면 parameters 에 target 계열 없음"
  - rule: "allowedContexts 가 비어있으면 어떤 컨텍스트에서도 실행 불가 (시스템 전용)"
  - rule: "sideEffects[].trigger=OnInstanceEnter 이면 category=Instance"
  - rule: "feedback.onFail 은 failReasons 가 비어있지 않으면 반드시 정의"
  - rule: "InteractionFlow.steps 의 stepOrder 는 중복 불가, 연속 정수"
  - rule: "InteractionFlow.steps[].interactionId 는 실존 Interaction"
  - rule: "costs[].currencyType 은 costType=Currency 일 때만 의미"
```

---

## 🔗 관련 문서

- [wiki-schema-guide.md](wiki-schema-guide.md) — 스키마 설계 철학
- [wiki-entity-ui.md](wiki-entity-ui.md) — 화면이 유발하는 Interaction
- [wiki-entity-item.md](wiki-entity-item.md) — 구매/판매 대상
- [wiki-entity-zone.md](wiki-entity-zone.md) — 텔레포트/던전 진입 대상
- [wiki-entity-quest.md](wiki-entity-quest.md) — 퀘스트 완료/수락 Interaction
- [wiki-entity-session.md](wiki-entity-session.md) — 로그인/캐릭터 선택 Interaction
- [wiki-entity-player.md](wiki-entity-player.md) — Precondition 의 주요 검증 대상
- [wiki-skill-schema.md](wiki-skill-schema.md) — Effect 구조 재사용
