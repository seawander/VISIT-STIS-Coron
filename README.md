# VISIT-STIS-Coron
VISIbility Tool for HST/STIS Coronagraph (VISIT-STIS-Coron), version 0.1. Developed by Bin Ren (Caltech) as a Phase II preparation tool for HST/STIS coronagraph. [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7404928.svg)](https://doi.org/10.5281/zenodo.7404928)



**TLDR**: Check out [VISIT-STIS-Coron Demo.ipynb](https://github.com/seawander/VISIT-STIS-Coron/blob/main/VISIT-STIS-Coron%20Demo.ipynb) for usage demo.

Some advantages of VISIT-STIS-Coron:
1. This tool uses a physical mask created by John H. Debes (STScI) in Debes et al. ([2017](https://ui.adsabs.harvard.edu/abs/2017ApJ...835..205D/abstract)).
2. The coronagraphic occulting locations (`BAR5`, `BAR10`, `WEDGEA0.6`, `WEDGEA1.0`, `WEDGEA1.8`, `WEDGEA2.0`, `WEDGEA2.5`, `WEDGEA2.8`, `WEDGEB1.0`, `WEDGEB1.8`, `WEDGEB2.0`, `WEDGEB2.5`, `WEDGEB2.8`), as well as `POSTARG` parameters, are supported. See [STIS_coron_positions.pdf](https://github.com/seawander/VISIT-STIS-Coron/blob/main/STIS_coron_positions.pdf) for their actual locations.
3. **Most accurate** occluting locations and diffration spikes. The occulting locations are measured by Bin Ren (Caltech) previously presented in Ren et al. ([2017](https://ui.adsabs.harvard.edu/abs/2017SPIE10400E..21R/abstract)). The diffraction spikes are also measured to be 10-pixel wide.
4. **Support** for the `ORIENT` parameter used in Phase II preparation.
5. If you position your target outside the occulting locations using `POSTARG` parameters, a warning message will be printed.

Acknowledgements:
1. I thank John H. Debes for allowing me to make the mask file he created in Debes et al. ([2017](https://ui.adsabs.harvard.edu/abs/2017ApJ...835..205D/abstract)) public. If you use that FITS file in your research, please cite  Debes et al. ([2017](https://ui.adsabs.harvard.edu/abs/2017ApJ...835..205D/abstract)).
2. I thank Kimberly Ward-Duong for developing [STIS Coronagraphic Visualization Tool (Preliminary Release)](https://www.stsci.edu/hst/instrumentation/stis/data-analysis-and-software-tools) which I used to verify the parameter setup for VISIT-STIS-Coron.

To be done:
Overall representation/choice of colormap, markers, etc.

```
@software{bin_ren_2022_7404928,
  author       = {Bin Ren},
  title        = {seawander/VISIT-STIS-Coron: First Release},
  month        = dec,
  year         = 2022,
  publisher    = {Zenodo},
  version      = {v1.0},
  doi          = {10.5281/zenodo.7404928},
  url          = {https://doi.org/10.5281/zenodo.7404928}
}
```
