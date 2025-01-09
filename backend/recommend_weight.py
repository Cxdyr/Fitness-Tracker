def round_to_nearest_fifth(val):
    return round(val/0.05) * 0.05

def calculate_recommendation(weight_performed, reps_in_reserve):
    if reps_in_reserve<= 2:
        recommended_weight = weight_performed
    elif 2< reps_in_reserve<5:
        recommended_weight = weight_performed+5
    else:
        recommended_weight= weight_performed+10
    return recommended_weight

def true_math(weight_per, reps_in_r):
    if weight_per is None or reps_in_r is None:
        true_weight = 0
    recommended_weight = calculate_recommendation(weight_per, reps_in_r)
    true_weight = round_to_nearest_fifth(recommended_weight)
    print(true_weight)
    return true_weight

