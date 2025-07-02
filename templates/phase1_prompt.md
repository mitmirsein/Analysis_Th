## Phase 1 실행 지시 (기초 및 데이터 분석) – Analysis_Th v1.1

### 1. 전제 사항

본 세션은 이미 Phase 0 결과(`phase_results.phase_id = 0`)와 **CONFIG** 파라미터가 메모리상에 로드돼 있다는 전제 아래 진행한다.  
`weighting_scheme`, `methodology_override`, `override_gate` 등 CONFIG 값이 Phase 1 전체에 적용되어야 하며, Phase 0에서 추천된 `recommended_methodology` **또는** `methodology_override` 값이 분석 항목 선정에 반영되었는지도 점검한다.

### 2. 목표

Phase 1의 두 핵심 항목—0) **정황 분석**과 1) **정량 분석**—을 완수한다.  
정량 분석에서는 CONFIG 의 `weighting_scheme`을 사용해 *중요도 점수*를 산출하고, 통계 유효성 기준 `$p < 0.05$` 또는 `$PMI > 3$` 를 충족한 지표만 '주요 지표'로 분류한다. 이후 단계에서 활용할 수 있도록 모든 수치·표·그래프를 **YAML 메타데이터**에 포함한다.

### 3. 세부 요구 사항

#### 3-1. 정황 분석

- 저자의 신학적 위치, 텍스트 장르, 역사·교회적 맥락, 한국/아시아 관련성을 **최소 3 단락**으로 서술한다.  
- 마지막에 200자 요약(`summary_200_chars`)을 제공한다.

#### 3-2. 정량 분석 (지표 ≥3)

- 용어 빈도 + 의미장 분석  
- 개념 네트워크 중심성 (**가중치 반영**)  
- 인용 패턴 통계 **또는** N-gram / 연어 분석 중 택일  
- 각 지표마다  
  1) 표 형태 결과  
  2) 객관적 관찰  
  3) 신학적 함의  
  4) 방법론적 한계  
  를 서술한다.  
- `statistical_validity` 서브키에 *p-value* 또는 *PMI* 값을 기재한다.

### 4. 형식 지침

1. 서론부에서 Phase 1 분석 목표와 CONFIG 적용 현황을 **2–3문장**으로 설명한다.  
2. 이어서 **phase_results** YAML 블록을 출력한다. 필수 필드:  

   ```yaml
   phase_results:
     phase_id: "1"
     contextual_findings:
       general: []
       korean_asian_context: []
     quantitative_metrics:
       basic_metrics: []
       semantic_field_analysis: []
       rhetorical_devices: []
     key_data:
       summary_200_chars: ""
     quality_check:
       minimum_criteria_met: false   # auto-calc
   ```

3. YAML 블록 뒤 **단독 줄**에 `NEXT_PHASE?` 만 출력 → 사용자 승인·파라미터 조정 기회 제공.  
4. 모든 문장은 평서문 종결어미(**-이다, -한다, -하다**)로 작성한다.  
5. 각 주장 뒤에는 `[텍스트 기반]`, `[신학 일반]`, `[추론]` 태그를 부착한다.

### 5. 오류·예외 처리

- **토큰 초과** 예상 시 Phase 1을 `1-A`(정황)와 `1-B`(정량)로 분할하고, 파일명 규칙 `[YYYYMMDD]_[id]_phase1_a.md` 를 따른다.  
- 통계 유효성 미달 지표가 **30 %** 초과하면 `quality_check.minimum_criteria_met = false` 로 표시하고 사용자 확인을 요청한다.

---

#### 프롬프트 종료 전 자가 점검

- 모든 문장이 평서문 종결어미로 끝나는가?  
- YAML 및 필수 항목이 모두 포함됐는가?  
- 할루시네이션·인용 오류가 없는가?  
- 마지막 줄에 `NEXT_PHASE?` 를 포함했는가?

---

**위 지침을 따라 Phase 1을 즉시 수행하고, 결과를 _서술 → YAML → `NEXT_PHASE?`_ 순으로 출력하라.**
