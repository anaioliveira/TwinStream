import os
import numpy as np
from collections import Counter

def get_dims(header):
    nrows, ncols = None, None
    for line in header:
        if "ILB_IUB" in line:
            parts = line.strip().split()
            nrows = int(parts[-1]) - int(parts[-2]) + 1
        if "JLB_JUB" in line:
            parts = line.strip().split()
            ncols = int(parts[-1]) - int(parts[-2]) + 1
    return nrows, ncols

def read_dat(filepath):
    header_lines = []
    data_lines = []
    in_grid = False
    
    with open(filepath, "r") as f:
        for line in f:
            if "<BeginGridData2D>" in line:
                in_grid = True
                header_lines.append(line)
                continue
            if "<EndGridData2D>" in line:
                in_grid = False
                header_lines.append(line)
                continue
            if in_grid:
                data_lines.append(line)
            else:
                header_lines.append(line)

    # converter para floats
    values = []
    for line in data_lines:
        try:
            values.append(float(line.strip()))
        except:
            continue
    values = np.array(values, dtype=np.float32)
    # obter dimensões e reshapar sem flip
    nrows, ncols = get_dims(header_lines)
    if nrows is None or ncols is None:
        raise ValueError("Não foi possível extrair ILB_IUB / JLB_JUB do header.")
    grid = values.reshape((nrows, ncols))  
    return header_lines, grid
    

def write_dat(filepath, header_lines, grid_2d, as_float=False):
    """Escreve o .dat assumindo que grid_2d já está na ordem do ficheiro (linha 0 = topo)."""
    # extrair dimensões a partir do array (consistente com header)
    nrows, ncols = grid_2d.shape
    with open(filepath, "w") as f:
        for line in header_lines:
            if "<BeginGridData2D>" in line:
                f.write(line)
                # escrever linhas na ordem do ficheiro (top -> bottom)
                for row in grid_2d:    # NÃO usar np.flipud aqui
                    for val in row:
                        if as_float:
                            f.write(f"{val:.3f}\n")   # float com 3 casas
                        else:
                            f.write(f"{int(val)}\n")  # inteiro
                continue
            f.write(line)

def most_frequent_non99(arr):
    mask = (arr != -99) & (arr != -999)
    valid = arr[mask]
    return Counter(valid).most_common(1)[0][0] if len(valid) > 0 else -99
        
# === Ler grids ===
regions = {
    "Portugal": {
        "dtm": r"dtm_pt_ND2_carved_fix_ND2.dat",
        "soil": [
            r"pt_soil_sl4.dat",
            r"pt_soil_sl5.dat",
            r"pt_soil_sl6.dat",
            r"pt_soil_sl7.dat"
        ],
        "landcover": r"lc_pt_fin.dat",
        "manning": r"manning_pt.dat"
    },
    #"Minho": {
    #    "dtm": r"dtm_mn_0.02_ND2_carved_ND2_fix.dat",
    #    "soil": [
    #        r"mn_soil_sl4.dat",
    #        r"mn_soil_sl5.dat",
    #        r"mn_soil_sl6.dat",
    #        r"mn_soil_sl7.dat"
    #    ],
    #    "landcover": r"lc_mn_fin.dat",
    #    "manning": r"manning_mn.dat"
    #}
}

# === Iterar pelas regiões ===
for region, paths in regions.items():
    print(f"\n🔹 Processando {region}...")
    header_dtm, dtm = read_dat(paths["dtm"])
    nrows, ncols = get_dims(header_dtm)
    mask_land = (dtm != -999) & (dtm!=-99)
    mask_void = ~mask_land # sem dados
    
    # --- Soil (todos os horizontes) ---
    for soil_path in paths["soil"]:
        if not os.path.exists(soil_path):
            print(f"❌ Soil file não encontrado: {soil_path}")
            continue
        header, soil = read_dat(soil_path)
        mode_val = most_frequent_non99(soil)
        soil[(soil == -99) & mask_land] = mode_val
        soil[mask_void] = -99   # força buracos do DTM
        out_path = soil_path.replace(".dat", "_fill.dat")
        write_dat(out_path, header, soil)
        print(f"✔ Soil preenchido: {out_path}")

    # --- LandCover ---
    if os.path.exists(paths["landcover"]):
        header, land = read_dat(paths["landcover"])
        mode_val = most_frequent_non99(land)
        land[(land == -99) & mask_land] = mode_val
        land[mask_void] = -99   # força buracos do DTM
        out_path = paths["landcover"].replace(".dat", "_fill.dat")
        write_dat(out_path, header, land)
        print(f"✔ LandCover preenchido: {out_path}")

    # --- Manning ---
    if os.path.exists(paths["manning"]):
        header, manning = read_dat(paths["manning"])
        mode_val = most_frequent_non99(manning)
        manning[(manning == -99) & mask_land] = mode_val
        manning[mask_void] = -99   # força buracos do DTM
        out_path = paths["manning"].replace(".dat", "_fill.dat")
        write_dat(out_path, header, manning, as_float=True)
        print(f"✔ Manning preenchido: {out_path}")