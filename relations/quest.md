# Relations — Quest 의 Outgoing Edges

> Quest (Template / Instance / QuestLog) 가 다른 엔티티를 참조하는 모든 edge. Edge Kind 정의는 [../wiki-relations.md](../wiki-relations.md) §1 참조.

---

## Quest → 외부

```yaml
- from: Quest.QuestTemplate.questGiver.giverId
  to:   Monster.id                 # NPC 가 Monster 로 모델링된 경우
  kind: IdReference
- from: Quest.QuestTemplate.questGiver.startZoneId
  to:   Zone.id
  kind: IdReference
- from: Quest.QuestTemplate.questGiver.completeZoneId
  to:   Zone.id
  kind: IdReference

- from: Quest.objectives[].targetId        # ObjectiveType 에 따라 대상이 바뀜
  to:   Monster.templateId                 # KillMonster
  kind: TemplateReference
- from: Quest.objectives[].targetId
  to:   Item.ItemTemplate.id               # CollectItem / DeliverItem
  kind: IdReference
- from: Quest.objectives[].targetId
  to:   Zone.id                            # ReachLocation / InZone
  kind: IdReference
- from: Quest.objectives[].targetId
  to:   Skill.id                           # UseSkill / TrainSkill
  kind: IdReference
- from: Quest.objectives[].targetId
  to:   Interaction.id                     # CompleteInteraction
  kind: IdReference

- from: Quest.rewards[].itemId
  to:   Item.ItemTemplate.id
  kind: RewardProduction
- from: Quest.rewards[].currencyType
  to:   Item.CurrencyType
  kind: EnumReuse
- from: Quest.rewards[].unlockId
  to:   Skill.id                           # Skill 해금
  kind: RewardProduction
- from: Quest.rewards[].unlockId
  to:   Zone.id                            # Zone 해금
  kind: RewardProduction
- from: Quest.rewards[].unlockId
  to:   Interaction.id                     # Interaction 해금
  kind: RewardProduction

- from: Quest.requiredPreviousQuest[]
  to:   Quest.QuestTemplate.id
  kind: IdReference
- from: Quest.nextQuest
  to:   Quest.QuestTemplate.id
  kind: IdReference
- from: Quest.nextQuest
  to:   Quest.requiredPreviousQuest[]
  kind: ReverseConstraint

- from: Quest.requiredZone
  to:   Zone.id
  kind: IdReference

- from: Quest.acceptPreconditions[].condition
  to:   Interaction.PreconditionCheck
  kind: EnumReuse

- from: Quest.onAccept
  to:   Skill.Effect
  kind: StructureReuse
- from: Quest.onComplete
  to:   Skill.Effect
  kind: StructureReuse
- from: Quest.failureConsequences
  to:   Skill.Effect
  kind: StructureReuse

- from: Quest.QuestInstance.ownerId
  to:   Player.id
  kind: IdReference
- from: Quest.QuestInstance.templateId
  to:   Quest.QuestTemplate.id
  kind: TemplateReference

- from: Quest.QuestLog.ownerId
  to:   Player.id
  kind: IdReference
- from: Quest.QuestLog.activeQuests[]
  to:   Quest.QuestInstance
  kind: ContainerReference
```
