# OpenNGC
A license friendly NGC/IC objects database

Credits: Mattia Verga
	https://github.com/mattiaverga/OpenNGC

[![DOI: 10.21938/y.1ejWUD_MQ6b_eDFoVbbw](https://img.shields.io/badge/DOI-10.21938%2Fy.1ejWUD__MQ6b__eDFoVbbw-blue.svg)](http://dc.zah.uni-heidelberg.de/voidoi/q/lp/custom/10.21938/y.1ejWUD_MQ6b_eDFoVbbw)


### INTRODUCTION

OpenNGC is a database containing positions and main data of
NGC (New General Catalogue) and IC (Index Catalogue) objects.
Unlike other similar databases which are released with
license limitations, OpenNGC is released under CC-BY-SA-4.0 license,
which allows the use for a wider range of cases.

For information about data fields contained in the database, please see
the file NGC_guide.txt.


### DATA SOURCES

OpenNGC has been built by merging data from:

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
   We used several databases from HEASARC such as messier, mwsc, lbn, plnebulae, lmcextobj and smcclustrs.

 - Harold Corwin's NGC/IC Positions and Notes
   http://haroldcorwin.net/ngcic/index.html

Some common names are taken from internet sources like Wikipedia.

#### NOTES ON OBJECT DATA

See the `sources` column for a detailed description of where each object data has been taken from.

 - Coordinates are usually taken from NED; some multiple objects,
   like multiple galaxies, are also listed following NED schema, thus the NED suffix.

 - B-Mag and V-Mag have different sources: for galaxies they're usually originated from LEDA
   if available, otherwise are from SIMBAD. J, H and K magnitudes are always from SIMBAD.

 - Parallax, proper motions, radial velocity and redshift are referred to the main value
   reported from SIMBAD.

 - Galaxies (G | GGroup | GPair | Gtrpl): data about major axis, minor axis, position angle,
   surface brightness and Hubble classification is taken from LEDA; if major axis or minor axis data
   is not available from LEDA, then it's taken from SIMBAD (usually from 2MASS measures,
   so they're referred to IR, not visual).

 - Star clusters (OCl | GCl | *Ass | Cl+N): where available, diameters and
   position angle are taken from the following HEASARC tables: mwsc [central_radius];
   smcclustrs [major_diameter, minor_diameter, position_angle];
   lmcextobj [major_axis, minor_axis, position_angle].

 - Planetary Nebulae (PN): data is imported from HEASARC plnebulae table,
   fields used are opt_diameter, umag_cstar, bmag_cstar, vmag_cstar,
   name, pk_name, iras_name, alt_name_1, alt_name_2, alt_name_3, alt_name_4.

 - Nebulae (HII | Neb | EmN | RfN | SNR): where available, major and minor axis are taken
   from HEASARC lbn table [large_dimension], [small dimension].

### THE ADDENDUM

The `addendum.csv` file contains a separate catalog file with notably objects that are not
part of the NGC or IC catalog. These objects may be of some interest to amateur astronomers.

Note that two Messier objects (M40 and M45) haven't got any NGC or IC designation, so  they're
listed only in the addendum.

### NEBULAE OUTLINES

In the `outlines` directory outlines for the most prominent nebulae are provided. You can find more
information about this data in the `metodology.txt` file. A simple Python script `shape.py` provides
an interface to build a catalog file from the raw data in the `objects` subdirectory. Currently
the script supports creating catalogs for Skychart and Stellarium.

### PYTHON INTERFACE

For a basic Python interface to OpenNGC data, see PyOngc project at https://github.com/mattiaverga/PyOngc.

### TAP INTERFACE

A TAP-accessible database table of OpenNGC is available on http://dc.g-vo.org/tap.
