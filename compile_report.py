# compile_report.py
"""
Analysis_Th v1.1
 ─ Phase 결과 (*.md) → 최종 보고서 컴파일러

기능
1. results/ 디렉터리에서   *{identifier}*_phase*.md  패턴 파일 수집
2. gate_status=blocked 검사 → 있으면 즉시 중단
3. 각 마크다운에서 YAML·진행률·요약 블록 제거, 비표준 헤더(**1. …**) 정규화
4. Phase 번호(## 2.5 …) 기준으로 본문 정렬
5. Executive Summary(Phase 4 YAML key ‘final_summary’) 삽입
6. 목차(TOC) 생성 후 하나의 Markdown으로 저장
"""

# ───────── 표준 라이브러리 ─────────
import argparse
import logging
import re
import sys, yaml
from datetime import datetime
from pathlib import Path
from typing import Dict

# ───────── 로깅 ─────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# --------------------------------------------------------------------------- #
#                               유틸리티 함수                                 #
# --------------------------------------------------------------------------- #
def _preprocess_headers(md: str) -> str:
    """
    **1. 제목** or **1 제목**  →  ## 1. 제목  로 변환하여
    헤더 파싱이 실패하지 않도록 표준화.
    """
    return re.sub(r"^\*\*((\d+\.?\s*)(.+?))\*\*", r"## \1", md, flags=re.MULTILINE)


def _strip_meta_blocks(md: str) -> str:
    """phase_results YAML, summary_200_chars, 진행률 블록 제거."""
    md = re.sub(r"```yaml\s*?\n?phase_results:.+?\n```", "", md, flags=re.DOTALL)
    # blockquote 형태의 200자 요약 제거
    md = re.sub(r">.*?summary_200_chars.*?\n", "", md, flags=re.IGNORECASE)
    md = re.sub(
        r"```.*?Phase 진행률:.*?```", "", md, flags=re.DOTALL | re.IGNORECASE
    )
    return re.sub(r"\n{3,}", "\n\n", md).strip()


def _slug(text: str) -> str:
    """헤더를 깃허브 호환 앵커(slug)로 변환."""
    text = re.sub(r"\*\*", "", text)  # bold 제거
    # 한글·영문·숫자·공백·하이픈 외 제거
    text = re.sub(r"[^\w\s\uac00-\ud7a3-]", "", text)
    return re.sub(r"\s+", "-", text).lower().strip("-")


def _num_from_header(h: str) -> float:
    """
    '## 2.5. 제목', '## 3 제목' 등에서 Phase 번호 추출 → float
    없으면 0.0
    """
    m = re.search(r"(\d+(?:\.\d+)?)", h)
    return float(m.group(1)) if m else 0.0


def _split_sections(md: str) -> Dict[float, str]:
    """## 헤더 기준으로 본문을 {phase_num: section_md} dict 로 분할."""
    parts = re.split(r"(^## .+?$)", md, flags=re.MULTILINE)
    sections: Dict[float, str] = {}
    for i in range(1, len(parts), 2):
        header, body = parts[i].strip(), parts[i + 1]
        n = _num_from_header(header)
        if n:
            sections[n] = f"{header}\n{body}"
    return sections


def _get_config_summary(res_dir: Path) -> str:
    """프로젝트 루트의 config.yaml을 읽어 요약 문자열을 반환합니다."""
    config_path = res_dir.parent / "config.yaml"
    if not config_path.exists():
        return ""
    try:
        config = yaml.safe_load(config_path.read_text("utf-8"))
        summary = yaml.dump(config, allow_unicode=True, sort_keys=False, indent=2)
        return f"## 분석 설정 요약\n\n```yaml\n{summary}```\n\n---\n"
    except Exception:
        return ""

# --------------------------------------------------------------------------- #
#                               메인 컴파일러                                 #
# --------------------------------------------------------------------------- #
def compile_report(identifier: str, res_dir: Path, delete_mid: bool = False) -> bool:
    pattern = f"*{identifier}*_phase*.md"
    files = sorted(res_dir.glob(pattern))
    if not files:
        logging.error("중간 결과 파일을 찾을 수 없습니다: %s", pattern)
        return False

    logging.info("컴파일 대상 파일 %d개: %s", len(files), [f.name for f in files])

    sections: Dict[float, str] = {}
    exec_summary = ""

    for fp in files:
        raw = fp.read_text(encoding="utf-8")

        # gate_status 검사
        if re.search(r'gate_status\s*:\s*"?blocked"?', raw, re.IGNORECASE):
            logging.error("🚫 게이트 차단 감지: %s → 보고서 중단", fp.name)
            return False

        # Phase 4 YAML 안의 final_summary 추출
        m = re.search(r"final_summary\s*:\s*\"(.+?)\"", raw, re.DOTALL)
        if m:
            exec_summary = m.group(1).strip()

        txt = _strip_meta_blocks(_preprocess_headers(raw))
        sections.update(_split_sections(txt))

    if exec_summary:
        sections[0.5] = f"## Executive Summary\n\n{exec_summary}"

    # 목차 생성
    toc_lines: list[str] = ["## 목차", ""]
    for num in sorted(sections):
        header_line = re.sub(r"^##\s*", "", sections[num].splitlines()[0]).strip()
        toc_lines.append(f"- [{header_line}](#{_slug(header_line)})")
    toc_md = "\n".join(toc_lines)

    # 본문 조립
    title = f"# {identifier.replace('_', ' ').title()} 심층 분석 최종 보고서"
    config_summary = _get_config_summary(res_dir)
    body_parts = [title, "", config_summary, toc_md, "\n---\n"]
    for num in sorted(sections):
        body_parts.append(sections[num])
        body_parts.append("\n---\n")
    report_md = "\n".join(body_parts).rstrip("-\n") + "\n"

    out_path = res_dir / f"{datetime.now():%Y%m%d}_{identifier}_final_report.md"
    out_path.write_text(report_md, encoding="utf-8", errors="ignore")
    logging.info("✅ 보고서 저장 완료: %s", out_path)

    if delete_mid:
        for fp in files:
            fp.unlink(missing_ok=True)
            logging.info("중간 파일 삭제: %s", fp.name)

    return True


# --------------------------------------------------------------------------- #
#                                   CLI                                       #
# --------------------------------------------------------------------------- #
def main() -> None:
    p = argparse.ArgumentParser(
        description="Phase 결과 Markdown → 최종 보고서 컴파일러"
    )
    p.add_argument("identifier", help="텍스트 식별자(ex. welker_creation)")
    p.add_argument("--results_path", default="results", help="results 디렉터리 경로")
    p.add_argument("--delete-intermediate", action="store_true", help="컴파일 후 중간 파일 삭제")
    args = p.parse_args()

    ok = compile_report(args.identifier, Path(args.results_path), args.delete_intermediate)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
