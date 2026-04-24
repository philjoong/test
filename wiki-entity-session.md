# Session Schema (세션/사회/인스턴스 수명주기 스키마)

> 로그인/캐릭터 선택/파티/길드/레이드/인스턴스 수명주기 등 **게임 플레이를 둘러싼 컨테이너** 를 AI가 이해하기 위한 스키마.
> Player 가 "누구인가"라면, Session 은 "**어떤 맥락으로 접속해 있는가**".

---

## 🎯 설계 원칙

1. **Session = 계정이 서버와 연결된 한 번의 연결**. Character 보다 상위 개념.
2. Character 는 Session 이 선택한 캐릭터 1개. Player 엔티티의 **런타임 래퍼**.
3. **Party/Raid/Guild** 는 별개 스키마지만 Session 이 어느 그룹에 속해있는지 항상 추적한다.
4. **Instance** (던전/레이드 인스턴스) 는 생성 → 진행 → 종료의 라이프사이클을 갖는다. Zone 은 장소 정의, Instance 는 그 장소의 "이번 회차".
5. 모든 Session 전이(로그인/캐릭터 선택/파티 가입)는 **Interaction** 으로 수행된다.

---

## 1️⃣ 분류 축 (Classification Axes)

### Axis.SessionState — 세션 상태

```yaml
SessionState:
  - Disconnected
  - Authenticating      # 로그인 인증 중
  - CharacterSelection  # 캐릭터 선택 화면
  - LoadingCharacter    # 캐릭터 로딩 중
  - InGame              # 게임 내
  - InLobby             # 로비 (전장 대기 등)
  - Reconnecting
  - Disconnecting
```

### Axis.ConnectionQuality — 연결 품질

```yaml
ConnectionQuality:
  - Stable
  - Unstable
  - Laggy
  - Dropped
```

### Axis.GroupType — 그룹 종류

```yaml
GroupType:
  - Solo
  - Party               # 5인 이하
  - Raid                # 6~40인
  - Battleground        # PvP 전장
  - Arena               # 경쟁 PvP
  - Guild
  - Alliance            # 길드 연합
```

### Axis.GroupRole — 그룹 내 역할

```yaml
GroupRole:
  - Leader
  - Officer             # 부관
  - Member
  - Trial               # 수습
  - Spectator
```

### Axis.LootDistribution — 분배 방식

```yaml
LootDistribution:
  - FreeForAll          # 선착순
  - RoundRobin
  - GroupLoot           # 주사위
  - MasterLoot          # 지정 분배
  - NeedBeforeGreed
  - Personal            # 개인 드롭
```

### Axis.InstanceLifecycleState — 인스턴스 수명주기

```yaml
InstanceLifecycleState:
  - NotCreated
  - Creating            # 인스턴스 생성 중
  - Ready               # 입장 대기
  - Active              # 진행 중
  - Paused              # 일시정지 (오프라인 파티 등)
  - Completing          # 보스 처치 후 마무리
  - Completed
  - Closing             # 정리 중
  - Closed
  - Abandoned           # 모든 멤버 이탈
```

### Axis.MatchmakingState — 매치메이킹 상태

```yaml
MatchmakingState:
  - NotQueued
  - Queued              # 대기열
  - Matched             # 매치 성사
  - Loading             # 인스턴스 로딩
  - InMatch
  - PostMatch
```

### Axis.ActivityType — 현재 활동 유형

```yaml
ActivityType:
  - Idle
  - Questing
  - Dungeoning
  - Raiding
  - PvPing
  - Crafting
  - Trading
  - Exploring
  - Chatting
  - AFK
```

---

## 2️⃣ Session 엔티티 속성

```yaml
Session:
  # --- 식별 ---
  sessionId: string                 # 세션 UUID
  accountId: string
  clientVersion: string
  platform: string                  # PC/Console/Mobile
  serverId: string                  # 접속 서버

  # --- 상태 ---
  sessionState: SessionState
  connectionQuality: ConnectionQuality
  connectedAt: number               # 접속 시각
  lastActivityAt: number

  # --- 현재 캐릭터 ---
  activeCharacterId: string         # 현재 선택된 Player ID
  availableCharacterIds: [string]   # 계정이 소유한 캐릭터 목록

  # --- 소속 그룹 ---
  partyId: string
  raidId: string
  guildId: string
  battlegroundId: string
  arenaTeamId: string

  # --- 현재 인스턴스 ---
  currentInstanceId: string

  # --- 매치메이킹 ---
  matchmakingState: MatchmakingState
  queuedRoles: [GroupRole]
  queueStartedAt: number

  # --- 활동 ---
  activityType: ActivityType
  idleSeconds: number

  # --- 입력 컨텍스트 ---
  currentScreenStack: [string]      # 열려있는 UI Screen ID 목록 (위→아래)

  # --- 최근 에러/알림 ---
  lastErrorCode: string
  pendingNotifications: [Notification]

  # --- 플래그 ---
  isGM: boolean
  isBot: boolean
  isNewSession: boolean             # 첫 로그인 이후 캐릭터 선택 안 함
  hasPendingTransitions: boolean    # Zone 전환 중 등
```

---

## 3️⃣ Party (파티)

```yaml
Party:
  # --- 식별 ---
  partyId: string
  createdAt: number

  # --- 멤버 ---
  members: [PartyMember]
  leaderId: string
  maxSize: number
  currentSize: number

  # --- 설정 ---
  lootDistribution: LootDistribution
  lootThreshold: Rarity             # 해당 등급 이상만 분배 대상
  masterLooterId: string
  difficultyLevel: string           # "Normal" / "Heroic" 등
  isPublic: boolean                 # 파티 찾기에 공개
  autoKickIdleSeconds: number

  # --- 목적 ---
  partyPurpose: PartyPurpose
  targetInstanceId: string          # 특정 던전 대상

  # --- 상태 ---
  isLocked: boolean                 # 인스턴스 진입 후 잠금
  instanceLocked: boolean

PartyMember:
  sessionId: string
  characterId: string
  groupRole: GroupRole
  readyState: ReadyState
  lootPassOptions: [Rarity]         # 자동 패스 등급
  joinedAt: number

PartyPurpose:
  - General
  - DungeonRun
  - RaidRun
  - PvPBattleground
  - WorldQuesting
  - Leveling
  - Achievement

ReadyState:
  - NotReady
  - Ready
  - AFK
```

---

## 4️⃣ Raid (공격대)

```yaml
Raid:
  raidId: string
  createdAt: number

  # --- 구조: 서브파티 ---
  subParties: [SubParty]
  leaderId: string
  assistantLeaderIds: [string]
  maxSize: number                   # 10/20/25/40

  # --- 설정 ---
  lootDistribution: LootDistribution
  masterLooterId: string
  difficultyLevel: string
  saveId: string                    # 주간 로그인 세이브

SubParty:
  subPartyIndex: number
  members: [PartyMember]
```

---

## 5️⃣ Guild (길드)

```yaml
Guild:
  # --- 식별 ---
  guildId: string
  name: string
  faction: string
  createdAt: number

  # --- 멤버 ---
  members: [GuildMember]
  leaderId: string
  maxMembers: number

  # --- 진척도 ---
  level: number
  experience: number
  achievements: [string]

  # --- 자원 ---
  guildBankId: string
  guildCurrency: number             # 길드 자금

  # --- 설정 ---
  ranks: [GuildRank]
  description: string
  motd: string                      # Message of the Day
  isRecruiting: boolean

GuildMember:
  characterId: string
  guildRank: string                 # GuildRank.name 참조
  joinedAt: number
  lastOnlineAt: number
  contribution: number              # 기여도
  note: string
  officerNote: string

GuildRank:
  name: string                      # "Guild Master" / "Officer" / "Member"
  rankOrder: number                 # 낮을수록 높은 권한
  permissions: [GuildPermission]

GuildPermission:
  - Invite
  - Kick
  - Promote
  - Demote
  - BankDeposit
  - BankWithdraw
  - EditNote
  - EditMotd
  - DeclareWar
  - EditRanks
```

---

## 6️⃣ Instance (인스턴스) — Zone 의 실제 회차

```yaml
Instance:
  # --- 식별 ---
  instanceId: string                # UUID
  zoneId: string                    # 어느 Zone 의 인스턴스인가 (wiki-entity-zone.md)
  createdAt: number

  # --- 수명주기 ---
  lifecycleState: InstanceLifecycleState
  startedAt: number
  completedAt: number
  closedAt: number

  # --- 소유/참여 ---
  ownerGroupId: string              # Party/Raid ID
  ownerGroupType: GroupType
  participants: [string]            # character ID 목록
  maxParticipants: number

  # --- 난이도 / 설정 ---
  difficultyLevel: string
  seed: number                      # 랜덤 시드 (절차적 던전)
  modifiers: [InstanceModifier]     # 주간 어픽스 등

  # --- 진행 상태 ---
  objectivesCompleted: [string]     # 완료한 기믹/보스 ID
  bossesKilled: [BossKillRecord]
  currentPhase: string              # 보스 페이즈

  # --- 저장/리셋 ---
  resetSchedule: string             # "Weekly Tuesday 06:00"
  savedForCharacters: [string]      # 저장된 캐릭터 (주간 잠금)

  # --- 통계 ---
  deathCount: number
  startTimeElapsed: number
  wipeCount: number

InstanceModifier:
  type: ModifierType
  value: any

ModifierType:
  - WeeklyAffix                     # 시즌 어픽스
  - MythicPlusKey
  - HardMode
  - Seasonal
  - Custom

BossKillRecord:
  bossId: string
  killedAt: number
  participants: [string]
  lootGenerated: [string]           # ItemInstance IDs
```

---

## 7️⃣ Battleground / Arena (경쟁 PvP)

```yaml
Battleground:
  bgId: string
  zoneId: string
  createdAt: number

  # --- 참가자 ---
  teams: [Team]
  maxPlayersPerTeam: number

  # --- 매치 상태 ---
  matchState: MatchState
  startedAt: number
  endedAt: number
  winningTeamIndex: number

  # --- 점수 ---
  scores: [TeamScore]

Team:
  teamIndex: number
  members: [string]
  teamFaction: string

TeamScore:
  teamIndex: number
  kills: number
  objectives: number
  score: number

MatchState:
  - WarmUp
  - InProgress
  - Ending
  - Ended
  - Cancelled
```

---

## 8️⃣ Notification (세션 알림)

```yaml
Notification:
  id: string
  notificationType: NotificationType
  severity: FailSeverity            # wiki-entity-interaction.md 재사용
  messageKey: string
  data: object
  createdAt: number
  acknowledged: boolean

NotificationType:
  - PartyInvite
  - GuildInvite
  - TradeRequest
  - DuelRequest
  - FriendRequest
  - SystemAnnouncement
  - MailReceived
  - QuestUpdate
  - AchievementUnlocked
  - ErrorMessage
  - ReconnectWarning
```

---

## 9️⃣ 완전한 예시

### 예시 1 — Session (게임 플레이 중)

```yaml
Session:
  sessionId: sess.uuid_7a8b9c
  accountId: acc.98765
  clientVersion: "1.4.2.115"
  platform: PC
  serverId: server.korea_01

  sessionState: InGame
  connectionQuality: Stable
  connectedAt: 1713000000
  lastActivityAt: 1713004500

  activeCharacterId: player.user_12345
  availableCharacterIds:
    - player.user_12345
    - player.user_12346

  partyId: party.001
  raidId: ""
  guildId: guild.phoenix
  battlegroundId: ""
  arenaTeamId: ""

  currentInstanceId: ""

  matchmakingState: NotQueued
  queuedRoles: []
  queueStartedAt: 0

  activityType: Questing
  idleSeconds: 0

  currentScreenStack:
    - screen.hud

  lastErrorCode: ""
  pendingNotifications: []

  isGM: false
  isBot: false
  isNewSession: false
  hasPendingTransitions: false
```

### 예시 2 — Party (던전 진행 전)

```yaml
Party:
  partyId: party.001
  createdAt: 1713003600

  members:
    - sessionId: sess.uuid_7a8b9c
      characterId: player.user_12345
      groupRole: Leader
      readyState: Ready
      lootPassOptions: []
      joinedAt: 1713003600
    - sessionId: sess.uuid_9d4e2f
      characterId: player.user_67890
      groupRole: Member
      readyState: Ready
      lootPassOptions: [Common, Uncommon]
      joinedAt: 1713003700

  leaderId: player.user_12345
  maxSize: 5
  currentSize: 2

  lootDistribution: NeedBeforeGreed
  lootThreshold: Uncommon
  masterLooterId: ""
  difficultyLevel: "Heroic"
  isPublic: false
  autoKickIdleSeconds: 600

  partyPurpose: DungeonRun
  targetInstanceId: ""

  isLocked: false
  instanceLocked: false
```

### 예시 3 — Raid Instance (진행 중)

```yaml
Instance:
  instanceId: raid.inst_042
  zoneId: zone.dragon_lair
  createdAt: 1713005000

  lifecycleState: Active
  startedAt: 1713005300
  completedAt: 0
  closedAt: 0

  ownerGroupId: raid.group_9987
  ownerGroupType: Raid
  participants:
    - player.user_12345
    - player.user_67890
    - player.user_11112
    # ... 20명
  maxParticipants: 20

  difficultyLevel: "Heroic"
  seed: 0
  modifiers:
    - type: WeeklyAffix
      value: "Bolstering"
    - type: WeeklyAffix
      value: "Volcanic"

  objectivesCompleted:
    - boss.drake_matriarch
    - boss.ember_lord
  bossesKilled:
    - bossId: boss.drake_matriarch
      killedAt: 1713005900
      participants: [player.user_12345, player.user_67890]
      lootGenerated: [inst.loot_001, inst.loot_002]
  currentPhase: "boss.flame_dragon.phase_2"

  resetSchedule: "Weekly Tuesday 06:00 KST"
  savedForCharacters:
    - player.user_12345
    - player.user_67890

  deathCount: 3
  startTimeElapsed: 4200
  wipeCount: 1
```

### 예시 4 — Guild

```yaml
Guild:
  guildId: guild.phoenix
  name: "Phoenix Ascendant"
  faction: Alliance
  createdAt: 1700000000

  members:
    - characterId: player.user_leader
      guildRank: "Guild Master"
      joinedAt: 1700000000
      lastOnlineAt: 1713004500
      contribution: 12400
      note: ""
      officerNote: ""
    - characterId: player.user_12345
      guildRank: "Officer"
      joinedAt: 1710000000
      lastOnlineAt: 1713004500
      contribution: 8200

  leaderId: player.user_leader
  maxMembers: 100

  level: 15
  experience: 124000
  achievements:
    - ach.guild_first_raid_clear

  guildBankId: gbank.phoenix
  guildCurrency: 540000

  ranks:
    - name: "Guild Master"
      rankOrder: 1
      permissions: [Invite, Kick, Promote, Demote, BankDeposit, BankWithdraw, EditNote, EditMotd, DeclareWar, EditRanks]
    - name: "Officer"
      rankOrder: 2
      permissions: [Invite, Kick, Promote, BankDeposit, BankWithdraw, EditNote, EditMotd]
    - name: "Member"
      rankOrder: 3
      permissions: [BankDeposit]
    - name: "Trial"
      rankOrder: 4
      permissions: []

  description: "PvE Progress Guild"
  motd: "Raid on Tuesday 20:00 KST"
  isRecruiting: true
```

---

## 🔟 불변식 (Invariants)

```yaml
Invariant:
  - rule: "sessionState=InGame 이면 activeCharacterId 가 공란이 아니어야 함"
  - rule: "sessionState=CharacterSelection 이면 activeCharacterId 는 공란"
  - rule: "activeCharacterId 는 availableCharacterIds 중 하나여야 함"
  - rule: "connectionQuality=Dropped 이면 sessionState 는 Reconnecting 또는 Disconnected"
  - rule: "partyId 와 raidId 는 동시에 값을 가질 수 없음 (둘 중 하나)"
  - rule: "currentInstanceId 가 있으면 해당 Instance 의 participants 에 activeCharacterId 포함"
  - rule: "Party.currentSize <= Party.maxSize"
  - rule: "Party.leaderId 는 members 중 한 명의 characterId"
  - rule: "Party.members 중 groupRole=Leader 인 멤버는 1명"
  - rule: "Raid.subParties 의 member 총합 = maxSize 이하"
  - rule: "Guild.members 의 guildRank 값은 모두 Guild.ranks.name 에 존재"
  - rule: "Guild.leaderId 의 guildRank.rankOrder 는 1 이어야 함"
  - rule: "Instance.lifecycleState=Active 이면 ownerGroupId 필수"
  - rule: "Instance.lifecycleState=Completed 이면 completedAt > 0"
  - rule: "Instance.savedForCharacters 에 포함된 캐릭터는 같은 주 동안 재입장 제한"
  - rule: "Battleground.matchState=InProgress 이면 teams.length >= 2"
  - rule: "matchmakingState=Queued 이면 queueStartedAt > 0"
  - rule: "currentScreenStack 의 모든 screenId 는 실존 Screen (wiki-entity-ui.md)"
```

---

## 🔗 관련 문서

- [wiki-schema-guide.md](wiki-schema-guide.md) — 스키마 설계 철학
- [wiki-entity-player.md](wiki-entity-player.md) — Session 이 소유한 캐릭터
- [wiki-entity-ui.md](wiki-entity-ui.md) — currentScreenStack 의 Screen 정의
- [wiki-entity-zone.md](wiki-entity-zone.md) — Instance 의 Zone 참조
- [wiki-entity-interaction.md](wiki-entity-interaction.md) — 로그인/캐릭터 선택/파티 가입 Interaction
- [wiki-entity-item.md](wiki-entity-item.md) — Guild Bank / Loot 분배
- [wiki-entity-quest.md](wiki-entity-quest.md) — 파티 퀘스트 공유
