# Relations — Interaction 의 Outgoing Edges

> Interaction (및 InteractionFlow) 이 다른 엔티티를 참조하는 모든 edge. Edge Kind 정의는 [../wiki-relations.md](../wiki-relations.md) §1 참조.

---

## Interaction → 외부

```yaml
- from: Interaction.preconditions[].condition.Player.*
  to:   Player.<field>             # Alive/NotInCombat/Level/Class/...
  kind: PredicateLookup
- from: Interaction.preconditions[].condition.Zone.*
  to:   Zone.<field>               # TypeIsOneOf/AllowsAction/SafetyLevelAtLeast
  kind: PredicateLookup
- from: Interaction.preconditions[].condition.Player.HasCurrency
  to:   Item.CurrencyAccount.balances
  kind: PredicateLookup
- from: Interaction.preconditions[].condition.Player.HasItem
  to:   Item.ItemInstance.templateId
  kind: PredicateLookup
- from: Interaction.preconditions[].condition.Quest.Completed
  to:   Quest.QuestLog.completedQuestIds
  kind: PredicateLookup
- from: Interaction.preconditions[].condition.Session.*
  to:   Session.<field>
  kind: PredicateLookup
- from: Interaction.preconditions[].condition.UI.ScreenOpen
  to:   UI.Screen.id               # Session.currentScreenStack 경유
  kind: PredicateLookup

- from: Interaction.costs[].currencyType
  to:   Item.CurrencyType
  kind: EnumReuse
- from: Interaction.costs[].itemId
  to:   Item.ItemTemplate.id
  kind: IdReference

- from: Interaction.parameters[].paramType.ZoneId
  to:   Zone.id
  kind: IdReference
- from: Interaction.parameters[].paramType.PlayerId
  to:   Player.id
  kind: IdReference
- from: Interaction.parameters[].paramType.ItemId
  to:   Item.ItemTemplate.id
  kind: IdReference
- from: Interaction.parameters[].paramType.ItemInstanceId
  to:   Item.ItemInstance.instanceId
  kind: IdReference
- from: Interaction.parameters[].paramType.SkillId
  to:   Skill.id
  kind: IdReference

- from: Interaction.effectsOnSuccess
  to:   Skill.Effect
  kind: StructureReuse
- from: Interaction.effectsOnStart
  to:   Skill.Effect
  kind: StructureReuse
- from: Interaction.effectsOnCancel
  to:   Skill.Effect
  kind: StructureReuse
- from: Interaction.effectsOnFail
  to:   Skill.Effect
  kind: StructureReuse
- from: Interaction.sideEffects[].effect
  to:   Skill.Effect
  kind: StructureReuse

- from: Interaction.sideEffects[].effect.operation.RemoveState
  to:   State.id
  kind: StateConsumption
  note: "던전 입장 시 버프 소실 — Session.Instance 전환과 연동"

- from: Interaction.feedback.*.popupScreenId
  to:   UI.Screen.id
  kind: InteractionTrigger          # 방향이 UI 로 가는 드문 케이스

- from: Interaction.InteractionFlow.steps[].interactionId
  to:   Interaction.id
  kind: FlowLink
```
