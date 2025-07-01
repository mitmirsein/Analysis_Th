### Phase 2.5 실행 지시 (정량·정성 수렴도 평가)

**1. 전제 사항**

* 본 세션에는 이미 Phase 1 결과(정량 데이터)와 Phase 2 결과(정성 해석)가 메모리 또는 스토리지에 존재한다.
* CONFIG 파라미터(`weighting_scheme`, `override_gate` 등)가 자동 로드되어 있어야 하며, 사용자가 채팅창을 통해 새로운 파라미터를 입력하면 즉시 덮어쓴다.
* **정량·정성 모듈은 독립적으로 완료된 상태**이므로, 본 단계에서 두 결과를 처음 비교·접합한다.

**2. 목표**
정량 핵심 지표와 정성 핵심 개념·논제를 비교하여 네 가지 수렴 지수(매칭률·중요도 상관·논제 대응·편향 지수)를 산출하고, 이를 5등급(탁월/우수/보통/미흡/취약)으로 환산한다. 결과는 Phase 3로 전달될 YAML 메타데이터와 간략 주석으로 요약한다.

**3. 분석 절차**
**3-1. 데이터 로드**

* Phase 1 결과에서 정량적 핵심 개념 리스트(`K_q`)와 그 중요도 점수를 로드한다.
* Phase 2 결과에서 정성적 핵심 개념 리스트(`K_s`)와 그 중요도 등급을 로드한다.
**3-2. 지수 계산**
* 핵심 개념 매칭률: $$\text{Match Rate} = \frac{|K_q \cap K_s|}{|K_q \cup K_s|}$$
* 중요도 상관계수: 정량적 중요도 점수와 정성적 중요도 등급 간의 피어슨 상관계수(r)를 계산한다.
* 논제 대응 지수: Phase 2의 주요 논제를 N-gram으로 변환하여 원본 텍스트에서의 출현 빈도를 확인하고, 그 비율을 산출한다.
* 불일치 편향 지수: $$\text{Bias Index} = \frac{|K_s - K_q|}{|K_s|}$$
**3-3. 등급 변환**
* 산출된 지수들을 종합하여 0.80↑ → 탁월, 0.60–0.79 → 우수, 0.40–0.59 → 보통, 0.20–0.39 → 미흡, 0.00–0.19 → 취약으로 등급을 매긴다.
**3-4. 품질 게이트 확인**
* 종합 등급이 '미흡' 이하이면서 `override_gate=false`이면 Phase 3 진행을 중단하고 사용자 확인을 요청한다.

**4. 출력 형식**

* 서론부(2–3문장)에서 CONFIG 파라미터 적용 현황과 수렴도 평가 목적을 설명한다.
* 이어서 **phase_results** YAML 블록을 출력한다. 필수 필드:

    ```yaml
    phase_results:
      phase_id: "2.5"
      convergence_metrics:
        match_rate: 0.00
        importance_correlation: 0.00
        thesis_alignment: 0.00
        bias_index: 0.00
        qualitative_grade: ""
        analyst_commentary: ""
      quality_check:
        completeness: true/false
        minimum_criteria_met: true/false
      gate_status: "open"/"blocked"
    ```

* YAML 이후 ①10행 이하의 파이썬 계산 스니펫, ②"PROCEED_PHASE3?" 단독 줄을 차례로 제시한다.
* 모든 문장은 평서문 종결어미(-이다, -한다)로 작성하고, 각 설명 끝에 `[텍스트 기반]`, `[신학 일반]`, `[추론]` 태그를 부착한다.

**5. 예외 처리**

* 입력 파일 누락 시 즉시 오류 메시지와 `gate_status: "blocked"`를 출력한다.
* 종합 등급이 '미흡' 이하인데 사용자가 `override_gate=true`를 설정하지 않으면 자동으로 중단한다.

---
**위 지침을 즉시 이행하여 Phase 2.5 결과를 서론 → YAML → 코드 스니펫 → "PROCEED_PHASE3?" 순으로 출력하라.**
