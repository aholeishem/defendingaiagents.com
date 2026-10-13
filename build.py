#!/usr/bin/env python3
"""Build the site's pages (English, Hebrew, 404) from one template.

Run:  python3 build.py
Writes index.html, he/index.html, 404.html and the blog (blog/index.html,
blog/<slug>/index.html, blog/feed.xml). Both languages share every structure;
only the strings differ, so a section added to one is added to both. The blog
is in English; each post's body is an HTML fragment in content/blog/<slug>.html.
"""
from __future__ import annotations

import html
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE = "https://defendingaiagents.com"
EMAIL = "shimon@defendingaiagents.com"
# The waitlist Worker (private repo, backend/waitlist). Set after `wrangler deploy`.
WAITLIST_URL = "https://waitlist.defendingaiagents.workers.dev"
AUTHOR = "Shimon R. Malka"
LINKEDIN = "https://www.linkedin.com/in/srmalka/"
E = html.escape

# Blog posts, newest first. Every reference carries a link that was checked by hand.
POSTS = [
    {
        "slug": "payload-splitting",
        "date": "2026-10-13",
        "title": "Payload splitting: when the detector and the model read different pages",
        "dek": "An attacker cuts an injection in the middle of a token and puts one unrelated line between the halves. Every pattern goes blind; the model reads straight through. The fix comes from network intrusion detection.",
        "tags": ["Prompt injection", "Detection", "Evasion"],
        "refs": [
            ("Kang, Li, Stoica, Guestrin, Zaharia, Hashimoto (2023). Exploiting Programmatic Behavior of LLMs: Dual-Use Through Standard Security Attacks.", "https://arxiv.org/abs/2302.05733"),
            ("Lee, Wei, Dong, Erichson (2026). Divide and Inject: Can Agents Reconstruct an Indirect Prompt Injection from Fragments?", "https://arxiv.org/abs/2609.36576"),
            ("Ptacek, Newsham (1998). Insertion, Evasion, and Denial of Service: Eluding Network Intrusion Detection. Secure Networks, Inc.", "https://insecure.org/stf/secnet_ids/secnet_ids.html"),
            ("Handley, Paxson, Kreibich (2001). Network Intrusion Detection: Evasion, Traffic Normalization, and End-to-End Protocol Semantics. USENIX Security.", "https://www.usenix.org/conference/10th-usenix-security-symposium/network-intrusion-detection-evasion-traffic-normalization"),
            ("Berners-Lee, Fielding, Masinter (2005). RFC 3986: Uniform Resource Identifier (URI): Generic Syntax, Appendix C.", "https://www.rfc-editor.org/rfc/rfc3986#appendix-C"),
            ("Kumar, Agarwal, Srinivas, Li, Feizi, Lakkaraju (2023). Certifying LLM Safety against Adversarial Prompting.", "https://arxiv.org/abs/2309.02705"),
            ("Debenedetti et al. (2024). AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents.", "https://arxiv.org/abs/2406.13352"),
            ("Zhan, Liang, Ying, Kang (2024). InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated Large Language Model Agents.", "https://arxiv.org/abs/2403.02691"),
            ("Zhang et al. (2024). Agent Security Bench (ASB): Formalizing and Benchmarking Attacks and Defenses in LLM-based Agents.", "https://arxiv.org/abs/2410.02644"),
            ("Evtimov et al. (2025). WASP: Benchmarking Web Agent Security Against Prompt Injection Attacks.", "https://arxiv.org/abs/2504.18575"),
        ],
    },
]

EN = {
    "lang": "en", "dir": "ltr", "path": "/", "other_path": "he/", "other_lang": "he", "other_label": "עברית",
    "title": "Defending AI Agents: a free course for data scientists",
    "description": "A free, build-it-yourself course that teaches ML engineers, statisticians and data scientists to secure AI agents, and to reason about what changes at scale.",
    "og_image": "og.png", "brand": "Defending AI Agents", "skip": "Skip to content",
    "nav": [("#curriculum", "Curriculum"), ("#certificate", "Certificate"), ("#faq", "FAQ"), ("blog/", "Blog")],
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
        ("05", "A retrieval store and memory that record where every entry came from"),
        ("06", "A membership-inference attack, and a differentially private release"),
        ("07", "Thresholds set from a false-positive budget, with a confidence bound"),
        ("08", "An evaluation harness on data shaped like real tool calls"),
        ("09", "A red-team harness and an adaptive attacker, with honest reports"),
        ("10", "Behavioural baselines and sequential detectors"),
        ("11", "Taint tracking, and an agent redesigned so injected text cannot act"),
        ("12", "Short-lived scoped credentials, a sandbox and a kill switch"),
        ("13", "A policy engine that allows, refuses, or holds for a person"),
        ("14", "Model and tool checks before anything is trusted"),
        ("15", "Personal-data detection, redaction and erasure"),
        ("16", "A signed, tamper-evident log, replay, and off-policy estimates"),
        ("17", "A policy learner that a patient attacker cannot train"),
        ("18", "An incident runbook, tested on a recorded attack"),
    ],

    "s4": "Scale", "s4_h": "Build it small. Reason about it at scale.",
    "s4_p": "Every module ends with what the same component becomes at millions of calls a day, thousands of agents and many teams, worked out from your own measurements.",
    "scale": [
        ("On your laptop", "40", "ms", "Your detector scores one tool call in <strong>40 milliseconds</strong>. You measured it, you understand every line, and it runs in 8 GB of memory with no GPU."),
        ("At 50 million calls a day", "23", "cores", "The same detector keeps about <strong>23 cores busy around the clock</strong>. Where does it run? What happens to a call when it is slow or down? Who reviews its alerts?"),
    ],

    "s5": "Curriculum", "s5_h": "Twenty modules and a capstone.",
    "s5_p": "Each module ends at a measurement you produce and defend, not at a page you have read. About 134 hours, self-paced, in English and Hebrew.",
    "parts": [
        ("I", "Foundations", [("00", "Orientation: why agent security is a statistics problem"), ("01", "Setting up your lab and your toy agent"), ("02", "Security fundamentals for data people"), ("03", "Anatomy of an agent and its attack surface")]),
        ("II", "Attacks", [("04", "Prompt injection and jailbreaks"), ("05", "Poisoning, backdoors and agent memory"), ("06", "Privacy attacks and differential privacy")]),
        ("III", "Measurement", [("07", "Detectors are classifiers: base rates, budgets, operating points"), ("08", "Evaluation hygiene and distribution shift"), ("09", "Adversarial robustness and red-teaming"), ("10", "Behavioural and sequence anomaly detection")]),
        ("IV", "Enforcement", [("11", "Secure by design: architectures injected text cannot steer"), ("12", "Identity, least privilege and containment"), ("13", "From score to decision: policy, holds and humans"), ("14", "The supply chain: models, packages and tools"), ("15", "Data protection: personal data, redaction, erasure")]),
        ("V", "Operations", [("16", "Evidence: audit trails, replay and counterfactual evaluation"), ("17", "Learning policy from traffic, safely"), ("18", "Monitoring and incident response for agents"), ("19", "Governance, audit and regulation for engineers")]),
    ],
    "cap_label": "Capstone", "cap_h": "Build it, then break someone else's.",
    "cap_p": "Your own design and gateway for a new scenario, run against a hidden attack suite; a scale memo; and a red-team report on another learner's work.",

    "s6": "Certificate", "s6_h": "Free to learn. Paid to certify.",
    "s6_p": "The whole course is open. The only paid part is the final exam, which a person reviews.",
    "cert": [
        ("The course", "Free", "No account needed to read.", ["Every lesson, build and test", "English and Hebrew", "A starter kit and automated checks for each module", "Yours to keep and revisit"]),
        ("Final exam and certificate", "Paid", "Optional. Price announced at launch.", ["Your capstone, reviewed personally", "Detailed written feedback", "A signed certificate that anyone can verify", "A public page linking your reviewed work, if you choose"]),
    ],

    "s7": "Questions", "s7_h": "Frequently asked.",
    "faq": [
        ("Why this course?", "We reviewed 24 university courses on machine-learning, LLM and agent security. None gives runtime defence of AI agents, or evaluation at production scale, more than a lecture or two. This course is built around both."),
        ("Do I need a security background?", "No. The course assumes Python, probability and machine learning, and teaches the security from the ground up."),
        ("What do I need to run it?", "A laptop with 8 GB of memory, running macOS, Windows (with WSL 2) or Linux. No GPU is required. Installing Docker and setting up the lab is a module of its own."),
        ("Which products does it teach?", "None. You build every component yourself with open, general-purpose tools, and wherever a tool is chosen the lesson names an alternative."),
        ("Is it really free?", "Yes. Every lesson, build and automated check is free. Only the final exam, which a person reviews, and the certificate that follows are paid."),
        ("In which languages?", "English and Hebrew. Code, commands and tools stay in English in both."),
        ("When does it open?", "It is in preparation. Join the waitlist to hear when the first modules are published."),
    ],

    "cta_label": "Waitlist", "cta_link": ["Join the", "waitlist"],
    "cta_fine": "One e-mail when the first modules are published, and occasional notes on how the course is going. Your address is used only for this course and is never shared. To be removed, write to " + EMAIL + ".",
    "wl_label": "Your e-mail address", "wl_placeholder": "you@example.com", "wl_button": "Join",
    "wl_msgs": {
        "sending": "Adding you…",
        "ok": "You are on the list. We will write when the first modules are out.",
        "invalid": "That does not look like an e-mail address. Check it and try again.",
        "busy": "Too many attempts from your network. Please try again in an hour.",
        "error": "The list could not be reached. Please try again, or write to " + EMAIL + ".",
    },
    "foot_copy": "© 2026 Defending AI Agents", "foot_contact": "Contact", "foot_security": "Security",

    "nf_title": "Page not found · Defending AI Agents", "nf_label": "404 · not found",
    "nf_h1": ["Nothing", "here"], "nf_btn": "Back to the home page",

    "blog_title": "Blog · Defending AI Agents", "blog_label": "Blog",
    "blog_h1": "Notes from the lab",
    "blog_p": "Technical posts on securing AI agents: attacks we reproduce, defences we build, and what they score when measured.",
    "blog_by": "By", "blog_min": "min read", "blog_refs": "References", "blog_all": "All posts", "blog_feed": "Atom feed",
}

HE = {
    "lang": "he", "dir": "rtl", "path": "/he/", "other_path": "", "other_lang": "en", "other_label": "English",
    "title": "הגנה על סוכני AI: קורס חינמי למדעני נתונים",
    "description": "קורס חינמי, שבו בונים הכול בעצמכם, שמלמד מהנדסי ML, סטטיסטיקאים ומדעני נתונים לאבטח סוכני AI, ולחשוב על מה שמשתנה בהיקף של ארגון גדול.",
    "og_image": "og-he.png", "brand": "הגנה על סוכני AI", "skip": "דילוג לתוכן",
    "nav": [("#curriculum", "תוכנית הלימודים"), ("#certificate", "תעודה"), ("#faq", "שאלות"), ("blog/", "בלוג")],
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
        ("05", "מאגר אחזור וזיכרון שמתעדים מאיפה הגיעה כל רשומה"),
        ("06", "מתקפת הסקת חברות, ופרסום נתונים בפרטיות דיפרנציאלית"),
        ("07", "ספים שנקבעים מתקציב התרעות שווא, עם רף ביטחון"),
        ("08", "מערך הערכה על נתונים בצורה של קריאות לכלים אמיתיות"),
        ("09", "מערך תקיפה יזומה ותוקף מסתגל, עם דוחות כנים"),
        ("10", "קווי בסיס התנהגותיים וגלאים סדרתיים"),
        ("11", "מעקב אחר מידע לא מהימן, וסוכן שתוכנן מחדש כך שטקסט מוזרק לא יכול לפעול"),
        ("12", "הרשאות קצרות וממוקדות, ארגז חול ומתג כיבוי"),
        ("13", "מנוע מדיניות שמאשר, דוחה, או מעכב לאישור אדם"),
        ("14", "בדיקת מודלים וכלים לפני שסומכים עליהם"),
        ("15", "זיהוי מידע אישי, השחרה ומחיקה"),
        ("16", "יומן חתום שחושף שינויים, הרצה חוזרת והערכה מנתונים קיימים"),
        ("17", "לומד מדיניות שתוקף סבלני לא יכול לאמן"),
        ("18", "נוהל טיפול באירוע, שנבדק על מתקפה מוקלטת"),
    ],

    "s4": "קנה מידה", "s4_h": "בונים בקטן. חושבים בגדול.",
    "s4_p": "כל מודול מסתיים במה שהרכיב הופך להיות במיליוני קריאות ביום, באלפי סוכנים ובצוותים רבים, מחושב מהמדידות שלכם.",
    "scale": [
        ("על המחשב הנייד", "40", "מ״ש", "הגלאי שלכם בודק קריאה לכלי ב־<strong>40 מילישניות</strong>. מדדתם אותו, אתם מבינים כל שורה בו, והוא רץ על 8GB זיכרון בלי GPU."),
        ("ב־50 מיליון קריאות ביום", "23", "ליבות", "אותו גלאי מעסיק <strong>כ־23 ליבות מסביב לשעון</strong>. איפה הוא רץ? מה קורה לקריאה כשהוא איטי או לא זמין? מי בודק את ההתרעות שלו?"),
    ],

    "s5": "תוכנית הלימודים", "s5_h": "עשרים מודולים ופרויקט גמר.",
    "s5_p": "כל מודול מסתיים במדידה שאתם מפיקים ומגינים עליה, לא בעמוד שקראתם. כ־134 שעות, בקצב שלכם, בעברית ובאנגלית.",
    "parts": [
        ("I", "יסודות", [("00", "התמצאות: למה אבטחת סוכנים היא בעיה סטטיסטית"), ("01", "הקמת המעבדה והסוכן שלכם"), ("02", "יסודות אבטחת מידע לאנשי נתונים"), ("03", "האנטומיה של סוכן ומשטח התקיפה שלו")]),
        ("II", "מתקפות", [("04", "הזרקת הנחיות ופריצת מגבלות"), ("05", "הרעלה, דלתות אחוריות וזיכרון של סוכנים"), ("06", "מתקפות על פרטיות ופרטיות דיפרנציאלית")]),
        ("III", "מדידה", [("07", "גלאים הם מסווגים: שיעורי בסיס, תקציבים ונקודות עבודה"), ("08", "היגיינת הערכה ושינוי בהתפלגות"), ("09", "עמידות מול יריב ותקיפה יזומה"), ("10", "זיהוי חריגות בהתנהגות וברצפים")]),
        ("IV", "אכיפה", [("11", "אבטחה כבר בתכנון: ארכיטקטורות שטקסט מוזרק לא יכול להטות"), ("12", "זהות, הרשאה מינימלית ובידוד"), ("13", "מציון להחלטה: מדיניות, עיכובים ובני אדם"), ("14", "שרשרת האספקה: מודלים, חבילות וכלים"), ("15", "הגנה על מידע: מידע אישי, השחרה ומחיקה")]),
        ("V", "תפעול", [("16", "ראיות: יומני ביקורת, הרצה חוזרת והערכה קונטרפקטואלית"), ("17", "למידת מדיניות מתעבורה, בבטחה"), ("18", "ניטור וטיפול באירועים בסוכנים"), ("19", "ממשל, ביקורת ורגולציה למהנדסים")]),
    ],
    "cap_label": "פרויקט גמר", "cap_h": "לבנות, ואז לשבור את של מישהו אחר.",
    "cap_p": "תכנון ושער משלכם לתרחיש חדש, שנבחנים מול סדרת מתקפות סמויה; מסמך על קנה מידה; ודוח תקיפה יזומה על עבודה של משתתף אחר.",

    "s6": "תעודה", "s6_h": "הלימוד חינם. ההסמכה בתשלום.",
    "s6_p": "הקורס כולו פתוח. החלק היחיד בתשלום הוא המבחן המסכם, שנבדק בידי אדם.",
    "cert": [
        ("הקורס", "חינם", "אין צורך בחשבון כדי לקרוא.", ["כל שיעור, בנייה ובדיקה", "עברית ואנגלית", "ערכת פתיחה ובדיקות אוטומטיות לכל מודול", "שלכם, לחזור אליו מתי שתרצו"]),
        ("מבחן מסכם ותעודה", "בתשלום", "לבחירתכם. המחיר יפורסם עם הפתיחה.", ["פרויקט הגמר שלכם, נבדק באופן אישי", "משוב כתוב ומפורט", "תעודה חתומה שכל אחד יכול לאמת", "עמוד ציבורי שמקשר לעבודה שנבדקה, אם תרצו"]),
    ],

    "s7": "שאלות", "s7_h": "שאלות נפוצות.",
    "faq": [
        ("למה הקורס הזה?", "סקרנו 24 קורסים אוניברסיטאיים באבטחת למידת מכונה, מודלי שפה וסוכני AI. אף אחד מהם לא מקדיש להגנה על סוכני AI בזמן ריצה, או להערכה בהיקף של סביבת ייצור, יותר מהרצאה או שתיים. הקורס הזה בנוי סביב שני הנושאים האלה."),
        ("צריך רקע באבטחת מידע?", "לא. הקורס מניח היכרות עם Python, הסתברות ולמידת מכונה, ומלמד את אבטחת המידע מהיסוד."),
        ("מה צריך כדי להריץ אותו?", "מחשב נייד עם 8GB זיכרון, עם macOS,‏ Windows (עם WSL 2) או Linux. אין צורך ב־GPU. התקנת Docker והקמת המעבדה הן מודול בפני עצמו."),
        ("אילו מוצרים הקורס מלמד?", "אף אחד. אתם בונים כל רכיב בעצמכם בכלים פתוחים וכלליים, ובכל מקום שבו נבחר כלי, השיעור מציין גם חלופה."),
        ("הוא באמת חינמי?", "כן. כל שיעור, בנייה ובדיקה אוטומטית הם בחינם. רק המבחן המסכם, שנבדק בידי אדם, והתעודה שבאה אחריו הם בתשלום."),
        ("באילו שפות?", "עברית ואנגלית. הקוד, הפקודות והכלים נשארים באנגלית בשתי הגרסאות."),
        ("מתי הוא נפתח?", "הוא בהכנה. הצטרפו לרשימת ההמתנה כדי לשמוע כשהמודולים הראשונים יתפרסמו."),
    ],

    "cta_label": "רשימת המתנה", "cta_link": ["הצטרפו לרשימת", "ההמתנה"],
    "cta_fine": "מייל אחד כשהמודולים הראשונים מתפרסמים, ומדי פעם עדכון על התקדמות הקורס. הכתובת שלכם תשמש רק לקורס הזה ולא תועבר לאיש. להסרה, כתבו ל־" + EMAIL + ".",
    "wl_label": "כתובת המייל שלכם", "wl_placeholder": "you@example.com", "wl_button": "הצטרפות",
    "wl_msgs": {
        "sending": "מוסיפים אתכם…",
        "ok": "נרשמתם. נכתוב כשהמודולים הראשונים יתפרסמו.",
        "invalid": "זו לא נראית כמו כתובת מייל. בדקו ונסו שוב.",
        "busy": "יותר מדי ניסיונות מהרשת שלכם. נסו שוב בעוד שעה.",
        "error": "לא הצלחנו להגיע לרשימה. נסו שוב, או כתבו ל־" + EMAIL + ".",
    },
    "foot_copy": "© 2026 הגנה על סוכני AI", "foot_contact": "יצירת קשר", "foot_security": "אבטחה",

    "nf_title": "הדף לא נמצא · הגנה על סוכני AI", "nf_label": "404 · לא נמצא",
    "nf_h1": ["אין כאן", "כלום"], "nf_btn": "חזרה לדף הבית",
}

MARK = ('<svg viewBox="0 0 22 22" aria-hidden="true" focusable="false">'
        '<rect width="22" height="22" fill="var(--fg)"/>'
        + "".join(f'<rect x="{4 + 5.5 * (i % 3)}" y="{4 + 5.5 * (i // 3)}" width="3" height="3" fill="var(--bg)"/>' for i in range(9) if i != 2)
        + '<rect x="15" y="4" width="3" height="3" fill="var(--sig)"/></svg>')
ARROW = '<span class="arrow" aria-hidden="true">→</span>'


def head(t, prefix, title, canonical, noindex=False, description=None, og_type="website", alternates=True, extra=""):
    display = "rubik-hebrew.woff2" if t["lang"] == "he" else "archivo-latin.woff2"
    body = "heebo-hebrew.woff2" if t["lang"] == "he" else "inter-latin.woff2"
    description = description or t["description"]
    seo = '<meta name="robots" content="noindex">' if noindex else f'<link rel="canonical" href="{SITE}{canonical}">' + (
        f'<link rel="alternate" hreflang="en" href="{SITE}/"><link rel="alternate" hreflang="he" href="{SITE}/he/">'
        f'<link rel="alternate" hreflang="x-default" href="{SITE}/">' if alternates else "")
    return f"""<!doctype html>
<html lang="{t['lang']}" dir="{t['dir']}" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(description)}">
{seo}{extra}
<meta name="theme-color" content="#e8e6df" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#060606" media="(prefers-color-scheme: dark)">
<meta property="og:type" content="{og_type}"><meta property="og:site_name" content="{E(t['brand'])}">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(description)}">
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
    nav = "".join(f'<a class="label" href="{home if h.startswith("#") else prefix}{h}">{E(l)}</a>' for h, l in t["nav"])
    return f"""
<a class="skip" href="#main">{E(t['skip'])}</a>
<header class="top">
  <a class="brand" href="{home}">{MARK}<span class="label">{E(t['brand'])}</span></a>
  <nav aria-label="Main">{nav}</nav>
  <div class="end">
    <a class="lang label" href="{prefix}{t['other_path']}" lang="{t['other_lang']}" hreflang="{t['other_lang']}">{E(t['other_label'])}</a>
    <a class="btn" href="{home}#waitlist" data-waitlist>{E(t['nav_cta'])}<span class="kbd" aria-hidden="true">W</span></a>
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

  <section class="cta" id="waitlist">
    <h2 class="big-link reveal">{E(t['cta_link'][0])}<br>{E(t['cta_link'][1])}</h2>
    <form class="wl reveal" action="{WAITLIST_URL}/join" method="post" novalidate>
      <label class="label" for="wl-email">{E(t['wl_label'])}</label>
      <div class="wl-row">
        <input id="wl-email" name="email" type="email" inputmode="email" autocomplete="email" autocapitalize="off" spellcheck="false" required maxlength="254" dir="ltr" placeholder="{E(t['wl_placeholder'])}">
        <button type="submit">{E(t['wl_button'])} {ARROW}</button>
      </div>
      <input type="hidden" name="lang" value="{t['lang']}">
      <div class="wl-hp" aria-hidden="true"><label>Website <input name="website" tabindex="-1" autocomplete="off"></label></div>
      <p class="wl-status" role="status" aria-live="polite"></p>
      {"".join(f'<p class="wl-note" id="wl-{k}" data-state="{k}">{E(v)}</p>' for k, v in t['wl_msgs'].items() if k != "sending")}
      <script type="application/json" id="wl-strings">{json.dumps(t['wl_msgs'], ensure_ascii=False)}</script>
    </form>
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


def fmt_date(iso):
    d = date.fromisoformat(iso)
    return f"{d.day} {d:%B %Y}"


def post_body(p):
    return (ROOT / "content" / "blog" / f"{p['slug']}.html").read_text(encoding="utf-8")


def minutes(body):
    return max(1, round(len(re.sub(r"<[^>]+>", " ", body).split()) / 230))


def byline(t, p, body):
    return (f'<p class="byline">{E(t["blog_by"])} <a href="{LINKEDIN}" rel="author">{E(AUTHOR)}</a></p>'
            f'<p class="label meta"><time datetime="{p["date"]}">{fmt_date(p["date"])}</time>'
            f'<span>{minutes(body)} {E(t["blog_min"])}</span>{"".join(f"<span>{E(x)}</span>" for x in p["tags"])}</p>')


FEED_LINK = '<link rel="alternate" type="application/atom+xml" title="Defending AI Agents: blog" href="{0}">'


def blog_index(t):
    prefix = "../"
    items = ""
    for p in POSTS:
        items += (f'<li class="reveal"><a href="{p["slug"]}/"><span class="label"><time datetime="{p["date"]}">{fmt_date(p["date"])}</time></span>'
                  f'<span><strong>{E(p["title"])}</strong><span class="d">{E(p["dek"])}</span>'
                  f'<span class="label">{E(t["blog_by"])} {E(AUTHOR)} · {minutes(post_body(p))} {E(t["blog_min"])}</span></span></a></li>')
    body = f"""
<main id="main">
  <section class="blog">
    {sec_head(1, t['blog_label'], t['blog_h1'], t['blog_p']).replace("<h2>", "<h1>").replace("</h2>", "</h1>")}
    <ol class="posts indent">{items}</ol>
    <p class="label indent feed"><a href="feed.xml">{E(t['blog_feed'])}</a></p>
  </section>
</main>
"""
    return (head(t, prefix, t["blog_title"], "/blog/", description=t["blog_p"], alternates=False, extra=FEED_LINK.format("feed.xml"))
            + topbar(t, prefix, prefix) + body + footer(t, prefix))


def post_page(t, p):
    prefix = "../../"
    body_html = post_body(p)
    url = f"/blog/{p['slug']}/"
    ld = {
        "@context": "https://schema.org", "@type": "BlogPosting", "headline": p["title"], "description": p["dek"],
        "datePublished": p["date"], "url": SITE + url, "image": f"{SITE}/{t['og_image']}",
        "author": {"@type": "Person", "name": AUTHOR, "url": LINKEDIN},
        "publisher": {"@type": "Organization", "name": t["brand"], "url": SITE + "/"},
    }
    extra = (FEED_LINK.format("../feed.xml") + f'<meta property="article:published_time" content="{p["date"]}">'
             f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>')
    refs = "".join(f'<li>{E(text)} <a href="{E(href)}">{E(href.split("://", 1)[1])}</a></li>' for text, href in p["refs"])
    body = f"""
<main id="main">
  <article class="post">
    <header class="post-head">
      <p class="label crumb"><a href="../">{E(t['blog_label'])}</a></p>
      <h1>{E(p['title'])}</h1>
      <p class="dek">{E(p['dek'])}</p>
      {byline(t, p, body_html)}
    </header>
    <div class="prose">
{body_html}
    </div>
    <footer class="prose refs">
      <h2 id="references">{E(t['blog_refs'])}</h2>
      <ol>{refs}</ol>
      <p class="label"><a href="../">← {E(t['blog_all'])}</a></p>
    </footer>
  </article>
</main>
"""
    return (head(t, prefix, f"{p['title']} · {t['brand']}", url, description=p["dek"], og_type="article", alternates=False, extra=extra)
            + topbar(t, prefix, prefix) + body + footer(t, prefix))


def feed(t):
    X = lambda s: html.escape(s, quote=False)
    entries = "".join(f"""
  <entry>
    <title>{X(p['title'])}</title>
    <link href="{SITE}/blog/{p['slug']}/"/>
    <id>{SITE}/blog/{p['slug']}/</id>
    <published>{p['date']}T00:00:00Z</published>
    <updated>{p['date']}T00:00:00Z</updated>
    <summary>{X(p['dek'])}</summary>
  </entry>""" for p in POSTS)
    return f"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Defending AI Agents: blog</title>
  <link href="{SITE}/blog/"/>
  <link rel="self" href="{SITE}/blog/feed.xml"/>
  <id>{SITE}/blog/</id>
  <updated>{POSTS[0]['date']}T00:00:00Z</updated>
  <author><name>{AUTHOR}</name><uri>{LINKEDIN}</uri></author>{entries}
</feed>
"""


def main():
    (ROOT / "index.html").write_text(page(EN, ""), encoding="utf-8")
    (ROOT / "he").mkdir(exist_ok=True)
    (ROOT / "he" / "index.html").write_text(page(HE, "../"), encoding="utf-8")
    (ROOT / "404.html").write_text(not_found(EN), encoding="utf-8")
    blog = ROOT / "blog"
    blog.mkdir(exist_ok=True)
    (blog / "index.html").write_text(blog_index(EN), encoding="utf-8")
    (blog / "feed.xml").write_text(feed(EN), encoding="utf-8")
    for p in POSTS:
        (blog / p["slug"]).mkdir(exist_ok=True)
        (blog / p["slug"] / "index.html").write_text(post_page(EN, p), encoding="utf-8")
    print(f"built index.html, he/index.html, 404.html, blog/ ({len(POSTS)} posts)")


if __name__ == "__main__":
    main()
