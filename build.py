#!/usr/bin/env python3
"""Build the site's pages (English, Hebrew, 404) from one template.

Run:  python3 build.py
Writes index.html, he/index.html and 404.html. Both languages share every
structure; only the strings differ, so a section added to one is added to both.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE = "https://defendingaiagents.com"
EMAIL = "shimon@defendingaiagents.com"
E = html.escape

EN = {
    "lang": "en", "dir": "ltr", "path": "/", "other_path": "he/", "other_lang": "he", "other_label": "עברית",
    "title": "Defending AI Agents: a free course for data scientists",
    "description": "A free, build-it-yourself course that teaches ML engineers, statisticians and data scientists to secure AI agents, and to reason about what changes at scale.",
    "og_image": "og.png", "brand": "Defending AI Agents", "skip": "Skip to content",
    "nav": [("#curriculum", "Curriculum"), ("#certificate", "Certificate"), ("#faq", "FAQ")],
    "nav_cta": "Join waitlist",
    "kicker": "Free course · for data scientists · in preparation",
    "h1": ["Defending", "AI agents"],
    "hero_p": "Agent security is a statistics problem. Build every defence yourself on a laptop, then learn what it becomes at fifty million calls a day.",
    "readout": [("Calls", "10,000", ""), ("Alerts", "101", ""), ("Attacks", "1", "s"), ("Real", "0.98%", "")],
    "field_aria": "Animation: ten thousand tool calls drawn as dots. About one in a hundred is flagged as an alert; one is a real attack.",

    "s1": "The problem", "s1_h": "You already know the hard part.",
    "s1_p": "The central problems of securing AI agents have statistical twins. The course supplies the security half.",
    "twins": [
        ("01", "Rare events", "Attacks are rare. How often an alert is right is set by the base rate, not by how good the detector looks on a balanced test set."),
        ("02", "Operating points", "Every threshold spends a false-alarm budget. You choose where to spend it, and measure it where the system acts."),
        ("03", "Distribution shift", "A detector tested on prose meets JSON, logs, diffs and SQL in production, and behaves differently."),
        ("04", "Counterfactuals", "Will a new policy help? Replay it over last month's traffic and run it in shadow before you enforce it."),
    ],

    "s2": "Try it", "s2_h": "Four sliders. One uncomfortable number.",
    "s2_p": "A detector that catches 99% of attacks and flags 1% of harmless calls sounds excellent. Move the sliders and see how many of its alerts are real.",
    "calc_labels": {"base": "Attacks per 10,000 calls", "tpr": "Attacks it catches", "fpr": "Harmless calls it flags", "calls": "Tool calls per day"},
    "calc_big_label": "Alerts that are real attacks",
    "calc_alerts": "Alerts per day", "calc_real": "Real attacks among them",
    "calc_key_real": "Real attack", "calc_key_false": "False alarm", "calc_grid_aria": "100 alerts, filled when real",
    "calc_js": {
        "sentenceLow": "When it fires, it is wrong {wrong} times in 100.| At this base rate, most of the {alerts} alerts a day are false alarms that someone has to clear.",
        "sentenceHigh": "When it fires, it is right {right} times in 100.| The base rate is high enough for most of its alerts to be real.",
        "fewerThanOne": "Fewer than 1 alert in 100 is real.",
    },

    "s3": "What you build", "s3_h": "Every component, with your own hands.",
    "s3_p": "No security product, commercial or open-source, is used or taught. You build a miniature agent gateway with general-purpose open tools, one component per module.",
    "build": [
        ("01", "A small tool-calling agent, and the attack that breaks it"),
        ("03", "A gateway that intercepts every tool call before it runs"),
        ("04", "Prompt-injection detectors: patterns and a fine-tuned classifier"),
        ("05", "Thresholds set from a measured false-positive budget"),
        ("06", "An evaluation harness on data shaped like real tool calls"),
        ("07", "A red-team harness with honest coverage reports"),
        ("08", "A policy engine that allows, refuses, or holds for a person"),
        ("09", "Behavioural baselines and sequence detectors"),
        ("10", "A model loader that checks before it trusts"),
        ("11", "Personal-data detection, redaction and erasure"),
        ("12", "A signed, tamper-evident log, and replay of a policy change"),
        ("13", "A policy learner with a shadow stage"),
    ],

    "s4": "Scale", "s4_h": "Build it small. Reason about it at scale.",
    "s4_p": "Every module ends with what the same component becomes at millions of calls a day, thousands of agents and many teams, worked out from your own measurements.",
    "scale": [
        ("On your laptop", "40", "ms", "Your detector scores one tool call in <strong>40 milliseconds</strong>. You measured it, you understand every line, and it runs in 8 GB of memory with no GPU."),
        ("At 50 million calls a day", "23", "cores", "The same detector keeps about <strong>23 cores busy around the clock</strong>. Where does it run? What happens to a call when it is slow or down? Who reviews its alerts?"),
    ],

    "s5": "Curriculum", "s5_h": "Fifteen modules and a capstone.",
    "s5_p": "Each module ends at a measurement you produce and defend, not at a page you have read. About 105 hours, self-paced, in English and Hebrew.",
    "parts": [
        ("I", "Foundations", [("00", "Orientation: why agent security is a statistics problem"), ("01", "Setting up your lab and your toy agent"), ("02", "Security fundamentals for data people"), ("03", "Anatomy of an agent and its attack surface")]),
        ("II", "Detection", [("04", "Prompt injection, direct and indirect"), ("05", "Detectors are classifiers: base rates, budgets, operating points"), ("06", "Evaluation hygiene and distribution shift"), ("07", "Adversarial robustness and red-teaming")]),
        ("III", "Enforcement", [("08", "From score to decision: policy, holds and humans"), ("09", "Behavioural and sequence anomaly detection"), ("10", "The ML supply chain"), ("11", "Data protection: personal data, redaction, erasure")]),
        ("IV", "Operations", [("12", "Evidence: audit trails, replay and counterfactual evaluation"), ("13", "Learning policy from traffic, safely"), ("14", "Governance, audit and regulation for engineers")]),
    ],
    "cap_label": "Capstone", "cap_h": "Build it, then break someone else's.",
    "cap_p": "Your own gateway for a new scenario, a scale memo, and a red-team report on another learner's work.",

    "s6": "Certificate", "s6_h": "Free to learn. Paid to certify.",
    "s6_p": "The whole course is open. The only paid part is the final exam, which a person reviews.",
    "cert": [
        ("The course", "Free", "No account needed to read.", ["Every lesson, build and test", "English and Hebrew", "A starter kit and automated checks for each module", "Yours to keep and revisit"]),
        ("Final exam and certificate", "Paid", "Optional. Price announced at launch.", ["Your capstone, reviewed personally", "Detailed written feedback", "A signed certificate that anyone can verify", "A public page linking your reviewed work, if you choose"]),
    ],

    "s7": "Questions", "s7_h": "Frequently asked.",
    "faq": [
        ("Do I need a security background?", "No. The course assumes Python, probability and machine learning, and teaches the security from the ground up."),
        ("What do I need to run it?", "A laptop with 8 GB of memory, running macOS, Windows (with WSL 2) or Linux. No GPU is required. Installing Docker and setting up the lab is a module of its own."),
        ("Which products does it teach?", "None. You build every component yourself with open, general-purpose tools, and wherever a tool is chosen the lesson names an alternative."),
        ("Is it really free?", "Yes. Every lesson, build and automated check is free. Only the final exam, which a person reviews, and the certificate that follows are paid."),
        ("In which languages?", "English and Hebrew. Code, commands and tools stay in English in both."),
        ("When does it open?", "It is in preparation. Join the waitlist to hear when the first modules are published."),
    ],

    "cta_label": "Waitlist", "cta_link": ["Join the", "waitlist"],
    "cta_fine": "One e-mail when the first modules are published, and occasional notes on how the course is going. Write to " + EMAIL + "; your address is used only for this course, and you can ask to be removed at any time.",
    "mail_subject": "Waitlist",
    "foot_copy": "© 2026 Defending AI Agents", "foot_contact": "Contact", "foot_security": "Security",

    "nf_title": "Page not found · Defending AI Agents", "nf_label": "404 · not found",
    "nf_h1": ["Nothing", "here"], "nf_btn": "Back to the home page",
}

HE = {
    "lang": "he", "dir": "rtl", "path": "/he/", "other_path": "", "other_lang": "en", "other_label": "English",
    "title": "הגנה על סוכני AI: קורס חינמי למדעני נתונים",
    "description": "קורס חינמי, שבו בונים הכול בעצמכם, שמלמד מהנדסי ML, סטטיסטיקאים ומדעני נתונים לאבטח סוכני AI, ולחשוב על מה שמשתנה בהיקף של ארגון גדול.",
    "og_image": "og-he.png", "brand": "הגנה על סוכני AI", "skip": "דילוג לתוכן",
    "nav": [("#curriculum", "תוכנית הלימודים"), ("#certificate", "תעודה"), ("#faq", "שאלות")],
    "nav_cta": "לרשימת ההמתנה",
    "kicker": "קורס חינמי · למדעני נתונים · בהכנה",
    "h1": ["הגנה על", "סוכני AI"],
    "hero_p": "אבטחת סוכני AI היא בעיה סטטיסטית. בונים כל הגנה בעצמכם על המחשב הנייד, ולומדים מה היא הופכת להיות בחמישים מיליון קריאות ביום.",
    "readout": [("קריאות", "10,000", ""), ("התרעות", "101", ""), ("מתקפות", "1", "s"), ("אמיתיות", "0.98%", "")],
    "field_aria": "הנפשה: עשרת אלפים קריאות לכלים מצוירות כנקודות. בערך אחת ממאה מסומנת כהתרעה; אחת היא מתקפה אמיתית.",

    "s1": "הבעיה", "s1_h": "את החלק הקשה אתם כבר יודעים.",
    "s1_p": "לבעיות המרכזיות באבטחת סוכני AI יש תאומות סטטיסטיות. הקורס משלים את החצי של אבטחת המידע.",
    "twins": [
        ("01", "אירועים נדירים", "מתקפות הן נדירות. הסיכוי שהתרעה אמיתית נקבע לפי שיעור הבסיס, לא לפי כמה טוב הגלאי נראה על סט בדיקה מאוזן."),
        ("02", "נקודות עבודה", "כל סף מוציא תקציב של התרעות שווא. אתם בוחרים איפה להוציא אותו, ומודדים אותו במקום שבו המערכת פועלת."),
        ("03", "שינוי בהתפלגות", "גלאי שנבדק על טקסט חופשי פוגש בייצור JSON, יומנים, diff ו־SQL, ומתנהג אחרת."),
        ("04", "קונטרפקטואלים", "האם מדיניות חדשה תעזור? מריצים אותה על התעבורה של החודש שעבר, ובמצב צל, לפני שאוכפים אותה."),
    ],

    "s2": "נסו", "s2_h": "ארבעה מחוונים. מספר אחד לא נוח.",
    "s2_p": "גלאי שתופס 99% מהמתקפות ומתריע בטעות על 1% מהקריאות התמימות נשמע מצוין. הזיזו את המחוונים וראו כמה מההתרעות שלו אמיתיות.",
    "calc_labels": {"base": "מתקפות לכל 10,000 קריאות", "tpr": "מתקפות שהוא תופס", "fpr": "קריאות תמימות שהוא מסמן", "calls": "קריאות לכלים ביום"},
    "calc_big_label": "התרעות שהן מתקפות אמיתיות",
    "calc_alerts": "התרעות ביום", "calc_real": "מתוכן מתקפות אמיתיות",
    "calc_key_real": "מתקפה אמיתית", "calc_key_false": "התרעת שווא", "calc_grid_aria": "100 התרעות, מלאות כשהן אמיתיות",
    "calc_js": {
        "sentenceLow": "כשהוא מתריע, הוא טועה {wrong} פעמים מתוך 100.| בשיעור הבסיס הזה, רוב {alerts} ההתרעות ביום הן התרעות שווא שמישהו צריך לבדוק.",
        "sentenceHigh": "כשהוא מתריע, הוא צודק {right} פעמים מתוך 100.| שיעור הבסיס גבוה מספיק כדי שרוב ההתרעות שלו יהיו אמיתיות.",
        "fewerThanOne": "פחות מהתרעה אחת מתוך 100 היא אמיתית.",
    },

    "s3": "מה תבנו", "s3_h": "כל רכיב, בידיים שלכם.",
    "s3_p": "אף מוצר אבטחה, מסחרי או בקוד פתוח, אינו בשימוש בקורס ואינו נלמד בו. אתם בונים שער קטן לסוכנים בכלים פתוחים וכלליים, רכיב אחד בכל מודול.",
    "build": [
        ("01", "סוכן קטן שקורא לכלים, והמתקפה שמפילה אותו"),
        ("03", "שער שבודק כל קריאה לכלי לפני שהיא מתבצעת"),
        ("04", "גלאים להזרקת הנחיות: תבניות ומסווג מאומן"),
        ("05", "ספים שנקבעים מתקציב התרעות שווא שנמדד"),
        ("06", "מערך הערכה על נתונים בצורה של קריאות לכלים אמיתיות"),
        ("07", "מערך תקיפה יזומה עם דוחות כיסוי כנים"),
        ("08", "מנוע מדיניות שמאשר, דוחה, או מעכב לאישור אדם"),
        ("09", "קווי בסיס התנהגותיים וגלאי רצפים"),
        ("10", "טוען מודלים שבודק לפני שהוא סומך"),
        ("11", "זיהוי מידע אישי, השחרה ומחיקה"),
        ("12", "יומן חתום שחושף שינויים, והרצה חוזרת של שינוי מדיניות"),
        ("13", "לומד מדיניות עם שלב צל"),
    ],

    "s4": "קנה מידה", "s4_h": "בונים בקטן. חושבים בגדול.",
    "s4_p": "כל מודול מסתיים במה שהרכיב הופך להיות במיליוני קריאות ביום, באלפי סוכנים ובצוותים רבים, מחושב מהמדידות שלכם.",
    "scale": [
        ("על המחשב הנייד", "40", "מ״ש", "הגלאי שלכם בודק קריאה לכלי ב־<strong>40 מילישניות</strong>. מדדתם אותו, אתם מבינים כל שורה בו, והוא רץ על 8GB זיכרון בלי GPU."),
        ("ב־50 מיליון קריאות ביום", "23", "ליבות", "אותו גלאי מעסיק <strong>כ־23 ליבות מסביב לשעון</strong>. איפה הוא רץ? מה קורה לקריאה כשהוא איטי או לא זמין? מי בודק את ההתרעות שלו?"),
    ],

    "s5": "תוכנית הלימודים", "s5_h": "חמישה־עשר מודולים ופרויקט גמר.",
    "s5_p": "כל מודול מסתיים במדידה שאתם מפיקים ומגינים עליה, לא בעמוד שקראתם. כ־105 שעות, בקצב שלכם, בעברית ובאנגלית.",
    "parts": [
        ("I", "יסודות", [("00", "התמצאות: למה אבטחת סוכנים היא בעיה סטטיסטית"), ("01", "הקמת המעבדה והסוכן שלכם"), ("02", "יסודות אבטחת מידע לאנשי נתונים"), ("03", "האנטומיה של סוכן ומשטח התקיפה שלו")]),
        ("II", "זיהוי", [("04", "הזרקת הנחיות, ישירה ועקיפה"), ("05", "גלאים הם מסווגים: שיעורי בסיס, תקציבים ונקודות עבודה"), ("06", "היגיינת הערכה ושינוי בהתפלגות"), ("07", "עמידות מול יריב ותקיפה יזומה")]),
        ("III", "אכיפה", [("08", "מציון להחלטה: מדיניות, עיכובים ובני אדם"), ("09", "זיהוי חריגות בהתנהגות וברצפים"), ("10", "שרשרת האספקה של ML"), ("11", "הגנה על מידע: מידע אישי, השחרה ומחיקה")]),
        ("IV", "תפעול", [("12", "ראיות: יומני ביקורת, הרצה חוזרת והערכה קונטרפקטואלית"), ("13", "למידת מדיניות מתעבורה, בבטחה"), ("14", "ממשל, ביקורת ורגולציה למהנדסים")]),
    ],
    "cap_label": "פרויקט גמר", "cap_h": "לבנות, ואז לשבור את של מישהו אחר.",
    "cap_p": "שער משלכם לתרחיש חדש, מסמך על קנה מידה, ודוח תקיפה יזומה על עבודה של משתתף אחר.",

    "s6": "תעודה", "s6_h": "הלימוד חינם. ההסמכה בתשלום.",
    "s6_p": "הקורס כולו פתוח. החלק היחיד בתשלום הוא המבחן המסכם, שנבדק בידי אדם.",
    "cert": [
        ("הקורס", "חינם", "אין צורך בחשבון כדי לקרוא.", ["כל שיעור, בנייה ובדיקה", "עברית ואנגלית", "ערכת פתיחה ובדיקות אוטומטיות לכל מודול", "שלכם, לחזור אליו מתי שתרצו"]),
        ("מבחן מסכם ותעודה", "בתשלום", "לבחירתכם. המחיר יפורסם עם הפתיחה.", ["פרויקט הגמר שלכם, נבדק באופן אישי", "משוב כתוב ומפורט", "תעודה חתומה שכל אחד יכול לאמת", "עמוד ציבורי שמקשר לעבודה שנבדקה, אם תרצו"]),
    ],

    "s7": "שאלות", "s7_h": "שאלות נפוצות.",
    "faq": [
        ("צריך רקע באבטחת מידע?", "לא. הקורס מניח היכרות עם Python, הסתברות ולמידת מכונה, ומלמד את אבטחת המידע מהיסוד."),
        ("מה צריך כדי להריץ אותו?", "מחשב נייד עם 8GB זיכרון, עם macOS,‏ Windows (עם WSL 2) או Linux. אין צורך ב־GPU. התקנת Docker והקמת המעבדה הן מודול בפני עצמו."),
        ("אילו מוצרים הקורס מלמד?", "אף אחד. אתם בונים כל רכיב בעצמכם בכלים פתוחים וכלליים, ובכל מקום שבו נבחר כלי, השיעור מציין גם חלופה."),
        ("הוא באמת חינמי?", "כן. כל שיעור, בנייה ובדיקה אוטומטית הם בחינם. רק המבחן המסכם, שנבדק בידי אדם, והתעודה שבאה אחריו הם בתשלום."),
        ("באילו שפות?", "עברית ואנגלית. הקוד, הפקודות והכלים נשארים באנגלית בשתי הגרסאות."),
        ("מתי הוא נפתח?", "הוא בהכנה. הצטרפו לרשימת ההמתנה כדי לשמוע כשהמודולים הראשונים יתפרסמו."),
    ],

    "cta_label": "רשימת המתנה", "cta_link": ["הצטרפו לרשימת", "ההמתנה"],
    "cta_fine": "מייל אחד כשהמודולים הראשונים מתפרסמים, ומדי פעם עדכון על התקדמות הקורס. כתבו ל־" + EMAIL + "; הכתובת שלכם תשמש רק לקורס הזה, ותוכלו לבקש להסיר אותה בכל עת.",
    "mail_subject": "Waitlist",
    "foot_copy": "© 2026 הגנה על סוכני AI", "foot_contact": "יצירת קשר", "foot_security": "אבטחה",

    "nf_title": "הדף לא נמצא · הגנה על סוכני AI", "nf_label": "404 · לא נמצא",
    "nf_h1": ["אין כאן", "כלום"], "nf_btn": "חזרה לדף הבית",
}

MARK = ('<svg viewBox="0 0 22 22" aria-hidden="true" focusable="false">'
        '<rect width="22" height="22" fill="var(--fg)"/>'
        + "".join(f'<rect x="{4 + 5.5 * (i % 3)}" y="{4 + 5.5 * (i // 3)}" width="3" height="3" fill="var(--bg)"/>' for i in range(9) if i != 2)
        + '<rect x="15" y="4" width="3" height="3" fill="var(--sig)"/></svg>')
ARROW = '<span class="arrow" aria-hidden="true">→</span>'


def head(t, prefix, title, canonical, noindex=False):
    display = "rubik-hebrew.woff2" if t["lang"] == "he" else "archivo-latin.woff2"
    body = "heebo-hebrew.woff2" if t["lang"] == "he" else "inter-latin.woff2"
    seo = '<meta name="robots" content="noindex">' if noindex else (
        f'<link rel="canonical" href="{SITE}{canonical}">'
        f'<link rel="alternate" hreflang="en" href="{SITE}/"><link rel="alternate" hreflang="he" href="{SITE}/he/">'
        f'<link rel="alternate" hreflang="x-default" href="{SITE}/">')
    return f"""<!doctype html>
<html lang="{t['lang']}" dir="{t['dir']}" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(t['description'])}">
{seo}
<meta name="theme-color" content="#e8e6df" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#060606" media="(prefers-color-scheme: dark)">
<meta property="og:type" content="website"><meta property="og:site_name" content="{E(t['brand'])}">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(t['description'])}">
<meta property="og:url" content="{SITE}{canonical}"><meta property="og:image" content="{SITE}/{t['og_image']}">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:locale" content="{'he_IL' if t['lang'] == 'he' else 'en_US'}"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{prefix}favicon.svg" type="image/svg+xml"><link rel="icon" href="{prefix}favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="{prefix}apple-touch-icon.png">
<link rel="preload" href="{prefix}assets/fonts/{display}" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{prefix}assets/fonts/{body}" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{prefix}assets/site.css">
<script>document.documentElement.classList.remove("no-js")</script>
</head>
<body>"""


def topbar(t, prefix, home):
    nav = "".join(f'<a class="label" href="{home}{h}">{E(l)}</a>' for h, l in t["nav"])
    mail = f"mailto:{EMAIL}?subject={t['mail_subject']}"
    return f"""
<a class="skip" href="#main">{E(t['skip'])}</a>
<header class="top">
  <a class="brand" href="{home}">{MARK}<span class="label">{E(t['brand'])}</span></a>
  <nav aria-label="Main">{nav}</nav>
  <div class="end">
    <a class="lang label" href="{prefix}{t['other_path']}" lang="{t['other_lang']}" hreflang="{t['other_lang']}">{E(t['other_label'])}</a>
    <a class="btn" href="{mail}" data-waitlist>{E(t['nav_cta'])}<span class="kbd" aria-hidden="true">W</span></a>
  </div>
</header>"""


def footer(t, prefix):
    return f"""
<footer class="foot label">
  <span>{E(t['foot_copy'])}</span>
  <nav aria-label="Footer">
    <a href="mailto:{EMAIL}">{E(t['foot_contact'])}</a>
    <a href="{prefix}.well-known/security.txt">{E(t['foot_security'])}</a>
    <a href="{prefix}{t['other_path']}" lang="{t['other_lang']}" hreflang="{t['other_lang']}">{E(t['other_label'])}</a>
  </nav>
</footer>
<script src="{prefix}assets/site.js" defer></script>
</body>
</html>
"""


def sec_head(n, label, h, p=None):
    para = f"<p>{E(p)}</p>" if p else ""
    return (f'<div class="sec-head reveal"><div class="label"><em>{n:02d}</em>{E(label)}</div>'
            f'<div><h2>{E(h)}</h2>{para}</div></div>')


def page(t, prefix):
    mail = f"mailto:{EMAIL}?subject={t['mail_subject']}"
    readout = "".join(f'<span class="label">{E(l)}<b class="{c}">{E(v)}</b></span>' for l, v, c in t["readout"])
    twins = "".join(f'<article class="twin reveal"><div class="label">{k}</div><h3>{E(h)}</h3><p>{E(p)}</p></article>' for k, h, p in t["twins"])
    builds = "".join(f'<li class="reveal"><span class="label">M{m}</span><span>{E(s)}</span></li>' for m, s in t["build"])
    scale = "".join(f'<div class="reveal"><div class="label">{E(k)}</div><span class="num">{E(n)}<small>{E(u)}</small></span><p>{p}</p></div>' for k, n, u, p in t["scale"])
    parts = ""
    for n, name, mods in t["parts"]:
        items = "".join(f'<li><span class="label">{m}</span><span>{E(s)}</span></li>' for m, s in mods)
        parts += f'<article class="part reveal"><div class="label">{n}</div><h3>{E(name)}</h3><ol>{items}</ol></article>'
    cert = ""
    for h, price, sub, items in t["cert"]:
        lis = "".join(f"<li>{E(s)}</li>" for s in items)
        cert += f'<div class="reveal"><span class="price">{E(price)}</span><h3>{E(h)}<small>{E(sub)}</small></h3><ul>{lis}</ul></div>'
    faq = "".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in t["faq"])
    L = t["calc_labels"]

    def slider(name, max_i, val):
        return (f'<div class="field"><label for="{name}"><span class="label">{E(L[name])}</span><output></output></label>'
                f'<input type="range" id="{name}" name="{name}" min="0" max="{max_i}" step="1" value="{val}"></div>')

    body = f"""
<main id="main">
  <section class="hero" aria-label="{E(t['brand'])}">
    <canvas data-field role="img" aria-label="{E(t['field_aria'])}"></canvas>
    <p class="kicker label"><i></i>{E(t['kicker'])}</p>
    <div class="word">
      <h1><span>{E(t['h1'][0])}</span><span>{E(t['h1'][1])}</span></h1>
      <div class="side"><p>{E(t['hero_p'])}</p><div class="readout">{readout}</div></div>
    </div>
  </section>

  <section>
    {sec_head(1, t['s1'], t['s1_h'], t['s1_p'])}
    <div class="twins">{twins}</div>
  </section>

  <section id="try">
    {sec_head(2, t['s2'], t['s2_h'], t['s2_p'])}
    <div class="calc reveal" id="calc">
      <div class="calc-controls">{slider('base', 8, 2)}{slider('tpr', 8, 7)}{slider('fpr', 6, 4)}{slider('calls', 4, 2)}</div>
      <div class="calc-out" aria-live="polite">
        <div><div class="label">{E(t['calc_big_label'])}</div><span class="big">1%</span></div>
        <p class="calc-sentence"></p>
        <div class="stats">
          <div class="stat"><span class="label">{E(t['calc_alerts'])}</span><span class="v" data-k="alerts"></span></div>
          <div class="stat"><span class="label">{E(t['calc_real'])}</span><span class="v" data-k="real"></span></div>
        </div>
        <div>
          <div class="alerts" role="img" aria-label="{E(t['calc_grid_aria'])}"></div>
          <div class="alerts-key label"><span class="real">{E(t['calc_key_real'])}</span><span>{E(t['calc_key_false'])}</span><span class="alerts-note"></span></div>
        </div>
      </div>
    </div>
    <script type="application/json" id="calc-strings">{json.dumps(t['calc_js'], ensure_ascii=False)}</script>
  </section>

  <section>
    {sec_head(3, t['s3'], t['s3_h'], t['s3_p'])}
    <ol class="build indent">{builds}</ol>
  </section>

  <section>
    {sec_head(4, t['s4'], t['s4_h'], t['s4_p'])}
    <div class="scale indent">{scale}</div>
  </section>

  <section id="curriculum">
    {sec_head(5, t['s5'], t['s5_h'], t['s5_p'])}
    <div class="parts">{parts}</div>
    <div class="capstone reveal"><span class="label">{E(t['cap_label'])}</span><strong>{E(t['cap_h'])}</strong><span class="d">{E(t['cap_p'])}</span></div>
  </section>

  <section id="certificate">
    {sec_head(6, t['s6'], t['s6_h'], t['s6_p'])}
    <div class="cert indent">{cert}</div>
  </section>

  <section id="faq">
    {sec_head(7, t['s7'], t['s7_h'])}
    <div class="faq indent reveal">{faq}</div>
  </section>

  <section class="cta">
    <a class="big-link reveal" href="{mail}">{E(t['cta_link'][0])}<br>{E(t['cta_link'][1])} {ARROW}</a>
    <div class="fine reveal"><span class="label"><em style="font-style:normal;color:var(--sig)">08</em>&nbsp; {E(t['cta_label'])}</span><p>{E(t['cta_fine'])}</p></div>
  </section>
</main>
"""
    return head(t, prefix, t["title"], t["path"]) + topbar(t, prefix, "./") + body + footer(t, prefix)


def not_found(t):
    body = f"""
<main id="main">
  <section class="nf">
    <canvas data-field aria-hidden="true"></canvas>
    <p class="label">{E(t['nf_label'])}</p>
    <h1>{E(t['nf_h1'][0])}<br>{E(t['nf_h1'][1])}</h1>
    <p><a class="btn" href="/">{E(t['nf_btn'])}</a></p>
  </section>
</main>
"""
    return head(t, "/", t["nf_title"], "/404.html", noindex=True) + topbar(t, "/", "/") + body + footer(t, "/")


def main():
    (ROOT / "index.html").write_text(page(EN, ""), encoding="utf-8")
    (ROOT / "he").mkdir(exist_ok=True)
    (ROOT / "he" / "index.html").write_text(page(HE, "../"), encoding="utf-8")
    (ROOT / "404.html").write_text(not_found(EN), encoding="utf-8")
    print("built index.html, he/index.html, 404.html")


if __name__ == "__main__":
    main()
