import copy

import numpy as np
from functools import partial


def optNM_dicts(objective, parameters, L_Bounds=None, R_Bounds=None, L_Bounds_global=None, R_Bounds_global=None,
                start_simplex=None, start_simplex_size=0.05, dif=None, is_int=None,
                save_dim=True, max_iter=10000, f_abs_tol=0.000001, f_rel_tol=0.000001,
                x_abs_tol=0.000001, x_rel_tol = 0.000001, **kwargs):

    def check_bounds(v):
        # If save_dim == False, when point v outside of boundary,
        # it will just move point back to edge of boundary.
        # If save_dim == True, if point v outside of boundary and
        # all point except worst located on edge of boundary
        # it will return True, that will make skipp reflection step.
        for k in working_keys:
            if v[k] < L_Bounds_global[k]:
                if save_dim and sumL[k] >= n:   # this mean that n point located on L_bound[k]
                    return True
                else:
                    v[k] = L_Bounds[k]          # move this point to bound edge

            if v[k] > R_Bounds_global[k]:
                if save_dim and sumR[k] >= n:
                    return True
                else:
                    v[k] = R_Bounds[k]
        return False

    n = len(parameters)
    keys = list(parameters.keys())
    values = list(parameters.values())
    if L_Bounds is None:
        L_Bounds = {key: -np.inf for key in keys}
    if R_Bounds is None:
        R_Bounds = {key: np.inf for key in keys}
    if L_Bounds_global is None:
        L_Bounds_global = {key: -np.inf for key in keys}
    if R_Bounds_global is None:
        R_Bounds_global = {key: np.inf for key in keys}

    # print("L_Bounds = ", L_Bounds, "R_Bounds = ", R_Bounds)

    is_global = (any((L_Bounds[key] == L_Bounds_global[key] and L_Bounds[key] != -np.inf) for key in keys) or
                 any((R_Bounds[key] == R_Bounds_global[key] and R_Bounds[key] != np.inf) for key in keys))

    if is_int is None:
        is_int = []
    else:
        is_int = is_int.copy()  # somehow changing is_int in one task, changes it in another task
    is_int_bool = [True if key in is_int else False for key in keys]
    any_is_int_bool = any(is_int_bool)

    if start_simplex is None:
        if dif is None:
            dif = ((np.array(R_Bounds.value()) - np.array(L_Bounds.value()))*start_simplex_size).tolist()
            for i in range(len(dif)):
                if dif[i] == np.inf:
                    dif[i] = abs(values[i]*start_simplex_size)
                if dif[i] == 0:
                    dif[i] = 0.0001
            if any_is_int_bool:
                dif[is_int_bool] = np.maximum(1, abs(np.round(dif[is_int_bool])))
            dif = dict(zip(keys, dif))

        # create simples
        Points = []
        for i in range(n):
            Points.append(parameters.copy())
        for i in range(n):
            Points[i][keys[i]] += dif[keys[i]]
        Points.append(parameters)

    else:
        Points = start_simplex
    num = n + 1  # all vertexes count

    iterations = 0
    objective_with_kwargs = partial(objective, **kwargs)
    Values = list(map(objective_with_kwargs, Points))
    Total_calls = num
    working_keys = copy.deepcopy(keys)  # keys after simplex dimension will be reduced

    skip_reflection = 0
    goto_second_reflection = False

    while True:
        ord_index = np.argsort(Values)  # sort Points by their Values
        Points = [Points[idx] for idx in ord_index]
        Values = [Values[idx] for idx in ord_index]
        # print("Points = ", Points)
        # print("Values = ", Values)

        # stopping conditions
        if Values[0] == np.inf:
            break_message = "Best value become infinity, Values[0] == np.inf"
            converged = False
            break
        if iterations >= max_iter:
            break_message = "Exceeded max number of iterations, iterations >= max_iter"
            converged = False
            break
        # check best point left cell bounds
        need_break = False
        for k in working_keys:
            if Points[0][k] < L_Bounds[k]:
                if Points[0][k] < L_Bounds_global[k]:
                    Points[0][k] = L_Bounds[k]
                else:
                    break_message = f"best point left grid cell, Points[0][{k}] < L_Bounds[{k}]"
                    converged = False
                    need_break = True
                    break
            if Points[0][k] > R_Bounds[k]:
                if Points[0][k] > R_Bounds_global[k]:
                    Points[0][k] = R_Bounds[k]
                else:
                    break_message = f"best point left grid cell, Points[0][{k}] > R_Bounds[{k}]"
                    converged = False
                    need_break = True
                    break
        if need_break:
            break

        # check f_abs_tol
        if abs(Values[-1] - Values[0]) < f_abs_tol:
            break_message = "abs tolerance reached, abs(Values[-1] - Values[0]) < f_abs_tol"
            converged = True
            break
        # check f_rel_tol
        if abs((Values[-1] - Values[0]) / Values[0]) < f_rel_tol:
            break_message = "relative tolerance reached, abs((Values[-1] - Values[0]) / Values[0]) < f_rel_tol"
            converged = True
            break

        # check  x_abs_tol
        if not any_is_int_bool:
            if all([abs(Points[-1][k] - Points[0][k]) < x_abs_tol for k in working_keys]):
                break_message = "abs tolerance reached for argument, all([abs(Points[-1][k] - Points[0][k]) < x_abs_tol for k in keys])"
                converged = True
                break
        else:
            # print("condition = ", [ k+":"+str(abs(Points[i][k] - Points[0][k]) ) if k not in is_int else
            #          k+":"+str(abs(Points[i][k] - Points[0][k]) )
            #          for i in range(1, num) for k in working_keys])
            if all([ (abs(Points[i][k] - Points[0][k]) < x_abs_tol) if k not in is_int else
                     (abs(Points[i][k] - Points[0][k]) <= 1)
                     for i in range(1, num) for k in working_keys]
                   ):
                break_message = "abs tolerance reached for argument, all([abs(Points[-1][k] - Points[0][k]) < x_abs_tol for k in keys])"
                converged = True
                break

        # check x_rel_tol
        if not any_is_int_bool:
            if all([abs((Points[-1][k] - Points[0][k])/Points[0][k]) < x_rel_tol for k in working_keys if Points[0][k] != 0]):
                break_message = "rel tolerance reached for argument, all([abs((Points[-1][k] - Points[0][k])/Points[0][k]) < x_rel_tol for k in keys if Points[0][k] !=0 ])"
                converged = True
                break
        else:
            if all([(abs((Points[i][k] - Points[0][k])/Points[0][k]) < x_rel_tol) if k not in is_int else
                    (abs(Points[i][k] - Points[0][k]) <= 1)
                    for i in range(1, num) for k in working_keys if (Points[0][k] != 0 or k in is_int)]
                   ):
                break_message = ("rel tolerance reached for argument, all([(abs((Points[i][k] - Points[0][k])/Points[0][k]) < x_rel_tol) if k not in is_int "
                                 "else (abs(Points[i][k] - Points[0][k]) <= 1) "
                                 "for i in range(1, num) for k in working_keys if (Points[0][k] != 0 or k in is_int)]  )")
                converged = True
                break

        # Reducing the dimension of a simplex when all vertex appear on one edge of the boundary
        if is_global:
            sumL = {}
            sumR = {}
            for k in working_keys:
                # sumL[i] = sum(Points[:, indexes[i]] == L_Bounds[indexes[i]])
                # sumR[i] = sum(Points[:, indexes[i]] == R_Bounds[indexes[i]])
                sumL[k] = sum([p[k] == L_Bounds_global[k] for p in Points])
                sumR[k] = sum([p[k] == R_Bounds_global[k] for p in Points])
                if sumL[k] >= num or sumR[k] >= num:  # all n+1 point on global bound
                    # todo: will it work for integer parameters?
                    # print("remove key = ", k)
                    working_keys.remove(k)
                    if k in is_int:
                        is_int.remove(k)
                    Points = Points[:-1]  # remove worst point from points list
                    Values = Values[:-1]
                    n -= 1
                    num -= 1
                    break  # this for

        # if not converged or break_message != "":
        #     break

        iterations = iterations + 1

        # Center of the opposite plane for the worst point‚ n=num-1
        # Center = np.apply_along_axis(np.mean, 0, Points[0:n])
        Center = {k: 0.0 for k in working_keys}
        for i in range(n):
            for k in working_keys:
                Center[k] += Points[i][k]
        for k in working_keys:
            Center[k] /= n

        # DX = Center - Points[-1]
        DX = {k: (Center[k]-Points[-1][k]) for k in working_keys}

        # Reflect
        if skip_reflection == 0:
            # DX2 = 2 * DX  # 1*DX
            DX2 = {k: 2*DX[k] for k in working_keys}
            if any_is_int_bool:
                # DX2[is_int] = np.maximum(1, np.abs(np.round(DX2[is_int]))) * np.sign(DX2[is_int])
                for k in is_int:
                    DX2[k] = max(1, abs(round(DX2[k]))) * (-1 if DX2[k] < 0 else 1)

            Reflected = Points[-1].copy()
            # Reflected[indexes] += DX2[indexes]
            for k in working_keys:
                Reflected[k] += DX2[k]
            goto_second_reflection = False
            if is_global:
                goto_second_reflection = check_bounds(Reflected)
            if not goto_second_reflection:
                Reflected_Value = objective_with_kwargs(Reflected)
                Total_calls += 1

        # Expand
        if skip_reflection == 0 and not goto_second_reflection and Reflected_Value < Values[0]:
            # DX2 = 3 * DX
            DX2 = {k: 3 * DX[k] for k in working_keys}
            if any_is_int_bool:
                # DX2[is_int] = np.maximum(1, np.abs(np.round(DX2[is_int]))) * np.sign(DX2[is_int])
                for k in is_int:
                    DX2[k] = max(1, abs(round(DX2[k]))) * (-1 if DX2[k] < 0 else 1)
            Expanded = Points[-1].copy()
            # Expanded[indexes] += DX2[indexes]
            for k in working_keys:
                Expanded[k] += DX2[k]
            if is_global:
                goto_second_reflection = check_bounds(Expanded)
            if not goto_second_reflection:
                Expanded_Value = objective_with_kwargs(Expanded)
                Total_calls += 1
            # todo: do we need check goto_second_reflection here?
            if not goto_second_reflection and Expanded_Value < Reflected_Value:
                Points[-1] = Expanded
                Values[-1] = Expanded_Value
                # print("Expanded! Points = ", Points)
            else:  # "Expanded_Value < Reflected_Value"
                Points[-1] = Reflected
                Values[-1] = Reflected_Value
                # print("Reflected! Points = ", Points)

        else:  # "Reflected_Value < Values[0]" (after Expand)
            if skip_reflection == 0 and not goto_second_reflection and Reflected_Value < Values[-1]:
                Points[-1] = Reflected
                Values[-1] = Reflected_Value
                # print("Reflected! Points = ", Points)
            else:  # "Reflected_Value < Values[-1]"
                # Outer_contraction
                if not goto_second_reflection:  # (  Reflected_Value2 < Values[-1]):
                    # DX2 = 1.5 * DX
                    DX2 = {k: 1.5 * DX[k] for k in working_keys}
                    if any_is_int_bool:
                        # DX2[is_int] = np.maximum(1, np.abs(np.round(DX2[is_int]))) * np.sign(DX2[is_int])
                        for k in is_int:
                            DX2[k] = max(1, abs(round(DX2[k]))) * (-1 if DX2[k] < 0 else 1)
                    # Contracted = Points[-1] + DX2  #Centr + DX2 #0.5*DX
                    Contracted = Points[-1].copy()
                    # Contracted[indexes] += DX2[indexes]
                    for k in working_keys:
                        Contracted[k] += DX2[k]
                    if is_global:
                        goto_second_reflection = check_bounds(Contracted)
                    # todo: Do we need check goto_second_reflection before Outer Contraction?
                    if not goto_second_reflection:
                        Contracted_Value = objective_with_kwargs(Contracted)
                        Total_calls += 1

                if not goto_second_reflection and Contracted_Value < Values[-1]:
                    Points[-1] = Contracted
                    Values[-1] = Contracted_Value
                    # print("Outer contracted! Points = ", Points)
                    if skip_reflection > 0:
                        skip_reflection -= 1        # reduce skip_reflection counter

                else:  # "Contracted_Value < Values[-1]"

                    # Second Reflection
                    # Center of the opposite plane for the second worst point‚ n=num-1
                    # indx = np.append(np.arange(num - 2), n)
                    # Center2 = np.apply_along_axis(np.mean, 0, Points[indx])
                    Center2 = {k: Points[-1][k] for k in working_keys}
                    for i in range(num-2):
                        for k in working_keys:
                            Center2[k] += Points[i][k]
                    for k in working_keys:
                        Center2[k] /= n

                    if goto_second_reflection:
                        # DX3 = Center2 - Points[-2]
                        DX3 = {k: (Center2[k] - Points[-2][k]) for k in working_keys}
                        # DX2 = 2 * DX3  # 1*DX
                        DX2 = {k: 2 * DX3[k] for k in working_keys}
                        if any_is_int_bool:
                            # DX2[is_int] = np.maximum(1, np.abs(np.round(DX2[is_int]))) * np.sign(DX2[is_int])
                            for k in is_int:
                                DX2[k] = max(1, abs(round(DX2[k]))) * (-1 if DX2[k] < 0 else 1)
                        Reflected2 = Points[-2].copy()
                        # Reflected2[indexes] += DX2[indexes]
                        for k in working_keys:
                            Reflected2[k] += DX2[k]
                    else:
                        # Center3 is center of opposite face to the best point
                        # index2 = np.arange(1, num)
                        # Center3 = np.apply_along_axis(np.mean, 0, Points[index2])
                        Center3 = {k: 0.0 for k in working_keys}
                        for i in range(1, num):
                            for k in working_keys:
                                Center3[k] += Points[i][k]
                        for k in working_keys:
                            Center3[k] /= n
                        # difference between two centers
                        # DX3 = Centr2 - Centr3
                        DX3 = {k: (Center2[k] - Center3[k]) for k in working_keys}
                        # move from Center2  to 3 times more than DX3
                        # p4 = Center2 + 3*DX3
                        p4 = {k: (Center2[k] + 3*DX3[k]) for k in working_keys}
                        # DX2 now is difference p4 and worst point
                        # DX2 =  p4 - Points[-1]   #3 * DX3  # 1*DX
                        DX2 = {k: (p4[k] - Points[-1][k]) for k in working_keys}
                        if any_is_int_bool:
                            # DX2[is_int] = np.maximum(1, np.abs(np.round(DX2[is_int]))) * np.sign(DX2[is_int])
                            for k in is_int:
                                DX2[k] = max(1, abs(round(DX2[k]))) * (-1 if DX2[k] < 0 else 1)
                        Reflected2 = Points[-1].copy()
                        # Reflected2[indexes] += DX2[indexes]
                        for k in working_keys:
                            Reflected2[k] += DX2[k]

                    failed_second_reflection = False
                    if is_global:
                        failed_second_reflection = check_bounds(Reflected2)
                    if not failed_second_reflection:
                        Reflected_Value2 = objective_with_kwargs(Reflected2)
                        Total_calls += 1
                    if not failed_second_reflection and Reflected_Value2 < Values[-1]:
                        Points[-1] = Reflected2
                        Values[-1] = Reflected_Value2
                        # print("Second Reflected! Points = ", Points)
                        if skip_reflection > 0:
                            skip_reflection -= 1

                    else:
                        # Inner contraction
                        # DX2 = 0.5 * DX
                        DX2 = {k: 0.5 * DX[k] for k in working_keys}
                        if any_is_int_bool:
                            # DX2[is_int] = np.maximum(1, np.abs(np.round(DX2[is_int]))) * np.sign(DX2[is_int])
                            for k in is_int:
                                DX2[k] = max(1, abs(round(DX2[k]))) * (-1 if DX2[k] < 0 else 1)
                        Contracted = Points[-1].copy()
                        # Contracted[indexes] += DX2[indexes]
                        for k in working_keys:
                            Contracted[k] += DX2[k]
                        Contracted_Value = objective_with_kwargs(Contracted)
                        Total_calls += 1
                        if Contracted_Value < Values[-1]:
                            Points[-1] = Contracted
                            Values[-1] = Contracted_Value
                            # print("Inner contracted! Points = ", Points)
                            if skip_reflection == 0:
                                skip_reflection = 2
                            else:
                                skip_reflection -= 1
                        else:  # "Contracted_Value < Values[-1]"

                            # Shrink
                            # DX4 = 0.5 * (Points - Points[0])
                            DX4 = [{k: 0.5*(p[k] - Points[0][k]) for k in working_keys} for p in Points]
                            if any_is_int_bool:
                                for i in range(len(DX4)):
                                    # DX4[i][is_int] = np.maximum(1, np.abs(np.round(DX4[i][is_int]))) * np.sign(DX4[i][is_int])
                                    for k in is_int:
                                        DX4[i][k] = max(1, abs(round(DX4[i][k]))) * (-1 if DX4[i][k] < 0 else 1)
                            Points_old = Points
                            Points = []
                            # Points = DX4 + Points[0]  # 0.5*(Points - Points[0]) + Points[0]
                            for i in range(num):
                                p = Points_old[0].copy()
                                if i>0:                     # dont change best point
                                    for k in working_keys:
                                        p[k] += DX4[i][k]
                                Points.append(p)
                            # print("Shrinked!")
                            # print("Before Points = ", Points_old)
                            # print("After  Points = ", Points)
                            # compare lists of points before func call (with build it tools, list1 == list2)
                            if Points == Points_old:  # np.array_equal(Points_old, Points)
                                break_message = ("After Shrink points didn't changed, Points == Points_old,"
                                                 "(all integer arguments cannot shrink anymore)")
                                converged = True
                                break
                            Values[1:num] = list(map(objective_with_kwargs, Points[1:num]))
                            # print("Values = ", Values)
                            Total_calls += n
                            if skip_reflection == 0:
                                skip_reflection = 2
                            else:
                                skip_reflection -= 1

    # end while true
    return Points[0], Values[0], converged, iterations, Total_calls, break_message
