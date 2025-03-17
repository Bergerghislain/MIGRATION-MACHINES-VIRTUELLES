# MIGRATION-MACHINES-VIRTUELLES
how to migrate Vms in a GRID 5000 environment using Openstack

Ceci ne constitue qu'un guide resumant les differentes etapes pour realiser la migration de machines virtuelles sur Openstack dans un environnement GRID 5000 ceci sous certaines conditions bien definies( dans un fichier Json) et entres des machines n'etant pas forcement dans le meme cluster.

Pour cela j'ai cree trois repertoires , 

- Les fichiers de code seront situes dans le sous-repertoire " codes de fonctionnement"
- Les powerpoint temoignant de mon evolution hebdomadaire  et des reflections que j'ai pu avoir seront dans le le sous-repertoire " Documentations"
- Et enfin dans un sous-repertoire du nom de  " Documentations" ,socle de la vulgarisation de mon travail j'ai :

-J'ai resume dans un fichier word la demarche generale adoptee ainsi que la liste enumeree des fichiers de codes et leurs utilites ( mais cela n'etait vraiment que tres bref)
- Ensuite pour faire un zoom plus detaille sur chaque fichier, j'explique dans un fichier word portant le nom du fichier de code apres le "--" pour dire exactement a quoi sert le fichier , en quoi il aide dans notre objectif principal plus haut et surtout , quelle a ete la reflexion mene pour editer et creer ce dernier et eventuellement tout ce qui tourne autour
-Dans un fichier principal je retracerai l'historique de parcours des fichiers, les commandes principales a execcuter qui joignent tous ses fichiers entre eux ( un peu comme un fil conducteur) ainsi comprendre le travail et le reproduire pourra etre un peu plus aise( a quelques choses pretes:) ) 

Aussi certains fichiers avec dans leur noms "folks" sont des approches que j'ai eus mais que j'ai du changer car elles etaient difficilement implementables car le temps imparti etaient insuffisant , j'ai tout de meme documenter ces fichiers ( la documentation de ces derniers ayant aussi folks dans leur nomenclature suivant le principe plus haut) pour un usage future, vu que certains d'entre eux figurent egalement dans mes presentations powerpoint 

J'ai pris enormement de plaisir a travailler dessus j'espere que vous en prendrez autant lors de vos lectures.( j'ai suppose que vous l'avez lu plusieurs fois:) )

NB: SUIVRE EXACTEMENT CHAQUE ETAPE DECRITE A LA LETTRE !!!
