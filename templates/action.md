## 신학 콘텐츠 심층 분석 — 단계별 실행 템플릿 v1.1  

*(Last updated: 2025-07-02, synchronized with Project v1.1)*  

---

**Version history:**  

* v 1.0 (Legacy v5.2) – Phase 2.5(수렴도 평가) 신설, 통계 유효성·가중치·상충 해소 규범 추가, 진행률·품질 체크리스트 개정.
* v 1.1 – `config.yaml` 기반의 승인 로직을 반영하여 '공통 서술 지침' 업데이트.

---

**0. 파일명 규칙**  
`[YYYYMMDD]_[텍스트식별자]_phase[단계번호]_[하위단계].md`  
예: `20250701_welker_resurrection_phase2_5.md`  

---

**1. 공통 YAML 결과 템플릿(각 단계 하단 삽입):**  

```yaml
phase_results:
  phase_id: "0"            # 0, 1, 2, 2.5, 3, 4
  items_completed: []
  completeness: true

  # Phase 0 전용
  text_profile:
    genre: ""
    complexity_score: 0.0
    theological_markers: {}
    recommended_methodology: ""
    korean_context_relevance: 0.0

  # 공통
  key_data:
    summary_200_chars: ""

  # Phase 1 전용
  contextual_findings:
    general: []
    korean_asian_context: []
  quantitative_metrics:
    basic_metrics: []
    semantic_field_analysis: []
    rhetorical_devices: []
    statistical_validity:
      p_value_threshold: 0.05
      pmi_threshold: 3

  # Phase 2 전용
  core_concepts:
    linguistic_layer: []
    historical_layer: []
    cultural_layer: []
  structural_elements: []

  # Phase 2.5 전용
  convergence_metrics:
    match_rate: 0.0
    importance_correlation: 0.0
    thesis_alignment: 0.0
    bias_index: 0.0
    qualitative_grade: ""     # 탁월/우수/보통/미흡/취약
    analyst_commentary: ""

  # Phase 3 전용
  theological_insights:
    biblical_theological: []
    systematic_theological: []
    practical_theological: []
    contextual_theological: []
  ecumenical_perspectives:
    western_traditions: []
    korean_asian_traditions: []

  # Phase 4 전용
  practical_applications: []
  evaluation_scores: {}
  research_questions: []

cross_references:
  previous_phases: []
  specific_items: []

quality_check:
  completeness: true
  accuracy: true
  hallucination_check: true
  methodological_consistency: true
  korean_terminology_accuracy: true
  adaptive_depth_appropriate: true
  style_consistency: true
  minimum_criteria_met: {}
missing_elements: []

next_phase_inputs:
  required_data: []
  optional_data: []
```

---

**2. 오류 발생 시 대응 방안:**  

| 유형 | 기본 대응 | 추가 조치 |
|------|-----------|-----------|
| 토큰 초과 | 해당 Phase 세분화(예: Phase 2 → 2-A, 2-B) | 항목별 독립 실행 |
| 데이터 누락 | 직전 Phase YAML `key_data` 보강 | `missing_elements` 기반 재실행 |
| 품질 미달 | `minimum_criteria_met` 확인 | 미충족 항목만 재분석 |
| 시스템 오류 | 최근 저장 파일부터 롤백 | 자동 백업 활용 |
| 할루시네이션 감지 | `hallucination_check` 실패 항목 재검토 | 원문 대조 강화 |
| 장르 판단 실패 | 사용자 확인 요청 | 수동 장르 선택 |
| 복잡도 과대평가 | Phase 중간 재조정 | 적응형 깊이 감소 |
| 방법론 부적합 | Phase 1 후 재평가 | 방법론 전환 |
| 문체 불일치 | `style_consistency` 점검 | 평서문 종결어미로 수정 |

---

**3. 진행률·토큰 트래커(샘플):**

Phase 진행률: [■■■□□□□] 3 / 6 Phases (50 %)
항목 진행률: [■■■■■■■□□□□] 7 / 13 항목 (54 %)
누적 토큰: 8 400 / 20 000 (42 %)
현재 Phase: Phase 2.5 – 수렴도 평가  
문체 일관성: ✓ 평서문 유지  

---

**4. Phase별 실행 프롬프트:**  

모든 Phase 프롬프트는 평어체 규칙과 할루시네이션 방지 지침을 준수한다.

### **공통 서술 지침**

모든 Phase의 분석 결과는 다음 서술체 규칙을 따른다:
* **평서문 종결어미 사용**: ~이다, ~하다, ~한다
* **객관적이고 학술적인 어조 유지**
* **단정적 서술과 추정적 서술의 명확한 구분**
* **문체 일관성 점검**: 각 Phase 종료 후 문체 및 YAML 자동 점검을 실행한다.
* **누락 항목 즉시 보고**: 결과물에 대한 누락 항목을 즉시 보고하고, 결함이 있을 경우 해당 부분을 재생성한다.
* **사용자 검토 요청**: 매 Phase 종료 시 사용자에게 검토 요청 알림을 보내고, 승인(OK)을 받은 후 다음 단계로 진행한다.

---

**Phase 0 — 텍스트 프로파일링 및 방법론 선택**  
(변경 없음 – v 5.1 정의 유지)

**Phase 1 — 기초 및 데이터 분석**  
(통계 유효성 및 다언어 전처리 가이드 항목 포함, p < 0.05 또는 PMI > 3 임계값 명시)

**Phase 2 — 정성 분석**  
(변경 없음 – 독립적 해석 유지)

**Phase 2.5 — 수렴도 평가(신설)**  

```yaml
phase_config:
  key: "p2_5"
  name: "Phase 2.5: 수렴도 평가"
  inputs: ["phase1_data", "phase2_data"]
  output_key: "phase2_5_data"
```

프롬프트:  

```  
Phase 1의 `core_terms.yaml`과 Phase 2의 `qual_findings.yaml`을 비교하여 다음 네 지수를 산출한다.  
1. 핵심 개념 매칭률  
2. 중요도 상관계수  
3. 논제 대응 지수  
4. 불일치 편향 지수  

지수를 5등급으로 환산하고 한 단락 해석적 주석을 작성한다. 코드 스니펫(10행 이하)으로 계산 과정을 명시하며, 평서문 종결어미를 사용한다.  
```

**Phase 3 — 심층 분석**  
(입력 키 배열에 `phase2_5_data` 추가, 상충 해소 3단계 절차 명시)

**Phase 4 — 적용 및 종합**  
(변경 없음 – 단, 학술적 평가 매트릭스에 `convergence_grade` 연동)

---

**5. 고급 모드 옵션(업데이트):**  

```yaml
parallel_options:
  phase3:
    - thread1: item_4  # 심층 신학 검토
    - thread2: item_5  # 다전통 관점
  merge_before: phase4
  style_check: "각 스레드 병합 후 평어체 검사"

weighting_scheme_default:
  frequency: 0.40
  network_centrality: 0.35
  citation_count: 0.25
```

---

**6. 자동화 스크립트 핵심 변경:**  

```python
# Phase 2.5 자동 실행 추가
results['phase2_5'] = run_convergence_evaluation(
    results['phase1'], results['phase2']
)
```

`run_convergence_evaluation` 함수는 Match Rate, Bias Index 등을 계산하고 등급·주석을 반환한다.

---

**7. 품질 검증 체크리스트(갱신):**  

```
□ Phase 0  : 프로파일 타당성 + 평어체
□ Phase 1  : 정황 분석 200자 요약 / 정량 지표 ≥3 / 통계 유효성 기재
□ Phase 2  : 핵심 개념 ≥3 / 3층 분석 / 구조 도식 / 평어체
□ Phase 2.5: 4대 지수 산출 / 등급·주석 / 코드 스니펫 명시
□ Phase 3  : 정량 데이터 활용 / 8개 전통 분석 / 상충 해소 절차 / 평어체
□ Phase 4  : 실천 의의 4영역 / 평가 4등급 / 연구과제 ≥7 / 요약 1800자↑
□ 공통     : 할루시네이션 체크 / 원어 정확성 / 태그·문체 일관성
```

**문체 일관성 체크리스트:**  

* 모든 문장이 평서문 종결어미로 끝나는가?  
* 경어체(습니다, 합니다)가 섞여 있지 않은가?  
* 권유형(~하세요)·의문형이 부적절하게 사용되지 않았는가?  
* 인용·본문의 문체가 구분되는가?  
* 학술적 객관성이 유지되는가?  

---

**최종 제출 전 확인:**  

* 모든 Phase YAML 완성도 확보  
* 상호 참조 정확성  
* 품질 최소 기준 충족  
* 평어체 일관성  
* 사용자 승인 획득  
