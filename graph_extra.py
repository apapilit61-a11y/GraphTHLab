# -*- coding: utf-8 -*-
"""ส่วนขยายอัลกอริทึม: Kirchhoff, Prüfer, Havel–Hakimi, Exact Cover/Independent/Clique/Dominating,
Planarity (เงื่อนไขที่ตรวจได้), Centrality+Laplacian Spectrum, Vertex/Edge Connectivity"""
from __future__ import annotations

import math
import re
from collections import deque
from fractions import Fraction
from itertools import combinations

from graph_algorithms import _Rec, _card, _hero, _html, _name, _prep, _result, _step, _tbl


def _simple(ids, edges):
    """เพื่อนบ้านของกราฟ simple แบบไม่มีทิศ (ตัด self-loop และเส้นขนาน)"""
    A = {i: set() for i in ids}
    for e in edges:
        if e["u"] != e["v"]:
            A[e["u"]].add(e["v"])
            A[e["v"]].add(e["u"])
    return A


def _chips(items):
    return " ".join(f'<span class="chip">{_html(x)}</span>' for x in items) or "—"


def _limit(n, cap, what):
    if n > cap:
        raise ValueError(f"{what} จำกัด |V| ≤ {cap} เพราะเวลาเพิ่มแบบทวีคูณ/ตารางใหญ่เกินอ่านได้ (ขณะนี้ |V| = {n})")


# ---------- ข้อ 19: Kirchhoff ----------
def _det(M):
    n, M, det = len(M), [[Fraction(x) for x in r] for r in M], Fraction(1)
    for c in range(n):
        p = next((r for r in range(c, n) if M[r][c] != 0), None)
        if p is None:
            return Fraction(0)
        if p != c:
            M[c], M[p], det = M[p], M[c], -det
        det *= M[c][c]
        for r in range(c + 1, n):
            f = M[r][c] / M[c][c]
            for k in range(c, n):
                M[r][k] -= f * M[c][k]
    return det


def _kirchhoff(p):
    nodes, edges, names, d, ids, adj, s = _prep(p, need_dir=False)
    _limit(len(ids), 40, "Kirchhoff")
    ix, n = {v: k for k, v in enumerate(ids)}, len(ids)
    L = [[0] * n for _ in ids]
    for e in edges:
        u, v = ix[e["u"]], ix[e["v"]]
        if u != v:
            L[u][u] += 1; L[v][v] += 1; L[u][v] -= 1; L[v][u] -= 1
    cnt = int(_det([r[1:] for r in L[1:]])) if n > 1 else 1
    r = _Rec(edges)
    r.snap("สร้าง Laplacian L = D − A แล้วตัดแถว/คอลัมน์แรกออก → det = จำนวน Spanning Tree")
    sm = _hero(f'🌲 จำนวน Spanning Tree = <span class="bignum">{cnt}</span>', "warn" if cnt == 0 else "")
    sm += "<h3>Laplacian Matrix L = D − A</h3>" + _tbl([""] + [_name(names, i) for i in ids], [[_name(names, i)] + L[k] for k, i in enumerate(ids)])
    sm += '<div class="note">Kirchhoff: τ(G) = det ของ cofactor ใดก็ได้ของ L · เส้นขนานนับแยกเป็นคนละต้นไม้ · τ = 0 แปลว่ากราฟไม่ Connected · ตรวจ: τ(Kₙ) = nⁿ⁻²</div>'
    return _result("📊 สรุปผล Matrix-Tree Theorem", "kirchhoff", r.steps, sm)


# ---------- ข้อ 19: Prüfer ----------
def _prufer(p):
    nodes, edges, names, d, ids, adj, s = _prep(p, need_dir=False)
    nm, n, A = (lambda i: _name(names, i)), len(ids), _simple(ids, edges)
    if n < 2 or len(edges) != n - 1 or any(e["u"] == e["v"] for e in edges) or len({frozenset((e["u"], e["v"])) for e in edges}) != n - 1:
        raise ValueError("Prüfer Code ใช้ได้กับ 'ต้นไม้' เท่านั้น: ต้องมี |V| ≥ 2, |E| = |V|−1, ไม่มี Self-loop/เส้นขนาน และ Connected")
    seen, q = {ids[0]}, deque([ids[0]])
    while q:
        for v in A[q.popleft()]:
            if v not in seen:
                seen.add(v); q.append(v)
    if len(seen) != n:
        raise ValueError("กราฟนี้ไม่ Connected จึงไม่ใช่ต้นไม้")
    deg, alive, code, r = {i: len(A[i]) for i in ids}, set(ids), [], _Rec(edges)
    eid = {frozenset((e["u"], e["v"])): e["id"] for e in edges}
    r.snap("ลบใบ (leaf) ที่ label น้อยสุดซ้ำ ๆ แล้วจดเพื่อนบ้านของมัน จนเหลือ 2 จุด")
    while len(alive) > 2:
        leaf = min(i for i in alive if deg[i] == 1)
        nb = next(v for v in A[leaf] if v in alive)
        code.append(nb); alive.discard(leaf); deg[nb] -= 1
        r.n[leaf] = "visited"; r.e[eid[frozenset((leaf, nb))]] = "soft"
        r.snap(f"ลบใบ {nm(leaf)} → จด {nm(nb)} | รหัสตอนนี้: [{', '.join(nm(c) for c in code)}]", {leaf: "current", nb: "consider"})
    r.snap("✔ รหัส Prüfer: [" + ", ".join(nm(c) for c in code) + "]")
    sm = _hero("🔢 Prüfer Code: " + _chips([nm(c) for c in code]) if code else "🔢 Prüfer Code ว่าง (ต้นไม้ 2 จุด)")
    sm += f'<div class="note">ยาว n−2 = {n - 2} · จุดที่ปรากฏ k ครั้งมี degree = k+1 · มีต้นไม้ที่ label ต่างกัน nⁿ⁻² แบบ (Cayley) · ถอดรหัสกลับได้ทุกรหัส</div>'
    return _result("📊 สรุปผล Prüfer Code", "prufer", r.steps, sm)


# ---------- ข้อ 20: Havel–Hakimi / Erdős–Gallai ----------
def _havel(p):
    raw, names = p.get("sequence"), None
    if raw and str(raw).strip():
        try:
            seq = [int(x) for x in re.split(r"[,\s]+", str(raw).strip()) if x]
        except ValueError:
            raise ValueError("Degree Sequence ต้องเป็นจำนวนเต็ม คั่นด้วย , เช่น 3,3,2,2,2") from None
        label = lambda i: f"v{i + 1}"
    else:
        nodes, edges, names, d, ids, adj, s = _prep(p, need_dir=False)
        deg = {i: 0 for i in ids}
        for e in edges:
            deg[e["u"]] += 1; deg[e["v"]] += 1
        seq, label = [deg[i] for i in ids], (lambda k, ids=ids: _name(names, ids[k]))
    if not seq or len(seq) > 60 or min(seq) < 0:
        raise ValueError("ต้องมี 1–60 ค่า และห้ามมีค่าติดลบ")
    s = sorted(seq, reverse=True)
    eg = all(sum(s[:k]) <= k * (k - 1) + sum(min(x, k) for x in s[k:]) for k in range(1, len(s) + 1))
    cur, out, ok, steps = list(zip(seq, range(len(seq)))), [], True, [_step(f"ลำดับเริ่มต้น: {seq} (ผลรวม {sum(seq)})")]
    while True:
        cur.sort(key=lambda c: -c[0])
        if cur[0][0] == 0:
            break
        d0, i0 = cur.pop(0)
        if d0 > len(cur) or any(c[0] == 0 for c in cur[:d0]):
            ok = False
            steps.append(_step(f"❌ {label(i0)} ต้องการเพื่อนบ้าน {d0} จุด แต่มีจุดที่ยังรับเส้นได้ไม่พอ"))
            break
        for k in range(d0):
            cur[k] = (cur[k][0] - 1, cur[k][1]); out.append((i0, cur[k][1]))
        steps.append(_step(f"เลือก {label(i0)} (deg {d0}) ต่อกับ {d0} จุดที่ deg มากสุด → เหลือ {sorted([c[0] for c in cur], reverse=True)}"))
    ok = ok and sum(seq) % 2 == 0
    steps.append(_step("✔ Graphical (สร้างกราฟ simple ได้)" if ok else "✘ Non-graphical"))
    sm = _hero("✅ สร้างเป็นกราฟ simple ได้" if ok else "❌ ลำดับนี้ไม่ใช่ Degree Sequence ของกราฟ simple", "" if ok else "bad")
    sm += f'<div class="cards">{_card("ผลรวม", sum(seq))}{_card("ผลรวมเป็นเลขคู่", "ใช่" if sum(seq) % 2 == 0 else "ไม่")}{_card("Erdős–Gallai", "ผ่าน" if eg else "ไม่ผ่าน")}{_card("Havel–Hakimi", "ผ่าน" if ok else "ไม่ผ่าน")}</div>'
    if ok:
        sm += "<h3>เส้นที่สร้างได้</h3><p>" + _chips(f"{label(a)}–{label(b)}" for a, b in out) + "</p>"
    sm += '<div class="note">Erdős–Gallai และ Havel–Hakimi ให้คำตอบตรงกันเสมอ · เวลา O(n² log n)</div>'
    return _result("📊 สรุปผล Havel–Hakimi / Erdős–Gallai", "havel", steps, sm)


# ---------- ข้อ 14: Exact Vertex Cover / Independent Set / Clique / Dominating Set ----------
def _cover(p):
    nodes, edges, names, d, ids, adj, s = _prep(p)
    n = len(ids)
    _limit(n, 16, "Exact Cover/Independent/Clique/Dominating")
    nm, ix = (lambda i: _name(names, i)), {v: k for k, v in enumerate(ids)}
    nb, loop = [0] * n, 0
    for e in edges:
        a, b = ix[e["u"]], ix[e["v"]]
        if a == b:
            loop |= 1 << a
        else:
            nb[a] |= 1 << b; nb[b] |= 1 << a
    full = (1 << n) - 1
    best = {"is": 0, "cl": 0, "ds": full}
    for m in range(1 << n):
        pc, vs = bin(m).count("1"), [v for v in range(n) if m >> v & 1]
        if pc > bin(best["is"]).count("1") and not m & loop and all(not nb[v] & m for v in vs):
            best["is"] = m
        if pc > bin(best["cl"]).count("1") and all((nb[v] | 1 << v) & m == m for v in vs):
            best["cl"] = m
        if pc < bin(best["ds"]).count("1"):
            cov = 0
            for v in vs:
                cov |= nb[v] | 1 << v
            if cov == full:
                best["ds"] = m
    best["vc"] = full ^ best["is"]
    pick = lambda m: [ids[v] for v in range(n) if m >> v & 1]
    title = {"vc": "Minimum Vertex Cover", "is": "Maximum Independent Set", "cl": "Maximum Clique", "ds": "Minimum Dominating Set"}
    r = _Rec(edges)
    r.snap("ค้นแบบ Exact ทุกซับเซต 2ⁿ (ใช้ bitmask)")
    for k in ("vc", "is", "cl", "ds"):
        r.n = {i: "visited" for i in pick(best[k])}
        r.snap(f"{title[k]} ขนาด {len(pick(best[k]))}: " + ", ".join(nm(i) for i in pick(best[k])))
    sm = _hero("🧱 Exact เมื่อกราฟเล็ก (|V| ≤ 16)")
    sm += _tbl(["ปัญหา", "ขนาด", "สมาชิก"], [[title[k], len(pick(best[k])), ", ".join(nm(i) for i in pick(best[k]))] for k in ("vc", "is", "cl", "ds")])
    sm += f'<div class="note">ตรวจ Gallai: α + τ = |V| → {len(pick(best["is"]))} + {len(pick(best["vc"]))} = {n} · มองกราฟเป็นแบบไม่มีทิศและตัดเส้นขนาน · Vertex Cover/Independent Set/Clique เป็น NP-hard จึงจำกัดขนาด</div>'
    return _result("📊 สรุปผล Exact Covering Problems", "cover", r.steps, sm)


# ---------- ข้อ 17: Planarity (เงื่อนไขที่ตรวจได้) ----------
def _planar(p):
    nodes, edges, names, d, ids, adj, s = _prep(p)
    nm, A = (lambda i: _name(names, i)), _simple(ids, edges)
    n, m = len(ids), sum(len(x) for x in A.values()) // 2
    seen, comps = set(), 0
    for i in ids:
        if i not in seen:
            comps += 1; seen.add(i); q = deque([i])
            while q:
                for v in A[q.popleft()]:
                    if v not in seen:
                        seen.add(v); q.append(v)
    tri = next(((a, b, c) for a, b in ((a, b) for a in ids for b in A[a] if a < b) for c in A[a] & A[b] if c > b), None)
    col, bip = {}, True
    for i in ids:
        if i in col:
            continue
        col[i], q = 0, deque([i])
        while q:
            u = q.popleft()
            for v in A[u]:
                if v not in col:
                    col[v] = 1 - col[u]; q.append(v)
                elif col[v] == col[u]:
                    bip = False
    b3 = n < 3 or m <= 3 * n - 6
    b4 = n < 3 or tri is not None or m <= 2 * n - 4
    k5 = next((c for c in combinations(ids, 5) if all(b in A[a] for a, b in combinations(c, 2))), None) if n <= 40 else None
    k33 = None
    if n <= 40:
        for tr in combinations(ids, 3):
            com = set.intersection(*(A[x] for x in tr)) - set(tr)
            if len(com) >= 3:
                k33 = (tr, sorted(com)[:3]); break
    bad = not b3 or not b4 or k5 or k33
    r = _Rec(edges)
    r.snap(f"n = {n}, m = {m}, components = {comps}")
    if k5:
        r.n = {i: "visited" for i in k5}; r.snap("พบ K₅ เป็น Subgraph → ไม่ Planar")
    if k33:
        r.n = {i: "visited" for i in k33[0] + tuple(k33[1])}; r.snap("พบ K₃,₃ เป็น Subgraph → ไม่ Planar")
    rows = [["m ≤ 3n−6", f"{m} ≤ {3 * n - 6}" if n >= 3 else "n<3", "✔" if b3 else "✘ ฝ่าฝืน"],
            ["m ≤ 2n−4 (ถ้าไม่มีสามเหลี่ยม)", f"{m} ≤ {2 * n - 4}" if tri is None and n >= 3 else "ข้าม (มีสามเหลี่ยม)", "✔" if b4 else "✘ ฝ่าฝืน"],
            ["Bipartite", "ใช่" if bip else "ไม่", ""], ["มีสามเหลี่ยม", "ไม่มี" if tri is None else ", ".join(nm(x) for x in tri), ""],
            ["K₅ เป็น Subgraph", "พบ" if k5 else "ไม่พบ", ""], ["K₃,₃ เป็น Subgraph", "พบ" if k33 else "ไม่พบ", ""]]
    r.snap("✘ ไม่ Planar แน่นอน" if bad else "ผ่านทุกเงื่อนไขที่ตรวจได้")
    sm = _hero("❌ ไม่ใช่ Planar Graph (พบข้อขัดแย้งที่พิสูจน์ได้)" if bad else f"⚠ ผ่านเงื่อนไขจำเป็นทั้งหมด — ยังสรุปว่า Planar ไม่ได้ (จำนวนหน้าถ้า Planar: f = m−n+{comps}+1 = {m - n + comps + 1})", "bad" if bad else "warn")
    sm += _tbl(["เงื่อนไข", "ค่า", "ผล"], rows)
    sm += '<div class="note">Kuratowski: Planar ⇔ ไม่มี Subdivision ของ K₅/K₃,₃ · Wagner: ⇔ ไม่มี K₅/K₃,₃ เป็น Minor · เวอร์ชันนี้ตรวจเฉพาะ Euler bound และ K₅/K₃,₃ แบบ Subgraph ตรง ๆ จึงยังไม่ตรวจ Subdivision/Minor, ไม่วาด Embedding และไม่สร้าง Dual Graph</div>'
    return _result("📊 สรุปผล Planarity", "planar", r.steps, sm)


# ---------- ข้อ 5, 6: Centrality + Laplacian Spectrum ----------
def _jacobi(A):
    n, A = len(A), [r[:] for r in A]
    for _ in range(60 * n * n):
        mx, pp, qq = 0.0, 0, 0
        for i in range(n):
            for j in range(i + 1, n):
                if abs(A[i][j]) > mx:
                    mx, pp, qq = abs(A[i][j]), i, j
        if mx < 1e-10:
            break
        th = (A[qq][qq] - A[pp][pp]) / (2 * A[pp][qq])
        t = (1 if th >= 0 else -1) / (abs(th) + math.sqrt(th * th + 1))
        c = 1 / math.sqrt(t * t + 1); sn = t * c
        for k in range(n):
            a, b = A[k][pp], A[k][qq]; A[k][pp], A[k][qq] = c * a - sn * b, sn * a + c * b
        for k in range(n):
            a, b = A[pp][k], A[qq][k]; A[pp][k], A[qq][k] = c * a - sn * b, sn * a + c * b
    return sorted(A[i][i] for i in range(n))


def _metrics(p):
    nodes, edges, names, d, ids, adj, s = _prep(p)
    _limit(len(ids), 60, "Centrality")
    nm, A, n = (lambda i: _name(names, i)), _simple(ids, edges), len(ids)
    close, btw = {}, {i: 0.0 for i in ids}
    for src in ids:  # Brandes (unweighted)
        dist, sig, pred, order, q = {src: 0}, {i: 0 for i in ids}, {i: [] for i in ids}, [], deque([src])
        sig[src] = 1
        while q:
            u = q.popleft(); order.append(u)
            for v in A[u]:
                if v not in dist:
                    dist[v] = dist[u] + 1; q.append(v)
                if dist[v] == dist[u] + 1:
                    sig[v] += sig[u]; pred[v].append(u)
        close[src] = (len(dist) - 1) / sum(dist.values()) if len(dist) > 1 else 0.0
        dep = {i: 0.0 for i in ids}
        for w in reversed(order):
            for u in pred[w]:
                dep[u] += sig[u] / sig[w] * (1 + dep[w])
            if w != src:
                btw[w] += dep[w] / 2
    def clus(i):
        k = len(A[i])
        return 0.0 if k < 2 else sum(1 for a, b in combinations(A[i], 2) if b in A[a]) / (k * (k - 1) / 2)
    cl = {i: clus(i) for i in ids}
    top = max(ids, key=lambda i: btw[i])
    r = _Rec(edges)
    r.nt = {i: f"{btw[i]:.1f}" for i in ids}
    r.snap(f"ป้ายบนจุด = Betweenness · จุดสำคัญที่สุดตามตัวกลาง: {nm(top)}", {top: "current"})
    sm = _hero(f"📈 Centrality · Clustering เฉลี่ย {sum(cl.values()) / n:.3f}")
    sm += _tbl(["จุด", "Degree", "Closeness", "Betweenness", "Clustering"], [[nm(i), len(A[i]), f"{close[i]:.3f}", f"{btw[i]:.2f}", f"{cl[i]:.3f}"] for i in ids])
    if n <= 30:
        ix = {v: k for k, v in enumerate(ids)}
        L = [[0.0] * n for _ in ids]
        for a in ids:
            L[ix[a]][ix[a]] = float(len(A[a]))
            for b in A[a]:
                L[ix[a]][ix[b]] = -1.0
        ev = _jacobi(L)
        zero = sum(1 for x in ev if abs(x) < 1e-6)
        sm += f"<h3>Laplacian Spectrum</h3><p>{_chips(f'{x:.4f}' for x in ev)}</p>"
        sm += f'<div class="cards">{_card("Components (จำนวน eigenvalue = 0)", zero)}{_card("Algebraic connectivity λ₂", f"{ev[1]:.4f}" if n > 1 else "—")}</div>'
    sm += '<div class="note">มองเป็นกราฟไม่มีทิศ ตัด Self-loop/เส้นขนาน · Closeness = (r−1)/Σระยะ ในส่วนที่เข้าถึงได้ · Betweenness ใช้ Brandes O(VE) · λ₂ > 0 ⇔ Connected</div>'
    return _result("📊 สรุปผล Centrality & Spectrum", "metrics", r.steps, sm)


# ---------- ข้อ 11: Vertex / Edge Connectivity ----------
def _maxflow(cap, s, t):
    f = 0
    while True:
        par, q = {s: None}, deque([s])
        while q and t not in par:
            u = q.popleft()
            for v, c in cap[u].items():
                if c > 0 and v not in par:
                    par[v] = u; q.append(v)
        if t not in par:
            return f
        v = t
        while par[v] is not None:
            u = par[v]; cap[u][v] -= 1; cap[v][u] = cap[v].get(u, 0) + 1; v = u
        f += 1


def _connect(p):
    nodes, edges, names, d, ids, adj, s = _prep(p, need_dir=False)
    _limit(len(ids), 20, "Connectivity κ/λ")
    nm, A, n = (lambda i: _name(names, i)), _simple(ids, edges), len(ids)
    if n < 2:
        raise ValueError("ต้องมีอย่างน้อย 2 จุด")
    lam = min(_maxflow({u: {v: 1 for v in A[u]} for u in ids}, ids[0], t) for t in ids[1:])
    complete = all(len(A[i]) == n - 1 for i in ids)
    kap, pair = n - 1, None
    if not complete:
        kap = n
        for a, b in combinations(ids, 2):
            if b in A[a]:
                continue
            cap = {(v, k): {} for v in ids for k in (0, 1)}
            for v in ids:
                cap[(v, 0)][(v, 1)] = n if v in (a, b) else 1
                for w in A[v]:
                    cap[(v, 1)][(w, 0)] = n
            f = _maxflow(cap, (a, 1), (b, 0))
            if f < kap:
                kap, pair = f, (a, b)
    delta = min(len(A[i]) for i in ids)
    r = _Rec(edges)
    r.snap(f"κ(G) = {kap}, λ(G) = {lam}, δ(G) = {delta}")
    if pair:
        r.n = {pair[0]: "current", pair[1]: "current"}; r.snap(f"คู่ {nm(pair[0])}, {nm(pair[1])} มีเส้นทางไม่ใช้จุดร่วมกันได้แค่ {kap} เส้น (Menger)")
    sm = _hero(f'🔗 κ(G) = <span class="bignum">{kap}</span> · λ(G) = <span class="bignum">{lam}</span>')
    sm += f'<div class="cards">{_card("Vertex Connectivity κ", kap)}{_card("Edge Connectivity λ", lam)}{_card("Min degree δ", delta)}</div>'
    sm += f'<div class="note">Whitney: κ ≤ λ ≤ δ → {kap} ≤ {lam} ≤ {delta} ✔ · Menger: จำนวนเส้นทางที่ไม่ใช้จุด (เส้น) ร่วมกันมากสุดระหว่างสองจุด = ขนาดการตัดจุด (เส้น) ที่น้อยสุด ซึ่งคำนวณด้วย Max Flow ที่ capacity 1 · มองเป็นกราฟ simple ไม่มีทิศ</div>'
    return _result("📊 สรุปผล Connectivity", "connect", r.steps, sm)


EXTRA = {"kirchhoff": _kirchhoff, "prufer": _prufer, "havel": _havel, "cover": _cover,
         "planar": _planar, "metrics": _metrics, "connect": _connect}
