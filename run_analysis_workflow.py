# run_analysis_workflow.py
"""
Analysis_Th 전체 워크플로우 자동 실행 (Phase 0–4 + 2.5)
파일명·Phase 체계는 v1.1 표준을 따르며, config.yaml 설정을 반영한다.
"""

import argparse, logging, os, random, re, sys, time, yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import google.generativeai as genai
from dotenv import load_dotenv
from subprocess import run, CalledProcessError

load_dotenv()

# ───────── 기본 설정 ─────────
API_KEY     = os.getenv("GOOGLE_API_KEY")
ROOT        = Path(__file__).resolve().parent
SRC_DIR     = ROOT / "sources";  SRC_DIR.mkdir(exist_ok=True)
RES_DIR     = ROOT / "results";  RES_DIR.mkdir(exist_ok=True)
TPL_DIR     = ROOT / "templates"
MAX_RETRY   = 5

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def read(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else ""

def backoff(n: int):
    time.sleep((2**n) + random.random())

class Workflow:
    def __init__(self, src_name: str, cli_args: argparse.Namespace):
        self.src = SRC_DIR / src_name
        if not self.src.exists():
            raise FileNotFoundError(f"소스 파일 없음: {self.src}")
        self.id = self.src.stem
        self.ts = datetime.now().strftime("%Y%m%d")
        self.pth = {k: RES_DIR / f"{self.ts}_{self.id}_phase{k}.md"
                    for k in ["0", "1", "2", "2_5", "3", "4"]}
        self._load_config(cli_args)
        self._configure_logging()
        self.main_prompt = read(TPL_DIR / "main_prompt.md")
        self.action_prompt = read(TPL_DIR / "action.md")
        self._init_llm()

    def _load_config(self, cli_args: argparse.Namespace):
        """설정 파일을 로드하고, 기본값과 병합합니다."""
        # 1. 코드에 정의된 기본값 (가장 낮은 우선순위)
        defaults = {
            'project_settings': {
                'model_name': 'gemini-1.5-pro-latest',
                'max_retries': 3,
                'approval_mode': 'auto',
                'logging_level': 'INFO',
            },
            'analysis_parameters': {
                'override_gate': False
            }
        }

        # 2. config.yaml 파일 (중간 우선순위)
        user_config = {}
        try:
            with open(ROOT / "config.yaml", "r", encoding="utf-8") as f:
                user_config = yaml.safe_load(f) or {}
        except FileNotFoundError:
            logging.warning("config.yaml 파일을 찾을 수 없어 기본값으로 실행합니다.")

        # 3. 설정 병합 (사용자 설정이 기본값을 덮어씀)
        # 깊은 병합을 위해 각 섹션별로 업데이트
        self.config = defaults
        for section, settings in user_config.items():
            if section in self.config:
                self.config[section].update(settings)
            else:
                self.config[section] = settings

        # 4. CLI 인자 (가장 높은 우선순위)
        if cli_args.no_confirm:
            self.config['project_settings']['approval_mode'] = 'auto'
        if cli_args.delete_intermediate:
            self.config['project_settings']['delete_intermediate'] = True

    def _configure_logging(self):
        """config에 따라 로깅 레벨을 설정합니다."""
        level = self.config.get('project_settings', {}).get('logging_level', 'INFO').upper()
        logging.getLogger().setLevel(level)
        logging.info(f"로깅 레벨이 '{level}'로 설정되었습니다.")

    def ask(self, prompt:str, r:int=0)->Optional[str]:
        max_retries = self.config.get('project_settings', {}).get('max_retries', 3)
        logging.info(f"LLM 호출 {r+1}/{max_retries}")
        try:
            return self.model.generate_content(prompt).text
        except Exception as e:
            logging.error(e)
            if r < max_retries - 1:
                backoff(r); return self.ask(prompt,r+1)
            return None

    def _build_prompt(self, phase_key: str, deps: List[str]) -> str:
        """주어진 단계와 의존성에 따라 동적으로 프롬프트를 생성합니다."""
        parts = [self.main_prompt, self.action_prompt]

        if not deps: # Phase 0의 경우
            parts.append(f"--- SOURCE ---\n{read(self.src)}")
        else: # 다른 Phase의 경우
            for dep_key in deps:
                header = f"--- P{dep_key.replace('_', '.')} ---"
                parts.append(f"{header}\n{read(self.pth[dep_key])}")

        parts.append(f"\nPhase {phase_key.replace('_', '.')}을 수행하라.")
        return "\n\n".join(parts)

    # ───── Phase 정의 ─────
    def steps(self)->List[Dict[str,Any]]:
        """워크플로우 단계를 선언적으로 정의합니다."""
        step_definitions = [
            {"k": "0",   "n": "Phase 0 프로파일링",      "deps": []},
            {"k": "1",   "n": "Phase 1 정량 분석",       "deps": ["0"]},
            {"k": "2",   "n": "Phase 2 정성 분석",       "deps": ["1"]},
            {"k": "2_5", "n": "Phase 2.5 수렴도 평가",   "deps": ["1", "2"]},
            {"k": "3",   "n": "Phase 3 심층 검토",       "deps": ["2_5"]},
            {"k": "4",   "n": "Phase 4 적용·종합",      "deps": ["3"]},
        ]
        for step in step_definitions:
            step["prompt"] = self._build_prompt(step["k"], step["deps"])
        return step_definitions

    def _handle_approval(self, phase_key: str) -> str:
        """
        config.yaml 설정에 따라 사용자 승인을 처리합니다.
        Returns: 'continue', 'stop', 'retry'
        """
        approval_mode = self.config.get('project_settings', {}).get('approval_mode', 'auto')

        if approval_mode == 'auto':
            return 'continue'

        needs_approval = False
        if approval_mode == 'manual':
            needs_approval = True
        elif approval_mode == 'conditional':
            rules = self.config.get('project_settings', {}).get('conditional_rules', [])
            rule_map = {str(r['phase_id']): r['require_user'] for r in rules}
            needs_approval = rule_map.get(phase_key, False)

        if not needs_approval:
            return 'continue'

        while True:
            try:
                prompt_text = (f"\n✅ Phase {phase_key} 완료. 계속 진행하시겠습니까? (Y/n/retry): ")
                confirm = input(prompt_text).lower().strip()
                if confirm in ["y", "yes", ""]: return 'continue'
                if confirm in ["n", "no"]: logging.info("사용자 요청으로 작업을 중단합니다."); return 'stop'
                if confirm in ["r", "retry"]: logging.info(f"사용자 요청으로 Phase {phase_key}를 재실행합니다."); return 'retry'
                print("잘못된 입력입니다. 'y', 'n', 'retry' 중 하나를 입력하세요.")
            except EOFError:
                logging.warning("비대화형 환경에서는 확인 절차를 건너뛰고 계속 진행합니다.")
                return 'continue'

    # ───── 단일 Phase 실행 ─────
    def run_phase(self, step:Dict[str,Any])->bool:
        if any(not self.pth[d].exists() for d in step["deps"]):
            logging.error(f"선행 Phase 결과 누락: {step['deps']}"); return False
        
        while True: # 재시도를 위한 루프
            logging.info(f"🚀 {step['n']} 시작...")
            res = self.ask(step["prompt"])
            if not res: return False # LLM 호출 실패 시 전체 중단
            
            self.pth[step["k"]].write_text(res, encoding="utf-8")
            logging.info(f"💾 저장: {self.pth[step['k']]}")

            approval_status = self._handle_approval(step["k"])

            if approval_status == 'continue':
                break # 루프 탈출, 다음 단계로
            elif approval_status == 'stop':
                return False # 전체 워크플로우 중단
            elif approval_status == 'retry':
                continue # 루프 처음으로 돌아가 재실행

        if step["k"] == "2_5" and re.search(r"gate_status.*blocked", res, re.I):
            if self.config.get('analysis_parameters', {}).get('override_gate', False):
                logging.warning("⚠️ gate_status=blocked이지만, config.yaml의 override_gate=true 설정에 따라 계속 진행합니다.")
            else:
                logging.error("🚫 gate_status=blocked → 이후 Phase 중단. config.yaml에서 override_gate: true로 설정하여 강제 진행할 수 있습니다.")
                return False
        return True

    # ───── 전체 실행 ─────
    def run(self, sel:Optional[List[str]]=None):
        for s in self.steps():
            if sel and s["k"] not in sel: continue
            if not self.run_phase(s):
                logging.info("워크플로우가 중단되었습니다.")
                sys.exit(1)

        try:
            cmd = [sys.executable, "compile_report.py", self.id, "--results_path", str(RES_DIR)]
            # --delete-intermediate 옵션이 주어졌을 경우 컴파일러에도 전달
            if self.config.get('project_settings', {}).get('delete_intermediate'):
                cmd.append("--delete-intermediate")
            run(cmd, check=True)
            logging.info("🎉 최종 보고서 생성 완료")
        except CalledProcessError as e:
            logging.error(f"보고서 컴파일 실패: {e}")

# ───── CLI ─────
def main():
    ap = argparse.ArgumentParser(
        description="Analysis_Th 워크플로우 실행",
        formatter_class=argparse.RawTextHelpFormatter # 도움말의 줄바꿈을 유지합니다.
    )
    ap.add_argument("source_file", help="sources/ 내 분석 대상 텍스트 파일")
    ap.add_argument(
        "--steps",
        help="실행할 Phase 키를 콤마로 구분하여 지정 (예: 1,2_5,4)\n지정하지 않으면 전체 워크플로우 실행"
    )
    ap.add_argument(
        "--no-confirm",
        action="store_true",
        help="Phase 0 완료 후 사용자 확인 절차를 건너뛰고 계속 진행"
    )
    ap.add_argument(
        "--delete-intermediate",
        action="store_true",
        help="최종 보고서 생성 성공 시 중간 단계 파일들(*_phase*.md)을 삭제"
    )
    ar = ap.parse_args()
    wf = Workflow(ar.source_file, ar)
    sel = ar.steps.split(",") if ar.steps else None
    wf.run(sel)

if __name__ == "__main__":
    main()
