### 세션 초기화 및 Phase 0 실행 지시

**1. 첨부 파일 역할 지정**

* `main_prompt_v4_2.md` 파일은 이 세션 전체를 관장하는 **SYSTEM_PROMPT**이다.
* `CONFIGURATION_GUIDE.md` 파일은 기본 설정을 담고 있는 **CONFIG_GUIDE**이다.
* 사용자가 업로드한 분석 대상 텍스트는 **SOURCE_TEXT**이다.

**2. CONFIG 적용 규칙**

* **1순위:** `CONFIG_GUIDE`에서 `weighting_scheme`, `methodology_override`, `override_gate` 값을 기본 설정으로 파싱한다.
* **2순위:** 만약 `config.yaml` 파일이 함께 첨부되었다면, `config.yaml`에 있는 동일한 키의 값으로 기본 설정을 덮어쓴다.
* **3순위:** 이후 대화창에서 `[파라미터 경로]=[값]` 형식의 명령이 입력되면, 그 세션 동안 해당 값으로 즉시 덮어쓴다.

**3. Phase 0 수행 요구 사항**

* **SOURCE_TEXT**를 예비 분석하여 `genre`, `complexity_score`, `theological_markers`, `korean_context_relevance`를 산출한다.
* `recommended_methodology`를 제시하되, CONFIG의 `methodology_override`가 있으면 그 값을 우선 표기한다.
* 200자 요약(`summary_200_chars`)을 작성한다.
* `adaptive_analysis` 계획표(Phase·강조항목·깊이·예상토큰·특별고려사항)를 테이블 형태로 출력한다.
* 모든 결과는 **공통 YAML 스키마**(`phase_id=0` 포함)에 맞춰 `phase_results` 블록으로 제공한다.

**4. 출력 형식**

* **[개선 제안]** 최종적으로 적용된 설정 값을 명시적으로 보여주는 **[CONFIG LOADED]** 블록을 최상단에 출력한다.
* YAML 블록 이전에 간단한 서술(2–3문장)로 프로파일링 핵심을 설명한다.
* YAML 블록 이후 마지막 줄에 **"CONFIRM"**만 단독 표기하여 사용자 승인 대기.
* 모든 서술은 평서문 종결어미(-이다, -한다)를 사용한다.

**5. 할루시네이션·문체·용어 규칙**

* `SYSTEM_PROMPT`의 페르소나, 정확성, 원어 표기, 평어체 규범을 준수한다.
* 모든 주장에 `[텍스트 기반]`, `[신학 일반]`, `[추론]` 중 하나의 태그를 부여한다.

---
**위 지시를 이행하여 Phase 0 결과를 출력하고 "CONFIRM"으로 종료하라.**

---

### AI 출력 예시

```
[CONFIG LOADED]
*   Source: config.yaml
*   weighting_scheme.frequency: 0.25
*   methodology_override.primary: "서사적 해석"

이 텍스트는 복잡도 7.8의 학술 논문으로, '과정신학'과 '복잡계 이론'이라는 신학적 마커가 두드러진다. 따라서 분석은 '조직신학적 검토'에 집중하는 것이 효과적일 것이다.

```yaml
phase_results:
  phase_id: "0"
  # ... (YAML 결과 내용)
```

CONFIRM

```
