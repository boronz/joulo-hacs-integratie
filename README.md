Joulo Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/default)

> **⚠️ Disclaimer & Unofficial Notice**  
> Dit is een **community-project** en is op geen enkele wijze gelieerd aan, officieel ondersteund door of ontwikkeld in opdracht van **Joulo**. Dit project is ontstaan als een persoonlijk initiatief om de integratie van Joulo-laadpalen en ERE-statistieken binnen Home Assistant zo eenvoudig en overzichtelijk mogelijk te maken.

---

## 📸 Functionaliteiten

* ⚡ **Live Laadsessies:** Status van de lader, actieve sessie (kWh) en laadstatus.
* 🔋 **Energie & ERE:** Totaal aantal geladen kWh (MID en Non-MID) en totaal opgebouwde ERE-credits.
* 💶 **Financieel Overzicht:** 
  * Verwachte jaaropbrengst (€)
  * Al uitbetaald bedrag (€)
  * Nog uit te betalen / gereserveerd (€)
  * Onverkochte ERE credits & prognose
  * Actuele indicatieve marktprijs per ERE (€/ERE)

---

## 🚀 Installatie

### Via HACS (Aanbevolen)

1. Zorg ervoor dat [HACS](https://hacs.xyz/) is geïnstalleerd in je Home Assistant instantie.
2. Ga in Home Assistant naar **HACS** > **Integraties**.
3. Klik rechtsboven op de **drie puntjes** en kies **Aangepaste repositories** (*Custom repositories*).
4. Vul bij **Repository** de URL van deze GitHub repository in.
5. Kies bij **Categorie** voor `Integratie`.
6. Klik op **Toevoegen** en zoek vervolgens in HACS naar **Joulo**.
7. Klik op **Downloaden** en herstart Home Assistant.

### Handmatige installatie

1. Download de nieuwste release van deze repository.
2. Kopieer de map `custom_components/joulo` naar je Home Assistant configuratiemap (`/config/custom_components/joulo`).
3. Herstart Home Assistant.

---

## ⚙️ Configuratie

1. Ga in Home Assistant naar **Instellingen** > **Apparaten & Diensten**.
2. Klik rechtsonder op **Integratie toevoegen**.
3. Zoek naar **Joulo**.
4. Vul je **Joulo API authorization token** in.
   > **Let op:** Vul de token in inclusief het voorvoegsel `Bearer `, bijvoorbeeld:  
   > `Bearer 2b79tJ...`
5. Klik op **Opslaan**. De integratie maakt nu automatisch het **Joulo** apparaat en alle sensoren aan.

---

## 📊 Beschikbare Sensoren

| Sensor Naam | Entiteit ID | Eenheid | Omschrijving |
| :--- | :--- | :--- | :--- |
| **Charger Status** | `sensor.joulo_charger_status` | - | Actuele status van de laadpaal |
| **Is Charging** | `sensor.joulo_is_charging` | - | `True` als de auto momenteel laadt |
| **Active Session kWh** | `sensor.joulo_active_session_kwh` | `kWh` | Verbruik van de huidige laadsessie |
| **Total MID kWh** | `sensor.joulo_total_mid_kwh` | `kWh` | Totaal geladen via MID-gecertificeerde lader |
| **Total ERE Credits** | `sensor.joulo_total_ere_credits` | ERE | Totaal aantal opgebouwde ERE-credits |
| **Total All kWh** | `sensor.joulo_total_all_kwh` | `kWh` | Totaal geladen via alle laders |
| **Verwachte Jaaropbrengst** | `sensor.joulo_verwachte_jaaropbrengst` | `€` | Geschatte netto jaaropbrengst uit ERE |
| **Al Uitbetaald** | `sensor.joulo_al_uitbetaald` | `€` | Totaal reeds uitbetaald bedrag |
| **Nog Uit Te Betalen** | `sensor.joulo_nog_uit_te_betalen` | `€` | Uitbetaalbaar + gereserveerd saldo |
| **Onverkochte ERE** | `sensor.joulo_onverkochte_ere` | ERE | Aantal credits dat nog verkocht moet worden |
| **Onverkochte Verwachte Opbrengst** | `sensor.joulo_onverkochte_verwachte_opbrengst` | `€` | Prognose van onverkochte credits |
| **Actuele ERE Marktprijs** | `sensor.joulo_actuele_ere_marktprijs` | `€/ERE` | Indicatieve marktprijs per ERE credit |

---

## 🔑 Hoe kom je aan een API Key?

Je vindt je API Key / Token in de **Joulo App** onder je profielinstellingen of ontwikkelaarsinstellingen, of via de Joulo helpdesk.

---

## 📄 Licentie

Gepubliceerd onder de **MIT Licentie**. Zie het `LICENSE` bestand voor meer informatie.