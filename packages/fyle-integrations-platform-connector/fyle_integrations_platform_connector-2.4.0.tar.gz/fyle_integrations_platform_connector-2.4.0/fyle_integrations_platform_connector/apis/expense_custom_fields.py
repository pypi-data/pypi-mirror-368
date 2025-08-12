from datetime import datetime, timezone
import logging
from fyle_accounting_mappings.models import ExpenseAttributesDeletionCache
from .base import Base

logger = logging.getLogger(__name__)
logger.level = logging.INFO


class ExpenseCustomFields(Base):
    """Class for Expense Custom Fields APIs."""

    def sync(self):
        """
        Syncs the latest API data to DB.
        """
        try:
            query_params = {'order': 'updated_at.desc', 'is_custom': 'eq.true', 'type': 'eq.SELECT', 'is_enabled': 'eq.true'}
            generator = self.connection.list_all(query_params)
            expense_attributes_deletion_cache, _ = ExpenseAttributesDeletionCache.objects.get_or_create(workspace_id=self.workspace_id)
            expense_field_list = []

            for items in generator:
                for row in items['data']:
                    if self.attribute_is_valid(row):
                        attributes = []
                        count = 1
                        attribute_type = row['field_name'].upper().replace(' ', '_')
                        expense_field_list.append({'attribute_type': attribute_type, 'value_list': row['options']})
                        for option in row['options']:
                            attributes.append({
                                'attribute_type': attribute_type,
                                'display_name': row['field_name'],
                                'value': option,
                                'active': True,
                                'source_id': 'expense_custom_field.{}.{}'.format(row['field_name'].lower(), count),
                                'detail': {
                                    'custom_field_id': row['id'],
                                    'placeholder': row['placeholder'],
                                    'is_mandatory': row['is_mandatory'],
                                    'is_dependent': False
                                }
                            })
                            count = count + 1
                        self.attribute_type = attribute_type
                        self.bulk_create_or_update_expense_attributes(attributes, True)
            expense_attributes_deletion_cache.custom_field_list = expense_field_list
            expense_attributes_deletion_cache.updated_at = datetime.now(timezone.utc)
            expense_attributes_deletion_cache.save(update_fields=['custom_field_list', 'updated_at'])

            self.bulk_update_deleted_expense_attributes()

        except Exception as e:
            logger.exception(e)
            expense_attributes_deletion_cache = ExpenseAttributesDeletionCache.objects.get(workspace_id=self.workspace_id)
            expense_attributes_deletion_cache.custom_field_list = []
            expense_attributes_deletion_cache.save(update_fields=['custom_field_list', 'updated_at'])

    def list_all(self, query_params=None):
        """
        List all the custom fields
        """
        if not query_params:
            query_params = {'order': 'updated_at.desc', 'is_custom': 'eq.true', 'is_enabled': 'eq.true'}
        generator = self.connection.list_all(query_params)
        custom_fields = []

        for items in generator:
            custom_fields = items['data']

        return custom_fields

    def get_count(self, field_name: str) -> int:
        """
        Get count of attributes
        """
        query_params = {'order': 'updated_at.desc', 'limit': 1, 'offset': 0, 'is_enabled': 'eq.true', 'field_name': 'eq.{}'.format(field_name)}
        custom_field = self.connection.list_all(query_params)
        count = 0

        if custom_field:
            count = len(custom_field[0]['options'])

        return count
