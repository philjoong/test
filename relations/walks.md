# Relations — Graph Walks

> 그래프 걷기 알고리즘 4종. 방향·깊이·엣지필터 명세. 원본은 [../wiki-relations.md](../wiki-relations.md) §5.
> Intent Routing ([../wiki-intent-routing.md](../wiki-intent-routing.md) / [../intent-routing.yaml](../intent-routing.yaml)) 에서 참조.

---

## 1. ChangeImpact — 변경 영향 분석

```yaml
Walk.ChangeImpact:
  start: <변경된 field>
  direction: incoming              # "나를 참조하는" 쪽으로 거슬러 올라감
  edgeFilter: [IdReference, TemplateReference, PredicateLookup,
               StateProduction, StateConsumption, StructureReuse, RewardProduction]
  depth: 2                         # 1홉=직접 참조, 2홉=그 참조를 또 참조하는 곳
  output: 영향받을 후보 field 리스트 (회귀 테스트 대상)
```

**예**: `Skill.effects[].value = state.burn` 를 `state.blaze` 로 바꿨다.
→ start = `State.id(state.burn)`
→ 1홉 incoming: `Player.debuffs`, `Monster.debuffs`, `Skill.effects.value`, `Quest.onAccept 중 AddState`, ...
→ 2홉: 그 Skill 을 사용하는 `Player.skillSlots`, `Monster.skillUsagePolicy`, `Quest.objectives(UseSkill)` ...

---

## 2. PredicateClosure — 술어 단계 추적

```yaml
Walk.PredicateClosure:
  start: <질문의 엔티티/조건>
  direction: outgoing
  edgeFilter: [PredicateLookup]
  depth: until_leaf                # PredicateLookup 이 더 이상 안 나올 때까지
  output: 이 조건이 결국 무엇을 읽는지 최종 근거 소스
```

**예**: "이 Interaction 을 지금 할 수 있나?"
→ `Interaction.preconditions` → `Zone.AllowsAction` → `Zone.restrictions[].action` → 최종 판정.

---

## 3. ProductionChain — 생성 연쇄

```yaml
Walk.ProductionChain:
  start: Skill.effects 또는 Item.effectsOnEquip 또는 Quest.onAccept
  direction: outgoing
  edgeFilter: [StateProduction, RewardProduction, EffectProduction]
  depth: 3
  output: "이걸 실행하면 어떤 상태/보상/효과가 생성되는가"
```

---

## 4. LifecycleTrace — 수명주기 추적

```yaml
Walk.LifecycleTrace:
  start: Session.Instance.instanceId
  direction: both
  edgeFilter: [LifecycleOwnership, Membership, IdReference]
  depth: 2
  output: "이 Instance 가 종료되면 어떤 Player/State/Item 이 어떻게 변하나"
```
