def get_rsi_emoji(rsi):
    """
    Повертає емодзі залежно від значення RSI.
    """
    if rsi is None:
        return "⚪"
    if rsi > 70:
        return "🟢"
    if rsi < 30:
        return "🔵"
    return "⚪"

def get_change_info(change, threshold):
    """
    Повертає колір, знак та емодзі залежно від зміни ціни.
    """
    if change >= threshold:
        return "\033[92m", "+", "📈"  # GREEN
    elif change <= -threshold:
        return "\033[91m", "", "📉"   # RED
    return "", "", "📊"              # RESET / GRAY

def get_volume_emoji(vol_change):
    """
    Повертає емодзі залежно від зміни об'єму.
    """
    if vol_change is None:
        return "⚪"
    if vol_change >= 100:
        return "🔥"
    if vol_change > 0:
        return "⬆️"
    if vol_change < 0:
        return "⬇️"
    return "⚪"
