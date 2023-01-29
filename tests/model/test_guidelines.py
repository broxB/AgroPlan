import app.model.guidelines as guidelines


def test_p2o5_reductions():
    assert isinstance(guidelines.p2o5_reductions(), dict)


def test_k2o_reductions():
    assert isinstance(guidelines.k2o_reductions(), dict)


def test_mg_reductions():
    assert isinstance(guidelines.mg_reductions(), dict)


def test_cao_reductions():
    assert isinstance(guidelines.cao_reductions(), dict)


def test_soil_reductions():
    assert isinstance(guidelines.soil_reductions(), dict)


def test_p2o5_classes():
    assert isinstance(guidelines.p2o5_classes(), dict)


def test_k2o_classes():
    assert isinstance(guidelines.k2o_classes(), dict)


def test_mg_classes():
    assert isinstance(guidelines.mg_classes(), dict)


def test_ph_classes():
    assert isinstance(guidelines.ph_classes(), dict)


def test_org_factor():
    assert isinstance(guidelines.org_factor(), dict)


def test_pre_crop_effect():
    assert isinstance(guidelines.pre_crop_effect(), dict)


def test_legume_delivery():
    assert isinstance(guidelines.legume_delivery(), dict)


def test_sulfur_needs():
    assert isinstance(guidelines.sulfur_needs(), dict)
