## 세션 초기화 및 Phase 0 실행 지시 — Analysis_Th v1.1

### 1. 첨부 파일 역할 지정

- **main_prompt.md**  →  SYSTEM_PROMPT (전역 규칙·페르소나)  
- **action.md**       →  ACTION_PLAN  (Phase별 단계·YAML 스키마)  
- **CONFIGURATION_GUIDE.md** → CONFIG_GUIDE (설정 설명서)  
- **config.yaml** *[선택]* → USER_CONFIG (사용자 설정)  
- **SOURCE_TEXT**      → 분석 대상 원본(.txt/.md)

### 2. CONFIG 우선순위

1. **CLI 인자** (채팅창의 `[파라미터 경로]=값` 실시간 명령)  
2. **USER_CONFIG**   (첨부된 `config.yaml`)  
3. **CONFIG_GUIDE**  (가이드의 기본값)  
4. **코드 기본값**   (시스템 내부)

> 동일 키를 발견하면 위에 나열된 항목이 아래 항목을 즉시 덮어쓴다.

### 3. Phase 0 수행 요구 사항

1. `SOURCE_TEXT`를 예비 분석하여  
   - `genre`  
   - `complexity_score` *(1‒10)*  
   - `theological_markers` *(dict)*  
   - `korean_context_relevance` *(0‒1)*  
   을 산출한다.  
2. `recommended_methodology` 제시  
   - 단, `methodology_override.primary` 값이 있으면 그 값을 우선 표기한다.  
3. 200자 요약 `summary_200_chars` 작성 *(공백 포함 190‒210자)*  
4. **adaptive_analysis** 계획표 출력  

   | Phase | 핵심 항목 | 깊이 | 예상 토큰 | 특별 고려 |
   |-------|-----------|------|-----------|-----------|

5. 결과는 **공통 YAML 스키마**(`phase_id=0`)로 제공한다.

---

### 4. 출력 형식

1. 최상단에 `[CONFIG LOADED]` 블록  

   > **[CONFIG LOADED]**  
>
   > ```yaml
   > model_name: gemini-1.5-pro-latest
   > approval_mode: conditional
   > weighting_scheme:
   >   frequency: 0.40
   >   network_centrality: 0.35
   >   citation_count: 0.25
   > methodology_override.primary: "서사적 해석"
   > ```

2. 이어서 2‒3문장으로 핵심 프로파일 요약.  
3. ```yaml``` 블록 안에 `phase_results` 출력.  
4. YAML 뒤 **단독 줄**로 `CONFIRM` 표기 → 사용자 승인 대기.  
5. 모든 서술은 평서문 종결어미(-이다, -한다)를 사용한다.

### 5. 할루시네이션·문체·용어 규칙

- SYSTEM_PROMPT의 페르소나·정확성·원어 표기·평어체 규범 준수.  
- 모든 주장에 `[텍스트 기반]`,`[신학 일반]`,`[추론]` 중 하나의 태그를 부착한다.  
- 출력 YAML 이 `yaml.safe_load` 로 파싱되지 않으면 **RETRY** 를 반환하고 재생성한다.

---

### 출력 예시

```plaintext
[CONFIG LOADED]
model_name: gemini-1.5-pro-latest
approval_mode: conditional
weighting_scheme:
  frequency: 0.40
  network_centrality: 0.35
  citation_count: 0.25
methodology_override.primary: "서사적 해석"

이 텍스트는 복잡도 7.8의 학술 논문이다[텍스트 기반]. '과정신학'과 '복잡계 이론'이 핵심 신학 마커로 나타난다[텍스트 기반].

```yaml
phase_results:
  phase_id: "0"
  text_profile:
    genre: "학술 논문"
    complexity_score: 7.8
    theological_markers:
      - 과정신학
      - 복잡계
    recommended_methodology: "서사적 해석"
    korean_context_relevance: 0.32
  key_data:
    summary_200_chars: "..."
  quality_check:
    completeness: true
    style_consistency: true
```

CONFIRM

```
