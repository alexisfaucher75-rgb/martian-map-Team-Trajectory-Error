# Martian Map — navigation EVA (prototype)

« GPS martien » pour planifier une sortie à pied sur Mars — NASA Space Apps Challenge 2026,
défi *Interplanetary Survival Guide: Martian Map*.

## Lancer le site

```
python serve.py
```

Le navigateur s'ouvre sur **http://localhost:8000** (Python 3, aucune installation).
`serve.py` sert le site et relaie les requêtes de données NASA/USGS (contourne le blocage CORS du navigateur).

## Les 6 étapes

1. **Départ** : latitude / longitude Est, ou clic sur la carte.
2. **Date et heure de sortie** : date terrestre + heure martienne locale de départ →
   année martienne, saison (Ls), lever/coucher du soleil, jour restant, risque de tempêtes de poussière,
   givre matinal (algorithme Mars24, NASA GISS).
   + **Modèle climatique** au point et à l'heure de départ : Mars Climate Database v6 (LMD / ESA / CNES) —
   température de l'air et du sol, cycle de la journée, pression, vent, opacité de la poussière, ensoleillement,
   givre au sol, et le même point en scénario « tempête de poussière ».
   + **Relevés réels** des stations météo de Curiosity (REMS, Gale) et Perseverance (MEDA, Jezero) :
   dernier relevé + moyennes mesurées à la même saison les années précédentes.
3. **Scaphandre** : xEMU (référence), AxEMU, combinaison martienne cible NASA, EMU (ISS), A7LB (Apollo).
4. **Déplacement, charge et rayon d'action** : **à pied** ou **en rover** (LTV Artemis ou LRV Apollo),
   masse de l'astronaute, charge utile, vitesse, temps sur place, marge de sécurité.
   En rover : cercle vert = rayon de sécurité (règle Apollo : retour à pied possible en cas de panne),
   cercle bleu pointillé = rayon nominal (batterie / O₂ / durée).
   → consommation d'O₂, surconsommation due à la charge, **rayon d'action aller-retour** (cercle vert ;
   cercle orange pointillé = sans marge).
5. **Arrivée** : coordonnées ou clic ; la distance est comparée au rayon d'action.
6. **Itinéraire le plus sûr** : l'appli cherche le chemin qui consomme le moins d'oxygène en évitant les pentes
   dangereuses (interdites : ≥ 30° à pied, ≥ 20° LTV / 25° LRV ; au-delà de 15° le coût augmente très fortement).
   Trois passes : (1) algorithme A* sur toute la zone (≤ 900 × 900 cases), chaque case prenant la pente **la plus forte**
   mesurée à l'intérieur pour ne pas effacer les talus étroits ; (2) nouvelle recherche à pleine résolution (cases de 2 m avec
   HiRISE), morceau par morceau d'environ 1 km, dans un couloir autour du premier tracé ; (3) lissage du tracé, un raccourci n'étant accepté que s'il ne
   traverse aucun terrain plus pentu que le bout qu'il remplace. L'itinéraire est
   l'affiche en cyan, puis le **revérifie à pleine résolution** et le compare à la ligne droite (tableau comparatif).
   Analyse fine : pente mesurée à la meilleure résolution disponible dans un couloir autour
   de la ligne (± 25 à 250 m), morceau par morceau (HiRISE ~1 m → CTX 20 m → MOLA 463 m).
   → couloir coloré sur la carte, profil d'altitude interactif, pentes, dénivelés,
   **O₂ aller / retour / sur place** et verdict (faisable, marge entamée, hors autonomie, infranchissable).

**Fond aligné** : dans la zone étudiée, l'appli affiche les images orthorectifiées USGS livrées avec chaque modèle d'altitude
(CTX puis HiRISE) : elles sont calées exactement sur les altitudes.

**Recalage HiRISE sur CTX** : les modèles d'altitude HiRISE et CTX de l'USGS ne sont pas toujours calés exactement au même
endroit (écarts de l'ordre de 100 m observés à Jezero). Avant le calcul, chaque modèle HiRISE de la zone est comparé au modèle CTX
(référence calée sur MOLA) sur leur zone commune (jusqu'à 6 × 6 km, cases de 10 m) : relief débarrassé de sa tendance générale,
corrélation normalisée, recherche jusqu'à ±400 m, précision sous la case. Le décalage n'est appliqué (au modèle et à son image
orthorectifiée) que si le pic de corrélation est net (indice ≥ 5, corrélation ≥ 0,3) ; le Diagnostic l'indique.

**Recalage du fond d'image** : la mosaïque CTX de Mars Trek n'est pas recalée et peut être décalée de quelques centaines
de mètres par rapport aux altitudes (recalées sur MOLA). Le bouton « Recaler automatiquement le fond d'image CTX » compare
l'image et un relief ombré calculé à partir des altitudes (corrélation normalisée, filtrage passe-haut, recherche du soleil),
mesure le décalage et déplace le fond. Si le résultat n'est pas net (indice < 5), le fond n'est pas déplacé.

Le verdict de l'itinéraire tient compte de la météo : retour avant le coucher du soleil, départ de nuit interdit,
pente max abaissée de 5° en cas de givre, alerte en saison des tempêtes.

**Itinéraire retour** : à pied, monter coûte plus d'O₂ que descendre ; l'appli cherche donc aussi le meilleur chemin
de l'arrivée vers le départ. S'il s'écarte de plus de 30 m de l'aller, il est tracé en pointillés orange ; l'O₂ et la durée
du retour sont calculés sur ce chemin, et ses pentes sont vérifiées. En rover, le retour reprend l'aller.

**Fiabilité de la météo** : le modèle climatique (Mars Climate Database) est interrogé aux sites de Curiosity (Gale)
et de Perseverance (Jezero), à la même saison, et comparé aux mesures réelles des stations REMS et MEDA :
écart de température min / max et de pression moyenne.
Si le départ est à moins de 300 km d'une de ces stations, les températures et la pression du modèle sont corrigées de l'écart mesuré
(écart du minimum le matin, du maximum l'après-midi, interpolé entre les deux) ; le modèle brut reste affiché à côté. Note « bonne » (≤ 6 °C et ≤ 5 %), « moyenne » (≤ 12 °C et ≤ 10 %) ou « faible ».

**Radiations** :
- débit au sol mesuré par RAD (Curiosity) : 0,64 ± 0,12 mSv/jour (Hassler et al., *Science* 2014) ;
- correction selon la pression au départ (épaisseur d'atmosphère) : ≈ −0,076 % par Pa autour de 840 Pa (Guo et al., *JGR Planets* 2017) ;
- borne haute : +25 % hors maximum solaire (Guo et al. 2018) et incertitude de mesure ;
- protection par le relief : part du ciel masquée (horizon calculé sur 16 directions jusqu'à 2,5 km, rayonnement supposé isotrope) ;
- abris naturels à moins de 300 m du trajet, un par tronçon de 1,5 km (pastilles violettes), avec la distance maximale pour rejoindre le plus proche, et temps de retour à l'abri du départ en cas d'éruption solaire ;
- comparaison à la limite de carrière NASA (600 mSv, NASA-STD-3001).

**Type de sol** : inertie thermique de la mosaïque quantitative THEMIS (USGS, 100 m/pixel, Fergason et al. 2006 ;
précision ≈ 20 %), lue directement dans les fichiers ISIS `.cub` par requêtes partielles (seul le morceau utile est téléchargé).
Classes : < 150 poussière / fines meubles, 150–350 sable, 350–1 000 sol consolidé / graviers, > 1 000 roche affleurante / blocs.
- Itinéraire : pénalité supplémentaire (à pied : poussière 1, sable 0,4, roche 0,2 ; en rover : 3 / 1,5 / 1 pour les blocs).
- O₂ : la part « marche » du métabolisme est multipliée par 1,8 dans la poussière et 1,35 dans le sable
  (mesures sur Terre : ×1,34 à ×2,7 selon les études, dont Lejeune et al. 1998, Zamparo et al. 1992).
- Carte des sols de la zone (case à cocher) et répartition des sols le long du trajet.
- Limites : résolution de 100 m (une petite nappe de sable peut passer inaperçue) ; mosaïque limitée à ±60° de latitude.
- Accès : le serveur USGS « astropedia » ne répond qu'en http (relayé par serve.py, délai de 20 s).
  S'il est injoignable, secours automatique : mosaïque THEMIS **de nuit** contrôlée (USGS, COG sur AWS, 100 m) quand le quadrangle en a une,
  sinon mosaïque mondiale THEMIS de nuit v14 (ASU / USGS, 100 m, planetarymaps.usgs.gov) ; données qualitatives.
  La nuit, les matériaux fins sont plus froids que la roche : chaque point est classé **par rapport à la zone**
  (nettement plus froid que la médiane locale → sol meuble probable, nettement plus chaud → roche probable). Le bilan indique la source utilisée.

**Optimisations (sans changer les résultats)** : le retour réutilise la grille de la zone calculée pour l'aller ;
les blocs de fichiers déjà téléchargés restent en mémoire (cache de ~100 Mo par fichier) ; les recherches dans le catalogue
sont mémorisées ; les pénalités (pente + sol) sont calculées une seule fois par case au lieu d'une fois par voisin.
La vérification recale l'altitude au passage d'un modèle d'altitude à l'autre (deux modèles n'ont pas exactement le même zéro).

**Eau et nourriture** : 0,24 L d'eau par heure de sortie (NASA-STD-3001, OCHMO-TB-027), dimensionnée pour toute l'autonomie
du scaphandre (poche à boire du xEMU : 1,07 L, le reste en réserve) ; 500 kcal dans le scaphandre au-delà de 4 h
(recommandation NASA 2023 : 400–600 kcal). Leur masse est ajoutée à la masse portée (donc à l'O₂). Le bilan donne l'eau bue
et l'énergie dépensée (calculée à partir de l'O₂ consommé).

**Vent** : cycle du vent sur la journée (Mars Climate Database) → vent maximal pendant la sortie, alerte au-delà de 15 m/s ;
rappel des tourbillons de poussière (10 h – 16 h) et des vents de pente quand le trajet a du relief.

**Option « Privilégier les zones abritées »** (étape 6) : carte de la part du ciel visible (un point tous les ~50 m, horizon sur
16 directions) ; chaque pas coûte d'autant plus que le ciel est dégagé, ce qui attire le tracé vers les fonds de cratère et le pied
des parois, sans jamais autoriser de pente interdite.

**Particules renvoyées par le sol** : les neutrons secondaires produits dans le régolithe sont inclus dans le débit mesuré par RAD ;
le relief n'en protège pas.

**Zones intéressantes (géologie)** : service OGC de l'USGS Astrogeology (pygeoapi) interrogé autour de l'itinéraire (±1,5 km) :
carte géologique de Mars 1:20 M (Tanaka et al. 2014, SIM 3292 : unités, contacts, structures) et cartes régionales si le service en propose.
- Unités traversées (part du trajet) et intérêt déduit de leur description : sédimentaire (eau ancienne, biosignatures), volcanique
  (basalte, construction), glace (eau, ISRU), impact (roches profondes), croûte ancienne.
- Points d'intérêt : changements d'unité (contacts), failles, escarpements, rides, chenaux, bords de cratère à moins de 1 km.
- Limite : à l'échelle mondiale, les contours sont précis à quelques kilomètres près : ce sont des zones à examiner.

**Feuille de route à l'estime** : tracé simplifié en tronçons (Douglas-Peucker, 15 m) ; pour chacun : cap (depuis le nord),
distance, nombre de pas (0,7 m), dénivelé, pente maximale et position du soleil par rapport au cap (algorithme Mars24) —
Mars n'a pas de champ magnétique global, donc pas de boussole. Aller et retour.

**Carte préchargée (hors ligne)** : page HTML autonome téléchargeable : carte du relief ombré et des pentes calculée à partir
des altitudes (aucune image distante), itinéraires, points de passage numérotés, abris, points d'intérêt, feuilles de route,
résumé (O₂, eau, radiations, horaires) et consignes ; imprimable. Exports GeoJSON et GPX (coordonnées Mars 2000, longitude Est).

**Langue** : bouton FR / EN en haut du panneau (choix mémorisé). L'interface est écrite en français ; en anglais, chaque texte
affiché, y compris les résultats calculés et la carte préchargée exportée, est traduit à la volée à partir d'un dictionnaire.

**Retour vérifié à pleine résolution** : quand le retour s'écarte de l'aller, son couloir de pentes détaillées est affiché
lui aussi (le retour est calculé avec le même affinage à ~2 m que l'aller, et ses pentes entrent dans le verdict).

## Modèle d'oxygène (hypothèses)

| Élément | Valeur | Origine |
|---|---|---|
| Conversion | 1 W·h de métabolisme ≈ 0,246 g d'O₂ | 1 L d'O₂ ≈ 19,8 BTU ; 1,43 g/L |
| Budget du scaphandre | autonomie × 352 W (1 200 BTU/h) | moyenne d'exploration NASA |
| Repos / tâches légères | 205 W (700 BTU/h) | NASA |
| Marche | 205 W + 1,17 J/(kg·m) × masse totale × vitesse | calé sur la marche de retour NASA (≈ 1 700 BTU/h à 3,6 km/h) |
| Montée | + masse × 3,71 × vitesse × pente / 0,25 | rendement musculaire ~25 % |
| Descente | aucun gain compté ; au-delà d'environ 18° de pente, surcoût de freinage (jusqu'à ×1,44 sur la part « marche ») | Minetti et al., *J Appl Physiol* 2002 |
| Secours (~30 min) | jamais compté | |
| Conduite du rover | 205 W | activité la moins exigeante des EVA Apollo |
| Rover LTV | 10 km/h (moy.), 15 km/h max, 20° max, 20 km par charge | exigences NASA Artemis |
| Rover LRV | 7 km/h (moy.), 25° max, 65 km, 490 kg de charge | Apollo 15–17 |

## Sources

- Fonds de carte : NASA Mars Trek WMTS — https://trek.nasa.gov/mars/
- Modèles d'altitude : USGS Astrogeology STAC — https://stac.astrogeology.usgs.gov/api
  (`mro_hirise_controlled_socet_dtms`, `mro_ctx_controlled_usgs_dtms`) et MOLA global (COG USGS)
- Climat : Mars Climate Database v6 — https://www-mars.lmd.jussieu.fr/mcd_python/ (LMD / ESA / CNES)
- Relevés météo : flux NASA/JPL `mars.nasa.gov/rss/api/?feed=weather&category=msl|mars2020`
- Scaphandres et métabolisme : NASA ICES-2026-127 *Mars Spacesuit Mass Requirements*, NASA EVA ConOps,
  NASA NTRS (voir le doc projet « besoins-astronaute-xEMU »)
