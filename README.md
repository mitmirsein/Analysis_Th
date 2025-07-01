```markdown
# Analysis_Th: AI-기반 신학 텍스트 심층 분석 프레임워크  
*(Last updated : 2025-07-01 · v4.2 / v5.2 정식 지원)*  

---

**Overview:**  
Analysis_Th는 최신 LLM(Gemini, ChatGPT 등)을 활용하여 신학 텍스트를 다단계(Phase 0 – 4 + 2.5)로 분석-검증-보고하는 "프롬프트 엔지니어링 + 파이썬 자동화" 프레임워크다. 웹 UI만으로도 사용할 수 있고, CLI 스크립트로 완전 자동화할 수도 있다.

---

## 1. 프로젝트 구조

```
Analysis_Th/
 ├─ results/            # Phase 결과·최종 보고서가 생성될 위치
 │   └─ .gitkeep
 ├─ sources/            # 분석 대상 텍스트 위치
 │   └─ .gitkeep
 ├─ templates/          # 모든 프롬프트·가이드
 │   ├─ main_prompt.md
 │   ├─ action.md
 │   ├─ CONFIGURATION_GUIDE.md
 │   ├─ PROMPT_COOKBOOK.md
 │   └─ ...
 ├─ run_analysis_workflow.py   # 전체 자동 실행
 ├─ compile_report.py          # Phase *.md → 최종 보고서
 ├─ config.yaml                # 가중치·방법론 기본값
 └─ README.md
```

---

## 2. 환경 설정 & 필수 라이브러리

### 2-1. Python 가상 환경(.venv) 권장 [#필수]

가상 환경을 사용하면 프로젝트마다 라이브러리 버전을 격리-관리할 수 있다.

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

```bash
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

## 3. 사용 방법

### 3-1. 분석할 소스 파일 준비

`sources/` 디렉터리에 예) `welker_creation.txt` 를 넣는다.

### 3-2. 전체 워크플로우 자동 실행

```bash
python run_analysis_workflow.py welker_creation.txt
```

* Phase 0 → 4(+2.5)가 순차 진행되며  
 `results/YYYYMMDD_welker_creation_phaseX.md` 파일이 자동 저장된다.  
* 모든 Phase 완료 후 `compile_report.py` 가 호출되어  
 `YYYYMMDD_welker_creation_final_report.md` 완성본이 `results/` 에 생성된다.

### 3-3. 특정 Phase만 실행

```bash
# Phase 1 과 2.5, 4 만 실행
python run_analysis_workflow.py welker_creation.txt --steps 1,2_5,4
```

Phase 결과가 이미 있을 경우 해당 파일만 덮어쓴 뒤 컴파일 단계로 진행한다.

### 3-4. 최종 보고서만 다시 컴파일

```bash
python compile_report.py welker_creation --results_path results
```

`results/` 폴더에 있는 Phase *.md 파일을 병합해 보고서를 재생성한다.

---

## 4. config.yaml 커스터마이징

```yaml
weighting_scheme:
  frequency:          0.40
  network_centrality: 0.35
  citation_count:     0.25

methodology_override:
  primary:   ""          # 예) "서사적 해석"
  auxiliary: []          # 예) ["실천신학적 검토"]

override_gate: false     # Phase 2.5 '미흡/취약' 차단 무시 여부
```

값을 바꾼 뒤 저장하면 다음 실행부터 자동 반영된다.  
웹-UI에서는 `[파라미터 경로]=값` 형식으로 실시간 덮어쓰기도 가능하다.

---

## 5. Git 관리 가이드

```
# .gitignore 핵심 항목
results/*
!results/.gitkeep
sources/*
!sources/.gitkeep
__pycache__/
*.py[cod]
.venv/
.vscode/
*.env
```

* `results/` 및 `sources/` 는 빈 폴더만 버전 관리하고 산출물·원문 텍스트는 제외.  
* API Key, 가상환경, 캐시 파일도 커밋하지 않는다.

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