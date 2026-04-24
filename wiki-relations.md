# Entity Relations (엔티티 참조 그래프) — 대문 (Index)

> 엔티티 스키마 간의 **참조 관계**를 담은 그래프 문서.
> AI 탐색의 "의미검색 대체 기반" — 한 속성이 바뀌면 어떤 속성/엔티티가 영향받는지
> 이 문서들만 보고 **홉(hop) 단위 BFS** 로 추적할 수 있다.
>
> **이 파일은 인덱스**다. 엔티티별 edge 정의는 `relations/` 하위 파일로 분리되어 있으니
> 필요한 엔티티의 것만 열어 읽으면 토큰이 절약된다.

---

## 🎯 설계 원칙

1. **Edge 단위로만 기술**: `from → to`, 둘 다 `Entity.field.subfield` 까지 정확히.
2. 엣지의 **종류(kind)** 를 enum 으로 고정 — AI 가 "왜 이 엔티티를 읽어야 하는지" 알 수 있게.
3. 본문에 등장하지 않는 추상적 관계는 **기술하지 않는다** (스키마에 실제로 적힌 것만).
4. **양방향 성질** 은 Edge 자체에 명시 (`reverseable: true` / 역참조 힌트).
5. Edge 는 **회귀 테스트의 출발점**이다 — 한 Edge 의 `to` 가 바뀌면 `from` 은 전부 재검증 후보.

---

## 1️⃣ Edge Kind 카탈로그 (참조의 종류)

```yaml
EdgeKind:
  # --- 값 / 식별자 참조 ---
  - IdReference              # 필드가 다른 엔티티의 id 를 가리킴 (Player.zoneId → Zone.id)
  - TemplateReference        # Instance 가 Template 의 id 를 가리킴 (ItemInstance.templateId → ItemTemplate.id)
  - ContainerReference       # 소유 관계 (Player.skillSlots → Skill)

  # --- 의미 / 술어 참조 ---
  - PredicateLookup          # 조건식이 다른 엔티티의 속성을 조회 (Skill.restriction.InSafeZone → Zone.safetyLevel)
  - EnumReuse                # 한 엔티티가 정의한 enum 을 다른 엔티티가 재사용 (Monster.controlState → Player.ControlState)
  - StructureReuse           # 한 엔티티가 정의한 구조체/서브스키마를 재사용 (Zone.modifiers.operation → Skill.EffectOperation)

  # --- 생성 / 소비 관계 ---
  - StateProduction          # 엔티티의 동작이 State 를 생성/부여 (Skill.effects.AddState → State.id)
  - StateConsumption         # 엔티티의 조건이 State 를 조회/소모 (Restriction.Silenced → State.stun)
  - EffectProduction         # 결과로 Effect 를 발생시킴 (Interaction.effectsOnSuccess → Effect)
  - RewardProduction         # 보상으로 대상 엔티티를 지급 (Quest.rewards.Item → ItemTemplate)

  # --- 행위 유발 ---
  - InteractionTrigger       # UI/행위가 Interaction 실행 (Screen.triggers → Interaction.id)
  - FlowLink                 # Flow 의 각 Step 이 다른 엔티티 참조 (InteractionFlow.step → Interaction.id)

  # --- 수명주기 ---
  - LifecycleOwnership       # 상위가 하위의 수명을 지배 (Instance → Zone, Session → Player)
  - Membership               # 다대일 소속 (PartyMember → Session, GuildMember → Player)

  # --- 역참조 / 가드 ---
  - ReverseConstraint        # A 가 B 를 가리키면 B 쪽에도 반드시 대응 존재 (Zone.parentZoneId ↔ Zone.subZones)
```

---

## 2️⃣ 엔티티별 Edge 파일 인덱스

> Intent Routing 은 이 인덱스에서 필요한 엔티티 파일 하나만 열면 된다.

| 엔티티    | 파일                                              | 설명                                                 |
|-----------|---------------------------------------------------|------------------------------------------------------|
| Skill     | [relations/skill.md](relations/skill.md)          | Restriction / Effect / Interaction 참조              |
| State     | [relations/state.md](relations/state.md)          | 부착 대상 / 재귀 / 해제 조건                         |
| Player    | [relations/player.md](relations/player.md)        | Zone/Skill/Item/Session 참조 + Enum 재사용 원천       |
| Monster   | [relations/monster.md](relations/monster.md)      | SkillUsagePolicy / Aggro / LootTable                 |
| Zone      | [relations/zone.md](relations/zone.md)            | parent/subZone / Portal / SpawnGroup / Modifier      |
| Item      | [relations/item.md](relations/item.md)            | Template-Instance / Currency / Socket                |
| Interaction | [relations/interaction.md](relations/interaction.md) | Precondition / Effect / SideEffect / Flow        |
| Quest     | [relations/quest.md](relations/quest.md)          | Objective / Reward / Chain                           |
| Session   | [relations/session.md](relations/session.md)      | Party / Raid / Guild / Instance / Battleground       |
| UI        | [relations/ui.md](relations/ui.md)                | Screen Transition / DataBinding / NavigationFlow     |

### 횡단 (Cross-cutting) 문서

| 문서                                             | 내용                                          |
|--------------------------------------------------|-----------------------------------------------|
| [relations/walks.md](relations/walks.md)         | ChangeImpact / PredicateClosure / ProductionChain / LifecycleTrace |
| [relations/invariants.md](relations/invariants.md) | 그래프 무결성 규칙                           |

---

## 3️⃣ 핵심 허브 (In-degree Top) — "바꾸면 위험한 노드"

> 다른 엔티티들이 가장 많이 참조하는 노드. **변경 시 회귀 테스트 범위가 넓음.**
> 허브 변경을 감지하면 Intent=ChangeImpact 로 자동 전이 권장.

```yaml
Hub:
  - node: Skill.Effect
    incoming:
      - State.effects / State.tickEffects
      - Interaction.effectsOnSuccess / effectsOnStart / effectsOnCancel / effectsOnFail / sideEffects
      - Zone.modifiers
      - Quest.onAccept / onComplete / failureConsequences
      - Item.effectsOnUse / effectsOnEquip
    note: "Effect 구조체가 바뀌면 거의 모든 엔티티가 영향"

  - node: State.id
    incoming:
      - Player.buffs / debuffs
      - Monster.buffs / debuffs
      - Skill.effects.AddState
      - Skill.effects.RemoveState
      - State.interactions
      - Interaction.sideEffects (RemoveState)
      - Item.effectsOnEquip (AddState)
      - Quest.onAccept/onComplete (AddState)

  - node: Skill.id
    incoming:
      - Player.skillSlots / skillBook
      - Monster.skillSlots / skillUsagePolicy / behaviorRules.UseSkill
      - Item.skillGranted
      - Quest.objectives (UseSkill/TrainSkill)
      - Quest.rewards.unlockId

  - node: Zone.id
    incoming:
      - Player.zoneId
      - Monster.zoneId
      - Zone.parentZoneId / subZones / portals.destinationZoneId
      - Session.Instance.zoneId
      - Session.Battleground.zoneId
      - Quest.requiredZone / questGiver.startZoneId / completeZoneId
      - Interaction.parameters (ZoneId)
      - UI.dataBindings.Zone.Current / Zone.List

  - node: Player.id
    incoming:
      - Session.activeCharacterId / availableCharacterIds
      - Session.Party/Raid/Guild.members
      - Session.Instance.participants
      - Monster.aggroTable / primaryTargetId / lootOwnerId
      - Item.ItemInstance.ownerId / CurrencyAccount.ownerId
      - Quest.QuestInstance.ownerId / QuestLog.ownerId

  - node: Item.ItemTemplate.id
    incoming:
      - Monster.lootTable
      - Zone.portals.requiresKey / Zone.requiredItem
      - Quest.objectives (CollectItem/DeliverItem) / Quest.rewards.itemId
      - Interaction.costs.itemId / parameters (ItemId)
      - Item.ItemInstance.templateId

  - node: Interaction.id
    incoming:
      - UI.Screen.triggers
      - UI.Screen.inputBindings (TriggerInteraction)
      - Interaction.InteractionFlow.steps
      - Quest.rewards.unlockId
      - Session (state transitions)

  - node: UI.Screen.id
    incoming:
      - UI.Screen.transitions / parentScreenId / allowedChildren
      - Interaction.feedback.popupScreenId
      - Session.currentScreenStack
      - UI.NavigationFlow.steps
```

---

## 4️⃣ 그래프 걷기 (Graph Walk) — [relations/walks.md](relations/walks.md)

Walk 4종 (ChangeImpact / PredicateClosure / ProductionChain / LifecycleTrace) 은
별도 파일에 분리. 자세한 방향·깊이·엣지필터 명세는 해당 파일 참조.

## 5️⃣ 불변식 — [relations/invariants.md](relations/invariants.md)

그래프 무결성 규칙.

---

## 6️⃣ AI 질의 템플릿 (Query Templates)

```yaml
Query:
  - "X 를 바꾸면 영향받는 모든 속성은?"
    → Walk.ChangeImpact(start=X)  [relations/walks.md]

  - "이 Restriction 은 결국 어느 엔티티의 무엇을 읽는가?"
    → Walk.PredicateClosure(start=Restriction.condition)

  - "이 Skill 을 쓰면 생성되는 모든 State 는?"
    → Walk.ProductionChain(start=Skill.effects, edgeFilter=[StateProduction])

  - "이 State 를 만들어내는 모든 Skill/Item/Quest 는?"
    → reverse lookup on State.id (incoming edges — relations/state.md + 타 엔티티 파일)

  - "사용되지 않는 엔티티(고아 노드) 는?"
    → incoming edges 가 0 인 노드 탐지 (설계 결함 시그널)

  - "순환 참조가 있는가?"
    → IdReference 만으로 cycle detection

  - "어떤 허브의 in-degree 가 급증했는가?"
    → 버전 간 diff — 리팩토링 필요 신호
```

---

## 🔗 관련 문서

- [wiki-schema-guide.md](wiki-schema-guide.md) — 스키마 설계 철학
- [wiki-intent-routing.md](wiki-intent-routing.md) / [intent-routing.yaml](intent-routing.yaml) — 라우팅
- [wiki-skill-schema.md](wiki-skill-schema.md)
- [wiki-entity-state.md](wiki-entity-state.md)
- [wiki-entity-player.md](wiki-entity-player.md)
- [wiki-entity-monster.md](wiki-entity-monster.md)
- [wiki-entity-zone.md](wiki-entity-zone.md)
- [wiki-entity-item.md](wiki-entity-item.md)
- [wiki-entity-interaction.md](wiki-entity-interaction.md)
- [wiki-entity-quest.md](wiki-entity-quest.md)
- [wiki-entity-session.md](wiki-entity-session.md)
- [wiki-entity-ui.md](wiki-entity-ui.md)
