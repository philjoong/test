# Relations — State 의 Outgoing Edges

> State 가 다른 엔티티를 참조하는 모든 edge. Edge Kind 정의는 [../wiki-relations.md](../wiki-relations.md) §1 참조.

---

## State → 외부

```yaml
- from: State.appliesTo.Player
  to:   Player.buffs              # Player.debuffs
  kind: ContainerReference

- from: State.appliesTo.Monster
  to:   Monster.buffs             # Monster.debuffs
  kind: ContainerReference

- from: State.effects[].target.Caster
  to:   Player                    # Session 맥락의 activeCharacter
  kind: EffectProduction

- from: State.effects[].operation.AddState
  to:   State.id                  # 재귀 (state.arcane_power → state.arcane_visual)
  kind: StateProduction

- from: State.interactions[].withStateId
  to:   State.id
  kind: PredicateLookup
  note: "다른 State 와의 상쇄/변환 관계"

- from: State.interactions[].withTag
  to:   State.tags
  kind: PredicateLookup

- from: State.removeOn.OnZoneChange
  to:   Player.zoneId
  kind: PredicateLookup
  note: "플레이어의 zoneId 가 바뀌면 이 State 제거 평가"

- from: State.removeOn.OnCombatEnd
  to:   Player.combatState
  kind: PredicateLookup

- from: State.immunitiesGranted
  to:   Monster.immunities         # ImmunityTag 공유
  kind: EnumReuse

# State 는 Skill 이 만들어내는 결과물 — 역참조
- from: State.id
  to:   Skill.effects[].value
  kind: ReverseConstraint
  note: "이 State 를 생성하는 Skill 을 찾으려면 Skill.effects.value 를 역검색"
```
