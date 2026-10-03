import json
import os
import re
import sys
import urllib.request
from pathlib import Path

COLOR_MAP = {
    "hl-yellow": "yellow_background",
    "hl-blue": "blue_background",
    "hl-green": "green_background",
    "hl-red": "red_background",
}

def parse_inline(text):
    bt = chr(96)
    parts = []
    pos = 0
    active_color = None
    while pos < len(text):
        m_mark_open = re.search(r'<mark class=["'](hl-[a-z]+)["']>', text[pos:])
        m_mark_close = re.search(r"</mark>", text[pos:])
        m_code = re.search(rf"{bt}(.+?){bt}|<code>(.+?)</code>", text[pos:])
        m_bold = re.search(r"\*\*(.+?)\*\*", text[pos:])
        m_link = re.search(r"\[([^\]]+)\]\(([^)]+)\)", text[pos:])

        matches = []
        if m_mark_open: matches.append((m_mark_open.start(), "mark_open", m_mark_open))
        if m_mark_close: matches.append((m_mark_close.start(), "mark_close", m_mark_close))
        if m_code: matches.append((m_code.start(), "code", m_code))
        if m_bold: matches.append((m_bold.start(), "bold", m_bold))
        if m_link: matches.append((m_link.start(), "link", m_link))

        if not matches:
            rem = text[pos:]
            if rem: parts.append({"text": rem, "bold": False, "code": False, "color": active_color, "link": None})
            break

        matches.sort(key=lambda x: x[0])
        earliest_start, m_type, m_obj = matches[0]
        abs_start = pos + earliest_start
        abs_end = pos + m_obj.end()

        if abs_start > pos:
            parts.append({"text": text[pos:abs_start], "bold": False, "code": False, "color": active_color, "link": None})

        if m_type == "mark_open":
            active_color = COLOR_MAP.get(m_obj.group(1), "yellow_background")
        elif m_type == "mark_close":
            active_color = None
        elif m_type == "code":
            c_txt = m_obj.group(1) or m_obj.group(2)
            parts.append({"text": c_txt, "bold": False, "code": True, "color": active_color, "link": None})
        elif m_type == "bold":
            b_txt = m_obj.group(1)
            sub_m = re.search(r'<mark class=["'](hl-[a-z]+)["']>(.+?)</mark>', b_txt)
            if sub_m:
                col = COLOR_MAP.get(sub_m.group(1), "yellow_background")
                parts.append({"text": sub_m.group(2), "bold": True, "code": False, "color": col, "link": None})
            else:
                parts.append({"text": b_txt, "bold": True, "code": False, "color": active_color, "link": None})
        elif m_type == "link":
            l_txt = m_obj.group(1)
            l_url = m_obj.group(2)
            parts.append({"text": l_txt, "bold": False, "code": False, "color": active_color, "link": l_url})
        pos = abs_end

    rich_text = []
    for p in parts:
        txt = p["text"]
        if not txt: continue
        chunks = [txt[k:k+1900] for k in range(0, len(txt), 1900)] or [""]
        for c in chunks:
            item = {
                "type": "text",
                "text": {"content": c},
                "annotations": {
                    "bold": p["bold"],
                    "italic": False,
                    "strikethrough": False,
                    "underline": False,
                    "code": p["code"],
                    "color": p["color"] or "default",
                },
            }
            if p["link"]: item["text"]["link"] = {"url": p["link"]}
            rich_text.append(item)
    return rich_text or [{"type": "text", "text": {"content": ""}}]

def split_callout_emoji(text):
    if text:
        code = ord(text[0])
        if 0x2190 <= code <= 0x3299 or code >= 0x1F000:
            emoji = text[0]
            rest = text[1:]
            if rest.startswith("\ufe0f"):
                emoji += "\ufe0f"
                rest = rest[1:]
            return emoji, rest.lstrip()
    return "💡", text

def md_to_notion_blocks(md_text):
    raw_lines = md_text.splitlines()
    top_blocks = []
    i = 0
    bullet_stack = []
    while i < len(raw_lines):
        line = raw_lines[i]
        stripped = line.strip()
        if not stripped: i += 1; continue
        indent = len(line) - len(line.lstrip())
        level = indent // 2
        if stripped == "---":
            bullet_stack.clear()
            top_blocks.append({"object": "block", "type": "divider", "divider": {}})
            i += 1; continue
        if stripped.startswith("# "):
            bullet_stack.clear()
            top_blocks.append({"object": "block", "type": "heading_1", "heading_1": {"rich_text": parse_inline(stripped[2:])}})
            i += 1; continue
        if stripped.startswith("## "):
            bullet_stack.clear()
            top_blocks.append({"object": "block", "type": "heading_2", "heading_2": {"rich_text": parse_inline(stripped[3:])}})
            i += 1; continue
        if stripped.startswith("### "):
            bullet_stack.clear()
            top_blocks.append({"object": "block", "type": "heading_3", "heading_3": {"rich_text": parse_inline(stripped[4:])}})
            i += 1; continue
        if stripped.startswith("!> "):
            bullet_stack.clear()
            callout_lines = []
            while i < len(raw_lines) and raw_lines[i].strip().startswith("!> "):
                callout_lines.append(raw_lines[i].strip()[3:].strip())
                i += 1
            while i < len(raw_lines):
                nxt = raw_lines[i].strip()
                if not nxt: break
                if nxt.startswith(("#", "---", "|", "-", "*", "!>", ">")): break
                callout_lines.append(nxt)
                i += 1
            full_txt = chr(10).join(callout_lines)
            emoji, text = split_callout_emoji(full_txt)
            color = "yellow_background" if ("⚠️" in emoji or "주의" in text) else "green_background"
            top_blocks.append({"object": "block", "type": "callout", "callout": {"icon": {"type": "emoji", "emoji": emoji}, "color": color, "rich_text": parse_inline(text)}})
            continue
        if stripped.startswith("> "):
            bullet_stack.clear()
            top_blocks.append({"object": "block", "type": "quote", "quote": {"rich_text": parse_inline(stripped[2:])}})
            i += 1; continue
        if stripped.startswith("|"):
            bullet_stack.clear()
            rows = []
            while i < len(raw_lines) and raw_lines[i].strip().startswith("|"):
                r = raw_lines[i].strip()
                if not all(c in "| -:" for c in r):
                    cells = [c.strip() for c in r.strip("|").split("|")]
                    rows.append(cells)
                i += 1
            if rows:
                width = max(len(r) for r in rows)
                tblock = {"object": "block", "type": "table", "table": {"table_width": width, "has_column_header": True, "has_row_header": False, "children": []}}
                for r in rows:
                    cells = r + [""] * (width - len(r))
                    tblock["table"]["children"].append({"object": "block", "type": "table_row", "table_row": {"cells": [parse_inline(c) for c in cells]}})
                top_blocks.append(tblock)
            continue
        if stripped.startswith("- [ ] ") or stripped.startswith("* [ ] "):
            bullet_stack.clear()
            top_blocks.append({"object": "block", "type": "to_do", "to_do": {"rich_text": parse_inline(stripped[6:]), "checked": False}})
            i += 1; continue
        if re.match(r"^[-*]\s+", stripped):
            content = re.sub(r"^[-*]\s+", "", stripped)
            b_node = {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": parse_inline(content)}, "children": []}
            while bullet_stack and bullet_stack[-1][0] >= level:
                bullet_stack.pop()
            if not bullet_stack:
                top_blocks.append(b_node)
            else:
                bullet_stack[-1][1]["children"].append(b_node)
            bullet_stack.append((level, b_node))
            i += 1; continue
        bullet_stack.clear()
        top_blocks.append({"object": "block", "type": "paragraph", "paragraph": {"rich_text": parse_inline(stripped)}})
        i += 1
    def clean_children(node):
        if "children" in node:
            if not node["children"]:
                del node["children"]
            else:
                for kid in node["children"]: clean_children(kid)
    for b in top_blocks: clean_children(b)
    return top_blocks

