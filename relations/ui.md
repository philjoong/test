# Relations — UI 의 Outgoing Edges

> UI (Screen / NavigationFlow) 가 다른 엔티티를 참조하는 모든 edge. Edge Kind 정의는 [../wiki-relations.md](../wiki-relations.md) §1 참조.

---

## UI → 외부

```yaml
- from: UI.Screen.openPreconditions[].condition.Player.*
  to:   Player.<field>
  kind: PredicateLookup
- from: UI.Screen.openPreconditions[].condition.Session.*
  to:   Session.<field>
  kind: PredicateLookup

- from: UI.Screen.inputBindings[].actionParams.screenId
  to:   UI.Screen.id
  kind: IdReference
- from: UI.Screen.transitions[].fromScreenId
  to:   UI.Screen.id
  kind: IdReference
- from: UI.Screen.transitions[].toScreenId
  to:   UI.Screen.id
  kind: IdReference

- from: UI.Screen.triggers[].interactionId
  to:   Interaction.id
  kind: InteractionTrigger

- from: UI.Screen.parentScreenId
  to:   UI.Screen.id
  kind: IdReference
- from: UI.Screen.allowedChildren[]
  to:   UI.Screen.id
  kind: IdReference
- from: UI.Screen.parentScreenId
  to:   UI.Screen.allowedChildren[]
  kind: ReverseConstraint

- from: UI.Screen.dataBindings[].source.Player.Inventory
  to:   Player.inventory
  kind: PredicateLookup
- from: UI.Screen.dataBindings[].source.Player.Skills
  to:   Player.skillSlots
  kind: PredicateLookup
- from: UI.Screen.dataBindings[].source.Player.Currency
  to:   Item.CurrencyAccount
  kind: PredicateLookup
- from: UI.Screen.dataBindings[].source.Zone.Current
  to:   Zone                        # Player.zoneId 경유
  kind: PredicateLookup
- from: UI.Screen.dataBindings[].source.Zone.List
  to:   Zone                        # 텔레포트 가능 목록
  kind: PredicateLookup
- from: UI.Screen.dataBindings[].source.Quest.Active
  to:   Quest.QuestLog.activeQuests
  kind: PredicateLookup
- from: UI.Screen.dataBindings[].source.Party.Members
  to:   Session.Party.members
  kind: PredicateLookup

- from: UI.NavigationFlow.steps[].screenId
  to:   UI.Screen.id
  kind: FlowLink
- from: UI.NavigationFlow.steps[].failurePath
  to:   UI.Screen.id
  kind: FlowLink
```
