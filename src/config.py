# 時段設定：slot 1 = 08:00-09:00, 2 = 09:00-10:00, ... 14 = 21:00-22:00
SLOTS_PER_DAY = 14
FIRST_SLOT_HOUR = 8
DAYS_PER_WEEK = 5  # 週一至週五

def slot_to_time_range(slot: int) -> str:
    h = FIRST_SLOT_HOUR + (slot - 1)
    return f"{h:02d}:00-{h+1:02d}:00"

def get_all_slot_labels():
    return [slot_to_time_range(s) for s in range(1, SLOTS_PER_DAY + 1)]
