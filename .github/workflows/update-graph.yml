name: Update contribution graph

on:
  schedule:
    - cron: "0 */6 * * *"   # runs every 6 hours (00:00, 06:00, 12:00, 18:00 UTC)
  workflow_dispatch: {}      # lets you trigger it manually from the Actions tab
  push:
    branches: [main]         # also runs whenever you push to the repo

jobs:
  update-graph:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - name: Checkout repo
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Generate graph
        env:
          GH_USERNAME: gopicode777
        run: python scripts/generate_graph.py

      - name: Commit and push if changed
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add contribution-graph.svg
          git diff --quiet && git diff --staged --quiet || git commit -m "chore: update contribution graph"
          git push
