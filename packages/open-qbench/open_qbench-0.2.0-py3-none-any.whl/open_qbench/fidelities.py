"""A file collecting different measures of fidelity between two probability distributions for use with the benchmarking suite."""

import itertools
import math

import numpy as np


def normalized_fidelity(dist_ideal: dict, dist_backend: dict) -> float:
    """Compute normalized fidelity of Lubinski et al."""
    backend_fidelity = classical_fidelity(dist_ideal, dist_backend)
    uniform_fidelity = fidelity_with_uniform(dist_ideal)

    raw_fidelity = (backend_fidelity - uniform_fidelity) / (1 - uniform_fidelity)
    fidelity = max([raw_fidelity, 0])
    return fidelity


def create_normalized_fidelity(input_state):
    def normalized_fidelity_orca(dist_ideal: dict, dist_backend: dict) -> float:
        """Compute normalized fidelity modified for Boson Sampling."""
        backend_fidelity = classical_fidelity_orca(
            dist_ideal, dist_backend, input_state
        )
        uniform_fidelity = classical_fidelity_orca(
            dist_ideal, _uniform_dist_orca(input_state), input_state
        )

        raw_fidelity = (backend_fidelity - uniform_fidelity) / (1 - uniform_fidelity)

        fidelity = max([raw_fidelity, 0])
        return fidelity

    return normalized_fidelity_orca


def classical_fidelity(dist_a: dict, dist_b: dict) -> float:
    r"""Compute classical fidelity of two probability distributions.

    Args:
        dist_a (dict): Distribution of experiment A
        dist_b (dict): Distribution of experiment B

    Returns:
        float: Classical fidelity given by:
        F(X,Y) = (\sum _i \sqrt{p_i q_i})^2

    """
    num_qubits = len(next(iter(dist_a.keys())))
    bitstrings = ("".join(i) for i in itertools.product("01", repeat=num_qubits))
    fidelity = 0.0
    for b in bitstrings:
        p_a = dist_a.get(b, 0)
        p_b = dist_b.get(b, 0)
        fidelity += math.sqrt(p_a * p_b)
    fidelity = fidelity**2
    return fidelity


def classical_fidelity_orca(
    dist_a: dict, dist_b: dict, input_state: list[int]
) -> float:
    r"""Compute classical fidelity of two probability distributions.

    Args:
        dist_a (dict): Distribution of experiment A
        dist_b (dict): Distribution of experiment B

    Returns:
        float: Classical fidelity given by:
        F(X,Y) = (\sum _i \sqrt{p_i q_i})^2

    """
    bitstrings = generate_all_possible_outputs_orca(input_state)
    fidelity = 0.0
    for b in bitstrings:
        p_a = dist_a.get(b, 0)
        p_b = dist_b.get(b, 0)
        fidelity += math.sqrt(p_a * p_b)
    fidelity = fidelity**2
    return fidelity


def fidelity_with_uniform(dist: dict) -> float:
    r"""Compute classical fidelity of a probability distribution with a same-sized uniform distribution.

    Args:
        dist (dict): Probability distribution

    Returns:
        float: Classical fidelity given by:
        F(X,Y) = (\sum _i \sqrt{p_i q_i})^2

    """
    num_qubits = len(next(iter(dist.keys())))
    fidelity = 0.0
    uniform_prob = 1 / 2**num_qubits
    for prob in dist.values():
        fidelity += math.sqrt(prob * uniform_prob)
    fidelity = fidelity**2
    return fidelity


def _uniform_dist_orca(input_state) -> dict:
    samples = generate_all_samples_orca(input_state)
    prob = 1 / len(samples)
    dist = {s: prob for s in samples}
    return dist


def counts_to_dist(counts: dict) -> dict:
    shots = sum(counts.values())
    dist = {x: y / shots for x, y in counts.items()}
    return dist


def generate_all_samples_orca(input_state):
    from ptseries.tbi import create_tbi

    time_bin_interferometer = create_tbi()
    samples = time_bin_interferometer.sample(
        input_state=input_state,
        theta_list=[np.pi / 4] * (len(input_state) - 1),  # 50/50 beam splitters
        n_samples=100000,
    )
    samples_sorted = dict(sorted(samples.items(), key=lambda state: -state[1]))
    labels = list(samples_sorted.keys())
    return labels


def generate_all_possible_outputs_orca(input_state):
    all_possible_outputs = []
    max_num_photons = np.sum(input_state)
    # print(max_num_photons)
    tab_num_photons = range(0, max_num_photons + 1)
    arr = itertools.product(tab_num_photons, repeat=len(input_state))

    for el in arr:
        if np.sum(el) <= np.sum(input_state):
            all_possible_outputs.append(el)
    return all_possible_outputs


def per(mtx, column, selected, prod, output=False):
    if column == mtx.shape[1]:
        if output:
            print(selected, prod)
        return prod
    else:
        result = 0
        for row in range(mtx.shape[0]):
            if row not in selected:
                result = result + per(
                    mtx,
                    column + 1,
                    [*selected, row],
                    prod * mtx[row, column],
                )
        return result


def compute_permanent(mat):
    return per(mat, 0, [], 1)


def construct_unitary(bm_parameters):
    def beamsplitter_matrix(theta, n, i, j):
        U = np.eye(n, dtype=complex)
        cos_theta = np.cos(theta)
        sin_theta = np.sin(theta)

        U[i, i] = cos_theta
        U[i, j] = -sin_theta
        U[j, i] = sin_theta
        U[j, j] = cos_theta

        return U

    def apply_sequential_beam_splitters(thetas):
        n = len(thetas) + 1
        U = np.eye(n, dtype=complex)
        for k, theta in enumerate(thetas):
            if k + 1 < n:
                BS = beamsplitter_matrix(theta, n, k, k + 1)
                U = BS @ U
        return U

    return apply_sequential_beam_splitters(bm_parameters)


def generate_submatrix(U, input_bitstring, output):
    columns = [j for j, t in enumerate(output) for _ in range(t)]
    UT = U[:, columns]

    rows = [i for i, s in enumerate(input_bitstring) for _ in range(s)]
    UST = UT[rows, :]
    return UST


def output_probabilities(input_bitstring, U):
    possible_outputs = generate_all_possible_outputs_orca(input_bitstring)
    probabilities = {}

    for output_indices in possible_outputs:
        U_submatrix = generate_submatrix(U, input_bitstring, output_indices)
        PQT = np.abs(compute_permanent(U_submatrix)) ** 2
        probabilities[tuple(output_indices)] = PQT / (
            np.prod([math.factorial(s) for s in input_bitstring])
            * np.prod([math.factorial(t) for t in output_indices])
        )

    total_prob = sum(probabilities.values())
    for key in probabilities:
        probabilities[key] /= total_prob

    return probabilities


def generate_analitically(input_bitstring):
    input_bitstring = input_bitstring[::-1]
    theta_list = [np.pi / 4] * (len(input_bitstring) - 1)
    U = construct_unitary(theta_list)
    probabilities = output_probabilities(input_bitstring, U)
    return sorted(
        [
            (key[::-1])
            for key, value in probabilities.items()
            if value > 1e-30 and sum(key) == sum(input_string)
        ]
    )


if __name__ == "__main__":
    input_string = (1, 1, 2)
    ans0 = generate_analitically(input_string)
    ans1 = generate_all_samples_orca(input_string)
    ans2 = generate_all_possible_outputs_orca(input_string)
    print(ans0)
    print(len(ans0))
    print(ans1)
    print(len(ans1))
    print(ans2)
    print(len(ans2))
