# convergence criteria
import pandas as pd  # TODO: do I need this import here given that we import it in the main script?


# criterion for numerical variables
def calc_num_criterion(
    new_data: pd.DataFrame,
    old_data: pd.DataFrame,
    nas: pd.DataFrame,
    vars: list[str] = [],
) -> float:
    sum_squared_diff = sum(
        ((new_data[nas[vars]][vars] - old_data[nas[vars]][vars]) ** 2).sum()
    )
    sum_squared_new = sum((new_data[nas[vars]][vars] ** 2).sum())
    num_criterion = sum_squared_diff / sum_squared_new
    return num_criterion


def calc_cat_ord_criterion(
    new_data: pd.DataFrame,
    old_data: pd.DataFrame,
    nas: pd.DataFrame,
    vars: list[str] = [],
) -> float:
    matches_cat = []
    for col in vars:
        matches_cat.append(
            sum(new_data[nas][col].dropna() != old_data[nas][col].dropna())
        )
    return sum(matches_cat) / sum(nas.sum())


def stopping_rule(criterion_cat: list, criterion_num: list) -> bool:
    if not criterion_cat:
        if criterion_num[-1] > criterion_num[-2]:
            return True
    elif not criterion_num:
        if criterion_cat[-1] > criterion_cat[-2]:
            return True
    else:
        if (criterion_cat[-1] > criterion_cat[-2]) and (
            criterion_num[-1] > criterion_num[-2]
        ):
            return True

    # if the final and the pre-final. you don't need i
