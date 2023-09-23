# OpenNGC
Database oggetti NGC/IC con licenza libera

Credits: Mattia Verga
	https://github.com/mattiaverga/OpenNGC

[![DOI: 10.21938/y.1ejWUD_MQ6b_eDFoVbbw](https://img.shields.io/badge/DOI-10.21938%2Fy.1ejWUD__MQ6b__eDFoVbbw-blue.svg)](http://dc.zah.uni-heidelberg.de/voidoi/q/lp/custom/10.21938/y.1ejWUD_MQ6b_eDFoVbbw)


### INTRODUZIONE

OpenNGC è un database contenente le posizioni e i principali dati degli
oggetti che compongono i cataloghi NGC (New General Catalogue) e
IC (Index Catalogue).
A differenza di altri database simili che sono rilasciati con limitazioni
di licenza, OpenNGC è rilasciato sotto la licenza CC-BY-SA-4.0, che permette
un più vasto ventaglio di campi d'impiego.

Per una legenda dei dati presenti nel database si rimanda al file
NGC_guide.txt.


### SORGENTI DATI

OpenNGC è stato compilato unendo i dati delle seguenti fonti:

 - NASA/IPAC Extragalactic Database
   http://ned.ipac.caltech.edu/
   This research has made use of the NASA/IPAC Extragalactic Database (NED)
   which is operated by the Jet Propulsion Laboratory,
   California Institute of Technology, under contract with the
   National Aeronautics and Space Administration.

 - HyperLEDA database
   http://leda.univ-lyon1.fr
   We acknowledge the usage of the HyperLeda database (http://leda.univ-lyon1.fr)

 - SIMBAD Astronomical Database
   http://simbad.u-strasbg.fr/simbad/
   This research has made use of the SIMBAD database, operated at CDS, Strasbourg, France

 - HEASARC High Energy Astrophysics Science Archive Research Center
   http://heasarc.gsfc.nasa.gov/
   Abbiamo usato diversi database da HEASARC come messier, mwsc, lbn, plnebulae, lmcextobj e smcclustrs.

 - Harold Corwin's NGC/IC Positions and Notes
   http://haroldcorwin.net/ngcic/index.html

Alcuni nomi comuni degli oggetti sono presi da sorgenti internet come Wikipedia.

#### NOTE SUI DATI

Vedi la colonna `sources` per una descrizione dettagliata sull'origine dei dati di ciascun oggetto.

 - Le coordinate sono originate da NED; alcuni oggetti multipli, come alcune galassie interagenti,
 - sono indicate secondo lo schema NED, da cui il relativo suffisso.

 - B-Mag e V-Mag hanno differenti origini: per le galassie i valori sono solitamente presi da LEDA,
   altrimenti sono presi da SIMBAD e una nota viene aggiunta all'ggetto. Le magnitudini J, H e K sono
   sempre originate da SIMBAD.

 - I dati di parallasse, moto proprio, velocità radiale e redshift sono riferiti al valore principale
   riportato da SIMBAD.

 - Galassie (G | GGroup | GPair | Gtrpl): diametri, angolo di posizione, luminosità superficiale
   e classificazione sono importati da LEDA. Se i diametri non sono disponibili in LEDA allora
   sono presi da SIMBAD (solitamente riferiti alle misure 2MASS, quindi in infrarosso e non visuale).

 - Ammassi stellari (OCl | GCl | *Ass | Cl+N): dove disponibili, i diametri e l'angolo
   di posizione sono ottenuti dalle seguenti tabelle HEASARC: mwsc [central_radius];
   smcclustrs [major_diameter, minor_diameter, position_angle];
   lmcextobj [major_axis, minor_axis, position_angle].

 - Nebulose planetarie (PN): i dati sono stati importati dalla tabella HEASARC plnebulae
   dai campi opt_diameter, umag_cstar, bmag_cstar, vmag_cstar,
   name, pk_name, iras_name, alt_name_1, alt_name_2, alt_name_3, alt_name_4.

 - Nebulose (HII | Neb | EmN | RfN | SNR): dove disponibili, i diametri e l'angolo
   di posizione sono ottenuti dalla tabella HEASARC lbn, campi [large_dimension], [small dimension].

### ADDEDUM

Il file 'addendum.csv' contiene un file di catalogo separato che lista una serie di oggetti interessanti
per gli astrofili, ma che non sono parte dei cataloghi NGC o IC.

Nota che due oggetti Messier (M40 e M45) non hanno nessuna designazione NGC o IC e perciò sono
presenti solo nell'addendum.

### LINEE DELLE NEBULOSE

Nella cartella `outlines` sono forniti file di dati che descrivono i contorni delle maggiori nebulosità.
Maggiori informazioni su come sono stati ottenuti questi dati sono fornite nel file `metodology.txt`
(in inglese). Un semplice script Python `shape.py` consente di trasformare i dati grezzi nella
sottocartella `objects` in cataloghi compatibili con diversi programmi astronomici. Attualmente
è possibile generare cataloghi adatti a essere importati in Skychart e Stellarium.

### INTERFACCIA PYTHON

Per accedere ai dati del database OpenNGC da Python potete usare PyOngc: https://github.com/mattiaverga/PyOngc.

### INTERFACCIA TAP

Una tabella TAP del database OpenNGC è disponibile su http://dc.g-vo.org/tap.
