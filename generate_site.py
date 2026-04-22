from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parents[2]

BOOK_ASSETS_DIR = (
    REPO_ROOT
    / "01_sources"
    / "01_books"
    / "03_领导管理与组织教练"
    / "领导者的意识进化"
    / "assets"
)
N_NOTES_DIR = REPO_ROOT / "02_collections" / "2_N_concepts" / "N_notes"
K_THEME_DIR = REPO_ROOT / "02_collections" / "3_K_themes" / "01_by_theme"
K_BOOK_DIR = REPO_ROOT / "02_collections" / "3_K_themes" / "02_by_book"
SOURCE_XHS_DIR = REPO_ROOT / "03_outputs" / "04_by_book" / "领导者的意识进化" / "小红书图"
SOURCE_INFOGRAPHICS_DIR = REPO_ROOT / "03_outputs" / "04_by_book" / "领导者的意识进化" / "infographics"
SOURCE_SCENES_DIR = REPO_ROOT / "03_outputs" / "04_by_book" / "领导者的意识进化" / "scenes"

VAULT_DIR = PROJECT_ROOT / "vault"
WEB_VAULT_DIR = PROJECT_ROOT / "web" / "public" / "vault"
WEB_IMAGE_DIR = PROJECT_ROOT / "web" / "public" / "chapter-images"
WEB_NOTE_IMAGE_DIR = PROJECT_ROOT / "web" / "public" / "note-images"
GRAPH_DATA_PATH = PROJECT_ROOT / "web" / "src" / "data" / "graphData.js"
TODAY = date.today().isoformat()
BUILD_VERSION = datetime.now().strftime("%Y%m%d%H%M%S")


NODE_TYPE_META = {
    "topic": {"label": "主题", "color": "#3f6c78", "size": 10},
    "chapter": {"label": "章节", "color": "#9f6a3a", "size": 11},
    "concept": {"label": "概念", "color": "#6b8566", "size": 9},
    "method": {"label": "方法", "color": "#8c5d7a", "size": 10},
    "scenario": {"label": "场景", "color": "#b07c4d", "size": 10},
    "person": {"label": "人物", "color": "#5c647b", "size": 12},
}

CATEGORY_DIR = {
    "topic": "主题",
    "chapter": "章节",
    "concept": "概念",
    "method": "方法",
    "scenario": "场景",
    "person": "人物",
}

FORBIDDEN_FILE_CHARS = str.maketrans(
    {
        "<": "＜",
        ">": "＞",
        ":": "：",
        "\"": "＂",
        "/": "／",
        "\\": "＼",
        "|": "｜",
        "?": "？",
        "*": "＊",
    }
)

METHOD_KEYWORDS = {
    "提出不同问题": {"提出不同问题", "旧问题句型", "新问题句型", "边际提问"},
    "领导力脚手架": {"领导力脚手架", "发展型教练", "工作即成长场", "组织的双重任务", "众人的任务"},
    "规律性的正式对话": {"规律性的正式对话", "发展型会议", "一对一", "复盘", "反馈会"},
    "边际提问": {"成长边际", "边际提问", "真正的好奇", "结构与内容"},
    "发展型教练": {"发展型教练", "扩展式成长教练", "主体 - 客体转换", "规范主导", "自主导向", "内观自变"},
    "反馈后学习": {"反馈后学习", "发展性反馈", "提出不同问题", "接纳多面向观点"},
    "发展型会议": {"发展型会议", "发展性会议", "共同思考", "工作即成长场"},
}

# 当前这组小红书图按章节正文顺序取前 8 张。
# 如果后续想手调某一章对应哪张图，只要改这个序号列表即可。
CHAPTER_IMAGE_ORDER = [1, 0, 2, 3, 4, 5, 6, 7]
OVERVIEW_IMAGE_INDEX = 0
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".svg", ".webp"}
TOPIC_IMAGE_PATTERN = re.compile(r"^\d+_(.+?)_K卡主题信息图(?:_内置预览)?$")
SCENARIO_IMAGE_PATTERN = re.compile(r"^\d+_(.+)$")


@dataclass
class NodeSpec:
    id: str
    type: str
    tagline: str = ""
    aliases: list[str] = field(default_factory=list)
    source: Path | None = None
    body: str = ""


@dataclass
class MarkdownSection:
    title: str
    body: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def safe_filename(name: str) -> str:
    return name.translate(FORBIDDEN_FILE_CHARS)


def ensure_clean_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def yaml_list(items: list[str]) -> str:
    return json.dumps(items, ensure_ascii=False)


def frontmatter(tags: list[str], layer: str, aliases: list[str] | None = None) -> str:
    lines = [
        "---",
        f"tags: {yaml_list(tags)}",
        f"layer: {layer}",
    ]
    if aliases:
        lines.append(f"aliases: {yaml_list(aliases)}")
    lines.append(f"created: {TODAY}")
    lines.append("---")
    return "\n".join(lines)


def write_note(target: Path, content: str) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content.strip() + "\n", encoding="utf-8")


def write_to_both(relative_path: Path, content: str) -> None:
    write_note(VAULT_DIR / relative_path, content)
    write_note(WEB_VAULT_DIR / relative_path, content)


def strip_first_heading(markdown: str) -> str:
    lines = markdown.splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    while lines and not lines[0].strip():
        lines = lines[1:]
    return "\n".join(lines).strip()


def replace_heading(markdown: str, title: str) -> str:
    return f"# {title}\n\n{strip_first_heading(markdown)}".strip()


def shorten(text: str, limit: int = 56) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    if len(compact) <= limit:
        return compact
    return compact[: limit - 1].rstrip() + "…"


def plain_text(value: str) -> str:
    text = value
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
    text = re.sub(r"(?<!\!)\[([^\]]+)\]\(\s*<?[^)>]+>?\s*\)", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"^>+\s*", "", text)
    text = re.sub(r"^[#\-]+\s*", "", text)
    return re.sub(r"\s+", " ", text).strip()


def derive_tagline(markdown: str, fallback: str) -> str:
    for line in strip_first_heading(markdown).splitlines():
        raw = line.strip()
        clean = plain_text(raw)
        if not clean:
            continue
        if raw.startswith("##") or raw.startswith("###"):
            continue
        if clean.startswith(("创建时间", "最后更新时间", "提取说明", "这是一张", "这是一个")):
            continue
        if len(clean) < 8:
            continue
        return shorten(clean)
    return shorten(fallback)


def bullet_list(items: list[str]) -> str:
    values = [item.strip() for item in items if item and item.strip()]
    if not values:
        return "- 暂无补充"
    return "\n".join(f"- {item}" for item in values)


def numbered_list(items: list[str]) -> str:
    values = [item.strip() for item in items if item and item.strip()]
    if not values:
        return "1. 暂无补充"
    return "\n".join(f"{index}. {item}" for index, item in enumerate(values, start=1))


def section(title: str, body: str) -> str:
    return f"## {title}\n\n{body.strip()}"


def compact_blank_lines(text: str) -> str:
    normalized: list[str] = []
    previous_blank = True
    for raw in text.splitlines():
        line = raw.rstrip()
        if line.strip():
            normalized.append(line)
            previous_blank = False
            continue
        if not previous_blank:
            normalized.append("")
        previous_blank = True
    while normalized and not normalized[-1].strip():
        normalized.pop()
    return "\n".join(normalized).strip()


def clean_source_body(markdown: str) -> str:
    cleaned: list[str] = []
    skip_quote_block = False

    for raw in strip_first_heading(markdown).splitlines():
        stripped = raw.strip()

        if skip_quote_block:
            if stripped.startswith(">") or not stripped:
                continue
            skip_quote_block = False

        if re.match(r"^>\s*提取说明", stripped):
            skip_quote_block = True
            continue

        if re.match(r"^>\s*(创建时间|最后更新时间)\s*[:：]", stripped):
            continue

        if stripped.startswith("这是一张 ") and ("N / Note" in stripped or "K / Knowledge" in stripped):
            continue

        cleaned.append(raw)

    return compact_blank_lines("\n".join(cleaned))


def parse_markdown_sections(markdown: str) -> tuple[str, list[MarkdownSection]]:
    intro_lines: list[str] = []
    sections: list[MarkdownSection] = []
    current_title: str | None = None
    current_lines: list[str] = []

    for line in compact_blank_lines(markdown).splitlines():
        if line.startswith("## "):
            if current_title is None:
                intro = compact_blank_lines("\n".join(intro_lines))
            else:
                sections.append(MarkdownSection(current_title, compact_blank_lines("\n".join(current_lines))))
            current_title = line[3:].strip()
            current_lines = []
            continue

        if current_title is None:
            intro_lines.append(line)
        else:
            current_lines.append(line)

    if current_title is not None:
        sections.append(MarkdownSection(current_title, compact_blank_lines("\n".join(current_lines))))
        intro = compact_blank_lines("\n".join(intro_lines))
    else:
        intro = compact_blank_lines("\n".join(intro_lines))

    return intro, sections


def parse_subsections(markdown: str) -> list[MarkdownSection]:
    sections: list[MarkdownSection] = []
    current_title: str | None = None
    current_lines: list[str] = []

    for line in compact_blank_lines(markdown).splitlines():
        if line.startswith("### "):
            if current_title is not None:
                sections.append(MarkdownSection(current_title, compact_blank_lines("\n".join(current_lines))))
            current_title = line[4:].strip()
            current_lines = []
            continue
        if current_title is not None:
            current_lines.append(line)

    if current_title is not None:
        sections.append(MarkdownSection(current_title, compact_blank_lines("\n".join(current_lines))))

    return sections


def find_section_body(sections: list[MarkdownSection], *keywords: str) -> str:
    for keyword in keywords:
        for item in sections:
            if keyword == item.title or keyword in item.title:
                return item.body
    return ""


def find_subsection_body(markdown: str, keyword: str) -> str:
    for item in parse_subsections(markdown):
        if keyword == item.title or keyword in item.title:
            return item.body
    return ""


def merge_bodies(*parts: str) -> str:
    values = [part.strip() for part in parts if part and part.strip()]
    return "\n\n".join(values)


def dedupe_items(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        value = item.strip()
        if not value or value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def clean_subsection_title(title: str) -> str:
    cleaned = title.strip()
    cleaned = re.sub(r"^(?:方法\s*/\s*动作|概念|案例|比喻|小节)\s*\d+\s*[：:]\s*", "", cleaned)
    return cleaned.strip()


def prune_internal_bullets(markdown: str) -> str:
    hidden_prefixes = (
        "类型：",
        "when_to_use：",
        "expected_effect：",
        "limits：",
        "case_type：",
        "scene_description：",
        "what_it_proves：",
        "linked_concepts：",
        "visual_elements：",
        "default_usage：",
        "metaphor_type：",
        "metaphor_summary：",
    )
    kept_lines = []
    for raw in markdown.splitlines():
        stripped = raw.strip()
        if stripped.startswith("- ") and any(stripped[2:].startswith(prefix) for prefix in hidden_prefixes):
            continue
        kept_lines.append(raw)
    return compact_blank_lines("\n".join(kept_lines))


def render_subsections(markdown: str, max_subsections: int) -> str:
    sections = parse_subsections(markdown)
    if not sections:
        return prune_internal_bullets(markdown)

    chunks = []
    for item in sections[:max_subsections]:
        title = clean_subsection_title(item.title)
        if item.body:
            chunks.append(f"### {title}\n\n{prune_internal_bullets(item.body)}")
    return "\n\n".join(chunks).strip()


def parse_labeled_bullets(markdown: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in markdown.splitlines():
        stripped = raw.strip()
        if not stripped.startswith("- "):
            continue
        item = stripped[2:].strip()
        if "：" not in item:
            continue
        key, value = item.split("：", 1)
        values[key.strip()] = value.strip()
    return values


def top_level_numbered_items(markdown: str) -> list[str]:
    items: list[str] = []
    for raw in markdown.splitlines():
        stripped = raw.strip()
        if not re.match(r"^\d+\.\s+", stripped):
            continue
        items.append(plain_text(re.sub(r"^\d+\.\s*", "", stripped)))
    return items


def top_level_bullet_items(markdown: str) -> list[str]:
    items: list[str] = []
    for raw in prune_internal_bullets(markdown).splitlines():
        stripped = raw.strip()
        if not stripped.startswith("- "):
            continue
        items.append(stripped[2:].strip())
    return items


def collect_wikilinks(*bodies: str, limit: int | None = None) -> list[str]:
    links: list[str] = []
    for body in bodies:
        links.extend(re.findall(r"\[\[([^\]]+)\]\]", body))
    unique = dedupe_items(links)
    if limit is None:
        return unique
    return unique[:limit]


def normalize_blurb(text: str, fallback: str = "", remove_prefixes: list[str] | None = None) -> str:
    value = plain_text(text) if text else ""
    for label in ["核心问题", "一句话", "本章核心问题", "作者介绍"]:
        value = re.sub(rf"^{re.escape(label)}\s*[:：]\s*", "", value)
    for prefix in remove_prefixes or []:
        value = re.sub(rf"^{re.escape(prefix)}\s*[:：]\s*", "", value)
    return value.strip() or fallback.strip()


def strip_hidden_lines(text: str, hidden_ids: set[str]) -> str:
    cleaned = text
    for hidden_id in hidden_ids:
        cleaned = re.sub(rf"^.*\[\[{re.escape(hidden_id)}\]\].*$", "", cleaned, flags=re.MULTILINE)
    return compact_blank_lines(cleaned)


def chapter_source(index: int, title: str) -> Path:
    return BOOK_ASSETS_DIR / f"单章深入提取_第{index:02d}章_{title}.md"


def image_sort_key(path: Path) -> tuple[int, str]:
    match = re.search(r"_(\d+)_", path.name)
    if match:
        return (int(match.group(1)), path.name)
    return (9999, path.name)


def freeze_patterns(text: str, patterns: list[str]) -> tuple[str, dict[str, str]]:
    placeholders: dict[str, str] = {}
    frozen = text
    for pattern in patterns:
        regex = re.compile(pattern)

        def repl(match: re.Match[str]) -> str:
            key = f"__FREEZE_{len(placeholders)}__"
            placeholders[key] = match.group(0)
            return key

        frozen = regex.sub(repl, frozen)
    return frozen, placeholders


def restore_patterns(text: str, placeholders: dict[str, str]) -> str:
    restored = text
    for key, value in placeholders.items():
        restored = restored.replace(key, value)
    return restored


def rewrite_markdown_links(text: str, stem_to_node: dict[str, str], name_to_node: dict[str, str]) -> str:
    pattern = re.compile(r"(?<!\!)\[([^\]]+)\]\(\s*<?([^)>]+?)>?\s*\)")

    def repl(match: re.Match[str]) -> str:
        label = match.group(1).strip()
        target = match.group(2).strip()
        normalized = target.split("#", 1)[0]
        if normalized.startswith(("http://", "https://", "mailto:")):
            return label
        stem = Path(normalized).stem
        node_id = stem_to_node.get(stem)
        if node_id:
            display = label if label in name_to_node else node_id
            return f"[[{display}]]"
        return label

    return pattern.sub(repl, text)


def build_linker(name_to_node: dict[str, str], excluded: set[str]):
    names = [name for name in name_to_node if name not in excluded]
    names = sorted(names, key=len, reverse=True)
    if not names:
        return lambda text: text
    pattern = re.compile("|".join(re.escape(name) for name in names))

    def link_text(text: str) -> str:
        frozen, placeholders = freeze_patterns(
            text,
            [r"```[\s\S]*?```", r"`[^`\n]+`", r"\[\[[^\]]+\]\]"],
        )
        linked = pattern.sub(lambda match: f"[[{match.group(0)}]]", frozen)
        return restore_patterns(linked, placeholders)

    return link_text


def scenario_to_method_ids(text: str, related_concepts: list[str]) -> list[str]:
    haystack = " ".join([text, *related_concepts])
    matches: list[str] = []
    for method_id, keywords in METHOD_KEYWORDS.items():
        if any(keyword in haystack for keyword in keywords):
            matches.append(method_id)
    return matches


def related_chapter_ids(chapter_keywords: dict[str, set[str]], names: list[str]) -> list[str]:
    matches: list[str] = []
    for chapter_id, keywords in chapter_keywords.items():
        if any(name in keywords for name in names):
            matches.append(chapter_id)
    return matches


def copy_chapter_images(chapter_ids: list[str]) -> dict[str, str]:
    ensure_clean_dir(WEB_IMAGE_DIR)
    node_images: dict[str, str] = {}

    if not SOURCE_XHS_DIR.exists():
        return node_images

    images = sorted(SOURCE_XHS_DIR.glob("*.jpg"), key=image_sort_key)
    if not images:
        return node_images

    overview = WEB_IMAGE_DIR / "overview.jpg"
    overview_source_index = min(OVERVIEW_IMAGE_INDEX, len(images) - 1)
    shutil.copy2(images[overview_source_index], overview)
    for node_id in ["全书摘要", "全书论证链", "K卡N卡总表"]:
        node_images[node_id] = "/chapter-images/overview.jpg"

    for chapter_position, chapter_id in enumerate(chapter_ids, start=1):
        if chapter_position - 1 >= len(CHAPTER_IMAGE_ORDER):
            break
        source_index = CHAPTER_IMAGE_ORDER[chapter_position - 1]
        if source_index >= len(images):
            break
        target = WEB_IMAGE_DIR / f"chapter-{chapter_position}.jpg"
        shutil.copy2(images[source_index], target)
        node_images[chapter_id] = f"/chapter-images/chapter-{chapter_position}.jpg"

    return node_images


def copy_named_public_image(source: Path, node_id: str) -> str:
    WEB_NOTE_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    target_name = f"{safe_filename(node_id)}{source.suffix.lower()}"
    target = WEB_NOTE_IMAGE_DIR / target_name
    shutil.copy2(source, target)
    return f"/note-images/{target_name}"


def sync_topic_and_scenario_images(valid_node_ids: set[str]) -> None:
    for source_dir, pattern in [
        (SOURCE_INFOGRAPHICS_DIR, TOPIC_IMAGE_PATTERN),
        (SOURCE_SCENES_DIR, SCENARIO_IMAGE_PATTERN),
    ]:
        if not source_dir.exists():
            continue
        for source in sorted(source_dir.iterdir()):
            if not source.is_file() or source.suffix.lower() not in IMAGE_EXTENSIONS:
                continue
            match = pattern.match(source.stem)
            if not match:
                continue
            node_id = match.group(1).strip()
            if node_id not in valid_node_ids:
                continue
            copy_named_public_image(source, node_id)


def collect_public_note_images(valid_node_ids: set[str]) -> dict[str, str]:
    node_images: dict[str, str] = {}
    if not WEB_NOTE_IMAGE_DIR.exists():
        return node_images

    for path in sorted(WEB_NOTE_IMAGE_DIR.iterdir()):
        if not path.is_file() or path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        node_id = path.stem
        if node_id not in valid_node_ids:
            continue
        node_images[node_id] = f"/note-images/{path.name}"

    return node_images


def build_graph_module(
    *,
    site: dict,
    filters: list[dict],
    toc: list[dict],
    home_sections: list[dict],
    file_map: dict,
    node_images: dict,
    nodes: list[dict],
    links: list[dict],
    link_labels: dict,
) -> str:
    def dump(value) -> str:
        return json.dumps(value, ensure_ascii=False, indent=2)

    parts = [
        f"export const SITE = {dump(site)}",
        f"export const NODE_TYPE_META = {dump(NODE_TYPE_META)}",
        f"export const FILTERS = {dump(filters)}",
        f"export const TOC = {dump(toc)}",
        f"export const HOME_SECTIONS = {dump(home_sections)}",
        f"export const FILE_MAP = {dump(file_map)}",
        f"export const NODE_IMAGES = {dump(node_images)}",
        f"export const NODES = {dump(nodes)}",
        f"export const LINKS = {dump(links)}",
        f"export const LINK_LABELS = {dump(link_labels)}",
    ]
    return "\n\n".join(parts) + "\n"


def main() -> None:
    structured = read_json(BOOK_ASSETS_DIR / "结构化知识.json")

    book = structured["book_metadata"]
    chapter_map = structured["chapter_map"]
    book_skeleton = structured["book_skeleton"]
    part_structure = structured["part_structure"]
    logic_chain = structured["logic_chain"]
    core_concepts = structured["core_concepts"]
    scenarios = structured["canonical_scenarios"]

    # 这两张卡现在已经在上游 N_notes 中补齐；这里同步把站点运行时的结构地图补成四结构版本，
    # 这样内容总览、章节延伸阅读和图谱关系都会一起长出来。
    book_skeleton["must_keep_concepts"] = dedupe_items(
        ["四种心智结构", "以我为尊", *book_skeleton["must_keep_concepts"]]
    )
    if len(chapter_map) > 1:
        chapter_map[1]["core_concepts"] = dedupe_items(
            ["四种心智结构", "以我为尊", *chapter_map[1]["core_concepts"]]
        )
    if len(chapter_map) > 3:
        chapter_map[3]["core_concepts"] = dedupe_items(
            ["以我为尊", *chapter_map[3]["core_concepts"]]
        )

    ensure_clean_dir(VAULT_DIR)
    ensure_clean_dir(WEB_VAULT_DIR)
    for folder in sorted(set(CATEGORY_DIR.values())):
        (VAULT_DIR / folder).mkdir(parents=True, exist_ok=True)
        (WEB_VAULT_DIR / folder).mkdir(parents=True, exist_ok=True)

    concept_lookup = {item["name"]: item for item in core_concepts}
    overview_id = "全书导读"
    overview_aliases = ["全书摘要", f"《{book['title']}》全书摘要"]
    logic_id = "全书脉络"
    logic_aliases = ["全书论证链"]
    content_map_id = "核心内容总览"
    content_map_aliases = ["K卡N卡总表", "整本书K卡_N卡总表", "整本书K卡/N卡总表"]
    content_direction_id = "内容拆解方向"
    content_direction_aliases = ["内容选题角度", f"《{book['title']}》选题角度"]
    visual_direction_id = "图解表达线索"
    visual_direction_aliases = ["视觉表达钩子", f"《{book['title']}》视觉钩子"]

    hidden_web_ids = {content_direction_id, visual_direction_id}

    theme_specs = [
        NodeSpec("领导者的意识进化", "topic", source=K_BOOK_DIR / "领导者的意识进化.md", aliases=["领导者的心智进化"]),
        NodeSpec("复杂世界中的领导者成长", "topic", source=K_THEME_DIR / "复杂世界中的领导者成长.md"),
        NodeSpec("领导力瓶颈不在技能，而在心智复杂度", "topic", source=K_THEME_DIR / "领导力瓶颈不在技能，而在心智复杂度.md"),
        NodeSpec("从结构判断到成长支持：如何找到成长边际", "topic", source=K_THEME_DIR / "从结构判断到成长支持：如何找到成长边际.md"),
        NodeSpec("为什么很多培训回到工作里人却没变", "topic", source=K_THEME_DIR / "为什么很多培训回到工作里人却没变.md"),
        NodeSpec("工作现场如何变成发展容器", "topic", source=K_THEME_DIR / "工作现场如何变成发展容器.md"),
    ]
    topic_specs = [
        NodeSpec(overview_id, "topic", tagline=book["core_one_liner"], source=BOOK_ASSETS_DIR / "全书摘要.md", aliases=overview_aliases),
        NodeSpec(logic_id, "topic", tagline="用 10 步把这本书从复杂世界的领导难题，推进到工作即成长场。", aliases=logic_aliases),
        NodeSpec(content_map_id, "topic", tagline="把这本书最值得留下的主题、概念和方法收成一张总览图。", source=BOOK_ASSETS_DIR / "整本书K卡_N卡总表.md", aliases=content_map_aliases),
        NodeSpec(content_direction_id, "topic", tagline="把全书拆成适合做内容、课程和表达的高价值切口。", source=BOOK_ASSETS_DIR / "选题角度.md", aliases=content_direction_aliases),
        NodeSpec(visual_direction_id, "topic", tagline="把抽象心智结构翻成更适合图解与页面表达的视觉对象。", source=BOOK_ASSETS_DIR / "视觉钩子.md", aliases=visual_direction_aliases),
    ]

    chapter_specs: list[NodeSpec] = []
    chapter_ids: list[str] = []
    for index, chapter in enumerate(chapter_map, start=1):
        node_id = f"{chapter['chapter']} {chapter['title']}"
        chapter_ids.append(node_id)
        chapter_specs.append(
            NodeSpec(
                node_id,
                "chapter",
                tagline=chapter["key_question"],
                aliases=[chapter["title"]],
                source=chapter_source(index, chapter["title"]),
            )
        )

    concept_specs = [
        NodeSpec("成人发展理论", "concept", source=N_NOTES_DIR / "成人发展理论.md"),
        NodeSpec("四种心智结构", "concept", source=N_NOTES_DIR / "四种心智结构.md", aliases=["四种心智"]),
        NodeSpec("主体 - 客体转换", "concept", aliases=["主体客体转换"], tagline=concept_lookup["主体 - 客体转换"]["solves_what"]),
        NodeSpec("以我为尊", "concept", source=N_NOTES_DIR / "以我为尊.md"),
        NodeSpec("规范主导", "concept", source=N_NOTES_DIR / "规范主导.md"),
        NodeSpec("自主导向", "concept", source=N_NOTES_DIR / "自主导向.md"),
        NodeSpec("内观自变", "concept", source=N_NOTES_DIR / "内观自变.md"),
        NodeSpec("结构与内容", "concept", source=N_NOTES_DIR / "结构与内容.md"),
        NodeSpec("成长边际", "concept", source=N_NOTES_DIR / "成长边际.md"),
        NodeSpec("转化性学习", "concept", source=N_NOTES_DIR / "转化性学习.md", aliases=["转化式专业发展"]),
        NodeSpec("跨层级空间", "concept", source=N_NOTES_DIR / "跨层级空间.md"),
        NodeSpec("转化性心智习惯", "concept", source=N_NOTES_DIR / "转化性心智习惯.md"),
        NodeSpec("工作即成长场", "concept", source=N_NOTES_DIR / "工作即成长场.md"),
    ]
    method_specs = [
        NodeSpec("边际提问", "method", source=N_NOTES_DIR / "边际提问.md", aliases=["发展性提问"]),
        NodeSpec("发展型教练", "method", source=N_NOTES_DIR / "发展型教练.md", aliases=["扩展式成长教练"]),
        NodeSpec("反馈后学习", "method", source=N_NOTES_DIR / "反馈后学习.md", aliases=["发展性反馈"]),
        NodeSpec("发展型会议", "method", source=N_NOTES_DIR / "发展型会议.md", aliases=["发展性会议"]),
    ]
    concept_specs.extend(
        [
            NodeSpec("信息性学习", "concept", source=N_NOTES_DIR / "信息性学习.md"),
            NodeSpec("接纳多面向观点", "concept", source=N_NOTES_DIR / "接纳多面向观点.md"),
            NodeSpec("看见系统全貌", "concept", source=N_NOTES_DIR / "看见系统全貌.md"),
            NodeSpec("组织的双重任务", "concept", source=N_NOTES_DIR / "组织的双重任务.md"),
            NodeSpec("众人的任务", "concept", source=N_NOTES_DIR / "众人的任务.md"),
        ]
    )
    method_specs.extend(
        [
            NodeSpec("提出不同问题", "method", source=N_NOTES_DIR / "提出不同问题.md"),
            NodeSpec("领导力脚手架", "method", source=N_NOTES_DIR / "领导力脚手架.md"),
            NodeSpec("规律性的正式对话", "method", source=N_NOTES_DIR / "规律性的正式对话.md"),
        ]
    )
    scenario_specs = [
        NodeSpec(item["scenario"], "scenario", tagline=item["what_it_shows"], aliases=[item["what_it_shows"]])
        for item in scenarios
    ]
    author_spec = NodeSpec(book["author"], "person", tagline=f"{book['title']} 作者；{book['domain']}")

    specs = topic_specs + theme_specs + chapter_specs + concept_specs + method_specs + scenario_specs + [author_spec]
    spec_by_id = {spec.id: spec for spec in specs}
    author_spec.aliases.extend(["Jennifer Garvey Berger", "珍妮弗·加维·伯格"])
    author_spec.tagline = "把成人发展理论推进到领导、教练、反馈与组织设计现场的作者"

    for spec in specs:
        if spec.source and not spec.tagline:
            spec.tagline = derive_tagline(read_text(spec.source), spec.id)

    name_to_node: dict[str, str] = {}
    stem_to_node: dict[str, str] = {}
    for spec in specs:
        name_to_node[spec.id] = spec.id
        for alias in spec.aliases:
            name_to_node[alias] = spec.id
        if spec.source:
            stem_to_node[spec.source.stem] = spec.id

    def link_text(text: str, current_spec: NodeSpec) -> str:
        excluded = {current_spec.id, *current_spec.aliases}
        return build_linker(name_to_node, excluded)(text)

    theme_ids = [spec.id for spec in theme_specs]
    concept_ids = [spec.id for spec in concept_specs]
    method_ids = [spec.id for spec in method_specs]
    scenario_ids = [spec.id for spec in scenario_specs]

    journey_map = [
        {
            "level": "LV.0",
            "stage": "总纲入口",
            "node": overview_id,
            "image": "/chapter-images/overview.jpg",
            "summary": book["core_one_liner"],
            "bridgeToNext": chapter_map[0]["key_question"],
        }
    ]
    stage_labels = [
        "总透镜",
        "结构坐标",
        "成长边际",
        "教练支持",
        "学习容器",
        "习惯升级",
        "领导工作",
        "组织收束",
    ]
    for index, chapter in enumerate(chapter_map):
        journey_map.append(
            {
                "level": f"LV.{index + 1}",
                "stage": stage_labels[index],
                "node": chapter_ids[index],
                "image": f"/chapter-images/chapter-{index + 1}.jpg",
                "summary": chapter["reader_output"],
                "bridgeToNext": chapter["bridge_to_next"] if index < len(chapter_map) - 1 else book_skeleton["final_landing"],
            }
        )

    chapter_keywords = {
        chapter_ids[0]: {"成人发展理论", "主体 - 客体转换"},
        chapter_ids[1]: {"四种心智结构", "以我为尊", "规范主导", "自主导向", "内观自变"},
        chapter_ids[2]: {"结构与内容", "成长边际", "边际提问"},
        chapter_ids[3]: {"发展型教练", "扩展式成长教练", "以我为尊"},
        chapter_ids[4]: {"转化性学习", "转化式专业发展", "跨层级空间"},
        chapter_ids[5]: {"转化性心智习惯"},
        chapter_ids[6]: {"反馈后学习", "发展性反馈"},
        chapter_ids[7]: {"工作即成长场", "发展型会议", "发展性会议"},
    }
    chapter_keywords.update(
        {
            chapter_ids[4]: {
                "转化性学习",
                "转化式专业发展",
                "跨层级空间",
                "信息性学习",
            },
            chapter_ids[5]: {
                "转化性心智习惯",
                "提出不同问题",
                "接纳多面向观点",
                "看见系统全貌",
            },
            chapter_ids[6]: {
                "反馈后学习",
                "发展性反馈",
                "领导力脚手架",
            },
            chapter_ids[7]: {
                "工作即成长场",
                "发展型会议",
                "发展性会议",
                "组织的双重任务",
                "众人的任务",
                "规律性的正式对话",
            },
        }
    )

    raw_bodies: dict[str, str] = {}

    def _legacy_public_links_section(*bodies: str, limit: int = 5) -> str:
        links = collect_wikilinks(*bodies, limit=limit)
        if not links:
            return ""
        return section("延伸阅读", bullet_list([f"[[{name}]]" for name in links]))

    def _legacy_build_public_topic_body(spec: NodeSpec, cleaned_body: str) -> str:
        intro, sections = parse_markdown_sections(cleaned_body)
        main_questions = find_section_body(sections, "主问题链")
        answers = find_section_body(sections, "这张主题页回答什么")
        judgments = find_section_body(sections, "用于调用的核心判断")
        logic = find_section_body(sections, "核心逻辑")
        mistakes = find_section_body(sections, "常见误判")

        parts = [f"# {spec.id}"]
        blurb = normalize_blurb(intro, spec.tagline, remove_prefixes=[spec.id])
        if blurb:
            parts.append(f"> {blurb}")

        overview = answers or main_questions
        if overview:
            parts.append(section("这篇内容在讲什么", overview))
        if judgments:
            parts.append(section("核心观点", judgments))
        if logic:
            parts.append(section("为什么这很重要", logic))
        if mistakes:
            parts.append(section("常见误区", mistakes))

        links = public_links_section(
            find_section_body(sections, "建议阅读路径"),
            find_section_body(sections, "先看什么，再看什么"),
            find_section_body(sections, "概念入口"),
            find_section_body(sections, "配套问题页"),
            limit=5,
        )
        if links:
            parts.append(links)

        return "\n\n".join(part for part in parts if part.strip())

    def _legacy_build_public_concept_body(spec: NodeSpec, cleaned_body: str) -> str:
        intro, sections = parse_markdown_sections(cleaned_body)
        definition = find_section_body(sections, "核心定义")
        judgments = find_section_body(sections, "可直接调用的判断")
        solves = find_section_body(sections, "这张卡解决什么")
        situations = find_section_body(sections, "进入哪些问题场景")
        decision_rule = find_subsection_body(find_section_body(sections, "判断案例"), "一个简单判断法")
        if not decision_rule:
            decision_rule = find_subsection_body(find_section_body(sections, "典型案例"), "一个简单判断法")
        if not decision_rule:
            decision_rule = render_subsections(merge_bodies(find_section_body(sections, "判断案例"), find_section_body(sections, "典型案例")), 2)
        actions = render_subsections(find_section_body(sections, "场景动作模板"), 3)
        mistakes = find_section_body(sections, "红线边界")

        parts = [f"# {spec.id}"]
        blurb = normalize_blurb(definition or intro, spec.tagline, remove_prefixes=[spec.id])
        if blurb:
            parts.append(f"> {blurb}")
        if judgments:
            parts.append(section("核心观点", judgments))
        if solves:
            parts.append(section("这个概念在解决什么", solves))
        if situations:
            parts.append(section("你会在什么情况下遇到它", situations))
        if decision_rule:
            parts.append(section("怎么判断你需要它", decision_rule))
        if actions:
            parts.append(section("你可以怎么使用", actions))
        if mistakes:
            parts.append(section("使用边界", mistakes))

        links = public_links_section(
            find_section_body(sections, "相关概念"),
            find_section_body(sections, "关联主题页"),
            limit=5,
        )
        if links:
            parts.append(links)

        return "\n\n".join(part for part in parts if part.strip())

    def _legacy_build_public_method_body(spec: NodeSpec, cleaned_body: str) -> str:
        intro, sections = parse_markdown_sections(cleaned_body)
        definition = find_section_body(sections, "核心定义")
        judgments = find_section_body(sections, "可直接调用的判断")
        solves = find_section_body(sections, "这张卡解决什么")
        situations = find_section_body(sections, "进入哪些问题场景")
        cases = render_subsections(merge_bodies(find_section_body(sections, "典型案例"), find_section_body(sections, "判断案例")), 2)
        actions = render_subsections(find_section_body(sections, "场景动作模板"), 3)
        mistakes = find_section_body(sections, "红线边界")

        parts = [f"# {spec.id}"]
        blurb = normalize_blurb(definition or intro, spec.tagline, remove_prefixes=[spec.id])
        if blurb:
            parts.append(f"> {blurb}")
        if situations:
            parts.append(section("什么时候适合用", situations))
        if solves:
            parts.append(section("这能解决什么问题", solves))
        if judgments:
            parts.append(section("用好它的关键", judgments))
        if actions:
            parts.append(section("可以怎么做", actions))
        if cases:
            parts.append(section("一个常见例子", cases))
        if mistakes:
            parts.append(section("常见错误", mistakes))

        links = public_links_section(
            find_section_body(sections, "相关概念"),
            find_section_body(sections, "关联主题页"),
            limit=5,
        )
        if links:
            parts.append(links)

        return "\n\n".join(part for part in parts if part.strip())

    def _legacy_build_public_chapter_body(spec: NodeSpec, cleaned_body: str) -> str:
        intro, sections = parse_markdown_sections(cleaned_body)
        position = parse_labeled_bullets(find_section_body(sections, "章节定位卡"))
        takeaways = top_level_numbered_items(find_section_body(sections, "章节内部推进链"))[:5]
        method_body = render_subsections(find_section_body(sections, "方法、流程与判断动作"), 1)

        chapter_index = chapter_ids.index(spec.id)
        chapter = chapter_map[chapter_index]
        related_links = [
            name_to_node.get(name, name)
            for name in chapter["core_concepts"]
            if name_to_node.get(name, name) in spec_by_id
        ]
        related_links.extend(scenario_to_method_ids(chapter["title"] + chapter["key_question"], chapter["core_concepts"]))
        if chapter_index > 0:
            related_links.append(chapter_ids[chapter_index - 1])
        if chapter_index < len(chapter_ids) - 1:
            related_links.append(chapter_ids[chapter_index + 1])
        related_links = dedupe_items([item for item in related_links if item in spec_by_id])[:5]

        parts = [f"# {spec.id}"]
        blurb = normalize_blurb(
            position.get("本章核心问题", "") or intro,
            spec.tagline,
            remove_prefixes=[spec.id],
        )
        if blurb:
            parts.append(f"> {blurb}")

        overview_items = [
            position.get("本章承担的作用", ""),
            position.get("一句话章结构", ""),
            position.get("本章最终收口", ""),
        ]
        if any(item for item in overview_items):
            parts.append(section("这一章在讲什么", bullet_list(overview_items)))

        if takeaways:
            parts.append(section("这一章最重要的收获", numbered_list(takeaways)))

        why_it_matters = [
            position.get("本章在全书中的位置", ""),
            position.get("本章与上一章的关系", ""),
            position.get("本章与下一章的关系", ""),
        ]
        if any(item for item in why_it_matters):
            parts.append(section("为什么这一章关键", bullet_list(why_it_matters)))

        if method_body:
            parts.append(section("你可以带走的一个方法", method_body))

        if related_links:
            parts.append(section("延伸阅读", bullet_list([f"[[{name}]]" for name in related_links])))

        return "\n\n".join(part for part in parts if part.strip())

    def public_links_section(*bodies: str, limit: int = 5) -> str:
        links = collect_wikilinks(*bodies, limit=limit)
        if not links:
            return ""
        return section("延伸阅读", bullet_list([f"[[{name}]]" for name in links]))

    def node_summary_items(node_ids: list[str], limit: int = 5) -> list[str]:
        items: list[str] = []
        for node_id in dedupe_items(node_ids):
            linked = spec_by_id.get(node_id)
            if not linked:
                continue
            tagline = normalize_blurb(linked.tagline, remove_prefixes=[node_id])
            items.append(f"[[{node_id}]]：{tagline}" if tagline else f"[[{node_id}]]")
            if len(items) >= limit:
                break
        return items

    def build_public_topic_body(spec: NodeSpec, cleaned_body: str) -> str:
        intro, sections = parse_markdown_sections(cleaned_body)
        main_questions = find_section_body(sections, "主问题链")
        answers = find_section_body(sections, "这张主题页回答什么")
        judgments = find_section_body(sections, "用于调用的核心判断")
        logic = find_section_body(sections, "核心逻辑")
        mistakes = find_section_body(sections, "常见误读")
        quick_start = find_section_body(sections, "快速进入")
        reading_path = merge_bodies(
            find_section_body(sections, "建议阅读路径"),
            find_section_body(sections, "先看什么，再看什么"),
            find_section_body(sections, "概念入口"),
        )
        next_topics = merge_bodies(
            find_section_body(sections, "关联主题页"),
            find_section_body(sections, "配套问题页"),
            find_section_body(sections, "可直接外溢的选题"),
        )

        parts = [f"# {spec.id}"]
        blurb = normalize_blurb(intro, spec.tagline, remove_prefixes=[spec.id])
        if blurb:
            parts.append(f"> {blurb}")

        overview = answers or main_questions
        if overview:
            parts.append(section("这篇内容在讲什么", overview))
        if judgments:
            parts.append(section("核心观点", judgments))
        if logic:
            parts.append(section("为什么这很重要", logic))
        if quick_start:
            parts.append(section("先抓住这几个点", prune_internal_bullets(quick_start)))
        if mistakes:
            parts.append(section("常见误区", mistakes))
        if reading_path:
            parts.append(section("可以从哪里进入", prune_internal_bullets(reading_path)))
        if next_topics:
            parts.append(section("还可以往哪几条线展开", prune_internal_bullets(next_topics)))

        links = public_links_section(
            find_section_body(sections, "建议阅读路径"),
            find_section_body(sections, "先看什么，再看什么"),
            find_section_body(sections, "概念入口"),
            find_section_body(sections, "关联主题页"),
            find_section_body(sections, "配套问题页"),
            limit=6,
        )
        if links:
            parts.append(links)

        return "\n\n".join(part for part in parts if part.strip())

    def build_public_overview_body(spec: NodeSpec, cleaned_body: str) -> str:
        intro, sections = parse_markdown_sections(cleaned_body)
        question_card = parse_labeled_bullets(find_section_body(sections, "这本书到底在解决什么问题"))
        key_relations = top_level_numbered_items(find_section_body(sections, "全书主逻辑链"))[:5]

        parts = [f"# {spec.id}"]
        blurb = normalize_blurb(
            question_card.get("一句话总论点", "") or intro,
            spec.tagline,
            remove_prefixes=[spec.id],
        )
        if blurb:
            parts.append(f"> {blurb}")

        parts.append(
            section(
                "这本书在回答什么",
                bullet_list(
                    [
                        question_card.get("这本书最关键的转向", ""),
                        question_card.get("这本书最独特的地方", ""),
                        book_skeleton["main_problem"],
                    ]
                ),
            )
        )
        parts.append(
            section(
                "全书怎么展开",
                bullet_list([f"{item['part']}《{item['title']}》：{item['function']}" for item in part_structure]),
            )
        )
        if key_relations:
            parts.append(section("先抓住的关键推进", numbered_list(key_relations)))
        parts.append(
            section(
                "适合从哪里开始读",
                bullet_list(
                    [
                        f"[[{logic_id}]]：适合先看整本书的问题链是怎么推进的。",
                        "[[领导者的意识进化]]：适合先拿到整本书的主题版总览。",
                        f"[[{chapter_ids[0]}]]：适合先回到理论起点，建立总透镜。",
                        f"[[{chapter_ids[-1]}]]：适合先看这本书最后怎样落到组织与工作现场。",
                    ]
                ),
            )
        )
        parts.append(
            section(
                "继续展开",
                bullet_list(
                    [
                        f"[[{logic_id}]]",
                        "[[领导者的意识进化]]",
                        f"[[{chapter_ids[0]}]]",
                        f"[[{chapter_ids[-1]}]]",
                    ]
                ),
            )
        )

        return "\n\n".join(part for part in parts if part.strip())

    def build_public_content_map_body(spec: NodeSpec, cleaned_body: str) -> str:
        must_keep_nodes = [
            canonical
            for canonical in (name_to_node.get(name) for name in book_skeleton["must_keep_concepts"])
            if canonical in spec_by_id
        ]

        parts = [
            f"# {spec.id}",
            f"> {spec.tagline}",
            section(
                "先抓住这几张总览页",
                bullet_list(
                    node_summary_items(
                        [overview_id, logic_id, "领导者的意识进化", "复杂世界中的领导者成长"],
                        limit=4,
                    )
                ),
            ),
            section("最值得优先看的主题", bullet_list(node_summary_items(theme_ids, limit=5))),
            section("关键概念", bullet_list(node_summary_items(must_keep_nodes or concept_ids, limit=6))),
            section("关键方法", bullet_list(node_summary_items(method_ids, limit=5))),
            section("高代入场景入口", bullet_list(node_summary_items(scenario_ids, limit=4))),
            section(
                "站内入口",
                bullet_list(
                    [
                        f"[[{overview_id}]]：先拿到整本书总览。",
                        f"[[{content_direction_id}]]：继续拆成内容方向。",
                        f"[[{visual_direction_id}]]：继续拆成图解与页面表达。",
                    ]
                ),
            ),
        ]

        return "\n\n".join(part for part in parts if part.strip())

    def build_public_content_direction_body(spec: NodeSpec, cleaned_body: str) -> str:
        intro, sections = parse_markdown_sections(cleaned_body)
        top_outline = render_subsections(find_section_body(sections, "总纲型选题"), 2)
        concept_tracks = render_subsections(find_section_body(sections, "概念卡"), 2)
        method_tracks = render_subsections(find_section_body(sections, "方法卡"), 2)
        org_tracks = render_subsections(find_section_body(sections, "组织实践卡"), 2)
        recommended_chain = top_level_bullet_items(find_section_body(sections, "如果只做一组内容"))[:8]

        parts = [f"# {spec.id}"]
        blurb = normalize_blurb(intro, spec.tagline, remove_prefixes=[spec.id])
        if blurb:
            parts.append(f"> {blurb}")
        if top_outline:
            parts.append(section("最适合先做的总纲内容", top_outline))
        if concept_tracks:
            parts.append(section("适合拆成概念页的方向", concept_tracks))
        if method_tracks:
            parts.append(section("适合拆成方法页的方向", method_tracks))
        if org_tracks:
            parts.append(section("适合拆成组织应用页的方向", org_tracks))
        if recommended_chain:
            parts.append(section("如果只做一组内容，建议这条链", bullet_list(recommended_chain)))
        parts.append(section("适合接着点开的主题", bullet_list(node_summary_items(theme_ids, limit=5))))

        return "\n\n".join(part for part in parts if part.strip())

    def build_public_visual_direction_body(spec: NodeSpec, cleaned_body: str) -> str:
        intro, sections = parse_markdown_sections(cleaned_body)
        overview_visuals = render_subsections(find_section_body(sections, "整本书最值得反复复用的视觉入口"), 3)
        method_visuals = render_subsections(find_section_body(sections, "最适合拆成方法页的视觉对象"), 3)
        org_visuals = render_subsections(find_section_body(sections, "最适合拆成组织实践页的视觉对象"), 3)
        chapter_visuals = top_level_bullet_items(find_section_body(sections, "按章节拆图时最优先抓的对象"))[:8]

        parts = [f"# {spec.id}"]
        blurb = normalize_blurb(intro, spec.tagline, remove_prefixes=[spec.id])
        if blurb:
            parts.append(f"> {blurb}")
        if overview_visuals:
            parts.append(section("整本书最值得先做的图", overview_visuals))
        if method_visuals:
            parts.append(section("适合拆成方法图的方向", method_visuals))
        if org_visuals:
            parts.append(section("适合拆成组织应用图的方向", org_visuals))
        if chapter_visuals:
            parts.append(section("按章节展开时优先抓什么", bullet_list(chapter_visuals)))
        parts.append(section("适合对照阅读的章节", bullet_list([f"[[{name}]]" for name in chapter_ids])))

        return "\n\n".join(part for part in parts if part.strip())

    def build_public_concept_body(spec: NodeSpec, cleaned_body: str) -> str:
        intro, sections = parse_markdown_sections(cleaned_body)
        definition = find_section_body(sections, "核心定义")
        judgments = find_section_body(sections, "可直接调用的判断")
        solves = find_section_body(sections, "这张卡解决什么")
        situations = find_section_body(sections, "进入哪些问题场景")
        decision_rule = find_subsection_body(find_section_body(sections, "判断案例"), "一个简单判断法")
        if not decision_rule:
            decision_rule = find_subsection_body(find_section_body(sections, "典型案例"), "一个简单判断法")
        if not decision_rule:
            decision_rule = render_subsections(
                merge_bodies(find_section_body(sections, "判断案例"), find_section_body(sections, "典型案例")),
                2,
            )
        actions = render_subsections(find_section_body(sections, "场景动作模板"), 3)
        mistakes = find_section_body(sections, "红线边界")

        parts = [f"# {spec.id}"]
        blurb = normalize_blurb(definition or intro, spec.tagline, remove_prefixes=[spec.id])
        if blurb:
            parts.append(f"> {blurb}")
        if judgments:
            parts.append(section("核心观点", judgments))
        if solves:
            parts.append(section("这个概念在解决什么", solves))
        if situations:
            parts.append(section("你会在什么情况下遇到它", situations))
        if decision_rule:
            parts.append(section("怎么判断你需要它", decision_rule))
        if actions:
            parts.append(section("你可以怎么使用", actions))
        if mistakes:
            parts.append(section("使用边界", mistakes))

        links = public_links_section(
            find_section_body(sections, "相关概念"),
            find_section_body(sections, "关联主题页"),
            limit=5,
        )
        if links:
            parts.append(links)

        return "\n\n".join(part for part in parts if part.strip())

    def build_public_method_body(spec: NodeSpec, cleaned_body: str) -> str:
        intro, sections = parse_markdown_sections(cleaned_body)
        definition = find_section_body(sections, "核心定义")
        judgments = find_section_body(sections, "可直接调用的判断")
        solves = find_section_body(sections, "这张卡解决什么")
        situations = find_section_body(sections, "进入哪些问题场景")
        cases = render_subsections(
            merge_bodies(find_section_body(sections, "典型案例"), find_section_body(sections, "判断案例")),
            2,
        )
        actions = render_subsections(find_section_body(sections, "场景动作模板"), 3)
        mistakes = find_section_body(sections, "红线边界")

        parts = [f"# {spec.id}"]
        blurb = normalize_blurb(definition or intro, spec.tagline, remove_prefixes=[spec.id])
        if blurb:
            parts.append(f"> {blurb}")
        if situations:
            parts.append(section("什么时候适合用", situations))
        if solves:
            parts.append(section("这能解决什么问题", solves))
        if judgments:
            parts.append(section("用好它的关键", judgments))
        if actions:
            parts.append(section("可以怎么做", actions))
        if cases:
            parts.append(section("一个常见例子", cases))
        if mistakes:
            parts.append(section("常见错误", mistakes))

        links = public_links_section(
            find_section_body(sections, "相关概念"),
            find_section_body(sections, "关联主题页"),
            limit=5,
        )
        if links:
            parts.append(links)

        return "\n\n".join(part for part in parts if part.strip())

    def build_public_chapter_body(spec: NodeSpec, cleaned_body: str) -> str:
        intro, sections = parse_markdown_sections(cleaned_body)
        position = parse_labeled_bullets(find_section_body(sections, "章节定位卡"))
        takeaways = top_level_numbered_items(find_section_body(sections, "章节内部推进链"))[:6]
        key_concepts = render_subsections(find_section_body(sections, "本章核心概念表"), 3)
        relation_lines = top_level_numbered_items(find_section_body(sections, "本章必须保留的关系线"))[:5]
        examples = render_subsections(find_section_body(sections, "本章案例与比喻库"), 2)
        method_body = render_subsections(find_section_body(sections, "本章方法、流程与判断动作"), 2)

        chapter_index = chapter_ids.index(spec.id)
        chapter = chapter_map[chapter_index]
        related_links = [
            name_to_node.get(name, name)
            for name in chapter["core_concepts"]
            if name_to_node.get(name, name) in spec_by_id
        ]
        related_links.extend(scenario_to_method_ids(chapter["title"] + chapter["key_question"], chapter["core_concepts"]))
        if chapter_index > 0:
            related_links.append(chapter_ids[chapter_index - 1])
        if chapter_index < len(chapter_ids) - 1:
            related_links.append(chapter_ids[chapter_index + 1])
        related_links = dedupe_items([item for item in related_links if item in spec_by_id])[:6]

        parts = [f"# {spec.id}"]
        blurb = normalize_blurb(
            position.get("本章核心问题", "") or intro,
            spec.tagline,
            remove_prefixes=[spec.id],
        )
        if blurb:
            parts.append(f"> {blurb}")

        overview_items = [
            position.get("本章承担的作用", ""),
            position.get("一句话章节结构", ""),
            position.get("本章最终收口", ""),
        ]
        if any(item for item in overview_items):
            parts.append(section("这一章在讲什么", bullet_list(overview_items)))

        if takeaways:
            parts.append(section("这一章最重要的收获", numbered_list(takeaways)))

        why_it_matters = [
            position.get("本章在全书中的位置", ""),
            position.get("本章与上一章的关系", ""),
            position.get("本章与下一章的关系", ""),
            chapter.get("reader_output", ""),
        ]
        if any(item for item in why_it_matters):
            parts.append(section("为什么这一章关键", bullet_list(why_it_matters)))

        if key_concepts:
            parts.append(section("本章关键概念", key_concepts))
        if relation_lines:
            parts.append(section("本章最值得记住的关系", numbered_list(relation_lines)))
        if examples:
            parts.append(section("一个能帮助理解本章的例子", examples))
        if method_body:
            parts.append(section("你可以带走的方法", method_body))
        if related_links:
            parts.append(section("延伸阅读", bullet_list([f"[[{name}]]" for name in related_links])))

        return "\n\n".join(part for part in parts if part.strip())

    def process_source(spec: NodeSpec) -> str:
        markdown = read_text(spec.source)
        body = clean_source_body(markdown)
        body = rewrite_markdown_links(body, stem_to_node, name_to_node)
        if spec.id == overview_id:
            body = build_public_overview_body(spec, body)
        elif spec.id == content_map_id:
            body = build_public_content_map_body(spec, body)
        elif spec.id == content_direction_id:
            body = build_public_content_direction_body(spec, body)
        elif spec.id == visual_direction_id:
            body = build_public_visual_direction_body(spec, body)
        elif spec.type == "chapter":
            body = build_public_chapter_body(spec, body)
        elif spec.type == "concept":
            body = build_public_concept_body(spec, body)
        elif spec.type == "method":
            body = build_public_method_body(spec, body)
        elif spec.type == "topic":
            body = build_public_topic_body(spec, body)
        if spec.id == overview_id:
            body = "\n\n".join(
                [
                    body,
                    section(
                        "继续展开",
                        bullet_list(
                            [
                                f"[[{logic_id}]]",
                                "[[领导者的意识进化]]",
                                f"[[{chapter_ids[0]}]]",
                                f"[[{chapter_ids[-1]}]]",
                            ]
                        ),
                    ),
                ]
            )
        elif spec.id == content_map_id:
            body = "\n\n".join(
                [
                    body,
                    section(
                        "站内入口",
                        bullet_list([f"[[{name}]]" for name in theme_ids + concept_ids[:6] + method_ids[:4]]),
                    ),
                ]
            )
        elif spec.id == content_direction_id:
            body = "\n\n".join(
                [
                    body,
                    section("适合接着点开的主题", bullet_list([f"[[{name}]]" for name in theme_ids])),
                ]
            )
        elif spec.id == visual_direction_id:
            body = "\n\n".join(
                [
                    body,
                    section("适合对照阅读的章节", bullet_list([f"[[{name}]]" for name in chapter_ids])),
                ]
            )
        return replace_heading(link_text(body, spec), spec.id)

    for spec in specs:
        if spec.source:
            raw_bodies[spec.id] = process_source(spec)

    subject_object = concept_lookup["主体 - 客体转换"]
    raw_bodies["主体 - 客体转换"] = "\n\n".join(
        [
            "# 主体 - 客体转换",
            f"> {subject_object['definition']}",
            section("这个概念在解决什么", link_text(subject_object["solves_what"], spec_by_id["主体 - 客体转换"])),
            section(
                "为什么它是全书的转轴",
                bullet_list(
                    [
                        "[[成人发展理论]]真正关键的，不是长了多少知识，而是原本裹挟我们的东西能不能被拿出来看。",
                        "[[发展型教练]]真正有效，不是更会给建议，而是帮助人把主体里的模式逐渐变成可观察的客体。",
                        "[[转化性学习]]和[[转化性心智习惯]]真正推动的，也都是这种视角关系的变化。",
                    ]
                ),
            ),
            section(
                "建议一起看",
                bullet_list(
                    [
                        "[[第一章 心智的层次]]",
                        "[[发展型教练]]",
                        "[[转化性学习]]",
                        "[[转化性心智习惯]]",
                    ]
                ),
            ),
            section("使用边界", link_text(subject_object["boundary"], spec_by_id["主体 - 客体转换"])),
        ]
    )

    raw_bodies[logic_id] = "\n\n".join(
        [
            f"# {logic_id}",
            f"> 用 {len(logic_chain)} 步把这本书从“复杂世界里的领导失灵”推进到“工作即成长场”。",
            section("主问题链", numbered_list([link_text(item, spec_by_id[logic_id]) for item in logic_chain])),
            section(
                "建议阅读路径",
                bullet_list(
                    [
                        "[[领导者的意识进化]]",
                        f"[[{chapter_ids[0]}]]",
                        f"[[{chapter_ids[2]}]]",
                        f"[[{chapter_ids[-1]}]]",
                    ]
                ),
            ),
        ]
    )

    raw_bodies[book["author"]] = "\n\n".join(
        [
            f"# {book['author']}",
            f"> **《{book['title']}》作者**：{book['domain']}",
            section("这本书最核心的贡献", bullet_list([book["core_one_liner"], book["differentiator"]])),
            section("它直接解决什么问题", bullet_list(book["solves_problems"])),
            section("建议从哪里读起", bullet_list([f"[[{overview_id}]]", f"[[{logic_id}]]", "[[领导者的意识进化]]", f"[[{chapter_ids[-1]}]]"])),
        ]
    )

    raw_bodies[book["author"]] = "\n\n".join(
        [
            f"# {book['author']}",
            f"> **《{book['title']}》作者**：{book['domain']}",
            section(
                "作者介绍",
                bullet_list(
                    [
                        "Jennifer Garvey Berger 长期关注成人发展、领导力成长、教练与组织发展，写作视角始终落在“人怎样长出更复杂的理解能力”。",
                        "她关心的不是再给领导者补一套技巧，而是帮助人看见：当现实复杂度上升时，真正先撞墙的往往是心智结构，而不只是知识和方法。",
                        "这本书最有辨识度的地方，是把发展理论从概念层推进到反馈、会议、培训、协作和组织设计这些真实工作场景里。",
                    ]
                ),
            ),
            section(
                "她在这本书里真正关心什么",
                bullet_list(
                    [
                        "为什么很多优秀管理者学了很多、也很努力，却还是会在复杂场景里失灵。",
                        "为什么组织总把结构问题误判成态度问题、沟通问题或执行问题。",
                        "为什么真正的成长，不发生在建议最响亮的地方，而发生在一个人刚好能被推动又不会被压垮的成长边际上。",
                    ]
                ),
            ),
            section("这本书最核心的贡献", bullet_list([book["core_one_liner"], book["differentiator"]])),
            section("它直接在解决什么问题", bullet_list(book["solves_problems"])),
            section(
                "如果你准备继续读她",
                bullet_list(
                    [
                        f"[[{overview_id}]]：先拿到她到底在回答什么大问题。",
                        f"[[{logic_id}]]：再看她如何把理论一步步推进到工作现场。",
                        "[[领导者的意识进化]]：把整本书收成一套可反复调用的判断路径。",
                        f"[[{chapter_ids[-1]}]]：如果你更关心组织落地，可以直接从最后一章进入。",
                    ]
                ),
            ),
        ]
    )

    raw_bodies[logic_id] = "\n\n".join(
        [
            f"# {logic_id}",
            f"> 用 {len(logic_chain)} 步把这本书从“复杂世界里的领导失灵”推进到“工作即成长场”。",
            section("主问题链", numbered_list([link_text(item, spec_by_id[logic_id]) for item in logic_chain])),
            section(
                "为什么这条主线重要",
                bullet_list(
                    [
                        book_skeleton["starting_point"],
                        book_skeleton["core_turn"],
                        book_skeleton["final_landing"],
                    ]
                ),
            ),
            section(
                "顺着主线读会看到什么",
                bullet_list([f"{item['part']}《{item['title']}》：{item['function']}" for item in part_structure]),
            ),
            section(
                "建议阅读路径",
                bullet_list(
                    [
                        "[[领导者的意识进化]]",
                        f"[[{chapter_ids[0]}]]",
                        f"[[{chapter_ids[2]}]]",
                        f"[[{chapter_ids[-1]}]]",
                    ]
                ),
            ),
        ]
    )

    for scenario, spec in zip(scenarios, scenario_specs):
        resolved_concepts = []
        for concept_name in scenario["linked_concepts"]:
            canonical = name_to_node.get(concept_name)
            if canonical and canonical not in resolved_concepts:
                resolved_concepts.append(canonical)
        related_methods = scenario_to_method_ids(spec.id + scenario["what_it_shows"], scenario["linked_concepts"])
        related_chapters = related_chapter_ids(chapter_keywords, scenario["linked_concepts"] + resolved_concepts)
        if not related_chapters:
            related_chapters = [chapter_ids[0], chapter_ids[-1]]
        raw_bodies[spec.id] = "\n\n".join(
            [
                f"# {spec.id}",
                f"> {scenario['what_it_shows']}",
                section("这暴露了什么", link_text(scenario["what_it_shows"], spec)),
                section("为什么这个场景值得记住", link_text(scenario["why_memorable"], spec)),
                section("相关概念", bullet_list([f"[[{item}]]" for item in resolved_concepts])),
                section("适合一起看的方法", bullet_list([f"[[{item}]]" for item in related_methods])),
                section("建议先看哪一章", bullet_list([f"[[{item}]]" for item in related_chapters])),
            ]
        )

    raw_bodies["00_首页"] = "\n\n".join(
        [
            "# 领导者的意识进化 · 单书互动站",
            f"> **核心一句话**：{book['core_one_liner']}",
            section(
                "推荐阅读路径",
                " → ".join(
                    [
                        f"[[{overview_id}]]",
                        "[[领导者的意识进化]]",
                        f"[[{chapter_ids[0]}]]",
                        "[[成长边际]]",
                        f"[[{chapter_ids[-1]}]]",
                    ]
                ),
            ),
            section(
                "升级地图",
                bullet_list(
                    [
                        f"{stage['level']} · {stage['stage']} · [[{stage['node']}]]：{stage['summary']}"
                        for stage in journey_map
                    ]
                ),
            ),
            section(
                "你可以从这些入口开始",
                bullet_list(
                    [
                        f"[[{overview_id}]]：先拿整本书的主问题、三部分推进和最后落点。",
                        f"[[{logic_id}]]：适合一口气看清逻辑推进。",
                        f"[[{content_map_id}]]：直接看这本书最值得留下的主题、概念和方法总览。",
                        f"[[{content_direction_id}]]：适合继续拆成内容、项目或课程。",
                        f"[[{visual_direction_id}]]：适合继续做图解和页面。",
                    ]
                ),
            ),
            section(
                "关注作者",
                bullet_list(
                    [
                        "复杂世界和复杂人性的同行翻译者",
                        "微信公众号：林子-心智进化之路",
                        "小红书：林子-心智进化之路",
                    ]
                ),
            ),
            section(
                "站内模块",
                bullet_list(
                    [
                        "主题：全书入口与关键主题判断。",
                        "章节：八章推进，直接按书的逻辑走。",
                        "概念：把成人发展、结构判断和工作即成长场串起来。",
                        "方法：把边际提问、发展型教练、反馈后学习、发展型会议落到实际动作上。",
                        "场景：从培训无效、反馈失灵、会议空转这些高频问题切入。",
                    ]
                ),
            ),
        ]
    )

    for scenario, spec in zip(scenarios, scenario_specs):
        resolved_concepts = []
        for concept_name in scenario["linked_concepts"]:
            canonical = name_to_node.get(concept_name)
            if canonical and canonical not in resolved_concepts:
                resolved_concepts.append(canonical)
        related_methods = scenario_to_method_ids(spec.id + scenario["what_it_shows"], scenario["linked_concepts"])
        related_chapters = related_chapter_ids(chapter_keywords, scenario["linked_concepts"] + resolved_concepts)
        if not related_chapters:
            related_chapters = [chapter_ids[0], chapter_ids[-1]]

        raw_bodies[spec.id] = "\n\n".join(
            [
                f"# {spec.id}",
                f"> {scenario['what_it_shows']}",
                section(
                    "这类情况表面发生了什么",
                    bullet_list(
                        [
                            f"你在现场看到的，往往就是“{spec.id}”这类反应。",
                            scenario["why_memorable"],
                        ]
                    ),
                ),
                section("底层卡点更可能在哪里", link_text(scenario["what_it_shows"], spec)),
                section("先看哪几个概念", bullet_list(node_summary_items(resolved_concepts, limit=4))),
                section(
                    "可以先怎么应对",
                    bullet_list(node_summary_items(related_methods, limit=3) or node_summary_items(resolved_concepts, limit=3)),
                ),
                section("适合一起看的章节", bullet_list(node_summary_items(related_chapters, limit=3))),
                section(
                    "如果想继续看透它",
                    bullet_list(
                        [
                            f"[[{overview_id}]]：先回到整本书的问题地图。",
                            f"[[{logic_id}]]：再看它在全书逻辑链里处在什么位置。",
                            "[[领导者的意识进化]]：最后回到主题页，把相关概念和方法连起来看。",
                        ]
                    ),
                ),
            ]
        )

    for special_id, builder in [
        (overview_id, build_public_overview_body),
        (content_map_id, build_public_content_map_body),
        (content_direction_id, build_public_content_direction_body),
        (visual_direction_id, build_public_visual_direction_body),
    ]:
        special_spec = spec_by_id[special_id]
        special_body = clean_source_body(read_text(special_spec.source))
        special_body = rewrite_markdown_links(special_body, stem_to_node, name_to_node)
        raw_bodies[special_id] = replace_heading(link_text(builder(special_spec, special_body), special_spec), special_spec.id)

    note_texts: dict[str, str] = {}

    for spec in specs:
        body = raw_bodies[spec.id]
        note_texts[spec.id] = "\n\n".join(
            [
                frontmatter([NODE_TYPE_META[spec.type]["label"]], NODE_TYPE_META[spec.type]["label"], spec.aliases),
                body,
            ]
        )

    public_specs = [spec for spec in specs if spec.id not in hidden_web_ids]
    web_note_texts = {
        spec.id: strip_hidden_lines(note_texts[spec.id], hidden_web_ids)
        for spec in public_specs
    }

    homepage_text = "\n\n".join(
        [
            frontmatter(["首页", book["title"]], "首页"),
            raw_bodies["00_首页"],
        ]
    )

    write_to_both(Path("00_首页.md"), homepage_text)

    file_map: dict[str, str] = {}
    for spec in specs:
        relative = Path(CATEGORY_DIR[spec.type]) / f"{safe_filename(spec.id)}.md"
        write_to_both(relative, note_texts[spec.id])
        file_map[spec.id] = f"/vault/{CATEGORY_DIR[spec.type]}/{safe_filename(spec.id)}.md"

    write_note(
        WEB_VAULT_DIR / Path("00_首页.md"),
        "\n\n".join(
            [
                frontmatter(["首页", book["title"]], "首页"),
                strip_hidden_lines(raw_bodies["00_首页"], hidden_web_ids),
            ]
        ),
    )

    for spec in public_specs:
        relative = Path(CATEGORY_DIR[spec.type]) / f"{safe_filename(spec.id)}.md"
        write_note(WEB_VAULT_DIR / relative, web_note_texts[spec.id])

    for spec in specs:
        if spec.id not in hidden_web_ids:
            continue
        relative = Path(CATEGORY_DIR[spec.type]) / f"{safe_filename(spec.id)}.md"
        hidden_path = WEB_VAULT_DIR / relative
        if hidden_path.exists():
            hidden_path.unlink()
        file_map.pop(spec.id, None)

    public_node_ids = {spec.id for spec in public_specs}
    sync_topic_and_scenario_images(public_node_ids)
    node_images = collect_public_note_images(public_node_ids)
    node_images.update(copy_chapter_images(chapter_ids))
    for node_id in [overview_id, logic_id, content_map_id, "领导者的意识进化"]:
        node_images.setdefault(node_id, "/chapter-images/overview.jpg")

    for node_id in [
        overview_id,
        logic_id,
        content_map_id,
        "全书摘要",
        "全书论证链",
        "K卡N卡总表",
    ]:
        node_images.pop(node_id, None)

    edges: list[dict] = []
    edge_keys: set[tuple[str, str]] = set()
    link_labels: dict[str, str] = {}

    def add_edge(source: str, target: str, label: str) -> None:
        if source == target or source not in spec_by_id or target not in spec_by_id:
            return
        key = (source, target)
        if key in edge_keys:
            return
        edge_keys.add(key)
        edges.append({"source": source, "target": target})
        link_labels[f"{source}→{target}"] = label

    for source_id, content in web_note_texts.items():
        for match in re.findall(r"\[\[([^\]]+)\]\]", content):
            target = name_to_node.get(match)
            if not target:
                continue
            add_edge(source_id, target, f"{NODE_TYPE_META[spec_by_id[source_id].type]['label']}关联")

    add_edge(book["author"], "领导者的意识进化", "作者与书卡")
    add_edge(overview_id, logic_id, "从总览到主线")
    for current, next_chapter in zip(chapter_ids, chapter_ids[1:]):
        add_edge(current, next_chapter, "章节推进")

    toc = [
        {
            "id": "topics",
            "label": "主题入口",
            "color": NODE_TYPE_META["topic"]["color"],
            "sections": [
                {"label": "全书入口", "items": [overview_id, logic_id, content_map_id, content_direction_id, visual_direction_id]},
                {"label": "核心主题", "items": theme_ids},
            ],
        },
        {
            "id": "chapters",
            "label": "章节地图",
            "color": NODE_TYPE_META["chapter"]["color"],
            "sections": [{"label": "八章推进", "items": chapter_ids}],
        },
        {
            "id": "concepts",
            "label": "核心概念",
            "color": NODE_TYPE_META["concept"]["color"],
            "sections": [{"label": "概念", "items": concept_ids}],
        },
        {
            "id": "methods",
            "label": "动作方法",
            "color": NODE_TYPE_META["method"]["color"],
            "sections": [{"label": "方法", "items": method_ids}],
        },
        {
            "id": "scenarios",
            "label": "现实场景",
            "color": NODE_TYPE_META["scenario"]["color"],
            "sections": [{"label": "高代入场景", "items": scenario_ids}],
        },
        {
            "id": "people",
            "label": "作者",
            "color": NODE_TYPE_META["person"]["color"],
            "sections": [{"label": "人物", "items": [book["author"]]}],
        },
    ]

    home_sections = [
        {
            "id": "overview",
            "title": "全书入口",
            "subtitle": "先拿总地图",
            "desc": "先看清主问题链、全书总览和内容化入口，再决定从哪一层往下钻。",
            "color": NODE_TYPE_META["topic"]["color"],
            "nodes": [overview_id, logic_id, content_map_id, content_direction_id, visual_direction_id],
        },
        {
            "id": "themes",
            "title": "核心主题",
            "subtitle": "把书变成可复用判断",
            "desc": "把《领导者的意识进化》从目录，重构成你可反复调用的主题与观点页。",
            "color": NODE_TYPE_META["topic"]["color"],
            "nodes": theme_ids,
        },
        {
            "id": "chapters",
            "title": "章节地图",
            "subtitle": "按原书推进",
            "desc": "八章从结构透镜一路推进到工作即成长场，适合顺读。",
            "color": NODE_TYPE_META["chapter"]["color"],
            "nodes": chapter_ids,
        },
        {
            "id": "concepts",
            "title": "核心概念",
            "subtitle": "把底层概念拿稳",
            "desc": "成人发展、成长边际、转化性学习、工作即成长场，是这本书最值得留下的底层抓手。",
            "color": NODE_TYPE_META["concept"]["color"],
            "nodes": concept_ids,
        },
        {
            "id": "methods",
            "title": "方法工具",
            "subtitle": "把成长落到动作",
            "desc": "从边际提问到发展型会议，把理论接回一对一、反馈、会议和带教现场。",
            "color": NODE_TYPE_META["method"]["color"],
            "nodes": method_ids,
        },
        {
            "id": "scenarios",
            "title": "现实场景",
            "subtitle": "从高频卡点切入",
            "desc": "培训无效、反馈失灵、会议空转，这些现实痛点都可以回到这本书里重新解释。",
            "color": NODE_TYPE_META["scenario"]["color"],
            "nodes": scenario_ids,
        },
    ]

    toc[0]["sections"][0]["items"] = [overview_id, logic_id, content_map_id]
    home_sections[0]["nodes"] = [overview_id, logic_id, content_map_id]

    filters = [
        {"type": node_type, "label": meta["label"], "color": meta["color"]}
        for node_type, meta in NODE_TYPE_META.items()
    ]

    site = {
        "title": book["title"],
        "shortTitle": "心智进化",
        "subtitle": "成人发展、领导力成长与工作即成长场",
        "description": "基于《领导者的意识进化》整理的单书知识站，把全书入口、核心主题、关键概念、方法工具与现实场景串成可点击的阅读地图。",
        "heroOverline": "LEADERSHIP · DEVELOPMENT · COMPLEXITY",
        "heroTitleLines": [book["title"], "把复杂世界中的领导成长做成可点击地图"],
        "creatorLabel": "整理与输出",
        "creatorName": "林子-心智进化之路",
        "footerNote": "复杂世界和复杂人性的同行翻译者",
        "assetVersion": BUILD_VERSION,
        "searchPlaceholder": "搜索主题、章节、概念、方法、场景…",
        "recommendedPath": [overview_id, "领导者的意识进化", chapter_ids[0], "成长边际", chapter_ids[-1]],
        "quickLinks": [logic_id, content_map_id, "领导力瓶颈不在技能，而在心智复杂度", "工作即成长场", "发展型教练", "发展型会议"],
        "followTitle": "关注作者",
        "followDescription": "复杂世界和复杂人性的同行翻译者",
        "socialChannels": [
            {
                "id": "wechat",
                "label": "微信公众号",
                "qrImage": "/social/wechat-official-qrcode.png",
                "fallbackText": "微信里搜索“林子-心智进化之路”即可关注。",
            },
            {
                "id": "xiaohongshu",
                "label": "小红书",
                "qrImage": "/social/xiaohongshu-qrcode.png",
                "fallbackText": "小红书搜索“林子-心智进化之路”即可关注。",
            },
        ],
        "journeyOverline": "Journey Map",
        "journeyTitle": "章节升级打怪地图",
        "journeyDescription": "从总纲入口到八章推进，把这本书做成一条持续升级的闯关路径。每一关都能直接点进去，缩略图对应你这套《领导者的意识进化》小红书图。",
        "journeyEntryLabel": "从总纲进入",
        "journeyMap": journey_map,
        "stats": [
            {"label": "主题页", "value": str(len(topic_specs) + len(theme_specs))},
            {"label": "章节", "value": str(len(chapter_ids))},
            {"label": "概念 / 方法", "value": str(len(concept_ids) + len(method_ids))},
            {"label": "场景", "value": str(len(scenario_ids))},
        ],
    }

    site["stats"][0]["value"] = str(sum(1 for spec in public_specs if spec.type == "topic"))

    node_data = [
        {"id": spec.id, "type": spec.type, "tagline": shorten(spec.tagline or spec.id)}
        for spec in public_specs
    ]

    GRAPH_DATA_PATH.write_text(
        build_graph_module(
            site=site,
            filters=filters,
            toc=toc,
            home_sections=home_sections,
            file_map=file_map,
            node_images=node_images,
            nodes=node_data,
            links=edges,
            link_labels=link_labels,
        ),
        encoding="utf-8",
    )

    print(f"Generated {len(public_specs)} public nodes and {len(edges)} links.")
    print(f"Vault: {VAULT_DIR}")
    print(f"Graph data: {GRAPH_DATA_PATH}")


if __name__ == "__main__":
    main()
