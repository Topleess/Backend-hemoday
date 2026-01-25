import asyncio
from tortoise import Tortoise
from app.core.config import TORTOISE_ORM
from app.models.analysis_template import AnalysisTemplate, AnalysisTemplateItem

async def seed():
    await Tortoise.init(config=TORTOISE_ORM)
    
    # CBC
    cbc_id = "tmpl_cbc_01"
    cbc = await AnalysisTemplate.get_or_none(id=cbc_id)
    if not cbc:
        print(f"Creating {cbc_id}...")
        cbc = await AnalysisTemplate.create(
            id=cbc_id,
            name="Общий анализ крови",
            is_default=True,
            family_id=None
        )
        
        items = [
            ("tmpl_item_hb_01", "Гемоглобин", "g/l"),
            ("tmpl_item_ery_01", "Эритроциты", "×10¹²/л"),
            ("tmpl_item_leu_01", "Лейкоциты", "×10⁹/л"),
            ("tmpl_item_plt_01", "Тромбоциты", "×10⁹/л"),
        ]
        
        for i_id, i_name, i_unit in items:
            await AnalysisTemplateItem.create(
                id=i_id,
                template_id=cbc.id,
                name=i_name,
                unit=i_unit,
                family_id=None
            )
    else:
        print(f"{cbc_id} already exists")

    # Biochem
    bio_id = "tmpl_biochem_01"
    bio = await AnalysisTemplate.get_or_none(id=bio_id)
    if not bio:
        print(f"Creating {bio_id}...")
        bio = await AnalysisTemplate.create(
            id=bio_id,
            name="Биохимический анализ",
            is_default=True,
            family_id=None
        )
        
        items = [
            ("tmpl_item_fer_01", "Ферритин", "нг/мл"),
            ("tmpl_item_alt_01", "АЛТ", "Ед/л"),
            ("tmpl_item_ast_01", "АСТ", "Ед/л"),
            ("tmpl_item_bil_01", "Билирубин общий", "мкмоль/л"),
        ]
        
        for i_id, i_name, i_unit in items:
            await AnalysisTemplateItem.create(
                id=i_id,
                template_id=bio.id,
                name=i_name,
                unit=i_unit,
                family_id=None
            )
    else:
        print(f"{bio_id} already exists")

    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(seed())
