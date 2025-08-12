import logging
from datetime import datetime, timezone
from fyle_accounting_mappings.models import ExpenseAttributesDeletionCache
from .base import Base

logger = logging.getLogger(__name__)
logger.level = logging.INFO


class CostCenters(Base):
    """Class for Cost Centers APIs."""

    def __init__(self):
        Base.__init__(self, attribute_type='COST_CENTER', query_params={'is_enabled': 'eq.true'})

    def sync(self, sync_after: datetime = None):
        """
        Syncs the latest API data to DB.
        """
        try:
            expense_attributes_deletion_cache, _ = ExpenseAttributesDeletionCache.objects.get_or_create(workspace_id=self.workspace_id)
            generator = self.get_all_generator()

            for items in generator:
                cost_center_attributes = []
                for cost_center in items['data']:
                    expense_attributes_deletion_cache.cost_center_ids.append(cost_center['id'])

                    if self.attribute_is_valid(cost_center):
                        cost_center_attributes.append({
                            'attribute_type': self.attribute_type,
                            'display_name': self.attribute_type.replace('_', ' ').title(),
                            'value': cost_center['name'],
                            'active': cost_center['is_enabled'],
                            'source_id': cost_center['id']
                        })

                expense_attributes_deletion_cache.updated_at = datetime.now(timezone.utc)
                expense_attributes_deletion_cache.save(update_fields=['cost_center_ids', 'updated_at'])
                self.bulk_create_or_update_expense_attributes(cost_center_attributes, True)

            self.bulk_update_deleted_expense_attributes()

        except Exception as e:
            logger.exception(e)
            expense_attributes_deletion_cache = ExpenseAttributesDeletionCache.objects.get(workspace_id=self.workspace_id)
            expense_attributes_deletion_cache.cost_center_ids = []
            expense_attributes_deletion_cache.updated_at = datetime.now(timezone.utc)
            expense_attributes_deletion_cache.save(update_fields=['cost_center_ids', 'updated_at'])
