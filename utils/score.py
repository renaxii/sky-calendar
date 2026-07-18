def calculate_score(
    clouds,
    humidity
):
    score = 100

    score -= clouds * 0.7

    if humidity > 80:
        score -= 10

    return max(
        0,
        min(
            100,
            round(score)
        )
    )

# remember to add
# - moon brightness
# - light pollution
# - visible planets
# - meteor showers