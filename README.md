# Analysis_Th: AI-기반 신학 텍스트 심층 분석 프레임워크  

*(Last updated: 2025-07-02 · v1.1 정식 지원)*  

---

**Overview:**  
Analysis_Th는 최신 LLM을 활용하여 신학 텍스트를 다단계로 분석-검증-보고하는 "프롬프트 엔지니어링 + 파이썬 자동화" 프레임워크입니다. 이 프레임워크는 웹 UI를 통해 대화형으로 사용하거나, 제공되는 파이썬 스크립트로 전체 과정을 완전 자동화할 수 있습니다.

이 시스템의 핵심 특징은 **적응형 분석(Adaptive Analysis)**과 **사용자 중심의 미세 조정(Fine-tuning)**입니다.

* **적응형 분석 (Adaptive Analysis):** Phase 0에서 AI가 텍스트의 장르와 복잡도를 스스로 진단하고, 그 결과에 따라 후속 분석 단계의 깊이와 초점을 자동으로 조절합니다.
* **사용자 중심 미세 조정 (User-driven Fine-tuning):** 사용자는 실행 전 `config.yaml` 파일을 통해 분석 가중치, 승인 절차 등 워크플로우의 모든 측면을 자신의 연구 목적에 맞게 정밀하게 제어할 수 있습니다.

이 두 가지 특징의 결합을 통해, 텍스트에 최적화된 맞춤형 보고서가 생성됩니다.

> **Note:**  
> 이 프로젝트는 인문학에 정량적 분석과 정성적 분석이 결합되면 더욱 단단한 연구를 할 수 있다고 생각하는, 그리고
> 코딩을 전적으로 AI에게 맡기고 지시만 할 줄 아는 개인 프로젝트입니다.
> 자유롭게 사용하고 테스트해 보실 수 있지만, 예기치 않은 동작이나 변경이 있을 수 있습니다.
> 피드백과 기여는 언제나 환영합니다!

---

## 1. 프로젝트 구조

```text
Analysis_Th/
├─ results/            # 분석 결과물이 생성되는 폴더
├─ sources/            # 분석할 원문 텍스트를 넣는 폴더 (md, txt, json 파일)
├─ templates/          # 프롬프트 엔지니어링 템플릿
│  ├─ action.md
│  ├─ CONFIGURATION_GUIDE.md
│  ├─ main_prompt.md
│  └─ PROMPT_COOKBOOK.md
├─ compile_report.py   # 중간 결과물을 최종 보고서로 컴파일
├─ config.yaml         # 분석 가중치, 승인 모드 등 프로젝트 전역 설정을 중앙에서 관리
├─ explanation_auto.md   # 자동화 스크립트 실행 가이드
├─ explanation_manual.md # 웹 UI 수동 실행 가이드
├─ README.md           # 프로젝트 개요 및 사용법 (현재 파일)
├─ requirements.txt    # 필요한 파이썬 라이브러리 목록
├─ requirements-dev.txt # 개발용 라이브러리 목록 (테스트, 린팅 등)
└─ run_analysis_workflow.py # 전체 분석 워크플로우 자동 실행

---

## 2. 환경 설정 & 필수 라이브러리

### 2-1. Python 가상 환경(.venv) 권장 [#필수]

가상 환경을 사용하면 프로젝트마다 라이브러리 버전을 격리-관리할 수 있습니다.

```bash
# ① 가상 환경 생성
python -m venv .venv

# ② 가상 환경 활성화
# macOS / Linux
source .venv/bin/activate
# Windows
.venv\Scripts\activate
```

가상 환경이 활성화되면 쉘 프롬프트 앞에 `(.venv)` 가 표시된다.

### 2-2. 필수 라이브러리 설치

**애플리케이션 실행용 (가상 환경 활성화 후):**

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

추가로 필요하다면 `requirements.txt` 에서 일괄 설치할 수 있다.

### 2-3. Google API Key 설정

```bash
# macOS / Linux
export GOOGLE_API_KEY="YOUR_KEY"
# Windows (cmd)
set GOOGLE_API_KEY=YOUR_KEY
```

---

## 3. 두 가지 실행 모드

이 프로젝트는 두 가지 방식으로 사용할 수 있습니다.

| 모드 | 제어 방식 | 설정 방법 | 장점 |
| :--- | :--- | :--- | :--- |
| **자동화 스크립트** | **실행 전** 설정 | `config.yaml` 파일 수정 | 완전 자동, 높은 재현성 |
| **대화형 UI (웹)** | **실행 중** 제어 | `PROMPT_COOKBOOK.md` 명령어 입력 | 높은 유연성, 실시간 조정 |

`run_analysis_workflow.py`는 **자동화 스크립트** 모드이며, 모든 설정은 실행 전에 완료해야 합니다.

---

## 4. 사용 방법

### 4-1. 분석할 소스 파일 준비

`sources/` 디렉터리에 예) `welker_creation.txt` 를 넣는다.

> **지원 파일 형식:**
> 이 시스템은 `.txt`, `.md`, `.json` 형식의 파일을 직접 처리할 수 있습니다. `.json` 파일의 경우, 그 구조가 자동으로 해석되어 분석에 사용됩니다. 만약 `.pdf`나 `.docx` 같은 다른 형식의 파일이 있다면, 내용을 복사하여 `.txt` 파일로 만들어 `sources/` 폴더에 넣어주세요.

### 4-2. 전체 워크플로우 자동 실행

```bash
python run_analysis_workflow.py welker_creation.txt
```

* Phase 0 → 4(+2.5)가 순차 진행되며  
 `results/YYYYMMDD_welker_creation_phaseX.md` 파일이 자동 저장된다.  
* 모든 Phase 완료 후 `compile_report.py` 가 호출되어  
 `YYYYMMDD_welker_creation_final_report.md` 완성본이 `results/` 에 생성된다.

### 4-3. 특정 Phase만 실행

```bash
# Phase 1 과 2.5, 4 만 실행
python run_analysis_workflow.py welker_creation.txt --steps 1,2_5,4
```

Phase 결과가 이미 있을 경우 해당 파일만 덮어쓴 뒤 컴파일 단계로 진행한다.

### 4-4. 최종 보고서만 다시 컴파일

```bash
python compile_report.py welker_creation --results_path results
```

`results/` 폴더에 있는 Phase *.md 파일을 병합해 보고서를 재생성한다.

---

## 5. config.yaml 커스터마이징 (핵심)

`config.yaml` 파일은 프로젝트 전체의 동작 방식을 제어하는 **중앙 설정 파일**입니다. 이 파일을 수정하여 워크플로우의 실행 방식, 분석 파라미터, 승인 절차 등을 유연하게 조정할 수 있습니다.

### 설정 계층 구조

설정은 다음 우선순위에 따라 적용됩니다. (높은 순서대로)

1. **CLI 인자:** `run_analysis_workflow.py` 실행 시 `--no-confirm` 같은 플래그
2. **`config.yaml`:** 사용자가 직접 정의한 값
3. **코드 기본값:** 스크립트 내에 하드코딩된 기본 설정

```yaml
# config.yaml 예시
# ==========================================================
# 1. 프로젝트 전역 설정 (Global Settings)
# ==========================================================
project_settings:
  # manual: 모든 Phase 후 승인 | auto: 자동 통과 | conditional: 아래 rules 따름
  approval_mode: "conditional"
  conditional_rules:
    - phase_id: "0"
      require_user: true
  
  # LLM 모델 및 API 관련
  model_name: "gemini-2.5-pro"
  max_retries: 3
  
  # 실행 제어
  logging_level: "INFO" # DEBUG, INFO, WARNING, ERROR

# ==========================================================
# 2. 분석 파라미터 (Analysis Parameters)
# ==========================================================
analysis_parameters:
  # 정량 분석 가중치 (합계 1.0 권장)
  weighting_scheme:
    frequency:          0.40
    network_centrality: 0.35
    citation_count:     0.25

  # Phase 0 결과 대신 강제로 적용할 방법론
  methodology_override:
    primary:   ""
    auxiliary: []

  # Phase 2.5 품질 게이트(blocked)를 무시하고 강제 진행할지 여부
  override_gate: false
```

값을 바꾼 뒤 저장하면 다음 실행부터 자동 반영된다.  
웹-UI에서는 `[파라미터 경로]=값` 형식으로 실시간 덮어쓰기도 가능하다.

---

## 6. FAQ (요약)

| 질문 | 답변 |
|------|------|
| **gate_status=blocked로 중단?** | `config.yaml`에서 `override_gate:true` 후 Phase 2.5 재실행. |
| **웹-UI만 쓰고 싶다면?** | templates 폴더 프롬프트 파일 업로드 → Phase별 지시 → 각 답변을 .md 로 저장 → `compile_report.py` 수동 실행. |
| **LLM 응답이 길어 토큰 초과?** | Cookbook 프롬프트 중 `token_limit_exceeded` 대응 스니펫 참고. |

---

**Happy Prompt-Engineering!**  
Analysis_Th를 자유롭게 포크하여 여러분의 연구에 맞게 확장하고, PR·이슈로 개선점을 공유해 주세요.  

MSN과 그의 Assistant AIs가 제작했습니다.

```
