# Analysis_Th 워크플로우 설정 가이드

이 문서는 `Analysis_Th` 워크플로우의 높은 자유도를 안정적으로 관리하고, 사용자의 연구 목적에 맞게 분석을 조정하는 세 가지 핵심 설정 포인트를 안내합니다.

---

## 1. 분석 방법론 선택 (Phase 0 기반)

본 워크플로우는 **Phase 0 (텍스트 프로파일링)** 단계의 결과를 바탕으로, 분석 대상 텍스트의 성격에 가장 적합한 분석 방법론을 '적응형'으로 선택합니다. 사용자는 이 단계의 결과를 검토하고, 필요시 추천된 방법론을 수동으로 조정할 수 있습니다.

### 선택 기준 예시

* **학술 논문 (Academic Paper)의 경우:**
    * **추천 방법론:** `성서신학적 검토`, `역사신학적 검토`, `조직신학적 검토`에 집중합니다.
    * **이유:** 텍스트의 논리적 구조, 교리적 함의, 신학사적 위치를 분석하는 것이 중요하기 때문입니다.

* **설교문 (Sermon)의 경우:**
    * **추천 방법론:** `실천신학적 검토`, `수사학적 장치 분석`에 집중합니다.
    * **이유:** 텍스트가 청중에게 미치는 영향, 설득의 기술, 목회적 적용 가능성을 분석하는 것이 중요하기 때문입니다.

* **한국/아시아 컨텍스트 관련 텍스트의 경우:**
    * **추천 방법론:** `상황신학적 검토` 모듈을 활성화하고, `문화적 층위` 분석을 심화합니다.
    * **이유:** 텍스트와 특정 문화적 맥락 사이의 상호작용을 깊이 있게 탐구해야 하기 때문입니다.

> **사용자 역할:** Phase 0의 `recommended_methodology` 결과를 확인하고, 자신의 연구 질문과 일치하는지 검토합니다. 필요시 후속 단계에서 특정 분석 항목에 더 집중하도록 프롬프트를 미세 조정할 수 있습니다.

---

## 2. 정량 분석 가중치 설정

**Phase 1 (정량 분석)**의 결과는 후속 분석의 객관적 근거가 됩니다. 사용자는 자신의 분석 목적에 따라 각 정량 지표의 중요도(가중치)를 조절할 수 있습니다.

`main_prompt.md`의 `Ⅴ. 가중치 기반 통합 프레임워크` 섹션에서 이 설정을 변경할 수 있습니다.

### 가중치 설정 예시  (합계 = 1.0)

* **기본 설정 (균형 잡힌 분석):**

```yaml
weighting_scheme:
  frequency: 0.40
  network_centrality: 0.35
  citation_count: 0.25
```

* **개념의 '관계'(개념사 연구)에 집중**  
  `network_centrality`(개념 네트워크 중심성)의 가중치를 높입니다.

* **저자의 '영향'(지성사 연구)에 집중**  
  `citation_count`(인용 빈도)의 가중치를 높입니다.

> **사용자 역할:** 분석을 시작하기 전, `main_prompt.md`의 가중치 설정을 자신의 연구 질문에 맞게 수정합니다. 이 설정은 **Phase 2.5 (수렴도 평가)**의 결과에 직접적인 영향을 미칩니다.

---

## 3. 품질 게이트(Quality Gate) 조건 이해

본 워크플로우는 분석의 신뢰도를 보장하기 위해 자동화된 '품질 게이트'를 포함하고 있습니다. 가장 중요한 게이트는 **Phase 2.5 (수렴도 평가)** 단계에 있습니다.

* **핵심 조건:** `main_prompt.md`에 명시된 바와 같이, **Phase 2.5 수렴도 평가 종합 등급이 '미흡' 이하이고 `override_gate=false`일 때** 워크플로우는 Phase 3으로 진행되지 않고 사용자 승인을 요청합니다.

* **의미:** 이는 AI가 수행한 정성적 해석(Phase 2)이 객관적 데이터(Phase 1)와 심각하게 불일치함을 의미합니다. 이 상태에서 분석을 계속 진행하면, 잘못된 해석 위에 논리를 쌓아 올리는 '사상누각'이 될 위험이 있습니다.

> **사용자 역할:** 품질 게이트가 작동하여 워크플로우가 멈추면, Phase 1과 Phase 2의 결과를 비교 검토해야 합니다. AI의 해석이 편향되었는지, 혹은 데이터 자체가 예상과 다른 패턴을 보이는지 등을 판단하고, 필요시 이전 단계를 재실행하거나 분석 방향을 수정해야 합니다. 이는 분석 과정의 오류를 조기에 발견하고 결과물의 최종 품질을 보장하는 핵심적인 안전장치입니다.

---

## 4. 실시간 분석 제어 및 파라미터 조정 (대화형 UI 기준)

본 워크플로우는 단순히 고정된 설정을 따르는 것을 넘어, 사용자가 대화창(프롬프트 창)을 통해 실시간으로 분석의 방향을 미세 조정할 수 있는 강력한 기능을 제공합니다. 이는 분석을 일회성 작업이 아닌, AI와 함께 탐구해 나가는 **'대화형 연구(Interactive Research)'**로 만들어 줍니다.

### 기본 원리

시스템은 기본적으로 업로드된 `config.yaml` 또는 `main_prompt.md`의 설정을 따릅니다. 하지만 사용자가 대화창에 특정 형식의 명령어를 입력하면, 해당 분석 단계에 한해 설정을 **실시간으로 덮어쓸(override)** 수 있습니다.

### 조정 가능한 주요 파라미터

* `weighting_scheme.<지표>` – 정량 분석 지표 가중치 (예: `weighting_scheme.network_centrality`)
* `methodology_override.primary` – 주된 분석 방법론 강제 지정
* `override_gate` – 품질 게이트 무시 여부 (config 기본값: `false`)

### 명령어 구문 및 예시

명령어는 **`[파라미터 경로]=[값]`** 형식으로 자연스러운 문장 안에 포함시키면 됩니다.

* **예시 1: 가중치 재조정 후 특정 단계 재실행**
    > `Phase 2.5의 수렴도 등급이 '미흡'으로 나왔네요. 개념 간의 관계를 더 중요하게 보기 위해, weighting_scheme.network_centrality=0.6, weighting_scheme.frequency=0.2 로 설정해서 Phase 2.5를 다시 실행해주세요.`

* **예시 2: 분석 방법론 강제 지정**
    > `Phase 0에서 '역사신학적 검토'를 추천했지만, 이번에는 `methodology_override.primary="실천신학적 검토"` 로 Phase 3를 진행하고 싶습니다.`

* **예시 3: 품질 게이트 무시하고 강제 진행**
    > `수렴도가 낮은 것을 인지하고 있습니다. 연구 목적상 그대로 진행해야 하니, override_gate=true 로 설정하고 Phase 3를 실행해주세요.`

> **사용자 역할:**
>
> 1. 분석의 중간 결과(특히 Phase 2.5의 수렴도)를 보고, 분석 방향을 수정하고 싶을 때 이 기능을 활용합니다.
> 2. 명령을 내린 후, AI의 출력 로그에 **"사용자 요청에 따라 다음 파라미터를 재조정합니다: ..."** 와 같은 확인 메시지가 뜨는지 반드시 확인하여, 설정이 올바르게 적용되었는지 검증합니다.
> 3. 이 기능을 통해, 사용자는 AI의 분석을 수동적으로 기다리는 대신, 능동적으로 연구 과정을 이끌어 나가는 '프로젝트 디렉터'의 역할을 수행할 수 있습니다.
