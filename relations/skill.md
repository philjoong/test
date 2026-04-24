# Relations — Skill 의 Outgoing Edges

> Skill 이 다른 엔티티를 참조하는 모든 edge. 형식·용어는 [../wiki-relations.md](../wiki-relations.md) §1 Edge Kind 카탈로그 참조.

---

## Skill → 외부

```yaml
- from: Skill.restrictions[].condition.InSafeZone
  to:   Zone.safetyLevel
  kind: PredicateLookup
  note: "안전지역 여부는 Zone 의 safetyLevel/pvpRule 로 판정"

- from: Skill.restrictions[].condition.InPvPZone
  to:   Zone.pvpRule
  kind: PredicateLookup

- from: Skill.restrictions[].condition.InDungeon
  to:   Zone.zoneType
  kind: PredicateLookup

- from: Skill.restrictions[].condition.Silenced
  to:   Player.controlState     # Monster.controlState 도 동일 (EnumReuse)
  kind: PredicateLookup

- from: Skill.restrictions[].condition.Stunned
  to:   Player.controlState
  kind: PredicateLookup

- from: Skill.restrictions[].condition.Rooted
  to:   Player.controlState
  kind: PredicateLookup

- from: Skill.restrictions[].condition.Mounted
  to:   Player.movementState
  kind: PredicateLookup

- from: Skill.restrictions[].condition.Stealthed
  to:   Player.visibilityState
  kind: PredicateLookup

- from: Skill.restrictions[].condition.CooldownReady
  to:   Player.skillSlots[].cooldownRemaining
  kind: PredicateLookup

- from: Skill.restrictions[].condition.ResourceSufficient
  to:   Player.mana             # or stamina/rage/energy (Skill.resourceType 에 따름)
  kind: PredicateLookup

- from: Skill.effects[].target.PrimaryTarget
  to:   Player.hp               # 또는 Monster.hp — attribute 에 따라 달라짐
  kind: EffectProduction

- from: Skill.effects[].operation.AddState
  to:   State.id
  kind: StateProduction
  note: "value 필드가 State.id 를 가리킴 (예: 'state.burn')"

- from: Skill.effects[].operation.RemoveState
  to:   State.id
  kind: StateConsumption

- from: Skill.interactions[].withTag
  to:   State.tags              # 또는 State.id
  kind: PredicateLookup
  note: "예: 'TargetHasState.Frozen' → State 로 역조회"

# Effect 구조체는 Interaction/State/Zone/Quest 에서 재사용됨
- from: Skill.Effect              # 스키마 구조체 자체
  to:   Interaction.effectsOnSuccess
  kind: StructureReuse
- from: Skill.Effect
  to:   State.effects
  kind: StructureReuse
- from: Skill.Effect
  to:   State.tickEffects
  kind: StructureReuse
- from: Skill.Effect
  to:   Zone.modifiers
  kind: StructureReuse
- from: Skill.Effect
  to:   Quest.onAccept            # onComplete / onAbandon / failureConsequences
  kind: StructureReuse
- from: Skill.Effect
  to:   Item.effectsOnUse         # effectsOnEquip
  kind: StructureReuse

- from: Skill.DamageType
  to:   Monster.resistances[].damageType
  kind: EnumReuse
```
