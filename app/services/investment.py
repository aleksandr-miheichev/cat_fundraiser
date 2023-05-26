from app.models.base import FinancialTransactionBase


def run_investment_process(
        target: FinancialTransactionBase,
        sources: list[FinancialTransactionBase]
) -> list[FinancialTransactionBase]:
    modified_entities = []
    for source in sources:
        transfer_volume = min(
            target.full_amount - target.invested_amount,
            source.full_amount - source.invested_amount
        )
        for entity in [target, source]:
            entity.invested_amount += transfer_volume
            if entity.full_amount == entity.invested_amount:
                entity.mark_as_fully_invested()
        modified_entities.append(source)
        if target.fully_invested:
            break
    return modified_entities
