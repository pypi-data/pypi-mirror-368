from iss_pass_tracker import get_passes


def test_get_passes_structure():
    # This test will actually hit the Open Notify endpoint; in CI you may want to mock it.
    passes = get_passes(lat=17.385044, lon=78.486671, n=1)
    assert isinstance(passes, list)
    assert len(passes) <= 1
    if passes:
        p = passes[0]
        assert p.duration >= 0
        assert p.risetime.tzinfo is not None
