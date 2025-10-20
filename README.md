# 🎰 The House ALWAYS Wins

**Watch different betting strategies fail in real-time.** This simulator proves why no system can beat the roulette house edge.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)

---

## What's This?

A fun roulette simulator that shows 4 different players using different betting strategies. Spoiler alert: they all lose money in the long run (because math).

### The Players

- 🤖 **RandomBot** - Picks colors randomly (no strategy)
- 💚 **GreenHunter** - Always bets on green (risky!)
- 🔴 **MartyRed** - Uses the famous Martingale system on red
- ⚫ **MartyBlack** - Uses the famous Martingale system on black

Each starts with $1,000 and bets $10 per round.

---

## Quick Start

```bash
# Clone this repo
git clone https://github.com/M-GROSZ/house-ALWAYS-wins.git
cd house-ALWAYS-wins

# Install requirements
pip install streamlit pandas plotly

# Run it!
streamlit run Roulette_App.py
```

Open your browser to `http://localhost:8501` and hit the "Run Simulation" button. That's it!

---

## How It Works

**European Roulette has:**
- 18 red numbers
- 18 black numbers  
- 1 green number (0)

**The Problem:**
- If you bet on red/black, you win 48.65% of the time (not 50%)
- That 1.35% difference is the house edge
- Over time, you **will** lose money

**The Martingale Strategy:**

| Round | Bet | Total Risk |
|-------|-----|------------|
| 1 | $10 | $10 |
| 2 | $20 | $30 |
| 3 | $40 | $70 |
| 4 | $80 | $150 |
| 5 | $160 | $310 |

It doubles your bet after each loss. Sounds good until you hit a losing streak and go broke!

---

## What You'll See

Run 100 rounds and typically:
- **RandomBot**: Loses $50-$150 slowly
- **GreenHunter**: Either loses everything or wins big (crazy variance)
- **Martingale players**: Often go bankrupt around round 50-80

The chart updates live so you can watch the carnage unfold. 📉

---

## Features

✅ Real-time animated chart  
✅ Adjustable number of rounds (10-1000)  
✅ Download results as CSV  
✅ Detailed stats for each player  
✅ No flickering (smooth updates)  

---

## Why Did I Make This?

To show that **no betting system beats math**. Every strategy looks good short-term, but the house edge always wins eventually.

Perfect for:
- Understanding probability
- Learning why casinos always profit
- Showing friends why their "foolproof system" isn't
- Teaching responsible gambling

---

## Contributing

Got ideas? Cool! Feel free to:
- Add new strategies
- Improve the UI
- Fix bugs
- Make it prettier

Just fork, make changes, and submit a PR.

---

## ⚠️ Important

This is **educational only**. Don't use it as gambling advice. Real gambling = real money loss.

If you have a gambling problem: 
- 🇺🇸 Call 1-800-522-4700
  

---

## License

MIT License - do whatever you want with it!

---

<div align="center">

**Made with ❤️ to prove that math > luck**

⭐ Star this repo if it saved you money by NOT going to a casino!

</div>
