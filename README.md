# TwinStream
Repository to share the MOHID-Land models and associated python scripts developed on behalf of the TwinStream project.

# TwinStream

### Operational Hydrological Forecasting Framework based on MOHID-Land

TwinStream repository holds a research and operational hydrological forecasting framework developed to automate the acquisition of meteorological forecasts, preparation of forcing datasets, execution of distributed hydrological models, and dissemination of forecast products using the **MOHID-Land** modelling system.

The framework was developed within the **TwinStream project,** a Digital Twin for water, to support operational hydrological forecasting across Portugal and transboundary Iberian river basins.

---

## Overview

TwinStream integrates:

* 🌦️ Automated meteorological forecast acquisition
* 🔄 Conversion and preprocessing of meteorological datasets
* 🌍 Distributed hydrological modelling with MOHID-Land
* 📈 Operational forecasting workflows

The system currently provides operational forecasts ranging from **2 to 5 days ahead**.

---

## Operational Domains

| Domain       | Resolution | Status      |
| ------------ | ---------- | ----------- |
| Portugal     | 2.5 km     | Operational |
| Douro        | 2.5 km     | Operational |
| Guadiana     | 2.5 km     | Operational |
| Tejo (Tagus) | 2.5 km     | Operational |
| Maranhão     | 600 m      | Operational |
| Minho        | 2.5 km     | Ready       |
| Mondego      | 2.5 km     | Ready       |
| Mira         | 500 m      | Ready       |

---

## Scientific Background

MOHID-Land is a physically-based, fully distributed hydrological model that explicitly simulates water fluxes between:

* atmosphere,
* surface water,
* river networks,
* soil and groundwater systems,
* vegetation.

The model combines:

* Saint-Venant equations for surface and channel flow;
* Richards equation for subsurface flow;
* FAO Penman-Monteith evapotranspiration formulation;
* Dynamic interactions between surface and groundwater compartments.

The implemented models simulate natural hydrological conditions without considering anthropogenic interventions such as dam operations or water abstractions.

---

## Repository Structure

```text
TwinStream/
├── Meteo/
│   ├── AROME_IPMA/
│   ├── WRF_MARETEC/
│   └── WRF_MeteoGalicia/
│
├── MOHID/
│   ├── OPPortugal/
│   ├── OPDouro/
│   ├── OPGuadiana/
│   ├── OPTejo/
│   ├── OPMaranhao/
│   ├── Minho/
│   ├── Mondego/
│   └── Mira/
│
├── ConvertToHDFExe/
├── HDF5Extractor/
└── MOHIDLandExe/
```

---

## Meteorological Forcing Systems

TwinStream uses three independent meteorological forecasting systems:

| Model            | Provider     | Resolution |
| ---------------- | ------------ | ---------- |
| AROME            | IPMA         | 2.5 km     |
| WRF-MARETEC      | MARETEC      | 3 km       |
| WRF-MeteoGalicia | MeteoGalicia | 3–36 km    |

The operational workflow automatically:

1. Downloads meteorological forecasts;
2. Converts NetCDF files to HDF5;
3. Extracts daily forecast datasets;
4. Interpolates forcing data to the hydrological grids;
5. Executes MOHID-Land simulations.

---

## Operational Workflow

```text
Meteorological Forecast
           ↓
      Download
           ↓
   NetCDF → HDF5
           ↓
 Spatial Interpolation
           ↓
     MOHID-Land
           ↓
    Post-processing
           ↓
 THREDDS Publication
```

The operational execution of MOHID-Land models is managed through:

```bash
run_operational.py
```

which controls:

* meteorological preprocessing,
* model execution,
* output management,
* operational monitoring.

---

## Software Requirements

### Python

| Component                   | Version     |
| --------------------------- | ----------- |
| Meteorological workflows    | Python 3.10 |
| MOHID operational workflows | Python 3.11 |

### External Executables

The following executables are required:

* MOHID-Land
* ConvertToHDF5
* HDF5Extractor

These executables are distributed in:

```text
MOHIDLandExe/
ConvertToHDFExe/
HDF5Extractor/
```

---

## Outputs

The operational system produces:

* Time-series outputs;
* Restart (.FIN) files;
* Spatial HDF5 datasets;
* THREDDS published products.

The published datasets feed the TwinStream operational platform.

---

## Publications

If you use TwinStream or the implemented MOHID-Land models, please cite:

```bibtex
@article{oliveira2020mohid,
  title={Sensitivity Analysis of the MOHID-Land Hydrological Model},
  author={Oliveira, A.R. and others},
  journal={Water},
  volume={12},
  pages={3258},
  year={2020}
}
```

Additional references:

* Trancoso et al. (2009)
* Brito (2017)
* Canuto et al. (2019)
* Oliveira et al. (2020)

---

## License

Please contact the repository maintainers regarding licensing conditions.
