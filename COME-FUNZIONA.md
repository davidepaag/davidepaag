# Come funziona questa pagina

Tre immagini animate (SVG) messe in fila dal `README.md`. GitHub non permette programmi nella pagina del profilo,
ma fa muovere le animazioni che stanno dentro le immagini.

| File | Cosa è | Come si rifà |
|---|---|---|
| `cubo-ascii.svg` | il Cubo di Espandity fatto di lettere, che si scrive riga per riga | `python scripts/make_ascii_svg.py` (legge `assets/cubo.pgm`) |
| `info-card.svg` | la scheda accanto, stile terminale | cambia `RIGHE` in `scripts/make_info_card.py` e rilancialo |
| `contrib-heatmap.svg` | il calendario delle attività, aggiornato ogni giorno | lo rifà da solo GitHub Actions (`.github/workflows/aggiorna-profilo.yml`) |

- Nessuna libreria da installare: bastano Python 3 e, solo per cambiare la foto, ImageMagick
  (`convert foto.png -colorspace gray -depth 8 assets/cubo.pgm`). La foto va su fondo nero.
- Il calendario legge la pagina pubblica `https://github.com/users/davidepaag/contributions`: nessuna chiave.
- Le attività nei progetti privati si vedono solo se è acceso «Include private contributions on my profile»
  in https://github.com/settings/profile.
- Colori: quelli dello stile Espandity (rosa `#E0457B`, arancio `#F2994A`, turchese `#3FC1E0` solo per accenti).
