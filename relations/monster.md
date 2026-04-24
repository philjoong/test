# Relations — Monster 의 Outgoing Edges

> Monster 가 다른 엔티티를 참조하는 모든 edge. Edge Kind 정의는 [../wiki-relations.md](../wiki-relations.md) §1 참조.

---

## Monster → 외부

```yaml
- from: Monster.zoneId
  to:   Zone.id
  kind: IdReference

- from: Monster.skillSlots[].skillId
  to:   Skill.id
  kind: IdReference

- from: Monster.skillUsagePolicy.priorityList[].skillId
  to:   Skill.id
  kind: IdReference

- from: Monster.buffs[].id
  to:   State.id
  kind: IdReference
- from: Monster.debuffs[].id
  to:   State.id
  kind: IdReference

- from: Monster.resistances[].damageType
  to:   Skill.DamageType
  kind: EnumReuse

- from: Monster.immunities
  to:   State.tags                 # 또는 Skill.ControlType
  kind: EnumReuse

- from: Monster.aggroTable[].entityId
  to:   Player.id                  # 또는 Monster.id (펫)
  kind: IdReference

- from: Monster.primaryTargetId
  to:   Player.id
  kind: IdReference

- from: Monster.lootTable[].itemId
  to:   Item.ItemTemplate.id
  kind: IdReference

- from: Monster.lootOwnerId
  to:   Player.id                  # 또는 Session.Party.partyId
  kind: IdReference

- from: Monster.behaviorRules[].action.UseSkill
  to:   Skill.id
  kind: IdReference
```
