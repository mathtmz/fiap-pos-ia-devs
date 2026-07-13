from pcos_fase2.config import GENERATED_FEATURES
from pcos_fase2.data import prepare_data


def test_prepare_data_creates_expected_features_and_split():
    prepared = prepare_data()

    for feature in GENERATED_FEATURES:
        assert feature in prepared.full_dataset.columns
        assert feature in prepared.feature_names

    assert prepared.x_train.shape[0] > prepared.x_test.shape[0]
    assert prepared.x_train_scaled.shape[1] == len(prepared.feature_names)
    assert prepared.x_test_scaled.shape[1] == len(prepared.feature_names)
    assert prepared.full_dataset.isna().sum().sum() == 0
