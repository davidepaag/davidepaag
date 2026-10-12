# re-lab

Laboratorio per studiare come funzionano le app (reverse engineering) e per costruire le nostre funzioni video.

## Installazione

In una sessione nuova:

```bash
bash re-lab/setup.sh
```

Lo script installa ciò che manca e segnala con ✘ cosa non è riuscito a scaricare.

| Strumento | A cosa serve | Da dove arriva |
|---|---|---|
| [REA](https://github.com/morluto/rea) | Analisi di app, siti e binari con l'AI | npm (`rea-agents`) |
| [Ghidra](https://github.com/NationalSecurityAgency/ghidra) | Decompilazione dei programmi nativi, usato da REA | zip ufficiale caricato nella release `ghidra` di questo repository |
| [whisper.cpp](https://github.com/ggml-org/whisper.cpp) | Sottotitoli automatici | compilato dal sorgente |
| FFmpeg | Montaggio ed effetti video | già presente nel sistema |

## Ghidra

La sessione cloud non può scaricare le release di altri repository, quindi:

1. Scarica lo zip da <https://github.com/NationalSecurityAgency/ghidra/releases>.
2. Crea una release con tag `ghidra` in questo repository e allega lo zip.
3. Rilancia `setup.sh` e confronta lo SHA-256 stampato con quello della pagina ufficiale.
