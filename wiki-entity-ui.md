# UI Schema (UI/화면/네비게이션 스키마)

> 게임 내 "화면과 화면 사이의 흐름"을 AI가 이해하기 위한 추상 네비게이션 스키마.
> 위젯 트리(버튼/리스트의 픽셀 위치)는 **다루지 않는다** — 대신 **Screen × Transition × Input** 로 흐름을 표현한다.
> QA 관점의 핵심: "이 입력을 넣으면 어느 화면으로 가는가?" "이 화면에 들어가기 위한 조건은 뭐인가?"

---

## 🎯 설계 원칙

1. UI 는 **상태 기계(State Machine)** 로 본다: Screen 이 상태, Transition 이 전이.
2. 위젯의 픽셀 좌표 · 렌더링 세부는 저장하지 않는다.
3. 대신 **어떤 입력(Input)이 어떤 전이(Transition)를 유발**하는지 원자 단위로 정의한다.
4. **중첩 가능성**: 팝업/모달은 Screen 위에 쌓이는 **ScreenLayer** 로 표현한다.
5. UI 가 촉발하는 실제 게임 행위는 **Interaction 스키마**(wiki-entity-interaction.md)로 넘긴다.

---

## 1️⃣ 분류 축 (Classification Axes)

### Axis.ScreenType — 화면 유형

```yaml
ScreenType:
  - HUD                 # 게임 플레이 중 상시 표시
  - MainMenu            # 최상위 메뉴
  - SubMenu             # 하위 메뉴
  - Modal               # 전체를 막는 팝업 (확인 전 조작 불가)
  - Popup               # 비차단 팝업 (알림/토스트)
  - Overlay             # 반투명 겹침 화면 (월드맵 등)
  - Panel               # 화면 일부 패널 (인벤토리/상점)
  - Tooltip             # 마우스오버 정보창
  - LoadingScreen       # 로딩 화면
  - CinematicScreen     # 컷신/연출
  - InputPrompt         # 입력 대기 (이름 입력 등)
```

### Axis.ScreenCategory — 기능 분류

```yaml
ScreenCategory:
  - Navigation          # 월드맵/미니맵/던전목록
  - Combat              # 전투 HUD/스킬바
  - Inventory           # 가방/장비
  - Shop                # 상점/거래소
  - Social              # 파티/길드/친구
  - Quest               # 퀘스트 창
  - Character           # 캐릭터 정보/스탯
  - Settings            # 옵션
  - System              # 로그인/선택/종료
  - Notification        # 알림/경고
  - Tutorial            # 튜토리얼
```

### Axis.LayerType — 레이어 깊이

```yaml
LayerType:
  - World               # 게임 월드 (가장 아래)
  - HUD                 # 상시 HUD
  - Menu                # 메뉴
  - Modal               # 모달 (입력 차단)
  - Popup               # 팝업 (입력 비차단)
  - Top                 # 최상위 (에러/긴급)
```

### Axis.InputBlockingMode — 입력 차단 여부

```yaml
InputBlockingMode:
  - FullBlock           # 모든 하위 입력 차단
  - PartialBlock        # 일부만 차단 (이동은 가능 등)
  - PassThrough         # 하위 입력 그대로 통과
```

### Axis.TransitionType — 전이 방식

```yaml
TransitionType:
  - Open                # 새 화면 열기 (스택에 쌓음)
  - Close               # 현재 화면 닫기 (스택에서 제거)
  - Replace             # 현재 화면을 다른 화면으로 대체
  - Push                # 네비게이션 스택에 추가
  - Pop                 # 네비게이션 스택에서 제거
  - PopToRoot           # 루트 화면까지 전부 닫기
  - Switch              # 같은 레벨 화면 간 전환
```

### Axis.InputSource — 입력 원천

```yaml
InputSource:
  - Hotkey              # 키보드 단축키
  - MouseClick          # 마우스 클릭
  - Gamepad             # 게임패드 버튼
  - Touch               # 터치
  - Voice               # 음성
  - System              # 시스템 자동 (퀘스트 완료 시 자동 팝업 등)
  - Timer               # 시간 경과
  - Event               # 게임 이벤트 (전투 시작 등)
```

### Axis.ScreenLifecycleState — 화면 생명주기

```yaml
ScreenLifecycleState:
  - NotLoaded
  - Loading
  - Opening             # 열리는 애니메이션 중
  - Active              # 사용자 조작 가능
  - Inactive            # 다른 화면 아래 가려짐
  - Closing             # 닫히는 애니메이션 중
  - Closed
```

---

## 2️⃣ Screen 엔티티 속성

```yaml
Screen:
  # --- 식별 (Identification) ---
  id: string                        # 고유 ID (예: "screen.world_map")
  name: string
  version: string

  # --- 분류 ---
  screenType: ScreenType
  screenCategory: ScreenCategory
  layerType: LayerType
  inputBlockingMode: InputBlockingMode

  # --- 생명주기 ---
  lifecycleState: ScreenLifecycleState

  # --- 진입/종료 규칙 ---
  openPreconditions: [ScreenPrecondition]
  closePreconditions: [ScreenPrecondition]

  # --- 입력 바인딩 ---
  inputBindings: [InputBinding]

  # --- 전이 가능 화면 ---
  transitions: [ScreenTransition]

  # --- 이 화면이 유발하는 Interaction ---
  triggers: [ScreenTriggerBinding]

  # --- 표시하는 데이터 ---
  dataBindings: [DataBinding]

  # --- 부모/자식 ---
  parentScreenId: string            # 이 화면이 열릴 때 아래에 깔리는 화면
  allowedChildren: [string]         # 이 화면 위에 열릴 수 있는 화면 ID

  # --- 플래그 ---
  isSingleton: boolean              # 동시에 하나만 존재 가능
  isModalBlocking: boolean          # 열리면 게임 일시정지
  pauseGameOnOpen: boolean
  cancelableByEscKey: boolean
```

---

## 3️⃣ ScreenPrecondition (진입/종료 조건)

```yaml
ScreenPrecondition:
  condition: PreconditionType
  value: string | number | boolean
  reason: string                    # 실패 사유 태그
  priority: number

PreconditionType:
  - Player.LevelAtLeast
  - Player.QuestCompleted
  - Player.HasItem
  - Player.InZone.Type              # 특정 ZoneType 일 것
  - Player.NotInCombat
  - Player.Alive
  - Session.LoggedIn
  - Session.CharacterSelected
  - Tutorial.Completed
  - UI.NoOtherModalOpen
  - Always
```

---

## 4️⃣ InputBinding (입력 → 행위)

```yaml
InputBinding:
  source: InputSource
  inputKey: string                  # "M", "Escape", "LeftClick", "Gamepad.Y"
  modifiers: [InputModifier]        # ["Ctrl", "Shift"]
  action: InputActionType           # 어떤 행위
  actionParams: object              # 행위 파라미터
  enabled: boolean
  priority: number                  # 같은 키 경합 시 우선순위

InputModifier:
  - Ctrl
  - Shift
  - Alt
  - Meta

InputActionType:
  - OpenScreen
  - CloseScreen
  - Transition                      # 다른 화면으로 전이
  - TriggerInteraction              # Interaction 스키마의 액션 실행
  - SelectItem
  - ConfirmSelection
  - Cancel
  - Navigate                        # 리스트 내 이동
  - Scroll
```

**예시 — 월드맵 단축키:**

```yaml
inputBindings:
  - source: Hotkey
    inputKey: "M"
    modifiers: []
    action: OpenScreen
    actionParams: { screenId: screen.world_map }
    enabled: true
    priority: 1

  - source: Hotkey
    inputKey: "Escape"
    modifiers: []
    action: CloseScreen
    actionParams: {}
    enabled: true
    priority: 10
```

---

## 5️⃣ ScreenTransition (화면 전이)

```yaml
ScreenTransition:
  id: string
  fromScreenId: string              # 현재 화면
  toScreenId: string                # 목적지 화면
  transitionType: TransitionType
  trigger: TransitionTrigger        # 무엇이 전이를 일으키나
  preconditions: [ScreenPrecondition]
  onTransition: [TransitionEffect]  # 전이 시 부수효과

TransitionTrigger:
  - InputBinding                    # 사용자 입력
  - SystemEvent                     # 시스템 자동 (퀘스트 완료 등)
  - Timer                           # 시간 경과
  - DataChanged                     # 데이터 조건 충족

TransitionEffect:
  - PlaySound
  - PlayAnimation
  - SaveState                       # 이전 화면 상태 보존
  - ResetState                      # 새 화면 초기화
  - DispatchInteraction             # Interaction 실행
```

---

## 6️⃣ ScreenTriggerBinding (화면이 유발하는 게임 행위)

> **UI → Interaction** 연결점. 이 화면에서 "구매 확정" 버튼이 눌리면 어떤 Interaction 이 실행되는가.

```yaml
ScreenTriggerBinding:
  triggerId: string                 # 화면 내 식별자 (예: "buyButton")
  triggerEvent: TriggerEventType    # 어떤 이벤트일 때
  interactionId: string             # 실행할 Interaction ID (wiki-entity-interaction.md 참조)
  paramMapping: object              # 화면 데이터를 Interaction 파라미터로 매핑

TriggerEventType:
  - OnClick
  - OnSelect
  - OnDoubleClick
  - OnConfirm
  - OnCancel
  - OnScreenOpen
  - OnScreenClose
  - OnTimer
```

---

## 7️⃣ DataBinding (화면이 표시하는 데이터)

```yaml
DataBinding:
  bindingId: string
  source: DataSource                # 데이터가 어디서 오는가
  refreshMode: RefreshMode
  emptyStateBehavior: EmptyStateBehavior

DataSource:
  - Player.Inventory
  - Player.Skills
  - Player.Stats
  - Player.Currency
  - Zone.Current
  - Zone.List                       # 텔레포트 가능 목록
  - Shop.Items
  - Quest.Active
  - Quest.Available
  - Dungeon.List
  - Party.Members

RefreshMode:
  - Once                            # 화면 열 때 1회
  - OnDataChange                    # 데이터 변경 시
  - Polling                         # 주기적
  - Manual

EmptyStateBehavior:
  - ShowEmptyMessage
  - ShowPlaceholder
  - HidePanel
  - BlockScreenOpen                 # 데이터 없으면 화면 자체 열리지 않음
```

---

## 8️⃣ NavigationFlow (화면 흐름 매크로)

> **여러 화면에 걸친 태스크 시나리오**. QA 의 "텔레포트 플로우" 같은 시나리오 레벨 테스트 단위.

```yaml
NavigationFlow:
  id: string
  name: string                      # "WorldMapTeleportFlow"
  description: string
  steps: [FlowStep]

FlowStep:
  stepOrder: number
  screenId: string                  # 이 단계의 화면
  action: FlowActionType            # 이 단계에서 무엇을 하는가
  expectedResult: FlowResult
  failurePath: string               # 실패 시 갈 화면 ID

FlowActionType:
  - OpenScreen
  - WaitForInput
  - Select
  - Confirm
  - TriggerInteraction
  - WaitForTransition

FlowResult:
  - ScreenOpened
  - ScreenClosed
  - InteractionSucceeded
  - InteractionFailed
  - PopupShown
```

---

## 9️⃣ 완전한 예시

### 예시 1 — 월드맵 화면

```yaml
Screen:
  id: screen.world_map
  name: "World Map"
  version: "1.0.0"

  screenType: Overlay
  screenCategory: Navigation
  layerType: Menu
  inputBlockingMode: FullBlock

  lifecycleState: NotLoaded

  openPreconditions:
    - condition: Player.Alive
      value: true
      reason: CannotOpenMapWhileDead
      priority: 1
    - condition: UI.NoOtherModalOpen
      value: true
      reason: ModalAlreadyOpen
      priority: 2

  closePreconditions:
    - condition: Always
      value: true
      reason: AlwaysClosable
      priority: 1

  inputBindings:
    - source: Hotkey
      inputKey: "M"
      action: CloseScreen
      priority: 1
    - source: Hotkey
      inputKey: "Escape"
      action: CloseScreen
      priority: 2
    - source: MouseClick
      inputKey: "LeftClick"
      action: SelectItem
      actionParams: { targetType: TeleportPoint }
      priority: 3

  transitions:
    - id: trans.wm_to_teleport_confirm
      fromScreenId: screen.world_map
      toScreenId: screen.teleport_confirm_popup
      transitionType: Open
      trigger: InputBinding
      preconditions:
        - condition: Always
          value: true
          reason: TeleportPointSelected
          priority: 1

  triggers:
    - triggerId: teleportPoint
      triggerEvent: OnClick
      interactionId: interaction.teleport
      paramMapping:
        destinationZoneId: "$selectedPoint.zoneId"

  dataBindings:
    - bindingId: availableTeleportPoints
      source: Zone.List
      refreshMode: Once
      emptyStateBehavior: ShowEmptyMessage

  parentScreenId: screen.hud
  allowedChildren:
    - screen.teleport_confirm_popup
    - screen.tooltip

  isSingleton: true
  isModalBlocking: false
  pauseGameOnOpen: false
  cancelableByEscKey: true
```

### 예시 2 — 상점 구매 → 재화 부족 팝업

```yaml
Screen:
  id: screen.shop
  name: "Shop"
  screenType: Panel
  screenCategory: Shop
  layerType: Menu
  inputBlockingMode: PartialBlock

  openPreconditions:
    - condition: Player.NotInCombat
      value: true
      reason: CannotShopInCombat
      priority: 1

  inputBindings:
    - source: Hotkey
      inputKey: "B"
      action: OpenScreen
      actionParams: { screenId: screen.shop }
      priority: 1

  triggers:
    - triggerId: buyButton
      triggerEvent: OnClick
      interactionId: interaction.purchase_item
      paramMapping:
        itemId: "$selectedItem.id"
        quantity: "$quantityInput"

  dataBindings:
    - bindingId: shopItemList
      source: Shop.Items
      refreshMode: OnDataChange
      emptyStateBehavior: ShowEmptyMessage
    - bindingId: playerGold
      source: Player.Currency
      refreshMode: OnDataChange
      emptyStateBehavior: ShowPlaceholder

  allowedChildren:
    - screen.insufficient_currency_popup
    - screen.purchase_confirm_popup

---
Screen:
  id: screen.insufficient_currency_popup
  name: "Not Enough Currency"
  screenType: Popup
  screenCategory: Notification
  layerType: Popup
  inputBlockingMode: FullBlock

  openPreconditions:
    - condition: Always
      value: true
      reason: SystemTriggeredPopup
      priority: 1

  inputBindings:
    - source: Hotkey
      inputKey: "Escape"
      action: CloseScreen
      priority: 1
    - source: MouseClick
      inputKey: "ConfirmButton"
      action: CloseScreen
      priority: 2

  triggers: []
  dataBindings:
    - bindingId: errorMessage
      source: Session.LastErrorCode
      refreshMode: Once
      emptyStateBehavior: HidePanel

  isSingleton: true
  isModalBlocking: true
  cancelableByEscKey: true
```

### 예시 3 — 월드맵 텔레포트 NavigationFlow

```yaml
NavigationFlow:
  id: flow.world_map_teleport
  name: "WorldMapTeleportFlow"
  description: "플레이어가 월드맵을 열어 텔레포트 지점을 선택해 이동"

  steps:
    - stepOrder: 1
      screenId: screen.hud
      action: OpenScreen
      expectedResult: ScreenOpened
      failurePath: ""

    - stepOrder: 2
      screenId: screen.world_map
      action: WaitForInput
      expectedResult: ScreenOpened
      failurePath: ""

    - stepOrder: 3
      screenId: screen.world_map
      action: Select
      expectedResult: InteractionSucceeded
      failurePath: screen.teleport_unavailable_popup

    - stepOrder: 4
      screenId: screen.teleport_confirm_popup
      action: Confirm
      expectedResult: InteractionSucceeded
      failurePath: screen.insufficient_currency_popup

    - stepOrder: 5
      screenId: screen.loading
      action: WaitForTransition
      expectedResult: ScreenClosed
      failurePath: ""

    - stepOrder: 6
      screenId: screen.hud
      action: WaitForInput
      expectedResult: ScreenOpened
      failurePath: ""
```

---

## 🔟 불변식 (Invariants)

```yaml
Invariant:
  - rule: "layerType=Modal 이면 inputBlockingMode=FullBlock 이어야 함"
  - rule: "isSingleton=true 인 Screen 은 동시에 2개 이상 Active 불가"
  - rule: "parentScreenId 가 존재하면 그 Screen 의 allowedChildren 에 자신이 포함"
  - rule: "transitions[].fromScreenId 는 자기 자신이어야 함"
  - rule: "transitions[].toScreenId 는 실존 Screen 이어야 함"
  - rule: "InputBinding 에서 같은 (source, inputKey, modifiers) 는 priority 로 결정되어야 함"
  - rule: "screenType=LoadingScreen 이면 inputBindings 는 비어있거나 Cancel 만 허용"
  - rule: "screenType=Modal 이면 cancelableByEscKey 는 명시되어야 함"
  - rule: "NavigationFlow.steps 의 stepOrder 는 연속된 정수 (1,2,3,...)"
  - rule: "triggers[].interactionId 는 실존 Interaction 이어야 함 (wiki-entity-interaction.md)"
  - rule: "dataBindings[].source 가 Shop.* 이면 screenCategory=Shop"
```

---

## 🔗 관련 문서

- [wiki-schema-guide.md](wiki-schema-guide.md) — 스키마 설계 철학
- [wiki-entity-interaction.md](wiki-entity-interaction.md) — UI 가 유발하는 게임 행위
- [wiki-entity-item.md](wiki-entity-item.md) — 인벤토리/상점 데이터
- [wiki-entity-quest.md](wiki-entity-quest.md) — 퀘스트 창 데이터
- [wiki-entity-session.md](wiki-entity-session.md) — 로그인/캐릭터 선택 흐름
- [wiki-entity-player.md](wiki-entity-player.md) — 화면 진입 조건 (Level/Quest 등)
- [wiki-entity-zone.md](wiki-entity-zone.md) — 월드맵/던전 목록 데이터 원천
