---
name: weird-new-app
description: Use when implementing a weird/unhinged new app, website, game, browser extension, bot, distro, multiplayer server, or any other standalone thing — typically sourced from PostHog's #do-more-weird Slack channel (C04JN5NNMPF) or framed as a parody product, fake competing company, novelty platform (OnlyHogs/OnlyBugs/TWIG-style), personalized outbound game, themed software, AI gag, or "PostHog but as X". Triggers include "build me a weird app", "let's ship OnlyX", "I have an unhinged idea", "do more weird new repo", or any request to spin up a brand new repo for a fun side-thing (not a change to posthog.com or the PostHog app — use those skills if so).
---

# do-more-weird: ship a brand new weird thing

## What this is

Sometimes the best PostHog idea isn't a feature, it's a whole new product nobody asked for: OnlyHogs, TWIG, the Camo Detector, a Monty Python Google Meet extension, a Linux distro called PostHogOS, a Hacker-News-but-for-weird-apps, a personalized mini-game generated for an outbound prospect. None of those belong in the main repos. They want their own home.

Your job: take one of those ideas and turn it into a **repo any teammate (technical or not) can clone, run, and laugh at within 60 seconds**. If the bit lands you also push it to a private GitHub repo and give a one-line Vercel command.

## The single rule

**Ship the bit, all of it, in one sitting.**

Tiny + finished beats sprawling + 70%. A landing page with one perfect joke and a working button is funnier than a "platform" with three TODO files. If you can't finish it in one sitting, narrow the bit until you can. The proposer should be able to open it, click through, and tag the thread with the URL.

## When to use

- Idea was posted in #do-more-weird (or forwarded from there) and is a *new product*, not a change to an existing one
- "OnlyX" / "X for Y" / "TWIG" / "PostHog but as a [thing]" framings
- Browser extensions, Chrome extensions, Slack bots, Discord bots
- Parody landing pages and fake-company stunts
- Novelty single-page tools ("are you Barbados compliant?")
- Multiplayer game servers, Factorio mods, modded Minecraft realms
- Personalized outbound gags (one-off generated game / site per prospect)
- Themed distros, OS images, terminal toys, screensavers
- AI gags that genuinely need a model call (otherwise the static version is funnier)

## When NOT to use

- Easter egg, themed takeover, or new page on **posthog.com** → use `weird-posthog-dot-com`
- Weird thing inside the **PostHog app** (analytics product) → use `weird-posthog`
- A real product roadmap item dressed in jokes → that's normal product work, not this
- Anything that pretends to involve actual fraud, actual customer data leaks, or actual money movement. Parody safe, real fraud not. The joke can *look* like fraud (twig.com fake acquisition press release), but no real press wire goes out, no real customer DM gets sent, no real charge is made.

## Workflow

1. **Read the thread, not just the headline.** The funniest version is almost always a reply, not the original post. Look for the reply where someone escalated the bit ("I don't think she was negative enough, Joe. I say we do it."). Lean toward that.
2. **Pick a slug.** Short kebab-case noun phrase: `onlyhogs`, `twig-fake`, `camo-detector`, `flightradar-replays`, `meet-monty`. This is the directory name AND the repo name (`weird-<slug>` when pushed).
3. **Set up the repo.** `~/Code/weird/<slug>` is the directory. `git init`, write a `.gitignore` that fits the stack, make a first commit before you've written anything funny so the diff is clean for review.
4. **Pick the smallest stack that supports the bit.** See "Stack selection" below. Lean obnoxiously vanilla. A single `index.html` opened directly in a browser is the floor, and it's a perfectly cromulent floor.
5. **Build the bit end-to-end.** Front-load the funny. The first thing the user sees is the punchline; the rest is filler. If it has a form, the form has to actually do something (even if "do something" is "show a fake confirmation that's part of the joke").
6. **Write the README like the bit's billboard.** See "README" below — this is non-negotiable, the README is part of the comedy surface and also the only thing a non-technical teammate will read before deciding whether to run it.
7. **Open it in a browser and run the actual flow.** Use Claude in Chrome MCP. Type-checking proves nothing landed. Click the button. Watch the gag. Take a screenshot or a `gif_creator` recording for the Slack reply.
8. **Pause and ask before pushing or deploying.** Pushing to GitHub and deploying to Vercel are both visible-to-others actions. Show the user what you'd push and where, then wait for go-ahead.
9. **On approval:** create a **private** GitHub repo (`gh repo create PostHog/weird-<slug> --private --source=. --push`, fall back to user's personal namespace if PostHog org is wrong for this bit), then drop a one-liner Vercel command into the README so the proposer can deploy it themselves with one paste.

## Stack selection

Default mood: **the least amount of build tooling that still works.** Vanilla HTML beats a framework every time when the bit is single-frame. Reach for a framework only when the bit demands it (real state, multiple routes, server endpoints).

| Idea shape | Stack | Why |
|---|---|---|
| Single-page joke, landing page, fake-company site, "are you X compliant?", parody marketing page | One `index.html` + a `style.css` + maybe an `app.js`. No build step. Open the file directly. | The bit is the page. Zero install friction. The README says "double-click index.html". |
| Form that submits something, fake order page, fake signup, fake leaderboard | `index.html` + tiny serverless function on Vercel (`/api/*.js`), or just a `mailto:` link if even simpler | Vercel functions deploy free, no infra |
| Multi-page parody platform (OnlyHogs, OnlyBugs feed, Public Do-More-Weird HN clone) | Vite + React + TS, no router unless 2+ real routes | Familiar, fast dev loop, deploys to Vercel cleanly |
| Server-side rendered, SEO, blog-shaped parody | Next.js (App Router) + TS | Only when SSR is actually needed |
| Real-time / live data visualisation (Flight radar for session replays) | Vite + React + a websocket, or static-site + fake feed | Faked data is usually funnier than wiring real data |
| Chrome / browser extension (Monty Python on screen-share) | Manifest V3, vanilla JS, no bundler | MV3 + plain JS is the path of least resistance |
| Slack bot / Discord bot | Node + `@slack/bolt` or `discord.js`, a `.env.example`, deploy notes for Fly/Render | Bots need a real host; document it but don't auto-deploy |
| AI gag (needs an actual model call) | Static frontend + Vercel serverless endpoint that calls Anthropic. Use `claude-haiku-4-5` unless the bit needs Sonnet/Opus. **Always cache prompts.** | Cheapest model that lands the joke. Use the `claude-api` skill if it gets non-trivial |
| Personalized outbound game (one per prospect) | Static template + a small generator script that takes a JSON brief and outputs a new folder | The generator IS the product |
| Linux distro / OS image / themed terminal | Dockerfile or build script + a README a teammate could run on a fresh machine | The "repo" is the recipe |
| Multiplayer game server (Factorio etc.) | Docker compose + config files + README with `connect to host:port`. No real server in the repo. | Repo = config, not the binary |

When in doubt: **vanilla HTML, opened directly from disk, no install step.** That's the platonic shape of a weird app.

## README is part of the bit

The README is the only thing most teammates read before deciding to run your thing. Treat it as the second punchline.

**Required sections:**
- **Title** — the product name in big text. If the bit has a logo, embed it.
- **One-paragraph pitch** — written in the parody's own voice. ("OnlyHogs is the exclusive platform where dedicated fans support their favorite hoggies and get behind-the-scenes art." — committed to the bit, not winking at it.)
- **Credit** — "Originally proposed by [Name] in [#do-more-weird]([slack thread URL if known])." Always credit the proposer. If you don't have the thread URL, just the name is fine.
- **How to run** — assume the reader has nothing installed:
  - For HTML: "Double-click `index.html`."
  - For Node: "Install Node 20+ ([nodejs.org](https://nodejs.org)). Then in this folder: `npm install && npm run dev`."
  - For Docker: link to Docker Desktop install.
  - **Real, copy-pasteable commands.** Not pseudocode.
- **Deploy** (when applicable) — one block:
  ```
  npx vercel --yes
  ```
  Plus a link to sign up at vercel.com if they don't have an account. For non-Vercel deploys (Fly, Render, bots) give the equivalent.
- **What's the joke** (optional, sometimes funnier to omit) — a one-line "in case it's not obvious" deadpan.

**Tone:** Match the parody. An OnlyHogs README written in corporate engineering voice ruins the bit. An OnlyHogs README written like an actual OnlyFans creator's onboarding doc *is* the bit. Stay in character through the README, the variable names, and the commit messages.

## GitHub conventions

- **Default private.** `gh repo create PostHog/weird-<slug> --private --source=. --push`. Bits that punch outward (fake-acquisition press releases, parodies of named companies) stay private until someone with judgment greenlights making them public.
- **Personal namespace is fine** if the bit is more "Arthur's joke" than "PostHog's joke," or if it impersonates a real third party.
- **Description:** one-liner of the bit. The repo description shows up in `gh repo list` and in Slack unfurls, so don't waste it on "A weird app."
- **No CI** unless the bit needs it. CI on a 50-line HTML page is corporate overhead. Skip.
- **License:** skip licensing unless the user asks. Default to no LICENSE file — keeps it loose.
- **Commit messages:** Capitalize the first word, be terse, no co-author trailer. Stay in voice if you can ("Add disclaimer that lawyers refuse to acknowledge").

## Vercel deploy

For static, Vite, and Next.js, the path is:
```
npx vercel --yes
```
The first run will ask account questions; after that it's one command. Put the command **and a sentence telling the user where to find the preview URL** in the README. Do not deploy from the agent without explicit user go-ahead — Vercel deploys are publicly addressable URLs, even if not indexed.

If the bit is bot/server/distro-shaped and Vercel doesn't apply, give the equivalent in the README (Fly.io launch, Render quickstart, `docker run` for self-hosting, Nitrado for game servers).

## Voice & copy

PostHog's voice is **self-aware, slightly self-deprecating, never corporate-sincere about a joke**. Read the proposer's tone in the thread and match it. If they were deadpan, you're deadpan. If they were leaning unhinged, you lean unhinged.

Useful patterns:
- **Commit to the bit.** A parody marketing site that uses the real parody's voice (acquisition press releases, exit interviews, "we're hiring" pages) reads way funnier than one that hedges.
- **Disclaimers are part of the joke.** If the bit edges into "could this be confused for real," a one-line disclaimer (`Not affiliated with [Real Company]. This is a joke from PostHog.`) at the bottom of the page is the safety net AND a punchline. Don't strip it.
- **Reference real PostHog culture freely.** Killed products, the Barbados offsite, the small-yet-mighty thing, the mascot, AI cohosts that don't exist, anything self-aware about being a startup.

## PostHog culture vocabulary (use freely)

| Term | What it means |
|---|---|
| **Max** | PostHog's AI character. Goes-to choice for AI gags. |
| **jAImes / Jamse** | The running "AI co-CEO" joke persona. Pure fiction, fair game. |
| **Hedgehogs / hoggies** | The mascot. Reach for them often. Heidi and Lottie are the in-house artists. |
| **DeskHog** | PostHog's ESP32 hardware mini-device. Anchor for hardware-flavored bits. |
| **"Unc energy"** | The vibe descriptor for what counts as on-brand weird. |
| **Killed products** | Product Tours, Helm support, etc. Self-aware sunsetting references are encouraged. |
| **The Barbados offsite** | Recurring excuse / running joke about team gatherings. Camo, sunburns, productivity-during-vacation. |
| **Vibe-check** | What PostHog does instead of LGTM. Reviews are optional. |
| **do-more-weird** | The Slack channel. The genre. The instruction. |

## Common mistakes

- **Skeleton repo.** README has "TODO: write the bit," `index.html` has Lorem Ipsum. Don't ship until the bit lands. Tiny + complete > big + stubbed.
- **Picked a framework because it felt professional.** Vite + React for a one-page joke is over-engineering. The framework you picked is part of the message. Vanilla HTML is more PostHoggy.
- **Forgot the proposer credit.** They proposed it, they get the byline.
- **README in corporate voice.** Reads as if a different person wrote the repo and the readme. Stay in character.
- **Pushed without asking.** GitHub repos and Vercel URLs are visible to others. Confirm first.
- **Made it public by default.** Default private. Public is a separate decision.
- **Bit relies on a custom domain you didn't register.** Use the Vercel preview URL until someone okays domain spend. (See: the entire twig.com thread.)
- **Auto-deployed something that impersonates a real company.** Trademarked parodies are fine *as parody*, but get a human read first.
- **Implemented the real version of the joke instead of the joke.** "Personalized outbound games" is the bit; you don't need to wire it up to the CRM. The bit is one example game, hand-built, demonstrated as proof the concept lands.
- **Wrote tests.** Unless the bit IS that it has tests, don't.
- **Burnt context arguing about whether the bit is too unhinged.** It probably isn't. Pick the funniest implementable option and ship.

## Red flags — STOP

| Thought | Reality |
|---|---|
| "I'll pick the safer of the three thread replies" | Pick the funniest implementable one. |
| "Skeleton is fine, I'll fill it in later" | No. Tiny + complete. |
| "I'll write a serious README, the code is the joke" | The README is the joke's billboard. Stay in voice. |
| "Public repo is fine, it's just a joke" | Default private. Public is a separate decision the proposer makes. |
| "Vite + React for safety even though it's one page" | Lean vanilla HTML unless the bit demands more. |
| "Let me wire it up to real customer data / real outbound / real billing" | The bit is the gag. The real wiring is a separate decision and almost never necessary for the joke to land. |
| "I should add CI / lint / tests / a license" | Not unless asked. Strip ceremony. |
| "I'll register twig.com to make the bit hit harder" | Domains are spend. Use the Vercel URL until someone signs off. |
| "I'll push it to GitHub before showing the user" | Pause and confirm. Pushing is visible. |
| "I'll just deploy it to Vercel so they can see it live" | Same. Confirm first. |
| "The disclaimer kills the joke, I'll remove it" | The disclaimer often IS the joke. Keep it. |

## Quick reference: doing this in one pass

```
mkdir -p ~/Code/weird/<slug> && cd ~/Code/weird/<slug>
git init
# build the bit (favor vanilla HTML)
# write the README in the bit's voice, with run + deploy instructions
# open in Claude in Chrome, click through the gag, take a screenshot
git add -A && git commit -m "<terse, in-voice commit>"
# PAUSE — show user the repo + screenshot, ask before pushing/deploying
# on approval:
gh repo create PostHog/weird-<slug> --private --source=. --push
# then point user at: npx vercel --yes
```

That's the whole skill. Now go pick the funniest reply in the thread and ship it.
