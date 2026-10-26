/* Defending AI Agents: reading progress. No dependencies, no build step.
 *
 * Progress is kept in this browser (localStorage) with no account. Nothing
 * is marked by opening or scrolling: the learner marks a page complete and a
 * problem attempted by hand, and can take either mark back. Each item keeps
 * its latest state and the time of that change, { at, done }; merging two
 * copies keeps the later change (ties go to done), so devices agree whatever
 * order they sync in. Checks arrive from the terminal and are never unmarked
 * here.
 *
 * Sync is optional and off unless the page carries
 *   <meta name="daa-accounts" content="https://accounts.example">
 * (set at build time from ACCOUNTS_URL). When signed in, local items are
 * merged into the account (latest change wins) and the account's state
 * replaces the local copy; from then on the account is the source of truth.
 *
 * Every storage access is wrapped: with storage blocked the page still works
 * and simply forgets. With scripts off nothing here runs and the pages are
 * plain documents.
 */
(function () {
  "use strict";
  var KEY = "daa.progress.v2";
  var OLD_KEY = "daa.progress.v1"; // v1 marked pages on reading; only its problem marks carry over
  var meta = document.querySelector('meta[name="daa-accounts"]');
  var ACC = meta && /^https?:\/\//.test(meta.content) ? meta.content.replace(/\/$/, "") : "";
  var main = document.querySelector("main.course");
  if (!main) return;

  // ── storage ────────────────────────────────────────────────────────────
  function blank() { return { items: {}, last: null, account: null }; }
  function load() {
    try {
      var s = JSON.parse(localStorage.getItem(KEY) || "null");
      if (s && typeof s === "object" && s.items && typeof s.items === "object") return s;
      var old = JSON.parse(localStorage.getItem(OLD_KEY) || "null");
      if (old && old.items && typeof old.items === "object") {
        var b = blank();
        for (var k in old.items) if (/^(problem|check):/.test(k)) b.items[k] = { at: old.items[k], done: true };
        b.account = old.account || null;
        localStorage.removeItem(OLD_KEY);
        return b;
      }
    } catch (e) { /* blocked or corrupt */ }
    return blank();
  }
  function save(s) {
    try { localStorage.setItem(KEY, JSON.stringify(s)); } catch (e) { /* blocked or full */ }
  }
  function clear() {
    try { localStorage.removeItem(KEY); localStorage.removeItem(OLD_KEY); } catch (e) { /* blocked */ }
  }

  var state = load();
  var user = null; // set when signed in and synced

  // The account page sends a deleted learner back here: forget the local copy.
  try {
    var q = new URLSearchParams(location.search);
    if (q.get("account") === "deleted") {
      clear();
      state = blank();
      q.delete("account");
      history.replaceState(null, "", location.pathname + (q.toString() ? "?" + q : "") + location.hash);
    }
  } catch (e) { /* old browser */ }

  function isDone(id) { var it = state.items[id]; return Boolean(it && it.done); }

  function setDone(id, done) {
    var prev = state.items[id];
    // A later change than any seen, even if this device's clock lags another's.
    var at = Math.max(Date.now(), prev ? prev.at + 1 : 0);
    state.items[id] = { at: at, done: done };
    save(state);
    render();
    push({ items: [{ id: id, at: at, done: done }] });
  }

  // ── this page ──────────────────────────────────────────────────────────
  var page = main.getAttribute("data-page"); // "<module>/<lesson>"
  if (page) {
    state.last = { page: page, at: Date.now() };
    save(state);
    Array.prototype.forEach.call(document.querySelectorAll("[data-complete]"), function (b) {
      b.hidden = false;
      b.addEventListener("click", function () { setDone("page:" + page, !isDone("page:" + page)); });
    });
  }

  // Problems: a control after each problem in the top-level list.
  var module_ = main.getAttribute("data-module");
  var problems = main.querySelector("article[data-problems]");
  if (problems && module_) {
    var lists = problems.querySelectorAll(":scope > ol");
    Array.prototype.forEach.call(lists, function (ol) {
      var start = parseInt(ol.getAttribute("start") || "1", 10);
      Array.prototype.forEach.call(ol.children, function (li, i) {
        var id = "problem:" + module_ + "/" + (start + i);
        li.id = "p" + (start + i); // the achievement badges link to #pN
        var b = document.createElement("button");
        b.type = "button";
        b.className = "attempt label";
        b.setAttribute("data-item", id);
        b.addEventListener("click", function () { setDone(id, !isDone(id)); });
        li.appendChild(b);
      });
    });
  }

  if (location.hash && /^#p\d+$/.test(location.hash)) {
    var target = document.getElementById(location.hash.slice(1));
    if (target) target.scrollIntoView();
  }

  // ── display ────────────────────────────────────────────────────────────
  function countPrefix(prefix) {
    var n = 0;
    for (var k in state.items) if (k.indexOf(prefix) === 0 && state.items[k].done) n++;
    return n;
  }

  function render() {
    Array.prototype.forEach.call(document.querySelectorAll("[data-page-link]"), function (a) {
      var done = isDone("page:" + a.getAttribute("data-page-link"));
      a.classList.toggle("is-read", done);
      var sr = a.querySelector(".read-state");
      if (!sr) { sr = document.createElement("span"); sr.className = "read-state"; a.appendChild(sr); }
      sr.textContent = done ? " (complete)" : "";
    });
    Array.prototype.forEach.call(document.querySelectorAll("button.attempt"), function (b) {
      var done = isDone(b.getAttribute("data-item"));
      b.textContent = done ? "Attempted \u2713 (undo)" : "Mark attempted";
      b.setAttribute("aria-pressed", done ? "true" : "false");
      b.classList.toggle("on", done);
    });
    Array.prototype.forEach.call(document.querySelectorAll("[data-complete]"), function (b) {
      var done = page && isDone("page:" + page);
      b.textContent = done ? "Completed \u2713 (undo)" : "Mark complete";
      b.setAttribute("aria-pressed", done ? "true" : "false");
      b.classList.toggle("on", Boolean(done));
    });
    Array.prototype.forEach.call(document.querySelectorAll("[data-module-progress]"), function (el) {
      var m = el.getAttribute("data-module-progress");
      var total = parseInt(el.getAttribute("data-total") || "0", 10);
      var probs = parseInt(el.getAttribute("data-problems") || "0", 10);
      var read = countPrefix("page:" + m + "/");
      var tried = countPrefix("problem:" + m + "/");
      // 07-detectors-as-classifiers -> check:7; e03-agent-loop -> check:E3; the on-ramp and capstone have none here
      var cn = /^e\d/.test(m) ? "E" + parseInt(m.slice(1), 10) : String(parseInt(m, 10));
      var check = isDone("check:" + cn) ? " · make check-" + cn + " passed" : "";
      if (!read && !tried && !check && el.hasAttribute("data-quiet")) { el.hidden = true; return; }
      el.textContent = read + " of " + total + " pages complete" + (probs ? " · " + tried + " of " + probs + " problems attempted" : "") + check;
      el.hidden = false;
    });
    renderSync();
    // The playable map (map.js) reads the same state; it never writes it.
    try { document.dispatchEvent(new CustomEvent("daa:progress", { detail: state })); } catch (e) { /* old browser */ }
  }
  window.DAAProgress = { state: function () { return state; }, done: isDone };

  // ── sync (only with ACCOUNTS_URL) ──────────────────────────────────────
  function api(path, opts) {
    opts = opts || {};
    opts.credentials = "include";
    opts.headers = opts.body ? { "Content-Type": "application/json" } : {};
    return fetch(ACC + path, opts).then(function (r) {
      if (!r.ok) throw new Error(String(r.status));
      return r.json();
    });
  }

  function adopt(server) {
    // The account is the source of truth: its items replace the local ones.
    var items = {};
    (server.items || []).forEach(function (it) { items[it.id] = { at: it.at, done: it.done !== false }; });
    state.items = items;
    if (server.last) state.last = server.last;
    state.account = user.id;
    save(state);
    render();
  }

  function localPayload() {
    var items = [];
    for (var k in state.items) if (/^(page|problem):/.test(k)) items.push({ id: k, at: state.items[k].at, done: state.items[k].done });
    return { items: items, last: state.last };
  }

  function push(payload) {
    if (!ACC || !user) return;
    api("/progress/merge", { method: "POST", body: JSON.stringify(payload) })
      .then(adopt)
      .catch(function () { /* kept locally; merged on the next page load */ });
  }

  function syncNow() {
    api("/me").then(function (me) {
      if (!me.signedIn) { user = null; renderSync(); return; }
      user = { id: me.user.id, email: (me.user.identities[0] || {}).email, provider: (me.user.identities[0] || {}).provider, accountUrl: me.accountUrl };
      // Local progress joins the account the first time (no account yet), or
      // when it already belongs to this account. A copy left by a different
      // account in this browser is replaced, never merged into this one.
      if (!state.account || state.account === user.id) return api("/progress/merge", { method: "POST", body: JSON.stringify(localPayload()) }).then(adopt);
      return api("/progress").then(adopt);
    }).catch(function () { syncError = true; renderSync(); });
  }
  var syncError = false;

  function el(tag, attrs, text) {
    var e = document.createElement(tag);
    for (var k in attrs || {}) e.setAttribute(k, attrs[k]);
    if (text) e.textContent = text;
    return e;
  }

  function renderSync() {
    var boxes = document.querySelectorAll("[data-sync]");
    if (!ACC) return; // sync is off: no sync UI at all
    Array.prototype.forEach.call(boxes, function (box) {
      box.textContent = "";
      var privacy = box.getAttribute("data-privacy");
      if (user) {
        var p = el("p", { "class": "sync-line" });
        p.appendChild(el("span", { "class": "label" }, "Synced"));
        p.appendChild(document.createTextNode(" " + (user.email || "signed in") + " "));
        p.appendChild(el("a", { href: user.accountUrl || ACC + "/account" }, "Account"));
        var out = el("button", { type: "button", "class": "linkish" }, "Sign out");
        out.addEventListener("click", function () {
          api("/auth/logout", { method: "POST", body: "{}" }).catch(function () {}).then(function () { user = null; renderSync(); });
        });
        p.appendChild(document.createTextNode(" · "));
        p.appendChild(out);
        box.appendChild(p);
      } else {
        box.appendChild(el("p", { "class": "sync-line" }, syncError
          ? "Progress is saved in this browser. Sync is unavailable right now."
          : "Progress is saved in this browser. Sign in to sync it across devices:"));
        if (!syncError) {
          var row = el("p", { "class": "sync-buttons" });
          [["github", "GitHub"], ["google", "Google"]].forEach(function (p) {
            row.appendChild(el("a", { "class": "btn", href: ACC + "/auth/" + p[0] + "/start?return=" + encodeURIComponent(location.href) }, "Sign in with " + p[1]));
          });
          box.appendChild(row);
        }
      }
      if (privacy) {
        var note = el("p", { "class": "sync-note label" });
        note.appendChild(el("a", { href: privacy }, "What is stored"));
        box.appendChild(note);
      }
      box.hidden = false;
    });
  }

  render();
  if (ACC) syncNow();
})();
