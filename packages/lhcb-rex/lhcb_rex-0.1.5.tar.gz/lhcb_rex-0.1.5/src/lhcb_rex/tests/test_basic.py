import lhcb_rex


def test_basic():
    lhcb_rex.run(
        events=250,
        decay="B+ -> K+ e+ e-",
        naming_scheme="MOTHER -> DAUGHTER1 DAUGHTER2 DAUGHTER3",
        decay_models="BTOSLLBALL_6 -> NA NA NA",
        reconstruction_topology="MOTHER -> DAUGHTER1 { INTERMEDIATE -> DAUGHTER2 DAUGHTER3 }",
        workingDir="./pytest",
    )
