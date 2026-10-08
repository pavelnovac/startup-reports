#!/usr/bin/env python3
"""Build data.js from the parsed report plus a credibility read of each headline."""
import json
import re
from datetime import datetime

items = json.load(open("/tmp/startups.json"))

# verdict: holds | dressed | flex
# Judge the headline this report ranks, not the founder's entire personality.
V = {
"cal-ai": dict(verdict="dressed", score=42, signals=["Self-reported", "Acquisition run-rate", "Unit switch", "Only the founder's posts"],
line="The exit story and the $50M are the same person's posts, and “$1M revenue” became “$1M MRR” in two months.",
read="Cal AI's entire trail in this report is Zach Yadegari's own X posts. In September 2024 he said the app had passed $1M in total revenue. Eight weeks later the claim was $1M in monthly revenue. That is a different number, roughly twelve times larger, and nothing here separates App Store gross from what is left after Apple's cut, refunds, and churn. The later points ($1.8M MRR, $24M ARR, then $50M ARR at a MyFitnessPal acquisition) are internally consistent with a founder telling a sale story. They are not a ledger. The company may well have been bought. The $4.2M a month this report ranks is still an unaudited run-rate, published by the seller."),

"kit-convertkit": dict(verdict="holds", score=86, signals=["Self-reported", "Slow public curve", "Since 2013"],
line="A twelve-year company that published $33M, then $40M, then $50M ARR. Boring on purpose.",
read="Kit is self-reported, and it still looks like a business. Nathan Barry has put numbers in public for years, and the ones captured here move like an old SaaS company: $33M ARR in November 2022, $40M in March 2024, $50M+ by December 2025. About 15% a year, not a launch tweet. One timeline entry is an origin story ($2K to $100K MRR) rather than a current metric, and “$50M+” is rounded. Neither of those is the pattern of someone inventing a valuation. Treat the latest figure as the founder's ARR, not as Stripe, and it still holds up."),

"jenni-ai": dict(verdict="dressed", score=58, signals=["Self-reported", "Years of exact MRR", "Round $1M", "Group revenue"],
line="The early years are too specific to be a costume. The $1M headline is a round, group-level tweet.",
read="From 2019 to 2023 David Park posted numbers that are awkward to fake: $2,254 MRR and 24 subscribers, then $7K, $43,646, $53,895 and 4,057 subscribers, a $1.95M year. That trail is why this is not a pure flex. The headline is the weak part. September 2025 says $723K MRR “across all tools (Jenni Group)”. December 2025 says they were stuck at $8–9M ARR. April 2026 says “we hit $1M MRR”, a round milestone, still self-reported, for an academic-writing product grown on short-form ads. Those products collect heavy refunds and chargebacks, and this report never shows net revenue. Real company, dressed finish."),

"chatbase": dict(verdict="holds", score=93, signals=["Stripe via TrustMRR", "Odd cents", "12,424 subs", "Multi-year trail"],
line="The rare big number that is an exact Stripe balance, not a milestone tweet.",
read="Chatbase is what a real headline looks like next to the round ones: $863,632 MRR, 12,424 subscriptions, synced from Stripe on July 31, 2026, with $19.2M all-time. The public posts before that ($60K, $220K, $390K and 8,000 customers in December 2024) climb into the verified figure instead of leaping past it. Doubling from $390K to $864K over nineteen months is fast and plausible for a support-chatbot tool. This is the cleanest large number in the set."),

"lemlist": dict(verdict="dressed", score=52, signals=["Self-reported", "Frozen in Oct 2021", "Real company, dead data"],
line="The company is real. The $10M ARR this report ranks is five years old.",
read="lemlist's ramp is the founder's posts from a single year: $3M ARR in December 2020, $4M in February 2021, $8M in June, $10M in October 2021. Then the public record in this report stops. Ranking that as current monthly revenue in October 2026 keeps a five-year-old peak on the board. The early ramp was steep for cold email, but lemlist is a known product, not a phantom. The failure is freshness. The number is a 2021 postcard."),

"quittr": dict(verdict="flex", score=16, signals=["Self-reported", "Contradicts itself", "Approximate date", "Influencer MRR"],
line="A $600K MRR post and a later $250K summary cannot both be the business.",
read="QUITTR is the clearest showoff in the hundred. The growth lead says the app was at $200K MRR when he joined in October 2025 and at $600K MRR seven months later, and the report itself marks that second date as approximate. In July 2026 a third-party roundup says “QUITTR: $250K MRR in 5 months”. The co-founder then folds QUITTR together with Cal AI as “20M+ downloads and $50M ARR combined”. Round number, influencer distribution, App Mafia framing, no Stripe connection, and two public MRR figures that disagree by more than half. The $600K is there to be screenshot."),

"tally": dict(verdict="holds", score=80, signals=["Self-reported", "Stepped ARR", "Recent", "Known product"],
line="From $0 to $6M ARR over six years, in steps, with a team size attached. Not a miracle post.",
read="Tally never connected Stripe to this report, so the $6M ARR is still Marie and Filip's own post. The shape is why it holds: $0 MRR and 20 users in September 2020, $150K MRR in November 2024, then $2M, $3M, $4M, a specific $4.3M at the end of 2025, $5M in April 2026, $6M and 2.5M users on September 22, 2026. A team of five is named at the $2M mark. That is a 3.3× climb in twenty-two months after they were already at $150K, which is fast for forms and still looks like an operating curve. Self-reported, recent, and hard to confuse with a one-night flex."),

"wave-ai": dict(verdict="flex", score=22, signals=["Self-reported", "60× in 15 months", "Went quiet after the peak", "Solo “vibe coder”"],
line="Hit $6M ARR as a solo meeting-notes app, posted it, and has not shown a number since.",
read="Wave's trail is five posts and then silence. February 2024: past $100K ARR, solo, with AI. June 2024: $1M ARR. November 2024: $5M ARR, “doing all the engineering himself”, 22,000 paid subs. May 7, 2025: $6M ARR “as a vibe coder”. Meeting notes are a crowded, high-churn category, and a first-time solo founder multiplying ARR by sixty in fifteen months is the valuation post. The report date is May 2025. As of this report, seventeen months have passed with no newer figure. People who still have the revenue usually keep posting it. People who needed the screenshot stop at the top."),

"gojiberry": dict(verdict="holds", score=84, signals=["Stripe via TrustMRR", "Matches the tweets", "YC, so not indie anymore"],
line="Ugly-fast growth, and the $424,368 is Stripe's number, a bit above the founder's own tweet.",
read="Gojiberry's speed is the part that feels fake: about €1M ARR nine months after the idea, Y Combinator in March 2026, then $4.5M ARR by October 5. The October 8 TrustMRR figure is $424,368 MRR, which annualizes above the founder's $4.5M tweet from three days earlier. When the ledger is higher than the brag, the brag is not the problem. What does not hold is the word “indie”. They joined YC. The revenue figure itself is the clean one."),

"headshotpro": dict(verdict="dressed", score=46, signals=["Third-party peak", "Founder said it came down", "Dec 2024"],
line="Danny Postma's business is real. The $300K month is a peak he later walked back.",
read="HeadshotPro is ranked at $300K a month from a December 2024 Starter Story piece, plus a company-site claim of $10M+ since launch. The report's own flag says Postma later said revenue came down and is “stable at a beautiful number”, which is what you say when you will not put the new number next to the old one. AI headshots had a real gold rush, and $10M all-time for a product that sells a one-time photo pack is believable. Leaving the peak month on the leaderboard two years later is how a good year becomes a valuation."),

"outrank": dict(verdict="flex", score=20, signals=["Self-reported", "$300 to $300K", "Portfolio blending", "Same founder's other app is $22K"],
line="The $300K+ sits on a mirror-image tweet, and his verified other product is at $22K.",
read="Outrank's public math is a poster. About $300 MRR in January 2025, then “$300 → $300K MRR in 15 months” in April 2026, then “$300K+” in September. The plus sign does the work. The same month Tibo wrote that the portfolio (Revid, Outrank, SuperX) was at $1M MRR. SuperX, his product, is on TrustMRR at $22,111 MRR, and his own later posts put all products combined around $30–35K MRR, not $1M. A round triple-zero climb, a blended portfolio, and a verified sibling that does not back the story. This is the number you put in the deck."),

"plausible-analytics": dict(verdict="holds", score=83, signals=["Years of exact MRR", "Latest ARR is an estimate", "Still publishing subs in 2026"],
line="The ~$3.1M is a tilde. The decade of exact MRR underneath it is not.",
read="Plausible's latest dollar figure is a third-party estimate, ~$3.1M ARR at the end of 2024, so the precision of that headline is soft and the date is behind. The history under it is the opposite of a flex: $400 MRR, then $10K, then $42,624, $55,411, $71,311, $83,637 at $1M ARR. In July 2026 they still published operating stats, $22.2K of new MRR, +28.5% year over year, 20,183 subscriptions. Use the tilde. Don't throw out the company."),

"rezi": dict(verdict="holds", score=88, signals=["Stripe via TrustMRR", "11 years old", "Founder rounded up slightly"],
line="$251,967 from Stripe. The founder's “$3.2M ARR” is a small round-up of the same number.",
read="Rezi's headline is the TrustMRR balance on October 8, 2026: $251,967 MRR and $10.3M all-time. A September post said nearly 11,000 paying subscribers and $3.2M ARR. Twelve times $251,967 is about $3.02M, so the tweet is roughly six percent high. That is ordinary rounding, not a second business. The X trail is thin. The processor figure is not."),

"postiz": dict(verdict="holds", score=80, signals=["Stripe via TrustMRR", "7,325 subs", "The growth story is theatrical"],
line="The $250,460 is Stripe. “$3M ARR next week” is just that number, said with a drumroll.",
read="Postiz crossed into this report at $250,460 MRR and 7,325 subscriptions on October 8, 2026. A September 21 post said $200K MRR. On October 3 the founder compressed the history into “two years to $1M ARR, three months to $2M, $3M next week”. $250K MRR already annualizes to $3.0M, so “next week” is the current run-rate in costume. Theatrical, and the cash figure matches the processor. Believe $250,460. Ignore the countdown."),

"1lookup": dict(verdict="holds", score=78, signals=["Stripe via TrustMRR", "Cash swings hard", "ARR tweet uses a peak month"],
line="The $249.6K MRR is the calm number. His “$5M ARR” is a hot month times twelve.",
read="1Lookup's ranked figure is TrustMRR MRR, $249.6K, with a real history back to a few hundred dollars in 2022. The cash months are not that calm: July 2026 verified revenue was $495.8K, August $407K, September $397K. Usage and annual billing do that. In July he also talked about getting to $140K MRR, which is lower than the ledger, and in August he said he was past $5M ARR. $5M is what you get by annualizing a peak cash month, not by multiplying the MRR. The headline this report uses is the one that holds. The ARR line in the tweets does not."),

"justin-welsh-solopreneur-business": dict(verdict="dressed", score=40, signals=["Self-reported", "One spike month", "60% partner deals", "Streams shut down"],
line="A $1.04M November, mostly partner deals, averaged into a fake-looking SaaS MRR.",
read="Justin Welsh's $236K a month is a 2025 average: $2.834M for the year, about 91% margins, self-reported. Inside that year, November alone was $1,043,516, and he said 60% of it was partner deals. That is a media spike, not monthly recurring software revenue. The report also says he shut down three of his four top streams and is retooling for 2026. The money in 2025 was probably real. Sitting it on a leaderboard next to Stripe MRR, as if the average were still running, is the showoff."),

"kibu": dict(verdict="dressed", score=55, signals=["Stripe, then the key died", "Annual contracts", "Headline ≠ latest month"],
line="Real healthcare revenue. The $234K MRR is not what the last full month actually collected.",
read="Kibu sells software to disability-services providers, and TrustMRR did see the Stripe account. The months swing like contract billing: $309K in January 2025, $72K in June 2025, $449K in January 2026, $150K in March 2026. The ranked headline is $234.3K MRR, synced April 19, 2026, when the Stripe key expired. March, the latest full month in the trail, was $150K. So the number on the card is neither the latest cash month nor a fresh sync. Real company, stale and smoothed headline."),

"kitze-tinkerer-club-products": dict(verdict="flex", score=28, signals=["One-time sales", "9-day spike", "Key expired", "No MRR"],
line="A nine-day sales burst, the Polar key dies, and it is ranked like a $223K MRR company.",
read="TrustMRR shows no MRR for Kitze. The $223.3K is last-30-day revenue from one-time sales of products and a $299 club, and the Polar key expired on February 9, 2026. From February 1 to 9 the verified cash was $150.9K, then the feed stopped. Ranking a launch week as a monthly run-rate is the whole trick. He even explained the unit economics in public: one sale a day is “almost $10K MRR”. The $223K headline is that kind of sentence with extra zeroes. Some of that cash was real. It is not a $2.7M ARR business."),

"typingmind": dict(verdict="holds", score=87, signals=["Self-reported", "Exact dollars", "Bio is below the peak"],
line="Tony posts the ugly exact months, and the current bio is lower than last year's high.",
read="TypingMind is a bio line, $137K a month on October 8, 2026, not a Stripe sync. The trail around it is specific and points the wrong way for a flex: $148K in March 2025, $170,005 in April, $210K+ in December, then the bio steps down to $137K. People inflating a valuation do not publish a lower number than their own all-time high. It is still his word, and a chunk of it is one-time licenses rather than classic MRR. The direction of the updates is the tell that it is real."),

"prosp": dict(verdict="dressed", score=50, signals=["Stripe, expired Feb 2026", "Several ventures in one feed"],
line="The $128,005 was Stripe in February. Eight months later it is a leftover, and the posts mix products.",
read="Prosp's headline is honest about its age: TrustMRR, $128,005 MRR, last sync February 5, 2026, all-time only $507K. That all-time figure is a quiet check on the MRR. A business doing $128K every month does not have $507K of lifetime revenue unless the MRR just arrived or the two numbers are not the same Stripe view. The founder's posts jump from $36K MRR to “$1M ARR in 7 months”, and the report says the feed mixes several ventures. Believe that a Stripe account read $128K in February. Don't believe it is October's revenue for one product."),

"scrapingbee": dict(verdict="dressed", score=48, signals=["Self-reported", "ARR from 2022", "Exited 2025"],
line="The Oxylabs exit is the news. The $1.5M ARR is a 2022 blog post that never got updated.",
read="ScrapingBee was acquired by Oxylabs in June 2025, and the founder describes an eight-figure exit. That is a real outcome. The revenue figure this report ranks is a single post from June 22, 2022: $1.5M ARR after three years. There is no public number between the ARR post and the sale. An old ARR frozen next to an exit is how a stale metric keeps a high rank."),

"typefully": dict(verdict="dressed", score=60, signals=["Self-reported", "Exact dashboard figure", "Frozen in Feb 2024"],
line="$100,329 and a +4.87% footnote look like a real dashboard. That dashboard is from February 2024.",
read="Typefully's figure is oddly precise for a lie: $100,329 MRR, up 4.87% over 30 days, from a chart shared on February 5, 2024. An earlier post had them approaching $42K MRR. Precision like that usually means someone cropped a billing page. It does not mean the crop is still true. Thirty-two months later, this report has nothing newer. Rank it as a 2024 fact, not as a 2026 run-rate."),

"carrd": dict(verdict="holds", score=70, signals=["Self-reported", "Approximate", "Founder stopped posting numbers"],
line="AJ stopped sharing. The ~$100K is an old interview, and that restraint is the opposite of a flex.",
read="Carrd's latest figure is a soft one: about $100K MRR, from a 2024 interview, date approximate, after he had already said the product was past $1M ARR in 2021. He took a small seed round, then stopped giving specifics. A founder who wanted to pump a valuation would not go quiet at a round ~$100K while sitting on millions of sites. The number is fuzzy and old. It is not a costume. Treat “about $100K” as the last time he was willing to say, not as this month's Stripe."),

"senja": dict(verdict="holds", score=84, signals=["Self-reported", "Exact $88,200", "Later admitted it was stuck"],
line="He posted $88,200, then later said they were stuck. Stuck is not a flex.",
read="Senja's February 2026 number is $88,200 MRR, after a slow public climb through $60K, $65K, and $70K. On October 1, 2026 he said it was flat, stuck around $1M ARR for months, which is about $83K a month. The two figures agree, and the newer one is the less flattering one. Self-reported, a few months stale, and behaviorally credible."),

"fly-pieter-plane-game": dict(verdict="flex", score=18, signals=["Launch-week MRR", "17 days to $1M ARR", "Churn admitted", "Bio moved on"],
line="A browser game went from $0 to $87K MRR in seventeen days. That is a spike, not a company.",
read="Fly Pieter's whole revenue trail is one week in March 2025: $57K MRR, $67K the next day, $87K and “$0 to $1M ARR in 17 days” on March 11. The report says the founder later talked about high churn and drop-off, and his bio now points at vibejam.com for $44K a month. A vibe-coded multiplayer game monetized with sponsor ads can take a burst of payments at launch. Calling that burst MRR, and leaving it on a 2026 leaderboard, is the showoff. The number describes a week."),

"photo-ai": dict(verdict="holds", score=85, signals=["Self-reported bio", "Published the drop", "Long trail"],
line="The bio says $86K. Last year he was posting $150K. He put the decline in public.",
read="Photo AI's current figure is one line in Pieter Levels' X bio: $86K a month. Through 2025 he posted $120K, $130K, $138K with about 13% churn, then almost $150K. The bio is lower. A bio is not a dashboard screenshot, and photo-generation revenue moves with ad spend and model costs, so “MRR” here is closer to a monthly run than to contracted subscriptions. Publishing the haircut is the opposite of dressing the number for a raise."),

"bannerbear": dict(verdict="holds", score=82, signals=["Self-reported", "Five-year curve", "One point may be SGD"],
line="Five years of MRR posts that creep from $8K to $81K. One 2024 point is labeled in SGD.",
read="Bannerbear's October 2026 figure is Jon Yongfook's bio: $81K MRR. Behind it is a public curve since 2020, $100K ARR, $20K, $35K, $40K and 490 customers, $50K, then a September 2024 note of 70.5K MRR marked as SGD. If that point was Singapore dollars, it should not be read as US dollars next to the others. The rest of the curve, ending at a bio that continues the climb rather than jumping it, looks like the same bootstrapped API he has described for years. Self-reported, coherent, one currency footnote."),

"llm-gateway": dict(verdict="dressed", score=60, signals=["Stripe MRR is real", "Credits sitting beside it", "Article says $1.2M"],
line="Trust the $78,764 MRR. The $259,539 next to it is credits, and someone already wrote “$1.2M”.",
read="LLM Gateway's Stripe MRR on September 7, 2026 was $78,764, with about $1M all-time. The headline puts $259,539 of last-30-day volume beside it and says that includes credits. Credits are customer prepay sitting on the platform, not the company's revenue. A September 18 article then says “LLM Gateway at $1.2M”. Twelve times the MRR is about $945K. The extra comes from treating throughput as sales. The processor MRR holds. The number a skimmer remembers does not."),

"podawaa": dict(verdict="holds", score=77, signals=["Stripe via TrustMRR", "616 subs", "Short history"],
line="$66,063 and 616 subscriptions from Stripe. The “90% margins” line is just a tweet.",
read="Podawaa's ranked number is TrustMRR on October 8, 2026: $66,063 MRR, 616 subscriptions. A August post said $10K to $50K MRR in two years and 90% margins, and a September note cites $1.2M all-time. The margin claim is unsupported. The MRR and the sub count are the processor. The history on the chart is short, so this is a verified snapshot of a real billing account, not a long operating study. At about $107 per sub, the arithmetic is ordinary SaaS, not a miracle."),

"small-bets": dict(verdict="dressed", score=54, signals=["Exited", "Quarterly average called monthly", "Sold for $3.6M"],
line="The Gumroad sale is specific. The “monthly” figure is one good quarter from the year before.",
read="Small Bets was sold to Gumroad in April 2025 for $3.6M, half cash and half options. That deal structure is specific enough to take seriously. The monthly number this report uses is Q1 2024 revenue of $173K, divided by three, about $58K. One quarter, a year before the sale, averaged into a run-rate. It was a real education business. It is not a current MRR, and the quarter was a record, which is exactly the slice you pick when you want the rank."),

"feedbackpanda": dict(verdict="dressed", score=45, signals=["Exited in 2019", "Single remembered figure"],
line="A real, famous little exit. The $55K MRR is from 2019 and should not be on a 2026 board.",
read="FeedbackPanda is Arvid Kahl's canonical indie exit: built to about $55K MRR and sold, with the figure dated approximately to June 2019. A 2020 post thanks the buyer for transparent terms. Nothing about that is a 2026 flex. It is also not 2026 revenue. Leaving a seven-year-old exit MRR in the ranking inflates the “combined monthly revenue” of this list."),

"remote-ok": dict(verdict="dressed", score=44, signals=["Self-reported", "June 2023", "Gone from the 2026 bio"],
line="He said “over $50K a month” in 2023. In 2026 it is not in the bio anymore.",
read="Remote OK appears once: Pieter Levels listing it at over $50K a month on June 10, 2023. The report notes it is absent from his 2026 bio, while Photo AI, Interior AI, and Nomad List are still there at lower numbers. When he is willing to publish declines on the other products, a product that disappears from the bio is not still doing $50K. The old post was probably true that summer. It is a stale peak now."),

"transistor-fm": dict(verdict="dressed", score=47, signals=["Exact figures stopped in 2020", "“Millions in ARR”", "Unconfirmed 2025 estimate"],
line="A real podcast host. The ranked ~$50K MRR is from 2020, and everything after is a shrug.",
read="Transistor's early numbers are the detailed kind: $9,372 ARR, a first month around $1,400 with 46 customers, $10K MRR, $219,444 ARR. Then the trail goes soft. About $50K MRR sometime in 2020, “millions in ARR” in 2021, and a third-party 2025 guess around $4.5M ARR that the report itself calls unconfirmed. The founders stopped sharing exact numbers. The company is real. The figure on the card is a six-year-old approximation wearing a current rank."),

"trustmrr": dict(verdict="dressed", score=62, signals=["Stripe-verified", "Cash ranked above MRR", "One-time marketplace fees"],
line="The verifier's own MRR is $23,234. The card leads with $47,200 of last-30-day cash.",
read="TrustMRR is dogfooded: Stripe is connected, and both numbers are on the page. MRR is $23,234. Last 30 days is $47,200. September was $53K. All-time is $374,798. This is a directory plus a marketplace for buying startups, so a large share of the cash is one-time, not recurring. Leading with the bigger cash number, and storing $47,200 as the monthly rank, makes a lumpy marketplace look like a $47K MRR SaaS. The data is real. The label is the dress-up."),

"nutria-stealth-listing": dict(verdict="holds", score=68, signals=["Stripe via TrustMRR", "Anonymous product"],
line="The billing account is verified. You cannot tell what the product is, or who runs it.",
read="Nutria is a stealth listing: TrustMRR has $46.5K MRR and a nine-point history, and the report does not identify the product. Verification here means a payment processor is attached to the listing, not that you can audit customers, churn, or whether the Stripe account is the company you think it is. For a named product that is enough. For an anonymous one, hold the number lightly. It is still a ledger, not a tweet."),

"starter-story": dict(verdict="dressed", score=42, signals=["Self-reported", "A single month in 2020", "Cumulative all-time"],
line="December 2020 did $46K. That month is not a run-rate, and the other figure is lifetime revenue.",
read="Starter Story's latest exact month in this report is December 2020: $46K of revenue and 640K visitors. The other number is cumulative, $1.25M+ all-time by September 2022. Pat Walls built a real media property. Neither figure is “monthly revenue” in October 2026. A fat traffic month from six years ago, plus a lifetime total, is a résumé. It is not MRR."),

"closet-tools": dict(verdict="dressed", score=58, signals=["Self-reported", "Cents-level old books", "Flat since 2021"],
line="The 2019–2020 books look real, down to the cent. The ~$40K rank stopped moving in January 2021.",
read="Closet Tools posted figures that are hard to invent casually: $16,274.55 MRR at the end of 2019, $37,899.54 and 1,356 customers at the end of 2020, about $40K MRR on January 12, 2021. In October 2023 the founder said MRR had been flat, within 5%, for a year. So the number was probably real, and it was already old when he said it had stopped growing. It should not be read as this year's revenue."),

"simple-analytics": dict(verdict="holds", score=80, signals=["Stripe via TrustMRR", "Thin history", "Bio rounds up to $45K"],
line="Stripe says $38,176. The bio says $45K+. Small stretch, real subscription base.",
read="Simple Analytics removed its public MRR page and left a short trail: one TrustMRR snapshot, $38,176 MRR on October 8, 2026, and $1.9M all-time. The founder's bio says $45K+. That is about an 18% polish on the processor number, the mild kind. There is no monthly history here to see churn. The headline itself matches Stripe, so it holds, with the bio treated as marketing."),

"screenshotone": dict(verdict="holds", score=76, signals=["Self-reported", "Exact earlier months", "Tilde on the latest"],
line="The climb is in exact dollars. The latest “~$36K” is the only soft one.",
read="ScreenshotOne posted $5,598 MRR, then about $16K, $19.4K, and $19,771, and in December 2025 said he had turned down a seven-figure acquisition. The September 28, 2026 figure is ~$36K MRR, tilde and all. Going from $20K to $36K in ten months is a real jump, and the tilde means he did not want to be pinned to the dollar. Still a coherent self-reported curve, not a round milestone from zero. Self-reported, recent, slightly fuzzy at the top."),

"habitkit": dict(verdict="holds", score=74, signals=["MRR snapshot only", "Synced Sep 9, not Oct 8", "No history"],
line="One Stripe snapshot, $32.5K, a month before the report. No history, no taller tweet.",
read="HabitKit's TrustMRR entry is a single MRR snapshot, last synced September 9, 2026, at $32.5K. There is no revenue history, so a launch spike or annual plan would be invisible. The founder's nearby post says MRR is growing and August beat the year before, which does not quote a bigger number than the snapshot. Thin, slightly stale, and still a processor figure rather than a claim."),

"supergrow": dict(verdict="flex", score=30, signals=["Three numbers, one product", "Stale Stripe key", "$300K+ ARR vs $32K cash"],
line="The founder, the ARR line, and TrustMRR each describe a different company.",
read="Supergrow's card is three businesses stacked. In late 2025 the founder posted $20K MRR, then $23K, then “crossed $300K ARR”, which is $25K a month. TrustMRR, last synced February 28, 2026, shows $32,216 of cash in the last 30 days and also lists $79,479 of MRR. Those cannot all be the same month of the same SaaS. The Stripe key is stale. The headline keeps the “$300K+ ARR” anyway. This is quoting whichever number is most useful, and the useful one is not the cash."),

"sitegpt": dict(verdict="holds", score=81, signals=["Self-reported", "Slow climb", "“Very close to”"],
line="From $10K to “very close to $30K” over a year, said like someone reading a dashboard.",
read="SiteGPT's posts are hedged and sequential: $10,183 in August 2025, almost $13K, $14K, $15K, $190K ARR after two flat years, then “very close to $30K MRR” on September 17, 2026. “Very close” is not how you write a number for a valuation. It is still self-reported, and support-chatbot MRR can be padded with annual plans. The voice of the updates is someone tracking a real, modest curve."),

"uneed": dict(verdict="dressed", score=56, signals=["Approximate", "30-day cash, not MRR", "Rounded in 48 hours"],
line="Two posts, two days apart, move $28K of directory cash to “~$30K”.",
read="Uneed is a launch directory. On July 21, 2026 the founder said $28K of revenue in the past 30 days. On July 23 he said very close to $30K a month. The report ranks ~$30K. That is promo and listing revenue, lumpy by nature, rounded up within forty-eight hours, and labeled with a tilde. Not a fake company. A soft number wearing an MRR-shaped rank."),

"screen-studio": dict(verdict="dressed", score=50, signals=["Third-party", "Same $30K in 2022 and 2024", "Founder stopped sharing"],
line="A beloved Mac app. The $30K is an October 2024 article, and it matches the launch month from 2022.",
read="Screen Studio's ranked revenue is a Starter Story figure from October 23, 2024: $30K a month, 8,000 customers. The founder's own earlier comment, date approximate, was also about $30K in the first month after the November 2022 launch. He no longer shares exact numbers. By May 2026 he will say 25,000 people used it last month, still a team of five, no investors. Usage without a revenue update, and a revenue update that has not moved in the public record since launch, means we do not know the current number. The product is obviously real. The $30K is a stale outside estimate."),

"draftly": dict(verdict="holds", score=72, signals=["Dodo Payments via TrustMRR", "Choppy months", "“$300K ARR” runs ahead"],
line="The $21.6K MRR matches the processor. The “$300K ARR” tweet does not match the choppy year.",
read="Draftly's headline is the verified MRR, $21.6K, with last-30-day cash of $29.2K on Dodo Payments. The months bounce: $29K, $24K, $17K, $13K, $9.4K, then $29.9K in September 2026. In July the founder said he had “built a company to $300K ARR” and that revenue had doubled since an accelerator cohort, which was while the summer months were falling. $21.6K MRR annualizes to about $260K. The ranked number holds. The ARR sentence is the flex, and it is not the number this report leads with."),

"interior-ai": dict(verdict="holds", score=83, signals=["Self-reported bio", "Down from $50K", "Same founder publishes declines"],
line="The bio says $21K. In 2023 he was posting $50K. The cut is in public.",
read="Interior AI's current number is Pieter Levels' bio on October 8, 2026: $21K a month. In May and June 2023 he posted $30K, $44K, and over $50K MRR, and he has claimed margins above 99%, which on an image-generation product is a claim about price versus API cost, not a revenue claim. The revenue trail itself stepped down and stayed specific. A bio line is weak evidence. A bio line that is less than half the old MRR is not a pump."),

"autocontent-api": dict(verdict="holds", score=75, signals=["Stripe via TrustMRR", "Key expired July 2026", "Flat, boring curve"],
line="A flat ~$17K curve. The only problem is the Stripe key died in July, so it is three months stale.",
read="AutoContent's verified months climb and then sit: a few thousand in late 2024, around $14K through 2025, $16–17K in the first half of 2026, latest full month $16.9K in June. The headline is $17.0K MRR with a key that expired around July 9, 2026. Nothing in the trail is a spike dressed up as a run-rate. It is simply not an October number. Hold it as “about $17K when the sync stopped”."),

"supastarter": dict(verdict="dressed", score=52, signals=["One-time licenses", "A year divided by twelve", "No 2026 run-rate"],
line="$165K in 2025, divided by twelve, is not MRR. It is an average of license sales.",
read="supastarter sells a one-time SaaS kit. The posts that look like books are the monthly ones: $13,855 and 43 customers in August 2025, $14,099 in September, about $11K and 35 sales in December, $300K+ cumulative by November. The ranked “monthly” figure is the 2025 total, $165K, spread across the year, about $13.8K. That average hides that December was already softer, and 2026 is not in the headline. Real sales. Not a subscription base."),

"black-magic": dict(verdict="dressed", score=57, signals=["Self-reported", "Exact 2022 MRR", "Product then hit a wall"],
line="The $13K was a careful build-in-public. Then X changed API pricing and the updates stopped.",
read="Black Magic's 2021–2022 posts are a genuine build in public: $350 MRR, $460, $2K, $5K, $6K with ~17% churn, $7K, then about 800 customers and $13K MRR on October 16, 2022. In May 2023 Tony wrote that a $42K a month X API price threatened the product. There is no newer revenue figure. The $13K was probably real on that day. It is a historical marker for a product the platform economics turned against."),

"nomad-list-nomads-com": dict(verdict="holds", score=86, signals=["Self-reported bio", "Published a long decline", "Specific $12K"],
line="He says it did ~$50K a month for nearly ten years, and the bio now says $12K. That is a confession, not a pitch.",
read="Nomad List's ranked number is the October 8, 2026 bio: $12K a month. The older posts say over $50K a month in 2023, and in August 2025 he wrote that it had made about $50K a month for nearly ten years and was now dropping. Membership revenue that depended on a nomad boom can fall that far. He put the smaller number in the bio anyway. Self-reported, current, and pointed downhill."),

"podscan": dict(verdict="dressed", score=55, signals=["Self-reported", "Stopped at $2K", "August 2024"],
line="Not a flex. A $2K MRR update from August 2024 that never got a sequel.",
read="Podscan's public trail is three modest posts: $500 MRR, $1K after two months, $2K and +25% month over month in August 2024. Nobody pumps a valuation with $2K. The problem is only time. There is no figure after that, so the rank treats a two-year-old early MRR as current. Small, probably real when posted, and stale."),

"shipfast": dict(verdict="holds", score=90, signals=["Stripe via TrustMRR", "Peak was real", "Now $1,793"],
line="The legend is $1.27M all-time. Stripe says last month was $1,793. The collapse is the credible part.",
read="ShipFast's fame is the 2024 run: a February post about $250K, then verified months of $75K, $133K, $123K, $80K, $62K, $60K. The same ledger then shows the fade, $12K to $21K through late 2025, and $2K in September 2026. The October 8 headline keeps both the $1.27M all-time and the $1,793 last 30 days. He says affiliates were cut and AI hurt the boilerplate business. The all-time number is what gets quoted in bios. This report's current figure does not hide the corpse. Trust the $1,793."),

"cyberleads": dict(verdict="holds", score=92, signals=["Self-reported", "Published the collapse", "$40K down to $1,083"],
line="The most honest trail in the set: a peak, then the actual fall, down to $1,083.",
read="CyberLeads is ranked at $1,083 in September 2026, after a public history that peaks at $40K MRR in February 2024 and $750K total, then a January 2025 note that revenue had dropped 50% in 2024, then the 2026 figure. A founder inventing numbers to look valuable does not finish the chart at a thousand dollars. The old $40K should not be remembered as the business. The new number should. This one holds."),

"easlo": dict(verdict="flex", score=24, signals=["Lifetime total", "No monthly rate", "Frozen in 2022", "374K followers"],
line="$260K of lifetime template sales, from 2022, parked in a monthly-revenue ranking.",
read="Easlo's headline is not a rate. It is $260K of total online income by November 12, 2022: Notion templates and ebooks, 150,000 templates sold, told across a few cumulative posts ($22K, $27K, $125K, $260K). There is no MRR, no recent figure, and a very large audience for a very old cumulative total. Dropping a lifetime Gumroad number into a list of monthly revenue is how a follower count gets a revenue rank. The sales may have happened. The way they are framed is the flex."),

"base44": dict(verdict="dressed", score=48, signals=["Exit reported at $80M", "No ARR", "“+$1M ARR every 2.5 days”"],
line="The Wix price is a reported exit. There is still no revenue number, and the later ARR claim is absurd.",
read="Base44's headline is not MRR. It is an acquisition: Wix, $80M cash, about six months in, reported in June 2025, with a third-party note of 250K users and $189K of profit in the prior month. This report never gets a founder-stated ARR for the period that was sold. After the deal, the founder said the product was adding $1M of ARR every 2.5 days, and later cited 2M users and 1,000 new paying subs in a day. That velocity is a victory lap, not an operating metric. Take the reported sale price as a reported sale price. There is no revenue figure here to trust."),

"tailwind-ui-tailwind-labs": dict(verdict="dressed", score=50, signals=["Launch cash from 2020", "Founder published an 80% drop", "No current MRR"],
line="The $2M was a famous 2020 launch. He has since said revenue fell about 80%. There is no current MRR.",
read="Tailwind UI's number in this report is lifetime launch cash: about to cross $2M, said on August 2, 2020, for a product that launched that February. In January 2026 Adam Wathan said revenue was down about 80% and three of four engineers were laid off, because AI tools cut documentation traffic. He published the bad news. The report still has nothing to rank except the 2020 haul, which was never a monthly run-rate. Real business, wrong number for 2026."),

"cod-dex": dict(verdict="holds", score=84, signals=["Stripe via TrustMRR", "6,745 subs", "Thin public trail"],
line="$85,022 MRR and 6,745 subscriptions from Stripe. The X history is one post, and it matches.",
read="Codédex reached a public “$1M ARR” post in May 2026, almost four years after the founder quit his job. TrustMRR on October 8 reads $85,022 MRR and 6,745 subscriptions, which annualizes to about $1.02M. The tweet and the processor are the same number. There is almost no earlier public trail, so you cannot see the shape of the climb. You can see that the milestone was not inflated past the billings."),

"tinylaunch": dict(verdict="holds", score=84, signals=["Stripe via TrustMRR", "Explicitly not MRR", "Latest month $6.4K"],
line="All-time $110.9K, last full month $6.4K, and the report says there is no MRR. That is a straight accounting.",
read="TinyLaunch sells one-time launch listings. TrustMRR shows $110.9K all-time, a peak month of $18.2K in November 2025, and a run of ordinary months around $4–6K, latest full month $6.4K in July 2026, with no revenue recorded after August 18. The headline does not pretend this is MRR. All-time is the larger number and it is labeled all-time. This is what a non-recurring product looks like when nobody is forcing it into a SaaS costume."),
}

# Extra customs that override the default verified template.
V.update({
"laper": dict(verdict="holds", score=76, signals=["Stripe via TrustMRR", "60-day jump", "End state matches"],
line="He says $7K to $40K MRR in 60 days. Stripe says $40.1K. The speed is real cash, and it is still very new.",
read="Laper's founder posted a 60-day jump from $7,000 to $40,000 MRR on August 26, 2026. TrustMRR on October 8 reads $40.1K MRR, so the destination matches the processor even though the chart's earlier points are monthly totals rather than a long MRR history. A six-week quadrupling is exactly the window where annual plans and a launch spike get called recurring. The $40.1K is real billing. Durability is unproven."),

"launch-club": dict(verdict="holds", score=73, signals=["Stripe MRR", "Tweet says $91K", "Membership plus services"],
line="Ranked MRR is $34.0K from Stripe. The tweet people will repeat is “I did $91K last month”.",
read="Launch Club's headline matches TrustMRR: $34.0K MRR, with $1.27M all-time. On September 16, 2026 the founder said he did $91K last month, “verified by TrustMRR”. A membership mixed with done-for-you Reddit marketing can collect a fat cash month without that cash being MRR. He is not inventing the account. He is pointing at the bigger month. The number this report ranks is the MRR, and that one holds. The $91K is a different claim."),

"web3forms": dict(verdict="holds", score=77, signals=["Paddle via TrustMRR", "Five years to $10K", "Then a fast jump"],
line="Paddle confirms $41,789. The odd part is a product that took five years to reach $10K and then quadrupled.",
read="Web3Forms has the long, unglamorous trail of a real side project: $101.60 in February 2021, $196 MRR, $417, $1K after 3.5 years, $10K MRR in March 2026 after five years. By October 8, TrustMRR shows $41,789 MRR and 3,025 subscriptions on Paddle. A 4× jump in seven months after half a decade of crawling is the kind of move annual plans or a price change can create. The subscriptions are on the processor. Read the $42K as current billing, and don't pretend the slope is a five-year habit."),

"sleek": dict(verdict="holds", score=74, signals=["Stripe via TrustMRR", "Tweets run hotter", "605 subs"],
line="Stripe says $21.3K and 605 subscriptions. The posts say $26K and “almost $30K”.",
read="Sleek's ranked figure is the TrustMRR MRR, $21.3K. The founder posted “today $26K MRR” in May 2026 and later described a path to almost $30K. The ledger did not follow the adjectives. About a 20–40% gap between the tweet and the processor is common when someone annualizes a good week or counts trials. Use $21.3K. The climb he describes is ahead of the billings."),

"superx": dict(verdict="holds", score=81, signals=["Stripe via TrustMRR", "Portfolio tweets are larger", "This row is the product"],
line="SuperX itself is $22.1K on Stripe. The founder's $30–35K lines are “all products”, and they still don't rescue Outrank.",
read="SuperX's own TrustMRR number is $22,111 MRR. The founder's posts around it say $30K MRR “across his products” and, on day 481 of a $100K goal, $35K MRR for all products combined. Blended tweets are how a portfolio sounds bigger than any one product. They are also much smaller than the $1M portfolio claim attached to Outrank. This row is the verified product. It holds. Don't add the siblings back in by tweet."),

"localrank-so": dict(verdict="holds", score=80, signals=["Stripe via TrustMRR", "Personal income is a different number"],
line="The startup is $20.6K MRR. The $297K in his income report is his month, not this product.",
read="LocalRank's TrustMRR headline is $20.6K MRR. The founder's September 2026 income report says $297K in total, of which $62.8K came from a SaaS portfolio that includes LocalRank and others. Those are three nested numbers, and only the smallest is this product's recurring revenue. The report ranks the small one. That is the correct choice, and it holds."),

"angel-match": dict(verdict="holds", score=85, signals=["Stripe via TrustMRR", "Founder posted the decline"],
line="He says the high was $43K MRR and “today $27K”. Stripe says $24.4K. He published the slide.",
read="Angel Match's founder posted his own 2025 months around $37–42K and later wrote that the high was $43K MRR and the number now was $27K. TrustMRR reads $24.4K. He is a little above the processor and clearly not hiding the drop. Verified, current, and pointed the unflattering direction."),

"traxy-ai": dict(verdict="holds", score=79, signals=["Stripe via TrustMRR", "Founder rounded down"],
line="He says $500K ARR in five months. $50.2K MRR annualizes closer to $600K. The tweet is the modest version.",
read="traxy's TrustMRR figure is $50.2K MRR. The founder says the product hit $500K ARR five months after launch, with a goal of $1M by the end of 2026. Twelve times $50.2K is about $602K, so the ARR tweet is rounded down, not up. Fast, self-described, and the processor is ahead of the marketing. The headline holds."),

"flipify": dict(verdict="holds", score=78, signals=["Stripe via TrustMRR", "A hiring post said $21K"],
line="A hiring post said $21K a month. Stripe says $17.9K MRR. Close, and the ledger is the lower one.",
read="Flipify's ranked number is $17.9K MRR from TrustMRR. In July the founder, while hiring, described an app doing $21K a month. That is a modest upward gloss in a job post, not a different order of magnitude. Nine verified points sit under the headline. Use the Stripe figure."),

"chatbase-placeholder": {},
})

# remove placeholder
V.pop("chatbase-placeholder", None)

def clean_founder(s):
    s = re.sub(r"\s*\(@[\w]+\)", "", s)
    s = re.sub(r"^by\s+", "", s)
    return s.strip()

out = []
missing = []
for rank, i in enumerate(items, 1):
    custom = V.get(i["id"])
    if custom is None:
        if i["source"] != "verified" or i["flags"] or i["exited"]:
            missing.append(i["id"])
            continue
        n = i["n_points"]
        if n >= 8:
            hist = f"The chart has {n} recorded months, enough to show a spike or a collapse, and the latest point agrees with the headline."
            score = 86
        elif n <= 2:
            hist = "The history is short, a snapshot rather than a track record. The snapshot is still from the payment processor, not from a launch thread."
            score = 76
        else:
            hist = f"{n} recorded months sit under the headline, and they are processor totals."
            score = 82
        custom = dict(
            verdict="holds",
            score=score,
            signals=["Payment processor via TrustMRR", f"Synced {i['date']}", f"{n} data points"],
            line=f"TrustMRR reads {i['headline']}. The headline is the ledger.",
            read=f"{i['name']} is listed at {i['headline']}, taken from TrustMRR on {i['date']}. {hist} This is current billing on a connected Stripe, Paddle, Polar, or Dodo account. It does not certify margins, churn, or that every tweet around it is careful.",
        )
    handle = i.get("handle") or ""
    out.append({
        "id": i["id"],
        "rank": rank,
        "name": i["name"],
        "site": i["site"],
        "founder": clean_founder(i["founder"]),
        "handle": handle,
        "x": ("https://x.com/" + handle[1:]) if handle.startswith("@") else "",
        "followers": i["followers"],
        "category": i["category"],
        "mrr": i["mrr"],
        "date": i["date"],
        "source": i["source"],
        "exited": i["exited"],
        "headline": i["headline"],
        "asof": i["asof"],
        "desc": i["desc"],
        "flags": i["flags"],
        "timeline": i["timeline"],
        "verdict": custom["verdict"],
        "score": custom["score"],
        "line": custom["line"],
        "read": custom["read"],
        "signals": custom["signals"],
    })

if missing:
    raise SystemExit("missing verdicts: " + ", ".join(missing))

ids = {i["id"] for i in items}
extra = set(V) - ids
if extra:
    raise SystemExit("unknown ids in verdicts: " + ", ".join(sorted(extra)))

from collections import Counter
c = Counter(x["verdict"] for x in out)
print("counts", dict(c), "n", len(out))
for key in ("flex", "dressed", "holds"):
    s = sum(x["mrr"] for x in out if x["verdict"] == key and x["mrr"] > 0)
    print(f"  {key} ${s/1e6:.2f}M  n={c[key]}")

js = "window.STARTUPS = " + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";\n"
path = "/Users/pavelnovac/Work/dev/startup-reports/data.js"
open(path, "w", encoding="utf-8").write(js)
print("wrote", path, "bytes", len(js))
