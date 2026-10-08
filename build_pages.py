#!/usr/bin/env python3
"""Extract X screenshots and write the GitHub Pages site."""
import base64
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "indie-startups-report-2.html"
OUT_S = ROOT / "s"
MEDIA = ROOT / "media"

raw_js = (ROOT / "data.js").read_text(encoding="utf-8")
raw_js = raw_js.split("=", 1)[1].strip().rstrip(";")
STARTUPS = json.loads(raw_js)
BY_ID = {s["id"]: s for s in STARTUPS}

# tag: build | avoid | study | watch
# Homepage lists are ordered.
BUILD = [
"conductor", "screenshotone", "datafast", "calendesk", "capgo",
"pasul-ro", "localrank-so", "traxy-ai", "glossa-live", "flipify",
]
AVOID = [
"quittr", "outrank", "wave-ai", "shipfast", "fly-pieter-plane-game",
"photo-ai", "cal-ai", "cyberleads", "tailwind-ui-tailwind-labs",
"supergrow", "kitze-tinkerer-club-products", "easlo",
]
STUDY = [
"kit-convertkit", "chatbase", "tally", "gojiberry", "postiz", "rezi",
"plausible-analytics", "bannerbear",
]
EXTRA_AVOID = {
"codefast", "headshotpro", "interior-ai", "boothie", "trackai",
"nutria-stealth-listing", "draftly", "podawaa",
}

PITCH = {
"conductor": "A clean API in front of software that will never be rewritten.",
"screenshotone": "One endpoint that turns a URL into an image or a PDF.",
"datafast": "Analytics that answers which visit made money, not how many people bounced.",
"calendesk": "Booking, payments, and a client portal for one profession.",
"capgo": "The deploy button a popular framework forgot to ship.",
"pasul-ro": "A trust marketplace for one language and the people who left home.",
"localrank-so": "Rank tracking for a local Google listing, sold to people who already do the work.",
"traxy-ai": "A listener that turns a public buying signal into a lead.",
"glossa-live": "One room, every week, one job, priced by the hour.",
"flipify": "A scanner for people who already hunt underpriced listings.",
"quittr": "A consumer habit app whose two public MRR numbers don't match.",
"outrank": "Autopilot SEO at a round number the founder's other products don't support.",
"wave-ai": "Meeting notes, a solo $6M claim, then seventeen months of silence.",
"shipfast": "A starter kit whose own ledger shows the category already died.",
"fly-pieter-plane-game": "A game that went from zero to $87k MRR in seventeen days.",
"photo-ai": "AI photos of a person. The founder has already published the decline.",
"cal-ai": "Snap a meal, get calories. The giant already bought the winner.",
"cyberleads": "A monthly lead list that the founder watched fall from $40k to $1,083.",
"tailwind-ui-tailwind-labs": "UI kits that needed documentation traffic. The traffic left.",
"supergrow": "AI posts for LinkedIn, with three different sizes in the same story.",
"kitze-tinkerer-club-products": "A launch week of one-time sales, ranked like a company.",
"easlo": "Notion templates. A 2022 lifetime total, not a business you start now.",
"kit-convertkit": "Email for creators. Real, and twelve years taken.",
"chatbase": "A website chatbot at $863,632 of Stripe MRR. You are late.",
"tally": "Free forms that grew in steps to $6M ARR. Don't build another one.",
"gojiberry": "Buying-signal outbound, already in YC at $424k MRR.",
"postiz": "Social scheduling at $250k MRR on Stripe. The slot is full.",
"rezi": "AI resumes, eleven years in, $252k MRR. Entrenched.",
"plausible-analytics": "Privacy analytics with a decade of exact numbers. Occupied.",
"bannerbear": "An image API, five years to $81k MRR. Copy the shape, not the product.",
}

WHY = {
"conductor": "QuickBooks Desktop is not getting a lovely modern API, and the businesses stuck on it still need developers. Conductor charges for that door: $41.5k MRR on TrustMRR, current as of this report. The thing to copy is not QuickBooks. It is any ugly system a trade already refuses to leave — an industry ERP, a desktop POS, an old insurer portal — if you can sit in front of it and speak HTTP.",
"screenshotone": "ScreenshotOne does one job: render a URL to an image or PDF. The founder posted $5,598 MRR, then the exact teens, and by September 2026 about $36k. Bannerbear is the same shape five years further on, at $81k in the bio. Don't start a third generic screenshot API. Take the shape into one document your users already produce: proposals, certificates, marketplace cards, invoices.",
"datafast": "Counting pageviews is crowded, and Plausible already proved that market with a long public history. The open question is which visit turned into revenue. DataFast is aimed at that, at $30.7k MRR on Stripe, and the monthly points are still climbing. Clone the question. Point it at one billing setup or one kind of site, not at 'analytics' in general.",
"calendesk": "Therapists need a calendar, a payment, and a place the client comes back to. Calendesk sells those as one product, $21.6k MRR, verified, with a ten-point history. That is a profession, not a platform. Pick a licensed job in one country — and not therapists, if that slot is already staffed — and own the appointment plus the invoice. Another horizontal Calendly is not this idea.",
"capgo": "A Capacitor app still needs an app-store review to ship a JavaScript fix. Capgo sells the missing button: push the web bundle without waiting. About $32k MRR, open source, after the founder spent years at nothing. Don't clone Capacitor updates if you have never shipped a Capacitor app. Do look for the framework people around you already use, and sell the operational hole it left open.",
"pasul-ro": "Pasul matches Romanian-speaking clients, including people who live abroad, with vetted Romanian-speaking therapists. TrustMRR shows a steady climb, and the ranked figure is about $32k in the last 30 days, not a slogan. The clone is not a second English therapy app. It is a language and a diaspora you actually belong to, where trust is the product and a directory with a calendar is enough to start.",
"localrank-so": "LocalRank tracks and tunes Google Business Profile rankings. The product's verified MRR is $20.6k. The founder's income report is much larger because it mixes the rest of his month; that larger number is not this product. Agencies already pay someone to watch the map pack. A clone works as one vertical — dentists, law firms, clinics — with the report they already send a client. 'All local SEO' is how this becomes a feature of a bigger suite.",
"traxy-ai": "Traxy listens to public social posts and turns a buying signal into a lead list. It launched in 2026. Stripe says $50.2k MRR. The founder's '$500k ARR' tweet is lower than twelve times that MRR, which is the opposite of a pump. Gojiberry is the same idea at $424k MRR and already inside Y Combinator. Build a narrower listener: one trade, one phrase, one place people announce that they need help. Don't build another general LinkedIn agent.",
"glossa-live": "Glossa translates a church service, live, into a lot of languages, and charges by the hour from $5. Verified MRR is about $13.6k, founded in 2025. The money is small and the shape is the lesson: a room that happens every week, a job that has to be done during that hour, a price tied to the hour. Clone it for a room you can sit in — a clinic, a classroom, a town hall — not for churches, unless that is your room.",
"flipify": "Resellers already live in Facebook Marketplace, eBay, Craigslist, and OfferUp, looking for a price that is wrong. Flipify scans those listings for them. TrustMRR puts it near $18k MRR, close to the '$21k a month' in a hiring post. Clone it only for a category of goods you know how to resell. A general 'deal finder' is a weekend project with no edge.",
"quittr": "QUITTR is a quit-porn app sold through influencers. One post puts it at $600k MRR. A later roundup puts it at $250k. The co-founder then folds it into Cal AI as a combined '$50M ARR'. You cannot decide to spend a year on this using a number that disagrees with itself, and the distribution depends on ad accounts that ban this category. If you build a habit app, underwrite it with a processor screenshot, not with this one.",
"outrank": "Outrank is autopilot SEO: keywords in, articles out, '$300 to $300k MRR' as the story, then '$300k+'. The same founder’s verified product SuperX is at $22k MRR, and his all-products posts sit around $30–35k, not $1M. Meanwhile SEObot, ChatSEO, and Sorank — the same kind of product, on Stripe — are each around $30k. That is the real size of the idea. The $300k is the costume. Don't build an article mill because a tweet said the mill prints money.",
"wave-ai": "Wave is a meeting recorder and summarizer, built by one person, from $100k ARR to a claimed $6M in about fifteen months, posted in May 2025. This report has nothing after that. Otter, Granola, and the model companies already sit on the job. A peak followed by silence is not a map of the market. Don't start a notes app from this number.",
"shipfast": "ShipFast is a Next.js boilerplate. Stripe shows the arc people forget: $133k in April 2024, then a long fade, to $1,793 in the last 30 days of this report. The founder says AI hurt it. CodeFast, the course beside it, faded on the same kind of curve. The starter kit became the default output of the models. Don't build another one, and don't buy a course that teaches you to.",
"fly-pieter-plane-game": "Fly Pieter is a browser flight game, vibe-coded, monetized with in-game ads. The entire revenue trail is one week in March 2025: $57k, $67k, then $87k MRR and '$0 to $1M ARR in 17 days'. The report notes the churn, and the bio moved on to a different URL. A launch week can collect money. It is not a company to clone.",
"photo-ai": "Photo AI generates pictures of you from selfies. Through 2025 the posts climbed toward $150k MRR. The October 2026 bio says $86k. Interior AI, same founder, fell from over $50k to $21k. HeadshotPro's $300k month is a late-2024 article the founder later walked back. Boothie, a cousin that re-renders a selfie as a digicam photo, is a real smaller Stripe balance — and it is still the same idea. The year for this already happened.",
"cal-ai": "Cal AI turns a photo of a meal into calories. The public trail is the founder's posts: '$1M in total revenue' in September 2024, then '$1M MRR' eight weeks later, then a claimed MyFitnessPal acquisition at '$50M ARR'. TrackAI is the same job on Stripe at about $20k MRR, and there is a stealth calorie app on the same leaderboard. The feature just got bought by a giant. Cloning it now means competing with that giant, using a headline you cannot audit.",
"cyberleads": "CyberLeads sent B2B lead lists every month. The founder posted the whole life of it: a climb to $40k MRR in 2024, a note that 2024 cut revenue in half, and $1,083 in September 2026. That is the rare chart that argues against its own idea. Don't build a done-for-you list business and expect the 2024 peak to be the market.",
"tailwind-ui-tailwind-labs": "Tailwind UI sold component kits and lived off people visiting the docs. The $2M figure is launch cash from 2020, not a monthly rate. In January 2026 Adam Wathan said revenue was down about 80% and most of the engineering team was laid off, because AI answers replaced the documentation. Don't build a product that needs strangers to keep reading your docs.",
"supergrow": "Supergrow writes and schedules LinkedIn posts. Late 2025 posts say roughly $20–25k MRR and '$300k+ ARR'. TrustMRR, last synced February 2026, shows about $32k of cash in 30 days and also lists about $79k of MRR. Three sizes, one product, a stale key. 'Personal brand on autopilot' is a crowded demo. It is not a spec you should raise against.",
"kitze-tinkerer-club-products": "The ranked number is $223k in a recent 30 days. TrustMRR shows no MRR. The Polar key died on 9 February 2026 after $150.9k verified in nine days of one-time sales, a $299 club and some products. Ranking that week as a run-rate is the trick. A paid community can be real. A launch spike is not a company you model yours on.",
"easlo": "Easlo sold Notion templates. The headline is $260k of lifetime income by November 2022 — cumulative, old, and sitting in front of a very large audience. There is no monthly rate. Template shops had a moment when Twitter could still push a Gumroad link. That is not a 2026 company to start.",
"kit-convertkit": "Kit is email marketing for creators, in public since the early days, from $33M ARR to $40M to $50M+. The curve is slow and the company is real. It is also finished as a thing you clone. Use it as proof that a boring workflow, held for a decade, becomes a large company. Don't start ConvertKit.",
"chatbase": "Chatbase trains a support chatbot on a customer's own content. The number to remember is not a round tweet: $863,632 MRR, 12,424 subscriptions, Stripe, July 2026, with a trail that climbs into that figure. The category is won at the top and crowded underneath (SiteGPT is the honest ~$30k version). Don't build another embeddable chatbot unless you already own a distribution channel they don't.",
"tally": "Tally is a form that feels like a document, free until you need the paid features. The posts step from $0 in 2020 through $2M, $3M, $4.3M at the end of 2025, to $6M ARR in September 2026. Self-reported, recent, and shaped like an operating business. The lesson is free-first inside a tool people already need. The product itself is taken.",
"gojiberry": "Gojiberry finds warm B2B leads from public buying signals and starts the outreach. Stripe says $424,368 MRR on the day of this report, a bit above the founder's own tweet from three days earlier. They joined Y Combinator. The signal is a real market — traxy is the smaller, still-indie version of it. Study the signal. Don't clone the YC company feature for feature.",
"postiz": "Postiz schedules posts across a lot of networks. Stripe says $250,460 MRR and 7,325 subscriptions. The 'we’ll hit $3M ARR next week' line is just that MRR, said with a drumroll. Post Bridge is a smaller verified scheduler at about $49k. Two funded-by-customers products already sit on the job. A new scheduler needs a network or a user they are bad at, not a landing page.",
"rezi": "Rezi is an AI resume builder that started eleven years ago, long before the chatbot wave. TrustMRR reads $251,967 MRR. A founder tweet said $3.2M ARR, about six percent above twelve times the MRR. Ordinary rounding, old product, deep habit. You will not out-resume them with a wrapper.",
"plausible-analytics": "Plausible is the privacy-friendly analytics product with the long exact trail: $42,624 MRR, $55,411, $71,311, $83,637, then a softer ~$3.1M ARR estimate for the end of 2024, and they were still publishing subscriber counts in 2026. Simple Analytics is the other real one, at $38k MRR on Stripe. Don't start a third cookie banner alternative.",
"bannerbear": "Bannerbear generates images and video from templates, via an API, and the bio says $81k MRR after a public climb that started at a $100k ARR post in 2020. One 2024 point is labeled in SGD, so don't treat every dot as dollars. The idea is proven and occupied. ScreenshotOne is the younger cousin. If you build here, pick one document type, not 'banners'.",
"codefast": "CodeFast teaches non-developers to code and ship a SaaS. Stripe shows real 2025 months around $15–30k and about $7k in the latest full month, against $833k all-time. ShipFast, the boilerplate from the same world, fell to $1,793 in the last 30 days. The models now do the first version of what the course sold. Don't start another one.",
"headshotpro": "HeadshotPro made AI business portraits and had a real gold rush. The $300k month is a December 2024 article. The founder later said revenue came down and is 'stable at a beautiful number', which is what you say when you will not put the new number next to the old one. The company site still says $10M+ since launch. The wave is over. Don't build headshots in 2026.",
"interior-ai": "Interior AI redesigns a room from a photo. The 2023 posts went from $30k to over $50k MRR. The October 2026 bio says $21k. Same founder as Photo AI, which he also marked down. Virtual staging is a feature inside listing tools now. Don't start it as a company from the old screenshot.",
"boothie": "Boothie re-renders a selfie as a digicam photo, film stock, a poster. Stripe says about $44k MRR, so the cash is real and current. It is also the same selfie-to-picture idea as Photo AI and HeadshotPro, and those two have already published the comedown. A new filter app is a bet on distribution, not on an empty market.",
"trackai": "TrackAI is a photo calorie tracker, the same job as Cal AI, on Stripe at about $19.7k MRR. That is the honest size of a new entrant. Cal AI's public number is a founder's acquisition story, and MyFitnessPal is the reported buyer. You would be cloning a feature a giant just picked up.",
"nutria-stealth-listing": "Nutria is another calorie tracker, hidden behind a stealth listing, with about $46.5k MRR on a connected processor. You cannot see the product, the founder, or the churn. Combined with Cal AI's exit story and TrackAI's smaller verified twin, this is a crowded job with a bad comp. Don't pick it because a leaderboard row looks large.",
"draftly": "Draftly generates a cinematic site from a prompt. The verified MRR is $21.6k and the months swing from $9k to $30k. In the same season the founder said he had built a company to $300k ARR and that revenue had doubled, while several summer months were falling. Generating the first screen is a demo. The business is hosting, edits, and distribution, and this trail doesn't show those.",
"podawaa": "Podawaa sells LinkedIn engagement pods, scheduling, and analytics, at $66k MRR on Stripe, 616 subscriptions. The cash is real. The product depends on LinkedIn continuing to tolerate pods. That is a platform bet, not a thing to clone. If LinkedIn turns the dial, the MRR leaves with it.",
}

TAG_LABEL = {
"build": "Build this shape",
"avoid": "Don't build this",
"study": "Real, don't clone",
"watch": "Not a pick",
}
TAG_CLASS = {"build": "holds", "avoid": "flex", "study": "dressed", "watch": "dressed"}


def tag_of(sid, startup):
    if sid in BUILD:
        return "build"
    if sid in AVOID or sid in EXTRA_AVOID or startup["verdict"] == "flex":
        return "avoid"
    if sid in STUDY:
        return "study"
    return "watch"


def pitch_of(sid, startup):
    if sid in PITCH:
        return PITCH[sid]
    if startup["verdict"] == "flex":
        return "The public number is the showoff. Don't use it to choose a project."
    if startup["verdict"] == "dressed":
        return "A real-looking company with a headline you should not plan against."
    return "The ledger looks real. It is not one of the clearer things to start next."


def opener(sid, startup):
    if sid in WHY:
        return WHY[sid]
    t = tag_of(sid, startup)
    if t == "avoid":
        return "Don't build your next project from this headline. " + startup["read"]
    if t == "study":
        return startup["read"]
    if startup["verdict"] == "dressed":
        return "The company may be real. The figure on the card is a peak, a stale year, a cash month, or an average. " + startup["read"]
    return "The money looks real, and it is still not a recommendation to start a copy. " + startup["read"]


def extract_posts(html_text):
    found = {}
    for m in re.finditer(r'<section class="det" id="([^"]+)"(.*?)(?=<section class="det"|</div>\s*<script|$)', html_text, re.S):
        sid, body = m.group(1), m.group(2)
        posts = []
        for fig in re.findall(r'<figure class="post">(.*?)</figure>', body, re.S):
            pill_m = re.search(r'class="pill sm">(.*?)</span>', fig)
            cap = re.sub(r"<[^>]+>", " ", fig)
            cap = html.unescape(re.sub(r"\s+", " ", cap)).strip()
            href_m = re.search(r'href="(https://x\.com/[^"]+)"', fig)
            img_m = re.search(r'src="data:image/([a-zA-Z0-9+.-]+);base64,([^"]+)"', fig)
            date_m = re.search(r"</span>\s*([^·<]+)", fig)
            posts.append({
                "pill": html.unescape(pill_m.group(1)).strip() if pill_m else "Post",
                "date": date_m.group(1).strip() if date_m else "",
                "url": href_m.group(1) if href_m else "",
                "caption": cap,
                "mime": img_m.group(1).lower() if img_m else "",
                "b64": img_m.group(2) if img_m else "",
            })
        # claims from timeline, matched later by url
        claims = []
        for li in re.findall(r"<li>(.*?)</li>", body, re.S):
            if "tlab" not in li:
                continue
            tm = re.search(r"<time>(.*?)</time>", li)
            lab = re.search(r'class="tlab">(.*?)</span>', li)
            src = re.search(r'href="([^"]+)"', li)
            claims.append({
                "date": html.unescape(re.sub(r"<[^>]+>", "", tm.group(1))).strip() if tm else "",
                "label": html.unescape(re.sub(r"<[^>]+>", "", lab.group(1))).strip() if lab else "",
                "url": src.group(1) if src else "",
            })
        found[sid] = {"posts": posts, "claims": claims}
    return found


def ext_for(mime):
    if "png" in mime:
        return "png"
    if "webp" in mime:
        return "webp"
    if "gif" in mime:
        return "gif"
    return "jpg"


def save_posts(extracted):
    if MEDIA.exists():
        for p in MEDIA.rglob("*"):
            if p.is_file():
                p.unlink()
    saved = {}
    n_img = 0
    for sid, pack in extracted.items():
        out = []
        folder = MEDIA / sid
        for i, post in enumerate(pack["posts"], 1):
            rel = ""
            if post["b64"]:
                folder.mkdir(parents=True, exist_ok=True)
                name = f"{i}.{ext_for(post['mime'])}"
                (folder / name).write_bytes(base64.b64decode(post["b64"]))
                rel = f"../media/{sid}/{name}"
                n_img += 1
            labels = []
            for c in pack["claims"]:
                if post["url"] and c["url"] == post["url"] and c["label"] and c["label"] not in labels:
                    labels.append(c["label"])
            if len(labels) > 1:
                claim = "This post is cited for more than one point in the trail: " + "; ".join(labels)
            else:
                claim = labels[0] if labels else ""
            out.append({
                "pill": post["pill"],
                "date": post["date"],
                "url": post["url"],
                "src": rel,
                "claim": claim,
            })
        saved[sid] = out
    return saved, n_img


def e(text):
    return html.escape(text or "", quote=True)


def cite_sentence(posts):
    if not posts:
        return "The source report did not capture an X screenshot for this startup. The trail further down is the text record, and each row links to the original post."
    bits = []
    for p in posts:
        if p["claim"].startswith("This post is cited"):
            bits.append(f"the {p['pill'].lower()} ({p['date']}): {p['claim']}")
        elif p["claim"]:
            bits.append(f"the {p['pill'].lower()} ({p['date']}) is the source for “{p['claim']}”")
        else:
            bits.append(f"the {p['pill'].lower()} ({p['date']})")
    return "Cited from the captured posts, shown below: " + "; ".join(bits) + "."


def page_html(s, posts):
    sid = s["id"]
    tag = tag_of(sid, s)
    pitch = pitch_of(sid, s)
    body = opener(sid, s)
    cite = cite_sentence(posts)
    shots = []
    for p in posts:
        img = f'<img src="{e(p["src"])}" alt="{e(p["pill"] + " — " + s["name"])}">' if p["src"] else "<p>Screenshot missing. The post is linked below.</p>"
        claim = f"<br>{e(p['claim'])}" if p["claim"] else ""
        link = f'<a href="{e(p["url"])}" target="_blank" rel="noopener">Open on X</a>' if p["url"] else ""
        shots.append(
            f'<figure>{img}<figcaption><strong>{e(p["pill"])}</strong> · {e(p["date"])}{claim}<br>{link}</figcaption></figure>'
        )
    shots_html = "".join(shots) if shots else "<p>No screenshot was stored for this startup in the source report.</p>"
    flags = "".join(f'<p class="flag">{e(f)}</p>' for f in s.get("flags") or [])
    tl = []
    for t in s["timeline"]:
        src = f' <a href="{e(t["url"])}" target="_blank" rel="noopener">source</a>' if t.get("url") else ""
        tl.append(f'<li><time>{e(t["date"])}</time><div class="tv">{e(t["value"] or "•")}</div><div>{e(t["label"])}{src}</div></li>')
    links = []
    if s.get("site"):
        links.append(f'<a href="{e(s["site"])}" target="_blank" rel="noopener">Website</a>')
    if s.get("x"):
        links.append(f'<a href="{e(s["x"])}" target="_blank" rel="noopener">Founder {e(s.get("handle") or "")}</a>')
    followers = f'{s["followers"]:,} followers · ' if s.get("followers") else ""
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(s["name"])} — build or skip</title>
<meta name="description" content="{e(pitch)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Figtree:wght@400;500;600;700&family=Newsreader:ital,opsz,wght@0,6..72,500;0,6..72,650;1,6..72,450&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../styles.css">
</head>
<body>
<a class="skip" href="#main">Skip to the write-up</a>
<header class="wrap topbar">
  <a href="../index.html">All ideas</a>
  <form class="page-search" data-finder data-prefix="" action="../index.html" role="search">
    <input type="search" placeholder="Search a startup" aria-label="Search startups" autocomplete="off">
    <div class="hits" hidden></div>
  </form>
</header>
<main class="wrap page" id="main">
  <p class="kicker"><span class="stamp {TAG_CLASS[tag]}">{e(TAG_LABEL[tag])}</span></p>
  <h1>{e(s["name"])}</h1>
  <p class="byline">{e(s["founder"])} · {followers}{e(s["category"])}</p>
  <p class="lede">{e(pitch)}</p>
  <div class="links">{"".join(links)}</div>
  <p class="money">{e(s["headline"])}</p>
  <p class="byline">{e(s.get("asof") or "")}</p>
  <h2 class="sec">Should you build this</h2>
  <div class="prose">
    <p>{e(body)}</p>
    <p class="cite">{e(cite)}</p>
  </div>
  <h2 class="sec">Posts this is based on</h2>
  <div class="shots">{shots_html}</div>
  <h2 class="sec">What the product is</h2>
  <p class="prose">{e(s["desc"])}</p>
  {flags}
  <h2 class="sec">Public trail</h2>
  <ol class="timeline">{"".join(tl)}</ol>
</main>
<footer class="wrap foot"><p>Read against the 8 Oct 2026 report. Screenshots are the captured X posts from that file. A “don’t build” label is a reading of that public record, not a claim of fraud.</p></footer>
<script src="../catalog.js"></script>
<script src="../search.js"></script>
</body>
</html>
'''


def idea_link(sid):
    s = BY_ID[sid]
    return (
        f'<a class="idea" href="s/{e(sid)}.html">'
        f'<div class="nm">{e(s["name"])}</div>'
        f'<p>{e(PITCH[sid])}</p>'
        f'<div class="meta">{e(s["headline"])}</div>'
        f'</a>'
    )


def index_html():
    best = "".join(idea_link(i) for i in BUILD)
    worst = "".join(idea_link(i) for i in AVOID)
    study = "".join(
        f'<a href="s/{e(i)}.html"><b>{e(BY_ID[i]["name"])}</b></a>' for i in STUDY
    )
    all_links = []
    for s in STARTUPS:
        tag = tag_of(s["id"], s)
        all_links.append(
            f'<a href="s/{e(s["id"])}.html">{e(s["name"])}<small>{e(TAG_LABEL[tag])} · {e(s["headline"])}</small></a>'
        )
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>What to build right now</title>
<meta name="description" content="Best and worst startup ideas to clone, from the October 2026 indie revenue report. Search any of the 100 for the posts and the numbers.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Figtree:wght@400;500;600;700&family=Newsreader:ital,opsz,wght@0,6..72,500;0,6..72,650;1,6..72,450&display=swap" rel="stylesheet">
<link rel="stylesheet" href="styles.css">
</head>
<body>
<a class="skip" href="#best">Skip to the ideas</a>
<header class="wrap">
  <p class="kicker"><span>8 Oct 2026</span> · 100 startups · what is alive, and what to copy</p>
  <h1>What to build <em>right now</em>.</h1>
  <p class="dek">The report ranks whoever posted the biggest number. This page uses that trail for a different question: which ideas are actually happening, and which ones would waste the next year.</p>
  <p class="ro">Pe scurt: construiește unealta plictisitoare, cu bani verificați. Nu construi ce trăiește doar într-un tweet rotund.</p>
  <ul class="now">
    <li>The live, copyable money is a narrow job: a door onto old software, a URL-to-PDF endpoint, a calendar for one profession, a marketplace in one language, local rank tracking, the deploy button a framework forgot.</li>
    <li>The loud ideas are where the number fails or the category already broke: autopilot SEO, meeting notes, quit-porn apps, AI photos, calorie snaps, boilerplate, documentation kits.</li>
    <li>About half of the $18.6M in headlines on the original leaderboard is a peak, a stale year, or a flex. Don’t pick a project from the ranking alone.</li>
  </ul>
</header>
<main class="wrap">
  <div class="board">
    <section id="best">
      <h2>Best ideas to build</h2>
      <p class="intro">Ten shapes a new founder can still enter. Each one has current, credible revenue, and none of them is “clone the category leader.”</p>
      {best}
    </section>
    <section id="worst">
      <h2>Worst ideas to build</h2>
      <p class="intro">Twelve that look like opportunities on a leaderboard and are a bad brief once you read the posts.</p>
      {worst}
    </section>
  </div>
  <section class="study">
    <h2>Real, and too late to clone</h2>
    <p class="intro">The number holds. The slot is taken. Study the wedge, then build a narrower job.</p>
    <div class="study-row">{study}</div>
  </section>
  <form data-finder data-prefix="s/" action="#all" role="search">
    <div class="finder">
      <input type="search" placeholder="Search all 100 startups" aria-label="Search startups" autocomplete="off">
      <div class="hits" hidden></div>
    </div>
  </form>
  <details class="all" id="all">
    <summary>Browse all 100</summary>
    <div class="all-list">{"".join(all_links)}</div>
  </details>
</main>
<footer class="wrap foot">
  <p>Built from the 8 Oct 2026 research file. Open a startup for the X screenshots and the trail each call is citing. GitHub Pages: deploy this folder from the branch root.</p>
</footer>
<script src="catalog.js"></script>
<script src="search.js"></script>
</body>
</html>
'''


def main():
    print("reading report…")
    html_text = SRC.read_text(encoding="utf-8")
    extracted = extract_posts(html_text)
    print("sections", len(extracted))
    posts, n_img = save_posts(extracted)
    print("images", n_img)
    OUT_S.mkdir(exist_ok=True)
    catalog = []
    missing = [s["id"] for s in STARTUPS if s["id"] not in extracted]
    if missing:
        print("no section match", missing)
    for s in STARTUPS:
        sid = s["id"]
        sp = posts.get(sid, [])
        (OUT_S / f"{sid}.html").write_text(page_html(s, sp), encoding="utf-8")
        catalog.append({
            "id": sid,
            "name": s["name"],
            "founder": s["founder"],
            "category": s["category"],
            "headline": s["headline"],
            "pitch": pitch_of(sid, s),
            "tag": tag_of(sid, s),
        })
    (ROOT / "catalog.js").write_text(
        "window.CATALOG = " + json.dumps(catalog, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    (ROOT / "index.html").write_text(index_html(), encoding="utf-8")
    from collections import Counter
    print(Counter(c["tag"] for c in catalog))
    print("pages", len(list(OUT_S.glob('*.html'))))


if __name__ == "__main__":
    main()
