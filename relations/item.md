# Relations — Item 의 Outgoing Edges

> Item (Template / Instance / Currency) 가 다른 엔티티를 참조하는 모든 edge. Edge Kind 정의는 [../wiki-relations.md](../wiki-relations.md) §1 참조.

---

## Item → 외부

```yaml
- from: Item.ItemInstance.templateId
  to:   Item.ItemTemplate.id
  kind: TemplateReference

- from: Item.ItemInstance.ownerId
  to:   Player.id
  kind: IdReference

- from: Item.ItemTemplate.effectsOnUse
  to:   Skill.Effect
  kind: StructureReuse
- from: Item.ItemTemplate.effectsOnEquip
  to:   Skill.Effect
  kind: StructureReuse

- from: Item.ItemTemplate.skillGranted
  to:   Skill.id
  kind: IdReference
  note: "장착 시 이 Skill 을 부여 (Player.skillSlots 에 런타임 주입)"

- from: Item.ItemTemplate.effectsOnEquip[].value
  to:   State.id
  kind: StateProduction
  note: "AddState operation 경유 — 장비가 특정 State 를 상시 부여"

- from: Item.ItemTemplate.setId
  to:   Item.ItemTemplate.setId    # 같은 set 끼리 묶임 (그룹 키)
  kind: IdReference

- from: Item.ItemTemplate.buyPriceCurrency
  to:   Item.CurrencyType
  kind: EnumReuse

- from: Item.CurrencyAccount.ownerId
  to:   Player.id                  # 또는 Session.accountId
  kind: IdReference

- from: Item.ItemInstance.location.containerId
  to:   Item.ItemInstance.instanceId  # 가방(Container) 이 또 다른 Item
  kind: IdReference

- from: Item.ItemInstance.sockets[].socketedItemId
  to:   Item.ItemInstance.instanceId
  kind: IdReference
```
