def merge_bbox_extent(bboxes: list) -> tuple[float, float, float, float]:
    bboxes = tuple(map(tuple, zip(*bboxes, strict=True)))

    return min(bboxes[0]), min(bboxes[1]), max(bboxes[2]), max(bboxes[3])


def make_json_serializable(data):
    if isinstance(data, set):
        return list(data)
    elif isinstance(data, dict):
        return {key: make_json_serializable(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [make_json_serializable(item) for item in data]
    return data
