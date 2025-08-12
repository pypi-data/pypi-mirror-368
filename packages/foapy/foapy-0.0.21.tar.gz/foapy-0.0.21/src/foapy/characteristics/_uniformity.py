import numpy as np


def uniformity(intervals_grouped, dtype=None):
    """
    Calculates uniformity of intervals grouped by element of the alphabet.

    $$ u = \\frac {1} {n} * \\sum_{j=1}^{m}{\\log_2 \\frac{ (\\sum_{i=1}^{n_j} \\frac{\\Delta_{ij}}{n_j})^{n_j} } { \\prod_{i=1}^{n_j} \\Delta_{ij}}}$$

    where \\( m \\) is count of groups (alphabet power), \\( n_j \\) is count of intervals in group \\( j \\),
    \\( \\Delta_{ij} \\) represents an interval at index \\( i \\) in group \\( j \\) and \\( n \\) is total count of intervals across all groups.

    $$n=\\sum_{j=1}^{m}{n_j} $$

    Parameters
    ----------
    intervals_grouped : array_like
        An array of intervals grouped by element
    dtype : dtype, optional
        The dtype of the output

    Returns
    -------
    : float
        The uniformity of the input array of intervals_grouped.

    Examples
    --------

    Calculate the uniformity of intervals_grouped of a sequence.

    ``` py linenums="1"
    import foapy
    import numpy as np

    source = np.array(['a', 'b', 'a', 'c', 'a', 'd'])
    order = foapy.ma.order(source)
    print(order)

    #[[0 -- 0 -- 0 --]
    # [-- 1 -- -- -- --]
    # [-- -- -- 2 -- --]
    # [-- -- -- -- -- 3]]

    intervals_grouped = foapy.ma.intervals(order, foapy.binding.start, foapy.mode.normal)

    print(intervals_grouped)
    # [
    #    array([1, 2, 2]),
    #    array([2]),
    #    array([4]),
    #    array([6])
    # ]

    # m = 4
    # n_0 = 3
    # n_1 = 1
    # n_2 = 1
    # n_3 = 1
    # n = 6

    result = foapy.characteristics.uniformity(intervals_grouped)
    print(result)
    # 0.03514946374976957

    # Improve precision by specifying a dtype.
    result = foapy.characteristics.uniformity(intervals_grouped, dtype=np.longdouble)
    print(result)
    # 0.03514946374976969819
    ```
    """  # noqa: E501
    from foapy.characteristics import average_remoteness, identifying_information

    total_elements = np.concatenate(intervals_grouped)

    H = identifying_information(intervals_grouped, dtype=dtype)
    g = average_remoteness(total_elements, dtype=dtype)

    return H - g
