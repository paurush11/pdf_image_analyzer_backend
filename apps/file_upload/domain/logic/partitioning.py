from math import ceil

MIN_PART = 5 * 1024 * 1024
TARGET_PART = 20 * 1024 * 1024
THRESHOLD = 100 * 1024 * 1024  # >100MB => multipart


def plan_part_size(size_bytes: int) -> tuple[int, int]:
    part_size = max(MIN_PART, TARGET_PART)
    total_parts = max(1, ceil(size_bytes / part_size))
    return part_size, total_parts
