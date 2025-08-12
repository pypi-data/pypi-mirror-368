# SPDX-FileCopyrightText: 2024 CERN
#
# SPDX-License-Identifier: BSD-4-Clause

import matplotlib.pyplot as plt
import numpy as np
import scipy as sci
from scipy import optimize

_knots_init_default = np.linspace(0.0, 1.0, 11)


class BSpline_2D:
    """
    A BSpline class to model space curves in 2D.
    """

    def __init__(self) -> None:
        """Default constructor."""

        # the spline degree
        self.degree = 3

        # the knot vector
        self.knots = np.array([])

        # the control points
        self.cpts = np.zeros((0, 2))

    def fit_to_points(self, t, points) -> None:
        """Fit a BSpline curve $x(t)$ through the data given by points, without
        specifying the knot vector. Here we fully rely on the default fitting
        provided by scipy.interpolate.splrep

        :param t:
            The parameter array. If You like, t is the 'time' the space curve
            reached the corresponding point in the points array. t must be
            monotonic increasing between 0 and 1.

        :param points:
            Points in 2D. That means, a numpy array of dimentsion $M\times  2$
            where $M$ is the number of points.

        :return:
            Nothing
        """
        tx, cx, kx = sci.interpolate.splrep(t, points[:, 0], k=self.degree)
        ty, cy, ky = sci.interpolate.splrep(t, points[:, 1], k=self.degree)

        # number of control points
        num_cpts = cx.shape[0]

        # combine the control points
        self.cpts = np.zeros((num_cpts, 2))
        self.cpts[:, 0] = cx
        self.cpts[:, 1] = cy

        # setup the knot vector
        self.knots = tx

    def evaluate(self, t):
        """Evaluate the Spline curve at some parameters t.

        :param t:
            The parameters.

        :return:
            The points in 2D.
        """

        num_eval = 1 if isinstance(t, float) else len(t)

        # container for the evaluation points
        points_eval = np.zeros((num_eval, 2))

        # evaluate
        points_eval[:, 0] = sci.interpolate.splev(t, (self.knots, self.cpts[:, 0], self.degree))
        points_eval[:, 1] = sci.interpolate.splev(t, (self.knots, self.cpts[:, 1], self.degree))

        return points_eval

    def evaluate_derivative(self, t, d=1):
        """Evaluate the Spline curves derivative at some parameters t.

        :param t:
            The parameters.

        :param d:
            The derivative order.

        :return:
            The points in 2D.
        """

        num_eval = 1 if isinstance(t, float) else len(t)

        # container for the evaluation points
        points_eval = np.zeros((num_eval, 2))

        # evaluate
        points_eval[:, 0] = sci.interpolate.splev(t, (self.knots, self.cpts[:, 0], self.degree), der=d)
        points_eval[:, 1] = sci.interpolate.splev(t, (self.knots, self.cpts[:, 1], self.degree), der=d)

        return points_eval

    def compute_distance_to_point(self, point, disc=1000):
        """Compute the minimum distance between a point and the spline curve.
        ML: 02/02/2024: We are keeping it simple here. We discretize the splines
        and then just take the minimum value. In this way we avoid the numerical
        optimisation. In the future, maybe we use some root finding algorithm.

        :param point:
            The point.

        :param disc:
            The discretization parameter. Default = 1000.

        :return:
            The minimum distance.
            The parameter t for which the distance is minimmal.
            The point on the spline which is closest to the given point.
        """

        # an initial guess is obtained from sampling

        # we construct a t vector
        t_disc = np.linspace(self.knots[0], self.knots[-1], disc)

        # we evaluate the spline at these points
        p_spl = self.evaluate(t_disc)

        # we compute the distances
        dist = p_spl.copy()
        dist[:, 0] -= point[0]
        dist[:, 1] -= point[1]
        dist = np.linalg.norm(dist, axis=1)

        # this is the initial guess. It should already be close.
        # not many newton steps are needed
        t_0 = t_disc[np.argmin(dist)]

        # # use the code at the bottom to get it more accurate.
        # # Take care though to limit the search interval
        # # this is the objective function
        # def obj_fcn(t):

        #     diff = self.evaluate(t)[0, :]
        #     diff[0] -= point[0]
        #     diff[1] -= point[1]

        #     return np.linalg.norm(diff)

        # # # this is the precise location
        # res = optimize.minimize(obj_fcn, t_0, bounds=[(t_disc[0], t_disc[-1])])

        # t_min = res.x

        t_min = t_0

        # this is the point on the Bspline
        p_min = self.evaluate(t_min)[0]

        # this is the distance
        dist_min = np.linalg.norm(p_min - point)

        return dist_min, t_min, p_min

    def compute_line_intersection(self, m, p_0, s_0, disc=500, plot=False, extend=False):
        """Compute the intersection point between a line with the equation

        $$
            \\vec{r}(s) = \\vec{m} s + \\vec{r}_0
        $$

        Also here we keep it simple and discretize.

        :param m:
            The tangential vector of the line.

        :param p_0:
            The point on the line for s = 0.

        :param s_0:
            An initial guess.

        :param bounds:
            The bounds for s_0.

        :param disc:
            The discretization parameter.

        :return:
            The parameter s of intersection.
            The point of intersection.
        """

        # we construct a t vector
        t_disc = np.linspace(self.knots[0], self.knots[-1], disc)

        # this is the residual we want to minimize with newtons method
        def func(t):
            # if isinstance(t, float):
            #     if t > t_disc[-1]:
            #         t = t_disc[-1]

            #     if t < t_disc[0]:
            #         t = t_disc[0]
            # else:
            #     t[t > t_disc[-1]] = t_disc[-1]
            #     t[t < t_disc[0]] = t_disc[0]

            # evaluate the spline at this point
            p_spl = self.evaluate(t)

            # get the x and y coordinates
            x_spl = p_spl[:, 0]
            y_spl = p_spl[:, 1]

            # compute the line
            y_line = m[1] / m[0] * x_spl - m[1] / m[0] * p_0[0] + p_0[1]

            return y_spl - y_line

        def func_prime(t):
            # if isinstance(t, float):
            #     if t > t_disc[-1]:
            #         t = t_disc[-1]

            #     if t < t_disc[0]:
            #         t = t_disc[0]
            # else:
            #     t[t > t_disc[-1]] = t_disc[-1]
            #     t[t < t_disc[0]] = t_disc[0]

            # evaluate the spline at this point
            dp_spl = self.evaluate_derivative(t)

            # get the x and y coordinates
            dx_spl = dp_spl[:, 0]
            dy_spl = dp_spl[:, 1]

            # compute the line
            dy_line = m[1] / m[0] * dx_spl

            return dy_spl - dy_line

        def func_prime2(t):
            # if isinstance(t, float):
            #     if t > t_disc[-1]:
            #         t = t_disc[-1]

            #     if t < t_disc[0]:
            #         t = t_disc[0]
            # else:
            #     t[t > t_disc[-1]] = t_disc[-1]
            #     t[t < t_disc[0]] = t_disc[0]

            # evaluate the spline at this point
            ddp_spl = self.evaluate_derivative(t, d=2)

            # get the x and y coordinates
            ddx_spl = ddp_spl[:, 0]
            ddy_spl = ddp_spl[:, 1]

            # compute the line
            ddy_line = m[1] / m[0] * ddx_spl

            return ddy_spl - ddy_line

        # an initial estimate
        t_0 = t_disc[np.argmin(abs(func(t_disc)))]

        if plot:
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.plot(t_disc, func(t_disc))
            ax.plot(t_0, func(t_0), "o")
            plt.show()

        # there must be a zero crossing
        if True:  # func(t_disc[0])*func(t_disc[-1]) < 0:
            t_newton = optimize.newton(func, t_0, fprime=func_prime, fprime2=func_prime2)
            p_intersect = self.evaluate(t_newton)[0, :]
            s_min = np.linalg.norm(p_intersect - p_0)

            if p_intersect[1] < p_0[1]:
                s_min *= -1.0

            success = True

            if plot:
                ax.plot(t_newton, func(t_newton), "o")

        else:
            print("else")
            s_min = s_0
            p_intersect = None
            success = False

        return s_min, p_intersect, success


class BSpline_3D:
    """
    The BSpline_3D class to model space curves in 3D using basis splines.
    """

    def __init__(self):
        """Default constructor."""

        # the spline degree
        self.degree = 3

        # the knot vector
        self.knots = np.array([])

        # the control points
        self.cpts = np.zeros((0, 3))

    def get_control_points(self):
        """This function returns the control points without the repetitions at the end."""
        return self.cpts[: -self.degree - 1, :]

    def adaptive_fit(
        self, curve_fcn, knots_init=_knots_init_default, tolerance=1e-3, disc=10, degree=3, plot=False, verbose=0
    ):
        """Adaptive curve fitting. We increase the number of control points
        until local convergence

        :param curve_fcn:
            The curve to fit as a function t in (0, 1) -> R3.

        :param knots_init:
            The initial knot vector.

        :param tolerance:
            A tolerance for the local errors.

        :param disc:
            The discretization level. We discretize each interval in the knots list by
            this amount.

        :param degree:
            The spline degree.

        :param plot:
            A flag to specify if a plot shall be generated.

        :param verbose:
            Info provided to user during the refinement. 0: none, 1: every step.
        """

        # get the t vector
        t_init = self.make_t_vector(disc, knots_init)

        # get the points
        points_init = curve_fcn(t_init)

        # fit
        self.fit_bspline_curve(t_init, points_init, knots_init)

        # evaluate
        points_fit = self.evaluate(t_init)

        # compute local errors
        err = np.linalg.norm(points_fit - points_init, axis=1)

        knots_new, max_error = self.refine_knot_vector(t_init, points_fit, points_init, knots_init)

        # a counter variable
        cnt = 1

        while max_error > tolerance:
            # get the t vector
            t = self.make_t_vector(disc, knots_new)

            # get the points
            points = curve_fcn(t)

            # fit
            self.fit_bspline_curve(t, points, knots_new)

            # evaluate
            fit = self.evaluate(t)

            knots_new, max_error = self.refine_knot_vector(t, points, fit, knots_new)

            # compute local errors
            err = np.linalg.norm(fit - points, axis=1)

            if plot:
                # plot
                fig = plt.figure()
                ax = fig.add_subplot(111)
                ax.plot(t, err, label="errors")
                ax.plot(knots_new, 0.0 * knots_new, "--x", label="knots new")
                plt.show()

            if verbose == 1:
                print(f"--step {cnt}, max error = {max_error:.2e}, tolerance = {tolerance:.2e}")

            cnt += 1

    def refine_knot_vector(self, t, data, fit, knot_vector, ratio=0.2):
        """Refine a knot vector based on the error between fit and data.

        :param t:
            The parameter vector

        :param data:
            The data to fit.

        :param fit:
            The fitted data.

        :knot_vector knots:
            The knot vector.

        :knot_vector ratio:
            The refinement ratio. We will refine this ratio of the
            sum of the maximum interval errors.
        """
        # the errors
        err = np.linalg.norm(fit - data, axis=1)

        # the number of intervals
        num_intervals = len(knot_vector) - 1

        # the indicators
        indicators = np.zeros((num_intervals,))

        for i in range(num_intervals):
            # mask for this interval
            mask = (t >= knot_vector[i]) * (t < knot_vector[i + 1])
            if i == num_intervals - 1:
                mask[-1] = True

            # the indicator is the maximum error in this interval
            indicators[i] = max(err[mask])

        # sum of maximum errors
        sum_max_err = sum(indicators)

        # the sorting of the indicators
        sorting = np.argsort(-1 * indicators)

        # the list of intervals to refine
        refine_list = [sorting[0]]

        # the counter for the combined errors
        err_cnt = indicators[sorting[0]]

        # counter of intervals
        int_cnt = 1

        while err_cnt < ratio * sum_max_err:
            refine_list.append(sorting[int_cnt])

            err_cnt += indicators[sorting[int_cnt]]

            int_cnt += 1

        # refine
        knots_new = knot_vector.copy()

        for i, indx in enumerate(refine_list):
            knots_new = np.insert(knots_new, indx + i + 1, 0.5 * (knots_new[indx + i] + knots_new[indx + i + 1]))

        return knots_new, max(indicators)

    def make_t_vector(self, disc, t_inner):
        """Make a parameter vector which is separating each interval in the
        knots list by disc number of points.

        :param disc:
            The number of cuts for each interval.

        :param t_inner:
            The inner knot vector.
        """

        # the return vector
        t = np.array([])

        # loop over the intervals
        for i in range(len(t_inner) - 1):
            if i == 0:
                t = np.append(t, np.linspace(t_inner[i], t_inner[i + 1], disc + 2))
            else:
                t = np.append(t, np.linspace(t_inner[i], t_inner[i + 1], disc + 2)[1:])

        return t

    def fit_bspline_curve(self, t, points, knots, degree=3, debug=False) -> None:
        """Fit a BSpline curve $x(t)$ through the data given by points.

        :param t:
            The parameter array. If You like, t is the 'time' the space curve
            reached the corresponding point in the points array. t must be
            monotonic increasing between 0 and 1.

        :param points:
            Points in 3D. That means, a numpy array of dimentsion $M\times x3$
            where $M$ is the number of points.

        :param knots:
            A knot vector which specifies only interior knots.

        :param degree:
            The spline degree.

        :param debug:
            Set this flag true if You like to generate an output plot.

        :return:
            None
        """

        # set the degree
        self.degree = degree

        # we interpolate x y and z coordinates
        # by specifying the knot vector this will essentially require the solution of a
        # linear least squares problem
        tx, cx, kx = sci.interpolate.splrep(
            t, points[:, 0], xb=knots[0], xe=knots[-1], k=degree, task=-1, t=knots[1:-1]
        )
        ty, cy, ky = sci.interpolate.splrep(
            t, points[:, 1], xb=knots[0], xe=knots[-1], k=degree, task=-1, t=knots[1:-1]
        )
        tz, cz, kz = sci.interpolate.splrep(
            t, points[:, 2], xb=knots[0], xe=knots[-1], k=degree, task=-1, t=knots[1:-1]
        )

        # number of control points
        num_cpts = cx.shape[0]

        # combine the control points
        self.cpts = np.zeros((num_cpts, 3))
        self.cpts[:, 0] = cx
        self.cpts[:, 1] = cy
        self.cpts[:, 2] = cz

        # setup the knot vector
        self.knots = tx

        if debug:
            t_hr = np.linspace(t[0], t[-1], 1000)

            fig = plt.figure()
            ax = fig.add_subplot(231)
            ax.plot(t, points[:, 0], "o")
            ax.plot(t_hr, sci.interpolate.splev(t_hr, [tx, cx, kx]))
            ax.set_title("x dim")
            ax = fig.add_subplot(232)
            ax.plot(t, points[:, 1], "o")
            ax.plot(t_hr, sci.interpolate.splev(t_hr, [ty, cy, ky]))
            ax.set_title("y dim")
            ax = fig.add_subplot(233)
            ax.plot(t, points[:, 2], "o")
            ax.plot(t_hr, sci.interpolate.splev(t_hr, [tz, cz, kz]))
            ax.set_title("z dim")

            ax = fig.add_subplot(234)
            ax.plot(t, points[:, 0] - sci.interpolate.splev(t, [tx, cx, kx]))
            ax.set_title("error x")
            ax = fig.add_subplot(235)
            ax.plot(t, points[:, 1] - sci.interpolate.splev(t, [ty, cy, ky]))
            ax.set_title("error y")
            ax = fig.add_subplot(236)
            ax.plot(t, points[:, 2] - sci.interpolate.splev(t, [tz, cz, kz]))
            ax.set_title("error z")
            plt.show()

        return None

    def fit_to_points(self, t, points):
        """Fit a BSpline curve $x(t)$ through the data given by points, without
        specifying the knot vector. Here we fully rely on the default fitting
        provided by scipy.interpolate.splrep

        :param t:
            The parameter array. If You like, t is the 'time' the space curve
            reached the corresponding point in the points array. t must be
            monotonic increasing between 0 and 1.

        :param points:
            Points in 3D. That means, a numpy array of dimentsion $M\times x3$
            where $M$ is the number of points.

        :return:
            Nothing
        """
        # print('y points to fit = {}'.format(points[:, 1]))

        tx, cx, kx = sci.interpolate.splrep(t, points[:, 0], k=self.degree)
        ty, cy, ky = sci.interpolate.splrep(t, points[:, 1], k=self.degree)
        tz, cz, kz = sci.interpolate.splrep(t, points[:, 2], k=self.degree)

        # print('control points = {}'.format(cy))
        # print('knot vector = {}'.format(ty))

        # t_hr = np.linspace(ty[0], ty[-1], 1000)
        # fig = plt.figure()
        # ax = fig.add_subplot(111)
        # ax.plot(t, points[:, 1], 'o')
        # ax.plot(t_hr, sci.interpolate.splev(t_hr, [ty, cy, ky]))
        # ax.plot(t, cy[:-ky-1], 'o')
        # plt.show()

        # number of control points
        num_cpts = cx.shape[0]

        # combine the control points
        self.cpts = np.zeros((num_cpts, 3))
        self.cpts[:, 0] = cx
        self.cpts[:, 1] = cy
        self.cpts[:, 2] = cz

        # setup the knot vector
        self.knots = tx

    def evaluate(self, t):
        """Evaluate the Spline curve at some parameters t.

        :param t:
            The parameters.

        :return:
            The points in 3D.
        """
        # number of evaluation points
        num_eval = len(t)

        # container for the evaluation points
        points_eval = np.zeros((num_eval, 3))

        # evaluate
        points_eval[:, 0] = sci.interpolate.splev(t, (self.knots, self.cpts[:, 0], self.degree))
        points_eval[:, 1] = sci.interpolate.splev(t, (self.knots, self.cpts[:, 1], self.degree))
        points_eval[:, 2] = sci.interpolate.splev(t, (self.knots, self.cpts[:, 2], self.degree))

        return points_eval

    def fit_cable_geometry(
        self,
        winding,
        edge_position="lower left",
        cable_position="center",
        degree=3,
        tolerance=1e-4,
        plot=False,
        frame="Darboux",
    ):
        """Fit a BSpline curve $x(t)$ to a corner of a winding geomety.

        :param winding:
            A winding instance.

        :param edge_position:
            Position of the edge. Must be: 'lower left', 'lower right',
            'upper left', 'upper right'

        :param cable_position:
            Position of the cable with respect to the space curve. Either
            'center' or 'lower_left_corner'.

        :param degree:
            BSpline degree.

        :param tolerance:
            The stopping criteria. We stop when all max. errors are below this
            threshhold.

        :param frame:
            The winding frame. Either 'Frenet' or 'Darboux'.
        """

        # discretization level
        disc = 20

        # get a coarse knot vector
        knots_init = winding.get_coarse_knot_vector()

        # get the t vector
        t_init = self.make_t_vector(disc, knots_init)

        # get the points
        points_init = winding.get_cond_corner_points(t_init, edge_position, cable_position, frame)

        # fit
        self.fit_bspline_curve(t_init, points_init, knots_init)

        # evaluate
        points_fit = self.evaluate(t_init)

        knots_new, max_error = self.refine_knot_vector(t_init, points_fit, points_init, knots_init)

        while max_error > tolerance:
            # get the t vector
            t = self.make_t_vector(disc, knots_new)

            # get the points
            points = winding.get_cond_corner_points(t_init, edge_position, cable_position, frame)

            # fit
            self.fit_bspline_curve(t, points, knots_new)

            # evaluate
            fit = self.evaluate(t)

            # refine
            knots_new, max_error = self.refine_knot_vector(t, points, fit, knots_new)

            # compute local errors
            err = np.linalg.norm(fit - points, axis=1)

            if plot:
                # plot
                fig = plt.figure()
                ax = fig.add_subplot(111)
                ax.plot(t, err, label="errors")
                ax.plot(knots_new, 0.0 * knots_new, "--x", label="knots new")
                plt.show()

    def to_gmsh_spline(self, gmsh_model_occ, target_meshsize=1e-2):
        """Translate the spline to a gmsh BSpline representation.

        :param gmsh_model_occ:
            The gmsh.model.occ engine.

        :param target_meshsize:
            The target meshsize. Only relevant if You want to use the
            gmsh mesh generator at some point.

        :return:
            The tag of the spline representation. Also return the point tag list.
        """

        # a point tag list
        point_tag_list = []

        # print('control points')
        # fill it
        for _, cpt in enumerate(self.get_control_points()):
            # print(cpt)
            point_tag_list.append(gmsh_model_occ.addPoint(cpt[0], cpt[1], cpt[2], target_meshsize))

        # repeated knots at the ends of the intervals
        multiplicities = np.ones((len(self.knots[self.degree : -self.degree]),))
        multiplicities[0] = self.degree + 1
        multiplicities[-1] = self.degree + 1

        # make the gmsh spline
        gmsh_spline = gmsh_model_occ.addBSpline(
            point_tag_list,
            degree=self.degree,
            knots=self.knots[self.degree : -self.degree],
            multiplicities=multiplicities,
        )

        # return
        return gmsh_spline, point_tag_list


def test_circle(t):
    """A simple test function evaluating a circle to test the
    code above.

    :param t:
        The parameter.
    """

    # number of points
    num_points = len(t)

    # the container for the return values
    ret_val = np.zeros((num_points, 3))

    # fill it
    ret_val[:, 0] = np.cos(2 * np.pi * t)
    ret_val[:, 1] = np.sin(2 * np.pi * t)

    return ret_val


if __name__ == "__main__":
    # number of points
    num_points = 100

    # a small test script
    t = np.linspace(0, 1, num_points)

    # evaluate the circle
    points = test_circle(t)

    # number of knots
    num_knots = 5

    # make a knot vector
    knots = np.linspace(0, 1, num_knots)

    # initialize a BSpline
    bspline = BSpline_3D()

    # fit the spline curve
    # bspline.fit_bspline_curve(t, points, knots)
    bspline.adaptive_fit(test_circle, tolerance=1e-5)

    print(f"Number of control points = {bspline.cpts.shape[0]}")

    # evaluate the bpline
    points_fit = bspline.evaluate(t)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(t, points[:, 0] - points_fit[:, 0], label="error_x")
    ax.plot(t, points[:, 1] - points_fit[:, 1], label="error_y")
    ax.plot(t, points[:, 2] - points_fit[:, 2], label="error_z")
    ax.set_xlabel("$t$")
    ax.set_ylabel("$x(t)$")
    ax.legend()
    plt.show()

    # plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    ax.plot(points[:, 0], points[:, 1], points[:, 2], label="Data")
    ax.plot(points_fit[:, 0], points_fit[:, 1], points_fit[:, 2], "--", label="Fit")
    ax.legend()
    ax.set_xlabel("$x$")
    ax.set_ylabel("$y$")
    ax.set_zlabel("$z$")
    plt.show()
