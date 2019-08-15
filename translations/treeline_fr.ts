<!DOCTYPE TS><TS>
<context>
    <name>cmdline</name>
    <message>
        <source>Error - could not read file %s</source>
        <comment>%s is filename</comment>
        <translation>Erreur - impossible de lire le fichier nommé %s</translation>
    </message>
    <message>
        <source>Error in %(filename)s - %(details)s</source>
        <translation>Erreur dans %(filename)s - %(details)s</translation>
    </message>
    <message>
        <source>File &quot;%(infile)s&quot; (%(intype)s type) was exported to &quot;%(outfile)s&quot; (%(outtype)s type)</source>
        <translation>Fichier &quot;%(infile)s&quot; (%(intype)s type) a été exporté dans &quot;%(outfile)s&quot; (%(outtype)s type)</translation>
    </message>
    <message>
        <source>Usage:</source>
        <translation>Utilisation:</translation>
    </message>
    <message>
        <source>qt-options</source>
        <translation>options-qt</translation>
    </message>
    <message>
        <source>infile</source>
        <translation>fichier</translation>
    </message>
    <message>
        <source>-or- (non-interactive):</source>
        <translation>-ou- (non-interactif):</translation>
    </message>
    <message>
        <source>import-option</source>
        <translation>options-import</translation>
    </message>
    <message>
        <source>export-option</source>
        <translation>options-export</translation>
    </message>
    <message>
        <source>misc-options</source>
        <translation>options-autres</translation>
    </message>
    <message>
        <source>infile2</source>
        <translation>fichier2</translation>
    </message>
    <message>
        <source>Qt-options:</source>
        <translation>Options-qt:</translation>
    </message>
    <message>
        <source>see Qt documentation for valid Qt options</source>
        <translation>voir dans la documentation Qt quelles sont les options Qt valides</translation>
    </message>
    <message>
        <source>Import-options:</source>
        <translation>Options-import:</translation>
    </message>
    <message>
        <source>import a tab indented text file</source>
        <translation>importe un fichier texte indenté avec des tabulations</translation>
    </message>
    <message>
        <source>import a tab-delimitted text table, one node per line</source>
        <translation>importe un tableau texte délimité par des tabulations, avec un nœud par ligne</translation>
    </message>
    <message>
        <source>import plain text, one node per line</source>
        <translation>importe du texte normal, avec un nœud par ligne
</translation>
    </message>
    <message>
        <source>import plain text, one node per paragraph</source>
        <translation>importe du texte normal, avec un nœud par paragraphe</translation>
    </message>
    <message>
        <source>import a Treepad text-node file</source>
        <translation>importe un fichier Treepad texte-nœud</translation>
    </message>
    <message>
        <source>import an XML bookmark file in XBEL format</source>
        <translation>importe un fichier XML de favoris au format XBEL</translation>
    </message>
    <message>
        <source>import an html bookmark file in Mozilla format</source>
        <translation>importe un fichier html de favoris au format Mozilla</translation>
    </message>
    <message>
        <source>import a generic XML file (non-TreeLine format)</source>
        <translation>importe un fichier générique XML (pas au format TreeLine)</translation>
    </message>
    <message>
        <source>import an ODF text document</source>
        <translation>importe un document texte au format ODF</translation>
    </message>
    <message>
        <source>Export-options:</source>
        <translation>Options-export :</translation>
    </message>
    <message>
        <source>export a single HTML file</source>
        <translation>exporte un fichier HTML unique</translation>
    </message>
    <message>
        <source>export HTML in directories</source>
        <translation>exporte au format HTML dans des dossiers</translation>
    </message>
    <message>
        <source>export an XSLT file</source>
        <translation>exporte un fichier XSLT</translation>
    </message>
    <message>
        <source>export a tab indented text file</source>
        <translation>exporte un fichier texte indenté avec des tabulations</translation>
    </message>
    <message>
        <source>export a text table of the first children only</source>
        <translation>exporte un tableau texte seulement pour les premiers enfants</translation>
    </message>
    <message>
        <source>export an XML bookmark file in XBEL format</source>
        <translation>exporte un fichier XML de favoris au format XBEL</translation>
    </message>
    <message>
        <source>export an html bookmark file in Mozilla format</source>
        <translation>exporte un fichier html de favoris au format Mozilla</translation>
    </message>
    <message>
        <source>export a generic XML file (non-TreeLine format)</source>
        <translation>exporte un fichier générique de type XML (pas au format TreeLine)</translation>
    </message>
    <message>
        <source>export an ODF text document</source>
        <translation>exporte un document texte au format ODF</translation>
    </message>
    <message>
        <source>Misc-options:</source>
        <translation>Options-autres :</translation>
    </message>
    <message>
        <source>the output filename, not used with multiple infiles</source>
        <translation>le nom du fichier exporté, non utilisé avec des fichiers d&apos;entrées multiples</translation>
    </message>
    <message>
        <source>exclude the root node form the output if applicable</source>
        <translation>exclut, le cas échéant, le nœud racine du fichier de sortie</translation>
    </message>
    <message>
        <source>add a header and footer to HTML exports</source>
        <translation>ajoute un en-tête et un pied de page aux fichiers HTML en sortie</translation>
    </message>
    <message>
        <source>change the indent amount for HTML exports (default = 20)</source>
        <translation>change le niveau d&apos;indentation pour les fichiers HTML exportés (défaut = 20)</translation>
    </message>
    <message>
        <source>supress normal status information, only give errors</source>
        <translation>supprime les informations de type normal, affiche seulement les erreurs</translation>
    </message>
    <message>
        <source>display this information and exit</source>
        <translation>affiche cette information et termine</translation>
    </message>
    <message>
        <source>No more than one import-option and one export-option may be
specified.  If either are not present, the native TreeLine
file format is assumed.</source>
        <translation>On ne peut spécifier qu&apos;une seule option-import et une seule option-export.
 Si l&apos;une est absente, on utilise le format de fichier TreeLine.</translation>
    </message>
    <message>
        <source>The output filename option can only be specified if there is
only one input file.  If it is not specified, the input&apos;s base
file name is used with the appropriate output file extension.
If the extensions are the same, an underscore is added before
the extension.  Note that this avoids overwriting the input
file, but other files may be overwritten without notification
if they share the output file&apos;s name.</source>
        <translation>Le nom du fichier de sortie ne peut être spécifié que s&apos;il n&apos;y a qu&apos;un seul fichier
à importer.  Si le nom n&apos;est pas spécifié, le nom du fichier d&apos;entrée est utilisé avec
l&apos;extension appropriée pour former le nom du fichier exporté.  Si les extensions sont les
mêmes, un charactère de soulignement est ajouté devant l&apos;extension.  Notez que cela évite d&apos;écraser
le fichier à importer, mais d&apos;autres fichiers peuvent être écrasés sans avertissement s&apos;ils
ont le même nom que le fichier de sortie.</translation>
    </message>
    <message>
        <source>FILE</source>
        <translation>FICHIER</translation>
    </message>
    <message>
        <source>NUM</source>
        <translation>NUM</translation>
    </message>
</context>
<context>
    <name>configdialog</name>
    <message>
        <source>Configure Data Types</source>
        <translation>Paramètres du Type de Données</translation>
    </message>
    <message>
        <source>T&amp;ype List</source>
        <translation>Liste des t&amp;ypes</translation>
    </message>
    <message>
        <source>&amp;Type Config</source>
        <translation>Configuration du t&amp;ype</translation>
    </message>
    <message>
        <source>Field &amp;List</source>
        <translation>&amp;Liste des champs</translation>
    </message>
    <message>
        <source>&amp;Field Config</source>
        <translation>Con&amp;figuration des champs</translation>
    </message>
    <message>
        <source>&amp;Output</source>
        <translation>S&amp;ortie</translation>
    </message>
    <message>
        <source>&amp;Show Advanced</source>
        <translation>Avancé&amp;s</translation>
    </message>
    <message>
        <source>&amp;OK</source>
        <translation>&amp;OK</translation>
    </message>
    <message>
        <source>&amp;Apply</source>
        <translation>&amp;Appliquer</translation>
    </message>
    <message>
        <source>&amp;Reset</source>
        <translation>&amp;Réinitialiser</translation>
    </message>
    <message>
        <source>&amp;Cancel</source>
        <translation>&amp;Annuler</translation>
    </message>
    <message>
        <source>Hide Advanced</source>
        <translation>Cacher les options avancées</translation>
    </message>
    <message>
        <source>Show Advanced</source>
        <translation>Montrer les options avancées</translation>
    </message>
    <message>
        <source>Add or Remove Data Types</source>
        <translation>Ajouter ou supprimer des Types de Données</translation>
    </message>
    <message>
        <source>&amp;New Type...</source>
        <translation>&amp;Nouveau Type...</translation>
    </message>
    <message>
        <source>Co&amp;py Type...</source>
        <translation>Co&amp;pier le type…</translation>
    </message>
    <message>
        <source>R&amp;ename Type...</source>
        <translation>R&amp;enommer le Type…</translation>
    </message>
    <message>
        <source>&amp;Delete Type</source>
        <translation>&amp;Supprimer Type</translation>
    </message>
    <message>
        <source>Add Type</source>
        <translation>Ajouter Type</translation>
    </message>
    <message>
        <source>Enter new type name:</source>
        <translation>Entrer un nouveau nom de type:</translation>
    </message>
    <message>
        <source>Rename Type</source>
        <translation>Renommer Type</translation>
    </message>
    <message>
        <source>Rename from &quot;%s&quot; to:</source>
        <translation>Renommer de &quot;%s&quot; à:</translation>
    </message>
    <message>
        <source>Cannot delete data type being used by nodes</source>
        <translation>Impossible de supprimer un type de données qui est en cours d&apos;utilisation par des nœuds</translation>
    </message>
    <message>
        <source>[None]</source>
        <comment>no default child type</comment>
        <translation>[Aucun]</translation>
    </message>
    <message>
        <source>&amp;Data Type</source>
        <translation>T&amp;ype de Données</translation>
    </message>
    <message>
        <source>Icon</source>
        <translation>Icône</translation>
    </message>
    <message>
        <source>Change &amp;Icon</source>
        <translation>Modifier l&apos;&amp;Icône</translation>
    </message>
    <message>
        <source>Default C&amp;hild Type</source>
        <translation>Type par Défaut du &amp;Fils</translation>
    </message>
    <message>
        <source>Link R&amp;eference Field</source>
        <translation>Champ avec li&amp;en de référence</translation>
    </message>
    <message>
        <source>Sibling Text</source>
        <translation>Texte du Frère</translation>
    </message>
    <message>
        <source>&amp;Prefix Tags</source>
        <translation>&amp;Balise Préfixe</translation>
    </message>
    <message>
        <source>Suffi&amp;x Tags</source>
        <translation>Balises de Suff&amp;ixe</translation>
    </message>
    <message>
        <source>Derived from &amp;Generic Type</source>
        <translation>Dérivé d&apos;un Type &amp;Générique</translation>
    </message>
    <message>
        <source>Automatic Types</source>
        <translation>Types Automatiques</translation>
    </message>
    <message>
        <source>None</source>
        <comment>no icon set</comment>
        <translation>Aucun</translation>
    </message>
    <message>
        <source>Modify Co&amp;nditional Types</source>
        <translation>Modifier un Type co&amp;nditionnel</translation>
    </message>
    <message>
        <source>Create Co&amp;nditional Types</source>
        <translation>Créer un Type Co&amp;nditionnel</translation>
    </message>
    <message>
        <source>Set Types Conditionally</source>
        <translation>Configurer Types Sous Conditons</translation>
    </message>
    <message>
        <source>Modify Field List</source>
        <translation>Modifier la liste des champs</translation>
    </message>
    <message>
        <source>Name</source>
        <translation>Nom</translation>
    </message>
    <message>
        <source>Type</source>
        <translation>Type</translation>
    </message>
    <message>
        <source>Move &amp;Up</source>
        <translation>Déplacer vers le &amp;haut</translation>
    </message>
    <message>
        <source>Move Do&amp;wn</source>
        <translation>Déplacer vers le &amp;bas</translation>
    </message>
    <message>
        <source>&amp;New Field...</source>
        <translation>&amp;Nouveau Champ...</translation>
    </message>
    <message>
        <source>R&amp;ename Field...</source>
        <translation>R&amp;enommer le Champ…</translation>
    </message>
    <message>
        <source>Delete F&amp;ield</source>
        <translation>Suppr&amp;imer le champ</translation>
    </message>
    <message>
        <source>Add Field</source>
        <translation>Ajouter un champ</translation>
    </message>
    <message>
        <source>Enter new field name:</source>
        <translation>Entrer le nouveau nom du champ :</translation>
    </message>
    <message>
        <source>Rename Field</source>
        <translation>Renommer le champ</translation>
    </message>
    <message>
        <source>Text</source>
        <comment>field type</comment>
        <translation>Texte</translation>
    </message>
    <message>
        <source>Number</source>
        <comment>field type</comment>
        <translation>Nombre</translation>
    </message>
    <message>
        <source>Choice</source>
        <comment>field type</comment>
        <translation>Choix</translation>
    </message>
    <message>
        <source>Combination</source>
        <comment>field type</comment>
        <translation>Combinaison</translation>
    </message>
    <message>
        <source>AutoChoice</source>
        <comment>field type</comment>
        <translation>ChoixAuto</translation>
    </message>
    <message>
        <source>Date</source>
        <comment>field type</comment>
        <translation>Date</translation>
    </message>
    <message>
        <source>Time</source>
        <comment>field type</comment>
        <translation>Heure</translation>
    </message>
    <message>
        <source>Boolean</source>
        <comment>field type</comment>
        <translation>Booléen</translation>
    </message>
    <message>
        <source>URL</source>
        <comment>field type</comment>
        <translation>URL</translation>
    </message>
    <message>
        <source>Path</source>
        <comment>field type</comment>
        <translation>Chemin</translation>
    </message>
    <message>
        <source>InternalLink</source>
        <comment>field type</comment>
        <translation>LienInterne</translation>
    </message>
    <message>
        <source>ExecuteLink</source>
        <comment>field type</comment>
        <translation>LienExécutable</translation>
    </message>
    <message>
        <source>UniqueID</source>
        <comment>field type</comment>
        <translation>IDunique</translation>
    </message>
    <message>
        <source>Email</source>
        <comment>field type</comment>
        <translation>Email</translation>
    </message>
    <message>
        <source>Picture</source>
        <comment>field type</comment>
        <translation>Image</translation>
    </message>
    <message>
        <source>No Alternate</source>
        <comment>no alt link field text</comment>
        <translation>Pas d&apos;alternative</translation>
    </message>
    <message>
        <source>F&amp;ield</source>
        <translation>C&amp;hamp</translation>
    </message>
    <message>
        <source>Fi&amp;eld Type</source>
        <translation>Typ&amp;e de champ</translation>
    </message>
    <message>
        <source>O&amp;utput Format</source>
        <translation>F&amp;ormat de Sortie</translation>
    </message>
    <message>
        <source>Format &amp;Help</source>
        <translation>Aide &amp; formatage</translation>
    </message>
    <message>
        <source>Extra Text</source>
        <translation>Texte Supplémentaire</translation>
    </message>
    <message>
        <source>&amp;Prefix</source>
        <translation>&amp;Préfixe</translation>
    </message>
    <message>
        <source>Suffi&amp;x</source>
        <translation>Suffi&amp;xe</translation>
    </message>
    <message>
        <source>Content Text Handling</source>
        <translation>Gestion du contenu texte</translation>
    </message>
    <message>
        <source>Allow HT&amp;ML rich text</source>
        <translation>Autoriser un texte en HT&amp;ML enrichi</translation>
    </message>
    <message>
        <source>Plai&amp;n text with line breaks</source>
        <translation>Texte &amp;normal avec des sauts de ligne</translation>
    </message>
    <message>
        <source>Default V&amp;alue for New Nodes</source>
        <translation>V&amp;aleur par défaut pour les nouveaux nœuds</translation>
    </message>
    <message>
        <source>Editor Height</source>
        <translation>Hauteur de l&apos;Editeur </translation>
    </message>
    <message>
        <source>Num&amp;ber of text lines</source>
        <translation>Nom&amp;bre de lignes de texte</translation>
    </message>
    <message>
        <source>Field &amp;with alternate text for links</source>
        <translation>Champ &amp;avec texte de remplacement pour les liens</translation>
    </message>
    <message>
        <source>Optional Parameters</source>
        <translation>Paramètres optionnels</translation>
    </message>
    <message>
        <source>Re&amp;quired to be filled</source>
        <translation>Ch&amp;amp obligatoire</translation>
    </message>
    <message>
        <source>Hidden on editor &amp;view</source>
        <translation>Caché en &amp;mode éditeur</translation>
    </message>
    <message>
        <source>File Info Reference</source>
        <translation>Références du Fichier</translation>
    </message>
    <message>
        <source>No Other Reference</source>
        <translation>Pas d&apos;Autre Référence</translation>
    </message>
    <message>
        <source>Any Ancestor Reference</source>
        <translation>Toute Référence à un Ascendant</translation>
    </message>
    <message>
        <source>Parent Reference</source>
        <translation>Référence du Parent</translation>
    </message>
    <message>
        <source>Grandparent Reference</source>
        <translation>Référence du Grand-parent</translation>
    </message>
    <message>
        <source>Great Grandparent Reference</source>
        <translation>Référence de l&apos;Arrière-grand-parent</translation>
    </message>
    <message>
        <source>Child Reference</source>
        <translation>Réference du Fils</translation>
    </message>
    <message>
        <source>Child Count</source>
        <translation>Nombre d&apos;enfant</translation>
    </message>
    <message>
        <source>F&amp;ield List</source>
        <translation>L&amp;iste des champs</translation>
    </message>
    <message>
        <source>Titl&amp;e Format</source>
        <translation>Format du Titr&amp;e</translation>
    </message>
    <message>
        <source>Other Field References</source>
        <translation>Références à d&apos;autres champs</translation>
    </message>
    <message>
        <source>Re&amp;ference Level</source>
        <translation>Niv&amp;eau de référence</translation>
    </message>
    <message>
        <source>Reference Ty&amp;pe</source>
        <translation>Ty&amp;pe de référence</translation>
    </message>
    <message>
        <source>Empty name is not acceptable</source>
        <translation>Un nom vide ne peut être accepté</translation>
    </message>
    <message>
        <source>Name must start with a letter</source>
        <translation>Un nom doit commencer par une lettre</translation>
    </message>
    <message>
        <source>Name cannot start with &quot;xml&quot;</source>
        <translation>Un nom ne peut commencer par &quot;xml&quot;</translation>
    </message>
    <message>
        <source>The following characters are not allowed</source>
        <translation>Les caractères suivants ne sont pas acceptés</translation>
    </message>
    <message>
        <source>Entered name was already used</source>
        <translation>Le nom entré est déja utilisé</translation>
    </message>
    <message>
        <source>Copy Type</source>
        <translation>Copier Type</translation>
    </message>
    <message>
        <source>Derive from original</source>
        <translation>Dérive de l&apos;original</translation>
    </message>
    <message>
        <source>and</source>
        <comment>filter bool</comment>
        <translation>et</translation>
    </message>
    <message>
        <source>or</source>
        <comment>filter bool</comment>
        <translation>ou</translation>
    </message>
    <message>
        <source>&amp;Add New Rule</source>
        <translation>&amp;Ajouter Nouvelle Règle</translation>
    </message>
    <message>
        <source>&amp;Remove Rule</source>
        <translation>&amp;Supprimer Règle</translation>
    </message>
    <message>
        <source>starts with</source>
        <comment>filter rule</comment>
        <translation>commence avec</translation>
    </message>
    <message>
        <source>ends with</source>
        <comment>filter rule</comment>
        <translation>se termine par</translation>
    </message>
    <message>
        <source>contains</source>
        <comment>filter rule</comment>
        <translation>contient</translation>
    </message>
    <message>
        <source>True</source>
        <comment>filter rule</comment>
        <translation>Vrai</translation>
    </message>
    <message>
        <source>False</source>
        <comment>filter rule</comment>
        <translation>Faux</translation>
    </message>
    <message>
        <source>Rule %d</source>
        <translation>Règle %d</translation>
    </message>
    <message>
        <source>default</source>
        <comment>icon name</comment>
        <translation>Par défaut</translation>
    </message>
    <message>
        <source>treeline</source>
        <comment>icon name</comment>
        <translation>treeline</translation>
    </message>
    <message>
        <source>anchor</source>
        <comment>icon name</comment>
        <translation>ancre</translation>
    </message>
    <message>
        <source>arrow_1</source>
        <comment>icon name</comment>
        <translation>flêche_1</translation>
    </message>
    <message>
        <source>arrow_2</source>
        <comment>icon name</comment>
        <translation>flêche_2</translation>
    </message>
    <message>
        <source>arrow_3</source>
        <comment>icon name</comment>
        <translation>flêche_3</translation>
    </message>
    <message>
        <source>arrow_4</source>
        <comment>icon name</comment>
        <translation>flêche_4</translation>
    </message>
    <message>
        <source>arrow_5</source>
        <comment>icon name</comment>
        <translation>flêche_5</translation>
    </message>
    <message>
        <source>bell</source>
        <comment>icon name</comment>
        <translation>sonnerie</translation>
    </message>
    <message>
        <source>book_1</source>
        <comment>icon name</comment>
        <translation>livre_1</translation>
    </message>
    <message>
        <source>book_2</source>
        <comment>icon name</comment>
        <translation>livre_2</translation>
    </message>
    <message>
        <source>book_3</source>
        <comment>icon name</comment>
        <translation>livre_3</translation>
    </message>
    <message>
        <source>bookmark</source>
        <comment>icon name</comment>
        <translation>favori</translation>
    </message>
    <message>
        <source>bulb</source>
        <comment>icon name</comment>
        <translation>ampoule</translation>
    </message>
    <message>
        <source>bullet_1</source>
        <comment>icon name</comment>
        <translation>puce_1</translation>
    </message>
    <message>
        <source>bullet_2</source>
        <comment>icon name</comment>
        <translation>puce_2</translation>
    </message>
    <message>
        <source>bullet_3</source>
        <comment>icon name</comment>
        <translation>puce_3</translation>
    </message>
    <message>
        <source>check_1</source>
        <comment>icon name</comment>
        <translation>vérif_1</translation>
    </message>
    <message>
        <source>check_2</source>
        <comment>icon name</comment>
        <translation>vérif_2</translation>
    </message>
    <message>
        <source>check_3</source>
        <comment>icon name</comment>
        <translation>vérif_3</translation>
    </message>
    <message>
        <source>clock</source>
        <comment>icon name</comment>
        <translation>horloge</translation>
    </message>
    <message>
        <source>colors</source>
        <comment>icon name</comment>
        <translation>couleurs</translation>
    </message>
    <message>
        <source>date_1</source>
        <comment>icon name</comment>
        <translation>date_1</translation>
    </message>
    <message>
        <source>date_2</source>
        <comment>icon name</comment>
        <translation>date_2</translation>
    </message>
    <message>
        <source>disk</source>
        <comment>icon name</comment>
        <translation>disque</translation>
    </message>
    <message>
        <source>doc</source>
        <comment>icon name</comment>
        <translation>doc</translation>
    </message>
    <message>
        <source>euro</source>
        <comment>icon name</comment>
        <translation>euro</translation>
    </message>
    <message>
        <source>folder_1</source>
        <comment>icon name</comment>
        <translation>dossier_1</translation>
    </message>
    <message>
        <source>folder_2</source>
        <comment>icon name</comment>
        <translation>dossier_2</translation>
    </message>
    <message>
        <source>folder_3</source>
        <comment>icon name</comment>
        <translation>dossier_3</translation>
    </message>
    <message>
        <source>gear</source>
        <comment>icon name</comment>
        <translation>engrenage</translation>
    </message>
    <message>
        <source>gnu</source>
        <comment>icon name</comment>
        <translation>gnu</translation>
    </message>
    <message>
        <source>hand</source>
        <comment>icon name</comment>
        <translation>main</translation>
    </message>
    <message>
        <source>heart</source>
        <comment>icon name</comment>
        <translation>coeur</translation>
    </message>
    <message>
        <source>home</source>
        <comment>icon name</comment>
        <translation>accueil</translation>
    </message>
    <message>
        <source>lock_1</source>
        <comment>icon name</comment>
        <translation>serrure_1</translation>
    </message>
    <message>
        <source>lock_2</source>
        <comment>icon name</comment>
        <translation>serrure_2</translation>
    </message>
    <message>
        <source>mag</source>
        <comment>icon name</comment>
        <translation>loupe</translation>
    </message>
    <message>
        <source>mail</source>
        <comment>icon name</comment>
        <translation>courrier</translation>
    </message>
    <message>
        <source>minus</source>
        <comment>icon name</comment>
        <translation>moins</translation>
    </message>
    <message>
        <source>misc</source>
        <comment>icon name</comment>
        <translation>divers</translation>
    </message>
    <message>
        <source>move</source>
        <comment>icon name</comment>
        <translation>déplacer</translation>
    </message>
    <message>
        <source>music</source>
        <comment>icon name</comment>
        <translation>musique</translation>
    </message>
    <message>
        <source>note</source>
        <comment>icon name</comment>
        <translation>note</translation>
    </message>
    <message>
        <source>pencil</source>
        <comment>icon name</comment>
        <translation>crayon</translation>
    </message>
    <message>
        <source>person</source>
        <comment>icon name</comment>
        <translation>personne</translation>
    </message>
    <message>
        <source>plus</source>
        <comment>icon name</comment>
        <translation>plus</translation>
    </message>
    <message>
        <source>printer</source>
        <comment>icon name</comment>
        <translation>imprimante</translation>
    </message>
    <message>
        <source>question</source>
        <comment>icon name</comment>
        <translation>question</translation>
    </message>
    <message>
        <source>rocket</source>
        <comment>icon name</comment>
        <translation>fusée</translation>
    </message>
    <message>
        <source>round_minus</source>
        <comment>icon name</comment>
        <translation>moins cerclé</translation>
    </message>
    <message>
        <source>round_plus</source>
        <comment>icon name</comment>
        <translation>plus cerclé</translation>
    </message>
    <message>
        <source>smiley_1</source>
        <comment>icon name</comment>
        <translation>smiley_1</translation>
    </message>
    <message>
        <source>smiley_2</source>
        <comment>icon name</comment>
        <translation>smiley_2</translation>
    </message>
    <message>
        <source>smiley_3</source>
        <comment>icon name</comment>
        <translation>smiley_3</translation>
    </message>
    <message>
        <source>smiley_4</source>
        <comment>icon name</comment>
        <translation>smiley_4</translation>
    </message>
    <message>
        <source>smiley_5</source>
        <comment>icon name</comment>
        <translation>smiley_5</translation>
    </message>
    <message>
        <source>sphere</source>
        <comment>icon name</comment>
        <translation>sphère</translation>
    </message>
    <message>
        <source>star</source>
        <comment>icon name</comment>
        <translation>étoile</translation>
    </message>
    <message>
        <source>sum</source>
        <comment>icon name</comment>
        <translation>somme</translation>
    </message>
    <message>
        <source>table</source>
        <comment>icon name</comment>
        <translation>tableau</translation>
    </message>
    <message>
        <source>task_1</source>
        <comment>icon name</comment>
        <translation>tache_1</translation>
    </message>
    <message>
        <source>task_2</source>
        <comment>icon name</comment>
        <translation>tache_2</translation>
    </message>
    <message>
        <source>term</source>
        <comment>icon name</comment>
        <translation>terminal</translation>
    </message>
    <message>
        <source>text</source>
        <comment>icon name</comment>
        <translation>texte</translation>
    </message>
    <message>
        <source>trash</source>
        <comment>icon name</comment>
        <translation>poubelle</translation>
    </message>
    <message>
        <source>tux_1</source>
        <comment>icon name</comment>
        <translation>tux_1</translation>
    </message>
    <message>
        <source>tux_2</source>
        <comment>icon name</comment>
        <translation>tux_2</translation>
    </message>
    <message>
        <source>warning</source>
        <comment>icon name</comment>
        <translation>attention</translation>
    </message>
    <message>
        <source>wrench</source>
        <comment>icon name</comment>
        <translation>clé</translation>
    </message>
    <message>
        <source>write</source>
        <comment>icon name</comment>
        <translation>écrire</translation>
    </message>
    <message>
        <source>x_1</source>
        <comment>icon name</comment>
        <translation>x_1</translation>
    </message>
    <message>
        <source>x_2</source>
        <comment>icon name</comment>
        <translation>x_2</translation>
    </message>
    <message>
        <source>x_3</source>
        <comment>icon name</comment>
        <translation>x_3</translation>
    </message>
    <message>
        <source>Set Data Type Icon</source>
        <translation>Configurer Icône Type de Données</translation>
    </message>
    <message>
        <source>Clear &amp;Select</source>
        <translation>Effacer  &amp;Sélection</translation>
    </message>
</context>
<context>
    <name>fieldformat</name>
    <message>
        <source>Optional Digit</source>
        <translation>Chiffre optionnel</translation>
    </message>
    <message>
        <source>Required Digit</source>
        <translation>Un chiffre est requis</translation>
    </message>
    <message>
        <source>Digit or Space (external)</source>
        <translation>Chiffre ou espace (externe)</translation>
    </message>
    <message>
        <source>&lt;space&gt;</source>
        <translation>&lt;espace&gt;</translation>
    </message>
    <message>
        <source>Decimal Point</source>
        <translation>Point décimal</translation>
    </message>
    <message>
        <source>Decimal Comma</source>
        <translation>Virgule décimale</translation>
    </message>
    <message>
        <source>Comma Separator</source>
        <translation>Séparateur virgule</translation>
    </message>
    <message>
        <source>Dot Separator</source>
        <translation>Séparateur point</translation>
    </message>
    <message>
        <source>Space Separator (internal)</source>
        <translation>Séparateur espace  (interne)</translation>
    </message>
    <message>
        <source>Optional Sign</source>
        <translation>Signe optionnel</translation>
    </message>
    <message>
        <source>Required Sign</source>
        <translation>Un signe est requis</translation>
    </message>
    <message>
        <source>Exponent (capital)</source>
        <translation>Exponent (majuscule)</translation>
    </message>
    <message>
        <source>Exponent (small)</source>
        <translation>Exponent (minuscule)</translation>
    </message>
    <message>
        <source>Separator</source>
        <translation>Séparateur</translation>
    </message>
    <message>
        <source>&quot;/&quot; Character</source>
        <translation>Caractère &quot;/&quot;</translation>
    </message>
    <message>
        <source>Example</source>
        <translation>Exemple</translation>
    </message>
    <message>
        <source>Now</source>
        <comment>date stamp setting</comment>
        <translation>Maintenant</translation>
    </message>
    <message>
        <source>Day (1 or 2 digits)</source>
        <translation>Jour (1 ou 2 chiffres)</translation>
    </message>
    <message>
        <source>Day (2 digits)</source>
        <translation>Jour (2 chiffres)</translation>
    </message>
    <message>
        <source>Month (1 or 2 digits)</source>
        <translation>Mois (1 ou 2 chiffres)</translation>
    </message>
    <message>
        <source>Month (2 digits)</source>
        <translation>Mois (2 chiffres)</translation>
    </message>
    <message>
        <source>Month Abbreviation</source>
        <translation>Abréviation de mois</translation>
    </message>
    <message>
        <source>Month Name</source>
        <translation>Nom du mois</translation>
    </message>
    <message>
        <source>Year (2 digits)</source>
        <translation>Année (2 chiffres)</translation>
    </message>
    <message>
        <source>Year (4 digits)</source>
        <translation>Année (4 chiffres)</translation>
    </message>
    <message>
        <source>Weekday (1 digit)</source>
        <translation>Jour de la semaine (1 chiffre)</translation>
    </message>
    <message>
        <source>Weekday Abbreviation</source>
        <translation>Abréviation du jour  de la semaine</translation>
    </message>
    <message>
        <source>Weekday Name</source>
        <translation>Nom du jour de la semaine</translation>
    </message>
    <message>
        <source>Now</source>
        <comment>time stamp setting</comment>
        <translation>Maintenant</translation>
    </message>
    <message>
        <source>Hour (0-23, 1 or 2 digits)</source>
        <translation>Heure (0-23, 1 ou 2 chiffres)</translation>
    </message>
    <message>
        <source>Hour (00-23, 2 digits)</source>
        <translation>Heure (0-23, 2 chiffres)</translation>
    </message>
    <message>
        <source>Hour (1-12, 1 or 2 digits)</source>
        <translation>Heure (1-12, 1 ou 2 chiffres)</translation>
    </message>
    <message>
        <source>Hour (01-12, 2 digits)</source>
        <translation>Heure (01-12, 2 chiffres)</translation>
    </message>
    <message>
        <source>Minute (1 or 2 digits)</source>
        <translation>Minute (1 ou 2 chiffres)</translation>
    </message>
    <message>
        <source>Minute (2 digits)</source>
        <translation>Minute (2 chiffres)</translation>
    </message>
    <message>
        <source>Second (1 or 2 digits)</source>
        <translation>Seconde (1 ou 2 chiffres)</translation>
    </message>
    <message>
        <source>Second (2 digits)</source>
        <translation>Seconde (2 chiffres)</translation>
    </message>
    <message>
        <source>Fractional Seconds</source>
        <translation>Fraction de seconde</translation>
    </message>
    <message>
        <source>AM/PM</source>
        <translation>AM/PM</translation>
    </message>
    <message>
        <source>am/pm</source>
        <translation>am/pm</translation>
    </message>
    <message>
        <source>yes/no</source>
        <translation>oui/non</translation>
    </message>
    <message>
        <source>true/false</source>
        <translation>vrai/faux</translation>
    </message>
    <message>
        <source>T/F</source>
        <translation>V/F</translation>
    </message>
    <message>
        <source>Y/N</source>
        <translation>O/N</translation>
    </message>
    <message>
        <source>today</source>
        <translation>aujourd&apos;hui</translation>
    </message>
    <message>
        <source>yesterday</source>
        <translation>hier</translation>
    </message>
    <message>
        <source>tomorrow</source>
        <translation>demain</translation>
    </message>
    <message>
        <source>now</source>
        <translation>maintenant</translation>
    </message>
    <message>
        <source>add</source>
        <translation>ajouter</translation>
    </message>
    <message>
        <source>remove</source>
        <translation>supprimer</translation>
    </message>
    <message>
        <source>Start Num Example</source>
        <translation>Démarrer exemple Num</translation>
    </message>
    <message>
        <source>Prefix Example</source>
        <translation>Exemple de préfixe</translation>
    </message>
</context>
<context>
    <name>genboolean</name>
    <message>
        <source>true</source>
        <translation>vrai</translation>
    </message>
    <message>
        <source>false</source>
        <translation>faux</translation>
    </message>
    <message>
        <source>yes</source>
        <translation>oui</translation>
    </message>
    <message>
        <source>no</source>
        <translation>non</translation>
    </message>
</context>
<context>
    <name>gendate</name>
    <message>
        <source>January</source>
        <translation>Janvier</translation>
    </message>
    <message>
        <source>February</source>
        <translation>Février</translation>
    </message>
    <message>
        <source>March</source>
        <translation>Mars</translation>
    </message>
    <message>
        <source>April</source>
        <translation>Avril</translation>
    </message>
    <message>
        <source>May</source>
        <translation>Mai</translation>
    </message>
    <message>
        <source>June</source>
        <translation>Juin</translation>
    </message>
    <message>
        <source>July</source>
        <translation>Juillet</translation>
    </message>
    <message>
        <source>August</source>
        <translation>Août</translation>
    </message>
    <message>
        <source>September</source>
        <translation>Septembre</translation>
    </message>
    <message>
        <source>October</source>
        <translation>Octobre</translation>
    </message>
    <message>
        <source>November</source>
        <translation>Novembre</translation>
    </message>
    <message>
        <source>December</source>
        <translation>Décembre</translation>
    </message>
    <message>
        <source>Jan</source>
        <translation>Jan</translation>
    </message>
    <message>
        <source>Feb</source>
        <translation>Fév</translation>
    </message>
    <message>
        <source>Mar</source>
        <translation>Mar</translation>
    </message>
    <message>
        <source>Apr</source>
        <translation>Avr</translation>
    </message>
    <message>
        <source>Jun</source>
        <translation>Jun</translation>
    </message>
    <message>
        <source>Jul</source>
        <translation>Jui</translation>
    </message>
    <message>
        <source>Aug</source>
        <translation>Aoû</translation>
    </message>
    <message>
        <source>Sep</source>
        <translation>Sep</translation>
    </message>
    <message>
        <source>Oct</source>
        <translation>Oct</translation>
    </message>
    <message>
        <source>Nov</source>
        <translation>Nov</translation>
    </message>
    <message>
        <source>Dec</source>
        <translation>Déc</translation>
    </message>
    <message>
        <source>Sunday</source>
        <translation>Dimanche</translation>
    </message>
    <message>
        <source>Monday</source>
        <translation>Lundi</translation>
    </message>
    <message>
        <source>Tuesday</source>
        <translation>Mardi</translation>
    </message>
    <message>
        <source>Wednesday</source>
        <translation>Mercredi</translation>
    </message>
    <message>
        <source>Thursday</source>
        <translation>Jeudi</translation>
    </message>
    <message>
        <source>Friday</source>
        <translation>Vendredi</translation>
    </message>
    <message>
        <source>Saturday</source>
        <translation>Samedi</translation>
    </message>
    <message>
        <source>Sun</source>
        <translation>Dimanche</translation>
    </message>
    <message>
        <source>Mon</source>
        <translation>Lun</translation>
    </message>
    <message>
        <source>Tue</source>
        <translation>Mar</translation>
    </message>
    <message>
        <source>Wed</source>
        <translation>Mer</translation>
    </message>
    <message>
        <source>Thu</source>
        <translation>Jeu</translation>
    </message>
    <message>
        <source>Fri</source>
        <translation>Ven</translation>
    </message>
    <message>
        <source>Sat</source>
        <translation>Sam</translation>
    </message>
    <message>
        <source>May</source>
        <comment>abbrev</comment>
        <translation>Mai</translation>
    </message>
</context>
<context>
    <name>gentime</name>
    <message>
        <source>am</source>
        <translation>am</translation>
    </message>
    <message>
        <source>pm</source>
        <translation>pm</translation>
    </message>
</context>
<context>
    <name>helpview</name>
    <message>
        <source>&amp;Back</source>
        <translation>&amp;Précédent</translation>
    </message>
    <message>
        <source>&amp;Forward</source>
        <translation>&amp;Suivant</translation>
    </message>
    <message>
        <source>&amp;Home</source>
        <translation>&amp;Accueil</translation>
    </message>
    <message>
        <source> Find: </source>
        <translation>Chercher:</translation>
    </message>
    <message>
        <source>Find &amp;Previous</source>
        <translation>Chercher &amp;Précédent</translation>
    </message>
    <message>
        <source>Find &amp;Next</source>
        <translation>Chercher &amp;Suivant</translation>
    </message>
    <message>
        <source>Text string not found</source>
        <translation>Chaîne de  caractères non trouvée</translation>
    </message>
</context>
<context>
    <name>nodeformat</name>
    <message>
        <source>File_Name</source>
        <translation>Fichier_Nom</translation>
    </message>
    <message>
        <source>File_Path</source>
        <translation>Fichier_Chemin</translation>
    </message>
    <message>
        <source>File_Size</source>
        <translation>Fichier_Taille</translation>
    </message>
    <message>
        <source>File_Mod_Date</source>
        <translation>Fichier_Mode_Date</translation>
    </message>
    <message>
        <source>File_Mod_Time</source>
        <translation>Fichier_Mode_Heure</translation>
    </message>
    <message>
        <source>File_Owner</source>
        <translation>Fichier_Propriétaire</translation>
    </message>
    <message>
        <source>Page_Number</source>
        <translation>Page_Numéro</translation>
    </message>
    <message>
        <source>Number_of_Pages</source>
        <translation>Nombre_de_Pages</translation>
    </message>
    <message>
        <source>Level</source>
        <comment>child count field</comment>
        <translation>Niveau</translation>
    </message>
</context>
<context>
    <name>optiondefaults</name>
    <message>
        <source>FileNew</source>
        <translation>FichierNouveau</translation>
    </message>
    <message>
        <source>FileOpen</source>
        <translation>FichierOuvrir</translation>
    </message>
    <message>
        <source>FileSave</source>
        <translation>FichierEnregistrer</translation>
    </message>
    <message>
        <source>FileSaveAs</source>
        <translation>FichierEnregistrerSous</translation>
    </message>
    <message>
        <source>FileExport</source>
        <translation>FichierExporter</translation>
    </message>
    <message>
        <source>FilePrint</source>
        <translation>FichierImprimer</translation>
    </message>
    <message>
        <source>FilePrintOpt</source>
        <translation>FichierOptionsImpression</translation>
    </message>
    <message>
        <source>FileQuit</source>
        <translation>FichierQuitter</translation>
    </message>
    <message>
        <source>EditUndo</source>
        <translation>EditerAnnuler</translation>
    </message>
    <message>
        <source>EditRedo</source>
        <translation>EditerRétablir</translation>
    </message>
    <message>
        <source>EditCut</source>
        <translation>EditerCouper</translation>
    </message>
    <message>
        <source>EditCopy</source>
        <translation>EditerCopier</translation>
    </message>
    <message>
        <source>EditCopyText</source>
        <translation>EditerCopierTexte</translation>
    </message>
    <message>
        <source>EditPaste</source>
        <translation>EditerColler</translation>
    </message>
    <message>
        <source>EditPasteText</source>
        <translation>EditerCollerTexte</translation>
    </message>
    <message>
        <source>EditRename</source>
        <translation>EditerRenommer</translation>
    </message>
    <message>
        <source>EditAddChild</source>
        <translation>EditerAjouterFils</translation>
    </message>
    <message>
        <source>EditDelete</source>
        <translation>EditerSupprimer</translation>
    </message>
    <message>
        <source>EditIndent</source>
        <translation>EditerIndenter</translation>
    </message>
    <message>
        <source>EditUnindent</source>
        <translation>EditerDésindenter</translation>
    </message>
    <message>
        <source>EditMoveUp</source>
        <translation>EditerMonter</translation>
    </message>
    <message>
        <source>EditMoveDown</source>
        <translation>EditerDescendre</translation>
    </message>
    <message>
        <source>ViewDataOutput</source>
        <translation>AffichageDonnées</translation>
    </message>
    <message>
        <source>ViewDataEdit</source>
        <translation>AffichageEditeurDonnées</translation>
    </message>
    <message>
        <source>ViewTitleList</source>
        <translation>AffichageListeTitre</translation>
    </message>
    <message>
        <source>DataSetItemType</source>
        <translation>DonnéesConfigTypeArticle</translation>
    </message>
    <message>
        <source>DataSetDescendType</source>
        <translation>DonnéesConfigTypeDescend</translation>
    </message>
    <message>
        <source>DataConfigType</source>
        <translation>DonnéesConfigType</translation>
    </message>
    <message>
        <source>DataCopyTypes</source>
        <translation>DonnéesCopierTypes</translation>
    </message>
    <message>
        <source>DataChange</source>
        <translation>DonnéesModifier</translation>
    </message>
    <message>
        <source>DataNumber</source>
        <translation>DonnéesNombre</translation>
    </message>
    <message>
        <source>DataCategoryAdd</source>
        <translation>DonnéesAjouterCatégorie</translation>
    </message>
    <message>
        <source>DataCategoryFlat</source>
        <translation>DonnéesAplatirCatégories</translation>
    </message>
    <message>
        <source>DataRefArrange</source>
        <translation>DonnéesOrganiserRef</translation>
    </message>
    <message>
        <source>DataRefFlat</source>
        <translation>DonnéesAplatirRef</translation>
    </message>
    <message>
        <source>ToolsExpand</source>
        <translation>OutilsDévelopper</translation>
    </message>
    <message>
        <source>ToolsCollapse</source>
        <translation>OutilsRéduire</translation>
    </message>
    <message>
        <source>ToolsFind</source>
        <translation>OutilsChercher</translation>
    </message>
    <message>
        <source>ToolsSpellCheck</source>
        <translation>OutilsOrthographVerif</translation>
    </message>
    <message>
        <source>ToolsRemXLST</source>
        <translation>OutilsRemXLST</translation>
    </message>
    <message>
        <source>ToolsGenOptions</source>
        <translation>OutilsGénOptions</translation>
    </message>
    <message>
        <source>ToolsFileOptions</source>
        <translation>OutilsFichierOptions</translation>
    </message>
    <message>
        <source>ToolsBackColor</source>
        <translation>OutilsFondCouleur</translation>
    </message>
    <message>
        <source>ToolsTextColor</source>
        <translation>OutilsTexteCouleur</translation>
    </message>
    <message>
        <source>HelpAbout</source>
        <translation>AideApropos</translation>
    </message>
    <message>
        <source>HelpPlugin</source>
        <translation>AidePlugin</translation>
    </message>
    <message>
        <source>TreeSelectPrev</source>
        <translation>ArbreSélectionPrécédente</translation>
    </message>
    <message>
        <source>TreeSelectNext</source>
        <translation>ArbreSelectSuivante</translation>
    </message>
    <message>
        <source>TreeOpenItem</source>
        <translation>ArbreOuvrirArticle</translation>
    </message>
    <message>
        <source>TreeCloseItem</source>
        <translation>ArbreFermerArticle</translation>
    </message>
    <message>
        <source>TreePrevSibling</source>
        <translation>ArbreFrèrePrécédent</translation>
    </message>
    <message>
        <source>TreeNextSibling</source>
        <translation>ArbreFrèreSuivant</translation>
    </message>
    <message>
        <source>TreeSelectParent</source>
        <translation>ArbreParentSélect</translation>
    </message>
    <message>
        <source>TreePageUp</source>
        <translation>ArbrePagePréc</translation>
    </message>
    <message>
        <source>TreePageDown</source>
        <translation>ArbrePageSuiv</translation>
    </message>
    <message>
        <source>TreeIncremSearch</source>
        <translation>ArbreRechIncrémentale</translation>
    </message>
    <message>
        <source>TreeIncremNext</source>
        <translation>ArbreIncrementSuivant</translation>
    </message>
    <message>
        <source>TreeIncremPrev</source>
        <translation>ArbreIncremtPréc</translation>
    </message>
    <message>
        <source>FileOpenSample</source>
        <translation>OuvrirFichierExample</translation>
    </message>
    <message>
        <source>HelpContents</source>
        <translation>AideContenu</translation>
    </message>
    <message>
        <source>HelpFullReadMe</source>
        <translation>AideComplète</translation>
    </message>
    <message>
        <source>FilePrintPreview</source>
        <translation>AperçuImprFiciher</translation>
    </message>
    <message>
        <source>EditInsertBefore</source>
        <translation>ÉditionInsAvant</translation>
    </message>
    <message>
        <source>EditInsertAfter</source>
        <translation>ÉditInsertAprès</translation>
    </message>
    <message>
        <source>EditMoveFirst</source>
        <translation>ÉditDéplacerPremier</translation>
    </message>
    <message>
        <source>EditMoveLast</source>
        <translation>ÉditionDéplacerDernier</translation>
    </message>
    <message>
        <source>ViewPreviousSelect</source>
        <translation>VoirSélecPréc</translation>
    </message>
    <message>
        <source>ViewNextSelect</source>
        <translation>VoirSélecSuiv</translation>
    </message>
    <message>
        <source>ViewTree</source>
        <translation>VoirArbre</translation>
    </message>
    <message>
        <source>ViewFlat</source>
        <translation>VueAPlat</translation>
    </message>
    <message>
        <source>ViewShowChild</source>
        <translation>VueMontrerEnfant</translation>
    </message>
    <message>
        <source>ViewShowDescend</source>
        <translation>VueMontrerDescendant</translation>
    </message>
    <message>
        <source>DataSort</source>
        <translation>DonnéesTrier</translation>
    </message>
    <message>
        <source>DataFilterCond</source>
        <translation>DonnéesFiltreCond</translation>
    </message>
    <message>
        <source>DataFilterText</source>
        <translation>DonnéesFiltreTexte</translation>
    </message>
    <message>
        <source>DataFilterClear</source>
        <translation>DonnerFiltreVider</translation>
    </message>
    <message>
        <source>ToolsTreeFont</source>
        <translation>OutilsArbrePolice</translation>
    </message>
    <message>
        <source>ToolsOutputFont</source>
        <translation>OutilsPoliceSortie</translation>
    </message>
    <message>
        <source>ToolsEditFont</source>
        <translation>OutilEditPolice</translation>
    </message>
    <message>
        <source>ToolsShortcuts</source>
        <translation>OutilsRaccourcis</translation>
    </message>
    <message>
        <source>ToolsCustomToolbar</source>
        <translation>OutilsPersonnaliser</translation>
    </message>
    <message>
        <source>ToolsDefaultColor</source>
        <translation>OutilsCouleurDéfaut</translation>
    </message>
    <message>
        <source>TextAddBoldTag</source>
        <translation>TexteAjoutBaliseGras</translation>
    </message>
    <message>
        <source>TextAddItalicsTag</source>
        <translation>TexteAjoutBaliseItal</translation>
    </message>
    <message>
        <source>TextAddUnderlineTag</source>
        <translation>TexteAjoutBaliseSouligné</translation>
    </message>
    <message>
        <source>TextAddSizeTag</source>
        <translation>TexteAjoutBaliseTaille</translation>
    </message>
    <message>
        <source>TextAddColorTag</source>
        <translation>TexteAjoutBaliseCouleur</translation>
    </message>
    <message>
        <source>TreeFocusView</source>
        <translation>VueArbre</translation>
    </message>
    <message>
        <source>RightChildPageUp</source>
        <translation>DroiteEnfantMonterPage</translation>
    </message>
    <message>
        <source>RightChildPageDown</source>
        <translation>DroiteEnfantDescendPage</translation>
    </message>
    <message>
        <source>RightParentPageUp</source>
        <translation>DroiteParentMonterPage</translation>
    </message>
    <message>
        <source>RightParentPageDown</source>
        <translation>DroiteParentDescendPage</translation>
    </message>
    <message>
        <source>ViewStatusBar</source>
        <translation>AfficherLaBarreDeStatut</translation>
    </message>
    <message>
        <source>WinNewWindow</source>
        <translation>WinNouvelleFenetre</translation>
    </message>
    <message>
        <source>WinCloseWindow</source>
        <translation>WinFermerFenetre</translation>
    </message>
    <message>
        <source>WinUpdateWindow</source>
        <translation>WinMiseAJourFenetre</translation>
    </message>
</context>
<context>
    <name>optiondlg</name>
    <message>
        <source>&amp;OK</source>
        <translation>&amp;OK</translation>
    </message>
    <message>
        <source>&amp;Cancel</source>
        <translation>&amp;Annuler</translation>
    </message>
</context>
<context>
    <name>printdata</name>
    <message>
        <source>Error initializing printer</source>
        <translation>Erreur à l&apos;initialisation de l&apos;imprimante</translation>
    </message>
</context>
<context>
    <name>printdialogs</name>
    <message>
        <source>Print Preview</source>
        <translation>AperçuAvantImpression</translation>
    </message>
    <message>
        <source>P&amp;rev. Page</source>
        <translation>P&amp;réc.Page</translation>
    </message>
    <message>
        <source>&amp;Next Page</source>
        <translation>Page &amp;Suivante</translation>
    </message>
    <message>
        <source>Print Option&amp;s...</source>
        <translation>Opton&amp;s Impression…</translation>
    </message>
    <message>
        <source>&amp;Print...</source>
        <translation>&amp;Imprimer....</translation>
    </message>
    <message>
        <source>&amp;Close</source>
        <translation>&amp;Fermer</translation>
    </message>
    <message>
        <source>Page %(current)i of %(max)i</source>
        <translation>Page %(current)i de %(max)i</translation>
    </message>
    <message>
        <source>Print Options</source>
        <translation>Options Impression</translation>
    </message>
    <message>
        <source>&amp;General Options</source>
        <translation>Options &amp;Générales</translation>
    </message>
    <message>
        <source>&amp;Page Setup</source>
        <translation>Disposition de la &amp;Page</translation>
    </message>
    <message>
        <source>&amp;Font Selection</source>
        <translation>&amp;Sélection Police</translation>
    </message>
    <message>
        <source>&amp;Header/Footer</source>
        <translation>&amp;En−tête/PiedDePage</translation>
    </message>
    <message>
        <source>Print Pre&amp;view...</source>
        <translation>Aperçu a&amp;vant impression...</translation>
    </message>
    <message>
        <source>P&amp;rint...</source>
        <translation>Imp&amp;rimer…</translation>
    </message>
    <message>
        <source>&amp;OK</source>
        <translation>&amp;OK</translation>
    </message>
    <message>
        <source>&amp;Cancel</source>
        <translation>&amp;Annuler</translation>
    </message>
    <message>
        <source>What to print</source>
        <translation>Qu&apos;imprimer </translation>
    </message>
    <message>
        <source>&amp;Entire tree</source>
        <translation>Arbre &amp;Entier</translation>
    </message>
    <message>
        <source>Selected &amp;branches</source>
        <translation>&amp;Branches sélectionnées</translation>
    </message>
    <message>
        <source>Selected &amp;nodes</source>
        <translation>&amp;Nœuds sélectionnés</translation>
    </message>
    <message>
        <source>Features</source>
        <translation>Fonctionnalités</translation>
    </message>
    <message>
        <source>Draw &amp;lines to children</source>
        <translation>Ligne vers &amp;les enfants</translation>
    </message>
    <message>
        <source>&amp;Include root node</source>
        <translation>&amp;Inclure le nœud racine</translation>
    </message>
    <message>
        <source>Only open no&amp;de children</source>
        <translation>Seulement les enfants des nœuds &amp;ouvert</translation>
    </message>
    <message>
        <source>&amp;Keep first child with parent</source>
        <translation>&amp;Garder le premier enfant avec le parent</translation>
    </message>
    <message>
        <source>Letter (8.5 x 11 in.)</source>
        <translation>Lettre (8.5 × 11 pouces) </translation>
    </message>
    <message>
        <source>Legal (8.5 x 14 in.)</source>
        <translation>Légal (8.5 × 14 pouces)</translation>
    </message>
    <message>
        <source>Tabloid (11 x 17 in.)</source>
        <translation>Tabloïde (11 × 17 pouces)</translation>
    </message>
    <message>
        <source>A3 (279 x 420 mm)</source>
        <translation>A3 (279 × 420 mm)</translation>
    </message>
    <message>
        <source>A4 (210 x 297 mm)</source>
        <translation>A4 (210 × 297 mm)</translation>
    </message>
    <message>
        <source>A5 (148 x 210 mm)</source>
        <translation>A5 (148 × 210 mm)</translation>
    </message>
    <message>
        <source>#10 Envelope (4.125 x 9.5 in.)</source>
        <translation>#10 Enveloppe (4.125 × 9.5 in)</translation>
    </message>
    <message>
        <source>C5 Envelope (163 x 229 mm)</source>
        <translation>C5 Enveloppe (163 × 229 mm)</translation>
    </message>
    <message>
        <source>DL Envelope (110 x 22 mm)</source>
        <translation>DL enveloppe (110 × 22 mm)</translation>
    </message>
    <message>
        <source>inches</source>
        <translation>pouces</translation>
    </message>
    <message>
        <source>centimeters</source>
        <translation>centimètres</translation>
    </message>
    <message>
        <source>millimeters</source>
        <translation>millimèlres</translation>
    </message>
    <message>
        <source>Paper &amp;Size</source>
        <translation>&amp;Taille papier</translation>
    </message>
    <message>
        <source>Orientation</source>
        <translation>Orientation</translation>
    </message>
    <message>
        <source>&amp;Portrait</source>
        <translation>&amp;Portrait</translation>
    </message>
    <message>
        <source>&amp;Landscape</source>
        <translation>&amp;Paysage</translation>
    </message>
    <message>
        <source>&amp;Units</source>
        <translation>&amp;Unités</translation>
    </message>
    <message>
        <source>Columns</source>
        <translation>Colonnes</translation>
    </message>
    <message>
        <source>&amp;Number of columns</source>
        <translation>&amp;Nombre de colonnes</translation>
    </message>
    <message>
        <source>Offsets</source>
        <translation>Offsets</translation>
    </message>
    <message>
        <source>Space &amp;between columns (%s)</source>
        <translation>Espace &amp;entre colonnes (%s)</translation>
    </message>
    <message>
        <source>Child &amp;indent offset (%s)</source>
        <translation>Taille de l&apos;&amp;indentation pour l&apos;enfant(%s)</translation>
    </message>
    <message>
        <source>Horizontal page &amp;margins (%s)</source>
        <translation>&amp;Marges pour une page horizontale (%s)</translation>
    </message>
    <message>
        <source>Vertical page m&amp;argins (%s)</source>
        <translation>M&amp;arges pour une page verticale (%s)</translation>
    </message>
    <message>
        <source>Default Font</source>
        <translation>Police par défaut</translation>
    </message>
    <message>
        <source>Use &amp;Data Output font</source>
        <translation>Police pour sortie des &amp;Données</translation>
    </message>
    <message>
        <source>Select Font</source>
        <translation>Sélectionner police</translation>
    </message>
    <message>
        <source>&amp;Font</source>
        <translation>&amp;Police</translation>
    </message>
    <message>
        <source>Font st&amp;yle</source>
        <translation>St&amp;yle de police</translation>
    </message>
    <message>
        <source>&amp;Size</source>
        <translation>&amp;Taille</translation>
    </message>
    <message>
        <source>Sample</source>
        <translation>Exemple</translation>
    </message>
    <message>
        <source>Name</source>
        <translation>Nom</translation>
    </message>
    <message>
        <source>Type</source>
        <translation>Type</translation>
    </message>
    <message>
        <source>&amp;Header Left</source>
        <translation>&amp;En-tête gauche</translation>
    </message>
    <message>
        <source>Header C&amp;enter</source>
        <translation>En-tête C&amp;entré</translation>
    </message>
    <message>
        <source>He&amp;ader Right</source>
        <translation>En&amp;−tête à Droite</translation>
    </message>
    <message>
        <source>Footer &amp;Left</source>
        <translation>Pied de page &amp;Gauche</translation>
    </message>
    <message>
        <source>Footer Ce&amp;nter</source>
        <translation>Pied de page Ce&amp;ntré</translation>
    </message>
    <message>
        <source>Footer R&amp;ight</source>
        <translation>Pied de page D&amp;roit</translation>
    </message>
    <message>
        <source>Fiel&amp;ds</source>
        <translation>Cham&amp;ps</translation>
    </message>
    <message>
        <source>Field Forma&amp;t</source>
        <translation>Forma&amp;t du champ</translation>
    </message>
    <message>
        <source>Header and Footer</source>
        <translation>En-tête et Pied de pages</translation>
    </message>
    <message>
        <source>Field Format for &quot;%s&quot;</source>
        <translation>Format de champ pour &quot;%s&quot;</translation>
    </message>
    <message>
        <source>Extra Text</source>
        <translation>Texte Supplémentaire</translation>
    </message>
    <message>
        <source>&amp;Prefix</source>
        <translation>&amp;Préfixe</translation>
    </message>
    <message>
        <source>Suffi&amp;x</source>
        <translation>Suff&amp;ixe</translation>
    </message>
    <message>
        <source>O&amp;utput Format</source>
        <translation>Format de s&amp;ortie</translation>
    </message>
    <message>
        <source>Format &amp;Help</source>
        <translation>Format de &amp;l&apos;Aide</translation>
    </message>
    <message>
        <source>Content Text Handling</source>
        <translation>Gestion du contenu texte</translation>
    </message>
    <message>
        <source>Allow HT&amp;ML rich text</source>
        <translation>Autoriser le texte HT&amp;ML enrichi</translation>
    </message>
    <message>
        <source>Plai&amp;n text with line breaks</source>
        <translation>Texte &amp;normal avec saut de ligne</translation>
    </message>
</context>
<context>
    <name>treedialogs</name>
    <message>
        <source>Fields</source>
        <translation>Champs</translation>
    </message>
    <message>
        <source>Move &amp;Up</source>
        <translation>Déplacer En &amp;haut</translation>
    </message>
    <message>
        <source>&amp;OK</source>
        <translation>&amp;OK</translation>
    </message>
    <message>
        <source>&amp;Cancel</source>
        <translation>&amp;Annuler</translation>
    </message>
    <message>
        <source>Set Data Types</source>
        <translation>Configurer le Type de Données</translation>
    </message>
    <message>
        <source>Set &amp;Selection</source>
        <translation>Configurer les &amp;Noeuds Sélectionnés</translation>
    </message>
    <message>
        <source>Set S&amp;election&apos;s Children</source>
        <translation>Configurer les F&amp;ils de la sélection</translation>
    </message>
    <message>
        <source>Set All &amp;Descendants</source>
        <translation>Configurer Tous les &amp;Descendants</translation>
    </message>
    <message>
        <source>Set Descendants C&amp;ondtionally...</source>
        <translation>Configurer les Descendants &amp;Conditionnellement...</translation>
    </message>
    <message>
        <source>&amp;Close</source>
        <translation>&amp;Fermer</translation>
    </message>
    <message>
        <source>Selection = &quot;%s&quot;</source>
        <translation>Sélection = &quot;%s&quot;</translation>
    </message>
    <message>
        <source>Multiple Selection</source>
        <translation>Sélection multiple</translation>
    </message>
    <message>
        <source>No Selection</source>
        <translation>Pas de Sélection</translation>
    </message>
    <message>
        <source>Select Type</source>
        <translation>Type de Sélection</translation>
    </message>
    <message>
        <source>Change from data type</source>
        <translation>Changer à partir du type de données</translation>
    </message>
    <message>
        <source>descend</source>
        <comment>sort direction</comment>
        <translation>descendant</translation>
    </message>
    <message>
        <source>ascend</source>
        <comment>sort direction</comment>
        <translation>ascendant</translation>
    </message>
    <message>
        <source>Direction</source>
        <translation>Direction</translation>
    </message>
    <message>
        <source>Change Selection</source>
        <translation>Changer la Sélection</translation>
    </message>
    <message>
        <source>&amp;Field</source>
        <translation>&amp;Champ</translation>
    </message>
    <message>
        <source>&amp;New Value</source>
        <translation>&amp;Nouvelle Valeur</translation>
    </message>
    <message>
        <source>Export File</source>
        <translation>Exporter</translation>
    </message>
    <message>
        <source>Export Type</source>
        <translation>Type d&apos;export</translation>
    </message>
    <message>
        <source>&amp;HTML single file output</source>
        <translation>&amp;Fichier HTML</translation>
    </message>
    <message>
        <source>HTML &amp;directories output</source>
        <translation type="obsolete">&amp;Dossiers HTML</translation>
    </message>
    <message>
        <source>&amp;XSLT output</source>
        <translation>&amp;XSLT</translation>
    </message>
    <message>
        <source>TreeLine &amp;subtree</source>
        <translation>&amp;Branche TreeLine</translation>
    </message>
    <message>
        <source>&amp;Tabbed title text</source>
        <translation>&amp;Texte des titres tabulés</translation>
    </message>
    <message>
        <source>&amp;Mozilla HTML bookmarks</source>
        <translation>Favoris &amp;HTML Mozilla</translation>
    </message>
    <message>
        <source>&amp;Generic XML</source>
        <translation>Fichier &amp;générique XML</translation>
    </message>
    <message>
        <source>Export Options</source>
        <translation>Options Export</translation>
    </message>
    <message>
        <source>&amp;Include root node</source>
        <translation>&amp;Inclure le noeud racine</translation>
    </message>
    <message>
        <source>Include print header &amp;&amp; &amp;footer</source>
        <translation>Inclure en-tête &amp;&amp; &amp;pied de page d&apos;impression</translation>
    </message>
    <message>
        <source>Co&amp;lumns</source>
        <translation>Co&amp;lonnes</translation>
    </message>
    <message>
        <source>Data Numbering</source>
        <translation>Numérotation des Données</translation>
    </message>
    <message>
        <source>&amp;Number Field</source>
        <translation>&amp;Champ de Numérotation</translation>
    </message>
    <message>
        <source>Root Node</source>
        <translation>Noeud Racine</translation>
    </message>
    <message>
        <source>Number Style</source>
        <translation>Style de la numérotation</translation>
    </message>
    <message>
        <source>Outline (&amp;discrete numbers)</source>
        <translation>Outline (&amp;redémarre la numérotation pour chaque groupe de fils)</translation>
    </message>
    <message>
        <source>&amp;Section (append to parent number)</source>
        <translation>&amp;Section (ajoute le nombre du parent)</translation>
    </message>
    <message>
        <source>Single &amp;level (children only)</source>
        <translation>&amp;Niveau unique (fils seulement)</translation>
    </message>
    <message>
        <source>Number &amp;Format</source>
        <translation>&amp;Format des Nombres</translation>
    </message>
    <message>
        <source>for Level</source>
        <translation>pour Niveau</translation>
    </message>
    <message>
        <source>Initial N&amp;umber</source>
        <translation>No&amp;mbre Initial</translation>
    </message>
    <message>
        <source>Start first level at number</source>
        <translation>Commencer le premier niveau à la valeur</translation>
    </message>
    <message>
        <source>Illegal characters in field (only alpa-numerics &amp; underscores allowed)</source>
        <translation>Caractères illégaux dans le champ (sont autorisés uniquement alphanumérique &amp; sous-lignés)</translation>
    </message>
    <message>
        <source>Find</source>
        <translation>Chercher</translation>
    </message>
    <message>
        <source>Enter key words</source>
        <translation>Entrer les mots clés</translation>
    </message>
    <message>
        <source>Find &amp;Previous</source>
        <translation>Chercher &amp;Précédent</translation>
    </message>
    <message>
        <source>Find &amp;Next</source>
        <translation>Chercher &amp;Suivant</translation>
    </message>
    <message>
        <source>Text string not found</source>
        <translation>Chaîne de  caractères non trouvée</translation>
    </message>
    <message>
        <source>Spell Check</source>
        <translation>Vérification orthographique</translation>
    </message>
    <message>
        <source>Not in Dictionary</source>
        <translation>Pas dans le dictionnaire</translation>
    </message>
    <message>
        <source>Word:</source>
        <translation>Mot:</translation>
    </message>
    <message>
        <source>Context:</source>
        <translation>Contexte:</translation>
    </message>
    <message>
        <source>Suggestions</source>
        <translation>Suggestions</translation>
    </message>
    <message>
        <source>Ignor&amp;e</source>
        <translation>Ignor&amp;er</translation>
    </message>
    <message>
        <source>&amp;Ignore All</source>
        <translation>&amp;Ignorer Tout</translation>
    </message>
    <message>
        <source>&amp;Add</source>
        <translation>&amp;Ajouter</translation>
    </message>
    <message>
        <source>Add &amp;Lowercase</source>
        <translation>Ajouter &amp;Minuscule</translation>
    </message>
    <message>
        <source>&amp;Replace</source>
        <translation>&amp;Remplacer</translation>
    </message>
    <message>
        <source>Re&amp;place All</source>
        <translation>Rem&amp;placer Tout</translation>
    </message>
    <message>
        <source>Encrypted File Password</source>
        <translation>Mot de passe encrypté</translation>
    </message>
    <message>
        <source>Type Password:</source>
        <translation>Entrer le mot de passe:</translation>
    </message>
    <message>
        <source>Re-Type Password:</source>
        <translation>Entrer à nouveau le mot de passe:</translation>
    </message>
    <message>
        <source>Remember password during this session</source>
        <translation>Se souvenir du mot de passe pendant cette session</translation>
    </message>
    <message>
        <source>Zero-length passwords are not permitted</source>
        <translation>Les mots de passe de longueur zéro ne sont pas autorisés</translation>
    </message>
    <message>
        <source>Re-typed password did not match</source>
        <translation>Le mot de passe entré la deuxième fois ne correspond pas</translation>
    </message>
    <message>
        <source>TreeLine Plugins</source>
        <translation>Plugins TreeLine</translation>
    </message>
    <message>
        <source>Plugin Modules Loaded</source>
        <translation>Modules Plugins Chargés</translation>
    </message>
    <message>
        <source>Set Descendants Conditionally</source>
        <translation>Configurer Descendants Conditionnellement</translation>
    </message>
    <message>
        <source>Sorting</source>
        <translation>Tri</translation>
    </message>
    <message>
        <source>What to Sort</source>
        <translation>Que trie−t−on</translation>
    </message>
    <message>
        <source>&amp;Entire tree</source>
        <translation>L&apos;arbre &amp;Entier</translation>
    </message>
    <message>
        <source>Selected &amp;branches</source>
        <translation>Les &amp;branches sélectionnées</translation>
    </message>
    <message>
        <source>Selection&apos;s childre&amp;n</source>
        <translation>Les e&amp;nfants de la sélection</translation>
    </message>
    <message>
        <source>Selection&apos;s &amp;siblings</source>
        <translation>Les frères de la &amp;sélection</translation>
    </message>
    <message>
        <source>Sort Method</source>
        <translation>Méthode de tri</translation>
    </message>
    <message>
        <source>All &amp;types</source>
        <translation>Tous les &amp;types</translation>
    </message>
    <message>
        <source>C&amp;hoose types</source>
        <translation>C&amp;hoisir les types</translation>
    </message>
    <message>
        <source>Titles only, ascendin&amp;g</source>
        <translation>Uniquement les titres, croissan&amp;t</translation>
    </message>
    <message>
        <source>Titles only, &amp;descending</source>
        <translation>Uniquement les titres, &amp;décroissant</translation>
    </message>
    <message>
        <source>Choose T&amp;ype(s)</source>
        <translation>Choisir le(s) t&amp;ype(s)</translation>
    </message>
    <message>
        <source>Select &amp;Fields in Order as Sort Keys</source>
        <translation>Choisir les &amp;champs dans l&apos;ordre comme clés de tri</translation>
    </message>
    <message>
        <source>&amp;Apply</source>
        <translation>&amp;Appliquer</translation>
    </message>
    <message>
        <source>Sorting by titles</source>
        <translation>Tri par les titres</translation>
    </message>
    <message>
        <source>Select types to sort</source>
        <translation>Sélectionner les types à trier</translation>
    </message>
    <message>
        <source>No common fields found in selected types</source>
        <translation>Pas de champ commun avec les types sélectionnés</translation>
    </message>
    <message>
        <source>Select fields as sort keys</source>
        <translation>Sélectionner les champs comme clés de tri</translation>
    </message>
    <message>
        <source>To change a field direction, use a right mouse click or the left/right keys</source>
        <translation>Pour changer l&apos;ordre sur un champ, faire un clic droit ou utiliser les touches gauche/droite</translation>
    </message>
    <message>
        <source>ALL</source>
        <comment>all languages selection for templates</comment>
        <translation>TOUS</translation>
    </message>
    <message>
        <source>New File</source>
        <translation>Nouveau Fichier</translation>
    </message>
    <message>
        <source>&amp;Select Template</source>
        <translation>&amp;Sélectionner un modèle</translation>
    </message>
    <message>
        <source>&amp;Language filter</source>
        <translation>Filtre de &amp;Langue</translation>
    </message>
    <message>
        <source>Default - No template - Single line text</source>
        <translation>Défaut - Pas de modèles - Texte sur une seule ligne</translation>
    </message>
    <message>
        <source>T&amp;able of node or child data</source>
        <translation>T&amp;ableau des nœuds ou données du fils</translation>
    </message>
    <message>
        <source>XBEL boo&amp;kmarks</source>
        <translation>Fav&amp;oris XBEL</translation>
    </message>
    <message>
        <source>ODF Text Fo&amp;rmat</source>
        <translation>Fo&amp;rmat de texte ODF </translation>
    </message>
    <message>
        <source>What to Export</source>
        <translation>Que faut−il exporter</translation>
    </message>
    <message>
        <source>Selected &amp;nodes</source>
        <translation>Les &amp;nœuds sélectionnés</translation>
    </message>
    <message>
        <source>Only o&amp;pen node children</source>
        <translation>Uniquement les enfants des nœuds &amp;ouverts</translation>
    </message>
    <message>
        <source>Number only where field already &amp;exists</source>
        <translation>Numéro uniqu&amp;ement si le champ existe déjà</translation>
    </message>
    <message>
        <source>Keyboard Shortcuts</source>
        <translation>Raccourcis clavier</translation>
    </message>
    <message>
        <source>&amp;Menu Items</source>
        <translation>Articles du &amp;Menu</translation>
    </message>
    <message>
        <source>&amp;Non-menu Items</source>
        <translation>Articles &amp;hors menus</translation>
    </message>
    <message>
        <source>Key %(key)s already used for &quot;%(cmd)s&quot;</source>
        <translation>La touche %(key)s est déjà utilisée pour &quot;%(cmd)s&quot;</translation>
    </message>
    <message>
        <source>Clear Key</source>
        <translation>Remettre la touche à 0</translation>
    </message>
    <message>
        <source>--Separator--</source>
        <translation>−Séparateur−</translation>
    </message>
    <message>
        <source>Customize Toolbars</source>
        <translation>Personnaliser les barres d&apos;&apos;outils</translation>
    </message>
    <message>
        <source>Toolbar &amp;Size</source>
        <translation>&amp;Taille des barres d&apos;outils</translation>
    </message>
    <message>
        <source>Small Icons</source>
        <translation>Petites icônes</translation>
    </message>
    <message>
        <source>Large Icons</source>
        <translation>Grandes icônes</translation>
    </message>
    <message>
        <source>Toolbar Quantity</source>
        <translation>Nombre de barres d&apos;outls</translation>
    </message>
    <message>
        <source>&amp;Toolbars</source>
        <translation>&amp;Barre d&apos;Outils</translation>
    </message>
    <message>
        <source>A&amp;vailable Commands</source>
        <translation>Comma&amp;ndes disponibles</translation>
    </message>
    <message>
        <source>Menu</source>
        <translation>Menu</translation>
    </message>
    <message>
        <source>Tool&amp;bar Commands</source>
        <translation>Commandes des &amp;barres d&apos;outils</translation>
    </message>
    <message>
        <source>Move &amp;Down</source>
        <translation>&amp;Descendre</translation>
    </message>
    <message>
        <source>HTML &amp;directory tables</source>
        <translation>HTML &amp;tables des répertoires</translation>
    </message>
    <message>
        <source>HTML directory &amp;pages</source>
        <translation>HTML &amp;pages des répertoires</translation>
    </message>
    <message>
        <source>Restore Defaults</source>
        <translation>Restoration de la configuration par défaut</translation>
    </message>
</context>
<context>
    <name>treedoc</name>
    <message>
        <source>Main</source>
        <comment>default root title</comment>
        <translation>Base</translation>
    </message>
    <message>
        <source>FOLDER</source>
        <comment>bookmark format folder name</comment>
        <translation>REPERTOIRE</translation>
    </message>
    <message>
        <source>BOOKMARK</source>
        <comment>bookmark format name</comment>
        <translation>FAVORIS</translation>
    </message>
    <message>
        <source>SEPARATOR</source>
        <comment>bookmark format separator name</comment>
        <translation>SEPARATEUR</translation>
    </message>
    <message>
        <source>Could not open as treeline file</source>
        <translation>Imossible d&apos;ouvrir en tant que fichier treeline</translation>
    </message>
    <message>
        <source>Error in tabbed list</source>
        <translation>Erreur dans la liste tabulée</translation>
    </message>
    <message>
        <source>Too few headings to read data as table</source>
        <translation>Insuffisamment d&apos;en-têtes pour pouvoir lire les données comme un tableau</translation>
    </message>
    <message>
        <source>Title</source>
        <comment>title field name</comment>
        <translation>Titre</translation>
    </message>
    <message>
        <source>Problem with Unicode characters in file</source>
        <translation>Problèmes avec les caractères de type Unicode dans le fichier</translation>
    </message>
    <message>
        <source>Could not open as XBEL file</source>
        <translation>Impossibel d&apos;ouvrir le fichier en tant que fichier XBEL</translation>
    </message>
    <message>
        <source>Bookmarks</source>
        <translation>Favoris</translation>
    </message>
    <message>
        <source>Could not open as HTML bookmark file</source>
        <translation>Impossible d&apos;ouvrir le fichier en tant que fichier de favoris</translation>
    </message>
    <message>
        <source>Could not open XML file</source>
        <translation>Impossible d&apos;ouvrir le fichier XML</translation>
    </message>
    <message>
        <source>Bad file format in %s</source>
        <translation>Format de fichier incorrect pour %s</translation>
    </message>
    <message>
        <source>Could not unzip ODF file</source>
        <translation>Extraction impossible</translation>
    </message>
    <message>
        <source>Could not open corrupt ODF file</source>
        <translation>Ouverture du fichier impossible ; fichier ODF corrompu</translation>
    </message>
    <message>
        <source>Error - cannot write file to %s</source>
        <translation>Erreur - Ne peut écrire le fichier dans %s</translation>
    </message>
</context>
<context>
    <name>treeeditviews</name>
    <message>
        <source>&amp;Bold</source>
        <translation type="obsolete">&amp;Gras</translation>
    </message>
    <message>
        <source>&amp;Italics</source>
        <translation type="obsolete">&amp;Italiques</translation>
    </message>
    <message>
        <source>&amp;Underline</source>
        <translation type="obsolete">&amp;Souligné</translation>
    </message>
    <message>
        <source>&amp;Size...</source>
        <translation type="obsolete">&amp;Taille...</translation>
    </message>
    <message>
        <source>&amp;Color...</source>
        <translation type="obsolete">&amp;Couleur...</translation>
    </message>
    <message>
        <source>Browse for file name</source>
        <translation>Parcourir pour obtenir un nom de fichier</translation>
    </message>
    <message>
        <source>All Files</source>
        <translation>Tous les fichiers</translation>
    </message>
    <message>
        <source>External Editor</source>
        <translation>Editeur externe</translation>
    </message>
    <message>
        <source>Could not find an external editor.
Manually locate?
(or set EDITOR env variable)</source>
        <translation>Impossible de trouver un éditeur externe.
Le chercher manuellement?
(ou alors positionner la variable d&apos;env. EDITOR)</translation>
    </message>
    <message>
        <source>&amp;Browse</source>
        <translation>&amp;Parcourir</translation>
    </message>
    <message>
        <source>&amp;Cancel</source>
        <translation>&amp;Annuler</translation>
    </message>
    <message>
        <source>Programs</source>
        <translation>Programmes</translation>
    </message>
    <message>
        <source>Locate external editor</source>
        <translation>Localiser un éditeur externe</translation>
    </message>
    <message>
        <source>&amp;External Editor...</source>
        <translation>&amp;Editeur Externe...</translation>
    </message>
    <message>
        <source>&amp;Modify Type Config...</source>
        <translation>&amp;Modifier config type…</translation>
    </message>
    <message>
        <source>Modify &amp;Field Config...</source>
        <translation>Modif config &amp;champ…</translation>
    </message>
    <message>
        <source>All</source>
        <translation>Tous</translation>
    </message>
    <message>
        <source>Node %(node_num)d of %(total_num)d</source>
        <translation>Nœud %(node_num)d of %(total_num)d</translation>
    </message>
    <message>
        <source>Nodes %(start_node)d-%(end_node)d of %(total_num)d</source>
        <translation>Nœud %(start_node)d-%(end_node)d de %(total_num)d</translation>
    </message>
    <message>
        <source>&amp;Add Internal Link...</source>
        <translation>&amp;Ajout d&apos;un lien interne...</translation>
    </message>
</context>
<context>
    <name>treeflatview</name>
    <message>
        <source>Search for:</source>
        <translation>Chercher:</translation>
    </message>
    <message>
        <source>Search for: %s</source>
        <translation>Chercher: %s</translation>
    </message>
    <message>
        <source>Search for: %s  (not found)</source>
        <translation>Chercher: %s  (non trouvé)</translation>
    </message>
    <message>
        <source>Next:  %s</source>
        <translation>Suivant:  %s</translation>
    </message>
    <message>
        <source>Next:  %s  (not found)</source>
        <translation>Suivant:  %s  (non trouvé)</translation>
    </message>
    <message>
        <source>Previous:  %s</source>
        <translation>Précédent:  %s</translation>
    </message>
    <message>
        <source>Previous:  %s  (not found)</source>
        <translation>Précédent:  %s  (non trouvé)</translation>
    </message>
</context>
<context>
    <name>treeformats</name>
    <message>
        <source>ROOT</source>
        <comment>root format default name</comment>
        <translation>RACINE</translation>
    </message>
    <message>
        <source>DEFAULT</source>
        <comment>default format name</comment>
        <translation>DEFAUT</translation>
    </message>
    <message>
        <source>Name</source>
        <comment>default field name</comment>
        <translation>Nom</translation>
    </message>
    <message>
        <source>Text</source>
        <comment>text field name</comment>
        <translation>Texte</translation>
    </message>
    <message>
        <source>Link</source>
        <comment>link field name</comment>
        <translation>Lien</translation>
    </message>
</context>
<context>
    <name>treeitem</name>
    <message>
        <source>New</source>
        <translation>Nouveau</translation>
    </message>
    <message>
        <source>[BLANK TITLE]</source>
        <translation>[TITRE VIDE]</translation>
    </message>
    <message>
        <source>Parent: </source>
        <translation>Parent: </translation>
    </message>
    <message>
        <source>TYPE</source>
        <comment>child category suffix</comment>
        <translation>TYPE</translation>
    </message>
    <message>
        <source>Error - cannot create directory %s</source>
        <translation>Erreur − ne peut créer le dossier %s</translation>
    </message>
    <message>
        <source>Error - cannot write file to %s</source>
        <translation>Erreur - Ne peut écrire le fichier dans %s</translation>
    </message>
</context>
<context>
    <name>treeline</name>
    <message>
        <source>Error</source>
        <translation>Erreur</translation>
    </message>
    <message>
        <source>Error loading XML Parser
See TreeLine ReadMe file</source>
        <translation>Erreur en chargeant le Décodeur XML
Se référer au fichier TreeLine LisezMoi</translation>
    </message>
</context>
<context>
    <name>treemainwin</name>
    <message>
        <source>TreeLine Files - Plain</source>
        <translation>Fichiers TreeLine - Normal</translation>
    </message>
    <message>
        <source>TreeLine Files - Compressed</source>
        <translation>Fichiers TreeLine - Compressé</translation>
    </message>
    <message>
        <source>TreeLine Files - Encrypted</source>
        <translation>Fichiers TreeLine - Encrypté</translation>
    </message>
    <message>
        <source>TreeLine Files</source>
        <translation>Fichiers TreeLine</translation>
    </message>
    <message>
        <source>All Files</source>
        <translation>Tous le Fichiers</translation>
    </message>
    <message>
        <source>Text Files</source>
        <translation>Fichiers Texte</translation>
    </message>
    <message>
        <source>Treepad Files</source>
        <translation>Fichiers Treepad</translation>
    </message>
    <message>
        <source>XBEL Bookmarks</source>
        <translation>Favoris XBEL</translation>
    </message>
    <message>
        <source>Mozilla Bookmarks</source>
        <translation>Favoris Mozilla</translation>
    </message>
    <message>
        <source>Html Files</source>
        <translation>Fichiers Html</translation>
    </message>
    <message>
        <source>XSLT Files</source>
        <translation>Fichiers XSLT</translation>
    </message>
    <message>
        <source>Table Files</source>
        <translation>Fichiers Tableaux</translation>
    </message>
    <message>
        <source>XML Files</source>
        <translation>Fichiers XML</translation>
    </message>
    <message>
        <source>Ready</source>
        <translation type="obsolete">Prêt</translation>
    </message>
    <message>
        <source>Could not load plugin module %s</source>
        <translation>Impossible de charger le module plugin %s</translation>
    </message>
    <message>
        <source>Backup file &quot;%s&quot; exists.
A previous session may have crashed.</source>
        <translation type="obsolete">Le fichier de sauvegarde &quot;%s&quot; existe.
Il est possible qu&apos;une session précédente ait crashé.</translation>
    </message>
    <message>
        <source>&amp;Restore Backup</source>
        <translation type="obsolete">&amp;Restaure Sauvegarde</translation>
    </message>
    <message>
        <source>&amp;Delete Backup</source>
        <translation type="obsolete">&amp;Supprime Sauvegarde</translation>
    </message>
    <message>
        <source>&amp;Cancel File Open</source>
        <translation type="obsolete">&amp;Annule Fichier Ouvert</translation>
    </message>
    <message>
        <source>Error - could not restore backup</source>
        <translation type="obsolete">Erreur - impossible de restaurer la sauvegarde</translation>
    </message>
    <message>
        <source>Error - could not read file &quot;%s&quot;</source>
        <translation>Erreur - imossible de lire le fichier &quot;%s&quot;</translation>
    </message>
    <message>
        <source>Import Text</source>
        <translation type="obsolete">Importer le Texte</translation>
    </message>
    <message>
        <source>Choose Text Import Method</source>
        <translation type="obsolete">Choisir la Méthode d&apos;importation de Texte</translation>
    </message>
    <message>
        <source>Tab &amp;indented text, one node per line</source>
        <translation type="obsolete">Texte &amp;indenté avec tabulations, un noeud par ligne</translation>
    </message>
    <message>
        <source>Text &amp;table with header row, one node per line</source>
        <translation type="obsolete">Texte &amp;tableau avec rangée d&apos;en-tête, un noeud par ligne</translation>
    </message>
    <message>
        <source>Plain text, one &amp;node per line (CR delimitted)</source>
        <translation type="obsolete">Texte normal, un &amp;noeud par ligne (délimité par des CR)</translation>
    </message>
    <message>
        <source>Plain text &amp;paragraphs (blank line delimitted)</source>
        <translation type="obsolete">&amp;Paragraphes de texte normal (délimité par des lignes vides)</translation>
    </message>
    <message>
        <source>Treepad &amp;file (text nodes only)</source>
        <translation type="obsolete">&amp;Fichier Treepad (noeuds texte seulement)</translation>
    </message>
    <message>
        <source>&amp;XML bookmarks (XBEL format)</source>
        <translation type="obsolete">&amp;XML favoris (format XBEL)</translation>
    </message>
    <message>
        <source>&amp;HTML bookmarks (Mozilla format)</source>
        <translation type="obsolete">favoris &amp;HTML (format Mozilla)</translation>
    </message>
    <message>
        <source>&amp;Generic XML (Non-TreeLine file)</source>
        <translation type="obsolete">&amp;Générique XML (fichier Non-TreeLine)</translation>
    </message>
    <message>
        <source>Error - %s</source>
        <translation type="obsolete">Erreur - %s</translation>
    </message>
    <message>
        <source>&amp;Yes</source>
        <translation>&amp;Oui</translation>
    </message>
    <message>
        <source>&amp;No</source>
        <translation>&amp;Non</translation>
    </message>
    <message>
        <source>&amp;Cancel</source>
        <translation>&amp;Annuler</translation>
    </message>
    <message>
        <source>Error - Could not write to %s</source>
        <translation>Erreur - impossible d&apos;écrire dans le fichier nommé %s</translation>
    </message>
    <message>
        <source>Save As</source>
        <translation>Enregistrer sous</translation>
    </message>
    <message>
        <source>Export Html</source>
        <translation>Exporter Html</translation>
    </message>
    <message>
        <source>Export to Directory</source>
        <translation>Exporter dans un Dossier</translation>
    </message>
    <message>
        <source>A link to a stylesheet can be added to the XSL file
Enter a CSS filename (blank for none)</source>
        <translation>Un lien vers un stylesheet peut être ajouté au fichier XSL
Entrer un nom de fichier CSS (rien pour aucun)</translation>
    </message>
    <message>
        <source>Export XSLT</source>
        <translation>Exporter XSLT</translation>
    </message>
    <message>
        <source>Export Subtree</source>
        <translation>Exporter Branche</translation>
    </message>
    <message>
        <source>Export Table</source>
        <translation>Exporter Tableau</translation>
    </message>
    <message>
        <source>Export Titles</source>
        <translation>Exporter Titres</translation>
    </message>
    <message>
        <source>Export XBEL Bookmarks</source>
        <translation>Exporter Favoris XBEL</translation>
    </message>
    <message>
        <source>Export Html Bookmarks</source>
        <translation>Exporter Favoris Html</translation>
    </message>
    <message>
        <source>Export Generic XML</source>
        <translation>Exporter XML Générique</translation>
    </message>
    <message>
        <source>Child indent offset (points)</source>
        <translation>Offset indentation du fils (en points)</translation>
    </message>
    <message>
        <source>Open Configuration File</source>
        <translation>Ouvrir Fichier Configuration</translation>
    </message>
    <message>
        <source>Filter Data</source>
        <translation>Filtrer Données</translation>
    </message>
    <message>
        <source>Select data type</source>
        <translation>Sélection du type de données</translation>
    </message>
    <message>
        <source>No common fields to set</source>
        <translation>Pas de champs communs à configurer</translation>
    </message>
    <message>
        <source>Category Fields</source>
        <translation>Champ du Classement</translation>
    </message>
    <message>
        <source>Select fields for new level</source>
        <translation>Sélection des champs pour le nouveau niveau</translation>
    </message>
    <message>
        <source>Cannot expand without common fields</source>
        <translation>Impossible de développer sans champs communs</translation>
    </message>
    <message>
        <source>Reference Field</source>
        <translation>Champ Référenciel</translation>
    </message>
    <message>
        <source>Select field with parent references</source>
        <translation>Sélectionner champ avec les références du parent</translation>
    </message>
    <message>
        <source>Flatten by Reference</source>
        <translation>Aplatir par Référence</translation>
    </message>
    <message>
        <source>Enter new field name for parent references:</source>
        <translation>Entrer le nouveau nom de champ pour les références du parent:</translation>
    </message>
    <message>
        <source>Could not find either aspell.exe or ispell.exe
Manually locate?</source>
        <translation>Impossible de trouver aspell.exe ou ispell.exe
Les localiser manuellement?</translation>
    </message>
    <message>
        <source>&amp;Browse</source>
        <translation>&amp;Parcourir</translation>
    </message>
    <message>
        <source>Program (*.exe)</source>
        <translation>Programme (*.exe)</translation>
    </message>
    <message>
        <source>Locate aspell.exe or ipsell.exe</source>
        <translation>Localiser aspell.exe ou ispell.exe</translation>
    </message>
    <message>
        <source>TreeLine Spell Check Error
Make sure aspell or ispell is installed</source>
        <translation>Erreur de Vérification Orthographique TreeLine
Assurez vous que aspell ou ispell est installé</translation>
    </message>
    <message>
        <source>TreeLine Spell Check</source>
        <translation>Vérification Orthographique TreeLIne</translation>
    </message>
    <message>
        <source>Finished checking the branch
Continue from the root branch?</source>
        <translation>Fin de la vérification de la branche
Continuer à partir de la branche racine?</translation>
    </message>
    <message>
        <source>Finished checking the branch</source>
        <translation>Fin de vérification de la branche</translation>
    </message>
    <message>
        <source>General Options</source>
        <translation>Options Générales</translation>
    </message>
    <message>
        <source>Startup Condition</source>
        <translation>Au Démarrage</translation>
    </message>
    <message>
        <source>Automatically open last file used</source>
        <translation>Ouvrir automatiquement le dernier fichier utilisé</translation>
    </message>
    <message>
        <source>Show children in right-hand view</source>
        <translation>Afficher les fils dans la vue de droite</translation>
    </message>
    <message>
        <source>Restore view states of recent files</source>
        <translation>Restaurer les états des volets des fichiers récents</translation>
    </message>
    <message>
        <source>Restore window geometry from last exit</source>
        <translation>Restaurer la géométrie de la fenêtre à partir de la dernière utilisation</translation>
    </message>
    <message>
        <source>Features Available</source>
        <translation>Fonctionnalités disponibles</translation>
    </message>
    <message>
        <source>Click item to rename</source>
        <translation>Clicker sur l&apos;article pour le renommer</translation>
    </message>
    <message>
        <source>Tree drag &amp;&amp; drop available</source>
        <translation>Glisser &amp;&amp; déposer l&apos;arborescence disponible dans le volet d&apos;exploration</translation>
    </message>
    <message>
        <source>Insert node with enter</source>
        <translation>Insertion d&apos;un noeud avec la touche &quot;entrer&quot;</translation>
    </message>
    <message>
        <source>Rename new nodes when created</source>
        <translation>Renommer les nouveaux noeuds quand ils sont créés</translation>
    </message>
    <message>
        <source>Automatically open search nodes</source>
        <translation>Ouvrir automatiquement les noeuds trouvés</translation>
    </message>
    <message>
        <source>Show icons in the tree view</source>
        <translation>Afficher les icônes dans le volet d&apos;exploration</translation>
    </message>
    <message>
        <source>Enable executable links</source>
        <translation>Autoriser les liens exécutables</translation>
    </message>
    <message>
        <source>New Objects</source>
        <translation>Nouveaux objets</translation>
    </message>
    <message>
        <source>Set new files to compressed by default</source>
        <translation>Configurer les nouveaux fichiers comme compressés par défaut</translation>
    </message>
    <message>
        <source>Set new files to encrypted by default</source>
        <translation>Configurer les nouveaux fichiers comme encryptés par défaut</translation>
    </message>
    <message>
        <source>New fields default to HTML content</source>
        <translation>Nouveaux champs ont un contenu HTML par défaut</translation>
    </message>
    <message>
        <source>Undo Memory</source>
        <translation>Mémoire utilisée pour la fonctionnalité &quot;Annuler&quot;</translation>
    </message>
    <message>
        <source>Auto Save</source>
        <translation>Sauvegarde automatique</translation>
    </message>
    <message>
        <source>Data Editor Formats</source>
        <translation>Formats de l&apos;Editeur de Données</translation>
    </message>
    <message>
        <source>Dates</source>
        <translation>Dates</translation>
    </message>
    <message>
        <source>Times</source>
        <translation>Heures</translation>
    </message>
    <message>
        <source>Printing Units</source>
        <translation type="obsolete">Unités pour l&apos;impression</translation>
    </message>
    <message>
        <source>Inches</source>
        <translation type="obsolete">Inches</translation>
    </message>
    <message>
        <source>Centimeters</source>
        <translation type="obsolete">Centimètres</translation>
    </message>
    <message>
        <source>Appearance</source>
        <translation>Apparence</translation>
    </message>
    <message>
        <source>Default max data editor lines</source>
        <translation>Nombre de lignes de l&apos;éditeur de données par défaut</translation>
    </message>
    <message>
        <source>Set Tree Font</source>
        <translation>Configurer la Police du volet d&apos;exploration</translation>
    </message>
    <message>
        <source>Set Data Output Font</source>
        <translation>Configurer la Police du volet Données</translation>
    </message>
    <message>
        <source>Set Editor Font</source>
        <translation>Configurer la Police de l&apos;éditeur de données</translation>
    </message>
    <message>
        <source>File Options</source>
        <translation>Options de fichier</translation>
    </message>
    <message>
        <source>Output Formating</source>
        <translation>Format de sortie</translation>
    </message>
    <message>
        <source>Add blank lines between nodes</source>
        <translation>Ajouter des lignes vides entre les noeuds</translation>
    </message>
    <message>
        <source>Add line breaks after each line</source>
        <translation>Ajouter des retours chariots après chaque ligne</translation>
    </message>
    <message>
        <source>Allow HTML rich text in formats</source>
        <translation>Autoriser HTML dans les formats</translation>
    </message>
    <message>
        <source>File Storage</source>
        <translation>Fichier</translation>
    </message>
    <message>
        <source>Use file compression</source>
        <translation>Utiliser la compression de fichiers</translation>
    </message>
    <message>
        <source>Use file encryption</source>
        <translation>Utiliser l&apos;encryptage de fichiers</translation>
    </message>
    <message>
        <source>Embedded Child Fields</source>
        <translation>Champs du Fils Inclus</translation>
    </message>
    <message>
        <source>Separator String</source>
        <translation>Chaîne de caractères séparateur</translation>
    </message>
    <message>
        <source>Read Me file not found</source>
        <translation>Fichier LisezMoi non trouvé</translation>
    </message>
    <message>
        <source>TreeLine README File</source>
        <translation>Fichier TreeLine LISEZMOI</translation>
    </message>
    <message>
        <source>TreeLine, Version %(ver)s
 by %(author)s</source>
        <translation>TreeLIne, Version %(ver)s
par %(author)s</translation>
    </message>
    <message>
        <source>Save changes?</source>
        <translation type="obsolete">Enregistrer les changements?</translation>
    </message>
    <message>
        <source>Save changes to &quot;%s&quot;?</source>
        <translation type="obsolete">Enregistrer les changements dans &quot;%s&quot;?</translation>
    </message>
    <message>
        <source>&amp;File</source>
        <translation>&amp;Fichier</translation>
    </message>
    <message>
        <source>New File</source>
        <translation>Nouveau Fichier</translation>
    </message>
    <message>
        <source>Start a new file</source>
        <translation>Commencer un nouveau fichier</translation>
    </message>
    <message>
        <source>Open File</source>
        <translation>Ouvrir Fichier</translation>
    </message>
    <message>
        <source>&amp;Open...</source>
        <translation>&amp;Ouvir...</translation>
    </message>
    <message>
        <source>Open a file from disk</source>
        <translation>Ouvrir un ficier à partir du disque</translation>
    </message>
    <message>
        <source>Save File</source>
        <translation>Enregistrer Fichier</translation>
    </message>
    <message>
        <source>&amp;Save</source>
        <translation>&amp;Enregistrer</translation>
    </message>
    <message>
        <source>Save changes to the current file</source>
        <translation>Enregistrer les changements dans le fichier courant</translation>
    </message>
    <message>
        <source>Save &amp;As...</source>
        <translation>Enregistrer &amp;Sous...</translation>
    </message>
    <message>
        <source>Save the file with a new name</source>
        <translation>Enregistrer le fichier sous un nouveau nom</translation>
    </message>
    <message>
        <source>&amp;Export...</source>
        <translation>&amp;Exporter...</translation>
    </message>
    <message>
        <source>Export the file as html, as a table or as text</source>
        <translation>Exporter le fichier en tant que html, tableau ou texte</translation>
    </message>
    <message>
        <source>&amp;Print...</source>
        <translation>&amp;Imprimer....</translation>
    </message>
    <message>
        <source>Print starting at the selected node</source>
        <translation>Imprimer en commençant au noeud sélectionné</translation>
    </message>
    <message>
        <source>P&amp;rint Options...</source>
        <translation>Options I&amp;mpression...</translation>
    </message>
    <message>
        <source>&amp;Quit</source>
        <translation>&amp;Quitter</translation>
    </message>
    <message>
        <source>Exit the application</source>
        <translation>Quitter l&apos;application</translation>
    </message>
    <message>
        <source>&amp;Edit</source>
        <translation>&amp;Editer</translation>
    </message>
    <message>
        <source>&amp;Undo</source>
        <translation>&amp;Annuler</translation>
    </message>
    <message>
        <source>Undo the previous action</source>
        <translation>Annuler l&apos;action précédente</translation>
    </message>
    <message>
        <source>&amp;Redo</source>
        <translation>&amp;Rétablir</translation>
    </message>
    <message>
        <source>Redo the previous undo</source>
        <translation>Rétablir l&apos;annulation précédente</translation>
    </message>
    <message>
        <source>Cu&amp;t</source>
        <translation>Co&amp;uper</translation>
    </message>
    <message>
        <source>Cut the branch or text to the clipboard</source>
        <translation>Couper la branche ou le texte dans le presse-papier</translation>
    </message>
    <message>
        <source>&amp;Copy</source>
        <translation>&amp;Copier</translation>
    </message>
    <message>
        <source>Copy the branch or text to the clipboard</source>
        <translation>Copier la branche ou le texte dans le presse-papier</translation>
    </message>
    <message>
        <source>Cop&amp;y Title Text</source>
        <translation>Cop&amp;ier Texte du Volet Titres</translation>
    </message>
    <message>
        <source>Copy node title text to the clipboard</source>
        <translation>Copier le titre du noeud dans le presse-papier</translation>
    </message>
    <message>
        <source>&amp;Paste</source>
        <translation>C&amp;oller</translation>
    </message>
    <message>
        <source>Paste nodes or text from the clipboard</source>
        <translation>Coller les noeuds ou le texte dans le presse-papier</translation>
    </message>
    <message>
        <source>Paste text from the clipboard</source>
        <translation>Copier le texte à partir du presse-papier</translation>
    </message>
    <message>
        <source>Re&amp;name</source>
        <translation>Re&amp;nommer</translation>
    </message>
    <message>
        <source>Rename the current tree entry</source>
        <translation>Renommer l&apos;entrée courante du volet d&apos;exploration</translation>
    </message>
    <message>
        <source>Insert Sibling &amp;Before</source>
        <translation>Insérer Frère A&amp;vant</translation>
    </message>
    <message>
        <source>Insert new sibling before selection</source>
        <translation>Insérer le nouveau frère avant la sélection</translation>
    </message>
    <message>
        <source>Insert Sibling &amp;After</source>
        <translation>Insérer Frère Apr&amp;ès</translation>
    </message>
    <message>
        <source>Insert new sibling after selection</source>
        <translation>Insérer le nouveau frère après la sélection</translation>
    </message>
    <message>
        <source>Add C&amp;hild</source>
        <translation>Ajouter &amp;Fils</translation>
    </message>
    <message>
        <source>Add a new child to the selected parent</source>
        <translation>Ajouter un nouveau fils au parent sélectionné</translation>
    </message>
    <message>
        <source>&amp;Delete Node</source>
        <translation>&amp;Supprimer Noeud</translation>
    </message>
    <message>
        <source>Delete the selected nodes</source>
        <translation>Supprimer les noeuds sélectionnés</translation>
    </message>
    <message>
        <source>&amp;Indent Node</source>
        <translation>Inden&amp;ter Noeud</translation>
    </message>
    <message>
        <source>Indent the selected nodes</source>
        <translation>Indenter les noeuds sélectionnés</translation>
    </message>
    <message>
        <source>Unind&amp;ent Node</source>
        <translation>DésInd&amp;enter Noeud</translation>
    </message>
    <message>
        <source>Unindent the selected nodes</source>
        <translation>Désindenter les noeuds sélectionnés</translation>
    </message>
    <message>
        <source>&amp;Move Up</source>
        <translation>&amp;Déplacer En &amp;haut</translation>
    </message>
    <message>
        <source>Move the selected nodes up</source>
        <translation>Déplacer les noeuds sélectionnés vers le haut</translation>
    </message>
    <message>
        <source>M&amp;ove Down</source>
        <translation>D&amp;éplacer En bas</translation>
    </message>
    <message>
        <source>Move the selected nodes down</source>
        <translation>Déplacer les noeuds sélectionnés vers le bas</translation>
    </message>
    <message>
        <source>&amp;View</source>
        <translation>&amp;Affichage</translation>
    </message>
    <message>
        <source>Show data output in right view</source>
        <translation>Afficher le volet de données dans la vue de droite</translation>
    </message>
    <message>
        <source>Show Data &amp;Editor</source>
        <translation>Afficher l&apos;&amp;Editeur de Données</translation>
    </message>
    <message>
        <source>Show data editor in right view</source>
        <translation>Afficher l&apos;éditeur de données dans la vue de droite</translation>
    </message>
    <message>
        <source>Show Title &amp;List</source>
        <translation>Afficher &amp;Liste des Titres</translation>
    </message>
    <message>
        <source>Show title list in right view</source>
        <translation>Afficher la liste des titres dans la vue de droite</translation>
    </message>
    <message>
        <source>&amp;Data</source>
        <translation>&amp;Données</translation>
    </message>
    <message>
        <source>&amp;Set Descendant Types...</source>
        <translation>&amp;Configurer le Type des Descendants...</translation>
    </message>
    <message>
        <source>Set data type of selections and children</source>
        <translation>Configurer le type de données des sélections et des fils</translation>
    </message>
    <message>
        <source>&amp;Configure Data Types...</source>
        <translation>&amp;Paramètres du Type de Données...</translation>
    </message>
    <message>
        <source>C&amp;opy Types from File...</source>
        <translation>C&amp;opier Types à partir du Fichier...</translation>
    </message>
    <message>
        <source>Copy the configuration from another TreeLine file</source>
        <translation>Copier la configuration à partir d&apos;un autre fichier TreeLine</translation>
    </message>
    <message>
        <source>Edit data values for all selected nodes</source>
        <translation>Editer les valeurs des données pour tous les noeuds sélectionnés</translation>
    </message>
    <message>
        <source>N&amp;umbering...</source>
        <translation>N&amp;umérotation des Données...</translation>
    </message>
    <message>
        <source>Add numbering to a given data field</source>
        <translation>Ajouter la numérotation à un champ de données donné</translation>
    </message>
    <message>
        <source>Insert category nodes above children</source>
        <translation>Insérer les noeuds du classement au-dessus des fils</translation>
    </message>
    <message>
        <source>&amp;Flatten by Category</source>
        <translation>Ap&amp;latir par Classement</translation>
    </message>
    <message>
        <source>Collapse data by merging fields</source>
        <translation>Réduire les données en fusionnant les champs</translation>
    </message>
    <message>
        <source>Arrange by &amp;Reference...</source>
        <translation>Organiser par &amp;Référence...</translation>
    </message>
    <message>
        <source>Arrange data using parent references</source>
        <translation>Organiser les données en utilisant les références</translation>
    </message>
    <message>
        <source>F&amp;latten by Reference...</source>
        <translation>Aplat&amp;ir par Référence...</translation>
    </message>
    <message>
        <source>Collapse data after adding references</source>
        <translation>Réduire les données après avoir ajouté les références</translation>
    </message>
    <message>
        <source>&amp;Tools</source>
        <translation>&amp;Outils</translation>
    </message>
    <message>
        <source>&amp;Expand Full Branch</source>
        <translation>&amp;Développer Toute la Branche</translation>
    </message>
    <message>
        <source>Expand all children of selected node</source>
        <translation>Développer tous les fils du noeud sélectionné</translation>
    </message>
    <message>
        <source>&amp;Collapse Full Branch</source>
        <translation>&amp;Réduire Toute la Branche</translation>
    </message>
    <message>
        <source>Collapse all children of the selected node</source>
        <translation>Réduire tous les fils du noeud sélectionné</translation>
    </message>
    <message>
        <source>&amp;Find...</source>
        <translation>&amp;Chercher...</translation>
    </message>
    <message>
        <source>Find node matching text string</source>
        <translation>Chercher un noeud correspondant à la chaîne de caractères</translation>
    </message>
    <message>
        <source>&amp;Spell Check</source>
        <translation>&amp;Vérification orthographique</translation>
    </message>
    <message>
        <source>Spell check the tree&apos;s text data</source>
        <translation>Vérifier l&apos;orthographe du texte du tree</translation>
    </message>
    <message>
        <source>&amp;Remove XSLT Ref</source>
        <translation>&amp;Supprimer Ref XSLT</translation>
    </message>
    <message>
        <source>Delete reference to XSLT export</source>
        <translation>Supprimer la référence à l&apos;export XSLT</translation>
    </message>
    <message>
        <source>&amp;General Options...</source>
        <translation>&amp;Options Générales...</translation>
    </message>
    <message>
        <source>Set user preferences for all files</source>
        <translation>Configurer les préférences utilisateur pour tous les fichiers</translation>
    </message>
    <message>
        <source>File &amp;Options...</source>
        <translation>Options &amp;Fichier...</translation>
    </message>
    <message>
        <source>Set preferences for this file</source>
        <translation>Configurer les préférences pour ce fichier</translation>
    </message>
    <message>
        <source>&amp;Background Color...</source>
        <translation>Couleur &amp;Arrière-plan...</translation>
    </message>
    <message>
        <source>Set view background color</source>
        <translation>Configurer la couleur d&apos;arrière plan</translation>
    </message>
    <message>
        <source>&amp;Text Color...</source>
        <translation>Couleur &amp;Texte...</translation>
    </message>
    <message>
        <source>Set view text color</source>
        <translation>Configurer la couleur du texte</translation>
    </message>
    <message>
        <source>&amp;Help</source>
        <translation>A&amp;ide</translation>
    </message>
    <message>
        <source>&amp;About TreeLine</source>
        <translation>A propos de &amp;TreeLine</translation>
    </message>
    <message>
        <source>About this program</source>
        <translation>A propos de ce programme</translation>
    </message>
    <message>
        <source>About &amp;Plugins</source>
        <translation>A propos des &amp;Plugins</translation>
    </message>
    <message>
        <source>Show loaded plugin modules</source>
        <translation>Afficher les modules plugin chargés</translation>
    </message>
    <message>
        <source>Number of undo levels</source>
        <translation>Nombre de niveaux d&apos;annulation</translation>
    </message>
    <message>
        <source>Minutes between saves</source>
        <translation type="obsolete">Temps en minutes entre sauvegardes</translation>
    </message>
    <message>
        <source>Recent Files</source>
        <translation>Fichiers récents</translation>
    </message>
    <message>
        <source>Number of recent files</source>
        <translation type="obsolete">Nombre de fichiers récents</translation>
    </message>
    <message>
        <source>in the File menu</source>
        <translation type="obsolete">dans le menu Fichier</translation>
    </message>
    <message>
        <source>Sample directory not found</source>
        <translation>Répertoire fichiers examples non trouvés</translation>
    </message>
    <message>
        <source>Open Sample Template File</source>
        <translation>Ouvrir Fichier Example</translation>
    </message>
    <message>
        <source>Spell Check Language</source>
        <translation>Langage de Vérification Orthographique</translation>
    </message>
    <message>
        <source>2-letter code (blank</source>
        <translation>code à 2 lettres</translation>
    </message>
    <message>
        <source>for system default)</source>
        <translation>pour le système par défaut)</translation>
    </message>
    <message>
        <source>Open Sa&amp;mple...</source>
        <translation>Ouvrir Exa&amp;mple...</translation>
    </message>
    <message>
        <source>Open a sample template file</source>
        <translation>Ouvrir un Fichier Example</translation>
    </message>
    <message>
        <source>&amp;Help Contents</source>
        <translation>&amp;Aide Contenu</translation>
    </message>
    <message>
        <source>View information about using TreeLine</source>
        <translation>Lire l&apos;information sur l&apos;utilisation de TreeLine</translation>
    </message>
    <message>
        <source>&amp;View Full ReadMe</source>
        <translation>&amp;Lire l&apos;Aide Complèt</translation>
    </message>
    <message>
        <source>View the entire ReadMe file</source>
        <translation>Lire l&apos;Aide Complète</translation>
    </message>
    <message>
        <source>ODF Text Files</source>
        <translation>Fichier Texte ODF</translation>
    </message>
    <message>
        <source>&amp;Bold</source>
        <translation>&amp;Gras</translation>
    </message>
    <message>
        <source>&amp;Italics</source>
        <translation>&amp;Italiques</translation>
    </message>
    <message>
        <source>&amp;Underline</source>
        <translation>&amp;Souligné</translation>
    </message>
    <message>
        <source>&amp;Size...</source>
        <translation>&amp;Taille...</translation>
    </message>
    <message>
        <source>&amp;Color...</source>
        <translation>&amp;Couleur...</translation>
    </message>
    <message>
        <source>Tree View</source>
        <translation>Vue de l&apos;arbre</translation>
    </message>
    <message>
        <source>Flat View</source>
        <translation>Vue à plat</translation>
    </message>
    <message>
        <source>Data Output</source>
        <translation>Sortie des données</translation>
    </message>
    <message>
        <source>Data Editor</source>
        <translation>Édition des données</translation>
    </message>
    <message>
        <source>Title List</source>
        <translation>Liste des titres</translation>
    </message>
    <message>
        <source>Conditional Filter</source>
        <translation>Filtre conditionnel</translation>
    </message>
    <message>
        <source>Text Filter</source>
        <translation>Filtre de texte</translation>
    </message>
    <message>
        <source>and</source>
        <translation>et</translation>
    </message>
    <message>
        <source>Open Document (ODF) text</source>
        <translation type="obsolete">Ouvrir le document texte (ODF)</translation>
    </message>
    <message>
        <source>Error - could not read template file &quot;%s&quot;</source>
        <translation type="obsolete">Erreur − fichier modèle &quot;%s&quot; illisible</translation>
    </message>
    <message>
        <source>Nothing to export</source>
        <translation>Rien à exporter</translation>
    </message>
    <message>
        <source>Export ODF Text</source>
        <translation>Exporter un texte ODF</translation>
    </message>
    <message>
        <source>Filter %s Data Type</source>
        <translation>Filtre type de données %s</translation>
    </message>
    <message>
        <source>Enter key words</source>
        <translation>Entrer les mots clés</translation>
    </message>
    <message>
        <source>No common fields with parent references</source>
        <translation>Pas de champs communs avec les références des parents</translation>
    </message>
    <message>
        <source>Spell Check Error</source>
        <translation>Erreur Correction Orthographe</translation>
    </message>
    <message>
        <source>Show descendants in output view</source>
        <translation>Montrer descendants dans l&apos;aperçu sortie</translation>
    </message>
    <message>
        <source>Multiple Selection Sequence</source>
        <translation>Séquence de sélection multiple</translation>
    </message>
    <message>
        <source>Tree order</source>
        <translation>Ordre de l&apos;arbre</translation>
    </message>
    <message>
        <source>Selection order</source>
        <translation>Ordre de sélection</translation>
    </message>
    <message>
        <source>Data Editor Pages</source>
        <translation>Données Éditeur de pages</translation>
    </message>
    <message>
        <source>Number of pages shown</source>
        <translation type="obsolete">Nombre de pages montrées</translation>
    </message>
    <message>
        <source>set to 0 for all</source>
        <translation type="obsolete">Mettre un 0 pour toutes</translation>
    </message>
    <message>
        <source>set to 0 to disable</source>
        <translation type="obsolete">Mettre un 0 pour mettre hors fonction</translation>
    </message>
    <message>
        <source>Font Size</source>
        <translation>Taille de la Police</translation>
    </message>
    <message>
        <source>Enter size factor (-6 to +6)</source>
        <translation>Entrer un facteur pour la taille (-6 à +6)</translation>
    </message>
    <message>
        <source>Set &amp;Item Type</source>
        <translation>Fixer le type de l&apos;&amp;article</translation>
    </message>
    <message>
        <source>Toolbar %d</source>
        <translation>Barre d&apos;outils%d</translation>
    </message>
    <message>
        <source>&amp;New...</source>
        <translation>&amp;Nouveau…</translation>
    </message>
    <message>
        <source>Set margins, page size and other options for printing</source>
        <translation>Fixer les marges, la taille de la page et d&apos;autres options d&apos;impression</translation>
    </message>
    <message>
        <source>Print Pre&amp;view...</source>
        <translation>Aperçu a&amp;vant impression…</translation>
    </message>
    <message>
        <source>Show a preview of printing results</source>
        <translation>Montrer l&apos;aperçu de l&apos;impression</translation>
    </message>
    <message>
        <source>Pa&amp;ste Text</source>
        <translation>Co&amp;ller du texte</translation>
    </message>
    <message>
        <source>Move &amp;First</source>
        <translation>Déplacer &amp;premier</translation>
    </message>
    <message>
        <source>Move the selected nodes to be the first children</source>
        <translation>Déplacer les nœuds sélectionnés comme premier enfant</translation>
    </message>
    <message>
        <source>Move &amp;Last</source>
        <translation>Déplacer &amp;dernier</translation>
    </message>
    <message>
        <source>Move the selected nodes to be the last children</source>
        <translation>Déplacer les nœuds sélectionnés comme dernier enfant</translation>
    </message>
    <message>
        <source>&amp;Previous Selection</source>
        <translation>Sélection &amp;Précédente</translation>
    </message>
    <message>
        <source>View the previous tree selection</source>
        <translation>Voir la sélection précédente de l&apos;arbre</translation>
    </message>
    <message>
        <source>&amp;Next Selection</source>
        <translation>&amp;Sélection suivante</translation>
    </message>
    <message>
        <source>View the next tree selection</source>
        <translation>Voir la sélection suivante de l&apos;arbre</translation>
    </message>
    <message>
        <source>Show &amp;Tree View</source>
        <translation>Montrer une vue de &amp;l&apos;arbre</translation>
    </message>
    <message>
        <source>Show the tree in the right view</source>
        <translation>Montrer l&apos;arbre dans la vue de droite</translation>
    </message>
    <message>
        <source>Show &amp;Flat View</source>
        <translation>Montrer une vue à &amp;plat</translation>
    </message>
    <message>
        <source>Show a flat list in the right view</source>
        <translation>Montrer une liste à plat dans la vue de droite</translation>
    </message>
    <message>
        <source>Show Data &amp;Output</source>
        <translation>Montrer une &amp;sortie des données</translation>
    </message>
    <message>
        <source>Show &amp;Child Pane</source>
        <translation>Montrer le panneau des &amp;enfants</translation>
    </message>
    <message>
        <source>Toggle splitting right-hand view to show children</source>
        <translation>Bascule de la vue sur la droite pour montrer les enfants</translation>
    </message>
    <message>
        <source>Show Output &amp;Descendants</source>
        <translation>Montrer la sortie pour les &amp;Descendants</translation>
    </message>
    <message>
        <source>Toggle showing descendants in output view</source>
        <translation>Bascule pour montrer les descendants dans la vue des sorties</translation>
    </message>
    <message>
        <source>Modify data types, fields &amp; output lines</source>
        <translation>Modifier les types de données, les champs &amp; les lignes en sortie</translation>
    </message>
    <message>
        <source>Sort &amp;Nodes...</source>
        <translation>Trier les &amp;Nœuds…</translation>
    </message>
    <message>
        <source>Open the dialog for sorting nodes</source>
        <translation>Ouvrir le dialogue pour le tri des nœuds</translation>
    </message>
    <message>
        <source>Con&amp;ditional Filter...</source>
        <translation>Filtre con&amp;ditionnel…</translation>
    </message>
    <message>
        <source>Filter types with conditional rules</source>
        <translation>Filtrer les types avec des règles conditionnelles</translation>
    </message>
    <message>
        <source>Te&amp;xt Filter...</source>
        <translation>Filtre de te&amp;xte…</translation>
    </message>
    <message>
        <source>Filter with a text search string</source>
        <translation>Filtrer avec une chaîne texte pour recherche</translation>
    </message>
    <message>
        <source>Cl&amp;ear Filtering</source>
        <translation>Purg&amp;er le système de filtrage</translation>
    </message>
    <message>
        <source>Clear current filtering</source>
        <translation>Purger le filtrage actuel</translation>
    </message>
    <message>
        <source>Set Fo&amp;nts</source>
        <translation>Fixer les po&amp;lices</translation>
    </message>
    <message>
        <source>&amp;Tree Font...</source>
        <translation>Police pour l&apos;&amp;arbre…</translation>
    </message>
    <message>
        <source>Sets font for tree &amp; flat views</source>
        <translation>Fixe la police pour les vues en arbre &amp; à plat</translation>
    </message>
    <message>
        <source>&amp;Data Output Font...</source>
        <translation>&amp;Donnée des police en sortie…</translation>
    </message>
    <message>
        <source>Sets font for output views</source>
        <translation>Fixe la police pour les vues en sortie</translation>
    </message>
    <message>
        <source>&amp;Editor Font...</source>
        <translation>Police de l&apos;&amp;Editeur…</translation>
    </message>
    <message>
        <source>Sets font for edit views</source>
        <translation>Fixe les polices pour les vues de l&apos;éditeur</translation>
    </message>
    <message>
        <source>Set &amp;Keyboard Shortcuts...</source>
        <translation>Fixe les raccourcis &amp;claviers...</translation>
    </message>
    <message>
        <source>Customize keyboard commands</source>
        <translation>Personnalise les commandes au clavier</translation>
    </message>
    <message>
        <source>Custo&amp;mize Toolbars...</source>
        <translation>Perso&amp;nnalise les barres d&apos;outils…</translation>
    </message>
    <message>
        <source>Customize toolbar buttons</source>
        <translation>Personnalise les boutons des barres d&apos;outils</translation>
    </message>
    <message>
        <source>&amp;Use Default System Colors</source>
        <translation>&amp;Utilise les couleurs par défaut du système</translation>
    </message>
    <message>
        <source>Use system colors, not custom</source>
        <translation>Utilise les couleurs du système, non personnalisé</translation>
    </message>
    <message>
        <source>&amp;Add Font Tags</source>
        <translation>&amp;Ajouter Balises de Police</translation>
    </message>
    <message>
        <source>&amp;Add Category Level...</source>
        <translation>&amp;Ajouter un niveau de catégorisation... </translation>
    </message>
    <message>
        <source>Show status bar</source>
        <translation>Montrer la barre de statut</translation>
    </message>
    <message>
        <source>Open files in new windows</source>
        <translation>Ouverture des fichiers dans de nouvelles fenetres</translation>
    </message>
    <message>
        <source>Click on tree node for link destination</source>
        <translation>Cliquer sur le noeud de l&apos;arbre pour le lien de destination </translation>
    </message>
    <message>
        <source>Show Status Bar</source>
        <translation>Montrer la barre de statut</translation>
    </message>
    <message>
        <source>Toggle the display of the status bar</source>
        <translation>Basculer l&apos;affichage de la barre de statut</translation>
    </message>
    <message>
        <source>&amp;Window</source>
        <translation>&amp;Fenetre</translation>
    </message>
    <message>
        <source>&amp;New Window</source>
        <translation>j&amp;Nouvelle Fenetre</translation>
    </message>
    <message>
        <source>Open a new window viewing the same file</source>
        <translation>Ouverture d&apos;une nouvelle fenetre pour l&apos;affichage d&apos;un ficher identique</translation>
    </message>
    <message>
        <source>&amp;Close Window</source>
        <translation>&amp;Fermer la fenetre</translation>
    </message>
    <message>
        <source>Close the current window</source>
        <translation>Fermer la fenetre actuelle</translation>
    </message>
    <message>
        <source>&amp;Update Other Window</source>
        <translation>&amp;Mise à jour de l&apos;autre fenetre</translation>
    </message>
    <message>
        <source>Update the contents of an alternate window</source>
        <translation>Mise à jour du contenut de la fenetre alternative</translation>
    </message>
    <message>
        <source>C&amp;hange Selected Data...</source>
        <translation>C&amp;anger les données selectionnées...</translation>
    </message>
    <message>
        <source>Number of pages shown 
(set to 0 for all)</source>
        <translation>Nombre de pages affichées</translation>
    </message>
    <message>
        <source>Minutes between saves 
(set to 0 to disable)</source>
        <translation>Minutes entres les sauvegardes </translation>
    </message>
    <message>
        <source>Number of recent files 
in the File menu</source>
        <translation>Nombre de fichier récent dans le menu Fichier</translation>
    </message>
</context>
<context>
    <name>treerightviews</name>
    <message>
        <source>Executable links are not enabled</source>
        <translation>Les liens exécutables ne sont pas activés</translation>
    </message>
</context>
<context>
    <name>treeview</name>
    <message>
        <source>Search for:</source>
        <translation>Chercher:</translation>
    </message>
    <message>
        <source>Search for: %s</source>
        <translation>Chercher: %s</translation>
    </message>
    <message>
        <source>Search for: %s  (not found)</source>
        <translation>Chercher: %  (non trouvé)</translation>
    </message>
    <message>
        <source>Next:  %s</source>
        <translation>Suivant:  %s</translation>
    </message>
    <message>
        <source>Next:  %s  (not found)</source>
        <translation>Suivant:  %s  (non trouvé)</translation>
    </message>
    <message>
        <source>Previous:  %s</source>
        <translation>Précédent:  %s</translation>
    </message>
    <message>
        <source>Previous:  %s  (not found)</source>
        <translation>Précédent:  %s  (non trouvé)</translation>
    </message>
</context>
<context>
    <name>treexmlparse</name>
    <message>
        <source>Element_Data</source>
        <comment>xml field name</comment>
        <translation>Element_Data</translation>
    </message>
    <message>
        <source>Bookmarks</source>
        <translation>Favoris</translation>
    </message>
</context>
</TS>
