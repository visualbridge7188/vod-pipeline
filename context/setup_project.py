import shutil
import sys
from pathlib import Path

SOURCE_DIR = Path(__file__).resolve().parent

def setup_project(target_dir_str=None):
    if target_dir_str:
        target_path = Path(target_dir_str).resolve()
    else:
        target_path = Path.cwd().resolve()

    print("🚀 [병원마케팅 프로젝트 환경 세팅 시작]")
    print(f"  - 소스 디렉토리: {SOURCE_DIR}")
    print(f"  - 대상 프로젝트 디렉토리: {target_path}")

    target_path.mkdir(parents=True, exist_ok=True)
    target_context = target_path / "context"
    target_context.mkdir(parents=True, exist_ok=True)

    copied_files = []
    for item in SOURCE_DIR.iterdir():
        if item.is_file() and item.name not in ("setup_project.py",):
            dest_file = target_context / item.name
            shutil.copy2(item, dest_file)
            copied_files.append(item.name)

    print(f"✅ context 파일 복사 완료 ({len(copied_files)}개): {', '.join(copied_files)}")

    template_file = SOURCE_DIR / "AGENTS_TEMPLATE.md"
    target_agents_md = target_path / "AGENTS.md"
    if template_file.exists():
        agents_content = template_file.read_text(encoding="utf-8")
        target_agents_md.write_text(agents_content, encoding="utf-8")
        print(f"✅ 프로젝트 루트 AGENTS.md 배포 완료: {target_agents_md}")
    else:
        print("⚠️ AGENTS_TEMPLATE.md를 찾을 수 없습니다.")

    print("")
    print("🎉 [세팅 완료 안내]")
    print(f"  1. 이제 이 프로젝트 폴더({target_path})에서 새 Codex 세션을 열면 AGENTS.md가 자동 인식됩니다.")
    print(f"  2. 에이전트가 context/ 내 문서와 노션 35개 에셋을 즉시 기반 맥락으로 활용합니다.")
    print(f"  3. 실제 업무 수행 후 '프롬프트 개선 루프'에 따라 AGENTS.md와 프롬프트를 지속 고도화하십시오.")
    print("")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    setup_project(target)
