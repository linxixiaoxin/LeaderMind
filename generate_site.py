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

VAULT_DIR = PROJECT_ROOT / "vault"
WEB_VAULT_DIR = PROJECT_ROOT / "web" / "public" / "vault"
WEB_IMAGE_DIR = PROJECT_ROOT / "web" / "public" / "chapter-images"
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


@dataclass
class NodeSpec:
    id: str
    type: str
    tagline: str = ""
    aliases: list[str] = field(default_factory=list)
    source: Path | None = None
    body: str = ""


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
    for node_id in ["全书摘要", "全书论证链", "K卡N卡总表", "领导者的意识进化"]:
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
    logic_chain = structured["logic_chain"]
    core_concepts = structured["core_concepts"]
    scenarios = structured["canonical_scenarios"]

    ensure_clean_dir(VAULT_DIR)
    ensure_clean_dir(WEB_VAULT_DIR)
    for folder in sorted(set(CATEGORY_DIR.values())):
        (VAULT_DIR / folder).mkdir(parents=True, exist_ok=True)
        (WEB_VAULT_DIR / folder).mkdir(parents=True, exist_ok=True)

    concept_lookup = {item["name"]: item for item in core_concepts}

    theme_specs = [
        NodeSpec("领导者的意识进化", "topic", source=K_BOOK_DIR / "领导者的意识进化.md", aliases=["领导者的心智进化"]),
        NodeSpec("复杂世界中的领导者成长", "topic", source=K_THEME_DIR / "复杂世界中的领导者成长.md"),
        NodeSpec("领导力瓶颈不在技能，而在心智复杂度", "topic", source=K_THEME_DIR / "领导力瓶颈不在技能，而在心智复杂度.md"),
        NodeSpec("从结构判断到成长支持：如何找到成长边际", "topic", source=K_THEME_DIR / "从结构判断到成长支持：如何找到成长边际.md"),
        NodeSpec("为什么很多培训回到工作里人却没变", "topic", source=K_THEME_DIR / "为什么很多培训回到工作里人却没变.md"),
        NodeSpec("工作现场如何变成发展容器", "topic", source=K_THEME_DIR / "工作现场如何变成发展容器.md"),
    ]
    topic_specs = [
        NodeSpec("全书摘要", "topic", tagline=book["core_one_liner"], source=BOOK_ASSETS_DIR / "全书摘要.md", aliases=[f"《{book['title']}》全书摘要"]),
        NodeSpec("全书论证链", "topic", tagline="用 10 步把这本书从复杂世界的领导难题，推进到工作即成长场。"),
        NodeSpec("K卡N卡总表", "topic", tagline="把这本书最值得复用的 K 卡与 N 卡收成一张总路由表。", source=BOOK_ASSETS_DIR / "整本书K卡_N卡总表.md", aliases=["整本书K卡_N卡总表", "整本书K卡/N卡总表"]),
        NodeSpec("内容选题角度", "topic", tagline="把全书拆成适合做内容、课程和表达的高价值切口。", source=BOOK_ASSETS_DIR / "选题角度.md", aliases=[f"《{book['title']}》选题角度"]),
        NodeSpec("视觉表达钩子", "topic", tagline="把抽象心智结构翻成更适合图解与页面表达的视觉对象。", source=BOOK_ASSETS_DIR / "视觉钩子.md", aliases=[f"《{book['title']}》视觉钩子"]),
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
        NodeSpec("主体 - 客体转换", "concept", aliases=["主体客体转换"], tagline=concept_lookup["主体 - 客体转换"]["solves_what"]),
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
            "node": "全书摘要",
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
        chapter_ids[1]: {"规范主导", "自主导向", "内观自变"},
        chapter_ids[2]: {"结构与内容", "成长边际", "边际提问"},
        chapter_ids[3]: {"发展型教练", "扩展式成长教练"},
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

    def process_source(spec: NodeSpec) -> str:
        markdown = read_text(spec.source)
        body = strip_first_heading(markdown)
        body = rewrite_markdown_links(body, stem_to_node, name_to_node)
        if spec.id == "全书摘要":
            body = "\n\n".join(
                [
                    body,
                    section(
                        "继续展开",
                        bullet_list(
                            [
                                "[[全书论证链]]",
                                "[[领导者的意识进化]]",
                                f"[[{chapter_ids[0]}]]",
                                f"[[{chapter_ids[-1]}]]",
                            ]
                        ),
                    ),
                ]
            )
        elif spec.id == "K卡N卡总表":
            body = "\n\n".join(
                [
                    body,
                    section(
                        "站内入口",
                        bullet_list([f"[[{name}]]" for name in theme_ids + concept_ids[:6] + method_ids]),
                    ),
                ]
            )
        elif spec.id == "内容选题角度":
            body = "\n\n".join(
                [
                    body,
                    section("适合接着点开的主题", bullet_list([f"[[{name}]]" for name in theme_ids])),
                ]
            )
        elif spec.id == "视觉表达钩子":
            body = "\n\n".join(
                [
                    body,
                    section("适合对照阅读的章节", bullet_list([f"[[{name}]]" for name in chapter_ids])),
                ]
            )
        elif spec.type == "chapter":
            chapter_index = chapter_ids.index(spec.id)
            chapter = chapter_map[chapter_index]
            related_concepts = [name_to_node.get(name, name) for name in chapter["core_concepts"] if name_to_node.get(name, name) in spec_by_id]
            related_methods = scenario_to_method_ids(chapter["title"] + chapter["key_question"], chapter["core_concepts"])
            extra_items = [f"[[{item}]]" for item in related_concepts + related_methods if item in spec_by_id]
            if chapter_index > 0:
                extra_items.append(f"[[{chapter_ids[chapter_index - 1]}]]")
            if chapter_index < len(chapter_ids) - 1:
                extra_items.append(f"[[{chapter_ids[chapter_index + 1]}]]")
            body = "\n\n".join([body, section("站内快链", bullet_list(extra_items))])
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

    raw_bodies["全书论证链"] = "\n\n".join(
        [
            "# 全书论证链",
            f"> 用 {len(logic_chain)} 步把这本书从“复杂世界里的领导失灵”推进到“工作即成长场”。",
            section("主问题链", numbered_list([link_text(item, spec_by_id["全书论证链"]) for item in logic_chain])),
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
            section("建议从哪里读起", bullet_list(["[[全书摘要]]", "[[全书论证链]]", "[[领导者的意识进化]]", f"[[{chapter_ids[-1]}]]"])),
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
                        "[[全书摘要]]：先拿到她到底在回答什么大问题。",
                        "[[全书论证链]]：再看她如何把理论一步步推进到工作现场。",
                        "[[领导者的意识进化]]：把整本书收成一套可反复调用的判断路径。",
                        f"[[{chapter_ids[-1]}]]：如果你更关心组织落地，可以直接从最后一章进入。",
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
                        "[[全书摘要]]",
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
                        "[[全书摘要]]：先拿整本书的主问题、三部分推进和最后落点。",
                        "[[全书论证链]]：适合一口气看清逻辑推进。",
                        "[[K卡N卡总表]]：直接看这本书最值得复用的 K / N 骨架。",
                        "[[内容选题角度]]：适合继续拆成内容、项目或课程。",
                        "[[视觉表达钩子]]：适合继续做图解和页面。",
                    ]
                ),
            ),
            section(
                "关注作者",
                bullet_list(
                    [
                        "微信公众号：林子-心智进化之路",
                        "小红书：林子-心智进化之路",
                        "小红书号：249152808",
                    ]
                ),
            ),
            section(
                "站内模块",
                bullet_list(
                    [
                        "主题：全书入口 + 书 K 卡 + 主题 K 卡。",
                        "章节：八章推进，直接按书的逻辑走。",
                        "概念：把成人发展、结构判断和工作即成长场串起来。",
                        "方法：把边际提问、发展型教练、反馈后学习、发展型会议直接落到动作上。",
                        "场景：从培训无效、反馈失灵、会议空转这些高频问题切入。",
                    ]
                ),
            ),
        ]
    )

    note_texts: dict[str, str] = {}

    for spec in specs:
        body = raw_bodies[spec.id]
        note_texts[spec.id] = "\n\n".join(
            [
                frontmatter([NODE_TYPE_META[spec.type]["label"]], NODE_TYPE_META[spec.type]["label"], spec.aliases),
                body,
            ]
        )

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

    node_images = copy_chapter_images(chapter_ids)

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

    for source_id, content in note_texts.items():
        for match in re.findall(r"\[\[([^\]]+)\]\]", content):
            target = name_to_node.get(match)
            if not target:
                continue
            add_edge(source_id, target, f"{NODE_TYPE_META[spec_by_id[source_id].type]['label']}关联")

    add_edge(book["author"], "领导者的意识进化", "作者与书卡")
    add_edge("全书摘要", "全书论证链", "从总览到主线")
    for current, next_chapter in zip(chapter_ids, chapter_ids[1:]):
        add_edge(current, next_chapter, "章节推进")

    toc = [
        {
            "id": "topics",
            "label": "主题入口",
            "color": NODE_TYPE_META["topic"]["color"],
            "sections": [
                {"label": "全书入口", "items": ["全书摘要", "全书论证链", "K卡N卡总表", "内容选题角度", "视觉表达钩子"]},
                {"label": "主题 K 卡", "items": theme_ids},
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
            "sections": [{"label": "N 概念卡", "items": concept_ids}],
        },
        {
            "id": "methods",
            "label": "动作方法",
            "color": NODE_TYPE_META["method"]["color"],
            "sections": [{"label": "N 方法卡", "items": method_ids}],
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
            "desc": "先看清主问题链、K/N 总表和内容化入口，再决定从哪一层往下钻。",
            "color": NODE_TYPE_META["topic"]["color"],
            "nodes": ["全书摘要", "全书论证链", "K卡N卡总表", "内容选题角度", "视觉表达钩子"],
        },
        {
            "id": "themes",
            "title": "主题 K 卡",
            "subtitle": "把书变成判断路径",
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
            "title": "N 概念卡",
            "subtitle": "把底层概念拿稳",
            "desc": "成人发展、成长边际、转化性学习、工作即成长场，是这本书最值得留下的底层抓手。",
            "color": NODE_TYPE_META["concept"]["color"],
            "nodes": concept_ids,
        },
        {
            "id": "methods",
            "title": "N 方法卡",
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

    filters = [
        {"type": node_type, "label": meta["label"], "color": meta["color"]}
        for node_type, meta in NODE_TYPE_META.items()
    ]

    site = {
        "title": book["title"],
        "shortTitle": "心智进化",
        "subtitle": "成人发展、领导力成长与工作即成长场",
        "description": "基于《领导者的意识进化》整理的单书知识站，把全书入口、K 卡、N 卡、章节地图和现实场景串成可点击的阅读地图。",
        "heroOverline": "LEADERSHIP · DEVELOPMENT · COMPLEXITY",
        "heroTitleLines": [book["title"], "把复杂世界中的领导成长做成可点击地图"],
        "creatorLabel": "整理与输出",
        "creatorName": "林子-心智进化之路",
        "footerNote": "公众号 / 小红书同名，欢迎关注",
        "assetVersion": BUILD_VERSION,
        "searchPlaceholder": "搜索主题、章节、概念、方法、场景…",
        "recommendedPath": ["全书摘要", "领导者的意识进化", chapter_ids[0], "成长边际", chapter_ids[-1]],
        "quickLinks": ["全书论证链", "K卡N卡总表", "领导力瓶颈不在技能，而在心智复杂度", "工作即成长场", "发展型教练", "发展型会议"],
        "followTitle": "关注作者",
        "followDescription": "这个站点背后的内容主理人是 林子-心智进化之路。公众号和小红书同名，小红书号也一并放在首页，方便你直接搜索、复制和关注。",
        "socialChannels": [
            {
                "id": "wechat",
                "label": "微信公众号",
                "name": "林子-心智进化之路",
                "description": "微信里直接搜索同名公众号即可找到我，适合长期关注系统化内容。",
                "copyNameLabel": "复制公众号名",
                "copyNameValue": "林子-心智进化之路",
                "qrImage": "/social/wechat-official-qrcode.png",
                "fallbackText": "微信里搜索“林子-心智进化之路”即可关注。",
            },
            {
                "id": "xiaohongshu",
                "label": "小红书",
                "name": "林子-心智进化之路",
                "accountId": "249152808",
                "description": "小红书可直接搜同名账号，或者用账号号更快定位到我。",
                "copyNameLabel": "复制小红书名",
                "copyNameValue": "林子-心智进化之路",
                "copyIdLabel": "复制小红书号",
                "copyIdValue": "249152808",
                "qrImage": "/social/xiaohongshu-qrcode.png",
                "fallbackText": "小红书搜索“林子-心智进化之路”或账号号 249152808。",
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
            {"label": "N 卡", "value": str(len(concept_ids) + len(method_ids))},
            {"label": "场景", "value": str(len(scenario_ids))},
        ],
    }

    node_data = [
        {"id": spec.id, "type": spec.type, "tagline": shorten(spec.tagline or spec.id)}
        for spec in specs
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

    print(f"Generated {len(specs)} nodes and {len(edges)} links.")
    print(f"Vault: {VAULT_DIR}")
    print(f"Graph data: {GRAPH_DATA_PATH}")


if __name__ == "__main__":
    main()
