// Defending AI Agents: the dot field, the base-rate calculator, header state and reveals.
(function () {
  "use strict";
  var root = document.documentElement;
  root.classList.remove("no-js");
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)");

  // Header background once the page scrolls.
  var top = document.querySelector(".top");
  function onScroll() { if (top) top.classList.toggle("scrolled", window.scrollY > 24); }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  // Reveal on scroll.
  var reveals = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && !reduce.matches) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } });
    }, { rootMargin: "0px 0px -6% 0px", threshold: 0.04 });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("in"); });
  }

  // The waitlist form. Without this script the form still posts, and the
  // server sends the visitor back here with ?waitlist=<outcome>.
  var form = document.querySelector("form.wl");
  var email = form && form.querySelector('input[type="email"]');
  function goToForm(e) {
    if (!email) return;
    if (e) e.preventDefault();
    form.scrollIntoView({ behavior: reduce.matches ? "auto" : "smooth", block: "center" });
    email.focus({ preventScroll: true });
  }
  if (form) {
    var M = JSON.parse(document.getElementById("wl-strings").textContent);
    var status = form.querySelector(".wl-status");
    var button = form.querySelector("button");
    var show = function (state) {
      status.textContent = M[state] || M.error;
      status.setAttribute("data-state", state);
      form.classList.toggle("done", state === "ok");
    };
    var VALID = /^[^\s@<>"(),;:\\]{1,64}@[^\s@<>"(),;:\\]+\.[^\s@<>"(),;:\\.]{2,}$/;
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (form.getAttribute("aria-busy") === "true") return;
      var value = email.value.trim();
      if (!VALID.test(value) || value.length > 254) { show("invalid"); email.focus(); return; }
      var data = { email: value, lang: form.lang.value, website: form.website.value };
      form.setAttribute("aria-busy", "true"); button.disabled = true; show("sending");
      fetch(form.action, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) })
        .then(function (r) { return r.json().catch(function () { return { outcome: "error" }; }); })
        .then(function (res) {
          var outcome = res && M[res.outcome] ? res.outcome : "error";
          show(outcome);
          if (outcome === "ok") email.value = "";
          else email.focus();
        })
        .catch(function () { show("error"); })
        .then(function () { form.removeAttribute("aria-busy"); button.disabled = false; });
    });
    email.addEventListener("input", function () {
      if (status.getAttribute("data-state") === "invalid") { status.textContent = ""; status.removeAttribute("data-state"); }
    });
    // Back from a script-less submission.
    var back = new URLSearchParams(window.location.search).get("waitlist");
    if (back && M[back] && back !== "sending") {
      show(back);
      if (window.history.replaceState) window.history.replaceState(null, "", window.location.pathname);
      goToForm();
    }
  }
  document.querySelectorAll("[data-waitlist]").forEach(function (a) {
    a.addEventListener("click", function (e) { if (email) goToForm(e); });
  });

  // "W" goes to the waitlist, unless the visitor is typing.
  document.addEventListener("keydown", function (e) {
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    var t = e.target;
    if (t && (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT|BUTTON)$/.test(t.tagName))) return;
    if (e.key === "w" || e.key === "W" || e.key === "'") {
      if (email) goToForm(e);
      else { var a = document.querySelector("[data-waitlist]"); if (a) window.location.href = a.href; }
    }
  });

  // The dot field: every dot a tool call, about 1 in 100 a false alarm, one real attack.
  function field(canvas) {
    var ctx = canvas.getContext("2d");
    var W, H, step, cols, rows, falseAlarms, attack, running = false, visible = true;
    var styles = getComputedStyle(root);
    function colours() { styles = getComputedStyle(root); }
    function rng(seed) { return function () { seed = (seed * 16807) % 2147483647; return seed / 2147483647; }; }
    function size() {
      var dpr = Math.min(2, window.devicePixelRatio || 1);
      W = canvas.clientWidth; H = canvas.clientHeight;
      canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      step = Math.max(7, Math.round(W / 150));
      cols = Math.ceil(W / step); rows = Math.ceil(H / step);
      var n = cols * rows, r = rng(11);
      falseAlarms = new Set();
      while (falseAlarms.size < Math.round(n * 0.01)) falseAlarms.add(Math.floor(r() * n));
      // Keep the attack in a clear band: below the header, above the headline, away from the edges.
      do {
        var ai = Math.floor(cols * (0.35 + r() * 0.4)), aj = Math.floor(rows * (0.2 + r() * 0.25));
        attack = aj * cols + ai;
      } while (falseAlarms.has(attack));
      draw(0);
    }
    function noise(i, j, t) {
      return Math.sin(i * 0.045 + t * 0.6) * Math.cos(j * 0.06 - t * 0.4)
        + Math.sin((i + j) * 0.02 + t * 0.3) * 0.6
        + Math.sin(Math.hypot(i - cols * 0.7, j - rows * 0.35) * 0.12 - t * 1.2) * 0.5;
    }
    function draw(t) {
      var fg = styles.getPropertyValue("--fg").trim(), sig = styles.getPropertyValue("--sig").trim();
      ctx.clearRect(0, 0, W, H);
      ctx.fillStyle = fg; ctx.strokeStyle = fg; ctx.lineWidth = 1;
      for (var j = 0; j < rows; j++) {
        var py = j * step + step / 2;
        var fade = Math.min(1, py / (H * 0.55)) * (1 - Math.max(0, (py - H * 0.55) / (H * 0.6)));
        for (var i = 0; i < cols; i++) {
          var k = j * cols + i, px = i * step + step / 2;
          if (k === attack) continue;
          if (falseAlarms.has(k)) {
            ctx.globalAlpha = Math.sin(t * 2 + k) > 0.2 ? 0.9 : 0.32;
            ctx.strokeRect(px - step * 0.32, py - step * 0.32, step * 0.64, step * 0.64);
            continue;
          }
          var v = (noise(i, j, t) + 2.1) / 4.2; v = v < 0 ? 0 : v > 1 ? 1 : v;
          var r = v * v * step * 0.24;
          if (r < 0.35) continue;
          ctx.globalAlpha = 0.16 + fade * 0.38;
          ctx.fillRect(px - r, py - r, r * 2, r * 2);
        }
      }
      var ax = (attack % cols) * step + step / 2, ay = Math.floor(attack / cols) * step + step / 2;
      var pulse = 0.6 + 0.4 * Math.sin(t * 3);
      ctx.fillStyle = sig;
      ctx.globalAlpha = 0.18 * pulse; ctx.beginPath(); ctx.arc(ax, ay, step * 2.2, 0, 7); ctx.fill();
      ctx.globalAlpha = 1; ctx.beginPath(); ctx.arc(ax, ay, step * 0.42, 0, 7); ctx.fill();
      ctx.globalAlpha = 1;
    }
    function loop(ms) {
      if (!running) return;
      draw(ms / 1000);
      requestAnimationFrame(loop);
    }
    function sync() {
      var go = visible && !reduce.matches && !document.hidden;
      if (go && !running) { running = true; requestAnimationFrame(loop); }
      if (!go) running = false;
    }
    size();
    window.addEventListener("resize", size);
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", function () { colours(); draw(0); });
    reduce.addEventListener("change", sync);
    document.addEventListener("visibilitychange", sync);
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (e) { visible = e[0].isIntersecting; sync(); }).observe(canvas);
    }
    sync();
  }
  document.querySelectorAll("canvas[data-field]").forEach(field);

  // The calculator.
  var calc = document.getElementById("calc");
  if (!calc) return;
  var T = JSON.parse(document.getElementById("calc-strings").textContent);
  var lang = root.lang || "en";
  var STEPS = {
    base: [0.1, 0.3, 1, 3, 10, 30, 100, 300, 1000],     // attacks per 10,000 calls
    tpr: [50, 60, 70, 80, 90, 95, 98, 99, 99.9],        // % of attacks caught
    fpr: [0.01, 0.03, 0.1, 0.3, 1, 3, 10],              // % of harmless calls flagged
    calls: [10000, 100000, 1000000, 10000000, 50000000] // tool calls per day
  };
  var inputs = {};
  Object.keys(STEPS).forEach(function (k) { inputs[k] = calc.querySelector('[name="' + k + '"]'); });
  function fmt(n, d) { return new Intl.NumberFormat(lang, { maximumFractionDigits: d == null ? 0 : d }).format(n); }
  function pct(p) {
    var v = p * 100;
    if (v > 0 && v < 0.1) return "<0.1%";
    return fmt(v, v < 10 ? 1 : 0) + "%";
  }
  function compact(n) { return n >= 1e6 ? fmt(n / 1e6, 0) + "M" : fmt(n / 1e3, 0) + "k"; }
  var grid = calc.querySelector(".alerts");
  for (var i = 0; i < 100; i++) grid.appendChild(document.createElement("i"));
  var cells = grid.children;
  var sentence = calc.querySelector(".calc-sentence");
  function update() {
    var v = {};
    Object.keys(inputs).forEach(function (k) {
      v[k] = STEPS[k][+inputs[k].value];
      inputs[k].style.setProperty("--fill", (100 * inputs[k].value / (STEPS[k].length - 1)) + "%");
    });
    var base = v.base / 10000, tpr = v.tpr / 100, fpr = v.fpr / 100;
    var tp = base * tpr, fp = (1 - base) * fpr, precision = tp / (tp + fp);
    var alerts = v.calls * (tp + fp), real = v.calls * tp;
    calc.querySelector('[for="base"] output').textContent = fmt(v.base, 1);
    calc.querySelector('[for="tpr"] output').textContent = fmt(v.tpr, 1) + "%";
    calc.querySelector('[for="fpr"] output').textContent = fmt(v.fpr, 2) + "%";
    calc.querySelector('[for="calls"] output').textContent = compact(v.calls);
    calc.querySelector(".big").textContent = pct(precision);
    calc.querySelector('[data-k="alerts"]').textContent = fmt(Math.round(alerts));
    calc.querySelector('[data-k="real"]').textContent = fmt(Math.round(real));
    var on = Math.round(precision * 100);
    for (var j = 0; j < 100; j++) cells[j].classList.toggle("on", j < on);
    var wrong = Math.round((1 - precision) * 100);
    var s = (precision < 0.5 ? T.sentenceLow : T.sentenceHigh)
      .replace("{wrong}", String(wrong)).replace("{right}", String(100 - wrong))
      .replace("{alerts}", fmt(Math.round(alerts)));
    var parts = s.split("|");
    sentence.textContent = "";
    var strong = document.createElement("strong"); strong.textContent = parts[0];
    sentence.appendChild(strong);
    if (parts[1]) sentence.appendChild(document.createTextNode(parts[1]));
    calc.querySelector(".alerts-note").textContent = on === 0 && precision > 0 ? T.fewerThanOne : "";
  }
  Object.keys(inputs).forEach(function (k) { inputs[k].addEventListener("input", update); });
  update();
})();
