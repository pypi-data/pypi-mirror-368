# Thème DSFR pour MkDocs DSFR

> ATTENTION : Ce thème est uniquement destiné à être utilisé pour les sites et applications officiels des services
> publics français. Son objectif principal est de faciliter l'identification des sites gouvernementaux pour les citoyens.

[Mentions légales](https://www.systeme-de-design.gouv.fr/cgu/).

## Documentation de Mkdocs DSFR

Vous trouverez la documentation de mkdocs-dsfr sur [le site de documentation](https://pub.gitlab-pages.din.developpement-durable.gouv.fr/numeco/mkdocs-dsfr-doc).

## Démarrage rapide

Pour expérimenter rapidement mkdocs avec le DSFR, vous pouvez cloner
le [projet d'exemple](https://gitlab-forge.din.developpement-durable.gouv.fr/pub/numeco/mkdocs-dsfr-exemple).

## Configuration du dépôt et des liens d'édition

Dans le fichier `mkdocs.yml`, trois configurations importantes sont définies pour permettre aux utilisateurs de naviguer
vers le dépôt source et d'éditer les pages directement :

* `repo_url`: URL du dépôt Git où le code source de la documentation est hébergé.
* `edit_uri`: Chemin relatif vers le dossier contenant les fichiers Markdown de la documentation dans le dépôt Git.
* `edit_text`: Texte à afficher pour le lien d'édition.

### Exemple de configuration

Dans ce projet, les configurations sont définies comme suit :

`repo_url: https://gitlab-forge.din.developpement-durable.gouv.fr/pub/numeco/mkdocs-dsfr/`
`edit_uri: blob/main/docs/`

### Comment cela fonctionne

* `repo_url` pointe vers le dépôt GitLab où se trouve le code source de la documentation.
* `edit_uri` indique le chemin relatif vers les fichiers Markdown dans ce dépôt.

Si l'une de ces variables n'est pas remplie, le lien d'édition n'apparaîtra pas.

## Configuration du thème DSFR MkDocs

Ce document décrit les différentes options de configuration pour le thème DSFR MkDocs.
Dans votre fichier de configuration `mkdocs.yml`, vous pouvez définir les options de thème pour personnaliser
votre site. Voici les options de thème disponibles et leurs valeurs par défaut :

```yaml

theme:
  # Config par défaut (modifiable)
  include_search_page: true
  afficher_date_de_revision: false
  afficher_menu_lateral: true
  afficher_bouton_editer: true
  bouton_hautdepage: left
  libelle_bouton_editer: Éditer dans Gitlab Forge

  # Ces valeurs sont à modifier
  intitule: "République <br> française"
  header:
    titre: "Titre"
    sous_titre: "Sous-titre"
  footer:
    description: "Description à modifier"
    links:
      - name: legifrance.gouv.fr
        url: https://legifrance.gouv.fr
      - name: gouvernement.fr
        url: https://gouvernement.fr
      - name: service-public.fr
        url: https://service-public.fr
      - name: data.gouv.fr
        url: https://data.gouv.fr

```

## Options de Thème

### `name`

Le nom du thème. Il doit être défini sur 'dsfr'.

### `locale`

La locale pour le thème. Il est défini sur 'fr' pour le français.

### `include_search_page`

Permet l'affichage et l'utilisation de la barre de recherche.

### `afficher_date_de_revision`

Permet d'afficher la date de dernière révision git.
Valeur booléenne qui permet d'afficher ou de masquer la date de la dernière révision de la page actuelle dans le pied de
page. Vous pouvez la définir sur `true` pour afficher la date, ou sur `false` pour la masquer.
Il est important de noter qu'en plus d'utiliser cette option, vous devez également installer le
plugin `mkdocs-git-revision-date-localized-plugin` pour que cela fonctionne.
`pip install mkdocs-git-revision-date-localized-plugin`

### `afficher_menu_lateral`

Valeur booléenne pour afficher ou masquer le menu latéral. Définissez-le sur `true` ou `false`.

### `afficher_bouton_editer`

Valeur booléenne pour afficher ou masquer le menu latéral. Définissez-le sur `true` ou `false`.

### `bouton_hautdepage`

Position du bouton "Haut de page" pour les pages longues. Valeurs possibles : `left` (par défaut) `right` (alignement à droite du bouton) ou `false` (désactivé)

### `libelle_bouton_editer`

Permet de personnaliser le libellé de bouton d'édition.

### `intitule`

Cette option définit le titre principal du logo dans l'en-tête et le pied de page.

## Options d'En-tête

### `titre`

Cela définit le titre qui apparaît dans l'en-tête de la page.

### `soustitre`

Cela définit le sous-titre qui apparaît sous le titre dans l'en-tête de la page.

## Options de Pied de Page

### `description`

Cela définit une description qui apparaît dans le pied de page.

### `links`

Cette option vous permet de définir une liste de liens qui apparaîtront dans le pied de page. Chaque lien doit être un
dictionnaire avec des clés `name` et `url`.

## Notes de version

### Version 0.15.2 (DSFR 1.14.0)
* Régression sur l'import de utility.css du DSFR corrigée

### Version 0.15.1 (DSFR 1.14.0)
* Déploiement altéré de la version 0.15.0.

### Version 0.15.0 (DSFR 1.14.0)
* Ajout des liens d'évitements
* Ajout du sommaire
* [BETA] Support des mots-clés
* Correction bug card sans image (via dsfr_structure)

### Version 0.14.0 (DSFR 1.14.0)
* Ajout via dsfr_structure des composants mise en avant et citation
* Ajout du fil d'Ariane
* Utilisation des métadonnées Markdown pour définir le fil d'Ariane, le menu latéral par page, et le bandeau d'information importante

### Version 0.13.1 (DSFR 1.14.0)
* Déplacement du lien d'édition de la page dans le bandeau d'en-tête pour corriger un bug de placement du menu de navigation
* Mise à jour du DSFR

### Version 0.13.0 (DSFR 1.13.2)

* Ajout personnalisable d'un bouton "Retour haut de page" pour les pages longues
* Ajout d'une page 404 suivant les recommendations DSFR
* Mise à jour du DSFR
* Mise à jour de [DSFR structure](https://pypi.org/project/dsfr_structure/)

### Version 0.12.2 (DSFR 1.13.1)

* Affichage de révision désactivé par défaut.

### Version 0.12.1 (DSFR 1.13.1)

* Réduction de la taille du bloc de code
* Création du site documentaire

### Version 0.12.0 (DSFR 1.13.1)

* Ajout du composant Card

### Version 0.11.0 (DSFR 1.13.1)

* Ajout de composants DSFR

### Version 0.10.0 (DSFR 1.13.1)

* Refonte technique : Passage à uv

### Version 0.9.3 (DSFR 1.13.1)

* Correction bug accordéon multiple sur une même page

### Version 0.9.2 (DSFR 1.13.1)

* Mise à jour du DSFR

### Version 0.9.1 (DSFR 1.13.0)

* Mise à jour du DSFR

### Version 0.9.0 (DSFR 1.12.1)

* Possibilité de masquer le menu latéral sur la page d'accueil
* Ajout des icônes additionnels du DSFR
* Support de [l'accordéon DSFR](https://www.systeme-de-design.gouv.fr/composants-et-modeles/composants/accordeon)

### Version 0.8.1 (DSFR 1.12.1)

* Correction version 0.8.0 inutilisable suite à la suppression de purgeCSS

### Version 0.8.0 (DSFR 1.12.1)

* Mise à jour du DSFR
* Intégration totale du DSFR, sans purge CSS

### Version 0.7.2 (DSFR 1.11.2)

* Mise à jour du DSFR

### Version 0.7.1 (DSFR 1.11.0)

* Mise à jour du DSFR

### Version 0.7.0 (DSFR 1.10.1)

* Coloration syntaxique du code
* Bouton copier-coller du code
* Création d'une extension pour la structure DSFR (contraintes CSS)

### Version 0.6.1 (DSFR 1.10.1)

* Correction de bug de paramètre de conf
* Changement de nom du paramètre `button_edit_label`

### Version 0.6.0 (DSFR 1.10.1)

* Allègement du thème
* Affichage de la date de dernière révision dans le footer de la page
* Ajout d'un bouton pour modifier la page (redirection vers le dépôt source)

### Version 0.5.3 (DSFR 1.10.1)

* Correction documentation pour la fonction recherche
* Mise à jour DSFR

### Version 0.5.2 (DSFR 1.10.0)

* Correction bug technique lié à la fonction recherche

### Version 0.5.1 (DSFR 1.10.0)

* Corrections pour prise en charge de la recherche

### Version 0.5.0 (DSFR 1.10.0)

* Prise en charge du texte barré
* Prise en charge des checkboxes
* Mise à jour du DSFR

### Version 0.4.0 (DSFR 1.9.3)

* Ajout de variables de configuration

### Version 0.3.1 (DSFR 1.9.3)

* Correction de problèmes d'import et d'affichage

### Version 0.3.0 (DSFR 1.9.3 Juin 2023)

* Ajout du composant paramètre d'affichage dans le footer pour la gestion des thèmes dark et light

### Version 0.2.0 (June 2023)

* Initial experimental version
