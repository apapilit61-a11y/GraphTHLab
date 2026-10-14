"""Python implementations of the graph algorithms used by Graph Theory Lab."""

from __future__ import annotations

from collections import deque
from html import escape
import math
from typing import Any


_PALETTE = [
    "#ef7d57", "#41a6f6", "#a7f070", "#ffcd75", "#f4a6d7",
    "#73eff7", "#b13e53", "#38b764", "#c28a4a", "#94b0c2",
    "#5d275d", "#3b5dc9", "#257179", "#d4a5ff", "#566c86",
]


def _fmt(value: float | int) -> str:
    if math.isinf(value):
        return "∞"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return f"{value:g}"


def _name(names: dict[int, str], node_id: int) -> str:
    return names.get(node_id, f"v{node_id}")


def _html(value: Any) -> str:
    return escape(str(value), quote=True)


def _step(message: str, **state: dict[str, Any]) -> dict[str, Any]:
    return {
        "msg": message,
        "ntext": state.get("ntext"),
        "node": state.get("node", {}),
        "edge": state.get("edge", {}),
        "etext": state.get("etext"),
        "fill": state.get("fill"),
    }


def _card(label: str, value: Any) -> str:
    return f'<div class="card"><div class="k">{label}</div><div class="v">{value}</div></div>'


def _result(title: str, key: str, steps: list[dict[str, Any]], summary: str, **extra: Any) -> dict[str, Any]:
    return {"title": title, "key": key, "steps": steps, "summary": summary, **extra}


def _graph(payload: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[int, str], bool]:
    nodes = payload.get("nodes")
    edges = payload.get("edges")
    if not isinstance(nodes, list) or not isinstance(edges, list):
        raise ValueError("ข้อมูลกราฟไม่ถูกต้อง")
    node_ids: list[int] = []
    names: dict[int, str] = {}
    for node in nodes:
        if not isinstance(node, dict) or not isinstance(node.get("id"), int):
            raise ValueError("ข้อมูลจุดยอดไม่ถูกต้อง")
        node_id = node["id"]
        if node_id in names:
            raise ValueError("พบรหัสจุดยอดซ้ำ")
        node_ids.append(node_id)
        names[node_id] = str(node.get("label", f"v{node_id}"))
    valid_ids = set(node_ids)
    cleaned_edges: list[dict[str, Any]] = []
    for edge in edges:
        if not isinstance(edge, dict) or not isinstance(edge.get("id"), int):
            raise ValueError("ข้อมูลเส้นเชื่อมไม่ถูกต้อง")
        u, v, weight = edge.get("u"), edge.get("v"), edge.get("w")
        if not isinstance(u, int) or not isinstance(v, int) or u not in valid_ids or v not in valid_ids:
            raise ValueError("เส้นเชื่อมอ้างถึงจุดยอดที่ไม่มีอยู่")
        if isinstance(weight, bool) or not isinstance(weight, (int, float)) or not math.isfinite(weight):
            raise ValueError("น้ำหนักหรือความจุของเส้นเชื่อมไม่ถูกต้อง")
        cleaned_edges.append({"id": edge["id"], "u": u, "v": v, "w": weight})
    return nodes, cleaned_edges, names, bool(payload.get("directed"))


def _dijkstra(payload: dict[str, Any]) -> dict[str, Any]:
    nodes, edges, names, directed = _graph(payload)
    ids = [node["id"] for node in nodes]
    source, sink = payload.get("source"), payload.get("sink")
    if not ids:
        raise ValueError("ยังไม่มีจุดยอด")
    if source not in names:
        raise ValueError('กรุณาเลือก "ต้นทาง" ก่อนรัน Dijkstra')
    negative = [edge for edge in edges if edge["w"] < 0]
    if negative:
        edges_list = ", ".join(f'{_name(names, edge["u"])}–{_name(names, edge["v"])}' for edge in negative)
        raise ValueError(f"Dijkstra ใช้ไม่ได้กับน้ำหนักติดลบ: {edges_list}")

    adj: dict[int, list[tuple[int, float, int]]] = {node_id: [] for node_id in ids}
    for edge in edges:
        adj[edge["u"]].append((edge["v"], edge["w"], edge["id"]))
        if not directed:
            adj[edge["v"]].append((edge["u"], edge["w"], edge["id"]))
    distances = {node_id: math.inf for node_id in ids}
    previous: dict[int, int | None] = {node_id: None for node_id in ids}
    previous_edge: dict[int, int] = {}
    done: set[int] = set()
    steps: list[dict[str, Any]] = []
    relax_count = 0
    distances[source] = 0

    def state() -> dict[str, Any]:
        return {
            "ntext": {node_id: _fmt(distances[node_id]) for node_id in ids},
            "node": {node_id: "visited" for node_id in done},
            "edge": {edge_id: "soft" for edge_id in previous_edge.values()},
        }

    def snap(message: str, node: dict[int, str] | None = None, edge: dict[int, str] | None = None) -> None:
        current = state()
        if node:
            current["node"].update(node)
        if edge:
            current["edge"].update(edge)
        steps.append(_step(message, **current))

    snap(f"เริ่มต้น: d({_name(names, source)}) = 0 และจุดอื่นทั้งหมด = ∞", {source: "current"})
    while True:
        available = [node_id for node_id in ids if node_id not in done and distances[node_id] < math.inf]
        if not available:
            remaining = [node_id for node_id in ids if node_id not in done]
            if remaining:
                labels = ", ".join(names[node_id] for node_id in remaining)
                snap(f"จุดที่เหลือ ({labels}) เข้าไม่ถึงจากต้นทาง → ระยะ = ∞")
            break
        current = min(available, key=lambda node_id: distances[node_id])
        best_distance = distances[current]
        done.add(current)
        snap(f"เลือก {_name(names, current)} ซึ่งมีระยะน้อยที่สุด ({_fmt(best_distance)}) ในจุดที่ยังไม่ปิด → ปิดจุดนี้ (ระยะนี้คือคำตอบสุดท้ายแล้ว)", {current: "current"})
        for target, weight, edge_id in adj[current]:
            if target in done:
                continue
            relax_count += 1
            candidate = distances[current] + weight
            old = distances[target]
            if candidate < old:
                distances[target] = candidate
                previous[target] = current
                previous_edge[target] = edge_id
                message = f"Relax {_name(names, current)} → {_name(names, target)}: {_fmt(distances[current])} + {_fmt(weight)} = {_fmt(candidate)} < {_fmt(old)} ✔ อัปเดต d({_name(names, target)}) = {_fmt(candidate)}"
                snap(message, {current: "current", target: "consider"}, {edge_id: "consider"})
            else:
                message = f"Relax {_name(names, current)} → {_name(names, target)}: {_fmt(distances[current])} + {_fmt(weight)} = {_fmt(candidate)} ≥ {_fmt(old)} ✘ ไม่เปลี่ยน"
                snap(message, {current: "current", target: "consider"}, {edge_id: "reject"})

    def path_to(target: int) -> list[int] | None:
        if math.isinf(distances[target]):
            return None
        path: list[int] = []
        current: int | None = target
        while current is not None:
            path.append(current)
            current = previous[current]
        return list(reversed(path))

    has_sink = sink in names
    path = path_to(sink) if has_sink else None
    path_edges: list[int] = []
    if path:
        current = sink
        while previous[current] is not None:
            path_edges.append(previous_edge[current])
            current = previous[current]
        snap(
            f"✔ เสร็จสิ้น! เส้นทางสั้นที่สุด: {' → '.join(_name(names, node_id) for node_id in path)} | ระยะรวม = {_fmt(distances[sink])}",
            {node_id: "path" for node_id in path},
            {edge_id: "path" for edge_id in path_edges},
        )
    elif has_sink:
        snap(f"✘ เสร็จสิ้น: ไม่มีเส้นทางจาก {_name(names, source)} ไป {_name(names, sink)} (ระยะ = ∞)")
    else:
        snap("✔ เสร็จสิ้น! ตัวเลขเหนือจุด = ระยะทางสั้นที่สุดจากต้นทาง (เลือก \"ปลายทาง\" เพื่อดูเส้นทาง)")

    summary = ""
    if has_sink:
        if path:
            route = " → ".join(f'<span class="chip">{_html(_name(names, node_id))}</span>' for node_id in path)
            summary += f'<div class="hero">🚚 ระยะทางสั้นที่สุดจาก <b>{_html(_name(names, source))}</b> ไป <b>{_html(_name(names, sink))}</b> = <span class="bignum">{_fmt(distances[sink])}</span><div class="route">{route}</div></div>'
        else:
            summary += f'<div class="hero bad">✘ ไปไม่ถึง {_html(_name(names, sink))} จาก {_html(_name(names, source))} (ระยะ = ∞)</div>'
    reachable = sum(not math.isinf(distances[node_id]) for node_id in ids)
    summary += '<div class="cards">' + _card("ต้นทาง", _html(_name(names, source))) + _card("ไปถึงได้", f"{reachable} / {len(nodes)} จุด") + _card("จำนวนครั้ง Relax", relax_count) + _card("จำนวนขั้นตอน", len(steps)) + "</div>"
    summary += '<h3>ระยะทางจากต้นทางไปทุกจุด</h3><div class="tw"><table class="tbl"><tr><th>จุดยอด</th><th>ระยะ</th><th>เส้นทาง</th></tr>'
    for node in sorted(nodes, key=lambda n: (distances[n["id"]], n["id"])):
        target = node["id"]
        path = path_to(target)
        route = " → ".join(_html(_name(names, path_id)) for path_id in path) if path else "เข้าไม่ถึง"
        summary += f'<tr><td class="l">{_html(names[target])}</td><td><b>{_fmt(distances[target])}</b></td><td class="l">{route}</td></tr>'
    summary += "</table></div><div class=\"note\">ใช้หาเส้นทางขนส่งที่สั้นที่สุดหรือถูกที่สุดจากคลังสินค้าไปยังร้านค้า/ลูกค้า ถ้าน้ำหนักคือ \"ค่าขนส่ง\" ผลลัพธ์จะเป็นเส้นทางที่ประหยัดที่สุด</div>"
    return _result("📊 สรุปผล Dijkstra — เส้นทางสั้นที่สุด", "dijkstra", steps, summary)


def _prim(payload: dict[str, Any]) -> dict[str, Any]:
    nodes, edges, names, directed = _graph(payload)
    if directed:
        raise ValueError("Prim ใช้ได้เฉพาะกราฟไม่มีทิศทาง")
    ids = [node["id"] for node in nodes]
    if not ids:
        raise ValueError("ยังไม่มีจุดยอด")
    source = payload.get("source")
    start = source if source in names else ids[0]
    in_tree: set[int] = set()
    selected: list[tuple[dict[str, Any], int, float]] = []
    roots: list[int] = []
    total: float = 0
    steps: list[dict[str, Any]] = []

    def base() -> dict[str, dict[int, str]]:
        return {
            "node": {node_id: "visited" for node_id in in_tree},
            "edge": {edge["id"]: "tree" for edge, _, _ in selected},
        }

    def snap(message: str, node: dict[int, str] | None = None, edge: dict[int, str] | None = None) -> None:
        current = base()
        if node:
            current["node"].update(node)
        if edge:
            current["edge"].update(edge)
        steps.append(_step(message, **current))

    order = [start, *(node_id for node_id in ids if node_id != start)]
    for root in order:
        if root in in_tree:
            continue
        tree_number = len(roots) + 1
        roots.append(root)
        in_tree.add(root)
        message = f"เริ่มต้นที่ {_name(names, root)} — ต้นไม้มี 1 จุด น้ำหนักรวม = 0" if tree_number == 1 else f"ไม่มีเส้นไปยังจุดที่เหลือแล้ว (กราฟไม่ Connected) → เริ่มต้นไม้ต้นที่ {tree_number} ที่ {_name(names, root)}"
        snap(message, {root: "current"})
        while True:
            candidates = [edge for edge in edges if edge["u"] != edge["v"] and ((edge["u"] in in_tree) != (edge["v"] in in_tree))]
            if not candidates:
                break
            best = min(candidates, key=lambda edge: edge["w"])
            edge_state = {edge["id"]: "consider" for edge in candidates}
            candidate_list = ", ".join(f'{_name(names, e["u"])}–{_name(names, e["v"])} ({_fmt(e["w"])})' for e in sorted(candidates, key=lambda e: e["w"])[:6])
            if len(candidates) > 6:
                candidate_list += ", ..."
            snap(f"ตัวเลือก {len(candidates)} เส้นที่เชื่อมต้นไม้กับจุดใหม่: {candidate_list}", edge=edge_state)
            new_node = best["v"] if best["u"] in in_tree else best["u"]
            in_tree.add(new_node)
            total += best["w"]
            selected.append((best, tree_number, total))
            snap(f"✔ เลือกเส้นต้นทุนต่ำสุด {_name(names, best['u'])}–{_name(names, best['v'])} = {_fmt(best['w'])} → เพิ่ม {_name(names, new_node)} | น้ำหนักรวม = {_fmt(total)}", {new_node: "current"}, {best["id"]: "path"})

    tree_count = len(roots)
    snap(f"✔ เสร็จสิ้น! Minimum Spanning Tree มี {len(selected)} เส้น น้ำหนักรวม = {_fmt(total)}" if tree_count == 1 else f"✔ เสร็จสิ้น! ได้ Spanning Forest {tree_count} ต้น ({len(selected)} เส้น) น้ำหนักรวม = {_fmt(total)}")
    label = "Minimum Spanning Tree" if tree_count == 1 else f"Spanning Forest ({tree_count} ต้น)"
    summary = f'<div class="hero {"warn" if tree_count > 1 else ""}">🌳 {label} น้ำหนักรวมต่ำสุด = <span class="bignum">{_fmt(total)}</span></div>'
    summary += '<div class="cards">' + _card("จุดเริ่ม", _html(_name(names, start))) + _card("จำนวนเส้นที่ใช้", f"{len(selected)} = |V| − {tree_count}") + _card("จำนวนต้นไม้", tree_count) + _card("เส้นที่ไม่ใช้", len(edges) - len(selected)) + "</div>"
    if tree_count > 1:
        roots_html = " ".join(f'<span class="chip">{_html(_name(names, root))}</span>' for root in roots)
        summary += f"<p>⚠ กราฟไม่ Connected จึงได้ป่า (Forest) — เริ่มแต่ละต้นที่: {roots_html}</p>"
    summary += '<h3>ลำดับเส้นที่เลือก</h3><div class="tw"><table class="tbl"><tr><th>#</th><th>ต้นที่</th><th>เส้น</th><th>น้ำหนัก</th><th>รวมสะสม</th></tr>'
    for index, (edge, tree_number, cumulative) in enumerate(selected, 1):
        summary += f'<tr><td>{index}</td><td>{tree_number}</td><td class="l">{_html(_name(names, edge["u"]))} – {_html(_name(names, edge["v"]))}</td><td>{_fmt(edge["w"])}</td><td><b>{_fmt(cumulative)}</b></td></tr>'
    summary += "</table></div><div class=\"note\">วางโครงข่ายถนน ท่อประปา หรือสายไฟให้ทุกจุดเชื่อมถึงกัน โดยใช้งบประมาณรวมน้อยที่สุด</div>"
    return _result("📊 สรุปผล Prim — Minimum Spanning Tree", "prim", steps, summary)


def _coloring(payload: dict[str, Any]) -> dict[str, Any]:
    nodes, edges, names, directed = _graph(payload)
    if directed:
        raise ValueError("Coloring ใช้ได้เฉพาะกราฟไม่มีทิศทาง")
    ids = [node["id"] for node in nodes]
    if not ids:
        raise ValueError("ยังไม่มีจุดยอด")
    neighbors: dict[int, set[int]] = {node_id: set() for node_id in ids}
    for edge in edges:
        if edge["u"] != edge["v"]:
            neighbors[edge["u"]].add(edge["v"])
            neighbors[edge["v"]].add(edge["u"])
    order = sorted(ids, key=lambda node_id: (-len(neighbors[node_id]), node_id))
    colors: dict[int, int] = {}
    color_names = payload.get("colorNames", [])
    def color_name(color: int) -> str:
        return color_names[color] if color < len(color_names) and color_names[color] else f"สี {color + 1}"

    def color_token(color: int) -> str:
        return f"{{{{COLOR_NAME_{color}}}}}"

    steps: list[dict[str, Any]] = []
    def snap(message: str, node: dict[int, str] | None = None, edge: dict[int, str] | None = None) -> None:
        steps.append(_step(message, fill=dict(colors), node=node or {}, edge=edge or {}))

    order_text = ", ".join(f"{_name(names, node_id)}({len(neighbors[node_id])})" for node_id in order)
    snap(f"Welsh–Powell: เรียงจุดตาม Degree มาก→น้อย: {order_text}")
    color = 0
    while len(colors) < len(order):
        snap(f'🎨 เริ่มใช้สีที่ {color + 1} "{color_name(color)}" — ไล่ตามลำดับ ใส่สีให้จุดที่ไม่ติดกับจุดสีนี้')
        for node_id in order:
            if node_id in colors:
                continue
            conflict = next((neighbor for neighbor in neighbors[node_id] if colors.get(neighbor) == color), None)
            if conflict is None:
                colors[node_id] = color
                snap(f'{_name(names, node_id)} ไม่ติดกับจุดที่ใช้ "{color_name(color)}" → ระบายสีนี้', {node_id: "current"})
            else:
                crossing = next((edge for edge in edges if (edge["u"] == node_id and edge["v"] == conflict) or (edge["v"] == node_id and edge["u"] == conflict)), None)
                snap(f'{_name(names, node_id)} ติดกับ {_name(names, conflict)} ที่ใช้ "{color_name(color)}" แล้ว → ข้ามไปก่อน', {node_id: "current"}, {crossing["id"]: "consider"} if crossing else {})
        color += 1
    color_count = color
    delta = max((len(neighbors[node_id]) for node_id in ids), default=0)

    exact: tuple[int, dict[int, int]] | None = None
    if len(ids) <= 15:
        exact_order = sorted(ids, key=lambda node_id: -len(neighbors[node_id]))
        exact_colors: dict[int, int] = {}
        def backtrack(index: int, limit: int, used: int) -> bool:
            if index == len(exact_order):
                return True
            node_id = exact_order[index]
            for candidate_color in range(min(limit, used + 1)):
                if all(exact_colors.get(neighbor) != candidate_color for neighbor in neighbors[node_id]):
                    exact_colors[node_id] = candidate_color
                    if backtrack(index + 1, limit, max(used, candidate_color + 1)):
                        return True
                    del exact_colors[node_id]
            return False
        for limit in range(1, len(ids) + 1):
            exact_colors.clear()
            if backtrack(0, limit, 0):
                exact = (limit, dict(exact_colors))
                break
    done_message = f"✔ เสร็จสิ้น! Greedy ใช้ {color_count} สี (ขอบเขตบน Δ+1 = {delta + 1})" + (f" | Chromatic Number χ(G) = {exact[0]}" if exact else "")
    snap(done_message)

    summary = f'<div class="hero">🎨 Welsh–Powell ใช้ <span class="bignum">{color_count}</span> สี' + (f' • ค่าที่ดีที่สุดจริง χ(G) = <b>{exact[0]}</b>' if exact else "") + "</div>"
    exact_value = str(exact[0]) if exact else "คำนวณเมื่อ |V| ≤ 15"
    summary += '<div class="cards">' + _card("Greedy (Welsh–Powell)", f"{color_count} สี") + _card("Δ (Degree สูงสุด)", delta) + _card("ขอบเขตบน Δ+1", delta + 1) + _card("χ(G) แบบ Exact", exact_value) + "</div>"
    if exact:
        summary += f"<p>⚠ Greedy ใช้สีมากกว่าค่าที่ดีที่สุด {color_count - exact[0]} สี (Greedy ไม่รับประกันว่าน้อยที่สุดเสมอ)</p>" if exact[0] < color_count else "<p>✔ Greedy ได้จำนวนสีเท่ากับค่าที่ดีที่สุด</p>"
    summary += '<h3>กลุ่มของแต่ละสี (กดตั้งชื่อความหมายได้)</h3>'
    for color in range(color_count):
        members = [node for node in nodes if colors[node["id"]] == color]
        chips = "".join(f'<span class="chip">{_html(node["label"])}</span>' for node in members)
        swatch = _PALETTE[color % len(_PALETTE)]
        summary += f'<div class="grp"><div class="gh"><span><span class="sw" style="background:{swatch}"></span>{color_token(color)} <small>({len(members)} จุด)</small></span><button type="button" class="btn mini" data-cname="{color}">✏️ ตั้งชื่อ</button></div>{chips}</div>'
    summary += '<h3>ลำดับ Welsh–Powell</h3><div class="tw"><table class="tbl"><tr><th>#</th><th>จุด</th><th>deg</th><th>สี</th></tr>'
    for index, node_id in enumerate(order, 1):
        summary += f'<tr><td>{index}</td><td class="l">{_html(_name(names, node_id))}</td><td>{len(neighbors[node_id])}</td><td class="l"><span class="sw" style="background:{_PALETTE[colors[node_id] % len(_PALETTE)]}"></span>{color_token(colors[node_id])}</td></tr>'
    summary += "</table></div><div class=\"note\">จุดที่เชื่อมกัน = ขัดแย้งกัน (เช่น วิชาที่มีนักเรียนสอบซ้อน หรือสินค้าที่ห้ามเก็บรวมกัน) จึงต้องได้สีต่างกัน แต่ละสีจึงหมายถึงช่วงเวลาสอบหรือช่องจัดเก็บ 1 ช่อง จำนวนสีจึงเท่ากับจำนวนช่วงเวลาหรือช่องที่ต้องใช้</div>"
    return _result("📊 สรุปผล Graph Coloring", "color", steps, summary, colors=colors)


def _flow(payload: dict[str, Any]) -> dict[str, Any]:
    nodes, edges, names, directed = _graph(payload)
    if not directed:
        raise ValueError("Max Flow ใช้ได้เฉพาะกราฟมีทิศทาง")
    ids = [node["id"] for node in nodes]
    source, sink = payload.get("source"), payload.get("sink")
    if source not in names or sink not in names:
        raise ValueError("กรุณาเลือก Source และ Sink ก่อนรัน Max Flow")
    if source == sink:
        raise ValueError("Source และ Sink ต้องเป็นคนละจุด")
    if any(edge["w"] < 0 for edge in edges):
        raise ValueError("ความจุของเส้นเชื่อมต้องไม่ติดลบ")

    graph: dict[int, list[dict[str, Any]]] = {node_id: [] for node_id in ids}
    original_arcs: list[dict[str, Any]] = []
    def add_arc(u: int, v: int, capacity: float, edge_id: int, sign: int) -> None:
        forward: dict[str, Any] = {"to": v, "cap": capacity, "flow": 0, "eid": edge_id, "sign": sign}
        backward: dict[str, Any] = {"to": u, "cap": 0, "flow": 0, "eid": None, "sign": 0}
        forward["rev"] = backward
        backward["rev"] = forward
        graph[u].append(forward)
        graph[v].append(backward)
        original_arcs.append(forward)

    for edge in edges:
        if edge["u"] == edge["v"]:
            continue
        add_arc(edge["u"], edge["v"], edge["w"], edge["id"], 1)
        if not directed:
            add_arc(edge["v"], edge["u"], edge["w"], edge["id"], -1)

    def flow_of() -> dict[int, float]:
        flow = {edge["id"]: 0 for edge in edges}
        for arc in original_arcs:
            flow[arc["eid"]] += arc["sign"] * arc["flow"]
        return flow

    steps: list[dict[str, Any]] = []
    augmentations: list[tuple[list[int], float, bool]] = []
    total: float = 0

    def base() -> dict[str, Any]:
        flows = flow_of()
        edge_text: dict[int, str] = {}
        edge_state: dict[int, str] = {}
        for edge in edges:
            value = abs(flows[edge["id"]])
            edge_text[edge["id"]] = f"{_fmt(value)}/{_fmt(edge['w'])}"
            if value > 1e-9:
                edge_state[edge["id"]] = "sat" if value >= edge["w"] - 1e-9 else "flow"
        return {"etext": edge_text, "edge": edge_state}

    def snap(message: str, node: dict[int, str] | None = None, edge: dict[int, str] | None = None) -> None:
        current = base()
        if node:
            current["node"] = node
        if edge:
            current["edge"].update(edge)
        steps.append(_step(message, **current))

    snap(f"เริ่มต้น: Flow ทุกเส้น = 0 (แสดงเป็น flow/capacity) | Source = {_name(names, source)}, Sink = {_name(names, sink)}", {source: "current", sink: "current"})
    for iteration in range(1, 10001):
        parent: dict[int, tuple[int, dict[str, Any]] | None] = {source: None}
        queue = deque([source])
        while queue and sink not in parent:
            current = queue.popleft()
            for arc in graph[current]:
                if arc["cap"] - arc["flow"] > 1e-9 and arc["to"] not in parent:
                    parent[arc["to"]] = (current, arc)
                    queue.append(arc["to"])
        if sink not in parent:
            break
        path_arcs: list[dict[str, Any]] = []
        path_nodes = [sink]
        current = sink
        bottleneck = math.inf
        while current != source:
            parent_item = parent[current]
            assert parent_item is not None
            previous, arc = parent_item
            path_arcs.append(arc)
            bottleneck = min(bottleneck, arc["cap"] - arc["flow"])
            current = previous
            path_nodes.append(current)
        path_arcs.reverse()
        path_nodes.reverse()
        edge_state = {arc["eid"] if arc["eid"] is not None else arc["rev"]["eid"]: "consider" for arc in path_arcs}
        node_state = {node_id: "consider" for node_id in path_nodes}
        uses_reverse = any(arc["eid"] is None for arc in path_arcs)
        path_text = " → ".join(_name(names, node_id) for node_id in path_nodes)
        snap(f"รอบ {iteration}: BFS พบ Augmenting Path {path_text} | คอขวดของเส้นทาง = {_fmt(bottleneck)}" + (" (มีการดันกระแสย้อนกลับผ่าน residual edge)" if uses_reverse else ""), node_state, edge_state)
        for arc in path_arcs:
            arc["flow"] += bottleneck
            arc["rev"]["flow"] -= bottleneck
        total += bottleneck
        augmentations.append((path_nodes, bottleneck, uses_reverse))
        snap(f"เพิ่ม Flow +{_fmt(bottleneck)} ตามเส้นทางนี้ → Flow รวม = {_fmt(total)}", node_state, {edge_id: "path" for edge_id in edge_state})

    reachable = {source}
    queue = deque([source])
    while queue:
        current = queue.popleft()
        for arc in graph[current]:
            if arc["cap"] - arc["flow"] > 1e-9 and arc["to"] not in reachable:
                reachable.add(arc["to"])
                queue.append(arc["to"])
    cut = [edge for edge in edges if (edge["u"] in reachable and edge["v"] not in reachable) or (not directed and edge["v"] in reachable and edge["u"] not in reachable)]
    cut_capacity = sum(edge["w"] for edge in cut)
    snap(f"ไม่พบ Augmenting Path อีกแล้ว → Max Flow = {_fmt(total)}")
    cut_names = ", ".join(f'{_name(names, edge["u"])}–{_name(names, edge["v"])}' for edge in cut) or "-"
    reachable_names = ", ".join(_name(names, node_id) for node_id in reachable)
    snap(f"✔ Min Cut: ฝั่ง S = {{{reachable_names}}} | เส้นคอขวด: {cut_names} | ความจุรวม = {_fmt(cut_capacity)} = Max Flow", {node_id: "inS" for node_id in reachable}, {edge["id"]: "cut" for edge in cut})

    final_flows = flow_of()
    cut_ids = {edge["id"] for edge in cut}
    summary = f'<div class="hero">🚰 ปริมาณไหลสูงสุดจาก <b>{_html(_name(names, source))}</b> ไป <b>{_html(_name(names, sink))}</b> = <span class="bignum">{_fmt(total)}</span></div>'
    summary += '<div class="cards">' + _card("จำนวนรอบ Augment", len(augmentations)) + _card("ความจุ Min Cut", _fmt(cut_capacity)) + _card("เส้นคอขวด", f"{len(cut)} เส้น") + _card("Max Flow = Min Cut", "✔ จริง" if math.isclose(total, cut_capacity, abs_tol=1e-9) else "✘") + "</div>"
    summary += '<h3>🔴 เส้นคอขวด (Min Cut)</h3>' + ("".join(f'<span class="chip" style="background:#ffd6d6">{_html(_name(names, edge["u"]))}–{_html(_name(names, edge["v"]))} ({_fmt(edge["w"])})</span>' for edge in cut) if cut else "<p>-</p>")
    side_s = " ".join(f'<span class="chip">{_html(_name(names, node_id))}</span>' for node_id in reachable)
    side_t = " ".join(f'<span class="chip">{_html(names[node_id])}</span>' for node_id in ids if node_id not in reachable)
    summary += f'<p style="font-size:14px">ฝั่ง S: {side_s}<br>ฝั่ง T: {side_t}</p>'
    summary += '<h3>Augmenting Paths ทีละรอบ</h3><div class="tw"><table class="tbl"><tr><th>รอบ</th><th>เส้นทาง</th><th>เพิ่ม</th></tr>'
    for index, (path, amount, uses_reverse) in enumerate(augmentations, 1):
        path_text = " → ".join(_html(_name(names, node_id)) for node_id in path) + (" ↺" if uses_reverse else "")
        summary += f"<tr><td>{index}</td><td class=\"l\">{path_text}</td><td><b>+{_fmt(amount)}</b></td></tr>"
    summary += "</table></div><h3>Flow บนแต่ละเส้น</h3><div class=\"tw\"><table class=\"tbl\"><tr><th>เส้น</th><th>Flow / Capacity</th><th>สถานะ</th></tr>"
    for edge in edges:
        value = final_flows[edge["id"]]
        absolute = abs(value)
        direction = f" ({_name(names, edge['u'])}→{_name(names, edge['v'])})" if not directed and absolute > 1e-9 and value > 0 else (f" ({_name(names, edge['v'])}→{_name(names, edge['u'])})" if not directed and absolute > 1e-9 else "")
        status = "🔴 คอขวด (เต็ม)" if edge["id"] in cut_ids else ("🟣 เต็ม" if absolute >= edge["w"] - 1e-9 and edge["w"] > 0 else f"เหลือ {_fmt(edge['w'] - absolute)}")
        summary += f'<tr><td class="l">{_html(_name(names, edge["u"]))}–{_html(_name(names, edge["v"]))}{_html(direction)}</td><td><b>{_fmt(absolute)}/{_fmt(edge["w"])}</b></td><td class="l">{status}</td></tr>'
    summary += "</table></div><div class=\"note\">ใช้ประเมินปริมาณสินค้าหรือการจราจรสูงสุดที่โครงข่ายรองรับได้ เส้นคอขวด (Min Cut) คือจุดที่ควรขยายก่อน เพราะถ้าเพิ่มความจุเส้นเหล่านี้ Max Flow จึงจะเพิ่มขึ้นได้</div>"
    return _result("📊 สรุปผล Max Flow (Edmonds–Karp)", "flow", steps, summary)


# ======================= ส่วนที่เพิ่มใหม่ (หมวด B: ข้อ 7–12) =======================
class _Rec:
    """เก็บสถานะที่ค้างอยู่ระหว่างขั้นตอน แล้วสร้าง step ต่อขั้น"""

    def __init__(self, edges):
        self.n, self.e, self.nt, self.fill, self.steps = {}, {}, {}, {}, []
        self.et = {e["id"]: _fmt(e["w"]) for e in edges}

    def snap(self, msg, node=None, edge=None):
        self.steps.append(_step(msg, node={**self.n, **(node or {})}, edge={**self.e, **(edge or {})},
                                ntext=dict(self.nt) or None, etext=dict(self.et), fill=dict(self.fill) or None))


def _prep(p, need_dir=None, src=False):
    nodes, edges, names, d = _graph(p)
    if not nodes:
        raise ValueError("ยังไม่มีจุดยอด")
    if need_dir is True and not d:
        raise ValueError("อัลกอริทึมนี้ต้องใช้กราฟแบบมีทิศทาง — กดปุ่ม 'ไม่มีทิศ' บนแถบเครื่องมือเพื่อเปิดทิศทางก่อน")
    if need_dir is False and d:
        raise ValueError("อัลกอริทึมนี้ใช้ได้เฉพาะกราฟไม่มีทิศทาง")
    ids = [n["id"] for n in nodes]
    adj = {i: [] for i in ids}
    for e in edges:
        adj[e["u"]].append((e["v"], e))
        if not d and e["u"] != e["v"]:
            adj[e["v"]].append((e["u"], e))
    s = p.get("source")
    if src and s not in names:
        raise ValueError("กรุณาเลือกจุดต้นทางก่อน")
    return nodes, edges, names, d, ids, adj, (s if s in names else ids[0])


def _tbl(head, rows):
    return ('<div class="tw"><table class="tbl"><tr>' + "".join(f"<th>{h}</th>" for h in head) + "</tr>"
            + "".join("<tr>" + "".join(f"<td>{_html(c)}</td>" for c in row) + "</tr>" for row in rows) + "</table></div>")


def _hero(text, kind=""):
    return f'<div class="hero {kind}">{text}</div>'


def _bfs(p):
    nodes, edges, names, d, ids, adj, s = _prep(p)
    nm = lambda i: _name(names, i)
    r, lvl, q, seen = _Rec(edges), {s: 0}, deque([s]), set()
    r.n[s], r.nt[s] = "consider", "L0"
    r.snap(f"เริ่มที่ {nm(s)} | Queue = [{nm(s)}]", {s: "current"})
    while q:
        u = q.popleft()
        r.n[u] = "visited"
        r.snap(f"นำ {nm(u)} ออกจาก Queue | Queue = [{', '.join(nm(x) for x in q)}]", {u: "current"})
        for v, e in adj[u]:
            if e["id"] in seen:
                continue
            seen.add(e["id"])
            if v not in lvl:
                lvl[v], r.n[v], r.e[e["id"]] = lvl[u] + 1, "consider", "tree"
                r.nt[v] = f"L{lvl[v]}"
                q.append(v)
                r.snap(f"พบ {nm(v)} ผ่าน {nm(u)} (ระดับ {lvl[v]}) → ใส่ Queue = [{', '.join(nm(x) for x in q)}]", {u: "current"})
            else:
                r.e[e["id"]] = "reject"
                r.snap(f"{nm(u)}–{nm(v)} เคยพบแล้ว → Non-tree edge ข้าม", {u: "current"})
    miss = [i for i in ids if i not in lvl]
    r.snap(f"✔ เสร็จสิ้น BFS เข้าถึง {len(lvl)}/{len(ids)} จุด")
    rows = [(nm(i), lvl[i]) for i in sorted(lvl, key=lvl.get)]
    sm = _hero(f"🔎 BFS จาก {_html(nm(s))} เข้าถึง {len(lvl)} จุด (ระยะ = จำนวนเส้นน้อยสุด)", "warn" if miss else "")
    sm += _tbl(["จุด", "ระดับ (Level)"], rows)
    if miss:
        sm += f"<p>⚠ เข้าถึงไม่ได้: {_html(', '.join(nm(i) for i in miss))}</p>"
    return _result("📊 สรุปผล BFS", "bfs", r.steps, sm + '<div class="note">เวลา O(V+E) · พื้นที่ O(V) · ใช้หาเส้นทางที่ใช้จำนวนเส้นน้อยที่สุดในกราฟไม่มีน้ำหนัก</div>')


def _dfs(p):
    nodes, edges, names, d, ids, adj, s = _prep(p)
    nm = lambda i: _name(names, i)
    r, disc, fin, cls, stk, t = _Rec(edges), {}, {}, {}, [], [0]
    names_c = {"T": "Tree", "B": "Back", "F": "Forward", "C": "Cross"}
    sty = {"T": "tree", "B": "cut", "F": "reject", "C": "reject"}

    def go(u):
        t[0] += 1
        disc[u] = t[0]
        stk.append(u)
        r.n[u], r.nt[u] = "current", f"{disc[u]}/?"
        r.snap(f"เข้า {nm(u)} (d={disc[u]}) | Stack = [{', '.join(nm(x) for x in stk)}]", {u: "current"})
        for v, e in adj[u]:
            if e["id"] in cls:
                continue
            if v not in disc:
                c = "T"
            elif v not in fin:
                c = "B"
            else:
                c = "F" if disc[u] < disc[v] else "C"
            cls[e["id"]], r.e[e["id"]], r.et[e["id"]] = c, sty[c], c
            r.snap(f"{nm(u)}→{nm(v)} = {names_c[c]} edge", {u: "current"})
            if c == "T":
                go(v)
        stk.pop()
        t[0] += 1
        fin[u], r.n[u], r.nt[u] = t[0], "visited", f"{disc[u]}/{t[0]}"
        r.snap(f"ออกจาก {nm(u)} (f={fin[u]}) | Stack = [{', '.join(nm(x) for x in stk)}]")

    for root in [s] + ids:
        if root not in disc:
            go(root)
    r.snap(f"✔ เสร็จสิ้น DFS (ป้ายบนจุด = เวลาค้นพบ/เวลาเสร็จ, ป้ายบนเส้น: T=Tree B=Back F=Forward C=Cross)")
    sm = _hero("🧭 DFS เสร็จสิ้น — ได้เวลา Discovery/Finish และชนิดของเส้น")
    sm += _tbl(["จุด", "d (ค้นพบ)", "f (เสร็จ)"], [(nm(i), disc[i], fin[i]) for i in sorted(disc, key=disc.get)])
    cnt = {k: sum(1 for c in cls.values() if c == k) for k in names_c}
    sm += '<div class="cards">' + "".join(_card(names_c[k] + " edge", v) for k, v in cnt.items()) + "</div>"
    sm += '<div class="note">Back edge ในกราฟมีทิศ = มีวงจร (Cycle) · เวลา O(V+E) · พื้นที่ O(V)</div>'
    return _result("📊 สรุปผล DFS", "dfs", r.steps, sm)


def _kruskal(p):
    nodes, edges, names, d, ids, adj, s = _prep(p, need_dir=False)
    nm = lambda i: _name(names, i)
    par = {i: i for i in ids}

    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x

    r, tot, chosen = _Rec(edges), 0, []
    for e in sorted(edges, key=lambda e: e["w"]):
        a, b, lab = find(e["u"]), find(e["v"]), f"{nm(e['u'])}–{nm(e['v'])} ({_fmt(e['w'])})"
        r.snap(f"พิจารณาเส้นที่เล็กที่สุดถัดไป {lab}", edge={e["id"]: "consider"})
        if a != b:
            par[a] = b
            tot += e["w"]
            chosen.append((e, tot))
            r.e[e["id"]], r.n[e["u"]], r.n[e["v"]] = "tree", "visited", "visited"
            r.snap(f"✔ รับ {lab} (คนละกลุ่ม) | น้ำหนักรวม = {_fmt(tot)}")
        else:
            r.e[e["id"]] = "reject"
            r.snap(f"✘ ข้าม {lab} เพราะจะเกิดวงจร (Union-Find พบว่าอยู่กลุ่มเดียวกัน)")
    k = len({find(i) for i in ids})
    r.snap(f"✔ เสร็จสิ้น เลือก {len(chosen)} เส้น น้ำหนักรวม = {_fmt(tot)}")
    sm = _hero(f"🌳 {'Minimum Spanning Tree' if k == 1 else f'Spanning Forest ({k} ต้น)'} น้ำหนักรวม = <span class=\"bignum\">{_fmt(tot)}</span>", "warn" if k > 1 else "")
    sm += _tbl(["#", "เส้น", "น้ำหนัก", "รวมสะสม"], [(i, f"{nm(e['u'])}–{nm(e['v'])}", _fmt(e["w"]), _fmt(c)) for i, (e, c) in enumerate(chosen, 1)])
    return _result("📊 สรุปผล Kruskal", "kruskal", r.steps, sm + '<div class="note">เวลา O(E log E) · พื้นที่ O(V) — ผลน้ำหนักรวมต้องเท่ากับ Prim (เปรียบเทียบจำนวนขั้นได้)</div>')


def _bellman(p):
    nodes, edges, names, d, ids, adj, s = _prep(p, src=True)
    nm = lambda i: _name(names, i)
    r, dist, pred = _Rec(edges), {i: math.inf for i in ids}, {}
    dist[s] = 0
    arcs = [(e["u"], e["v"], e) for e in edges] + ([] if d else [(e["v"], e["u"], e) for e in edges if e["u"] != e["v"]])
    r.nt = {i: "∞" for i in ids}
    r.nt[s] = "0"
    r.snap(f"เริ่มต้น d({nm(s)}) = 0 ส่วนจุดอื่น = ∞", {s: "current"})
    neg = None
    for rnd in range(1, len(ids) + 1):
        changed = None
        for u, v, e in arcs:
            if dist[u] < math.inf and dist[u] + e["w"] < dist[v] - 1e-12:
                dist[v], pred[v], changed = dist[u] + e["w"], (u, e["id"]), v
                r.nt[v] = _fmt(dist[v])
                r.snap(f"รอบ {rnd}: Relax {nm(u)}→{nm(v)} (w={_fmt(e['w'])}) ⇒ d({nm(v)}) = {_fmt(dist[v])}", {u: "current", v: "consider"}, {e["id"]: "consider"})
        if changed is None:
            r.snap(f"รอบ {rnd}: ไม่มีระยะเปลี่ยน → หยุดก่อนได้")
            break
        if rnd == len(ids):
            neg = changed
    if neg is not None:
        x = neg
        for _ in ids:
            x = pred[x][0]
        cyc, es, y = [x], [], x
        while True:
            y, eid = pred[y]
            es.append(eid)
            if y == x:
                break
            cyc.append(y)
        r.snap("⚠ พบ Negative Cycle: " + " → ".join(nm(c) for c in reversed(cyc)) + f" → {nm(x)} (ผลรวมน้ำหนักติดลบ วนแล้วถูกลงเรื่อย ๆ)", {c: "consider" for c in cyc}, {i: "cut" for i in es})
        sm = _hero("⚠ พบ Negative Cycle — ไม่มีระยะสั้นที่สุดที่แน่นอน (ในกราฟไม่มีทิศ เส้นติดลบเส้นเดียวก็ทำให้เกิดวงจรลบ)", "bad")
        return _result("📊 สรุปผล Bellman-Ford", "bellman", r.steps, sm)

    def path(t):
        out = [t]
        while out[-1] in pred:
            out.append(pred[out[-1]][0])
        return " → ".join(nm(i) for i in reversed(out))

    r.e = {eid: "soft" for _, eid in pred.values()}
    r.n = {i: "visited" for i in ids if dist[i] < math.inf}
    r.snap("✔ เสร็จสิ้น — ไม่มี Negative Cycle")
    rows = [(nm(i), _fmt(dist[i]), path(i) if dist[i] < math.inf else "เข้าถึงไม่ได้") for i in ids]
    return _result("📊 สรุปผล Bellman-Ford", "bellman", r.steps, _hero(f"🛣️ ระยะสั้นที่สุดจาก {_html(nm(s))} (รองรับน้ำหนักติดลบ)") + _tbl(["ปลายทาง", "ระยะ", "เส้นทาง"], rows) + '<div class="note">เวลา O(VE) · พื้นที่ O(V) · ช้ากว่า Dijkstra แต่ใช้กับน้ำหนักติดลบและตรวจวงจรลบได้</div>')


def _topo(p):
    nodes, edges, names, d, ids, adj, s = _prep(p, need_dir=True)
    nm = lambda i: _name(names, i)
    indeg = {i: 0 for i in ids}
    for e in edges:
        indeg[e["v"]] += 1
    q, order, r = deque(i for i in ids if indeg[i] == 0), [], _Rec(edges)
    r.nt = {i: str(indeg[i]) for i in ids}
    r.snap("เลข = in-degree · เริ่มจากจุดที่ in-degree = 0", {i: "consider" for i in q})
    while q:
        u = q.popleft()
        order.append(u)
        r.n[u], r.nt[u] = "visited", f"#{len(order)}"
        for v, e in adj[u]:
            indeg[v] -= 1
            r.e[e["id"]] = "soft"
            r.nt[v] = str(indeg[v])
            if indeg[v] == 0:
                q.append(v)
                r.n[v] = "consider"
        r.snap(f"เลือก {nm(u)} เป็นลำดับที่ {len(order)} แล้วลบเส้นขาออก | พร้อมถัดไป = [{', '.join(nm(x) for x in q)}]", {u: "current"})
    if len(order) < len(ids):
        stuck = ", ".join(nm(i) for i in ids if i not in order)
        raise ValueError(f"กราฟมีวงจร (Cycle) จึงทำ Topological Sort ไม่ได้ — จุดที่ติดอยู่ในวงจรหรือตามหลังวงจร: {stuck}")
    r.snap("✔ ลำดับ: " + " → ".join(nm(i) for i in order))
    sm = _hero("📋 Topological Order: " + " → ".join(f'<span class="chip">{_html(nm(i))}</span>' for i in order))
    return _result("📊 สรุปผล Topological Sort (Kahn)", "topo", r.steps, sm + '<div class="note">เวลา O(V+E) · ใช้จัดลำดับงานที่มีเงื่อนไขต้องทำก่อน-หลัง (DAG เท่านั้น)</div>')


def _scc(p):
    nodes, edges, names, d, ids, adj, s = _prep(p, need_dir=True)
    nm = lambda i: _name(names, i)
    r, idx, low, st, on, comps = _Rec(edges), {}, {}, [], set(), []

    def go(u):
        idx[u] = low[u] = len(idx)
        st.append(u)
        on.add(u)
        r.nt[u] = f"{idx[u]}/{low[u]}"
        r.snap(f"เยี่ยม {nm(u)} (index={idx[u]})", {u: "current"})
        for v, e in adj[u]:
            if v not in idx:
                r.e[e["id"]] = "tree"
                go(v)
                low[u] = min(low[u], low[v])
            elif v in on:
                low[u] = min(low[u], idx[v])
            r.nt[u] = f"{idx[u]}/{low[u]}"
        if low[u] == idx[u]:
            comp = []
            while True:
                w = st.pop()
                on.discard(w)
                comp.append(w)
                if w == u:
                    break
            for w in comp:
                r.fill[w] = len(comps)
            comps.append(comp)
            r.snap(f"low = index ที่ {nm(u)} → ได้ SCC #{len(comps)} = {{{', '.join(nm(w) for w in comp)}}}")

    for i in ids:
        if i not in idx:
            go(i)
    cid = {w: k for k, c in enumerate(comps) for w in c}
    cond = sorted({(cid[e["u"]], cid[e["v"]]) for e in edges if cid[e["u"]] != cid[e["v"]]})
    r.snap(f"✔ พบ {len(comps)} SCC แต่ละสี = 1 กลุ่ม")
    sm = _hero("🔗 กราฟนี้ Strongly Connected" if len(comps) == 1 else f"🔗 พบ {len(comps)} Strongly Connected Components", "" if len(comps) == 1 else "warn")
    sm += "".join(f'<div class="grp"><b>SCC #{k+1}</b> ' + "".join(f'<span class="chip">{_html(nm(w))}</span>' for w in c) + "</div>" for k, c in enumerate(comps))
    sm += "<h3>Condensation Graph (DAG)</h3><p>" + (", ".join(f"SCC#{a+1} → SCC#{b+1}" for a, b in cond) or "ไม่มีเส้นระหว่างกลุ่ม") + "</p>"
    return _result("📊 สรุปผล SCC (Tarjan)", "scc", r.steps, sm + '<div class="note">เวลา O(V+E) · พื้นที่ O(V)</div>')


def _bridges(p):
    nodes, edges, names, d, ids, adj, s = _prep(p, need_dir=False)
    nm = lambda i: _name(names, i)
    r, disc, low, br, ap = _Rec(edges), {}, {}, [], set()

    def go(u, pe):
        disc[u] = low[u] = len(disc) + 1
        kids = 0
        r.n[u], r.nt[u] = "visited", f"{disc[u]}/{low[u]}"
        r.snap(f"เยี่ยม {nm(u)} (disc={disc[u]}) · ป้าย = disc/low", {u: "current"})
        for v, e in adj[u]:
            if e["id"] == pe:
                continue
            if v not in disc:
                kids += 1
                r.e[e["id"]] = "tree"
                go(v, e["id"])
                low[u] = min(low[u], low[v])
                if low[v] > disc[u]:
                    br.append(e)
                    r.e[e["id"]] = "cut"
                    r.snap(f"🌉 {nm(u)}–{nm(v)} เป็น Bridge (low[{nm(v)}]={low[v]} > disc[{nm(u)}]={disc[u]})")
                if (pe is None and kids > 1) or (pe is not None and low[v] >= disc[u]):
                    if u not in ap:
                        ap.add(u)
                        r.n[u] = "consider"
                        r.snap(f"📍 {nm(u)} เป็น Articulation Point")
            else:
                low[u] = min(low[u], disc[v])
            r.nt[u] = f"{disc[u]}/{low[u]}"

    for i in ids:
        if i not in disc:
            go(i, None)
    r.snap(f"✔ พบ Bridge {len(br)} เส้น, Articulation Point {len(ap)} จุด")
    sm = _hero(f"🌉 Bridge {len(br)} เส้น · 📍 Articulation Point {len(ap)} จุด", "warn" if br or ap else "")
    sm += "<h3>Bridge</h3><p>" + (" ".join(f'<span class="chip">{_html(nm(e["u"]))}–{_html(nm(e["v"]))}</span>' for e in br) or "ไม่มี") + "</p>"
    sm += "<h3>Articulation Point</h3><p>" + (" ".join(f'<span class="chip">{_html(nm(i))}</span>' for i in sorted(ap)) or "ไม่มี") + "</p>"
    return _result("📊 สรุปผล Bridge & Articulation", "bridges", r.steps, sm + '<div class="note">เวลา O(V+E) · ใช้หาจุด/เส้นที่ถ้าขาดแล้วเครือข่ายแยกส่วน</div>')


def _euler(p):
    nodes, edges, names, d, ids, adj, s = _prep(p)
    nm = lambda i: _name(names, i)
    if not edges:
        raise ValueError("ยังไม่มีเส้นเชื่อม")
    r = _Rec(edges)
    out, inn = {i: 0 for i in ids}, {i: 0 for i in ids}
    for e in edges:
        out[e["u"]] += 1
        inn[e["v"]] += 1
    if d:
        st = [i for i in ids if out[i] - inn[i] == 1]
        en = [i for i in ids if inn[i] - out[i] == 1]
        ok = all(abs(out[i] - inn[i]) <= 1 for i in ids) and ((not st and not en) or (len(st) == 1 and len(en) == 1))
        circuit, start, odd = not st and not en, (st[0] if st else None), st + en
        why = "กราฟมีทิศ: ต้องมี in=out ทุกจุด (Circuit) หรือมี 1 จุดที่ out−in=1 และ 1 จุดที่ in−out=1 (Path)"
    else:
        odd = [i for i in ids if (out[i] + inn[i]) % 2]
        ok, circuit, start = len(odd) in (0, 2), not odd, (odd[0] if odd else None)
        why = f"จุดที่ degree คี่มี {len(odd)} จุด — ต้องเป็น 0 (Circuit) หรือ 2 (Path)"
    used_v = {x for e in edges for x in (e["u"], e["v"])}
    und = {i: set() for i in ids}
    for e in edges:
        und[e["u"]].add(e["v"])
        und[e["v"]].add(e["u"])
    seen, stack = {min(used_v)}, [min(used_v)]
    while stack:
        for v in und[stack.pop()]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    conn = used_v <= seen
    if not ok or not conn:
        msg = why if not ok else "จุดที่มีเส้นไม่ได้เชื่อมถึงกันทั้งหมด (ไม่ Connected)"
        r.snap("✘ ไม่มี Euler Path/Circuit: " + msg, {i: "consider" for i in odd})
        return _result("📊 สรุปผล Euler", "euler", r.steps, _hero("✘ ไม่มี Euler Path หรือ Circuit<br>" + _html(msg), "bad") + '<div class="note">Königsberg: 4 พื้นที่ มี degree คี่ 4 จุด จึงเดินข้ามทุกสะพานครั้งเดียวไม่ได้</div>')
    start = start if start is not None else (s if s in used_v else min(used_v))
    r.snap(f"{'Euler Circuit' if circuit else 'Euler Path'} มีอยู่ — เริ่ม Hierholzer ที่ {nm(start)}", {start: "current"})
    used, stk, circ = set(), [(start, None)], []
    while stk:
        u, ei = stk[-1]
        nx = next(((v, e) for v, e in adj[u] if e["id"] not in used), None)
        if nx:
            v, e = nx
            used.add(e["id"])
            stk.append((v, e["id"]))
            r.e[e["id"]] = "tree"
            r.snap(f"เดิน {nm(u)}→{nm(v)} ต่อไปเรื่อย ๆ จนตัน", {v: "current"})
        else:
            stk.pop()
            circ.append((u, ei))
            r.snap(f"ตันที่ {nm(u)} → ถอยกลับและบันทึกลงผลลัพธ์", {u: "current"})
    circ.reverse()
    r.e = {}
    for k, (v, ei) in enumerate(circ):
        if ei is not None:
            r.e[ei], r.et[ei] = "path", str(k)
            r.snap(f"ลำดับที่ {k}: ไปที่ {nm(v)}", {v: "current"})
    route = " → ".join(nm(v) for v, _ in circ)
    r.snap("✔ " + route)
    return _result("📊 สรุปผล Euler (Hierholzer)", "euler", r.steps, _hero(f"{'🔁 Euler Circuit' if circuit else '➡ Euler Path'}: {_html(route)}") + f"<p>{_html(why)}</p>" + '<div class="note">Hierholzer: เวลา O(E)</div>')


def run_algorithm(payload: dict[str, Any]) -> dict[str, Any]:
    algorithm = payload.get("algorithm")
    runners = {
        "dijkstra": _dijkstra,
        "prim": _prim,
        "color": _coloring,
        "flow": _flow,
        "bfs": _bfs, "dfs": _dfs, "kruskal": _kruskal, "bellman": _bellman,
        "topo": _topo, "scc": _scc, "bridges": _bridges, "euler": _euler,
        "floyd": _floyd, "dsatur": _dsatur, "edgecolor": _edgecolor, "matching": _matching, "hamilton": _hamilton, "tsp": _tsp,
        **EXTRA,
    }
    if algorithm not in runners:
        raise ValueError("ไม่รู้จักอัลกอริทึมที่เลือก")
    return runners[algorithm](payload)


# ======================= ส่วนที่เพิ่มใหม่ (ข้อ 9, 13, 14, 15, 16) =======================
def _floyd(p):
    nodes, edges, names, d, ids, adj, s = _prep(p)
    nm, INF = (lambda i: _name(names, i)), math.inf
    if len(ids) > 30:
        raise ValueError("Floyd–Warshall จำกัด |V| ≤ 30 เพื่อให้ตารางอ่านได้และรันทัน (เวลา O(V³))")
    if not d and any(e["w"] < 0 for e in edges):
        raise ValueError("กราฟไม่มีทิศที่มีเส้นติดลบจะเกิด Negative Cycle ทันที (เดินไป–กลับเส้นเดิม) — ใช้กับกราฟมีทิศแทน")
    D = {i: {j: 0 if i == j else INF for j in ids} for i in ids}
    for e in edges:
        for a, b in [(e["u"], e["v"])] + ([] if d else [(e["v"], e["u"])]):
            D[a][b] = min(D[a][b], e["w"])
    r = _Rec(edges)
    r.snap("เริ่มจากเมทริกซ์ระยะทางโดยตรง (∞ = ไม่มีเส้น)")
    for k in ids:
        ch = 0
        for i in ids:
            for j in ids:
                if D[i][k] + D[k][j] < D[i][j]:
                    D[i][j], ch = D[i][k] + D[k][j], ch + 1
        r.snap(f"ใช้ {nm(k)} เป็นจุดผ่าน → ปรับระยะสั้นลง {ch} คู่", {k: "current"})
    neg = [i for i in ids if D[i][i] < 0]
    r.snap("✔ เสร็จสิ้น" if not neg else "⚠ พบ Negative Cycle ที่จุด " + ", ".join(nm(i) for i in neg), {i: "consider" for i in neg})
    sm = _hero("⚠ พบ Negative Cycle — ระยะสั้นสุดไม่มีค่าที่แน่นอน" if neg else "🧮 Floyd–Warshall: ระยะสั้นสุดทุกคู่", "warn" if neg else "")
    sm += _tbl([""] + [nm(j) for j in ids], [[nm(i)] + [_fmt(D[i][j]) for j in ids] for i in ids])
    return _result("📊 สรุปผล Floyd–Warshall", "floyd", r.steps, sm + '<div class="note">เวลา O(V³) · พื้นที่ O(V²) · รองรับน้ำหนักติดลบ · ∞ = เข้าถึงไม่ได้</div>')


def _nbrs(ids, edges):
    nb = {i: set() for i in ids}
    for e in edges:
        if e["u"] != e["v"]:
            nb[e["u"]].add(e["v"])
            nb[e["v"]].add(e["u"])
    return nb


def _greedy_col(order, nb):
    c = {}
    for v in order:
        used = {c[u] for u in nb[v] if u in c}
        c[v] = next(k for k in range(len(nb) + 1) if k not in used)
    return c


def _dsatur(p):
    nodes, edges, names, d, ids, adj, s = _prep(p, need_dir=False)
    nm, nb, col, r = (lambda i: _name(names, i)), _nbrs(ids, edges), {}, _Rec(edges)
    while len(col) < len(ids):
        sat = lambda v: len({col[u] for u in nb[v] if u in col})
        v = max((i for i in ids if i not in col), key=lambda i: (sat(i), len(nb[i]), -i))
        sv, used = sat(v), {col[u] for u in nb[v] if u in col}
        col[v] = next(k for k in range(len(ids) + 1) if k not in used)
        r.fill[v], r.nt[v] = col[v], f"c{col[v] + 1}"
        r.snap(f"เลือก {nm(v)} (Saturation = {sv}, deg = {len(nb[v])}) → สี c{col[v] + 1}", {v: "current"})
    k = max(col.values()) + 1
    wp = max(_greedy_col(sorted(ids, key=lambda i: (-len(nb[i]), i)), nb).values()) + 1
    delta = max(len(nb[i]) for i in ids)
    r.snap(f"✔ DSatur ใช้ {k} สี (Welsh–Powell ใช้ {wp} สี)")
    sm = _hero(f"🎨 DSatur ใช้ <span class=\"bignum\">{k}</span> สี", "")
    sm += '<div class="cards">' + _card("DSatur", f"{k} สี") + _card("Welsh–Powell", f"{wp} สี") + _card("ขอบเขตบน Δ+1", delta + 1) + "</div>"
    for c in range(k):
        sm += f'<div class="grp"><div class="gh"><span class="sw" style="background:{_PALETTE[c % len(_PALETTE)]}"></span> c{c + 1}</div>' + "".join(f'<span class="chip">{_html(nm(i))}</span>' for i in ids if col[i] == c) + "</div>"
    sm += '<div class="note">DSatur เลือกจุดที่มี Saturation (จำนวนสีต่างกันของเพื่อนบ้าน) สูงสุดก่อน มักใช้สีน้อยกว่าหรือเท่า Welsh–Powell · เวลา O(V²)</div>'
    return _result("📊 สรุปผล DSatur", "color", r.steps, sm, colors=col)


def _edgecolor(p):
    nodes, edges, names, d, ids, adj, s = _prep(p, need_dir=False)
    nm = lambda i: _name(names, i)
    es = [e for e in edges if e["u"] != e["v"]]
    if not es:
        raise ValueError("ไม่มีเส้นให้ระบายสี (Self-loop ไม่นับ)")
    deg = {i: 0 for i in ids}
    for e in es:
        deg[e["u"]] += 1
        deg[e["v"]] += 1
    delta = max(deg.values())
    simple = len({frozenset((e["u"], e["v"])) for e in es}) == len(es)
    share = lambda a, b: bool({a["u"], a["v"]} & {b["u"], b["v"]})
    r, col = _Rec(edges), {}
    for e in sorted(es, key=lambda e: -(deg[e["u"]] + deg[e["v"]])):
        used = {col[f["id"]] for f in es if f["id"] in col and share(e, f)}
        c = col[e["id"]] = next(k for k in range(len(es) + 1) if k not in used)
        r.et[e["id"]] = f"c{c + 1}"
        r.snap(f"ระบาย {nm(e['u'])}–{nm(e['v'])} → สี c{c + 1} (เส้นที่มีจุดร่วมกันต้องคนละสี)", edge={e["id"]: "consider"})
        r.steps[-1]["efill"] = dict(col)
    k = max(col.values()) + 1
    exact = None
    if len(es) <= 14:
        def ok(i, c, kk):
            if i == len(es):
                return True
            for x in range(kk):
                if all(c[j] != x for j in range(i) if share(es[i], es[j])):
                    c[i] = x
                    if ok(i + 1, c, kk):
                        return True
                    del c[i]
            return False
        exact = next(kk for kk in range(delta, len(es) + 1) if ok(0, {}, kk))
    r.snap(f"✔ ใช้ {k} สี" + (f" | χ′(G) = {exact}" if exact else ""))
    r.steps[-1]["efill"] = dict(col)
    bound = f"Δ ≤ χ′ ≤ Δ+1 → {delta} ≤ χ′ ≤ {delta + 1} (Vizing)" if simple else f"มีเส้นขนาน: Vizing ใช้ไม่ได้ → ใช้ Shannon χ′ ≤ ⌊3Δ/2⌋ = {3 * delta // 2}"
    sm = _hero(f"🖍️ ระบายเส้นด้วย <span class=\"bignum\">{k}</span> สี", "")
    sm += '<div class="cards">' + _card("สีที่ใช้ (Greedy)", k) + _card("Δ", delta) + _card("χ′(G) แบบ Exact", exact if exact else "คำนวณเมื่อ |E| ≤ 14") + "</div>"
    sm += f"<p>{bound}</p>"
    for c in range(k):
        sm += f'<div class="grp"><div class="gh"><span class="sw" style="background:{_PALETTE[c % len(_PALETTE)]}"></span> c{c + 1}</div>' + "".join(f'<span class="chip">{_html(nm(e["u"]))}–{_html(nm(e["v"]))}</span>' for e in es if col[e["id"]] == c) + "</div>"
    return _result("📊 สรุปผล Edge Coloring", "edgecolor", r.steps, sm)


def _matching(p):
    nodes, edges, names, d, ids, adj, s = _prep(p, need_dir=False)
    nm, side = (lambda i: _name(names, i)), {}
    for st in ids:
        if st in side:
            continue
        side[st], q = 0, deque([st])
        while q:
            u = q.popleft()
            for v, _ in adj[u]:
                if v == u or side.get(v) == side[u]:
                    raise ValueError("กราฟนี้ไม่ใช่ Bipartite (มี Self-loop หรือวงจรคี่) จึงใช้ Matching แบบสองส่วนไม่ได้")
                if v not in side:
                    side[v] = 1 - side[u]
                    q.append(v)
    mate = {}

    def aug(u, seen):
        for v, _ in adj[u]:
            if v not in seen:
                seen.add(v)
                if v not in mate or aug(mate[v], seen):
                    mate[u], mate[v] = v, u
                    return True
        return False

    def cur():
        out, used = {}, set()
        for e in edges:
            key = frozenset((e["u"], e["v"]))
            if mate.get(e["u"]) == e["v"] and key not in used:
                used.add(key)
                out[e["id"]] = "tree"
        return out

    r, L = _Rec(edges), [i for i in ids if side[i] == 0]
    for u in L:
        ok = aug(u, set())
        r.e, r.n = cur(), {x: "visited" for x in mate}
        r.snap(f"หา Augmenting Path จาก {nm(u)} → " + (f"สำเร็จ |M| = {len(r.e)}" if ok else "ไม่พบ (ข้าม)"), {u: "current"})
    m = len(cur())
    r.snap(f"✔ Maximum Matching ขนาด {m}")
    pairs = [(nm(e["u"]), nm(e["v"])) for e in edges if e["id"] in cur()]
    free = [nm(i) for i in ids if i not in mate]
    sm = _hero(f"🤝 Maximum Matching ขนาด <span class=\"bignum\">{m}</span>")
    sm += '<div class="cards">' + _card("|M|", m) + _card("Min Vertex Cover (König)", m) + _card("Max Independent Set", len(ids) - m) + "</div>"
    sm += _tbl(["#", "คู่ที่จับ"], [(i, f"{a} ↔ {b}") for i, (a, b) in enumerate(pairs, 1)])
    sm += f"<p>{'✔ ฝั่งซ้ายถูกจับคู่ครบ (เข้าเงื่อนไข Hall)' if m == len(L) else '⚠ ฝั่งซ้ายจับคู่ไม่ครบ → มีเซตที่ |N(S)| < |S| (ละเมิด Hall)'}" + (f" · ไม่ได้จับคู่: {_html(', '.join(free))}" if free else "") + "</p>"
    return _result("📊 สรุปผล Bipartite Matching", "matching", r.steps, sm + '<div class="note">Kuhn (Augmenting Path) เวลา O(V·E) · König: |Max Matching| = |Min Vertex Cover| ในกราฟสองส่วน</div>')


def _hamilton(p):
    nodes, edges, names, d, ids, adj, s = _prep(p)
    n, nm = len(ids), (lambda i: _name(names, i))
    if n > 10:
        raise ValueError("Hamiltonian เป็นปัญหา NP-complete: Backtracking แย่สุด O(n!) จึงจำกัด |V| ≤ 10")
    nb = {u: {v for v, _ in adj[u] if v != u} for u in ids}
    eid = {}
    for e in edges:
        for a, b in [(e["u"], e["v"])] + ([] if d else [(e["v"], e["u"])]):
            eid.setdefault((a, b), e["id"])
    r, path = _Rec(edges), []

    def show(msg, close=False):
        t = path + path[:1] if close else path
        if len(r.steps) < 400:
            r.snap(msg, {x: "path" for x in path}, {eid[(a, b)]: "path" for a, b in zip(t, t[1:])})

    def dfs(cyc):
        show("เดิน: " + " → ".join(nm(x) for x in path))
        if len(path) == n:
            return (not cyc) or path[0] in nb[path[-1]]
        for v in sorted(nb[path[-1]]):
            if v not in path:
                path.append(v)
                if dfs(cyc):
                    return True
                path.pop()
        return False

    found = None
    for cyc in (True, False):
        for st in ([ids[0]] if cyc else ids):
            path[:] = [st]
            if dfs(cyc):
                found = cyc
                break
        if found is not None:
            break
    dg = {u: len(nb[u]) for u in ids}
    simple_u = not d and n >= 3
    dirac = simple_u and min(dg.values()) >= n / 2
    ore = simple_u and all(dg[a] + dg[b] >= n for a in ids for b in ids if a < b and b not in nb[a])
    if found is None:
        r.snap("✘ ไม่พบ Hamiltonian Path/Cycle (ลองครบทุกแบบแล้ว)")
        sm = _hero("✘ ไม่พบ Hamiltonian Path หรือ Cycle", "warn")
    else:
        show("✔ " + " → ".join(nm(x) for x in path) + (f" → {nm(path[0])}" if found else ""), found)
        sm = _hero(("🔁 พบ Hamiltonian Cycle: " if found else "➰ พบเฉพาะ Hamiltonian Path (ไม่มี Cycle): ") + _html(" → ".join(nm(x) for x in path)))
    yn = lambda b: "✔ ผ่าน" if b else "✘ ไม่ผ่าน"
    sm += _tbl(["ทฤษฎีบท", "เงื่อนไข", "ผล"], [("Dirac", "n ≥ 3 และ deg(v) ≥ n/2 ทุกจุด ⇒ มี Hamiltonian Cycle", yn(dirac)), ("Ore", "deg(u)+deg(v) ≥ n ทุกคู่ที่ไม่ติดกัน ⇒ มี Hamiltonian Cycle", yn(ore))])
    return _result("📊 สรุปผล Hamiltonian", "hamilton", r.steps, sm + '<div class="note">เงื่อนไข Dirac/Ore เป็น “เพียงพอ” ไม่ใช่ “จำเป็น” (ไม่ผ่านก็อาจมี Cycle ได้) · ใช้กับกราฟไม่มีทิศแบบ Simple</div>')


def _tsp(p):
    nodes, edges, names, d, ids, adj, s = _prep(p)
    n, nm, INF = len(ids), (lambda i: _name(names, i)), math.inf
    if n > 10:
        raise ValueError("TSP แบบ Held–Karp ใช้เวลา O(n²·2ⁿ) และหน่วยความจำ O(n·2ⁿ) จึงจำกัด |V| ≤ 10")
    if n < 3:
        raise ValueError("TSP ต้องมีอย่างน้อย 3 จุดยอด")
    ix = {v: k for k, v in enumerate(ids)}
    W, eid = [[INF] * n for _ in range(n)], {}
    for e in edges:
        a, b = ix[e["u"]], ix[e["v"]]
        for x, y in [(a, b)] + ([] if d else [(b, a)]):
            if x != y and e["w"] < W[x][y]:
                W[x][y], eid[(x, y)] = e["w"], e["id"]
    dp = {(1, 0): (0, None)}
    for mask in range(1, 1 << n, 2):
        for j in range(n):
            if (mask, j) in dp:
                for k in range(1, n):
                    c = dp[(mask, j)][0] + W[j][k]
                    if not mask >> k & 1 and c < INF and ((mask | 1 << k, k) not in dp or c < dp[(mask | 1 << k, k)][0]):
                        dp[(mask | 1 << k, k)] = (c, j)
    full = (1 << n) - 1
    best = min(((dp[(full, j)][0] + W[j][0], j) for j in range(1, n) if (full, j) in dp and W[j][0] < INF), default=None)
    ed = lambda t, st: {eid[(a, b)]: st for a, b in zip(t, t[1:] + t[:1]) if (a, b) in eid}
    cur, seen, nn = 0, {0}, [0]
    while len(seen) < n:
        c = min((k for k in range(n) if k not in seen and W[cur][k] < INF), key=lambda k: W[cur][k], default=None)
        if c is None:
            break
        seen.add(c)
        nn.append(c)
        cur = c
    nn_len = sum(W[a][b] for a, b in zip(nn, nn[1:] + nn[:1])) if len(nn) == n else INF
    r = _Rec(edges)
    if len(nn) == n and nn_len < INF:
        r.snap(f"Nearest Neighbor จาก {nm(ids[0])}: ความยาว {_fmt(nn_len)}", edge=ed(nn, "consider"))
    if best is None:
        r.snap("✘ ไม่มีทัวร์ที่ผ่านทุกจุดครั้งเดียวแล้วกลับจุดเริ่ม")
        return _result("📊 สรุปผล TSP", "tsp", r.steps, _hero("✘ ไม่มี Hamiltonian Cycle จึงไม่มีคำตอบ TSP", "warn"))
    tour, mask, j = [], full, best[1]
    while j is not None:
        tour.append(j)
        mask, j = mask ^ (1 << j), dp[(mask, j)][1]
    tour = tour[::-1]
    r.snap(f"Held–Karp (DP): ทัวร์ที่ดีที่สุด ความยาว {_fmt(best[0])}", {ids[x]: "path" for x in tour}, ed(tour, "path"))
    sm = _hero(f"🧭 TSP ที่ดีที่สุด = <span class=\"bignum\">{_fmt(best[0])}</span>")
    sm += f"<p>{_html(' → '.join(nm(ids[x]) for x in tour + tour[:1]))}</p>"
    nn_txt = f"{_fmt(nn_len)} (แย่กว่า {(nn_len / best[0] - 1) * 100:.0f}%)" if nn_len < INF and best[0] > 0 else _fmt(nn_len)
    sm += '<div class="cards">' + _card("Held–Karp (Exact)", _fmt(best[0])) + _card("Nearest Neighbor", nn_txt) + "</div>"
    return _result("📊 สรุปผล TSP", "tsp", r.steps, sm + '<div class="note">Held–Karp เวลา O(n²·2ⁿ) · Nearest Neighbor เวลา O(n²) แต่ไม่รับประกันค่าที่ดีที่สุด · เส้นที่ไม่มี = ∞</div>')


try:  # อัลกอริทึมส่วนขยาย (graph_extra.py)
    from graph_extra import EXTRA
except ImportError:
    EXTRA = {}
