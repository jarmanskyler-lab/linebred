# LineBred

Hereford linebreeding analysis for the Mark Donald program. COI, blood percentage
to the two foundation sires, founder balance and mating planning over the full
10,575-animal herd book.

This folder IS the website. Nothing needs installing or building.

---

## Putting it online (about 5 minutes, one time)

1. Go to **github.com** and sign in (or create a free account).
2. Click **+** at the top right, then **New repository**.
3. Name it `linebred`. Leave it **Public**. Click **Create repository**.
4. On the next page click **uploading an existing file**.
5. Drag in **every file from this folder**: `index.html`, `app.js`, `data.json`,
   `sw.js`, `manifest.webmanifest`, `icon-180.png`, `icon-512.png`.
   (`README.md` and `refresh-numbers.py` are optional — they are notes and a script,
   not part of the site.)
6. Click **Commit changes**.
7. Go to **Settings** → **Pages** (left sidebar).
8. Under *Branch*, choose **main** and **/ (root)**. Click **Save**.
9. Wait a minute or two. The page will show your address:
   `https://YOURNAME.github.io/linebred/`

That address is the app. Open it on any device.

### Put it on your iPhone home screen

Open the address in Safari → tap **Share** → **Add to Home Screen**.
It then opens like an app, full screen, and works with no signal.

### A note on privacy

A free GitHub Pages site is readable by anyone who has the address. It is not
listed or searchable, but it is not private. If that matters, Cloudflare Pages
hosts the same folder for free and can put a password in front of it.

---

## Updating the numbers after you change the database

Every figure in the app — COI, blood percentage, occurrences, founder balance,
generations — is computed from the spreadsheet ahead of time and stored in
`data.json`. The app reads those values rather than recalculating them, which is
what makes it fast on a phone.

So when the spreadsheet changes, `data.json` is regenerated:

1. Send me the updated spreadsheet.
2. I rerun `refresh-numbers.py` against it, which rewrites `data.json` and stamps
   a new version.
3. You replace `data.json` (and `index.html` and `sw.js`, which carry the version
   stamp) in the GitHub repository.

The app picks up the new numbers the next time it is opened online. The version
stamp is what tells already-installed phones that something changed.

Nothing else in the folder changes on a data update.

---

## What is in each file

| File | What it is |
|---|---|
| `index.html` | The page itself, and the loading screen |
| `app.js` | The whole application, with React bundled in — no outside dependencies |
| `data.json` | All 10,575 animals plus every precomputed figure |
| `sw.js` | Makes the app work offline and notices new data |
| `manifest.webmanifest` | Lets it install to a home screen |
| `icon-180.png`, `icon-512.png` | Home screen icon |
| `refresh-numbers.py` | The generator that rebuilds `data.json` from the spreadsheet |

---

## Things worth knowing

**Animals you add in the app** are saved on that device only, in that browser.
They are layered on top of the shipped database and do not sync between your
phone and your computer. Anything you add has its numbers calculated live rather
than read from `data.json`, and anything descended from an animal you added or
whose parents you edited is also recalculated live, so you never see a stale
figure. Use **Reports → Backup** to get your additions out as a CSV.

**Eleven pedigree loops** exist in the source spreadsheet — animals recorded as
their own ancestor. They are listed in `data.json` under `cyclesRemoved`. The
link that closed each loop is severed in the shipped data, because a pedigree
that contains a loop makes any COI calculation run forever. The original value is
kept alongside as `sRaw`/`dRaw` so the defect stays visible and fixable in the
master spreadsheet.

**"Active"** means an animal you can actually breed: frozen semen on hand, in the
living herd, or an explicit active status. 211 animals qualify. A blank status
does not count as active.

**The ancestor table** on an animal's page ranks by coefficient of relationship,
which is genuinely pairwise and cannot be precomputed for every combination. It
is evaluated for the 60 strongest candidates by blood percentage to fill 10 rows.
Blood percentage and occurrences shown there are exact for every ancestor.
