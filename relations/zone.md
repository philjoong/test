# Relations — Zone 의 Outgoing Edges

> Zone 이 다른 엔티티를 참조하는 모든 edge. Edge Kind 정의는 [../wiki-relations.md](../wiki-relations.md) §1 참조.

---

## Zone → 외부

```yaml
- from: Zone.parentZoneId
  to:   Zone.id
  kind: IdReference
- from: Zone.subZones[]
  to:   Zone.id
  kind: IdReference
- from: Zone.parentZoneId
  to:   Zone.subZones[]
  kind: ReverseConstraint
  note: "부모-자식 상호 일관성 (Zone invariant)"

- from: Zone.portals[].destinationZoneId
  to:   Zone.id
  kind: IdReference
- from: Zone.portals[].requiresKey
  to:   Item.ItemTemplate.id
  kind: IdReference

- from: Zone.requiredQuest
  to:   Quest.QuestTemplate.id
  kind: IdReference
- from: Zone.requiredItem
  to:   Item.ItemTemplate.id
  kind: IdReference

- from: Zone.spawnGroups[].templateIds[]
  to:   Monster.templateId
  kind: TemplateReference

- from: Zone.npcList[]
  to:   Monster.id                 # 고정 NPC (Monster 로 모델링되는 경우)
  kind: IdReference

- from: Zone.instanceId
  to:   Session.Instance.instanceId
  kind: IdReference
- from: Zone.ownerId
  to:   Session.Party.partyId      # 또는 Raid.raidId / Player.id
  kind: IdReference

- from: Zone.modifiers[].operation
  to:   Skill.EffectOperation
  kind: EnumReuse
- from: Zone.modifiers[].condition
  to:   Monster.BehaviorCondition
  kind: EnumReuse

- from: Zone.restrictions[].action
  to:   Interaction.allowedContexts    # Teleport/Duel/Trade 등과 의미적 대응
  kind: PredicateLookup

- from: Zone.activeEvents[].modifiers
  to:   Zone.modifiers
  kind: StructureReuse
```
