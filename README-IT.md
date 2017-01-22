# OpenNGC
Database NGC (New General Catalogue) con licenza libera

Versione 0.3

Contatto: mattia dot verga at tiscali dot it



### PRESENTAZIONE

OpenNGC è un database contenente le posizioni e i principali dati degli
oggetti che compongono il catalogo NGC (New General Catalogue).
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
   Abbiamo usato diversi database da HEASARC come mwsc, lbn, plnebulae, lmcextobj e smcclustrs.

In caso di incongruenze tra i diversi cataloghi si è preferito tenere i dati dal NED.

#### NOTE SUI DATI

 - Tutti gli oggetti: le coordinate sono ottenute dal NED; le magnitudini sono
   ottenute da SIMBAD.
   
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
   B_Mag è importato da Revised New General Catalogue (Sulentic+, 1973).
   
 - Nebulose (HII | Neb | EmN | RfN | SNR): dove disponibili, i diametri e l'angolo
   di posizione sono ottenuti dalla tabella HEASARC lbn, campi [large_dimension], [small dimension].

### STATO
Oggetti NGC sono completi.
Il prossimo passo sarà iniziare a importare i dati degli oggetti IC.
