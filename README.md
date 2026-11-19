# The World in One Day — 19 November 2026

[![make.fun](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/coupcakes/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/coupcakes/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119)

An entry for the make.fun bounty
[Sum up 19 November's world news in one image](https://make.fun/bounty/news-image-20261119).

## What it is

`main.py` (Python 3, standard library only) draws a 1024×1024 newspaper-style
front page summing up the world news of Thursday 19 November 2026 and writes
it to `/output/entry.png`. No network, no external files, no fonts on disk:
the picture is drawn pixel by pixel with an embedded 5×7 bitmap font and
encoded as PNG by hand. It is deterministic — two runs write identical bytes.

## The day it sums up

- **Top story — Shenzhen:** Trump, Xi and Putin meet for the first
  three-way summit of the world's biggest nuclear powers (APEC sidelines);
  Ukraine, nuclear arms and Iran on the table.
- **The Hague:** the world court rules on the Rohingya genocide case —
  Myanmar's forces killed about 10,000 Rohingya in 2017.
- **Ukraine:** the Crimean bridge is hit again, traffic halted after a
  third strike in a week.
- **The Gulf:** Iran strikes Gulf states; Kuwait repels an attack after
  the US hit Qeshm island.
- **Antalya:** COP31 ministers race to unblock the final climate text.
- **Bangladesh:** Yunus's home torched amid unrest in 28 districts.
- **Markets:** Anthropic's $81bn record IPO values the AI firm at
  $1.5 trillion.
- **Also today:** a Van Gogh sells for a record $190.4m; Cyclone Akvan
  forces 100,000 to flee in India; Jeffries is set to be the first Black
  Speaker of the US House; measles returns in the US; GTA VI launches.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## License

MIT — see [LICENSE](LICENSE).
