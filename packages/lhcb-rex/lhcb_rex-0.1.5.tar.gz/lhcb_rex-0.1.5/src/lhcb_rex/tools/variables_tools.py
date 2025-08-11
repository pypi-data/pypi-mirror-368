import numpy as np
import vector

import uproot


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


def compute_DIRA(
    df, mother, particles, true_vars=True, true_vertex=False, RapidSim=False
):
    PX = 0
    PY = 0
    PZ = 0

    if true_vars:
        for particle in particles:
            if RapidSim:
                PX += df[f"{particle}_PX_TRUE"]
                PY += df[f"{particle}_PY_TRUE"]
                PZ += df[f"{particle}_PZ_TRUE"]
            else:
                PX += df[f"{particle}_TRUEP_X"]
                PY += df[f"{particle}_TRUEP_Y"]
                PZ += df[f"{particle}_TRUEP_Z"]

    else:
        for particle in particles:
            PX += df[f"{particle}_PX"]
            PY += df[f"{particle}_PY"]
            PZ += df[f"{particle}_PZ"]

    A = norm(np.asarray([PX, PY, PZ]))

    if RapidSim:
        if true_vertex:
            B = norm(
                np.asarray(
                    [
                        df[f"{mother}_vtxX_TRUE"] - df[f"{mother}_origX_TRUE"],
                        df[f"{mother}_vtxY_TRUE"] - df[f"{mother}_origY_TRUE"],
                        df[f"{mother}_vtxZ_TRUE"] - df[f"{mother}_origZ_TRUE"],
                    ]
                )
            )
        else:
            B = norm(
                np.asarray(
                    [
                        df[f"{mother}_vtxX"] - df[f"{mother}_origX"],
                        df[f"{mother}_vtxY"] - df[f"{mother}_origY"],
                        df[f"{mother}_vtxZ"] - df[f"{mother}_origZ"],
                    ]
                )
            )
    else:
        if true_vertex:
            B = norm(
                np.asarray(
                    [
                        df[f"{mother}_TRUEENDVERTEX_X"]
                        - df[f"{mother}_TRUEORIGINVERTEX_X"],
                        df[f"{mother}_TRUEENDVERTEX_Y"]
                        - df[f"{mother}_TRUEORIGINVERTEX_Y"],
                        df[f"{mother}_TRUEENDVERTEX_Z"]
                        - df[f"{mother}_TRUEORIGINVERTEX_Z"],
                    ]
                )
            )
        else:
            B = norm(
                np.asarray(
                    [
                        df[f"{mother}_ENDVERTEX_X"] - df[f"{mother}_OWNPV_X"],
                        df[f"{mother}_ENDVERTEX_Y"] - df[f"{mother}_OWNPV_Y"],
                        df[f"{mother}_ENDVERTEX_Z"] - df[f"{mother}_OWNPV_Z"],
                    ]
                )
            )

    dira = dot(A, B) / np.sqrt(mag(A) ** 2 * mag(B) ** 2)

    return dira


def compute_flightDistance(df, mother, particles, true_vars=True, true_vertex=False):
    # PX = 0
    # PY = 0
    # PZ = 0

    # if true_vars:
    #     for particle in particles:
    #         PX += df[f"{particle}_TRUEP_X"]
    #         PY += df[f"{particle}_TRUEP_Y"]
    #         PZ += df[f"{particle}_TRUEP_Z"]
    # else:
    #     for particle in particles:
    #         PX += df[f"{particle}_PX"]
    #         PY += df[f"{particle}_PY"]
    #         PZ += df[f"{particle}_PZ"]

    # momenta = vector.obj(
    #     px=PX,
    #     py=PY,
    #     pz=PZ,
    # )

    # if true_vertex:
    #     end_vertex = np.asarray(
    #         [df[f"{mother}_TRUEENDVERTEX_X"], df[f"{mother}_TRUEENDVERTEX_Y"], df[f"{mother}_TRUEENDVERTEX_Z"]]
    #     )
    #     primary_vertex = np.asarray(
    #         [df[f"{mother}_TRUEORIGINVERTEX_X"], df[f"{mother}_TRUEORIGINVERTEX_Y"], df[f"{mother}_TRUEORIGINVERTEX_Z"]]
    #     )
    # else:
    #     end_vertex = np.asarray(
    #         [df[f"{mother}_ENDVERTEX_X"], df[f"{mother}_ENDVERTEX_Y"], df[f"{mother}_ENDVERTEX_Z"]]
    #     )
    #     primary_vertex = np.asarray(
    #         [df[f"{mother}_OWNPV_X"], df[f"{mother}_OWNPV_Y"], df[f"{mother}_OWNPV_Z"]]
    #     )

    # momenta_array = np.asarray([momenta.px, momenta.py, momenta.pz])
    # P = momenta.mag
    # t = 0
    # for i in range(3):
    #     t += momenta_array[i] / P * (primary_vertex[i] - end_vertex[i])
    # dist = 0
    # for i in range(3):
    #     dist += (t * momenta_array[i] / P) ** 2
    # dist = np.sqrt(dist)

    dist = np.sqrt(
        (df[f"{mother}_TRUEENDVERTEX_X"] - df[f"{mother}_TRUEORIGINVERTEX_X"]) ** 2
        + (df[f"{mother}_TRUEENDVERTEX_Y"] - df[f"{mother}_TRUEORIGINVERTEX_Y"]) ** 2
        + (df[f"{mother}_TRUEENDVERTEX_Z"] - df[f"{mother}_TRUEORIGINVERTEX_Z"]) ** 2
    )
    return dist


def mag(vec):
    sum_sqs = 0
    for component in vec:
        sum_sqs += component**2
    mag = np.sqrt(sum_sqs)
    return mag


def norm(vec):
    mag_vec = mag(vec)
    for component_idx in range(np.shape(vec)[0]):
        vec[component_idx] *= 1.0 / mag_vec
    return vec


def dot(vec1, vec2):
    dot = 0
    for component_idx in range(np.shape(vec1)[0]):
        dot += vec1[component_idx] * vec2[component_idx]
    return dot


def compute_angle(df, mother, particle, true_vars=True, RapidSim=False):
    df = df.copy()
    if true_vars:
        if RapidSim:
            momenta_B = np.asarray(
                [
                    df[f"{mother}_PX_TRUE"],
                    df[f"{mother}_PY_TRUE"],
                    df[f"{mother}_PZ_TRUE"],
                ]
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
                [
                    df[f"{mother}_TRUEP_X"],
                    df[f"{mother}_TRUEP_Y"],
                    df[f"{mother}_TRUEP_Z"],
                ]
            )
            momenta_i = np.asarray(
                [
                    df[f"{particle}_TRUEP_X"],
                    df[f"{particle}_TRUEP_Y"],
                    df[f"{particle}_TRUEP_Z"],
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


def compute_impactParameter_i(
    df, mother, particle, true_vars=True, true_vertex=False, RapidSim=False
):
    df = df.copy()

    if true_vars:
        if RapidSim:
            momenta = vector.obj(
                px=df[f"{particle}_PX_TRUE"],
                py=df[f"{particle}_PY_TRUE"],
                pz=df[f"{particle}_PZ_TRUE"],
            )
        else:
            momenta = vector.obj(
                px=df[f"{particle}_TRUEP_X"],
                py=df[f"{particle}_TRUEP_Y"],
                pz=df[f"{particle}_TRUEP_Z"],
            )

    else:
        momenta = vector.obj(
            px=df[f"{particle}_PX"],
            py=df[f"{particle}_PY"],
            pz=df[f"{particle}_PZ"],
        )

    if RapidSim:
        if true_vertex:
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
        else:
            end_vertex = np.asarray(
                [
                    df[f"{mother}_vtxX"],
                    df[f"{mother}_vtxY"],
                    df[f"{mother}_vtxZ"],
                ]
            )
            primary_vertex = np.asarray(
                [df[f"{mother}_origX"], df[f"{mother}_origY"], df[f"{mother}_origZ"]]
            )
    else:
        if true_vertex:
            end_vertex = np.asarray(
                [
                    df[f"{mother}_TRUEENDVERTEX_X"],
                    df[f"{mother}_TRUEENDVERTEX_Y"],
                    df[f"{mother}_TRUEENDVERTEX_Z"],
                ]
            )
            primary_vertex = np.asarray(
                [
                    df[f"{mother}_TRUEORIGINVERTEX_X"],
                    df[f"{mother}_TRUEORIGINVERTEX_Y"],
                    df[f"{mother}_TRUEORIGINVERTEX_Z"],
                ]
            )
        else:
            end_vertex = np.asarray(
                [
                    df[f"{mother}_ENDVERTEX_X"],
                    df[f"{mother}_ENDVERTEX_Y"],
                    df[f"{mother}_ENDVERTEX_Z"],
                ]
            )
            primary_vertex = np.asarray(
                [
                    df[f"{mother}_OWNPV_X"],
                    df[f"{mother}_OWNPV_Y"],
                    df[f"{mother}_OWNPV_Z"],
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


def compute_intermediate_distance(df, intermediate, mother):
    df = df.copy()
    X = df[f"{intermediate}_TRUEENDVERTEX_X"] - df[f"{mother}_TRUEENDVERTEX_X"]
    Y = df[f"{intermediate}_TRUEENDVERTEX_Y"] - df[f"{mother}_TRUEENDVERTEX_Y"]
    Z = df[f"{intermediate}_TRUEENDVERTEX_Z"] - df[f"{mother}_TRUEENDVERTEX_Z"]
    dist = np.sqrt(X**2 + Y**2 + Z**2)
    return dist


def compute_distance(df, A, A_var, B, B_var, RapidSim=False, true_vars=True):
    df = df.copy()

    if RapidSim:
        X = df[f"{A}_{A_var}X_TRUE"] - df[f"{B}_{B_var}X_TRUE"]
        Y = df[f"{A}_{A_var}Y_TRUE"] - df[f"{B}_{B_var}Y_TRUE"]
        Z = df[f"{A}_{A_var}Z_TRUE"] - df[f"{B}_{B_var}Z_TRUE"]
    else:
        X = df[f"{A}_{A_var}_X"] - df[f"{B}_{B_var}_X"]
        Y = df[f"{A}_{A_var}_Y"] - df[f"{B}_{B_var}_Y"]
        Z = df[f"{A}_{A_var}_Z"] - df[f"{B}_{B_var}_Z"]

    dist = np.sqrt(X**2 + Y**2 + Z**2)
    return dist


def compute_impactParameter(
    df, mother, particles, true_vars=True, true_vertex=False, RapidSim=False
):
    df = df.copy()

    PX = 0
    PY = 0
    PZ = 0

    if true_vars:
        for particle in particles:
            if RapidSim:
                PX += df[f"{particle}_PX_TRUE"]
                PY += df[f"{particle}_PY_TRUE"]
                PZ += df[f"{particle}_PZ_TRUE"]
            else:
                PX += df[f"{particle}_TRUEP_X"]
                PY += df[f"{particle}_TRUEP_Y"]
                PZ += df[f"{particle}_TRUEP_Z"]
    else:
        for particle in particles:
            PX += df[f"{particle}_PX"]
            PY += df[f"{particle}_PY"]
            PZ += df[f"{particle}_PZ"]

    momenta = vector.obj(
        px=PX,
        py=PY,
        pz=PZ,
    )
    if RapidSim:
        if true_vertex:
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
        else:
            end_vertex = np.asarray(
                [
                    df[f"{mother}_vtxX"],
                    df[f"{mother}_vtxY"],
                    df[f"{mother}_vtxZ"],
                ]
            )
            primary_vertex = np.asarray(
                [df[f"{mother}_origX"], df[f"{mother}_origY"], df[f"{mother}_origZ"]]
            )
    else:
        if true_vertex:
            end_vertex = np.asarray(
                [
                    df[f"{mother}_TRUEENDVERTEX_X"],
                    df[f"{mother}_TRUEENDVERTEX_Y"],
                    df[f"{mother}_TRUEENDVERTEX_Z"],
                ]
            )
            primary_vertex = np.asarray(
                [
                    df[f"{mother}_TRUEORIGINVERTEX_X"],
                    df[f"{mother}_TRUEORIGINVERTEX_Y"],
                    df[f"{mother}_TRUEORIGINVERTEX_Z"],
                ]
            )
        else:
            end_vertex = np.asarray(
                [
                    df[f"{mother}_ENDVERTEX_X"],
                    df[f"{mother}_ENDVERTEX_Y"],
                    df[f"{mother}_ENDVERTEX_Z"],
                ]
            )
            primary_vertex = np.asarray(
                [
                    df[f"{mother}_OWNPV_X"],
                    df[f"{mother}_OWNPV_Y"],
                    df[f"{mother}_OWNPV_Z"],
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


# def compute_delta_mom(df, particle):
def compute_reconstructed_momentum_residual(df, particle, RapidSim=False):
    df = df.copy()

    if RapidSim:
        PX = df[f"{particle}_PX"] - df[f"{particle}_PX_TRUE"]
        PY = df[f"{particle}_PY"] - df[f"{particle}_PY_TRUE"]
        PZ = df[f"{particle}_PZ"] - df[f"{particle}_PZ_TRUE"]
    else:
        PX = df[f"{particle}_PX"] - df[f"{particle}_TRUEP_X"]
        PY = df[f"{particle}_PY"] - df[f"{particle}_TRUEP_Y"]
        PZ = df[f"{particle}_PZ"] - df[f"{particle}_TRUEP_Z"]

    return np.sqrt((PX**2 + PY**2 + PZ**2)), np.sqrt((PX**2 + PY**2))


# def compute_miss_mom(df, mother, particles, true_vars=True):
def compute_missing_momentum(df, mother, particles, true_vars=True, RapidSim=False):
    df = df.copy()

    if true_vars:
        if RapidSim:
            PX = np.asarray(df[f"{mother}_PX_TRUE"]).copy()
            PY = np.asarray(df[f"{mother}_PY_TRUE"]).copy()
            PZ = np.asarray(df[f"{mother}_PZ_TRUE"]).copy()

            for particle in particles:
                PX += -1.0 * np.asarray(df[f"{particle}_PX_TRUE"]).copy()
                PY += -1.0 * np.asarray(df[f"{particle}_PY_TRUE"]).copy()
                PZ += -1.0 * np.asarray(df[f"{particle}_PZ_TRUE"]).copy()
        else:
            PX = np.asarray(df[f"{mother}_TRUEP_X"]).copy()
            PY = np.asarray(df[f"{mother}_TRUEP_Y"]).copy()
            PZ = np.asarray(df[f"{mother}_TRUEP_Z"]).copy()

            for particle in particles:
                PX += -1.0 * np.asarray(df[f"{particle}_TRUEP_X"]).copy()
                PY += -1.0 * np.asarray(df[f"{particle}_TRUEP_Y"]).copy()
                PZ += -1.0 * np.asarray(df[f"{particle}_TRUEP_Z"]).copy()
    else:
        PX = np.asarray(df[f"{mother}_PX"]).copy()
        PY = np.asarray(df[f"{mother}_PY"]).copy()
        PZ = np.asarray(df[f"{mother}_PZ"]).copy()

        for particle in particles:
            PX += -1.0 * np.asarray(df[f"{particle}_PX"]).copy()
            PY += -1.0 * np.asarray(df[f"{particle}_PY"]).copy()
            PZ += -1.0 * np.asarray(df[f"{particle}_PZ"]).copy()

    return np.sqrt((PX**2 + PY**2 + PZ**2)), np.sqrt((PX**2 + PY**2))


def compute_reconstructed_intermediate_momenta(df, particles, true_vars=True):
    df = df.copy()

    PX = 0
    PY = 0
    PZ = 0

    if true_vars:
        for particle in particles:
            PX += df[f"{particle}_TRUEP_X"]
            PY += df[f"{particle}_TRUEP_Y"]
            PZ += df[f"{particle}_TRUEP_Z"]
    else:
        for particle in particles:
            PX += df[f"{particle}_PX"]
            PY += df[f"{particle}_PY"]
            PZ += df[f"{particle}_PZ"]

    return np.sqrt((PX**2 + PY**2 + PZ**2)), np.sqrt((PX**2 + PY**2))


def compute_TRUEE(df, particle, RapidSim=False):
    df = df.copy()

    M = df[f"{particle}_mass"]
    if RapidSim:
        PX = df[f"{particle}_PX_TRUE"]
        PY = df[f"{particle}_PY_TRUE"]
        PZ = df[f"{particle}_PZ_TRUE"]
    else:
        PX = df[f"{particle}_TRUEP_X"]
        PY = df[f"{particle}_TRUEP_Y"]
        PZ = df[f"{particle}_TRUEP_Z"]

    return np.sqrt((M**2 + PX**2 + PY**2 + PZ**2))


def compute_TRUEP(df, particle, RapidSim=False):
    df = df.copy()

    if RapidSim:
        PX = df[f"{particle}_PX_TRUE"]
        PY = df[f"{particle}_PY_TRUE"]
        PZ = df[f"{particle}_PZ_TRUE"]
    else:
        PX = df[f"{particle}_TRUEP_X"]
        PY = df[f"{particle}_TRUEP_Y"]
        PZ = df[f"{particle}_TRUEP_Z"]

    return np.sqrt((PX**2 + PY**2 + PZ**2))


# def compute_B_mom(df, mother, true_vars=True):
def compute_reconstructed_mother_momenta(df, mother, true_vars=True):
    df = df.copy()

    if true_vars:
        PX = df[f"{mother}_TRUEP_X"]
        PY = df[f"{mother}_TRUEP_Y"]
        PZ = df[f"{mother}_TRUEP_Z"]
    else:
        PX = df[f"{mother}_PX"]
        PY = df[f"{mother}_PY"]
        PZ = df[f"{mother}_PZ"]

    return np.sqrt((PX**2 + PY**2 + PZ**2)), np.sqrt((PX**2 + PY**2))


def compute_mass_N(df, particles, true_vars=True):
    df = df.copy()

    if true_vars:
        for p_idx, particle in enumerate(particles):
            if p_idx == 0:
                PE = np.sqrt(
                    df[f"{particle}_mass"] ** 2
                    + df[f"{particle}_TRUEP_X"] ** 2
                    + df[f"{particle}_TRUEP_Y"] ** 2
                    + df[f"{particle}_TRUEP_Z"] ** 2
                )
                PX = df[f"{particle}_TRUEP_X"]
                PY = df[f"{particle}_TRUEP_Y"]
                PZ = df[f"{particle}_TRUEP_Z"]

            else:
                PE += np.sqrt(
                    df[f"{particle}_mass"] ** 2
                    + df[f"{particle}_TRUEP_X"] ** 2
                    + df[f"{particle}_TRUEP_Y"] ** 2
                    + df[f"{particle}_TRUEP_Z"] ** 2
                )
                PX += df[f"{particle}_TRUEP_X"]
                PY += df[f"{particle}_TRUEP_Y"]
                PZ += df[f"{particle}_TRUEP_Z"]
    else:
        for p_idx, particle in enumerate(particles):
            if p_idx == 0:
                PE = np.sqrt(
                    df[f"{particle}_mass"] ** 2
                    + df[f"{particle}_PX"] ** 2
                    + df[f"{particle}_PY"] ** 2
                    + df[f"{particle}_PZ"] ** 2
                )
                PX = df[f"{particle}_PX"]
                PY = df[f"{particle}_PY"]
                PZ = df[f"{particle}_PZ"]

            else:
                PE += np.sqrt(
                    df[f"{particle}_mass"] ** 2
                    + df[f"{particle}_PX"] ** 2
                    + df[f"{particle}_PY"] ** 2
                    + df[f"{particle}_PZ"] ** 2
                )
                PX += df[f"{particle}_PX"]
                PY += df[f"{particle}_PY"]
                PZ += df[f"{particle}_PZ"]

    mass = np.sqrt((PE**2 - PX**2 - PY**2 - PZ**2))

    return mass
