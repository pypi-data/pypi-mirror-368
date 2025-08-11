import lhcb_rex.settings.globals as myGlobals
import numpy as np
import lhcb_rex.tools.variables_tools as vt
import uproot
import lhcb_rex.tools.tuple_tools as tt
import vector
import pickle

# pid_list = [11, 13, 211, 321]
pid_list = [11, 13, 211, 321, 2212]
PID_charges = {
    11: -1,
    -11: 1,
    13: -1,
    -13: 1,
    211: 1,
    -211: -1,
    321: 1,
    -321: -1,
    2212: 1,
    -2212: -1,
}


def compute_masses(data_in, units="MeV"):
    particles = ["DAUGHTER1", "DAUGHTER2", "DAUGHTER3"]

    masses = {}
    if units == "MeV":
        masses[2212] = 938.272
        masses[321] = 493.677
        masses[211] = 139.57039
        masses[13] = 105.66
        masses[11] = 0.51099895000  # * 1e-3
    elif units == "GeV":
        masses[2212] = 938.272 * 1e-3
        masses[321] = 493.677 * 1e-3
        masses[211] = 139.57039 * 1e-3
        masses[13] = 105.66 * 1e-3
        masses[11] = 0.51099895000 * 1e-3

    for particle in particles:
        mass = np.asarray(data_in[f"{particle}_ID"]).astype("float32")
        for pid in pid_list:
            mass[np.where(np.abs(mass) == pid)] = masses[pid]
        data_in[f"{particle}_mass"] = mass

    for particle in particles:
        charge_ = np.asarray(data_in[f"{particle}_ID"]).copy()
        for key in list(PID_charges.keys()):
            charge_[np.where(charge_ == key)] = PID_charges[key]
        data_in[f"{particle}_charge"] = charge_

    where_keep = np.where(
        data_in[f"{particles[0]}_charge"] != data_in[f"{particles[1]}_charge"]
    )
    where_swap = np.where(
        data_in[f"{particles[0]}_charge"] == data_in[f"{particles[1]}_charge"]
    )

    ########################
    # Retrieve momenta (RECONSTRUCTED) and masses
    px1_reco, py1_reco, pz1_reco = (
        np.asarray(data_in[f"{particles[0]}_PX"]).copy(),
        np.asarray(data_in[f"{particles[0]}_PY"]).copy(),
        np.asarray(data_in[f"{particles[0]}_PZ"]).copy(),
    )
    px2_reco, py2_reco, pz2_reco = (
        np.asarray(data_in[f"{particles[1]}_PX"]).copy(),
        np.asarray(data_in[f"{particles[1]}_PY"]).copy(),
        np.asarray(data_in[f"{particles[1]}_PZ"]).copy(),
    )
    px3_reco, py3_reco, pz3_reco = (
        np.asarray(data_in[f"{particles[2]}_PX"]).copy(),
        np.asarray(data_in[f"{particles[2]}_PY"]).copy(),
        np.asarray(data_in[f"{particles[2]}_PZ"]).copy(),
    )

    px2_reco_buffer, py2_reco_buffer, pz2_reco_buffer = (
        px2_reco.copy(),
        py2_reco.copy(),
        pz2_reco.copy(),
    )
    px3_reco_buffer, py3_reco_buffer, pz3_reco_buffer = (
        px3_reco.copy(),
        py3_reco.copy(),
        pz3_reco.copy(),
    )

    px2_reco[where_swap], py2_reco[where_swap], pz2_reco[where_swap] = (
        px3_reco_buffer[where_swap],
        py3_reco_buffer[where_swap],
        pz3_reco_buffer[where_swap],
    )
    px3_reco[where_swap], py3_reco[where_swap], pz3_reco[where_swap] = (
        px2_reco_buffer[where_swap],
        py2_reco_buffer[where_swap],
        pz2_reco_buffer[where_swap],
    )
    ########################

    ########################
    # Retrieve momenta (TRUE) and masses
    try:
        px1, py1, pz1 = (
            np.asarray(data_in[f"{particles[0]}_TRUEP_X"]).copy(),
            np.asarray(data_in[f"{particles[0]}_TRUEP_Y"]).copy(),
            np.asarray(data_in[f"{particles[0]}_TRUEP_Z"]).copy(),
        )
        px2, py2, pz2 = (
            np.asarray(data_in[f"{particles[1]}_TRUEP_X"]).copy(),
            np.asarray(data_in[f"{particles[1]}_TRUEP_Y"]).copy(),
            np.asarray(data_in[f"{particles[1]}_TRUEP_Z"]).copy(),
        )
        px3, py3, pz3 = (
            np.asarray(data_in[f"{particles[2]}_TRUEP_X"]).copy(),
            np.asarray(data_in[f"{particles[2]}_TRUEP_Y"]).copy(),
            np.asarray(data_in[f"{particles[2]}_TRUEP_Z"]).copy(),
        )
    except:
        px1, py1, pz1 = (
            np.asarray(data_in[f"{particles[0]}_PX_TRUE"]).copy(),
            np.asarray(data_in[f"{particles[0]}_PY_TRUE"]).copy(),
            np.asarray(data_in[f"{particles[0]}_PZ_TRUE"]).copy(),
        )
        px2, py2, pz2 = (
            np.asarray(data_in[f"{particles[1]}_PX_TRUE"]).copy(),
            np.asarray(data_in[f"{particles[1]}_PY_TRUE"]).copy(),
            np.asarray(data_in[f"{particles[1]}_PZ_TRUE"]).copy(),
        )
        px3, py3, pz3 = (
            np.asarray(data_in[f"{particles[2]}_PX_TRUE"]).copy(),
            np.asarray(data_in[f"{particles[2]}_PY_TRUE"]).copy(),
            np.asarray(data_in[f"{particles[2]}_PZ_TRUE"]).copy(),
        )

    px2_buffer, py2_buffer, pz2_buffer = px2.copy(), py2.copy(), pz2.copy()
    px3_buffer, py3_buffer, pz3_buffer = px3.copy(), py3.copy(), pz3.copy()

    px2[where_swap], py2[where_swap], pz2[where_swap] = (
        px3_buffer[where_swap],
        py3_buffer[where_swap],
        pz3_buffer[where_swap],
    )
    px3[where_swap], py3[where_swap], pz3[where_swap] = (
        px2_buffer[where_swap],
        py2_buffer[where_swap],
        pz2_buffer[where_swap],
    )
    ########################

    mass_shape = np.shape(np.asarray(data_in[f"{particles[0]}_mass"]).copy())
    mass1, mass2, mass3 = (
        np.ones(mass_shape) * masses[321],
        np.ones(mass_shape) * masses[11],
        np.ones(mass_shape) * masses[11],
    )

    mass2_buffer, mass3_buffer = mass2.copy(), mass3.copy()
    mass2_buffer[where_swap], mass3_buffer[where_swap] = (
        mass3_buffer[where_swap],
        mass2_buffer[where_swap],
    )

    # Calculate energies
    E1 = np.sqrt(px1**2 + py1**2 + pz1**2 + mass1**2)
    E2 = np.sqrt(px2**2 + py2**2 + pz2**2 + mass2**2)
    E3 = np.sqrt(px3**2 + py3**2 + pz3**2 + mass3**2)

    # Calculate energies
    E1_reco = np.sqrt(px1_reco**2 + py1_reco**2 + pz1_reco**2 + mass1**2)
    E2_reco = np.sqrt(px2_reco**2 + py2_reco**2 + pz2_reco**2 + mass2**2)
    E3_reco = np.sqrt(px3_reco**2 + py3_reco**2 + pz3_reco**2 + mass3**2)

    # Compute invariant mass squared for each pair
    def invariant_mass_squared(E1, E2, px1, px2, py1, py2, pz1, pz2):
        return (E1 + E2) ** 2 - ((px1 + px2) ** 2 + (py1 + py2) ** 2 + (pz1 + pz2) ** 2)

    # Compute invariant mass squared for each pair
    def invariant_mass_squared_3_particles(
        E1, E2, E3, px1, px2, px3, py1, py2, py3, pz1, pz2, pz3
    ):
        return (E1 + E2 + E3) ** 2 - (
            (px1 + px2 + px3) ** 2 + (py1 + py2 + py3) ** 2 + (pz1 + pz2 + pz3) ** 2
        )

    def compute_costhetal_vec(E1, E2, E3, px1, px2, px3, py1, py2, py3, pz1, pz2, pz3):
        B = vector.obj(
            px=px1 + px2 + px3, py=py1 + py2 + py3, pz=pz1 + pz2 + pz3, E=E1 + E2 + E3
        )
        eplus = vector.obj(px=px3, py=py3, pz=pz3, E=E3)
        eminus = vector.obj(px=px2, py=py2, pz=pz2, E=E2)

        vecA = eplus.boost_beta3(-B.to_beta3())
        vecB = eminus.boost_beta3(-B.to_beta3())
        vecAB = vecA.add(vecB)

        boostedA = vecB.boost_beta3(-vecAB.to_beta3())
        vecAB.E = 0
        boostedA.E = 0

        dirAB = vecAB.unit()
        dirboostedA = boostedA.unit()
        costhetal = dirboostedA.dot(dirAB)

        return costhetal

    # m12^2, m13^2, and m23^2
    m12_squared = invariant_mass_squared(E1, E2, px1, px2, py1, py2, pz1, pz2)
    m13_squared = invariant_mass_squared(E1, E3, px1, px3, py1, py3, pz1, pz3)
    m23_squared = invariant_mass_squared(E2, E3, px2, px3, py2, py3, pz2, pz3)

    m123_squared = invariant_mass_squared_3_particles(
        E1, E2, E3, px1, px2, px3, py1, py2, py3, pz1, pz2, pz3
    )

    ctl = compute_costhetal_vec(E1, E2, E3, px1, px2, px3, py1, py2, py3, pz1, pz2, pz3)

    # m12^2, m13^2, and m23^2
    m12_squared_reco = invariant_mass_squared(
        E1_reco, E2_reco, px1_reco, px2_reco, py1_reco, py2_reco, pz1_reco, pz2_reco
    )
    m13_squared_reco = invariant_mass_squared(
        E1_reco, E3_reco, px1_reco, px3_reco, py1_reco, py3_reco, pz1_reco, pz3_reco
    )
    m23_squared_reco = invariant_mass_squared(
        E2_reco, E3_reco, px2_reco, px3_reco, py2_reco, py3_reco, pz2_reco, pz3_reco
    )

    m123_squared_reco = invariant_mass_squared_3_particles(
        E1_reco,
        E2_reco,
        E3_reco,
        px1_reco,
        px2_reco,
        px3_reco,
        py1_reco,
        py2_reco,
        py3_reco,
        pz1_reco,
        pz2_reco,
        pz3_reco,
    )

    ctl_reco = compute_costhetal_vec(
        E1_reco,
        E2_reco,
        E3_reco,
        px1_reco,
        px2_reco,
        px3_reco,
        py1_reco,
        py2_reco,
        py3_reco,
        pz1_reco,
        pz2_reco,
        pz3_reco,
    )

    # print(np.sqrt(m123_squared))
    # print(np.sqrt(m123_squared_reco))
    # quit()

    data_in["dalitz_mass_m12"] = np.asarray(m12_squared) / 1e6
    data_in["dalitz_mass_m13"] = np.asarray(m13_squared) / 1e6
    data_in["dalitz_mass_m23"] = np.asarray(m23_squared) / 1e6

    data_in["dalitz_mass_m12_reco"] = np.asarray(m12_squared_reco) / 1e6
    data_in["dalitz_mass_m13_reco"] = np.asarray(m13_squared_reco) / 1e6
    data_in["dalitz_mass_m23_reco"] = np.asarray(m23_squared_reco) / 1e6

    data_in["mkl"] = np.sqrt(np.asarray(m12_squared_reco))
    data_in["q2"] = np.asarray(m23_squared_reco) / 1e6
    data_in["mkee"] = np.sqrt(np.asarray(m123_squared_reco)) / 1e3

    data_in["ctl_true"] = ctl
    data_in["ctl"] = ctl_reco

    return data_in


def add_conditions(events, particles, mother, intermediates, intermediate_recipes):
    # # Kee physics example validation variables:
    # events = compute_masses(events)

    for particle in particles:
        # add true mass values for each particle based on TRUEID
        mass = np.asarray(events[f"{particle}_TRUEID"]).astype("float32")
        for pid in pid_list:
            mass[np.where(np.abs(mass) == pid)] = myGlobals.masses[pid]
        events[f"{particle}_mass"] = mass

    # convert ENDVERTEX_CHI2 to ENDVERTEX_CHI2NDOF
    events[f"{mother}_ENDVERTEX_CHI2NDOF"] = (
        events[f"{mother}_ENDVERTEX_CHI2"] / events[f"{mother}_ENDVERTEX_NDOF"]
    )
    for intermediate in intermediates:
        events[f"{intermediate}_ENDVERTEX_CHI2NDOF"] = (
            events[f"{intermediate}_ENDVERTEX_CHI2"]
            / events[f"{intermediate}_ENDVERTEX_NDOF"]
        )

    events[f"{mother}_TRUE_FD"] = events.eval(
        "sqrt((MOTHER_TRUEENDVERTEX_X-MOTHER_TRUEORIGINVERTEX_X)**2 + (MOTHER_TRUEENDVERTEX_Y-MOTHER_TRUEORIGINVERTEX_Y)**2 + (MOTHER_TRUEENDVERTEX_Z-MOTHER_TRUEORIGINVERTEX_Z)**2)"
    )

    # compute distance mother flies before decay
    A = vt.compute_distance(events, mother, "TRUEENDVERTEX", mother, "TRUEORIGINVERTEX")
    A = np.asarray(A)
    A[np.where(A == 0)] = 5e-5
    events[f"{mother}_FLIGHT"] = A

    # compute distance (scalar) any intermediate flies before decay
    for particle in particles:
        A = vt.compute_distance(
            events, particle, "TRUEORIGINVERTEX", mother, "TRUEENDVERTEX"
        )
        A = np.asarray(A)
        A[np.where(A == 0)] = 5e-5
        events[f"{particle}_FLIGHT"] = A

    # print(events)
    # quit()
    # for particle in particles:
    #     for dim in ["X",'Y',"Z"]:
    #         events[f"{particle}_TRUEORIGIN_wrtMEV_VERTEX_X"] = events[f"{particle}_TRUEORIGINVERTEX_X"]-events[f"{mother}_TRUEENDVERTEX_X"]
    #     events[f"{particle}_TRUEORIGIN_wrtMEV_VERTEX_T"] =

    # compute distance any intermediate flies before decay in each dimension
    for particle in particles:
        events[f"{particle}_deltaEV_X"] = (
            events[f"{particle}_TRUEORIGINVERTEX_X"]
            - events[f"{mother}_TRUEENDVERTEX_X"]
        )
        events[f"{particle}_deltaEV_Y"] = (
            events[f"{particle}_TRUEORIGINVERTEX_Y"]
            - events[f"{mother}_TRUEENDVERTEX_Y"]
        )
        events[f"{particle}_deltaEV_Z"] = (
            events[f"{particle}_TRUEORIGINVERTEX_Z"]
            - events[f"{mother}_TRUEENDVERTEX_Z"]
        )
        events[f"{particle}_deltaEV_T"] = np.sqrt(
            events[f"{particle}_deltaEV_X"] ** 2 + events[f"{particle}_deltaEV_Y"] ** 2
        )

    # compute masses of mother particle, reco and true
    events[f"{mother}_M"] = vt.compute_mass_N(events, particles)
    events[f"{mother}_M_reco"] = vt.compute_mass_N(events, particles, true_vars=False)

    # compute whether fully reco or not
    mother_masses = -1.0 * np.ones(events.shape[0])
    mother_TRUEID = events["MOTHER_TRUEID"]
    for PID in list(myGlobals.particle_masses_dict_mothers.keys()):
        mother_masses[np.where(np.abs(mother_TRUEID.astype(int)) == PID)] = (
            myGlobals.particle_masses_dict_mothers[PID]
        )
    events["abs_mass_diff"] = np.abs(np.asarray(events["MOTHER_M"]) - mother_masses)
    fully_reco = np.zeros(events.shape[0])
    fully_reco[np.where(events["abs_mass_diff"] < 50.0)] = 1  # 1 if within 50 MeV
    events["fully_reco"] = fully_reco

    # comptue mother momenta, reco and true
    events[f"{mother}_P"], events[f"{mother}_PT"] = (
        vt.compute_reconstructed_mother_momenta(events, mother, true_vars=False)
    )
    events[f"{mother}_TRUEP"], events[f"{mother}_TRUEP_T"] = (
        vt.compute_reconstructed_mother_momenta(events, mother, true_vars=True)
    )

    # comptue residual in momentum measurement of each particle
    for particle in particles:
        for dim in ["X", "Y", "Z"]:
            residual_frac = (
                events[f"{particle}_P{dim}"] - events[f"{particle}_TRUEP_{dim}"]
            ) / (events[f"{particle}_TRUEP_{dim}"] + 1e-4)

            _residualfrac_limit = 5.0
            limit = _residualfrac_limit
            residual_frac[residual_frac < (limit * -1.0)] = -limit
            residual_frac[residual_frac > limit] = limit

            events[f"{particle}_residualfrac_P{dim}"] = residual_frac

        PX = events[f"{particle}_TRUEP_X"]
        PY = events[f"{particle}_TRUEP_Y"]
        PZ = events[f"{particle}_TRUEP_Z"]
        PX_reco = events[f"{particle}_PX"]
        PY_reco = events[f"{particle}_PY"]
        PZ_reco = events[f"{particle}_PZ"]

        events[f"{particle}_P"] = np.sqrt((PX_reco**2 + PY_reco**2 + PZ_reco**2))
        events[f"{particle}_TRUEP"] = np.sqrt((PX**2 + PY**2 + PZ**2))
        events[f"{particle}_Preco_overP"] = (
            events[f"{particle}_P"] / events[f"{particle}_TRUEP"]
        )

    # comptue how much momentum is missing from the reconstructed mother
    events[f"{mother}_missing_P"], events[f"{mother}_missing_PT"] = (
        vt.compute_missing_momentum(events, mother, particles)
    )
    for intermediate in intermediates:
        events[f"{intermediate}_P"], events[f"{intermediate}_PT"] = (
            vt.compute_reconstructed_intermediate_momenta(
                events, intermediate_recipes[intermediate], true_vars=False
            )
        )

        events[f"{intermediate}_TRUEP"], events[f"{intermediate}_TRUEP_T"] = (
            vt.compute_reconstructed_intermediate_momenta(
                events, intermediate_recipes[intermediate], true_vars=True
            )
        )

        events[f"{intermediate}_TRUEP_X"] = np.zeros(
            np.shape(events["DAUGHTER2_TRUEP_X"])
        )
        events[f"{intermediate}_TRUEP_Y"] = np.zeros(
            np.shape(events["DAUGHTER2_TRUEP_Y"])
        )
        events[f"{intermediate}_TRUEP_Z"] = np.zeros(
            np.shape(events["DAUGHTER2_TRUEP_Z"])
        )
        for particle in intermediate_recipes[intermediate]:
            events[f"{intermediate}_TRUEP_X"] += events[f"{particle}_TRUEP_X"]
            events[f"{intermediate}_TRUEP_Y"] += events[f"{particle}_TRUEP_Y"]
            events[f"{intermediate}_TRUEP_Z"] += events[f"{particle}_TRUEP_Z"]

        events[f"{intermediate}_PX"] = np.zeros(np.shape(events["DAUGHTER2_PX"]))
        events[f"{intermediate}_PY"] = np.zeros(np.shape(events["DAUGHTER2_PY"]))
        events[f"{intermediate}_PZ"] = np.zeros(np.shape(events["DAUGHTER2_PZ"]))
        for particle in intermediate_recipes[intermediate]:
            events[f"{intermediate}_PX"] += events[f"{particle}_PX"]
            events[f"{intermediate}_PY"] += events[f"{particle}_PY"]
            events[f"{intermediate}_PZ"] += events[f"{particle}_PZ"]

    for particle in particles:
        events[f"{particle}_TRUEE"] = vt.compute_TRUEE(events, particle)

        (
            events[f"{particle}_delta_P"],
            events[f"{particle}_delta_PT"],
        ) = vt.compute_reconstructed_momentum_residual(events, particle)

    # print(events)
    # quit()

    for particle in particles:
        # if f"{particle}_TRUEP_T" not in events:
        PT = events.eval(f"sqrt({particle}_TRUEP_X**2 + {particle}_TRUEP_Y**2)")
        # else:
        #     PT = events[f"{particle}_TRUEP_T"]
        # if f"{particle}_TRUEP" not in events:
        P = events.eval(
            f"sqrt({particle}_TRUEP_X**2 + {particle}_TRUEP_Y**2 + {particle}_TRUEP_Z**2)"
        )
        # else:
        #     P = events[f"{particle}_TRUEP"]

        events[f"{particle}_eta_TRUE"] = -np.log(np.tan(np.arcsin(PT / P) / 2.0))

    for particle in particles:
        # if f"{particle}_PT" not in events:
        PT = events.eval(f"sqrt({particle}_PX**2 + {particle}_PY**2)")
        # else:
        #     PT = events[f"{particle}_PT"]
        # if f"{particle}_P" not in events:
        P = events.eval(f"sqrt({particle}_PX**2 + {particle}_PY**2 + {particle}_PZ**2)")
        # else:
        #     P = events[f"{particle}_P"]

        events[f"{particle}_eta"] = -np.log(np.tan(np.arcsin(PT / P) / 2.0))

    for particle in particles:
        for dim in ["X", "Y", "Z"]:
            events[f"{particle}_delta_P{dim}"] = (
                events[f"{particle}_P{dim}"] - events[f"{particle}_TRUEP_{dim}"]
            )
        events[f"{particle}_delta_eta"] = (
            events[f"{particle}_eta"] - events[f"{particle}_eta_TRUE"]
        )
        # events[f"{particle}_delta_theta"] = np.arctan2(events[f"{particle}_delta_PX"], events[f"{particle}_delta_PY"])

    ################################################################################

    for particle in particles:
        events[f"{particle}_angle_wrt_mother"] = vt.compute_angle(
            events, mother, f"{particle}"
        )
        events[f"{particle}_angle_wrt_mother_reco"] = vt.compute_angle(
            events, mother, f"{particle}", true_vars=False
        )
        # for intermediate in intermediates:
        #     events[f"{particle}_angle_wrt_mother_intermediate"] = vt.compute_angle(
        #         events, intermediate, f"{particle}"
        #     )
        #     events[f"{particle}_angle_wrt_mother_intermediate_reco"] = vt.compute_angle(
        #         events, intermediate, f"{particle}", true_vars=False
        #     )

    for i, particle_i in enumerate(particles):
        for j, particle_j in enumerate(particles):
            if i != j:
                events[f"edge_angle_{particle_i}_{particle_j}"] = vt.compute_angle(
                    events, f"{particle_i}", f"{particle_j}", true_vars=False
                )
                events[f"edge_angle_{particle_i}_{particle_j}_TRUE"] = vt.compute_angle(
                    events, f"{particle_i}", f"{particle_j}", true_vars=True
                )

    true_vertex = True
    events[f"{mother}_IP"] = vt.compute_impactParameter(
        events, mother, particles, true_vertex=true_vertex, true_vars=False
    )
    for particle in particles:
        events[f"{particle}_IP"] = vt.compute_impactParameter_i(
            events, mother, f"{particle}", true_vertex=true_vertex, true_vars=False
        )
    events[f"{mother}_DIRA"] = vt.compute_DIRA(
        events, mother, particles, true_vertex=true_vertex, true_vars=False
    )

    events[f"{mother}_IP_TRUE"] = vt.compute_impactParameter(
        events, mother, particles, true_vertex=true_vertex, true_vars=True
    )
    for particle in particles:
        events[f"{particle}_IP_TRUE"] = vt.compute_impactParameter_i(
            events, mother, f"{particle}", true_vertex=true_vertex, true_vars=True
        )
    events[f"{mother}_DIRA_TRUE"] = vt.compute_DIRA(
        events, mother, particles, true_vertex=true_vertex, true_vars=True
    )

    for intermediate in intermediates:
        events[f"{intermediate}_IP"] = vt.compute_impactParameter(
            events,
            mother,
            intermediate_recipes[intermediate],
            true_vertex=true_vertex,
            true_vars=False,
        )
        events[f"{intermediate}_DIRA"] = vt.compute_DIRA(
            events,
            mother,
            intermediate_recipes[intermediate],
            true_vertex=true_vertex,
            true_vars=False,
        )

        events[f"{intermediate}_IP_TRUE"] = vt.compute_impactParameter(
            events,
            mother,
            intermediate_recipes[intermediate],
            true_vertex=true_vertex,
            true_vars=True,
        )
        events[f"{intermediate}_DIRA_TRUE"] = vt.compute_DIRA(
            events,
            mother,
            intermediate_recipes[intermediate],
            true_vertex=true_vertex,
            true_vars=True,
        )

    events["weight"] = 1.0
    weights = {}
    weights[11] = 11.0
    weights[2212] = 1.0
    weights[211] = 0.15
    weights[321] = 0.85
    weights[13] = 1.7
    for ID in [11, 211, 321, 13, 2212]:
        sel_string = ""
        for particle in particles:
            sel_string += f"(abs({particle}_TRUEID) == {ID})"
            sel_string += " or "
        sel_string = sel_string[:-4]
        select = events.query(sel_string)
        events.loc[select.index, "weight"] *= weights[ID]

    return events


def compute_and_append(file_name, setting_file):
    head = -1

    print(setting_file)

    with open(setting_file, "rb") as handle:
        setting = pickle.load(handle)
        setting = setting[list(setting.keys())[0]]

    print("\n####### ####### ####### ####### #######")
    for item in setting:
        print(item, setting[item])
    print("####### ####### ####### ####### #######\n")
    # quit()

    # file_name = setting["file_name"]
    # use_intermediate = setting["use_intermediate"]
    # intermediate_recipe = setting["intermediate_recipe"]
    # N = setting["N"]

    particles = [i for i in setting["branches"].keys() if "DAUGHTER" in i]
    mother = "MOTHER"
    intermediates = [i for i in setting["branches"].keys() if "INTERMEDIATE" in i]
    intermediate_recipes = {}

    for idx, intermediate_name in enumerate(setting["intermediate_names"]):
        recipe = setting["intermediate_daughters_recursive"][intermediate_name]
        recipe_DAUGHTERS = []
        for item in recipe:
            for daughter_idx, code in enumerate(
                setting["particles"].values()
            ):  # for name, age in dictionary.iteritems():  (for Python 2.x)
                if code == item:
                    recipe_DAUGHTERS.append(f"DAUGHTER{daughter_idx + 1}")
        intermediate_recipes[f"INTERMEDIATE{idx + 1}"] = recipe_DAUGHTERS

    print("Opening...")
    file = uproot.open(f"{file_name}:DecayTree")
    branches = file.keys()
    branches = [a for a in branches if "_COV_" not in a]
    print("Cut _COV_ branches")
    if head != -1:
        events = file.arrays(branches, library="pd", entry_stop=head)
    else:
        events = file.arrays(branches, library="pd")

    print("Opened file as pd array")
    print(events.shape)

    print("Shuffling...")
    events = events.sample(frac=1)
    print("Shuffled")

    # print(events)
    for particle in particles:
        # Cut tuple to only keep muons, electrons, pions and kaons (for now)
        # print(np.unique(np.abs(events[f"{particle}_TRUEID"])))
        events = events[np.abs(events[f"{particle}_TRUEID"]).isin(pid_list)]

    # print(events)
    # quit()
    events = events.reset_index(drop=True)
    events = add_conditions(
        events, particles, mother, intermediates, intermediate_recipes
    )

    # cut_condition = "(MOTHER_TRUEID != 0) & (MOTHER_BKGCAT < 60)"
    # events = events.query(cut_condition)
    # print(events)

    tt.write_df_to_root(events, f"{file_name[:-5]}_more_vars.root")
