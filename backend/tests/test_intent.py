import pytest
from app.agents.intent_parser import intent_parser

@pytest.mark.asyncio
async def test_fast_add_intent():
    res = await intent_parser.parse_intent("Add 2kg rice")
    assert res.intent == "ADD_ITEM"
    assert len(res.items) > 0
    assert "rice" in res.items[0]["raw_query"]

@pytest.mark.asyncio
async def test_fast_remove_intent():
    res = await intent_parser.parse_intent("Remove milk")
    assert res.intent == "REMOVE_ITEM"
    assert len(res.items) > 0
    assert "milk" in res.items[0]["raw_query"]

@pytest.mark.asyncio
async def test_decision_intent():
    res = await intent_parser.parse_intent("I need a laptop under 80000")
    assert res.intent == "RECOMMEND"
    assert res.category == "electronics"
    assert "max_budget" in res.hard_constraints
