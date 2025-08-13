import pandas as pd
from .schemas.cost_center import CostCenterSchema

class CostCenters:
    """
    Handles all cost center related operations in Meta4
    """
    def __init__(self, meta4):
        self.meta4 = meta4
        schema_fields = CostCenterSchema.model_fields
        column_names = [field.alias or name for name, field in schema_fields.items()]
        self.batch_df = pd.DataFrame(columns=column_names)

    def create(self, df: pd.DataFrame) -> str:
        """
        Export cost center data to CSV with validation.

        Args:
            df (pd.DataFrame): DataFrame containing cost center data to validate and export

        Returns:
            str: Path to the generated CSV file

        Raises:
            Exception: If validation or export fails
        """
        try:
            # Set movement_type to ALTA for all records
            df['movement_type'] = '-36'
            valid_df = self.meta4.validate(df=df,schema=CostCenterSchema)
            self.batch_df = pd.concat([self.batch_df, valid_df], ignore_index=True)
            return {"success": True, "message": "Cost centers created successfully"}
        except Exception as e:
            raise Exception(f"Failed to export cost centers: {e}")

    def update(self, df: pd.DataFrame) -> str:

        try:
            # Set movement_type to MODIFICACION for all records
            df['movement_type'] = '-36'
            valid_df = self.meta4.validate(df=df,schema=CostCenterSchema)
            self.batch_df = pd.concat([self.batch_df, valid_df], ignore_index=True)
            return {"success": True, "message": "Cost centers updated successfully"}
        except Exception as e:
            raise Exception(f"Failed to update cost centers: {e}")

    def delete(self, df: pd.DataFrame) -> str:

        try:
            # Set movement_type to BAJA for all records
            df['movement_type'] = '-37'
            valid_df = self.meta4.validate(df=df,schema=CostCenterSchema)
            self.batch_df = pd.concat([self.batch_df, valid_df], ignore_index=True)
            return {"success": True, "message": "Cost centers deleted successfully"}
        except Exception as e:
            raise Exception(f"Failed to delete cost centers: {e}")

    def export(self) -> str:
        """
        Export cost center data to CSV with validation.
        """
        return self.meta4.export(df=self.batch_df, filename="cost_center_import.csv")

    def get_batch_df(self) -> pd.DataFrame:
        """
        Get the current batch DataFrame containing all validated cost center records.
        """
        return self.batch_df

    def clear_batch_df(self):
        """
        Clear the batch DataFrame.
        """
        self.batch_df = pd.DataFrame()
