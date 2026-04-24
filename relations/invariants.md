# Relations — Graph Invariants

> 엔티티 참조 그래프의 무결성 규칙. 원본은 [../wiki-relations.md](../wiki-relations.md) §6.

---

```yaml
Invariant:
  - rule: "모든 IdReference 의 to 는 실존하는 엔티티·속성이어야 함"
  - rule: "ReverseConstraint 는 양방향 일관성 검사 필수 (Zone.parentZoneId ↔ Zone.subZones 등)"
  - rule: "TemplateReference 의 to 는 반드시 Template 엔티티 (Instance 아님)"
  - rule: "StateProduction/StateConsumption 의 to 는 State.id 형식"
  - rule: "StructureReuse 는 한 쪽을 바꾸면 다른 쪽도 함께 검증해야 함 (Skill.Effect)"
  - rule: "EnumReuse 의 정의 노드(from)를 변경하면 모든 재사용처(to) 재검증 필요"
  - rule: "FlowLink 의 to 가 존재하지 않으면 Flow 자체가 데드링크"
  - rule: "Edge 의 from/to 는 스키마 문서의 실제 필드에 정확히 매핑되어야 함 (유령 참조 금지)"
```
