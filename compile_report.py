# compile_report.py
"""
Analysis_Th v4.2 · v5.2  ─ Phase 결과 → 최종 보고서 컴파일러
※ gate_status, Phase 2.5, Executive Summary 지원
"""

import argparse, logging, re, sys
from datetime import datetime
from pathlib import Path
from typing import Dict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ────────────── 유틸 ──────────────
def _preprocess_content(md: str) -> str:
    """
    LLM이 생성한 비표준 헤더(예: **1. 제목**)를 표준 H2 헤더(## 1. 제목)로 변환합니다.
    AI의 비일관적인 출력 형식에 대응하여 안정성을 높입니다.
    """
    # **1. Title** 또는 **1 Title** 같은 형식을 ## 1. Title 로 변환
    return re.sub(r"^\*\*((\d+\.?\s*).*?)\*\*", r"## \1", md, flags=re.M)

def strip_blocks(md: str) -> str:
    """phase_results·진행률·요약 블록 제거"""
    md = re.sub(r"```yaml\s*\n?phase_results:.+?\n```", "", md, flags=re.S)
    md = re.sub(r">.*?summary_200_chars.*?\n", "", md, flags=re.I)
    md = re.sub(r"```.*?Phase 진행률:.*?```", "", md, flags=re.S|re.I)
    return re.sub(r"\n{3,}", "\n\n", md).strip()

def slug(text: str) -> str:
    text = re.sub(r"\*\*", "", text)
    text = re.sub(r"[^\w\s가-힣-]", "", text)
    return re.sub(r"\s+", "-", text).lower().strip("-")

def num_from_header(h: str) -> float:
    m = re.search(r"(\d+(?:\.\d+)?)", h)
    return float(m.group(1)) if m else 0.0

def split_sections(md: str) -> Dict[float, str]:
    parts = re.split(r"(^## .+?$)", md, flags=re.M)
    sec: Dict[float, str] = {}
    for i in range(1, len(parts), 2):
        head, body = parts[i].strip(), parts[i+1]
        n = num_from_header(head)
        if n:
            sec[n] = f"{head}\n{body}"
    return sec

# ────────────── 메인 ──────────────
def compile_report(identifier: str, res_dir: Path, delete_mid: bool=False) -> bool:
    pattern = f"*{identifier}*phase*.md"
    files = sorted(res_dir.glob(pattern))
    if not files:
        logging.error("중간 결과 파일이 없습니다.")
        return False
    logging.info(f"컴파일 대상 파일 {len(files)}개 발견")

    sections, summary = {}, ""
    for fp in files:
        original_txt = fp.read_text(encoding="utf-8")
        processed_txt = _preprocess_content(original_txt) # 비표준 헤더를 표준 형식으로 변환
        if re.search(r"gate_status\s*:\s*[\"']?blocked[\"']?", processed_txt, re.I):
            logging.error(f"{fp.name} : gate_status=blocked ➜ 보고서 중단")
            return False
        new_sections = split_sections(strip_blocks(processed_txt))
        if not new_sections:
            logging.warning(f"파일 '{fp.name}'에서 유효한 섹션(## 번호. 제목)을 찾지 못했습니다. 건너뜁니다.")
        sections.update(new_sections)
        m = re.search(r"final_summary\s*:\s*\"(.+?)\"", original_txt, re.S)
        if m: summary = m.group(1).strip()

    if summary:
        sections[0.5] = f"## Executive Summary\n\n{summary}"

    # 목차
    toc = ["## 목차", ""]
    for k in sorted(sections):
        h = re.sub(r"^##\s*", "", sections[k].splitlines()[0])
        toc.append(f"{k}. [{h}](#{slug(f'{k}-{h}')})")
    toc_md = "\n".join(toc)

    title = f"# {identifier.replace('_',' ').title()} 심층 분석 최종 보고서"
    body = [title, "", toc_md, "\n---\n"]
    for k in sorted(sections):
        body += [sections[k], "\n---\n"]
    report = "\n".join(body).rstrip("-\n")

    out = res_dir / f"{datetime.now():%Y%m%d}_{identifier}_final_report.md"
    out.write_text(report, encoding="utf-8")
    logging.info(f"✅ 보고서 저장: {out}")

    if delete_mid:
        for fp in files:
            fp.unlink()
            logging.info(f"삭제: {fp.name}")
    return True

# ────────────── CLI ──────────────
if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Phase 결과 → 최종 보고서 컴파일")
    p.add_argument("identifier", help="텍스트 식별자(ex. welker_creation)")
    p.add_argument("--results_path", default="results")
    p.add_argument("--delete-intermediate", action="store_true")
    a = p.parse_args()
    ok = compile_report(a.identifier, Path(a.results_path), a.delete_intermediate)
    sys.exit(0 if ok else 1)
