"""
Unit tests for AIService.parse_transactions

Tests mock the Groq client so no API key / network is required.
Run: cd backend && poetry run pytest tests/ -v
"""
import json
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

from services.ai_service import AIService


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def service():
    with patch("services.ai_service.Groq") as mock_groq_cls:
        mock_groq_cls.return_value = MagicMock()
        svc = AIService()
        svc.client = mock_groq_cls.return_value
        yield svc


def _mock_llm(service: AIService, response_json):
    """Set the mocked LLM to return a given Python object serialised as JSON."""
    content = json.dumps(response_json, ensure_ascii=False)
    choice = MagicMock()
    choice.message.content = content
    service.client.chat.completions.create.return_value = MagicMock(
        choices=[choice]
    )


# ---------------------------------------------------------------------------
# 1. 單筆交易 — 中文
# ---------------------------------------------------------------------------

class TestSingleTransactionChinese:
    @pytest.mark.asyncio
    async def test_TC01_breakfast(self, service):
        _mock_llm(service, [{"amount": 40, "description": "早餐蛋餅", "category": "food"}])
        result = await service.parse_transactions("早餐蛋餅40元")
        assert len(result) == 1
        assert result[0]["amount"] == 40.0
        assert result[0]["category"] == "food"

    @pytest.mark.asyncio
    async def test_TC02_coffee(self, service):
        _mock_llm(service, [{"amount": 90, "description": "咖啡", "category": "drink"}])
        result = await service.parse_transactions("咖啡90元")
        assert result[0]["amount"] == 90.0
        assert result[0]["category"] == "drink"

    @pytest.mark.asyncio
    async def test_TC03_lunch_box(self, service):
        _mock_llm(service, [{"amount": 120, "description": "午餐便當", "category": "food"}])
        result = await service.parse_transactions("午餐便當120元")
        assert result[0]["amount"] == 120.0

    @pytest.mark.asyncio
    async def test_TC04_taxi(self, service):
        _mock_llm(service, [{"amount": 250, "description": "計程車", "category": "transport"}])
        result = await service.parse_transactions("計程車費250元")
        assert result[0]["category"] == "transport"

    @pytest.mark.asyncio
    async def test_TC05_hotpot(self, service):
        _mock_llm(service, [{"amount": 350, "description": "火鍋", "category": "food"}])
        result = await service.parse_transactions("晚餐火鍋350元")
        assert result[0]["amount"] == 350.0

    @pytest.mark.asyncio
    async def test_TC06_medicine(self, service):
        _mock_llm(service, [{"amount": 80, "description": "藥費", "category": "health"}])
        result = await service.parse_transactions("藥費80塊")
        assert result[0]["category"] == "health"

    @pytest.mark.asyncio
    async def test_TC07_bubble_tea(self, service):
        _mock_llm(service, [{"amount": 55, "description": "奶茶", "category": "drink"}])
        result = await service.parse_transactions("奶茶55塊")
        assert result[0]["amount"] == 55.0

    @pytest.mark.asyncio
    async def test_TC08_movie(self, service):
        _mock_llm(service, [{"amount": 280, "description": "電影票", "category": "entertainment"}])
        result = await service.parse_transactions("電影票280元")
        assert result[0]["category"] == "entertainment"

    @pytest.mark.asyncio
    async def test_TC09_parking(self, service):
        _mock_llm(service, [{"amount": 30, "description": "停車費", "category": "transport"}])
        result = await service.parse_transactions("停車費30元")
        assert result[0]["amount"] == 30.0

    @pytest.mark.asyncio
    async def test_TC10_convenience_store(self, service):
        _mock_llm(service, [{"amount": 199, "description": "超商購物", "category": "shopping"}])
        result = await service.parse_transactions("超商買東西199元")
        assert result[0]["amount"] == 199.0


# ---------------------------------------------------------------------------
# 2. 單筆交易 — 英文
# ---------------------------------------------------------------------------

class TestSingleTransactionEnglish:
    @pytest.mark.asyncio
    async def test_TC11_lunch(self, service):
        _mock_llm(service, [{"amount": 80, "description": "lunch", "category": "food"}])
        result = await service.parse_transactions("lunch 80")
        assert result[0]["amount"] == 80.0
        assert result[0]["category"] == "food"

    @pytest.mark.asyncio
    async def test_TC12_coffee_english(self, service):
        _mock_llm(service, [{"amount": 90, "description": "coffee", "category": "drink"}])
        result = await service.parse_transactions("coffee 90")
        assert result[0]["category"] == "drink"

    @pytest.mark.asyncio
    async def test_TC13_taxi_english(self, service):
        _mock_llm(service, [{"amount": 250, "description": "taxi", "category": "transport"}])
        result = await service.parse_transactions("taxi 250")
        assert result[0]["amount"] == 250.0

    @pytest.mark.asyncio
    async def test_TC14_breakfast_english(self, service):
        _mock_llm(service, [{"amount": 45, "description": "breakfast", "category": "food"}])
        result = await service.parse_transactions("breakfast 45")
        assert result[0]["amount"] == 45.0

    @pytest.mark.asyncio
    async def test_TC15_dinner(self, service):
        _mock_llm(service, [{"amount": 320, "description": "dinner", "category": "food"}])
        result = await service.parse_transactions("dinner 320")
        assert result[0]["amount"] == 320.0

    @pytest.mark.asyncio
    async def test_TC16_movie_ticket(self, service):
        _mock_llm(service, [{"amount": 280, "description": "movie ticket", "category": "entertainment"}])
        result = await service.parse_transactions("movie ticket 280")
        assert result[0]["category"] == "entertainment"

    @pytest.mark.asyncio
    async def test_TC17_parking_english(self, service):
        _mock_llm(service, [{"amount": 30, "description": "parking", "category": "transport"}])
        result = await service.parse_transactions("parking 30")
        assert result[0]["amount"] == 30.0

    @pytest.mark.asyncio
    async def test_TC18_medicine_english(self, service):
        _mock_llm(service, [{"amount": 65, "description": "medicine", "category": "health"}])
        result = await service.parse_transactions("medicine 65")
        assert result[0]["category"] == "health"

    @pytest.mark.asyncio
    async def test_TC19_groceries(self, service):
        _mock_llm(service, [{"amount": 450, "description": "groceries", "category": "shopping"}])
        result = await service.parse_transactions("groceries 450")
        assert result[0]["amount"] == 450.0

    @pytest.mark.asyncio
    async def test_TC20_rent(self, service):
        _mock_llm(service, [{"amount": 12000, "description": "rent", "category": "housing"}])
        result = await service.parse_transactions("rent 12000")
        assert result[0]["category"] == "housing"


# ---------------------------------------------------------------------------
# 3. 多筆拆分 — 核心功能
# ---------------------------------------------------------------------------

class TestMultipleTransactions:
    @pytest.mark.asyncio
    async def test_TC21_bread_and_coffee(self, service):
        _mock_llm(service, [
            {"amount": 73, "description": "7-11麵包", "category": "food"},
            {"amount": 125, "description": "咖啡", "category": "drink"},
        ])
        result = await service.parse_transactions("7-11的麵包73，一杯咖啡125")
        assert len(result) == 2
        assert result[0]["amount"] == 73.0
        assert result[1]["amount"] == 125.0

    @pytest.mark.asyncio
    async def test_TC22_categories_correct(self, service):
        _mock_llm(service, [
            {"amount": 73, "description": "麵包", "category": "food"},
            {"amount": 125, "description": "咖啡", "category": "drink"},
        ])
        result = await service.parse_transactions("麵包73和咖啡125")
        assert result[0]["category"] == "food"
        assert result[1]["category"] == "drink"

    @pytest.mark.asyncio
    async def test_TC23_three_items(self, service):
        _mock_llm(service, [
            {"amount": 40, "description": "蛋餅", "category": "food"},
            {"amount": 55, "description": "奶茶", "category": "drink"},
            {"amount": 30, "description": "捷運", "category": "transport"},
        ])
        result = await service.parse_transactions("蛋餅40元奶茶55元捷運30元")
        assert len(result) == 3

    @pytest.mark.asyncio
    async def test_TC24_english_multi(self, service):
        _mock_llm(service, [
            {"amount": 85, "description": "sandwich", "category": "food"},
            {"amount": 60, "description": "juice", "category": "drink"},
        ])
        result = await service.parse_transactions("sandwich 85 and juice 60")
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_TC25_mixed_language_multi(self, service):
        _mock_llm(service, [
            {"amount": 73, "description": "bread", "category": "food"},
            {"amount": 125, "description": "latte", "category": "drink"},
        ])
        result = await service.parse_transactions("bread 73元 latte 125元")
        assert len(result) == 2
        assert result[0]["amount"] == 73.0

    @pytest.mark.asyncio
    async def test_TC26_amounts_correct_types(self, service):
        _mock_llm(service, [
            {"amount": 100, "description": "午餐", "category": "food"},
            {"amount": 50, "description": "飲料", "category": "drink"},
        ])
        result = await service.parse_transactions("午餐100飲料50")
        for item in result:
            assert isinstance(item["amount"], float)

    @pytest.mark.asyncio
    async def test_TC27_four_items(self, service):
        _mock_llm(service, [
            {"amount": 40, "description": "早餐", "category": "food"},
            {"amount": 28, "description": "捷運", "category": "transport"},
            {"amount": 350, "description": "晚餐", "category": "food"},
            {"amount": 55, "description": "手搖飲", "category": "drink"},
        ])
        result = await service.parse_transactions("早餐40元捷運28元晚餐350元手搖飲55元")
        assert len(result) == 4

    @pytest.mark.asyncio
    async def test_TC28_descriptions_preserved(self, service):
        _mock_llm(service, [
            {"amount": 73, "description": "7-11麵包", "category": "food"},
            {"amount": 125, "description": "拿鐵咖啡", "category": "drink"},
        ])
        result = await service.parse_transactions("7-11麵包73拿鐵咖啡125")
        assert result[0]["description"] == "7-11麵包"
        assert result[1]["description"] == "拿鐵咖啡"


# ---------------------------------------------------------------------------
# 4. 類別正規化（小寫）
# ---------------------------------------------------------------------------

class TestCategoryNormalization:
    @pytest.mark.asyncio
    async def test_TC29_uppercase_food(self, service):
        _mock_llm(service, [{"amount": 80, "description": "lunch", "category": "Food"}])
        result = await service.parse_transactions("lunch 80")
        assert result[0]["category"] == "food"

    @pytest.mark.asyncio
    async def test_TC30_uppercase_drink(self, service):
        _mock_llm(service, [{"amount": 90, "description": "coffee", "category": "Drink"}])
        result = await service.parse_transactions("coffee 90")
        assert result[0]["category"] == "drink"

    @pytest.mark.asyncio
    async def test_TC31_mixed_case(self, service):
        _mock_llm(service, [{"amount": 250, "description": "taxi", "category": "Transport"}])
        result = await service.parse_transactions("taxi 250")
        assert result[0]["category"] == "transport"

    @pytest.mark.asyncio
    async def test_TC32_all_caps(self, service):
        _mock_llm(service, [{"amount": 280, "description": "movie", "category": "ENTERTAINMENT"}])
        result = await service.parse_transactions("movie 280")
        assert result[0]["category"] == "entertainment"

    @pytest.mark.asyncio
    async def test_TC33_other_default(self, service):
        _mock_llm(service, [{"amount": 100, "description": "misc", "category": "other"}])
        result = await service.parse_transactions("misc 100")
        assert result[0]["category"] == "other"


# ---------------------------------------------------------------------------
# 5. 金額過濾（≤ 0 不新增）
# ---------------------------------------------------------------------------

class TestAmountFiltering:
    @pytest.mark.asyncio
    async def test_TC34_zero_amount_filtered(self, service):
        _mock_llm(service, [{"amount": 0, "description": "free item", "category": "other"}])
        result = await service.parse_transactions("free item")
        assert result == []

    @pytest.mark.asyncio
    async def test_TC35_negative_filtered(self, service):
        _mock_llm(service, [{"amount": -50, "description": "refund", "category": "other"}])
        result = await service.parse_transactions("refund -50")
        assert result == []

    @pytest.mark.asyncio
    async def test_TC36_mixed_valid_zero(self, service):
        _mock_llm(service, [
            {"amount": 100, "description": "lunch", "category": "food"},
            {"amount": 0, "description": "free drink", "category": "drink"},
        ])
        result = await service.parse_transactions("lunch 100 free drink")
        assert len(result) == 1
        assert result[0]["amount"] == 100.0

    @pytest.mark.asyncio
    async def test_TC37_all_zero_returns_empty(self, service):
        _mock_llm(service, [
            {"amount": 0, "description": "a", "category": "other"},
            {"amount": 0, "description": "b", "category": "other"},
        ])
        result = await service.parse_transactions("no amount text")
        assert result == []


# ---------------------------------------------------------------------------
# 6. 容錯 — LLM 回傳異常格式
# ---------------------------------------------------------------------------

class TestFallback:
    @pytest.mark.asyncio
    async def test_TC38_invalid_json_fallback(self, service):
        choice = MagicMock()
        choice.message.content = "this is not json"
        service.client.chat.completions.create.return_value = MagicMock(choices=[choice])
        result = await service.parse_transactions("早餐40元")
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["amount"] == 0.0
        assert result[0]["category"] == "other"

    @pytest.mark.asyncio
    async def test_TC39_single_dict_wrapped_in_list(self, service):
        # LLM returns single dict instead of array — should still work
        _mock_llm(service, {"amount": 80, "description": "lunch", "category": "food"})
        result = await service.parse_transactions("lunch 80")
        assert len(result) == 1
        assert result[0]["amount"] == 80.0

    @pytest.mark.asyncio
    async def test_TC40_missing_amount_key(self, service):
        _mock_llm(service, [{"description": "lunch", "category": "food"}])
        result = await service.parse_transactions("lunch")
        # amount defaults to 0, gets filtered out
        assert result == []

    @pytest.mark.asyncio
    async def test_TC41_missing_category_defaults_other(self, service):
        _mock_llm(service, [{"amount": 80, "description": "lunch"}])
        result = await service.parse_transactions("lunch 80")
        assert result[0]["category"] == "other"

    @pytest.mark.asyncio
    async def test_TC42_missing_description_uses_text(self, service):
        _mock_llm(service, [{"amount": 80}])
        result = await service.parse_transactions("lunch 80")
        assert result[0]["amount"] == 80.0

    @pytest.mark.asyncio
    async def test_TC43_empty_array_from_llm(self, service):
        _mock_llm(service, [])
        result = await service.parse_transactions("lunch 80")
        assert result == []

    @pytest.mark.asyncio
    async def test_TC44_llm_exception_returns_fallback(self, service):
        service.client.chat.completions.create.side_effect = Exception("API error")
        result = await service.parse_transactions("lunch 80")
        assert isinstance(result, list)
        assert result[0]["amount"] == 0.0

    @pytest.mark.asyncio
    async def test_TC45_amount_as_string_converted(self, service):
        _mock_llm(service, [{"amount": "99", "description": "snack", "category": "food"}])
        result = await service.parse_transactions("snack 99")
        assert result[0]["amount"] == 99.0

    @pytest.mark.asyncio
    async def test_TC46_extra_fields_ignored(self, service):
        _mock_llm(service, [{"amount": 80, "description": "lunch", "category": "food", "note": "extra"}])
        result = await service.parse_transactions("lunch 80")
        assert result[0]["amount"] == 80.0


# ---------------------------------------------------------------------------
# 7. 金額型別轉換
# ---------------------------------------------------------------------------

class TestAmountConversion:
    @pytest.mark.asyncio
    async def test_TC47_integer_amount(self, service):
        _mock_llm(service, [{"amount": 100, "description": "lunch", "category": "food"}])
        result = await service.parse_transactions("lunch 100")
        assert result[0]["amount"] == 100.0
        assert isinstance(result[0]["amount"], float)

    @pytest.mark.asyncio
    async def test_TC48_float_amount(self, service):
        _mock_llm(service, [{"amount": 99.5, "description": "snack", "category": "food"}])
        result = await service.parse_transactions("snack 99.5")
        assert result[0]["amount"] == 99.5

    @pytest.mark.asyncio
    async def test_TC49_large_amount(self, service):
        _mock_llm(service, [{"amount": 15000, "description": "rent", "category": "housing"}])
        result = await service.parse_transactions("rent 15000")
        assert result[0]["amount"] == 15000.0

    @pytest.mark.asyncio
    async def test_TC50_small_amount(self, service):
        _mock_llm(service, [{"amount": 5, "description": "gum", "category": "food"}])
        result = await service.parse_transactions("gum 5")
        assert result[0]["amount"] == 5.0


# ---------------------------------------------------------------------------
# 8. 各類別全覆蓋
# ---------------------------------------------------------------------------

class TestAllCategories:
    @pytest.mark.asyncio
    async def test_TC51_food(self, service):
        _mock_llm(service, [{"amount": 100, "description": "飯", "category": "food"}])
        result = await service.parse_transactions("飯100")
        assert result[0]["category"] == "food"

    @pytest.mark.asyncio
    async def test_TC52_drink(self, service):
        _mock_llm(service, [{"amount": 55, "description": "茶", "category": "drink"}])
        result = await service.parse_transactions("茶55")
        assert result[0]["category"] == "drink"

    @pytest.mark.asyncio
    async def test_TC53_transport(self, service):
        _mock_llm(service, [{"amount": 28, "description": "捷運", "category": "transport"}])
        result = await service.parse_transactions("捷運28")
        assert result[0]["category"] == "transport"

    @pytest.mark.asyncio
    async def test_TC54_shopping(self, service):
        _mock_llm(service, [{"amount": 599, "description": "衣服", "category": "shopping"}])
        result = await service.parse_transactions("衣服599")
        assert result[0]["category"] == "shopping"

    @pytest.mark.asyncio
    async def test_TC55_housing(self, service):
        _mock_llm(service, [{"amount": 12000, "description": "房租", "category": "housing"}])
        result = await service.parse_transactions("房租12000")
        assert result[0]["category"] == "housing"

    @pytest.mark.asyncio
    async def test_TC56_health(self, service):
        _mock_llm(service, [{"amount": 300, "description": "看診", "category": "health"}])
        result = await service.parse_transactions("看診300")
        assert result[0]["category"] == "health"

    @pytest.mark.asyncio
    async def test_TC57_entertainment(self, service):
        _mock_llm(service, [{"amount": 330, "description": "Netflix", "category": "entertainment"}])
        result = await service.parse_transactions("Netflix330")
        assert result[0]["category"] == "entertainment"

    @pytest.mark.asyncio
    async def test_TC58_other(self, service):
        _mock_llm(service, [{"amount": 50, "description": "雜費", "category": "other"}])
        result = await service.parse_transactions("雜費50")
        assert result[0]["category"] == "other"


# ---------------------------------------------------------------------------
# 9. 日常語音輸入語境模擬
# ---------------------------------------------------------------------------

class TestVoiceInputSimulation:
    @pytest.mark.asyncio
    async def test_TC59_casual_chinese(self, service):
        _mock_llm(service, [{"amount": 120, "description": "今天午餐便當", "category": "food"}])
        result = await service.parse_transactions("今天中午吃了便當一百二十元")
        assert result[0]["amount"] == 120.0

    @pytest.mark.asyncio
    async def test_TC60_family_mart_coffee(self, service):
        _mock_llm(service, [{"amount": 45, "description": "全家咖啡", "category": "drink"}])
        result = await service.parse_transactions("全家咖啡四十五元")
        assert result[0]["category"] == "drink"

    @pytest.mark.asyncio
    async def test_TC61_7eleven_bread(self, service):
        _mock_llm(service, [{"amount": 73, "description": "7-11麵包", "category": "food"}])
        result = await service.parse_transactions("7-11的麵包七十三元")
        assert result[0]["amount"] == 73.0

    @pytest.mark.asyncio
    async def test_TC62_uber_eats(self, service):
        _mock_llm(service, [{"amount": 380, "description": "Uber Eats外送", "category": "food"}])
        result = await service.parse_transactions("叫了Uber Eats三百八十元")
        assert result[0]["amount"] == 380.0

    @pytest.mark.asyncio
    async def test_TC63_english_casual(self, service):
        _mock_llm(service, [{"amount": 85, "description": "sandwich", "category": "food"}])
        result = await service.parse_transactions("I had a sandwich for eighty five dollars")
        assert result[0]["amount"] == 85.0

    @pytest.mark.asyncio
    async def test_TC64_starbucks_english(self, service):
        _mock_llm(service, [{"amount": 160, "description": "Starbucks latte", "category": "drink"}])
        result = await service.parse_transactions("Starbucks latte one sixty")
        assert result[0]["category"] == "drink"

    @pytest.mark.asyncio
    async def test_TC65_multi_voice_realistic(self, service):
        _mock_llm(service, [
            {"amount": 73, "description": "7-11麵包", "category": "food"},
            {"amount": 125, "description": "咖啡", "category": "drink"},
        ])
        result = await service.parse_transactions("7-11的麵包加73名字還有一杯咖啡是125")
        assert len(result) == 2
        assert result[0]["amount"] == 73.0
        assert result[1]["amount"] == 125.0
        assert result[0]["category"] == "food"
        assert result[1]["category"] == "drink"

    @pytest.mark.asyncio
    async def test_TC66_numbers_in_merchant_name(self, service):
        _mock_llm(service, [{"amount": 35, "description": "7-11零食", "category": "food"}])
        result = await service.parse_transactions("7-11零食35元")
        assert result[0]["amount"] == 35.0

    @pytest.mark.asyncio
    async def test_TC67_gym_membership(self, service):
        _mock_llm(service, [{"amount": 999, "description": "健身房月費", "category": "health"}])
        result = await service.parse_transactions("健身房月費999元")
        assert result[0]["amount"] == 999.0

    @pytest.mark.asyncio
    async def test_TC68_phone_bill(self, service):
        _mock_llm(service, [{"amount": 699, "description": "電話費", "category": "other"}])
        result = await service.parse_transactions("電話費699元")
        assert result[0]["amount"] == 699.0

    @pytest.mark.asyncio
    async def test_TC69_electricity_bill(self, service):
        _mock_llm(service, [{"amount": 2500, "description": "水電費", "category": "housing"}])
        result = await service.parse_transactions("水電費2500元")
        assert result[0]["category"] == "housing"

    @pytest.mark.asyncio
    async def test_TC70_mrt_pass(self, service):
        _mock_llm(service, [{"amount": 1280, "description": "捷運月票", "category": "transport"}])
        result = await service.parse_transactions("捷運月票1280元")
        assert result[0]["amount"] == 1280.0
