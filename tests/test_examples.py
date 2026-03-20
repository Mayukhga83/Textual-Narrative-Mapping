from narrative_dna.utils import load_examples


def test_examples_have_required_fields() -> None:
    examples = load_examples()
    assert len(examples) >= 6
    for item in examples:
        assert item["id"]
        assert item["label"]
        assert len(item["source"]["text"]) >= 80
        assert len(item["target"]["text"]) >= 80
