import numpy as np


def nvt_accept(
    U_old: float,
    U_new: float,
    beta: float,
    chi2_old: float = 0.0,
    chi2_new: float = 0.0,
    rng: np.random.Generator | None = None,
) -> bool:
    """
    NVT Metropolis with extra χ² cost.
    Accept with prob min(1, exp( - [Δχ² + βΔU] )).
    """

    dcost = (chi2_new - chi2_old) + beta * (U_new - U_old)
    if dcost <= 0:
        return True

    rng = rng or np.random.default_rng()
    return np.log(rng.random()) < -dcost


def npt_accept(
    U_old: float,
    U_new: float,
    V_old: float,
    V_new: float,
    N: int,
    beta: float,
    pressure: float,
    chi2_old: float = 0.0,
    chi2_new: float = 0.0,
    *,
    log_volume_proposal: bool = True,  # True for Δ = ln V proposals (your move)
    rng: np.random.Generator | None = None,
) -> bool:
    """
    NPT Metropolis for isotropic volume move with extra χ² cost.

    If proposals are symmetric in ln V (Δ ~ Uniform[-Δ,Δ]), set
    log_volume_proposal=True:

        accept ∝ exp[ - (Δχ² + β(ΔU + PΔV)) + (N+1) ln(V_new/V_old) ]

    If proposals are symmetric in V (ΔV ~ Uniform[-a,a]), set
    log_volume_proposal=False:

        accept ∝ exp[ - (Δχ² + β(ΔU + PΔV)) + N ln(V_new/V_old) ]
    """

    if V_old <= 0.0 or V_new <= 0.0:
        return False

    dchi2 = chi2_new - chi2_old
    dU = U_new - U_old
    dV = V_new - V_old

    # Jacobian power: N (linear-in-V) or N+1 (log-volume proposal)
    jpow = N + 1 if log_volume_proposal else N
    lnVratio = np.log(V_new) - np.log(V_old)

    dcost = dchi2 + beta * (dU + pressure * dV) - jpow * lnVratio
    if dcost <= 0:
        return True

    rng = rng or np.random.default_rng()
    return np.log(rng.random()) < -dcost
