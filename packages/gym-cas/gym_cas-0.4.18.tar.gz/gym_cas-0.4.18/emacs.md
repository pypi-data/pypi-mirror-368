# Om anvendelse af Emacs til opgaveløsning i matematik

I Emacs kan org-mode anvendes til at skrive opgaver i.

> Org Mode is an authoring tool and a TODO lists manager for GNU Emacs. It relies on a lightweight plain-text markup language used in files with the ‘.org’ extension. -- <https://orgmode.org/manual/Summary.html>

Denne har en præambel (valgfri), hvor ting såsom forfatter, titel og setupfil kan angives på følgende vis:

```txt
#+TITLE: <titel>
#+AUTHOR: <forfatter>
#+SETUPFILE: <path til setupfil>
```

Samt har denne en rubrikstruktur:

```txt
* Rubrik niveau 1
** Rubrik niveau 2
*** Rubrik niveau 3 ...
```

> Org-mode er en afart af markdown-sprog, dog smartere fx kan det håndtere fodnoter, ToDo-lists LaTeX-snippets m.m, samt er det mere fleksibelt end Jupyter Notebook, men det understøtter også "literate programming" via src-blokke (Source Code) -- <https://orgmode.org/manual/Working-with-Source-Code.html>

Src-blokke gives ved:

```txt
#+NAME: <name> (valgfri)
#+BEGIN_SRC <sprog> <argumenter>
  <krop>
#+END_SRC
```

Src-blokkene kan da køres i selve org-filen, hvorefter denne vil give følgende:

```txt
#+RESULTS:
<resultat af program>
```

Src-blokkene har standardindstillinger, men disse kan ændres ved at angive argumenter på formattet `":<argument> <værdi>"`. Det er min erfaring, at følgende er de vigtigste:

- `":results output"` sørger for at kodens output renderes under #+RESULTS:
- `":exports both"` el. `"exports none"` el `"exports results"`, som hhv. eksporter både kodeblok samt resultatet, denne giver, eksporterer ingen af delene, sidste nøjes med at eksportere resultaterne af koden. Mere om denne "eksport":

Såfremt koden ønskes kontinueret i en senere kodeblok, da kan `":session <navn>"` (navn er valgfrit) anvendes, da denne kode så behandles som en lang kodesession, hvilket betyder, at funktioner kan kaldes og variabler kan hentes i senere kodeblokke, desuden behøves kodebiblioteker kun hentes en gang.

Desuden, hvis man ellers har de rigtige programmer, et LaTeX-engine, kan org-mode filen eksporteres til en PDF-fil via LaTeX. Dette gøres ved at køre emacs-kommandoen "org-export-dispatch".

Såfremt man ønsker nemmere kodebibliotekstyring og kører på Linux, da kan direnv anvendes, der loader kodemiljøer per ens projekt. Her tages udgangspunkt i python:

først installeres direnv-packagen via ens package manager og opsættes per instruks (se fx <https://www.youtube.com/watch?v=lz2qbtWZu90&t=4s>). Herefter laves filen ".envrc" i ens projektmappe, her tilføjes teksten "layout_python3", hvorefter kommandoen køres i terminalen i selvsamme mappe "direnv allow", hvorefter denne vil blive kørt hver gang mappen tilgås. Herefter kan man køre "pip install gym-cas" fx.

> "direnv is an extension for your shell. It augments existing shells with a new feature that can load and unload environment variables depending on the current directory." -- <https://direnv.net/>

Ligedan kan emacs-packagen direnv hentes via fx Doom Emacs' package manager (hvilket anbefales), hvorefter kodemiljøerne automatisk anvendes, når org-filen eksisterer i en projektmape, der har en .envrc-fil, som beskrevet ovenfor (direnv emacs-integrationen er afhængig af direnv-packagen)

## Om Doom Emacs

> "Doom is a configuration framework for GNU Emacs tailored for Emacs bankruptcy veterans who want less framework in their frameworks, a modicum of stability (and reproducibility) from their package manager, and the performance of a hand rolled config (or better). It can be a foundation for your own config or a resource for Emacs enthusiasts to learn more about our favorite operating system." -- <https://github.com/doomemacs/doomemacs>

## Andet

Org-filen kan indeholde eksport-indstillinger fx

```txt
#+LATEX_HEADER: \usepackage[a4paper, margin=2.5cm]{geometry}
```

Links til filer kan indsættes (via kommando org-insert-link), hvorefter disse kan renderes in-line også samt eksporteres som figurer i LaTeX m. billedtekst.

Således er org-filer det bedste af mange verdener, det er nem og overskuelig opgaveopsætning med LaTeX' matematikrendering og elegance i færdigproduktet, men også et sted, hvor kode kan skrives, køres og renderes. Den største ulempe ved org-mode er realtid samtidsredigering, dog muligt via fx CRDT-packagen i emacs. Desuden kan "org-mode"-ekstensionen anvendes i VScode, hvis dette er strengt nødvendigt.
