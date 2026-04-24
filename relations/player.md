# Relations — Player 의 Outgoing Edges

> Player 가 다른 엔티티를 참조하는 모든 edge. Edge Kind 정의는 [../wiki-relations.md](../wiki-relations.md) §1 참조.

---

## Player → 외부

```yaml
- from: Player.zoneId
  to:   Zone.id
  kind: IdReference

- from: Player.instanceId
  to:   Session.Instance.instanceId
  kind: IdReference

- from: Player.skillSlots[].skillId
  to:   Skill.id
  kind: IdReference

- from: Player.skillBook[]
  to:   Skill.id
  kind: IdReference

- from: Player.buffs[].id
  to:   State.id
  kind: IdReference
- from: Player.debuffs[].id
  to:   State.id
  kind: IdReference

- from: Player.buffs[].source
  to:   Skill.id                   # 또는 Item.id (effectsOnEquip 경유)
  kind: IdReference

- from: Player.equipment.*
  to:   Item.ItemInstance.instanceId
  kind: IdReference

- from: Player.inventory[]
  to:   Item.ItemInstance
  kind: ContainerReference

- from: Player.partyId
  to:   Session.Party.partyId
  kind: IdReference
- from: Player.guildId
  to:   Session.Guild.guildId
  kind: IdReference
- from: Player.raidId
  to:   Session.Raid.raidId
  kind: IdReference

- from: Player.controlState       # enum 정의처
  to:   Monster.controlState
  kind: EnumReuse
- from: Player.LifeState
  to:   Monster.lifeState
  kind: EnumReuse
- from: Player.CombatState
  to:   Monster.combatState
  kind: EnumReuse
- from: Player.MovementState
  to:   Monster.movementState
  kind: EnumReuse
- from: Player.VisibilityState
  to:   Monster.visibilityState
  kind: EnumReuse

- from: Player.actionRestrictions[].condition.InSafeZone
  to:   Zone.safetyLevel
  kind: PredicateLookup
- from: Player.actionRestrictions[].condition.InPvPZone
  to:   Zone.pvpRule
  kind: PredicateLookup
```
