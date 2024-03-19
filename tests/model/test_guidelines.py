def test_p2o5_reductions(guidelines):
    assert isinstance(guidelines.p2o5_reductions(), dict)


def test_k2o_reductions(guidelines):
    assert isinstance(guidelines.k2o_reductions(), dict)


def test_mg_reductions(guidelines):
    assert isinstance(guidelines.mg_reductions(), dict)


def test_cao_reductions(guidelines):
    assert isinstance(guidelines.cao_reductions(), dict)


def test_soil_reductions(guidelines):
    assert isinstance(guidelines.soil_reductions(), dict)


def test_p2o5_classes(guidelines):
    assert isinstance(guidelines.p2o5_classes(), dict)


def test_k2o_classes(guidelines):
    assert isinstance(guidelines.k2o_classes(), dict)


def test_mg_classes(guidelines):
    assert isinstance(guidelines.mg_classes(), dict)


def test_ph_classes(guidelines):
    assert isinstance(guidelines.ph_classes(), dict)


def test_org_factor(guidelines):
    assert isinstance(guidelines.org_factor(), dict)


def test_pre_crop_effect(guidelines):
    assert isinstance(guidelines.pre_crop_effect(), dict)


def test_legume_delivery(guidelines):
    assert isinstance(guidelines.legume_delivery(), dict)


def test_sulfur_needs(guidelines):
    assert isinstance(guidelines.sulfur_needs(), dict)
