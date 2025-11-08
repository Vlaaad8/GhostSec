## 🚀 Prezentare Generală

Securitatea cibernetică devine din ce în ce mai importantă într-o lume cu atacuri digitale aflate în continuă creștere. Proiectul **Pitch Sibiu** propune o soluție inteligentă, accesibilă și eficientă pentru detecția și analiza comportamentelor suspecte din trafic de rețea și log-uri.

Sistemul rulează pe un dispozitiv **Raspberry Pi**, asigurând un consum redus de energie, portabilitate și cost minim. Analiza artefactelor se realizează în timp real, iar un model LLM validează și explică riscurile într-un limbaj accesibil utilizatorilor.

---

## 👥 Echipa

Echipa noastră combină expertiza în securitate, software engineering și arhitectură de sisteme pentru a construi o soluție modernă, scalabilă și educațională.
Echipa a fost formata din:
  * Balahura Vlad
  * Hordoan Darius
  * Moga Antonia
  * Pricope Dorina
---

## ✅ Soluția

Proiectul propune o platformă inteligentă care:

* Analizează în timp real traficul de rețea și log-urile unui server.
* Identifică anomalii pe baza unor pattern-uri predefinite.
* Trimite datele suspecte către un **LLM** care acționează ca analist de securitate.
* Oferă explicații prietenoase și recomandări de bune practici.

Sistemul rulează pe **Raspberry Pi**, colectând date în timp real din rețea și servere (ex: Apache).

---

## 🧰 Tech Stack

### Backend

* **Python**
* **scapy / tshark** – captură și analiză de pachete
* **re & apache_log_parser** – analiză log-uri web
* **WebSockets** – transmitere alerte live
* **FastAPI** – API performant

### Frontend

* **Angular** – dashboard dinamic și interactiv

### Validare

Soluția a fost testată pe capturi de trafic și log-uri generate în medii virtualizate, simulând atacuri reale.

---

## 🎥 Descriere

Sistemul monitorizează în timp real:

* traficul de rețea (prin Raspberry Pi în *monitor mode*)
* log-urile serverului web

Activitățile suspecte sunt detectate și interpretate de un **LLM (GPT-5o)**, care:

* validează suspiciunea
* explică riscul pe înțelesul utilizatorului
* oferă recomandări pentru prevenție

Pe viitor, GPT-5o va fi înlocuit cu **GhostSec LLM**, un model antrenat specific pentru analiză de trafic și log-uri.


Mulțumim pentru interes!
