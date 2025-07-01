# compile_report_v2.py
import argparse
import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ---------- 유틸 함수 ----------
def remove_yaml_blocks(md: str) -> str:
    """phase_results YAML, 요약, 진행률 블록 제거"""
    # phase_results
    md = re.sub(r"```yaml\s*?\n?phase_results:.+?\n```", "", md,
                flags=re.DOTALL)
    # 200자 요약(quote·blockquote 형태 포함)
    md = re.sub(r">.{0,10}summary_200_chars.+?\n", "", md)
    # 진행률 블록
    md = re.sub(r"```\s*\n?Phase 진행률:.+?\n```", "", md, flags=re.DOTALL)
    # 여분 개행 정리
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip()

def slugify(text: str) -> str:
    text = re.sub(r"\*\*", "", text)
    text = re.sub(r"[^\w\s가-힣-]", "", text)
    text = re.sub(r"\s+", "-", text).lower()
    return re.sub(r"-{2,}", "-", text).strip("-")

def extract_section_num(header: str) -> float:
    """
    ## 2. 핵심 개념  → 2
    ## Phase 2.5: 수렴도  → 2.5
    """
    m = re.search(r"(\d+(?:\.\d+)?)", header)
    return float(m.group(1)) if m else 0.0

# ---------- 파서 ----------
def split_sections(md: str) -> Dict[float, str]:
    """## 헤더 기준으로 본문 분할"""
    parts = re.split(r"(^## .+?$)", md, flags=re.MULTILINE)
    sections: Dict[float, str] = {}
    for i in range(1, len(parts), 2):
        header, body = parts[i].strip(), parts[i + 1]
        num = extract_section_num(header)
        if num:
            sections[num] = f"{header}\n{body}"
    return sections

# ---------- 메인 로직 ----------
def compile_report(identifier: str, results_dir: Path,
                   delete_intermediate: bool = False) -> bool:
    logging.info("=== 최종 보고서 생성 시작 ===")

    # 1) 파일 탐색 패턴
    pattern = f"*{identifier}*phase*.md"
    files = sorted(results_dir.glob(pattern))
    if not files:
        logging.error("중간 결과 파일을 찾을 수 없습니다.")
        return False
    logging.info(f"{len(files)}개 파일 발견: {[f.name for f in files]}")

    # 2) gate_status 검증 및 섹션 파싱
    sections_all: Dict[float, str] = {}
    final_summary = ""
    for fp in files:
        txt = fp.read_text(encoding="utf-8")
        if re.search(r"gate_status:\s*\"blocked\"", txt):
            logging.error(f"게이트 차단 감지: {fp.name}. 보고서 생성을 중단합니다.")
            return False

        txt_clean = remove_yaml_blocks(txt)
        secs = split_sections(txt_clean)
        # Phase 4 final_summary 추출
        fs_match = re.search(r"final_summary:\s*\"(.+?)\"", txt, re.DOTALL)
        if fs_match:
            final_summary = fs_match.group(1).strip()
        sections_all.update(secs)

    if final_summary:
        sections_all[0.5] = f"## Executive Summary\n\n{final_summary}"

    # 3) TOC 생성
    toc_lines = []
    for num in sorted(sections_all):
        header_line = sections_all[num].splitlines()[0]
        clean_header = re.sub(r"^##\s*", "", header_line)
        slug = slugify(f"{num}-{clean_header}")
        toc_lines.append(f"{num}. [{clean_header}](#{slug})")
    toc_md = "## 목차\n\n" + "\n".join(toc_lines)

    # 4) 최종 조립
    title = f"# {identifier.replace('_', ' ').title()} 심층 분석 최종 보고서"
    body_parts = [title, "", toc_md, "\n---\n"]
    for num in sorted(sections_all):
        body_parts.append(sections_all[num])
        body_parts.append("\n---\n")
    report = "\n".join(body_parts).rstrip("-\n")

    # 5) 저장
    out_name = f"{datetime.now():%Y%m%d}_{identifier}_final_report.md"
    out_path = results_dir / out_name
    out_path.write_text(report, encoding="utf-8")
    logging.info(f"✔ 보고서 저장 완료: {out_path}")

    # 6) 옵션: 중간 파일 삭제
    if delete_intermediate:
        for fp in files:
            fp.unlink()
            logging.info(f"삭제: {fp.name}")

    return True

# ---------- CLI ----------
if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description="Analysis_Th 중간 결과를 최종 보고서로 컴파일")
    p.add_argument("identifier", help="텍스트 식별자(ex. welker_resurrection)")
    p.add_argument("--results_path", default="results",
                   help="중간 결과가 저장된 디렉터리")
    p.add_argument("--delete-intermediate", action="store_true",
                   help="완료 후 중간 파일 삭제")
    args = p.parse_args()
    success = compile_report(
        args.identifier, Path(args.results_path), args.delete_intermediate)
    sys.exit(0 if success else 1)
