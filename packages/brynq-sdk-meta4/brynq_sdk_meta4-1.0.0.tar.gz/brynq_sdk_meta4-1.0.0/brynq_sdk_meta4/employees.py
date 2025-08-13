import pandas as pd
from .schemas.employee import EmployeeSchema
import os

class Employees:
    """
    Handles all employee related operations in Meta4
    """
    def __init__(self, meta4):
        self.meta4 = meta4
        # Initialize batch_df with EmployeeSchema columns
        schema_fields = EmployeeSchema.model_fields
        column_names = [field.alias or name for name, field in schema_fields.items()]
        self.batch_df = pd.DataFrame(columns=column_names)

    def create(self, df: pd.DataFrame) -> str:
        """
        Create new employees (ALTA movement type).

        Args:
            df (pd.DataFrame): DataFrame containing employee data for creation

        Returns:
            str: Path to the generated CSV file

        Raises:
            Exception: If validation or export fails
        """
        try:
            # Set movement_type to ALTA for all records
            df['movement_type'] = '1'
            validated_df = self.meta4.validate(df=df, schema=EmployeeSchema)

            # Append validated DataFrame to batch_df
            self.batch_df = pd.concat([self.batch_df, validated_df], ignore_index=True)

            return {"success": True, "message": "Employees created successfully"}
        except Exception as e:
            raise Exception(f"Failed to create employees: {e}")

    def update(self, df: pd.DataFrame) -> str:
        """
        Update existing employees (MODIFICACION movement type).

        Args:
            df (pd.DataFrame): DataFrame containing employee data for update

        Returns:
            str: Path to the generated CSV file

        Raises:
            Exception: If validation or export fails
        """
        try:
            # Set movement_type to MODIFICACION for all records
            df['movement_type'] = '3'
            validated_df = self.meta4.validate(df=df, schema=EmployeeSchema)

            # Append validated DataFrame to batch_df
            self.batch_df = pd.concat([self.batch_df, validated_df], ignore_index=True)

            return {"success": True, "message": "Employees updated successfully"}
        except Exception as e:
            raise Exception(f"Failed to update employees: {e}")

    def delete(self, df: pd.DataFrame) -> str:
        """
        Delete/terminate employees (BAJA movement type).

        Args:
            df (pd.DataFrame): DataFrame containing employee data for termination

        Returns:
            str: Path to the generated CSV file

        Raises:
            Exception: If validation or export fails
        """
        try:
            # Set movement_type to BAJA for all records
            df['movement_type'] = '2'
            validated_df = self.meta4.validate(df=df, schema=EmployeeSchema)

            # Append validated DataFrame to batch_df
            self.batch_df = pd.concat([self.batch_df, validated_df], ignore_index=True)

            return {"success": True, "message": "Employees deleted successfully"}
        except Exception as e:
            raise Exception(f"Failed to delete employees: {e}")

    def export(self) -> str:
        """
        Export employee data to CSV with validation (generic export).

        Args:
            df (pd.DataFrame): DataFrame containing employee data to validate and export

        Returns:
            str: Path to the generated CSV file

        Raises:
            Exception: If validation or export fails
        """
        return self.meta4.export(df=self.batch_df, filename="employee_import.csv")

    def get_batch_df(self) -> pd.DataFrame:
        """
        Get the current batch DataFrame containing all validated employee records.

        Returns:
            pd.DataFrame: The batch DataFrame with all validated records
        """
        return self.batch_df

    def clear_batch_df(self):
        """
        Clear the batch DataFrame.
        """
        schema_fields = EmployeeSchema.model_fields
        column_names = [field.alias or name for name, field in schema_fields.items()]
        self.batch_df = pd.DataFrame(columns=column_names)
