#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Graph Theory Lab (Logistics & Urban Planning)
อัลกอริทึม: Dijkstra, Prim, Graph Coloring (Welsh-Powell), Network Flow (Edmonds-Karp)

วิธีรัน:  python app.py
- เปิดเบราว์เซอร์อัตโนมัติที่ http://localhost:8765
- มือถือ/แท็บเล็ตใน Wi-Fi เดียวกัน: เปิด URL แบบ LAN ที่แสดงใน Terminal
- จะสร้างไฟล์ graph_lab.html ไว้ข้าง ๆ (การรันอัลกอริทึมต้องเปิดผ่านเซิร์ฟเวอร์นี้)
- ใช้ภาพตกแต่ง city_header.png ซึ่งต้องอยู่โฟลเดอร์เดียวกัน
กด Ctrl+C เพื่อปิด
"""
import http.server
import json
import socket
import sys
import threading
import webbrowser
from pathlib import Path

from graph_algorithms import run_algorithm

HTML = r"""<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="theme-color" content="#1a1c2c">
<title>Graph Theory Lab</title>
<link rel="icon" type="image/png" href="web.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Pixelify+Sans:wght@400;700&family=Mitr:wght@400;500&display=swap" rel="stylesheet">
<style>
:root{
  --ink:#1a1c2c; --paper:#f4efe1; --navy:#333c57; --yellow:#ffcd75; --green:#a7f070; --dgreen:#38b764;
  --blue:#41a6f6; --dblue:#3b5dc9; --orange:#ef7d57; --red:#b13e53; --purple:#5d275d; --gray:#94b0c2; --cyan:#73eff7;
  --font:'Mitr','Tahoma',sans-serif;
}
*{box-sizing:border-box}
html,body{margin:0;height:100%;overflow:hidden;background:var(--navy);font-family:var(--font);color:var(--ink);
  -webkit-user-select:none;user-select:none;-webkit-tap-highlight-color:transparent;touch-action:manipulation;-webkit-text-size-adjust:100%}
#app{display:flex;flex-direction:column;height:100%;height:100dvh;
  padding:env(safe-area-inset-top) env(safe-area-inset-right) env(safe-area-inset-bottom) env(safe-area-inset-left)}
header{position:relative;isolation:isolate;padding-top:46px;background:var(--ink);border-bottom:4px solid #000;flex:0 0 auto}
header::before{content:"";position:absolute;z-index:-1;inset:0;height:46px;background:url('head.png') center center/cover no-repeat;image-rendering:pixelated;pointer-events:none}
.titlebar{position:absolute;inset:0 0 auto;z-index:1;height:46px;display:flex;align-items:center;gap:10px;padding:4px 12px}
.logo{position:relative;display:inline-flex;align-items:center;color:#ffb52e;background:linear-gradient(180deg,#9b5b27 0 20%,#633518 20% 100%);border:3px solid #241b20;border-radius:6px;padding:1px 9px 1px 32px;font-family:'Pixelify Sans','Mitr',sans-serif;font-weight:700;font-size:19px;letter-spacing:1px;text-shadow:2px 2px 0 var(--red),-1px -1px 0 #ffd783;white-space:nowrap;box-shadow:0 0 0 2px #8e5a27,3px 4px 0 #000,inset 0 2px 0 #ffd783}
.logo::before{content:"";position:absolute;inset:-4px;border:1px solid #63c74d;border-radius:8px;pointer-events:none}
.logo-cat{position:absolute;left:-6px;top:-9px;width:30px;height:30px;display:grid;place-items:center;font:20px/1 'Mitr','Tahoma',sans-serif;filter:drop-shadow(2px 2px 0 #000);z-index:2}
.sub{color:#241b20;background:#ffcd75;border:2px solid #281b1b;border-radius:3px;padding:0 6px;font-size:12px;font-weight:500;box-shadow:2px 3px 0 #000;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.scroll{position:relative;z-index:1;display:flex;gap:8px;overflow-x:auto;overflow-y:hidden;scrollbar-width:none;-ms-overflow-style:none;-webkit-overflow-scrolling:touch;padding:8px 10px 11px;background:#604025;border-top:3px solid #b17836}
.scroll::-webkit-scrollbar{display:none}
.sep{flex:0 0 3px;background:#566c86;margin:4px 2px}
.btn{font-family:var(--font);font-size:15px;min-height:44px;min-width:44px;padding:6px 12px;background:#f4dfb5;color:var(--ink);
  border:3px solid #30201b;box-shadow:inset 2px 2px 0 rgba(255,255,255,.72),inset -2px -2px 0 rgba(111,75,43,.26),4px 4px 0 #000;
  cursor:pointer;white-space:nowrap;display:inline-flex;align-items:center;justify-content:center;gap:6px;border-radius:5px;text-decoration:none;
  flex:0 0 auto;transition:transform .08s steps(2,end),box-shadow .08s steps(2,end)}
.btn:hover:not(:disabled){transform:translate(-1px,-1px);box-shadow:inset 2px 2px 0 rgba(255,255,255,.72),inset -2px -2px 0 rgba(111,75,43,.26),5px 5px 0 #000}
.btn:active:not(:disabled){transform:translate(4px,4px);box-shadow:inset 2px 2px 0 rgba(255,255,255,.72),inset -2px -2px 0 rgba(111,75,43,.26),0 0 0 #000}
.btn:focus-visible{outline:3px solid var(--blue);outline-offset:2px}
.btn:disabled{opacity:.55;cursor:not-allowed}
.btn.on{background:var(--yellow)}
.btn.primary{background:var(--green)}
.btn.danger{background:var(--orange)}
.btn.mini{min-height:34px;font-size:13px;padding:2px 8px}
.tbtn{flex-direction:column;gap:0;font-size:12px;min-width:66px;padding:3px 8px;line-height:1.2}
.tbtn .ic{font-size:20px;line-height:1.15}
@media (min-width:1400px){
  #toolbar::after{content:"";align-self:center;flex:0 0 62px;height:58px;margin-left:auto;background:url('mascot_clean.png') center/contain no-repeat;filter:drop-shadow(2px 2px 0 #241b20);pointer-events:none}
}
#hint{background:var(--yellow);border-bottom:3px solid var(--ink);padding:6px 12px;font-size:14px;line-height:1.35;flex:0 0 auto}
main{flex:1;display:flex;flex-direction:column;min-height:0}
#stage{flex:1;position:relative;min-height:150px;overflow:hidden;background:var(--paper);border:5px solid #6b4727;box-shadow:inset 0 0 0 2px #d3a45c}
#cv{position:absolute;inset:0;touch-action:none;display:block;cursor:crosshair}
#badge{position:absolute;left:8px;top:8px;background:#fff;border:3px solid var(--ink);box-shadow:3px 3px 0 var(--ink);padding:4px 8px;font-size:13px;pointer-events:none}
#zoom{position:absolute;right:10px;bottom:10px;display:flex;flex-direction:column;gap:8px}
#zoom .btn{font-size:20px;padding:0;width:46px}
#dock{flex:0 0 auto;max-height:48vh;overflow-y:auto;background:#e8e4d8;border-top:4px solid #6b4727;padding:4px 10px 10px;-webkit-overflow-scrolling:touch}
@media (min-width:900px){
  main{flex-direction:row}
  #dock{width:390px;max-height:none;border-top:none;border-left:4px solid #6b4727}
  .scroll{padding:4px 10px 6px}
  .tbtn{min-height:36px;font-size:11px}
  .tbtn .ic{font-size:16px}
  .logo{font-size:15px;letter-spacing:.5px;padding:1px 7px 1px 27px;border-width:2px;box-shadow:0 0 0 2px #8e5a27,2px 3px 0 #000,inset 0 2px 0 #ffd783}
  .logo-cat{left:-5px;top:-7px;width:25px;height:25px;font-size:17px}
  .sub{font-size:10px}
}
.dockhead{display:flex;align-items:flex-start;gap:6px;padding-top:6px}
.dockhead #dockToggle{flex:0 0 auto;margin-top:2px}
.tabgrid{flex:1;display:grid;grid-template-columns:repeat(auto-fill,minmax(100px,1fr));gap:8px;padding:2px 4px 8px 0}
.btn.tab{font-size:14px;min-width:0;width:100%;padding:6px 6px;white-space:normal;line-height:1.2;text-align:center}

.row{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin:8px 0}
.desc{background:#fff9e8;border:3px solid #6b4727;padding:8px 10px;font-size:14px;line-height:1.5;box-shadow:3px 3px 0 #241b20}
.desc .app{display:block;margin-top:4px;color:#257179;font-weight:bold}
label.sel{display:flex;flex-direction:column;font-size:13px;flex:1;min-width:130px;gap:3px}
select{font-family:var(--font);font-size:15px;min-height:44px;border:3px solid var(--ink);background:#fff;padding:4px;border-radius:0;box-shadow:3px 3px 0 var(--ink);color:var(--ink);width:100%}
.bigbtn{width:100%;font-size:17px;min-height:50px}
.player .btn{flex:1;font-size:18px;padding:4px;min-width:44px}
input[type=range]{flex:1;accent-color:var(--red);height:34px;min-width:120px}
#stepLbl{font-size:13px;min-width:80px;text-align:right}
.speed .btn{flex:1;font-size:14px}
.stepbox{background:var(--ink);color:var(--green);border:3px solid #000;padding:10px 12px;min-height:72px;font-size:15px;line-height:1.55;box-shadow:inset 0 0 0 3px var(--navy);-webkit-user-select:text;user-select:text}
.legend{font-size:12px;display:flex;flex-wrap:wrap;gap:6px 12px;margin-top:6px}
.lg{display:inline-flex;align-items:center;gap:5px}
.lg i{display:inline-block;width:16px;height:16px;border:2px solid var(--ink)}
.lg i.ln{height:6px;width:24px;border:none}
.lg i.dash{height:0;width:24px;border:none;border-top:5px dashed var(--red)}
#quick{font-size:13px;background:#fff;border:2px solid var(--ink);padding:4px 8px}
#dock.collapsed .collapsible{display:none}
@keyframes blink{50%{background:var(--yellow)}}
.glow{animation:blink .9s steps(2) infinite}
/* modal */
#modal{position:fixed;inset:0;background:rgba(26,28,44,.65);display:flex;align-items:center;justify-content:center;z-index:50;
  padding:calc(env(safe-area-inset-top) + 10px) calc(env(safe-area-inset-right) + 10px) calc(env(safe-area-inset-bottom) + 10px) calc(env(safe-area-inset-left) + 10px)}
#modal.hidden{display:none}
.win{background:#fff;border:4px solid var(--ink);box-shadow:8px 8px 0 #000;max-width:780px;width:100%;max-height:100%;display:flex;flex-direction:column}
.winbar{background:var(--dblue);color:#fff;display:flex;justify-content:space-between;align-items:center;padding:4px 4px 4px 12px;border-bottom:4px solid var(--ink);font-weight:bold;gap:8px}
.winbar .btn{min-height:38px;min-width:38px;padding:0 8px;background:var(--orange)}
#mbody{overflow:auto;padding:14px;-webkit-user-select:text;user-select:text;line-height:1.55;-webkit-overflow-scrolling:touch}
#mbody h3{margin:16px 0 6px;font-size:17px;border-bottom:3px solid var(--ink);display:inline-block}
.hero{background:var(--green);border:3px solid var(--ink);box-shadow:4px 4px 0 var(--ink);padding:12px 14px;font-size:17px;margin-bottom:12px}
.hero.warn{background:var(--yellow)}
.hero.bad{background:var(--orange)}
.bignum{font-size:30px;font-weight:bold;display:inline-block;padding:0 6px;background:#fff;border:3px solid var(--ink);margin-left:4px}
.route{margin-top:8px;line-height:2.1}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px;margin:10px 0}
.card{border:3px solid var(--ink);box-shadow:3px 3px 0 var(--ink);padding:8px 10px;background:#fffbe6}
.card .k{font-size:12px;opacity:.75}
.card .v{font-size:22px;font-weight:bold}
.tw{overflow:auto;max-width:100%}
.tbl{border-collapse:collapse;margin:6px 0;font-size:14px}
.tbl th,.tbl td{border:2px solid var(--ink);padding:4px 9px;text-align:center;white-space:nowrap}
.tbl th{background:var(--yellow)}
.tbl td.l{text-align:left;white-space:normal}
.chip{display:inline-block;border:2px solid var(--ink);padding:1px 8px;margin:2px;background:#fff;box-shadow:2px 2px 0 var(--ink)}
.sw{display:inline-block;width:20px;height:20px;border:3px solid var(--ink);vertical-align:middle;margin-right:6px}
.grp{border:3px solid var(--ink);padding:8px;margin:8px 0;background:#fff;box-shadow:3px 3px 0 var(--ink)}
.grp .gh{display:flex;align-items:center;justify-content:space-between;gap:8px;font-weight:bold;margin-bottom:4px}
.note{background:#fff7d6;border:3px dashed var(--ink);padding:8px 10px;margin-top:12px}
.preview{max-width:100%;border:3px solid var(--ink);display:block;margin-top:10px;-webkit-touch-callout:default;-webkit-user-select:auto;user-select:auto}
.pgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}
.pcard{border:3px solid var(--ink);box-shadow:4px 4px 0 var(--ink);padding:10px;background:#fffbe6;display:flex;flex-direction:column;gap:8px}
.pcard b{font-size:16px}
ol.steps li{margin-bottom:6px}
#toast{position:fixed;left:50%;top:calc(env(safe-area-inset-top) + 120px);transform:translateX(-50%);background:var(--ink);color:#fff;
  padding:8px 14px;border:3px solid #fff;box-shadow:4px 4px 0 #000;z-index:60;opacity:0;transition:opacity .2s;pointer-events:none;max-width:90vw;text-align:center;font-size:14px}
</style>
</head>
<body>
<div id="app">
  <header>
    <div class="titlebar"><span class="logo"><span class="logo-cat" aria-hidden="true">🐱</span>GRAPH LAB</span><span class="sub">Logistics &amp; Urban Planning</span></div>
    <div class="scroll" id="toolbar">
      <button type="button" class="btn tbtn on" data-tool="move"><span class="ic">✋</span>ย้าย/เลื่อน</button>
      <button type="button" class="btn tbtn" data-tool="node"><span class="ic">⬛</span>เพิ่มจุด</button>
      <button type="button" class="btn tbtn" data-tool="edge"><span class="ic">🔗</span>เชื่อมเส้น</button>
      <button type="button" class="btn tbtn" data-tool="edit"><span class="ic">✏️</span>แก้ชื่อ/น้ำหนัก</button>
      <button type="button" class="btn tbtn" data-tool="bend"><span class="ic">〰️</span>ดัดเส้น</button>
      <button type="button" class="btn tbtn" data-tool="del"><span class="ic">🗑️</span>ลบ</button>
      <span class="sep"></span>
      <button type="button" class="btn tbtn" id="aDir"><span class="ic" id="dirIc">—</span><span id="dirTxt">ไม่มีทิศ</span></button>
      <button type="button" class="btn tbtn" id="aUndo"><span class="ic">↶</span>Undo</button>
      <button type="button" class="btn tbtn" id="aRedo" disabled><span class="ic">↷</span>Redo</button>
      <button type="button" class="btn tbtn" id="aStraight"><span class="ic">📏</span>เส้นตรงหมด</button>
      <button type="button" class="btn tbtn" id="aPreset"><span class="ic">📂</span>ตัวอย่าง</button>
      <button type="button" class="btn tbtn" id="aPNG"><span class="ic">🖼️</span>PNG</button>
      <button type="button" class="btn tbtn" id="aClear"><span class="ic">🧹</span>ล้างกราฟ</button>
      <button type="button" class="btn tbtn" id="aHelp"><span class="ic">❓</span>วิธีใช้</button>
    </div>
  </header>
  <div id="hint"></div>
  <main>
    <div id="stage">
      <canvas id="cv"></canvas>
      <div id="badge"></div>
      <div id="zoom">
        <button type="button" class="btn" id="zIn" title="ซูมเข้า">+</button>
        <button type="button" class="btn" id="zOut" title="ซูมออก">−</button>
        <button type="button" class="btn" id="zFit" title="จัดกึ่งกลาง">⌖</button>
      </div>
    </div>
    <aside id="dock">
      <div class="dockhead">
        <div class="tabgrid" id="tabs"></div>
        <button type="button" class="btn mini" id="dockToggle" title="ย่อ/ขยายแผง">▾</button>
      </div>
      <div id="algoDesc" class="desc collapsible"></div>
      <div class="row collapsible" id="selRow">
        <label class="sel" id="lblS"><span id="lblSText">ต้นทาง</span><select id="selS"></select></label>
        <label class="sel" id="lblT"><span id="lblTText">ปลายทาง</span><select id="selT"></select></label>
      </div>
      <div class="row"><button type="button" class="btn primary bigbtn" id="runBtn">▶ เริ่มรัน</button></div>
      <div id="player" class="player">
        <div class="row">
          <button type="button" class="btn" id="bFirst" title="ขั้นแรก">⏮</button>
          <button type="button" class="btn" id="bPrev" title="ย้อน">◀</button>
          <button type="button" class="btn" id="bPlay" title="เล่นอัตโนมัติ">▶</button>
          <button type="button" class="btn" id="bNext" title="ถัดไป">▶|</button>
          <button type="button" class="btn" id="bLast" title="ขั้นสุดท้าย">⏭</button>
        </div>
        <div class="row"><input type="range" id="slider" min="0" max="0" value="0"><span id="stepLbl">ขั้น 0/0</span></div>
        <div class="row speed">
          <button type="button" class="btn" data-sp="0.5">0.5×</button>
          <button type="button" class="btn on" data-sp="1">1×</button>
          <button type="button" class="btn" data-sp="2">2×</button>
          <button type="button" class="btn" data-sp="4">4×</button>
        </div>
        <div id="stepText" class="stepbox"></div>
        <div class="row">
          <button type="button" class="btn" id="sumBtn" style="flex:1">📊 สรุปผล</button>
          <button type="button" class="btn danger" id="clearRunBtn" style="flex:1">✖ ล้างผล</button>
        </div>
      </div>
      <div id="legend" class="legend collapsible"></div>
      <div class="row collapsible"><div id="quick"></div></div>
    </aside>
  </main>
</div>
<div id="modal" class="hidden"><div class="win"><div class="winbar"><span id="mtitle"></span><button type="button" class="btn" id="mclose">✖</button></div><div id="mbody"></div></div></div>
<div id="toast"></div>

<script>
(() => {
'use strict';
const $ = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];
const cv = $('#cv'), ctx = cv.getContext('2d');
const FONT = "'Mitr',Tahoma,sans-serif";
const INK = '#1a1c2c', PAPER = '#f4efe1';
const PALETTE = ['#ef7d57','#41a6f6','#a7f070','#ffcd75','#f4a6d7','#73eff7','#b13e53','#38b764','#c28a4a','#94b0c2','#5d275d','#3b5dc9','#257179','#d4a5ff','#566c86'];
const NODE_FILL = {current:'#ffcd75', consider:'#ef7d57', visited:'#a7f070', path:'#38b764', inS:'#73eff7'};
const EDGE_STY = {
  base:{c:INK,w:3}, consider:{c:'#ef7d57',w:6,hl:1}, soft:{c:'#38b764',w:4}, tree:{c:'#38b764',w:6,hl:1},
  path:{c:'#38b764',w:8,hl:1}, reject:{c:'#94b0c2',w:3,dash:1}, cut:{c:'#b13e53',w:7,dash:1,hl:1},
  flow:{c:'#3b5dc9',w:5}, sat:{c:'#5d275d',w:6,hl:1}
};
const NR = 22, MINS = 0.2, MAXS = 4, EPS = 1e-9, LS_KEY = 'graphTheoryLab.v1', UNDO_MAX = 70;
const IOS = /iPad|iPhone|iPod/.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);

function emptyGraph(){ return {nodes:[], edges:[], directed:false, nextId:1, nextEid:1, source:null, sink:null, colorNames:[]}; }
let G = emptyGraph(), view = {x:0, y:0, s:1}, W = 300, H = 300, DPR = 1;
let tool = 'move', selNode = null, undoStack = [], redoStack = [], algo = 'dijkstra';
let run = null, stepIdx = 0, playing = false, timer = null, speed = 1;
const pointers = new Map(); let drag = null, pinch = null, lastTap = {t:0, key:''};
let hoverNode = null, hoverEdge = null, hoverStarted = 0, hoverFrame = 0;
let edgePreview = null;

/* ---------- utils ---------- */
const clamp = (v,a,b) => Math.max(a, Math.min(b, v));
const fmt = x => x === Infinity ? '∞' : (Number.isInteger(x) ? String(x) : String(+(+x).toFixed(3)));
const esc = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const nodeById = id => G.nodes.find(n => n.id === id);
const nm = id => { const n = nodeById(id); return n ? n.label : '?'; };
const edgeName = e => `${nm(e.u)} ${G.directed ? '→' : '–'} ${nm(e.v)}`;
const cName = i => G.colorNames[i] || `สี ${i+1}`;
const cmpNum = (a,b) => a === b ? 0 : (a < b ? -1 : 1);
const card = (k,v) => `<div class="card"><div class="k">${k}</div><div class="v">${v}</div></div>`;
const appNote = t => `<div class="note">💡 <b>การประยุกต์:</b> ${t}</div>`;
function textOn(hex){ const r=parseInt(hex.slice(1,3),16), g=parseInt(hex.slice(3,5),16), b=parseInt(hex.slice(5,7),16); return (0.299*r+0.587*g+0.114*b) < 140 ? '#ffffff' : INK; }
let toastT;
function toast(msg){ const t=$('#toast'); t.textContent=msg; t.style.opacity=1; clearTimeout(toastT); toastT=setTimeout(()=>t.style.opacity=0, 2000); }
function openModal(title, html){ $('#mtitle').textContent=title; $('#mbody').innerHTML=html; $('#modal').classList.remove('hidden'); $('#mbody').scrollTop=0; }
function closeModal(){ $('#modal').classList.add('hidden'); }
function alertBox(msg){ openModal('⚠ แจ้งเตือน', `<div class="hero warn">${msg}</div>`); }

/* ---------- save / undo ---------- */
function sanitize(g){
  g = Object.assign(emptyGraph(), g);
  g.nodes = (g.nodes||[]).filter(n => n && typeof n.id === 'number');
  g.nodes.forEach(n => { if(n.label == null) n.label = 'v'+n.id; if(n.color === undefined) n.color = null; });
  const ids = new Set(g.nodes.map(n => n.id));
  g.edges = (g.edges||[]).filter(e => ids.has(e.u) && ids.has(e.v) && e.u !== e.v);
  g.edges.forEach(e => { e.w = Number(e.w)||0; e.curve = e.curve||0; });
  g.nextId = Math.max(g.nextId||1, 1, ...g.nodes.map(n => n.id+1));
  g.nextEid = Math.max(g.nextEid||1, 1, ...g.edges.map(e => e.id+1));
  if(!ids.has(g.source)) g.source = null;
  if(!ids.has(g.sink)) g.sink = null;
  if(!Array.isArray(g.colorNames)) g.colorNames = [];
  return g;
}
function save(){ try{ localStorage.setItem(LS_KEY, JSON.stringify({G, view, tab:algo})); }catch(_){} }
function load(){
  try{ const d = JSON.parse(localStorage.getItem(LS_KEY)); if(d && d.G){ G = sanitize(d.G); if(d.view && isFinite(d.view.s)) view = d.view; return d.tab || 'dijkstra'; } }catch(_){}
  return null;
}
function updateHistoryButtons(){
  $('#aUndo').disabled = !undoStack.length;
  $('#aRedo').disabled = !redoStack.length;
}
function pushUndo(){
  undoStack.push(JSON.stringify(G));
  if(undoStack.length > UNDO_MAX) undoStack.shift();
  redoStack = [];
  updateHistoryButtons();
}
function undo(){
  if(!undoStack.length) return toast('ไม่มีขั้นให้ย้อนแล้ว');
  redoStack.push(JSON.stringify(G));
  if(redoStack.length > UNDO_MAX) redoStack.shift();
  G = sanitize(JSON.parse(undoStack.pop())); selNode = null; clearRun(); afterChange();
  toast(`↶ ย้อนแล้ว (ไปข้างหน้าได้อีก ${redoStack.length} ขั้น)`);
}
function redo(){
  if(!redoStack.length) return toast('ไม่มีขั้นให้ไปข้างหน้าแล้ว');
  undoStack.push(JSON.stringify(G));
  if(undoStack.length > UNDO_MAX) undoStack.shift();
  G = sanitize(JSON.parse(redoStack.pop())); selNode = null; clearRun(); afterChange();
  toast(`↷ ไปข้างหน้าแล้ว (ไปข้างหน้าได้อีก ${redoStack.length} ขั้น)`);
}
function commit(fn, invalidate = true){ pushUndo(); fn(); if(invalidate) clearRun(); afterChange(); }
function afterChange(){ save(); refreshSelects(); updateBadge(); updateHint(); updateHistoryButtons(); draw(); }

/* ---------- geometry ---------- */
function toWorld(sx, sy){ return {x:(sx-view.x)/view.s, y:(sy-view.y)/view.s}; }
function edgeGeom(e){
  const a = nodeById(e.u), b = nodeById(e.v); if(!a || !b || a === b) return null;
  const mx=(a.x+b.x)/2, my=(a.y+b.y)/2, dx=b.x-a.x, dy=b.y-a.y, L=Math.hypot(dx,dy)||1;
  const nx=-dy/L, ny=dx/L, c=e.curve||0;
  return {a, b, mx, my, nx, ny, cx:mx+nx*c*2, cy:my+ny*c*2, px:mx+nx*c, py:my+ny*c};
}
function bez(g, t){ const u=1-t; return {x:u*u*g.a.x+2*u*t*g.cx+t*t*g.b.x, y:u*u*g.a.y+2*u*t*g.cy+t*t*g.b.y}; }
function distSeg(p, a, b){ const dx=b.x-a.x, dy=b.y-a.y, L=dx*dx+dy*dy; let t=L?((p.x-a.x)*dx+(p.y-a.y)*dy)/L:0; t=clamp(t,0,1); return Math.hypot(p.x-(a.x+t*dx), p.y-(a.y+t*dy)); }
function hitNode(w){ const r=NR+6/view.s; for(let i=G.nodes.length-1;i>=0;i--){ const n=G.nodes[i]; if(Math.abs(w.x-n.x)<=r && Math.abs(w.y-n.y)<=r) return n; } return null; }
function hitEdge(w){
  const tol = 12/view.s; let best=null, bd=tol;
  for(const e of G.edges){
    const g = edgeGeom(e); if(!g) continue;
    const dl = Math.hypot(w.x-g.px, w.y-g.py); if(dl < 16/view.s && dl < bd){ bd=dl; best=e; }
    let prev = bez(g,0);
    for(let i=1;i<=24;i++){ const p=bez(g,i/24); const d=distSeg(w,prev,p); if(d<bd){ bd=d; best=e; } prev=p; }
  }
  return best;
}

/* ---------- rendering ---------- */
function resize(){
  const r = $('#stage').getBoundingClientRect(); DPR = window.devicePixelRatio || 1;
  W = Math.max(1, r.width); H = Math.max(1, r.height);
  cv.width = Math.round(W*DPR); cv.height = Math.round(H*DPR); cv.style.width = W+'px'; cv.style.height = H+'px';
  draw();
}
function currentStep(){ return run ? run.steps[stepIdx] : null; }
function draw(){ ctx.setTransform(DPR,0,0,DPR,0,0); renderScene(ctx, W, H, view); }
const CURSOR_STYLES = {
  move: 'grab',
  node: 'crosshair',
  edge: 'crosshair',
  edit: 'text',
  bend: 'move',
  del: 'not-allowed'
};
function updateCanvasCursor(){
  cv.style.cursor = CURSOR_STYLES[tool] || 'default';
}
function setHover(node, edge){
  const nodeId = node ? node.id : null, edgeId = edge ? edge.id : null;
  updateCanvasCursor();
  if(nodeId === hoverNode && edgeId === hoverEdge) return;
  hoverNode = nodeId; hoverEdge = edgeId; hoverStarted = performance.now();
  updateCanvasCursor();
  draw();
  if((node || edge) && !hoverFrame) hoverFrame = requestAnimationFrame(animateHover);
}
function animateHover(){
  if(hoverNode == null && hoverEdge == null){ hoverFrame = 0; return; }
  draw(); hoverFrame = requestAnimationFrame(animateHover);
}
function renderScene(c, w, h, v){
  c.fillStyle = PAPER; c.fillRect(0,0,w,h);
  const gs = 40*v.s;
  if(gs > 12){
    c.fillStyle = '#d6cdb5';
    const ox = ((v.x%gs)+gs)%gs, oy = ((v.y%gs)+gs)%gs;
    for(let x=ox;x<w;x+=gs) for(let y=oy;y<h;y+=gs) c.fillRect(Math.round(x)-1, Math.round(y)-1, 3, 3);
  }
  c.save(); c.translate(v.x, v.y); c.scale(v.s, v.s);
  const st = currentStep(), showW = !['color','dsatur'].includes(algo);
  for(const e of G.edges) drawEdge(c, e, st, showW);
  if(tool === 'edge' && selNode != null && edgePreview) drawEdgePreview(c, selNode, edgePreview);
  for(const n of G.nodes) drawNode(c, n, st);
  c.restore();
}
function drawEdgePreview(c, sourceId, target){
  const source = nodeById(sourceId); if(!source) return;
  const dx = target.x-source.x, dy = target.y-source.y, length = Math.hypot(dx,dy);
  if(length < 1) return;
  const ux = dx/length, uy = dy/length, endNode = hitNode(target);
  const start = {x:source.x+ux*NR, y:source.y+uy*NR};
  const endDistance = endNode && endNode.id !== sourceId ? Math.max(NR, length-NR) : length;
  const end = {x:source.x+ux*endDistance, y:source.y+uy*endDistance};
  c.save(); c.beginPath(); c.moveTo(start.x,start.y); c.lineTo(end.x,end.y);
  c.setLineDash([8,6]); c.lineWidth=4; c.strokeStyle='#ffcd75'; c.lineCap='round';
  c.shadowColor=INK; c.shadowBlur=2; c.stroke(); c.restore();
}
function pill(c, x, y, text, bg, fg, border){
  c.font = `bold 13px ${FONT}`;
  const tw = c.measureText(text).width, pw = tw+12, ph = 20;
  c.fillStyle = INK; c.fillRect(x-pw/2+2, y-ph/2+2, pw, ph);
  c.fillStyle = bg; c.fillRect(x-pw/2, y-ph/2, pw, ph);
  c.lineWidth = 2; c.strokeStyle = border || INK; c.strokeRect(x-pw/2, y-ph/2, pw, ph);
  c.fillStyle = fg; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText(text, x, y+1);
}
function tag(c, x, y, t, bg){
  c.fillStyle = INK; c.fillRect(x-9, y-9, 18, 18);
  c.fillStyle = bg; c.fillRect(x-7, y-7, 14, 14);
  c.fillStyle = '#fff'; c.font = `bold 11px ${FONT}`; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText(t, x, y+1);
}
function roundedBox(c, x, y, size, radius=6){
  const r = Math.min(radius, size/2);
  c.beginPath(); c.moveTo(x+r,y); c.lineTo(x+size-r,y); c.quadraticCurveTo(x+size,y,x+size,y+r);
  c.lineTo(x+size,y+size-r); c.quadraticCurveTo(x+size,y+size,x+size-r,y+size);
  c.lineTo(x+r,y+size); c.quadraticCurveTo(x,y+size,x,y+size-r);
  c.lineTo(x,y+r); c.quadraticCurveTo(x,y,x+r,y); c.closePath();
}
function drawEdge(c, e, st, showW){
  const g = edgeGeom(e); if(!g) return;
  const hovered = hoverEdge === e.id, key = st && st.edge ? st.edge[e.id] : null;
  let S = EDGE_STY[key] || EDGE_STY.base; const efc = st && st.efill ? st.efill[e.id] : null; if(efc != null) S = {...S, c:PALETTE[efc % PALETTE.length], w:7};
  if(hovered){
    const wobble = Math.sin((performance.now()-hoverStarted)/75)*2.5;
    g.cx += g.nx*wobble; g.cy += g.ny*wobble; g.px += g.nx*wobble/2; g.py += g.ny*wobble/2;
  }
  const path = () => { c.beginPath(); c.moveTo(g.a.x,g.a.y); c.quadraticCurveTo(g.cx,g.cy,g.b.x,g.b.y); };
  c.save(); c.lineCap = 'round'; c.lineJoin = 'round';
  if(S.hl){ c.setLineDash([]); c.strokeStyle = INK; c.lineWidth = S.w+4; path(); c.stroke(); }
  c.setLineDash(S.dash ? [12,8] : []); c.strokeStyle = hovered ? '#ef7d57' : S.c; c.lineWidth = S.w+(hovered?3:0); path(); c.stroke(); c.setLineDash([]);
  if(G.directed){
    let t1 = 1;
    for(let i=0;i<=60;i++){ const t=1-i/60, p=bez(g,t); if(Math.abs(p.x-g.b.x)>NR+4 || Math.abs(p.y-g.b.y)>NR+4){ t1=t; break; } }
    const tip = bez(g,t1);
    const dx = 2*(1-t1)*(g.cx-g.a.x)+2*t1*(g.b.x-g.cx), dy = 2*(1-t1)*(g.cy-g.a.y)+2*t1*(g.b.y-g.cy);
    const L = Math.hypot(dx,dy)||1, ux = dx/L, uy = dy/L, sz = 10+S.w;
    c.beginPath(); c.moveTo(tip.x, tip.y);
    c.lineTo(tip.x-ux*sz-uy*sz*0.55, tip.y-uy*sz+ux*sz*0.55);
    c.lineTo(tip.x-ux*sz+uy*sz*0.55, tip.y-uy*sz-ux*sz*0.55); c.closePath();
    c.fillStyle = S.c; c.fill(); c.lineWidth = 2; c.strokeStyle = INK; c.stroke();
  }
  const txt = st && st.etext ? st.etext[e.id] : (showW ? fmt(e.w) : null);
  if(txt != null) pill(c, g.px, g.py, txt, '#ffffff', INK, S.hl ? S.c : INK);
  c.restore();
}
function drawNode(c, n, st){
  const hovered = hoverNode === n.id;
  if(hovered){
    const phase = (performance.now()-hoverStarted)/75;
    c.save(); c.translate(n.x,n.y); c.rotate(Math.sin(phase)*0.035);
    const scale = 1.04+Math.sin(phase*2)*0.025; c.scale(scale,scale); c.translate(-n.x,-n.y);
  }
  const sty = st && st.node ? st.node[n.id] : null, r = NR;
  let fill = '#8bea3c';
  if(st && st.fill){ if(st.fill[n.id] != null) fill = PALETTE[st.fill[n.id] % PALETTE.length]; }
  else if(!st && n.color != null) fill = PALETTE[n.color % PALETTE.length];
  if(!(st && st.fill) && sty && NODE_FILL[sty]) fill = NODE_FILL[sty];
  let ring = null; if(sty === 'current') ring = '#b13e53'; if(selNode === n.id) ring = '#41a6f6';
  if(ring){ roundedBox(c, n.x-r-8, n.y-r-8, 2*r+16, 10); c.fillStyle = ring; c.fill(); c.strokeStyle = INK; c.lineWidth = 2; c.stroke(); }
  roundedBox(c, n.x-r+5, n.y-r+5, 2*r, 9); c.fillStyle = 'rgba(26,28,44,0.9)'; c.fill();
  roundedBox(c, n.x-r, n.y-r, 2*r, 9); c.fillStyle = fill; c.fill(); c.lineWidth = 3; c.strokeStyle = INK; c.stroke();
  c.fillStyle = 'rgba(255,255,255,0.85)'; c.fillRect(n.x-r+5, n.y-r+5, 7, 4); c.fillRect(n.x-r+5, n.y-r+9, 4, 5);
  c.fillStyle = 'rgba(26,28,44,0.18)'; c.fillRect(n.x+r-6, n.y-r+8, 3, 2*r-16); c.fillRect(n.x-r+8, n.y+r-6, 2*r-16, 3);
  const short = n.label.length <= 4;
  const label = short ? n.label : 'v'+n.id, numericLabel = /^\d+$/.test(label);
  c.fillStyle = textOn(fill); c.font = `bold ${numericLabel?16:(short?14:12)}px ${numericLabel?"Arial,Tahoma,sans-serif":FONT}`; c.textAlign = 'center'; c.textBaseline = 'middle';
  c.fillText(label, n.x, n.y+1);
  if(!short) pill(c, n.x, n.y+r+17, n.label, '#fffbe6', INK, INK);
  const T = TABS[algo];
  if(T && T.s && G.source === n.id) tag(c, n.x-r, n.y+r, 'S', '#38b764');
  if(T && T.t && G.sink === n.id) tag(c, n.x+r, n.y+r, 'T', '#b13e53');
  if(st && st.ntext && st.ntext[n.id] != null) pill(c, n.x, n.y-r-17, st.ntext[n.id], '#ffcd75', INK, INK);
  if(hovered) c.restore();
}

/* ---------- view ---------- */
function zoomAt(sx, sy, f){
  const ns = clamp(view.s*f, MINS, MAXS); f = ns/view.s;
  view.x = sx-(sx-view.x)*f; view.y = sy-(sy-view.y)*f; view.s = ns; draw(); saveSoon();
}
let saveT; function saveSoon(){ clearTimeout(saveT); saveT = setTimeout(save, 400); }
function fitView(){
  if(!G.nodes.length){ view = {x:W/2, y:H/2, s:1}; draw(); return; }
  let x0=Infinity, y0=Infinity, x1=-Infinity, y1=-Infinity;
  G.nodes.forEach(n => { x0=Math.min(x0,n.x); y0=Math.min(y0,n.y); x1=Math.max(x1,n.x); y1=Math.max(y1,n.y); });
  x0-=80; x1+=80; y0-=60; y1+=70;
  const s = clamp(Math.min(W/(x1-x0), H/(y1-y0)), MINS, 1.6);
  view.s = s; view.x = W/2-(x0+x1)/2*s; view.y = H/2-(y0+y1)/2*s; draw(); save();
}

/* ---------- pointer / touch ---------- */
function ptr(e){ const r = cv.getBoundingClientRect(); return {x:e.clientX-r.left, y:e.clientY-r.top}; }
cv.addEventListener('pointerdown', e => {
  e.preventDefault();
  setHover(null, null);
  try{ cv.setPointerCapture(e.pointerId); }catch(_){}
  const p = ptr(e); pointers.set(e.pointerId, p);
  if(pointers.size === 2){
    const [a,b] = [...pointers.values()];
    pinch = {d:Math.hypot(a.x-b.x,a.y-b.y)||1, cx:(a.x+b.x)/2, cy:(a.y+b.y)/2, v:{...view}};
    if(drag && drag.undo) save();
    drag = null; return;
  }
  if(pointers.size > 2) return;
  const w = toWorld(p.x, p.y), n = hitNode(w), ed = n ? null : hitEdge(w);
  let type = 'tap';
  if(n && (tool === 'move' || tool === 'node')) type = 'node';
  else if(ed && tool === 'bend') type = 'bend';
  else if(!n && !ed) type = 'pan';
  drag = {type, n, ed, w, sx:p.x, sy:p.y, lx:p.x, ly:p.y, moved:false, undo:false, offX:n?n.x-w.x:0, offY:n?n.y-w.y:0};
});
cv.addEventListener('pointermove', e => {
  if(!pointers.has(e.pointerId)){
    if(e.pointerType !== 'touch'){
      const p = ptr(e), w = toWorld(p.x, p.y), n = hitNode(w), ed = n ? null : hitEdge(w);
      if(tool === 'edge' && selNode != null){ edgePreview = w; draw(); }
      setHover(n, ed);
    }
    return;
  }
  const p = ptr(e); pointers.set(e.pointerId, p);
  if(pinch && pointers.size >= 2){
    const [a,b] = [...pointers.values()];
    const d = Math.hypot(a.x-b.x,a.y-b.y)||1, cx = (a.x+b.x)/2, cy = (a.y+b.y)/2;
    const ns = clamp(pinch.v.s*d/pinch.d, MINS, MAXS);
    const wx = (pinch.cx-pinch.v.x)/pinch.v.s, wy = (pinch.cy-pinch.v.y)/pinch.v.s;
    view.s = ns; view.x = cx-wx*ns; view.y = cy-wy*ns; draw(); return;
  }
  if(!drag) return;
  if(!drag.moved && Math.hypot(p.x-drag.sx, p.y-drag.sy) > 6) drag.moved = true;
  if(!drag.moved) return;
  const w = toWorld(p.x, p.y);
  if(drag.type === 'node'){ if(!drag.undo){ pushUndo(); drag.undo = true; } drag.n.x = w.x+drag.offX; drag.n.y = w.y+drag.offY; }
  else if(drag.type === 'pan'){ view.x += p.x-drag.lx; view.y += p.y-drag.ly; }
  else if(drag.type === 'bend'){
    if(!drag.undo){ pushUndo(); drag.undo = true; }
    const g = edgeGeom(drag.ed); if(g){ let cv2 = (w.x-g.mx)*g.nx+(w.y-g.my)*g.ny; if(Math.abs(cv2) < 6) cv2 = 0; drag.ed.curve = cv2; }
  }
  drag.lx = p.x; drag.ly = p.y; draw();
});
function endPtr(e){
  if(!pointers.has(e.pointerId)) return;
  pointers.delete(e.pointerId);
  if(pinch){ if(pointers.size < 2){ pinch = null; save(); } drag = null; return; }
  if(!drag) return;
  const d = drag; drag = null;
  if(d.moved){ save(); return; }
  if(e.type === 'pointercancel') return;
  handleTap(d);
}
cv.addEventListener('pointerup', endPtr);
cv.addEventListener('pointercancel', endPtr);
cv.addEventListener('pointerleave', () => {
  if(!pointers.size){
    edgePreview = null;
    setHover(null, null);
    draw();
  }
});
cv.addEventListener('contextmenu', e => e.preventDefault());
cv.addEventListener('wheel', e => { e.preventDefault(); const p = ptr(e); zoomAt(p.x, p.y, Math.exp(-e.deltaY*0.0015)); }, {passive:false});
document.addEventListener('gesturestart', e => e.preventDefault());

function handleTap(d){
  const {n, ed, w} = d, now = Date.now();
  const key = n ? 'n'+n.id : ed ? 'e'+ed.id : 'bg';
  const dbl = (now-lastTap.t < 400 && lastTap.key === key); lastTap = {t:now, key};
  switch(tool){
    case 'move':
      if(dbl && n) renameNode(n); else if(dbl && ed) editWeight(ed);
      else if(n) toast(nodeInfo(n)); else if(ed) toast(`${edgeName(ed)} • น้ำหนัก = ${fmt(ed.w)} (แตะ 2 ครั้งเพื่อแก้)`);
      break;
    case 'node':
      if(!n && !ed) addNodeAt(w.x, w.y); else if(n && dbl) renameNode(n);
      break;
    case 'edge':
      if(!n){ selNode = null; updateHint(); draw(); break; }
      if(selNode == null || !nodeById(selNode)){ selNode = n.id; }
      else if(selNode === n.id){ selNode = null; }
      else { const u = selNode; selNode = null; addEdge(u, n.id); }
      edgePreview = {x:w.x,y:w.y};
      updateHint(); draw();
      break;
    case 'edit': if(n) renameNode(n); else if(ed) editWeight(ed); break;
    case 'del': if(n) deleteNode(n); else if(ed) deleteEdge(ed); break;
    case 'bend': if(ed && ed.curve){ commit(() => { ed.curve = 0; }, false); toast('📏 ทำให้เส้นตรงแล้ว'); } break;
  }
}
function nodeInfo(n){
  const d = degreeInfo()[n.id];
  return `${n.label} (v${n.id}) • deg = ${d.deg}` + (G.directed ? ` (เข้า ${d.in} / ออก ${d.out})` : '') + ' • แตะ 2 ครั้งเพื่อเปลี่ยนชื่อ';
}

/* ---------- edit ops ---------- */
function addNodeAt(x, y){
  let id; commit(() => { id = G.nextId++; G.nodes.push({id, x, y, label:'v'+id, color:null}); });
  toast(`➕ เพิ่ม v${id} แล้ว (ตั้งชื่อด้วยเครื่องมือ ✏️)`);
}
function askWeight(def, msg){
  for(;;){
    const s = prompt(msg, String(def)); if(s === null) return null;
    const t = String(s).trim().replace(',', '.'), v = Number(t);
    if(t !== '' && isFinite(v) && v >= 0) return v;
    alert('⚠ น้ำหนักต้องเป็นตัวเลขที่ไม่ติดลบ เช่น 5 หรือ 2.5');
  }
}
function addEdge(u, v){
  if(u === v) return toast('ไม่อนุญาตให้เชื่อมจุดกับตัวเอง (loop)');
  const dup = G.edges.find(e => (e.u === u && e.v === v) || (!G.directed && e.u === v && e.v === u));
  if(dup){ toast('มีเส้นนี้อยู่แล้ว → เปลี่ยนน้ำหนักแทน'); editWeight(dup); return; }
  const w = askWeight(1, `น้ำหนักของเส้น ${nm(u)} ${G.directed?'→':'–'} ${nm(v)}\n(ระยะทาง / ค่าใช้จ่าย / ความจุ — ไม่ติดลบ)`);
  if(w === null) return;
  commit(() => {
    const e = {id:G.nextEid++, u, v, w, curve:0};
    const rev = G.directed && G.edges.find(x => x.u === v && x.v === u);
    if(rev){ e.curve = 28; if(!rev.curve) rev.curve = 28; }
    G.edges.push(e);
  });
  toast(`🔗 สร้างเส้น ${nm(u)} ${G.directed?'→':'–'} ${nm(v)} = ${fmt(w)}`);
}
function renameNode(n){
  const s = prompt('ตั้งชื่อจุดยอด (เช่น คลังสินค้า, ร้านค้า 1, โรงพยาบาล):', n.label);
  if(s === null) return;
  const t = s.trim() || ('v'+n.id);
  commit(() => { n.label = t; }, false);
}
function editWeight(e){
  const w = askWeight(e.w, `น้ำหนักใหม่ของเส้น ${edgeName(e)} (ไม่ติดลบ):`);
  if(w === null) return;
  commit(() => { e.w = w; });
}
function deleteNode(n){
  commit(() => {
    G.edges = G.edges.filter(e => e.u !== n.id && e.v !== n.id);
    G.nodes = G.nodes.filter(x => x !== n);
    if(G.source === n.id) G.source = null; if(G.sink === n.id) G.sink = null; if(selNode === n.id) selNode = null;
  });
  toast(`🗑 ลบ ${n.label} แล้ว`);
}
function deleteEdge(e){ commit(() => { G.edges = G.edges.filter(x => x !== e); }); toast(`🗑 ลบเส้น ${edgeName(e)} แล้ว`); }

/* ---------- graph helpers ---------- */
function outAdj(){
  const adj = new Map(G.nodes.map(n => [n.id, []]));
  for(const e of G.edges){ adj.get(e.u).push({to:e.v, w:e.w, e}); if(!G.directed) adj.get(e.v).push({to:e.u, w:e.w, e}); }
  return adj;
}
function nbrSets(){
  const m = new Map(G.nodes.map(n => [n.id, new Set()]));
  for(const e of G.edges){ if(e.u === e.v) continue; m.get(e.u).add(e.v); m.get(e.v).add(e.u); }
  return m;
}
function components(){
  const nb = nbrSets(), seen = new Set(), comps = [];
  for(const n of G.nodes){
    if(seen.has(n.id)) continue;
    const comp = [], q = [n.id]; seen.add(n.id);
    while(q.length){ const u = q.shift(); comp.push(u); for(const v of nb.get(u)) if(!seen.has(v)){ seen.add(v); q.push(v); } }
    comps.push(comp);
  }
  return comps;
}
function degreeInfo(){
  const d = {}; G.nodes.forEach(n => d[n.id] = {deg:0, in:0, out:0});
  G.edges.forEach(e => { d[e.u].deg++; d[e.v].deg++; d[e.u].out++; d[e.v].in++; });
  return d;
}
function mkStep(msg, b, ex){
  ex = ex || {};
  return {msg, ntext:ex.ntext||b.ntext||null, node:Object.assign({}, b.node, ex.node), edge:Object.assign({}, b.edge, ex.edge), etext:ex.etext||b.etext||null, fill:ex.fill||b.fill||null};
}

/* ---------- analysis ---------- */
function matrixHTML(kind){
  const ids = G.nodes.map(n => n.id), idx = new Map(ids.map((id,i) => [id,i]));
  const A = ids.map(() => ids.map(() => 0)), M = ids.map(() => ids.map(() => null));
  for(const e of G.edges){
    const i = idx.get(e.u), j = idx.get(e.v);
    A[i][j]++; M[i][j] = M[i][j] == null ? e.w : Math.min(M[i][j], e.w);
    if(!G.directed){ A[j][i]++; M[j][i] = M[i][j]; }
  }
  let h = '<div class="tw"><table class="tbl"><tr><th></th>' + ids.map(id => `<th title="${esc(nm(id))}">v${id}</th>`).join('') + '</tr>';
  ids.forEach((id,i) => {
    h += `<tr><th title="${esc(nm(id))}">v${id}</th>` + ids.map((_,j) => {
      if(kind === 'A') return `<td>${A[i][j]}</td>`;
      return `<td>${i===j ? 0 : (M[i][j] == null ? '∞' : fmt(M[i][j]))}</td>`;
    }).join('') + '</tr>';
  });
  return h + '</table></div>';
}
function analysisHTML(){
  const n = G.nodes.length, m = G.edges.length, deg = degreeInfo(), comps = components();
  const sumDeg = G.nodes.reduce((a,x) => a+deg[x.id].deg, 0), neg = G.edges.filter(e => e.w < 0);
  let h = `<div class="cards">${card('|V| จำนวนจุดยอด', n)}${card('|E| จำนวนเส้นเชื่อม', m)}${card('ชนิดกราฟ', G.directed?'มีทิศทาง →':'ไม่มีทิศทาง —')}${card('Components', comps.length)}</div>`;
  if(!n) return h + '<div class="hero warn">ยังไม่มีจุดยอด ลองกด 📂 ตัวอย่าง หรือ ⬛ เพิ่มจุด</div>';
  h += comps.length <= 1
    ? `<div class="hero">✔ กราฟเชื่อมต่อกัน (Connected)${G.directed?' แบบไม่สนทิศ':''} — Prim จะได้ Spanning Tree เดียว</div>`
    : `<div class="hero warn">⚠ กราฟไม่เชื่อมต่อ มี ${comps.length} ส่วน — Prim จะได้ Spanning Forest และ Flow/Dijkstra อาจไปไม่ถึงบางจุด</div>`;
  h += `<h3>ตรวจ Σdeg = 2|E|</h3><p>Σdeg = ${G.nodes.map(x => deg[x.id].deg).join(' + ')} = <b>${sumDeg}</b> และ 2|E| = 2 × ${m} = <b>${2*m}</b> ${sumDeg===2*m?'✔ ถูกต้อง':'✘'}</p>`;
  if(G.directed) h += `<p>กราฟมีทิศ: Σdeg⁺(ออก) = ${G.nodes.reduce((a,x)=>a+deg[x.id].out,0)} = Σdeg⁻(เข้า) = ${G.nodes.reduce((a,x)=>a+deg[x.id].in,0)} = |E| ✔</p>`;
  h += `<h3>ตรวจน้ำหนักติดลบ</h3>` + (neg.length ? `<div class="hero bad">⚠ พบ ${neg.length} เส้นติดลบ: ${neg.map(e => esc(edgeName(e))).join(', ')} — ห้ามใช้ Dijkstra</div>` : '<p>✔ ไม่มีน้ำหนักติดลบ (Dijkstra ใช้ได้)</p>');
  h += `<h3>Degree ของแต่ละจุด</h3><div class="tw"><table class="tbl"><tr><th>จุด</th><th>ชื่อ</th><th>deg</th>${G.directed?'<th>เข้า (in)</th><th>ออก (out)</th>':''}</tr>`;
  G.nodes.forEach(x => { h += `<tr><td>v${x.id}</td><td class="l">${esc(x.label)}</td><td><b>${deg[x.id].deg}</b></td>${G.directed?`<td>${deg[x.id].in}</td><td>${deg[x.id].out}</td>`:''}</tr>`; });
  h += '</table></div>';
  h += `<h3>Components (${comps.length})</h3>` + comps.map((c,i) => `<div>ส่วนที่ ${i+1}: ${c.map(id => `<span class="chip">${esc(nm(id))}</span>`).join('')}</div>`).join('');
  if(n <= 30){
    h += `<h3>Adjacency Matrix</h3><p style="font-size:13px">แถว = ต้นทาง, คอลัมน์ = ปลายทาง, ตัวเลข = จำนวนเส้น</p>` + matrixHTML('A');
    h += `<h3>Weight Matrix</h3><p style="font-size:13px">∞ = ไม่มีเส้นตรงถึงกัน (ถ้ามีหลายเส้นจะใช้ค่าน้อยสุด)</p>` + matrixHTML('W');
  } else h += '<p>(Matrix แสดงเมื่อ |V| ≤ 30)</p>';
  return h;
}
function showAnalysis(){ openModal('🔍 ผลวิเคราะห์กราฟ', analysisHTML()); }

/* ---------- Python algorithm API ---------- */
async function runPythonAlgorithm(algorithm, extra={}){
  if(!G.nodes.length && !extra.sequence) return toast('ยังไม่มีจุดยอด');
  try{
    const response = await fetch('/api/run', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({
        ...extra,
        algorithm,
        nodes:G.nodes.map(({id,label}) => ({id,label})),
        edges:G.edges.map(({id,u,v,w}) => ({id,u,v,w})),
        directed:G.directed,
        source:G.source,
        sink:G.sink,
        colorNames:G.colorNames
      })
    });
    const result = await response.json();
    if(!response.ok) throw new Error(result.error || `HTTP ${response.status}`);
    if(result.key === 'color'){
      pushUndo();
      G.nodes.forEach(n => { n.color = result.colors[n.id] ?? null; });
      save();
    }
    setRun({
      key:result.key,
      title:result.title,
      steps:result.steps,
      summary:() => result.summary.replace(/\{\{COLOR_NAME_(\d+)\}\}/g, (_, i) => esc(cName(+i)))
    });
  }catch(error){
    console.error('Python algorithm request failed:', error);
    toast(`รันอัลกอริทึมไม่สำเร็จ: ${error.message}`);
  }
}
function runDijkstra(){ return runPythonAlgorithm('dijkstra'); }
function runPrim(){ return runPythonAlgorithm('prim'); }
function runColoring(){ return runPythonAlgorithm('color'); }
function runFlow(){ return runPythonAlgorithm('flow'); }

/* ---------- player ---------- */
function setRun(r){
  stop(); run = r; stepIdx = 0; updatePlayer(); draw();
  toast(`พร้อมแล้ว ${r.steps.length} ขั้น — กด ▶ เพื่อเล่น หรือ ▶| ทีละขั้น`);
}
function clearRun(){ stop(); run = null; stepIdx = 0; updatePlayer(); }
function go(i){ if(!run) return; stepIdx = clamp(i, 0, run.steps.length-1); updatePlayer(); draw(); }
function stop(){ playing = false; clearTimeout(timer); const b = $('#bPlay'); if(b) b.textContent = '▶'; }
function play(){
  if(!run) return toast('กด "เริ่มรัน" ก่อน');
  if(playing) return stop();
  if(stepIdx >= run.steps.length-1) go(0);
  playing = true; $('#bPlay').textContent = '⏸'; tick();
}
function tick(){
  clearTimeout(timer);
  timer = setTimeout(() => {
    if(!playing || !run) return;
    if(stepIdx < run.steps.length-1){
      go(stepIdx+1);
      if(stepIdx >= run.steps.length-1){ stop(); setTimeout(showSummary, 600); } else tick();
    } else stop();
  }, 1200/speed);
}
function manual(fn){ stop(); fn(); }
function updatePlayer(){
  const n = run ? run.steps.length : 0, sl = $('#slider');
  sl.max = Math.max(0, n-1); sl.value = stepIdx;
  $('#stepLbl').textContent = n ? `ขั้น ${stepIdx+1}/${n}` : 'ขั้น 0/0';
  $('#stepText').textContent = run ? run.steps[stepIdx].msg : defaultStepText();
  $('#sumBtn').classList.toggle('glow', !!run && stepIdx === n-1);
}
function defaultStepText(){
  const T = TABS[algo];
  if(algo === 'color') return '👉 กด "▶ เริ่มรัน" เพื่อระบายสีแบบ Welsh–Powell';
  return `👉 ${T.s ? 'เลือก ' + T.s.replace(/^\S+\s/, '') + (T.t ? ' และ ' + T.t.replace(/^\S+\s/, '') : '') + ' แล้ว' : ''}กด "▶ เริ่มรัน"`;
}
function showSummary(){
  if(algo === 'analyze') return showAnalysis();
  if(!run) return toast('กด "เริ่มรัน" ก่อน แล้วค่อยดูสรุปผล');
  openModal(run.title, run.summary());
}

/* ---------- tabs ---------- */
const TABS = {
  analyze:{icon:'🔍', name:'วิเคราะห์', desc:'ดูภาพรวมของกราฟ: |V|, |E|, Degree, Σdeg = 2|E|, Connected/Components, ตรวจน้ำหนักติดลบ, Adjacency & Weight Matrix', s:null, t:null, run:() => showAnalysis()},
  dijkstra:{icon:'🛣️', name:'Dijkstra', desc:'หาเส้นทางสั้นที่สุดจากต้นทางไปทุกจุด โดยใช้น้ำหนักเป็นระยะทางหรือค่าขนส่ง', app:'เส้นทางขนส่งที่สั้น/ถูกที่สุด', s:'🚩 ต้นทาง', t:'🏁 ปลายทาง', run:runDijkstra},
  prim:{icon:'🌳', name:'Prim (MST)', desc:'สร้าง Spanning Tree ที่น้ำหนักรวมน้อยที่สุด โดยเพิ่มเส้นที่ถูกที่สุดทีละเส้น', app:'วางถนน/ท่อ/สายไฟให้ต้นทุนรวมต่ำสุด', s:'🚩 จุดเริ่ม', t:null, run:runPrim},
  color:{icon:'🎨', name:'Coloring', desc:'ระบายสีแบบ Welsh–Powell: จุดที่เชื่อมกัน (ขัดแย้งกัน) ต้องได้สีต่างกัน (ไม่สนน้ำหนักเส้น)', app:'จัดตารางสอบ/ช่องเก็บสินค้าไม่ให้ชนกัน', s:null, t:null, run:runColoring},
  flow:{icon:'🚰', name:'Max Flow', desc:'Edmonds–Karp: หา Augmenting Path ด้วย BFS ซ้ำจนไหลเพิ่มไม่ได้ ใช้น้ำหนักเป็นความจุ (Capacity) ควรใช้กราฟแบบมีทิศ', app:'ปริมาณสินค้า/การจราจรสูงสุด และจุดคอขวด', s:'🟢 Source', t:'🔴 Sink', run:runFlow},
  bfs:{icon:'🌊', name:'BFS', desc:'ท่องกราฟทีละระดับด้วย Queue แสดงระดับ (Level) และ Non-tree edge', app:'หาเส้นทางที่ผ่านจำนวนเส้นน้อยที่สุด', s:'🚩 จุดเริ่ม', t:null, run:() => runPythonAlgorithm('bfs')},
  dfs:{icon:'🧭', name:'DFS', desc:'ท่องลึกด้วย Stack แสดงเวลา Discovery/Finish และจำแนกเส้น Tree / Back / Forward / Cross', app:'ตรวจวงจร จัดลำดับงาน หาทางออกเขาวงกต', s:'🚩 จุดเริ่ม', t:null, run:() => runPythonAlgorithm('dfs')},
  kruskal:{icon:'🪓', name:'Kruskal', desc:'MST โดยเรียงเส้นตามน้ำหนัก เลือกเส้นที่ไม่ทำให้เกิดวงจร (Union-Find) ถ้าไม่ Connected จะได้ Spanning Forest', app:'วางโครงข่ายต้นทุนต่ำสุด เทียบจำนวนขั้นกับ Prim', s:null, t:null, run:() => runPythonAlgorithm('kruskal')},
  bellman:{icon:'⚖️', name:'Bellman-Ford', desc:'ระยะสั้นที่สุดที่รองรับน้ำหนักติดลบ และไฮไลต์ Negative Cycle ถ้ามี', app:'คำนวณต้นทุนที่มีส่วนลด/กำไรติดลบ', s:'🚩 ต้นทาง', t:null, run:() => runPythonAlgorithm('bellman')},
  topo:{icon:'📋', name:'Topo Sort', desc:'จัดลำดับจุดของ DAG ด้วย Kahn (ต้องเป็นกราฟมีทิศและไม่มีวงจร มิฉะนั้นจะแจ้งเตือน)', app:'ลำดับการทำงานที่มีเงื่อนไขก่อน-หลัง', s:null, t:null, run:() => runPythonAlgorithm('topo')},
  scc:{icon:'🔗', name:'SCC', desc:'หา Strongly Connected Components ด้วย Tarjan ระบายสีแต่ละกลุ่ม และสร้าง Condensation Graph', app:'จัดกลุ่มเว็บเพจ/เส้นทางที่ไปมาหากันได้', s:null, t:null, run:() => runPythonAlgorithm('scc')},
  bridges:{icon:'🌉', name:'Bridge/AP', desc:'หา Bridge และ Articulation Point ด้วย DFS + Low-link (กราฟไม่มีทิศ)', app:'หาจุดอ่อนของเครือข่ายที่ขาดแล้วแยกส่วน', s:null, t:null, run:() => runPythonAlgorithm('bridges')},
  euler:{icon:'🔁', name:'Euler', desc:'ตรวจ Euler Path/Circuit (เงื่อนไข degree คี่ หรือ In/Out) แล้วเดินด้วย Hierholzer ทีละขั้น', app:'วางเส้นทางเก็บขยะ/ตรวจถนนให้ผ่านทุกเส้นครั้งเดียว', s:null, t:null, run:() => runPythonAlgorithm('euler')},
  floyd:{icon:'🧮', name:'Floyd–Warshall', desc:'ระยะสั้นสุดทุกคู่ด้วย DP ทีละจุดผ่าน รองรับน้ำหนักติดลบ และตรวจ Negative Cycle', app:'ตารางระยะทางระหว่างทุกคลังสินค้า', s:null, t:null, run:() => runPythonAlgorithm('floyd')},
  dsatur:{icon:'🌈', name:'DSatur', desc:'ระบายสีจุดยอดโดยเลือกจุดที่ Saturation สูงสุดก่อน แล้วเทียบกับ Welsh–Powell', app:'จัดตารางสอบ/ช่องจัดเก็บให้ใช้ช่องน้อยสุด', s:null, t:null, run:() => runPythonAlgorithm('dsatur')},
  edgecolor:{icon:'🖍️', name:'Edge Color', desc:'ระบายสีเส้น เส้นที่มีจุดร่วมกันต้องคนละสี แสดง χ′(G) และขอบเขต Vizing', app:'จัดรอบแข่งขัน/ช่วงเวลาให้ไม่ชนกัน', s:null, t:null, run:() => runPythonAlgorithm('edgecolor')},
  matching:{icon:'🤝', name:'Matching', desc:'Maximum Bipartite Matching ด้วย Augmenting Path พร้อม Hall และ König', app:'จับคู่งาน–คน หรือคลัง–ร้านค้า', s:null, t:null, run:() => runPythonAlgorithm('matching')},
  hamilton:{icon:'🧩', name:'Hamiltonian', desc:'หา Hamiltonian Path/Cycle ด้วย Backtracking (|V| ≤ 10) พร้อมเงื่อนไข Dirac/Ore', app:'วางเส้นทางเยี่ยมทุกเมืองครั้งเดียว', s:null, t:null, run:() => runPythonAlgorithm('hamilton')},
  tsp:{icon:'🧭', name:'TSP', desc:'Held–Karp (Exact, |V| ≤ 10) เทียบกับ Nearest Neighbor', app:'จัดเส้นทางส่งของให้สั้นที่สุด', s:null, t:null, run:() => runPythonAlgorithm('tsp')},
  kirchhoff:{icon:'🌲', name:'Spanning Tree', desc:'นับจำนวน Spanning Tree ด้วย Kirchhoff Matrix-Tree Theorem (det ของ Laplacian)', app:'นับจำนวนวิธีวางโครงข่ายที่เชื่อมครบโดยไม่มีวงจร', s:null, t:null, run:() => runPythonAlgorithm('kirchhoff')},
  prufer:{icon:'🔢', name:'Prüfer Code', desc:'แปลงต้นไม้เป็นรหัส Prüfer ทีละขั้น (ลบใบ label น้อยสุด)', app:'เข้ารหัสต้นไม้ให้กะทัดรัด', s:null, t:null, run:() => runPythonAlgorithm('prufer')},
  havel:{icon:'🧾', name:'Havel–Hakimi', desc:'ตรวจว่า Degree Sequence สร้างเป็นกราฟได้ไหม (Erdős–Gallai + Havel–Hakimi) และสร้างเส้นให้', app:'ตรวจความเป็นไปได้ของโครงสร้างเครือข่าย', s:null, t:null, run:() => { const t = prompt('ใส่ Degree Sequence เช่น 3,3,2,2,2 (เว้นว่าง = ใช้ของกราฟปัจจุบัน)', ''); if(t !== null) runPythonAlgorithm('havel', {sequence:t}); }},
  cover:{icon:'🧱', name:'Cover/Clique', desc:'Exact: Vertex Cover, Independent Set, Clique, Dominating Set (|V| ≤ 16)', app:'วางกล้อง/สถานีให้ครอบคลุมโดยใช้น้อยที่สุด', s:null, t:null, run:() => runPythonAlgorithm('cover')},
  planar:{icon:'🗺️', name:'Planarity', desc:'ตรวจ m ≤ 3n−6, m ≤ 2n−4, Bipartite/Triangle และค้นหา K₅ / K₃,₃ แบบ Subgraph', app:'ตรวจว่าวาดวงจร/ถนนบนระนาบโดยไม่ตัดกันได้ไหม', s:null, t:null, run:() => runPythonAlgorithm('planar')},
  metrics:{icon:'📈', name:'Centrality', desc:'Degree/Closeness/Betweenness, Clustering Coefficient และ Laplacian Spectrum', app:'หาจุดสำคัญของเครือข่ายสังคม/การขนส่ง', s:null, t:null, run:() => runPythonAlgorithm('metrics')},
  connect:{icon:'🛡️', name:'κ / λ', desc:'Vertex Connectivity κ(G), Edge Connectivity λ(G) ด้วย Max Flow + Menger\'s Theorem (|V| ≤ 20)', app:'วัดความทนทานของเครือข่ายเมื่อจุด/เส้นล่ม', s:null, t:null, run:() => runPythonAlgorithm('connect')},
};
const LEGENDS = {
  kirchhoff:'', prufer:'<span class="lg"><i style="background:#38b764"></i>ใบที่ถูกลบ</span>', havel:'',
  cover:'<span class="lg"><i style="background:#38b764"></i>สมาชิกของคำตอบ Exact</span>',
  planar:'<span class="lg"><i style="background:#38b764"></i>จุดของ K₅ / K₃,₃ ที่พบ</span>',
  metrics:'<span class="lg">ป้าย = Betweenness</span>', connect:'<span class="lg"><i style="background:#ffcd75"></i>คู่จุดที่เปราะบางที่สุด</span>',
  analyze:'',
  dijkstra:'<span class="lg"><i style="background:#ffcd75"></i>กำลังปิดจุด</span><span class="lg"><i style="background:#ef7d57"></i>กำลัง Relax</span><span class="lg"><i style="background:#a7f070"></i>ปิดแล้ว</span><span class="lg"><i class="ln" style="background:#38b764"></i>เส้นทางสั้นสุด</span><span class="lg">🟨 ตัวเลขเหนือจุด = ระยะ</span>',
  prim:'<span class="lg"><i class="ln" style="background:#ef7d57"></i>เส้นตัวเลือก</span><span class="lg"><i class="ln" style="background:#38b764"></i>อยู่ในต้นไม้</span><span class="lg"><i style="background:#a7f070"></i>จุดในต้นไม้</span>',
  color:'<span class="lg"><i style="background:#fff;border-color:#b13e53;border-width:4px"></i>จุดที่กำลังพิจารณา</span><span class="lg"><i class="ln" style="background:#ef7d57"></i>เส้นขัดแย้ง</span><span class="lg">สีของจุด = กลุ่ม (ช่วงเวลา/ช่องเก็บ)</span>',
  flow:'<span class="lg">ตัวเลข f/c = flow/ความจุ</span><span class="lg"><i class="ln" style="background:#3b5dc9"></i>มี flow</span><span class="lg"><i class="ln" style="background:#5d275d"></i>เต็ม</span><span class="lg"><i class="dash"></i>คอขวด (Min Cut)</span><span class="lg"><i style="background:#73eff7"></i>ฝั่ง S</span>',
  bfs:'<span class="lg"><i style="background:#ef7d57"></i>อยู่ใน Queue</span><span class="lg"><i style="background:#a7f070"></i>เสร็จแล้ว</span><span class="lg">L# = ระดับ</span>',
  dfs:'<span class="lg">d/f = เวลาค้นพบ/เสร็จ</span><span class="lg">T=Tree B=Back F=Forward C=Cross</span><span class="lg"><i class="dash"></i>Back edge (มีวงจร)</span>',
  kruskal:'<span class="lg"><i class="ln" style="background:#ef7d57"></i>กำลังพิจารณา</span><span class="lg"><i class="ln" style="background:#38b764"></i>รับเข้า MST</span><span class="lg"><i class="ln" style="background:#94b0c2"></i>ข้าม (เกิดวงจร)</span>',
  bellman:'<span class="lg">ป้ายบนจุด = ระยะปัจจุบัน</span><span class="lg"><i class="ln" style="background:#ef7d57"></i>กำลัง Relax</span><span class="lg"><i class="dash"></i>Negative Cycle</span>',
  topo:'<span class="lg">ตัวเลข = in-degree ที่เหลือ, #n = ลำดับที่ได้</span><span class="lg"><i style="background:#ef7d57"></i>พร้อมเลือก</span>',
  scc:'<span class="lg">แต่ละสี = 1 SCC</span><span class="lg">ป้าย = index/low</span>',
  bridges:'<span class="lg">ป้าย = disc/low</span><span class="lg"><i class="dash"></i>Bridge</span><span class="lg"><i style="background:#ef7d57"></i>Articulation Point</span>',
  euler:'<span class="lg"><i class="ln" style="background:#38b764"></i>ลำดับการเดิน (เลขบนเส้น)</span><span class="lg"><i style="background:#ef7d57"></i>จุด degree คี่</span>',
  floyd:'<span class="lg"><i style="background:#ffcd75"></i>จุดผ่าน k</span><span class="lg"><i style="background:#ef7d57"></i>อยู่ใน Negative Cycle</span>',
  dsatur:'<span class="lg">สีจุด = กลุ่มสี · ป้าย c# = หมายเลขสี</span>',
  edgecolor:'<span class="lg">สีเส้น = กลุ่มสี · ป้าย c# = หมายเลขสี</span>',
  matching:'<span class="lg"><i class="ln" style="background:#38b764"></i>เส้นใน Matching</span><span class="lg"><i style="background:#ffcd75"></i>จุดที่กำลังหา Augmenting Path</span>',
  hamilton:'<span class="lg"><i class="ln" style="background:#38b764"></i>เส้นทางที่กำลังเดิน</span>',
  tsp:'<span class="lg"><i class="ln" style="background:#ef7d57"></i>Nearest Neighbor</span><span class="lg"><i class="ln" style="background:#38b764"></i>Held–Karp (ดีที่สุด)</span>'
};
function setTab(key){
  algo = TABS[key] ? key : 'dijkstra'; const T = TABS[algo];
  clearRun();
  $$('#tabs .btn').forEach(b => b.classList.toggle('on', b.dataset.tab === algo));
  $('#algoDesc').innerHTML = `<b>${T.icon} ${T.name}</b> — ${T.desc}` + (T.app ? `<span class="app">💡 การประยุกต์: ${T.app}</span>` : '');
  $('#lblS').style.display = T.s ? '' : 'none'; $('#lblT').style.display = T.t ? '' : 'none';
  $('#selRow').style.display = (T.s || T.t) ? '' : 'none';
  if(T.s) $('#lblSText').textContent = T.s; if(T.t) $('#lblTText').textContent = T.t;
  $('#runBtn').textContent = algo === 'analyze' ? '🔍 เปิดผลวิเคราะห์' : `▶ เริ่มรัน ${T.name}`;
  $('#player').style.display = algo === 'analyze' ? 'none' : '';
  $('#legend').innerHTML = LEGENDS[algo];
  updatePlayer(); save(); draw();
}
function refreshSelects(){
  for(const [sel, key] of [[$('#selS'), 'source'], [$('#selT'), 'sink']]){
    sel.innerHTML = '<option value="">— เลือกจุด —</option>' + G.nodes.map(n => `<option value="${n.id}">${esc(n.label)}${n.label !== 'v'+n.id ? ' (v'+n.id+')' : ''}</option>`).join('');
    sel.value = G[key] == null ? '' : String(G[key]);
  }
}
function updateBadge(){
  const comps = G.nodes.length ? components().length : 0;
  $('#badge').textContent = `|V| ${G.nodes.length} · |E| ${G.edges.length} · ${G.directed ? 'มีทิศ →' : 'ไม่มีทิศ —'}`;
  $('#dirIc').textContent = G.directed ? '→' : '—';
  $('#dirTxt').textContent = G.directed ? 'มีทิศ' : 'ไม่มีทิศ';
  $('#quick').textContent = `|V| = ${G.nodes.length} • |E| = ${G.edges.length} • ` + (comps <= 1 ? 'Connected ✔' : `⚠ ไม่ Connected (${comps} ส่วน)`) + ` • Undo ได้ ${undoStack.length} ขั้น`;
}
const HINTS = {
  move:'✋ ลากจุดเพื่อย้าย • ลากพื้นที่ว่างเพื่อเลื่อนจอ • แตะ 2 ครั้งที่จุด/เส้นเพื่อแก้ไข • ล้อเมาส์/บีบ 2 นิ้ว = ซูม',
  node:'⬛ แตะพื้นที่ว่างเพื่อเพิ่มจุดยอด (ลากจุดเดิมเพื่อย้ายได้)',
  edge:'🔗 แตะจุดแรก แล้วแตะจุดที่สอง เพื่อสร้างเส้นและใส่น้ำหนัก',
  edit:'✏️ แตะจุดเพื่อตั้งชื่อ (เช่น คลังสินค้า) • แตะเส้นเพื่อเปลี่ยนน้ำหนัก',
  bend:'〰️ ลากที่เส้นเพื่อดัดให้โค้ง • แตะเส้นเพื่อทำให้ตรง',
  del:'🗑️ แตะจุดหรือเส้นที่ต้องการลบ (กด Undo ได้)'
};
function updateHint(){
  let h = HINTS[tool];
  if(tool === 'edge' && selNode != null && nodeById(selNode)) h = `🔗 เลือก "${nm(selNode)}" แล้ว → แตะจุดปลายทาง (แตะที่ว่างเพื่อยกเลิก)`;
  $('#hint').textContent = h;
}

/* ---------- presets ---------- */
function mk(directed, nodes, edges, opt){
  const g = emptyGraph(); g.directed = directed;
  nodes.forEach(([x,y,l], i) => g.nodes.push({id:i+1, x, y, label:l, color:null}));
  g.nextId = nodes.length+1;
  edges.forEach(([u,v,w,c]) => g.edges.push({id:g.nextEid++, u, v, w, curve:c||0}));
  return Object.assign(g, opt || {});
}
const PRESETS = {
  transport:{name:'🚚 โครงข่ายขนส่ง', tab:'dijkstra', desc:'หาเส้นทางส่งสินค้าจากคลังไปลูกค้าที่สั้นที่สุด (หน่วย: กม.)', build:() => mk(false,
    [[80,250,'คลังสินค้า'],[250,110,'ศูนย์กระจาย A'],[250,390,'ศูนย์กระจาย B'],[420,250,'จุดพักรถ'],[590,110,'ร้านค้า 1'],[590,390,'ร้านค้า 2'],[760,250,'ลูกค้า']],
    [[1,2,7],[1,3,9],[2,3,10],[2,4,15],[3,4,11],[2,5,20],[4,5,6],[4,6,9],[3,6,21],[5,7,8],[6,7,5]], {source:1, sink:7})},
  city:{name:'🏙️ แผนที่เมือง/โครงสร้างพื้นฐาน', tab:'prim', desc:'วางสายไฟ/ท่อประปาให้ทุกสถานที่เชื่อมกันด้วยต้นทุนต่ำสุด (ล้านบาท)', build:() => mk(false,
    [[100,100,'โรงไฟฟ้า'],[340,60,'โรงพยาบาล'],[580,110,'โรงเรียน'],[200,280,'ตลาด'],[430,260,'ศาลากลาง'],[680,290,'หมู่บ้าน A'],[120,460,'หมู่บ้าน B'],[390,460,'นิคมอุตสาหกรรม'],[640,480,'สถานีรถไฟ']],
    [[1,2,4],[1,4,3],[2,4,5],[2,5,6],[2,3,8],[3,5,7],[3,6,4],[4,5,2],[4,7,6],[5,8,5],[5,6,9],[7,8,7],[8,9,3],[6,9,5],[5,9,8],[4,8,9]], {source:1})},
  exam:{name:'📝 ตารางสอบ/ช่องเก็บสินค้า', tab:'color', desc:'วิชาที่เชื่อมกัน = มีนักเรียนสอบซ้อน ต้องอยู่คนละช่วงเวลา (สี = ช่วงเวลาสอบ)', build:() => {
    const names = ['คณิตศาสตร์','ฟิสิกส์','เคมี','ชีววิทยา','ภาษาอังกฤษ','ภาษาไทย','สังคมศึกษา','คอมพิวเตอร์'];
    const nodes = names.map((l,i) => { const a = (-90+i*45)*Math.PI/180; return [Math.round(400+230*Math.cos(a)), Math.round(300+230*Math.sin(a)), l]; });
    return mk(false, nodes, [[1,2,1],[1,3,1],[1,8,1],[1,7,1],[2,3,1],[2,8,1],[2,4,1],[3,4,1],[4,5,1],[5,6,1],[5,8,1],[6,7,1],[3,8,1]],
      {colorNames:['จันทร์ 09:00','จันทร์ 13:00','อังคาร 09:00','อังคาร 13:00','พุธ 09:00','พุธ 13:00']});
  }},
  pipe:{name:'🚰 โครงข่ายท่อ/ถนน', tab:'flow', desc:'ส่งสินค้าจากโรงงานไปตลาดกลางได้มากที่สุดกี่หน่วย/ชม. และคอขวดอยู่ที่ไหน', build:() => mk(true,
    [[80,260,'โรงงาน'],[280,110,'คลัง A'],[280,410,'คลัง B'],[520,110,'ศูนย์ C'],[520,410,'ศูนย์ D'],[720,260,'ตลาดกลาง']],
    [[1,2,16],[1,3,13],[3,2,4],[2,4,12],[4,3,9],[3,5,14],[5,4,7],[4,6,20],[5,6,4]], {source:1, sink:6})}
};
function showPresets(){
  openModal('📂 ตัวอย่างสาธิต', `<p>เลือกตัวอย่าง (กราฟปัจจุบันจะถูกแทนที่ แต่กด Undo กลับได้)</p><div class="pgrid">` +
    Object.entries(PRESETS).map(([k,p]) => `<div class="pcard"><b>${p.name}</b><span style="font-size:14px">${p.desc}</span><span style="font-size:13px">อัลกอริทึม: <b>${TABS[p.tab].name}</b></span><button type="button" class="btn primary" data-preset="${k}">เปิดตัวอย่างนี้</button></div>`).join('') + '</div>');
}
function loadPreset(k){
  const p = PRESETS[k]; if(!p) return;
  pushUndo(); G = p.build(); selNode = null; closeModal(); setTab(p.tab); afterChange(); fitView();
  toast(`โหลด "${p.name}" แล้ว → กด ▶ เริ่มรัน`);
}

/* ---------- export PNG ---------- */
function exportPNG(){
  if(!G.nodes.length) return toast('ยังไม่มีจุดยอดให้ส่งออก');
  let x0=Infinity, y0=Infinity, x1=-Infinity, y1=-Infinity;
  G.nodes.forEach(n => { x0=Math.min(x0,n.x); y0=Math.min(y0,n.y); x1=Math.max(x1,n.x); y1=Math.max(y1,n.y); });
  G.edges.forEach(e => { const g = edgeGeom(e); if(g){ x0=Math.min(x0,g.px); y0=Math.min(y0,g.py); x1=Math.max(x1,g.px); y1=Math.max(y1,g.py); } });
  x0 -= 100; x1 += 100; y0 -= 70; y1 += 70;
  const FOOT = 46, SC = 2, w = Math.ceil(x1-x0), h = Math.ceil(y1-y0)+FOOT;
  const oc = document.createElement('canvas'); oc.width = w*SC; oc.height = h*SC;
  const c = oc.getContext('2d'); c.scale(SC, SC);
  renderScene(c, w, h-FOOT, {x:-x0, y:-y0, s:1});
  c.fillStyle = INK; c.fillRect(0, h-FOOT, w, FOOT);
  c.fillStyle = '#ffcd75'; c.font = `bold 16px ${FONT}`; c.textAlign = 'left'; c.textBaseline = 'middle';
  c.fillText(`GRAPH THEORY LAB   |V| = ${G.nodes.length}   |E| = ${G.edges.length}   ${G.directed?'Directed':'Undirected'}${run ? '   • '+TABS[run.key].name : ''}`, 14, h-FOOT/2);
  const url = oc.toDataURL('image/png');
  openModal('🖼️ ส่งออก PNG', `<p>ขนาด ${w*SC} × ${h*SC} px (Scale 2) พร้อม |V| = ${G.nodes.length}, |E| = ${G.edges.length}</p>
    <a class="btn primary" download="graph-lab.png" href="${url}">⬇ ดาวน์โหลด PNG</a>
    <div class="note">📱 <b>iPhone/iPad หรือดาวน์โหลดไม่ได้:</b> กดค้างที่ภาพด้านล่าง แล้วเลือก "บันทึกลงในรูปภาพ" (Save to Photos)</div>
    <img src="${url}" class="preview" alt="graph">`);
  if(!IOS){ try{ const a = document.createElement('a'); a.href = url; a.download = 'graph-lab.png'; document.body.appendChild(a); a.click(); a.remove(); }catch(_){} }
}

/* ---------- help ---------- */
function showHelp(){
  openModal('❓ วิธีใช้ Graph Theory Lab', `<div class="hero">👋 ยินดีต้อนรับ! ทดลองอัลกอริทึมกราฟสำหรับงานขนส่งและผังเมือง</div>
  <h3>เริ่มใน 3 ขั้น</h3>
  <ol class="steps">
    <li><b>สร้างกราฟ</b> — กด ⬛ เพิ่มจุด แล้วแตะพื้นที่ว่าง → กด 🔗 เชื่อมเส้น แล้วแตะ 2 จุด (หรือกด 📂 ตัวอย่าง)</li>
    <li><b>เลือกอัลกอริทึม</b> ที่แท็บในแผงควบคุม (ด้านล่างบนมือถือ / ด้านขวาบนคอม) แล้วเลือกต้นทาง-ปลายทาง</li>
    <li><b>กด ▶ เริ่มรัน</b> แล้วดูทีละขั้นด้วย ⏮ ◀ ▶ ▶| ⏭ จากนั้นกด 📊 สรุปผล</li>
  </ol>
  <h3>เครื่องมือ</h3>
  <div class="tw"><table class="tbl">
    <tr><td>✋</td><td class="l">ลากจุด / เลื่อนจอ / แตะ 2 ครั้งเพื่อแก้ไข</td></tr>
    <tr><td>⬛</td><td class="l">เพิ่มจุดยอด</td></tr>
    <tr><td>🔗</td><td class="l">สร้างเส้น + ใส่น้ำหนัก (ตัวเลขไม่ติดลบ)</td></tr>
    <tr><td>✏️</td><td class="l">ตั้งชื่อจุด (เช่น คลังสินค้า) / แก้น้ำหนักเส้น</td></tr>
    <tr><td>〰️</td><td class="l">ดัดเส้นให้โค้ง / แตะเพื่อให้ตรง</td></tr>
    <tr><td>🗑️</td><td class="l">ลบจุดหรือเส้น</td></tr>
    <tr><td>⇄</td><td class="l">สลับกราฟมีทิศ / ไม่มีทิศ</td></tr>
    <tr><td>⌖</td><td class="l">จัดกราฟให้อยู่กึ่งกลางจอ</td></tr>
  </table></div>
  <h3>ทางลัด</h3>
  <p>Ctrl/⌘+Z = Undo • Ctrl/⌘+Y หรือ Ctrl/⌘+Shift+Z = Redo (ประมาณ 70 ขั้น) • ← → = ย้อน/ถัดไป • Space = เล่น/หยุด • ล้อเมาส์หรือบีบ 2 นิ้ว = ซูม</p>
  <div class="note">💾 ระบบบันทึกอัตโนมัติในเบราว์เซอร์ (localStorage): จุด เส้น น้ำหนัก ทิศทาง ชื่อ สี และ Source/Sink</div>
  <p><button type="button" class="btn primary" id="helpPreset">📂 เปิดตัวอย่างสาธิต</button></p>`);
}

/* ---------- bind UI ---------- */
function init(){
  $('#tabs').innerHTML = Object.entries(TABS).map(([k,T]) => `<button type="button" class="btn tab" data-tab="${k}">${T.icon} ${T.name}</button>`).join('');
  $('#tabs').addEventListener('click', e => { const b = e.target.closest('[data-tab]'); if(b) setTab(b.dataset.tab); });
  $('#toolbar').addEventListener('click', e => {
    const b = e.target.closest('[data-tool]'); if(!b) return;
    tool = b.dataset.tool; selNode = null; edgePreview = null;
    $$('[data-tool]').forEach(x => x.classList.toggle('on', x === b));
    updateCanvasCursor(); updateHint(); draw();
  });
  $('#aDir').onclick = () => { commit(() => { G.directed = !G.directed; }); toast(G.directed ? '→ เปลี่ยนเป็นกราฟมีทิศทาง' : '— เปลี่ยนเป็นกราฟไม่มีทิศทาง'); };
  $('#aUndo').onclick = undo;
  $('#aRedo').onclick = redo;
  $('#aStraight').onclick = () => { if(!G.edges.some(e => e.curve)) return toast('เส้นตรงอยู่แล้วทั้งหมด'); commit(() => G.edges.forEach(e => e.curve = 0), false); toast('📏 รีเซ็ตเป็นเส้นตรงแล้ว'); };
  $('#aPreset').onclick = showPresets;
  $('#aPNG').onclick = exportPNG;
  $('#aClear').onclick = () => { if(!G.nodes.length) return; if(confirm('ล้างกราฟทั้งหมด? (กด Undo กลับได้)')){ const d = G.directed; commit(() => { G = emptyGraph(); G.directed = d; }); selNode = null; } };
  $('#aHelp').onclick = showHelp;
  $('#zIn').onclick = () => zoomAt(W/2, H/2, 1.25);
  $('#zOut').onclick = () => zoomAt(W/2, H/2, 0.8);
  $('#zFit').onclick = fitView;
  $('#selS').onchange = e => { G.source = e.target.value === '' ? null : +e.target.value; clearRun(); save(); draw(); };
  $('#selT').onchange = e => { G.sink = e.target.value === '' ? null : +e.target.value; clearRun(); save(); draw(); };
  $('#runBtn').onclick = () => TABS[algo].run();
  $('#bFirst').onclick = () => manual(() => go(0));
  $('#bPrev').onclick = () => manual(() => go(stepIdx-1));
  $('#bPlay').onclick = play;
  $('#bNext').onclick = () => manual(() => go(stepIdx+1));
  $('#bLast').onclick = () => manual(() => go(run ? run.steps.length-1 : 0));
  $('#slider').oninput = e => manual(() => go(+e.target.value));
  $$('[data-sp]').forEach(b => b.onclick = () => { speed = +b.dataset.sp; $$('[data-sp]').forEach(x => x.classList.toggle('on', x === b)); if(playing) tick(); });
  $('#sumBtn').onclick = showSummary;
  $('#clearRunBtn').onclick = () => {
    if(G.nodes.some(n => n.color != null)){ pushUndo(); G.nodes.forEach(n => n.color = null); }
    clearRun(); afterChange(); toast('ล้างผลแล้ว');
  };
  $('#dockToggle').onclick = () => { const d = $('#dock'); d.classList.toggle('collapsed'); $('#dockToggle').textContent = d.classList.contains('collapsed') ? '▴' : '▾'; };
  $('#mclose').onclick = closeModal;
  $('#modal').addEventListener('click', e => { if(e.target.id === 'modal') closeModal(); });
  $('#mbody').addEventListener('click', e => {
    const p = e.target.closest('[data-preset]'); if(p) return loadPreset(p.dataset.preset);
    if(e.target.closest('#helpPreset')) return showPresets();
    const cn = e.target.closest('[data-cname]');
    if(cn){
      const i = +cn.dataset.cname;
      const s = prompt('ตั้งชื่อความหมายของสีนี้ (เช่น จันทร์ 09:00, ช่องเก็บ A):', cName(i));
      if(s !== null){ G.colorNames[i] = s.trim() || `สี ${i+1}`; save(); if(run && run.key === 'color') $('#mbody').innerHTML = run.summary(); }
    }
  });
  window.addEventListener('keydown', e => {
    const tg = e.target.tagName; if(tg === 'INPUT' || tg === 'SELECT' || tg === 'TEXTAREA') return;
    if((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'z'){ e.preventDefault(); if(e.shiftKey) redo(); else undo(); }
    else if((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'y'){ e.preventDefault(); redo(); }
    else if(e.key === 'Escape') closeModal();
    else if(e.key === 'ArrowRight') manual(() => go(stepIdx+1));
    else if(e.key === 'ArrowLeft') manual(() => go(stepIdx-1));
    else if(e.key === ' '){ e.preventDefault(); play(); }
  });

  const savedTab = load();
  if(!savedTab) G = PRESETS.transport.build();
  if('ResizeObserver' in window) new ResizeObserver(() => resize()).observe($('#stage'));
  else window.addEventListener('resize', resize);
  resize();
  setTab(savedTab || 'dijkstra');
  afterChange();
  if(!savedTab){ fitView(); setTimeout(showHelp, 300); }
}
if(document.fonts && document.fonts.ready) document.fonts.ready.then(() => draw());
init();
})();
</script>
</body>
</html>
"""

PORT_START = 8765


def lan_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return
        assets = {
            "/head.png": ("head.png", "image/png"),
            "/mascot_clean.png": ("mascot_clean.png", "image/png"),
            "/web.png": ("web.png", "image/png"),
        }
        if self.path in assets:
            filename, content_type = assets[self.path]
            asset = Path(__file__).with_name(filename)
            try:
                body = asset.read_bytes()
            except OSError:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "public, max-age=3600")
            self.end_headers()
            self.wfile.write(body)
            return
        body = HTML.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path != "/api/run":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0 or length > 2_000_000:
            self.send_error(413, "ข้อมูลกราฟไม่ถูกต้องหรือมีขนาดใหญ่เกินไป")
            return
        try:
            payload = json.loads(self.rfile.read(length))
            if not isinstance(payload, dict):
                raise ValueError("ข้อมูลคำขอไม่ถูกต้อง")
            result = run_algorithm(payload)
        except (ValueError, UnicodeDecodeError) as error:
            body = json.dumps({"error": str(error)}, ensure_ascii=False).encode("utf-8")
            self.send_response(400)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        body = json.dumps(result, ensure_ascii=False, allow_nan=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass  # ปิด log เพื่อให้ Terminal สะอาด


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    # สร้างไฟล์ HTML ไว้ข้าง ๆ เพื่อเปิดแบบออฟไลน์ได้
    out = Path(__file__).with_name("graph_lab.html")
    try:
        out.write_text(HTML, encoding="utf-8")
    except OSError:
        out = None

    httpd = None
    port = PORT_START
    for p in range(PORT_START, PORT_START + 40):
        try:
            httpd = http.server.ThreadingHTTPServer(("0.0.0.0", p), Handler)
            port = p
            break
        except OSError:
            continue

    if httpd is None:
        print("เปิดเซิร์ฟเวอร์ไม่ได้ → เปิดไฟล์ HTML สำรอง (การรันอัลกอริทึมต้องใช้ Python server)")
        if out:
            webbrowser.open(out.as_uri())
        return

    url = f"http://localhost:{port}"
    print("=" * 56)
    print("  GRAPH THEORY LAB  (Logistics & Urban Planning)")
    print("=" * 56)
    print(f"  คอมพิวเตอร์นี้ : {url}")
    print(f"  มือถือ/แท็บเล็ต : http://{lan_ip()}:{port}  (Wi-Fi เดียวกัน)")
    if out:
        print(f"  ไฟล์ออฟไลน์    : {out}")
    print("  กด Ctrl+C เพื่อปิดโปรแกรม")
    print("=" * 56)

    threading.Timer(0.7, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nปิดเซิร์ฟเวอร์แล้ว")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
