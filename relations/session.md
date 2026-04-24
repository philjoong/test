# Relations — Session 의 Outgoing Edges

> Session (및 Party / Raid / Guild / Instance / Battleground) 이 다른 엔티티를 참조하는 모든 edge. Edge Kind 정의는 [../wiki-relations.md](../wiki-relations.md) §1 참조.

---

## Session → 외부

```yaml
- from: Session.activeCharacterId
  to:   Player.id
  kind: IdReference
- from: Session.availableCharacterIds[]
  to:   Player.id
  kind: IdReference

- from: Session.partyId
  to:   Session.Party.partyId
  kind: IdReference
- from: Session.raidId
  to:   Session.Raid.raidId
  kind: IdReference
- from: Session.guildId
  to:   Session.Guild.guildId
  kind: IdReference
- from: Session.battlegroundId
  to:   Session.Battleground.bgId
  kind: IdReference

- from: Session.currentInstanceId
  to:   Session.Instance.instanceId
  kind: IdReference

- from: Session.currentScreenStack[]
  to:   UI.Screen.id
  kind: IdReference

- from: Session.pendingNotifications[].severity
  to:   Interaction.FailSeverity
  kind: EnumReuse

- from: Session.Party.members[].sessionId
  to:   Session.sessionId
  kind: Membership
- from: Session.Party.members[].characterId
  to:   Player.id
  kind: Membership
- from: Session.Party.leaderId
  to:   Player.id
  kind: IdReference
- from: Session.Party.targetInstanceId
  to:   Session.Instance.instanceId
  kind: IdReference

- from: Session.Raid.subParties[].members[].characterId
  to:   Player.id
  kind: Membership

- from: Session.Guild.members[].characterId
  to:   Player.id
  kind: Membership
- from: Session.Guild.members[].guildRank
  to:   Session.Guild.ranks[].name
  kind: IdReference

- from: Session.Instance.zoneId
  to:   Zone.id
  kind: IdReference
- from: Session.Instance.ownerGroupId
  to:   Session.Party.partyId        # 또는 Raid.raidId
  kind: IdReference
- from: Session.Instance.participants[]
  to:   Player.id
  kind: Membership
- from: Session.Instance.bossesKilled[].bossId
  to:   Monster.templateId
  kind: TemplateReference
- from: Session.Instance.bossesKilled[].lootGenerated[]
  to:   Item.ItemInstance.instanceId
  kind: IdReference
- from: Session.Instance.savedForCharacters[]
  to:   Player.id
  kind: IdReference

- from: Session.Battleground.teams[].members[]
  to:   Player.id
  kind: Membership
- from: Session.Battleground.zoneId
  to:   Zone.id
  kind: IdReference

- from: Session.<any state transition>
  to:   Interaction.id
  kind: InteractionTrigger
  note: "로그인/캐릭터선택/파티가입 등 모든 Session 전이는 Interaction 을 통함"
```
