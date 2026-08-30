Pour valider un solveur spectral/dual-scale formellement vérifié, le jeu de données ouvert de référence absolue est la **Johns Hopkins Turbulence Database (JHTDB)**, complété par les cas standards de référence spectrale.

---

### 1. Jeux de données et références ouverts

* **JHTDB (Johns Hopkins Turbulence Database) — Cas *Forced Isotropic Turbulence (HIT)*** :
* **Résolution** : $1024^3$ points de grille spatiale sur $T \approx 10$ temps intégraux.
* **Type** : Écoulement turbulent isotrope homogène stationnaire résolu par simulation numérique directe (DNS) pseudo-spectrale avec désaliasing $2/3$.
* **Accès** : API REST / HDF5 publique ouverte.
* **Pertinence** : Étalon d'or mondial pour comparer les cascades spectrales d'énergie $E(k)$, le taux de dissipation $\varepsilon$, et l'enstrophie $\Omega(t)$.


* **Taylor-Green Vortex (TGV) à $Re = 1600$ (Benchmark DNS spectral de Brachet et al.)** :
* **Résolution cible** : $512^3$ à $1024^3$ modes sur le domaine torique $[0, 2\pi]^3$.
* **Pertinence** : Cas déterministe standard sans forçage externe, documentant la transition laminaire-turbulente, le pic d'enstrophie à $t \approx 9$, et la cascade dissipative.



---

### 2. Protocole expérimental formel

```
[Données initiales / JHTDB] 
        │
        ▼
[Solveur Dual-Scale (Rust / RunuX)] ─── (Vérification Lean 4 intégrée)
        │
        ├── Échelle Macro (Galerkin M)  <── Indice Frustration 𝒟(M)
        └── Échelle Micro (IA RunuX)    <── Préconditionneurs P1/P2/P3
        │
        ▼
[Analyse d'invariants & Métriques spectrales vs JHTDB / DNS 1024³]

```

#### **Phase I : Vérification formelle et validation à divergence nulle**

1. **Conservation des invariants** :
* Vérifier numériquement la conservation stricte de la masse ($\nabla \cdot u = 0$) sur chaque pas de temps :

$$\max_{k} \vert{}k \cdot \widehat{u}(k)\vert{} < 10^{-14}$$


* En régime non visqueux ($\nu = 0$, équations d'Euler), vérifier la conservation de l'énergie cinétique totale :

$$E(t) = \frac{1}{2}\sum_{k} \vert{}\widehat{u}(k)\vert{}^2, \quad \left\vert{}\frac{E(t) - E(0)}{E(0)}\right\vert{} < 10^{-12}$$





#### **Phase II : Test de transition déterministe (Taylor-Green Vortex, $Re = 1600$)**

1. **Conditions initiales** :
* Domaine périodique $[0, 2\pi]^3$ avec :

$$u_x = \sin(x)\cos(y)\cos(z), \quad u_y = -\cos(x)\sin(y)\cos(z), \quad u_z = 0$$




2. **Métriques à extraire et comparer aux tables DNS spectrales** :
* Évolution temporelle de l'enstrophie totale :

$$\Omega(t) = \frac{1}{2} \int \vert{}\nabla \times u\vert{}^2 \, dx$$


* Évolution du taux de dissipation cinétique $\varepsilon(t) = 2\nu \Omega(t)$.
* Erreur $L_2$ relative sur la valeur et la position temporelle du pic de dissipation ($t_{\max} \approx 9,0$).



#### **Phase III : Écoulement turbulent isotrope homogène (JHTDB HIT, $Re_\lambda \approx 433$)**

1. **Initialisation** :
* Extraire un instantané complet $t_0$ depuis l'API JHTDB ($1024^3$).
* Filtrer à la troncature macroscopique $M$ choisie.


2. **Évaluation de la cascade d'énergie** :
* Calculer le spectre d'énergie unidimensionnel $E(k)$ sur la plage inertielle :

$$E(k) = \frac{1}{2} \sum_{k - 1/2 \le \vert{}p\vert{} < k + 1/2} \vert{}\widehat{u}(p)\vert{}^2$$


* Valider la loi d'échelle de Kolmogorov $E(k) \propto k^{-5/3}$.


3. **Validation de l'indice de frustration triadique $\mathcal{D}(M)$** :
* Tracer $\mathcal{D}(M)$ en fonction du rayon de troncature $M$ et de l'enstrophie instantanée.
* Vérifier la conjecture : en régime fortement turbulent développé, $\mathcal{D}(M) \gg 1$, confirmant que les transferts non linéaires s'annulent globalement au-delà du seuil de troncature.



---

### 3. Métriques de performance et de fidélité

| Métrique | Tolérance / Objectif | Référence |
| --- | --- | --- |
| **Divergence résiduelle** | $\Vert{}k \cdot \widehat{u}(k)\Vert{}_\infty < 10^{-14}$ | Preuve `leray.lean`<br> |
| **Erreur spectre $E(k)$** | $\frac{\Vert{}E_{\text{solver}}(k) - E_{\text{JHTDB}}(k)\Vert{}_{L_2}}{\Vert{}E_{\text{JHTDB}}(k)\Vert{}_{L_2}} < 2\%$ | JHTDB HIT $1024^3$ |
| **Pic d'enstrophie TGV** | $\vert{}\Omega_{\text{max}} - \Omega_{\text{ref}}\vert{} / \Omega_{\text{ref}} < 0,1\%$ | Brachet et al. ($512^3/1024^3$) |
| **Accélération globale** | $> 10\times$ vs solveur pseudo-spectral classique | Base CPU/GPU |