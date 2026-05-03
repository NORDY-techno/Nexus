def get_rsi_emoji(rsi):
    if rsi is None: return "⚪"
    return "🟢" if rsi > 70 else "🔵" if rsi < 30 else "⚪"

def get_change_info(change, threshold):
    if change >= threshold: return "\033[92m", "+", "📈"
    if change <= -threshold: return "\033[91m", "", "📉"
    return "", "", "📊"

def get_volume_emoji(vol):
    if vol is None: return "⚪"
    return "🔥" if vol >= 100 else "⬆️" if vol > 0 else "⬇️" if vol < 0 else "⚪"
