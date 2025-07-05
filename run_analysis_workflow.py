# run_analysis_workflow.py
"""
Analysis_Th - v1.1
 ─ 텍스트 → Phase 0‒4(+2.5) 자동 분석 워크플로우

• 파일·Phase 규칙: 20250702 표준
• config.yaml + CLI 인자 병합
"""

# ───────── 표준 라이브러리 ─────────
import argparse
import logging
import math
import os
import random
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from subprocess import CalledProcessError, run
from typing import Any, Dict, List, Optional

import yaml  # PyYAML

# ───────── 외부 라이브러리 ─────────
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(override=True)

# ───────── 상수 / 경로 ─────────
API_KEY = os.getenv("GOOGLE_API_KEY")
ROOT = Path(__file__).resolve().parent
SRC_DIR = ROOT / "sources"
RES_DIR = ROOT / "results"
TPL_DIR = ROOT / "templates"

for d in (SRC_DIR, RES_DIR):
    d.mkdir(exist_ok=True)

# ───────── 로깅 ─────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# --------------------------------------------------------------------------- #
#                               헬퍼 함수                                     #
# --------------------------------------------------------------------------- #
def read(p: Path) -> str:
    """파일 내용 안전 읽기(없으면 '')."""
    try:
        return p.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def backoff(n: int) -> None:
    """지수 백오프 + jitter."""
    time.sleep((2**n) + random.random())


# --------------------------------------------------------------------------- #
#                               워크플로우 클래스                              #
# --------------------------------------------------------------------------- #
class Workflow:
    def __init__(self, src_name: str, cli_args: argparse.Namespace) -> None:
        self.src = SRC_DIR / src_name
        if not self.src.exists():
            raise FileNotFoundError(f"소스 파일 없음: {self.src}")

        self.id = self.src.stem
        self.ts = datetime.now().strftime("%Y%m%d")
        self.pth: Dict[str, Path] = {
            k: RES_DIR / f"{self.ts}_{self.id}_phase{k}.md"
            for k in ["0", "1", "2", "2_5", "3", "4"]
        }

        self._load_config(cli_args)
        self._configure_logging()

        self.main_prompt = read(TPL_DIR / "main_prompt.md")
        self.action_prompt = read(TPL_DIR / "action.md")

        self._validate_config()
        self._init_llm()

    # ---------------- config / LLM ----------------------------------
    def _load_config(self, cli_args: argparse.Namespace) -> None:
        """기본값 → config.yaml → CLI 순으로 병합."""
        defaults: Dict[str, Any] = {
            "project_settings": {
                "model_name": "gemini-1.5-pro-latest",
                "max_retries": 3,
                "approval_mode": "auto",  # auto | manual | conditional
                "logging_level": "INFO",
            },
            "analysis_parameters": {
                "override_gate": False,
            },
        }

        user_cfg: Dict[str, Any] = {}
        cfg_path = ROOT / "config.yaml"
        if cfg_path.exists():
            user_cfg = yaml.safe_load(cfg_path.read_text("utf-8")) or {}
        else:
            logging.warning("config.yaml 파일을 찾지 못했습니다. 기본값으로 실행합니다.")

        # 얕은/깊은 병합
        self.config: Dict[str, Any] = defaults
        for sec, data in user_cfg.items():
            self.config.setdefault(sec, {}).update(data)

        # CLI 인자 영향
        if cli_args.no_confirm:
            self.config["project_settings"]["approval_mode"] = "auto"
        if cli_args.delete_intermediate:
            self.config["project_settings"]["delete_intermediate"] = True

    def _configure_logging(self) -> None:
        lvl = self.config["project_settings"].get("logging_level", "INFO").upper()
        logging.getLogger().setLevel(lvl)
        logging.info("로깅 레벨을 %s 로 설정했습니다.", lvl)

    def _validate_config(self) -> None:
        """config.yaml의 주요 값들이 논리적으로 유효한지 검사하고, 필요시 조정합니다."""
        # 1. 가중치 합계 검증 및 자동 정규화
        params = self.config.get("analysis_parameters", {})
        scheme = params.get("weighting_scheme", {})
        if scheme:
            total_weight = sum(scheme.values())
            if not math.isclose(total_weight, 1.0):
                logging.warning(
                    "config.yaml의 weighting_scheme 합계가 1.0이 아닙니다 (현재: %.2f). 자동 정규화합니다.",
                    total_weight,
                )
                if total_weight > 0:
                    factor = 1.0 / total_weight
                    for key in scheme:
                        scheme[key] *= factor
                    # Update the config in place
                    self.config["analysis_parameters"]["weighting_scheme"] = scheme

    def _init_llm(self) -> None:
        if not API_KEY:
            raise EnvironmentError("GOOGLE_API_KEY 환경변수가 설정되지 않았습니다.")
        genai.configure(api_key=API_KEY)
        
        model_name = self.config["project_settings"]["model_name"]
        
        gen_config_params = {}
        if max_tokens := self.config["project_settings"].get("max_output_tokens"):
            gen_config_params["max_output_tokens"] = max_tokens
        
        self.model = genai.GenerativeModel(
            model_name,
            generation_config=genai.types.GenerationConfig(**gen_config_params) if gen_config_params else None
        )
        logging.info("Gemini 모델 초기화 완료: %s", model_name)

    # ---------------- LLM 호출 ----------------
    def ask(self, prompt: str, r: int = 0) -> Optional[str]:
        max_retry = self.config["project_settings"]["max_retries"]
        timeout = self.config["project_settings"].get("timeout_seconds")
        logging.info("LLM 호출 %d/%d", r + 1, max_retry)
        try:
            opts = {"timeout": timeout} if timeout else {}
            return self.model.generate_content(prompt, request_options=opts).text
        except Exception as exc:  # pylint: disable=broad-except
            logging.error(exc)
            if r < max_retry - 1:
                backoff(r)
                return self.ask(prompt, r + 1)
            return None

    # ---------------- 프롬프트 빌드 ----------------
    def _build_prompt(self, phase_key: str, deps: List[str]) -> str:
        cfg_block = (
            "--- CONFIG ---\n```yaml\n"
            + yaml.safe_dump(self.config, allow_unicode=True, sort_keys=False)
            + "```\n"
        )

        parts = [cfg_block, self.main_prompt, self.action_prompt]

        # 1. 원본 소스 텍스트를 항상 포함시켜, 각 Phase가 분석 대상을 명확히 인지하도록 합니다.
        source_content = ""
        if self.src.suffix == ".json":
            try:
                # PyYAML은 JSON을 직접 파싱할 수 있습니다.
                json_data = yaml.safe_load(read(self.src))
                # LLM이 이해하기 쉽도록 예쁘게 포맷된 YAML 문자열로 변환합니다.
                source_content = yaml.dump(
                    json_data, allow_unicode=True, sort_keys=False, indent=2
                )
                logging.info(".json 소스 파일을 파싱하여 YAML 형식으로 변환했습니다.")
            except yaml.YAMLError as e:
                logging.error(".json 파일 파싱 실패: %s. 원본 텍스트로 처리합니다.", e)
                source_content = read(self.src)  # 파싱 실패 시 원본 텍스트로 대체
        else:  # .txt, .md 등 다른 텍스트 파일
            source_content = read(self.src)
        parts.append(f"--- SOURCE ---\n{source_content}")

        # 2. 이전 단계(Phase)의 결과물을 의존성에 따라 추가합니다.
        for d in deps:
            parts.append(f"--- P{d.replace('_', '.')} ---\n{read(self.pth[d])}")

        parts.append(f"\nPhase {phase_key.replace('_', '.')}을 즉시 수행하라.")
        return "\n\n".join(parts)

    # ---------------- 단계 정의 ----------------
    def steps(self) -> List[Dict[str, Any]]:
        step_def = [
            {"k": "0", "n": "Phase 0 프로파일링", "deps": []},
            {"k": "1", "n": "Phase 1 정량 분석", "deps": ["0"]},
            {"k": "2", "n": "Phase 2 정성 분석", "deps": ["1"]},
            {"k": "2_5", "n": "Phase 2.5 수렴도 평가", "deps": ["1", "2"]},
            {"k": "3", "n": "Phase 3 심층 검토", "deps": ["2_5"]},
            {"k": "4", "n": "Phase 4 적용·종합", "deps": ["3"]},
        ]
        for s in step_def:
            s["prompt"] = self._build_prompt(s["k"], s["deps"])
        return step_def

    # ---------------- 승인 로직 ----------------
    def _handle_approval(self, phase_key: str) -> str:
        mode = self.config["project_settings"]["approval_mode"]
        if mode == "auto":
            return "continue"

        need = False
        if mode == "manual":
            need = True
        elif mode == "conditional":
            rules = self.config["project_settings"].get("conditional_rules", [])
            rule_map = {str(r["phase_id"]): r["require_user"] for r in rules}
            need = rule_map.get(phase_key, False)

        if not need:
            return "continue"

        while True:
            try:
                ans = input(
                    f"\n✅ Phase {phase_key} 완료. 진행?(Y/n/retry): "
                ).lower()
            except EOFError:
                logging.warning("비대화형 환경 → 자동 continue")
                return "continue"

            if ans in ("", "y", "yes"):
                return "continue"
            if ans in ("n", "no"):
                return "stop"
            if ans == "retry":
                return "retry"
            print("y / n / retry 중 하나를 입력하세요.")

    # ---------------- Phase 실행 ----------------
    def run_phase(self, step: Dict[str, Any]) -> bool:
        if any(not self.pth[d].exists() for d in step["deps"]):
            logging.error("선행 Phase 결과 누락: %s", step["deps"])
            return False

        while True:
            logging.info("🚀 %s 시작", step["n"])
            res = self.ask(step["prompt"])
            if not res:
                return False  # LLM 실패

            self.pth[step["k"]].write_text(res, encoding="utf-8")
            logging.info("💾 저장: %s", self.pth[step["k"]])

            # 게이트 검사 (Phase 2.5)
            if step["k"] == "2_5" and re.search(r"gate_status:\s*\"?blocked", res):
                if self.config["analysis_parameters"].get("override_gate"):
                    logging.warning("gate_status=blocked 무시하고 진행")
                else:
                    logging.error("gate_status=blocked → 워크플로우 중단")
                    return False

            # 승인
            act = self._handle_approval(step["k"])
            if act == "continue":
                break
            if act == "stop":
                return False
            # act == "retry" → while 루프 재실행
        return True

    # ---------------- 전체 실행 ----------------
    def run(self, selected: Optional[List[str]] = None) -> None:
        for s in self.steps():
            if selected and s["k"] not in selected:
                continue
            if not self.run_phase(s):
                logging.info("워크플로우가 중단되었습니다.")
                sys.exit(1)

        # 최종 보고서 컴파일
        cmd = [
            sys.executable,
            str(ROOT / "compile_report.py"),
            self.id,
            "--results_path",
            str(RES_DIR),
        ]
        if self.config["project_settings"].get("delete_intermediate"):
            cmd.append("--delete-intermediate")

        try:
            run(cmd, check=True)
            logging.info("🎉 최종 보고서 생성 완료")
        except CalledProcessError as exc:
            logging.error("보고서 컴파일 실패: %s", exc)


# --------------------------------------------------------------------------- #
#                                CLI 진입점                                   #
# --------------------------------------------------------------------------- #
def main() -> None:
    ap = argparse.ArgumentParser(
        description="Analysis_Th 워크플로우 실행",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    ap.add_argument("source_file", help="sources/ 내 분석 대상 텍스트 파일")
    ap.add_argument(
        "--steps",
        help="실행할 Phase 키를 콤마로 지정 (예: 1,2_5,4). "
        "미지정 시 전체 실행",
    )
    ap.add_argument(
        "--no-confirm",
        action="store_true",
        help="모든 승인 절차 생략",
    )
    ap.add_argument(
        "--delete-intermediate",
        action="store_true",
        help="최종 보고서 후 중간 *_phase*.md 파일 삭제",
    )

    args = ap.parse_args()
    wf = Workflow(args.source_file, args)
    sel = args.steps.split(",") if args.steps else None
    wf.run(sel)


if __name__ == "__main__":
    main()
