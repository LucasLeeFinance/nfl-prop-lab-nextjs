# NFL Prop Lab — Next.js V1

A $0-budget, Outlier-inspired NFL research interface. **All numeric football data currently shown is synthetic demonstration data** in `data/demo.ts`. It is NOT connected to live NFL statistics, injuries, FTN, or Underdog offers yet. This is an interactive frontend foundation, not a betting research tool yet.

## Free deployment

1. Create a **new** GitHub repository `nfl-prop-lab-nextjs` (do not overwrite your existing Streamlit repo).
2. Upload all the contents of this folder, retaining the `app/` and `data/` directories.
3. Visit https://vercel.com/new and sign in with GitHub.
4. Import the new repository. Select **Hobby (Free)**, framework **Next.js**, root directory `./`.
5. Click **Deploy**. No environment variables, API keys, database, or credit card are needed for this demo.
6. Use the generated `*.vercel.app` address.

## Running locally (optional)

Install Node.js, then run `npm install` and `npm run dev`. Visit http://localhost:3000.

## Working features

- Responsive dark UI with fixed left navigation on desktop
- Player and position-appropriate market selectors
- L5/L10/L20 game-window buttons
- Interactive hoverable chart and optional hypothetical comparison line
- Recent 5 versus previous 5 averages
- Opponent-defense ranking cards and practice-status presentation
- Searchable demo player board
- Explicit placeholders for unimplemented scheme and game-script data

## Planned integrations

- Export real player logs, defensive rankings, and injuries from the existing Python/nflreadpy pipeline to versioned JSON
- Calculate team score-state pass/run tendencies from nflverse play-by-play
- Add verified FTN scheme fields only where actually supported
- Fetch limited Underdog offers server-side with secret keys and strict caching; never expose API keys to the browser

No live API calls are made in V1. Do not use synthetic data to make betting decisions.
NFL Prop Lab Next.js deployment setup.
