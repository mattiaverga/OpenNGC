# OpenNGC
Database oggetti NGC/IC con licenza libera

Credits: Mattia Verga
	https://github.com/mattiaverga/OpenNGC

[![DOI: 10.21938/y.1ejWUD_MQ6b_eDFoVbbw](https://img.shields.io/badge/DOI-10.21938%2Fy.1ejWUD__MQ6b__eDFoVbbw-blue.svg)](http://dc.zah.uni-heidelberg.de/voidoi/q/lp/custom/10.21938/y.1ejWUD_MQ6b_eDFoVbbw)


### PRESENTAZIONE

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

In caso di incongruenze tra i diversi cataloghi si è preferito tenere i dati dal NED.

Alcuni nomi comuni degli oggetti sono presi da sorgenti internet come Wikipedia.

#### NOTE SUI DATI

 - Tutti gli oggetti: le coordinate sono ottenute dal NED; le magnitudini sono
   ottenute da SIMBAD, se non specificato altrimenti.

 - Galassie (G | GGroup | GPair | Gtrpl): diametri, angolo di posizione, luminosità superficiale
   e classificazione sono importati da LEDA. Se i diametri non sono disponibili in LEDA allora
   sono presi da SIMBAD (solitamente riferiti alle misure 2MASS, quindi in infrarosso e non visuale;
   in questo caso è stata aggiunta una nota all'oggetto).

 - Ammassi stellari (OCl | GCl | *Ass | Cl+N): dove disponibili, i diametri e l'angolo
   di posizione sono ottenuti dalle seguenti tabelle HEASARC: mwsc [central_radius];
   smcclustrs [major_diameter, minor_diameter, position_angle];
   lmcextobj [major_axis, minor_axis, position_angle].

 - Nebulose planetarie (PN): i dati sono stati importati dalla tabella HEASARC plnebulae
   dai campi opt_diameter, umag_cstar, bmag_cstar, vmag_cstar,
   name, pk_name, iras_name, alt_name_1, alt_name_2, alt_name_3, alt_name_4.
   B_Mag e V_Mag sono importati da LEDA, mentre J, H e K da Simbad.

 - Nebulose (HII | Neb | EmN | RfN | SNR): dove disponibili, i diametri e l'angolo
   di posizione sono ottenuti dalla tabella HEASARC lbn, campi [large_dimension], [small dimension].
   Se la sorgente dei dati è diversa, allora è specificata nelle note dell'oggetto.

#### ADDEDUM

La cartella 'addendum' contiene un file di catalogo separato che lista una serie di oggetti interessanti
per gli astrofili, ma che non sono parte dei cataloghi NGC o IC.

Nota che due oggetti Messier (M40 e M45) non hanno nessuna designazione NGC o IC e perciò sono
presenti solo nell'addendum.

### INTERFACCIA PYTHON

Per accedere ai dati del database OpenNGC da Python potete usare PyOngc: https://github.com/mattiaverga/PyOngc.

### INTERFACCIA TAP

Una tabella TAP del database OpenNGC è disponibile su http://dc.g-vo.org/tap.


[![ko-fi](https://www.ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/E1E41AH8L)
<img src="http://img.shields.io/liberapay/patrons/mattia.svg?logo=liberapay">
