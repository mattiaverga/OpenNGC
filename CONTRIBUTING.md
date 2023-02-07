# Contributing to ONGC

If you spot any error or want to contribute to OpenNGC, file a bug or open
a pull request in the [Github repository](https://github.com/mattiaverga/OpenNGC).

Don't forget to describe what is the purpose of your proposed change and the sources
of the data you're submitting. You can find the list of sources that are currently
used at the end of the `NGC_guide.txt` file.

When opening the csv file for edit, make sure to select `text` as column type for
all columns, to ensure not to change existing number formatting. Columns with number
values must be formatted as following:

- MajAx and MinAx: one leading zero and two decimals (0.00 or 1.00)
- PosAng: integer value without decimals
- Magnitudes and SurfBr: one leading zero and two decimals with negative sign ([-]0.00 or 1.00)
- Pax: one leading zero and four decimals (0.0000)
- Pm-RA and Pm-Dec: one leading zero and three decimals with negative sign ([-]0.000)
- RadVel: integer value without decimals and negative sign
- Redshift: one leading zero and six decimals with negative sign ([-]0.000000)
- Cstar magnitudes: one leading zero and two decimals with negative sign ([-]0.00 or 1.00)

