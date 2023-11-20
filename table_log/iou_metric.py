def calc_iou(a, p):  # both are in the form x1, y1, x2, y2
    # print(a)
    # print(p)
    total_area = abs(a[2]-a[0])*abs(a[3]-a[1]) + abs(p[2]-p[0])*abs(p[3]-p[1])
    lx = a[2] - a[0] + p[2] - p[0] - (max(a[2], a[0], p[2], p[0]) - min(a[2], a[0], p[2], p[0]))
    if lx <= 0:
        return 0
    ly = a[3] - a[1] + p[3] - p[1] - (max(a[3], a[1], p[3], p[1]) - min(a[3], a[1], p[3], p[1]))
    if ly <= 0:
        return 0
    intersection_area = lx * ly

    return intersection_area/(total_area-intersection_area)