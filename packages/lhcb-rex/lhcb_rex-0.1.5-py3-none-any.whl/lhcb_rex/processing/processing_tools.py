import lhcb_rex.settings.globals as myGlobals

import numpy as np
import vector
import uproot


np.seterr(divide="ignore", invalid="ignore")


def write_df_to_root(df, output_name, output_tree):
    df = df.loc[:, ~df.columns.duplicated()]

    branch_dict = {}
    data_dict = {}
    dtypes = df.dtypes
    used_columns = []  # Prevent repeat columns, kpipi_correction was getting repeated

    for branch in df.keys():
        if branch not in used_columns:
            dtype = dtypes[branch]

            # Convert unsigned types to signed
            if dtype == "uint32":
                dtype = "int32"
            elif dtype == "uint64":
                dtype = "int64"

            branch_dict[branch] = dtype

            # Handle DataFrame shapes
            if df[branch].ndim > 1:
                data_dict[branch] = (
                    df[branch].iloc[:, 0].to_numpy()
                )  # Convert to NumPy array
            else:
                data_dict[branch] = df[branch].to_numpy()  # Convert to NumPy array

            if isinstance(data_dict[branch][0], list):
                data_2d = np.vstack(data_dict[branch]).astype(dtype)

                # hack to somehow avoid uproot writing count_branch, n{branch_name}:
                vec = np.empty((np.shape(data_2d)[0], np.shape(data_2d)[1]))
                for dim in range(np.shape(data_2d)[1]):
                    vec[:, dim] = data_2d[:, dim]
                data_dict[branch] = vec

        used_columns.append(branch)

    # Create the ROOT file and write the tree
    with uproot.recreate(output_name) as f:
        # Create a new tree with the specified branches and types
        f[output_tree] = data_dict

    # if myGlobals._verbose:
    # print(f"Tuple written to {output_name}")


def mag(vec):
    sum_sqs = 0
    for component in vec:
        sum_sqs += component**2
    mag = np.sqrt(sum_sqs)
    return mag


def norm(vec):
    mag_vec = mag(vec)

    # mag_vec[np.where(mag_vec==0.)] += 1e-10

    for component_idx in range(np.shape(vec)[0]):
        vec[component_idx] *= 1.0 / mag_vec
    return vec


def dot(vec1, vec2):
    dot = 0
    for component_idx in range(np.shape(vec1)[0]):
        dot += vec1[component_idx] * vec2[component_idx]
    return dot


def compute_angles(origin, end):
    vector = np.array(end) - np.array(origin)
    theta = np.arccos(
        vector[2] / np.sqrt(vector[0] ** 2 + vector[1] ** 2 + vector[2] ** 2)
    )
    phi = np.arctan2(vector[1], vector[0])
    return theta, phi


def redefine_endpoint(origin, theta, phi, new_distance):
    x = new_distance * np.sin(theta) * np.cos(phi)
    y = new_distance * np.sin(theta) * np.sin(phi)
    z = new_distance * np.cos(theta)
    return origin[0] + x, origin[1] + y, origin[2] + z


def compute_distance(df, A, A_var, B, B_var):
    X = df[f"{A}_{A_var}X_TRUE"] - df[f"{B}_{B_var}X_TRUE"]
    Y = df[f"{A}_{A_var}Y_TRUE"] - df[f"{B}_{B_var}Y_TRUE"]
    Z = df[f"{A}_{A_var}Z_TRUE"] - df[f"{B}_{B_var}Z_TRUE"]
    dist = np.sqrt(X**2 + Y**2 + Z**2)
    return dist


def compute_distance_wrapped(df, A, A_var, B, B_var):
    A = compute_distance(df, A, A_var, B, B_var)
    A = np.asarray(A)
    min_A = 5e-5
    A[np.where(A == 0)] = min_A

    return A


def compute_reconstructed_mother_momenta(df, mother, true_vars=True):
    if true_vars:
        PX = df[f"{mother}_PX_TRUE"]
        PY = df[f"{mother}_PY_TRUE"]
        PZ = df[f"{mother}_PZ_TRUE"]
    else:
        PX = df[f"{mother}_PX"]
        PY = df[f"{mother}_PY"]
        PZ = df[f"{mother}_PZ"]

    return np.sqrt((PX**2 + PY**2 + PZ**2)), np.sqrt((PX**2 + PY**2))


def compute_reconstructed_intermediate_momenta(df, particles, true_vars=True):
    PX = 0
    PY = 0
    PZ = 0

    for particle in particles:
        if true_vars:
            PX += df[f"{particle}_PX_TRUE"]
            PY += df[f"{particle}_PY_TRUE"]
            PZ += df[f"{particle}_PZ_TRUE"]
        else:
            PX += df[f"{particle}_PX"]
            PY += df[f"{particle}_PY"]
            PZ += df[f"{particle}_PZ"]

    return np.sqrt((PX**2 + PY**2 + PZ**2)), np.sqrt((PX**2 + PY**2)), PX, PY, PZ


def compute_missing_momentum(df, mother, particles):
    PX = np.asarray(df[f"{mother}_PX_TRUE"]).copy()
    PY = np.asarray(df[f"{mother}_PY_TRUE"]).copy()
    PZ = np.asarray(df[f"{mother}_PZ_TRUE"]).copy()

    for particle in particles:
        PX += -1.0 * np.asarray(df[f"{particle}_PX_TRUE"]).copy()
        PY += -1.0 * np.asarray(df[f"{particle}_PY_TRUE"]).copy()
        PZ += -1.0 * np.asarray(df[f"{particle}_PZ_TRUE"]).copy()

    return np.sqrt((PX**2 + PY**2 + PZ**2)), np.sqrt((PX**2 + PY**2))


def compute_reconstructed_momentum_residual(df, particle):
    PX = df[f"{particle}_PX"] - df[f"{particle}_PX_TRUE"]
    PY = df[f"{particle}_PY"] - df[f"{particle}_PY_TRUE"]
    PZ = df[f"{particle}_PZ"] - df[f"{particle}_PZ_TRUE"]

    return np.sqrt((PX**2 + PY**2 + PZ**2)), np.sqrt((PX**2 + PY**2))


def compute_angle(df, mother, particle, true_vars=True):
    if true_vars:
        momenta_B = np.asarray(
            [df[f"{mother}_PX_TRUE"], df[f"{mother}_PY_TRUE"], df[f"{mother}_PZ_TRUE"]]
        )
        momenta_i = np.asarray(
            [
                df[f"{particle}_PX_TRUE"],
                df[f"{particle}_PY_TRUE"],
                df[f"{particle}_PZ_TRUE"],
            ]
        )
    else:
        momenta_B = np.asarray(
            [df[f"{mother}_PX"], df[f"{mother}_PY"], df[f"{mother}_PZ"]]
        )
        momenta_i = np.asarray(
            [
                df[f"{particle}_PX"],
                df[f"{particle}_PY"],
                df[f"{particle}_PZ"],
            ]
        )

    dot_prod = np.arccos(dot(momenta_B, momenta_i) / (mag(momenta_B) * mag(momenta_i)))

    dot_prod[np.where(np.isnan(dot_prod))] = 1e-6
    dot_prod[np.where(dot_prod == 0)] = 1e-6

    return dot_prod


def compute_impactParameter(df, mother, particles, true_vars=True):
    PX = 0
    PY = 0
    PZ = 0

    for particle in particles:
        if true_vars:
            PX += df[f"{particle}_PX_TRUE"]
            PY += df[f"{particle}_PY_TRUE"]
            PZ += df[f"{particle}_PZ_TRUE"]
        else:
            PX += df[f"{particle}_PX"]
            PY += df[f"{particle}_PY"]
            PZ += df[f"{particle}_PZ"]

    momenta = vector.obj(
        px=PX,
        py=PY,
        pz=PZ,
    )

    end_vertex = np.asarray(
        [
            df[f"{mother}_vtxX_TRUE"],
            df[f"{mother}_vtxY_TRUE"],
            df[f"{mother}_vtxZ_TRUE"],
        ]
    )
    primary_vertex = np.asarray(
        [
            df[f"{mother}_origX_TRUE"],
            df[f"{mother}_origY_TRUE"],
            df[f"{mother}_origZ_TRUE"],
        ]
    )

    momenta_array = np.asarray([momenta.px, momenta.py, momenta.pz])
    P = momenta.mag
    t = 0
    for i in range(3):
        t += momenta_array[i] / P * (primary_vertex[i] - end_vertex[i])
    dist = 0
    for i in range(3):
        dist += (primary_vertex[i] - end_vertex[i] - t * momenta_array[i] / P) ** 2
    dist = np.sqrt(dist)

    return dist


def compute_impactParameter_i(df, mother, particle, true_vars=True):
    if true_vars:
        momenta = vector.obj(
            px=df[f"{particle}_PX_TRUE"],
            py=df[f"{particle}_PY_TRUE"],
            pz=df[f"{particle}_PZ_TRUE"],
        )
    else:
        momenta = vector.obj(
            px=df[f"{particle}_PX"],
            py=df[f"{particle}_PY"],
            pz=df[f"{particle}_PZ"],
        )

    end_vertex = np.asarray(
        [
            df[f"{mother}_vtxX_TRUE"],
            df[f"{mother}_vtxY_TRUE"],
            df[f"{mother}_vtxZ_TRUE"],
        ]
    )
    primary_vertex = np.asarray(
        [
            df[f"{mother}_origX_TRUE"],
            df[f"{mother}_origY_TRUE"],
            df[f"{mother}_origZ_TRUE"],
        ]
    )

    momenta_array = np.asarray([momenta.px, momenta.py, momenta.pz])
    P = momenta.mag
    t = 0
    for i in range(3):
        t += momenta_array[i] / P * (primary_vertex[i] - end_vertex[i])
    dist = 0
    for i in range(3):
        dist += (primary_vertex[i] - end_vertex[i] - t * momenta_array[i] / P) ** 2
    dist = np.sqrt(dist)

    return dist


def compute_flightDistance(df, mother, particles):
    dist = np.sqrt(
        (df[f"{mother}_vtxX_TRUE"] - df[f"{mother}_origX_TRUE"]) ** 2
        + (df[f"{mother}_vtxY_TRUE"] - df[f"{mother}_origY_TRUE"]) ** 2
        + (df[f"{mother}_vtxZ_TRUE"] - df[f"{mother}_origZ_TRUE"]) ** 2
    )

    return dist


def compute_DIRA(df, mother, particles, true_vars=True):
    PX = 0
    PY = 0
    PZ = 0

    for particle in particles:
        if true_vars:
            PX += df[f"{particle}_PX_TRUE"]
            PY += df[f"{particle}_PY_TRUE"]
            PZ += df[f"{particle}_PZ_TRUE"]
        else:
            PX += df[f"{particle}_PX"]
            PY += df[f"{particle}_PY"]
            PZ += df[f"{particle}_PZ"]

    A = norm(np.asarray([PX, PY, PZ]))

    B = norm(
        np.asarray(
            [
                df[f"{mother}_vtxX_TRUE"] - df[f"{mother}_origX_TRUE"],
                df[f"{mother}_vtxY_TRUE"] - df[f"{mother}_origY_TRUE"],
                df[f"{mother}_vtxZ_TRUE"] - df[f"{mother}_origZ_TRUE"],
            ]
        )
    )

    dira = dot(A, B) / np.sqrt(mag(A) ** 2 * mag(B) ** 2)

    return dira
