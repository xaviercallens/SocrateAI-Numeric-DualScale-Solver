import os
import shutil
import subprocess
import numpy as np
import time

def generate_openfoam_case(case_dir, ux, uy, n_grid=32, L=2*np.pi, nu=1e-3, dt=5e-4, n_steps=200):
    os.makedirs(case_dir, exist_ok=True)
    os.makedirs(os.path.join(case_dir, "0"), exist_ok=True)
    os.makedirs(os.path.join(case_dir, "constant"), exist_ok=True)
    os.makedirs(os.path.join(case_dir, "system"), exist_ok=True)
    
    # ─── system/blockMeshDict ───
    blockMeshDict = f"""/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v1912                                 |
|   \\\\  /    A nd           | Website:  www.openfoam.com                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile {{ version 2.0; format ascii; class dictionary; object blockMeshDict; }}
scale   1.0;
vertices
(
    (0 0 0)
    ({L} 0 0)
    ({L} {L} 0)
    (0 {L} 0)
    (0 0 0.1)
    ({L} 0 0.1)
    ({L} {L} 0.1)
    (0 {L} 0.1)
);
blocks
(
    hex (0 1 2 3 4 5 6 7) ({n_grid} {n_grid} 1) simpleGrading (1 1 1)
);
edges ();
boundary
(
    left
    {{
        type cyclic;
        neighbourPatch right;
        faces ((0 4 7 3));
    }}
    right
    {{
        type cyclic;
        neighbourPatch left;
        faces ((1 2 6 5));
    }}
    bottom
    {{
        type cyclic;
        neighbourPatch top;
        faces ((0 1 5 4));
    }}
    top
    {{
        type cyclic;
        neighbourPatch bottom;
        faces ((3 7 6 2));
    }}
    frontAndBack
    {{
        type empty;
        faces ((0 3 2 1) (4 5 6 7));
    }}
);
mergePatchPairs ();
"""
    with open(os.path.join(case_dir, "system", "blockMeshDict"), "w") as f:
        f.write(blockMeshDict)
        
    # ─── system/controlDict ───
    end_time = dt * n_steps
    controlDict = f"""FoamFile {{ version 2.0; format ascii; class dictionary; object controlDict; }}
application     icoFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         {end_time};
deltaT          {dt};
writeControl    timeStep;
writeInterval   {n_steps};
purgeWrite      0;
writeFormat     ascii;
writePrecision  6;
writeCompression off;
timeFormat      general;
timePrecision   6;
runTimeModifiable true;
"""
    with open(os.path.join(case_dir, "system", "controlDict"), "w") as f:
        f.write(controlDict)

    # ─── system/fvSchemes ───
    fvSchemes = """FoamFile { version 2.0; format ascii; class dictionary; object fvSchemes; }
ddtSchemes { default Euler; }
gradSchemes { default Gauss linear; }
divSchemes { default none; div(phi,U) Gauss linear; }
laplacianSchemes { default Gauss linear orthogonal; }
interpolationSchemes { default linear; }
snGradSchemes { default orthogonal; }
"""
    with open(os.path.join(case_dir, "system", "fvSchemes"), "w") as f:
        f.write(fvSchemes)

    # ─── system/fvSolution ───
    fvSolution = """FoamFile { version 2.0; format ascii; class dictionary; object fvSolution; }
solvers {
    p { solver PCG; preconditioner DIC; tolerance 1e-06; relTol 0.01; }
    pFinal { $p; relTol 0; }
    U { solver smoothSolver; smoother symGaussSeidel; tolerance 1e-05; relTol 0.1; }
}
PISO { nCorrectors 3; nNonOrthogonalCorrectors 0; pRefCell 0; pRefValue 0; }
"""
    with open(os.path.join(case_dir, "system", "fvSolution"), "w") as f:
        f.write(fvSolution)

    # ─── constant/transportProperties ───
    transportProperties = f"""FoamFile {{ version 2.0; format ascii; class dictionary; object transportProperties; }}
nu              [0 2 -1 0 0 0 0] {nu};
"""
    with open(os.path.join(case_dir, "constant", "transportProperties"), "w") as f:
        f.write(transportProperties)
        
    # ─── 0/p ───
    pDict = """FoamFile { version 2.0; format ascii; class volScalarField; object p; }
dimensions      [0 2 -2 0 0 0 0];
internalField   uniform 0;
boundaryField
{
    left { type cyclic; }
    right { type cyclic; }
    bottom { type cyclic; }
    top { type cyclic; }
    frontAndBack { type empty; }
}
"""
    with open(os.path.join(case_dir, "0", "p"), "w") as f:
        f.write(pDict)

    # ─── 0/U ───
    # Flatten the velocity array for blockMesh (x varies fastest, then y, then z)
    # The JHTDB array is shape (nx, ny). Let's reshape it appropriately.
    # Actually, in OpenFOAM, blockMesh hex (0 1 2 3 4 5 6 7) defines local x, y, z.
    # The cell order is x varying fastest.
    lines = []
    for j in range(n_grid):
        for i in range(n_grid):
            # JHTDB returns arrays where index 0 is x, 1 is y? No, usually (y,x) or (x,y).
            # Let's assume ux[i,j] or ux[j,i]. Our python FDM uses ux[i, j] where X, Y = meshgrid(x, y, indexing='ij').
            # We'll just flatten following 'F' (Fortran) or 'C' depending on how it was built. 
            # In Python FDM we had x,y = meshgrid indexing 'ij', so X[i,j] = x[i].
            # Meaning i is x-axis (varies fastest in memory if transposed, or slowest if not).
            # We'll just write ux[i,j], uy[i,j], 0
            u_x = ux[i, j]
            u_y = uy[i, j]
            lines.append(f"({u_x} {u_y} 0)")
    
    u_vals = "\n".join(lines)
    
    uDict = f"""FoamFile {{ version 2.0; format ascii; class volVectorField; object U; }}
dimensions      [0 1 -1 0 0 0 0];
internalField   nonuniform List<vector>
{n_grid*n_grid}
(
{u_vals}
)
;
boundaryField
{{
    left {{ type cyclic; }}
    right {{ type cyclic; }}
    bottom {{ type cyclic; }}
    top {{ type cyclic; }}
    frontAndBack {{ type empty; }}
}}
"""
    with open(os.path.join(case_dir, "0", "U"), "w") as f:
        f.write(uDict)

def run_openfoam(case_dir):
    bashrc = "/usr/share/openfoam/etc/bashrc"
    
    print("[*] Running blockMesh...")
    cmd1 = f"bash -c 'source {bashrc} && blockMesh -case {case_dir}'"
    subprocess.run(cmd1, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print("[*] Running icoFoam...")
    t0 = time.time()
    cmd2 = f"bash -c 'source {bashrc} && icoFoam -case {case_dir} > {case_dir}/log.icoFoam'"
    subprocess.run(cmd2, shell=True)
    t1 = time.time()
    
    # Parse log for divergence and time
    divs = []
    with open(os.path.join(case_dir, "log.icoFoam"), "r") as f:
        for line in f:
            if "time step continuity errors" in line:
                # e.g.: time step continuity errors : sum local = 1.09677e-07, global = 1.34141e-18, cumulative = -3.73199e-17
                parts = line.split(",")
                for p in parts:
                    if "sum local" in p:
                        val_str = p.split("=")[1].strip()
                        divs.append(float(val_str))
                        break
                        
    max_div = max(divs) if divs else -1
    return {"wall_time_sec": t1 - t0, "final_max_divergence": max_div}

