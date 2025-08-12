from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from xgboost import XGBClassifier, XGBRegressor


def initialize_model(model_type: str, is_numeric: bool, **kwargs) -> object:
    if model_type == "forest":
        model = (
            RandomForestRegressor(**kwargs)
            if is_numeric
            else RandomForestClassifier(**kwargs)
        )

    elif model_type == "xgboost":
        model = XGBRegressor(**kwargs) if is_numeric else XGBClassifier(**kwargs)

    return model
    # else:
    #    logging.error("Model {} is not yet supported".format(model_type))
    #    return(None)
    # TODO: logging is on another file
