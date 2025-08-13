import pandas as pd
from .schemas.job import JobSchema

class Jobs:
    """
    Handles all job related operations in Meta4
    """
    def __init__(self, meta4):
        self.meta4 = meta4
        # Initialize batch_df with JobSchema columns
        schema_fields = JobSchema.model_fields
        column_names = [field.alias or name for name, field in schema_fields.items()]
        self.batch_df = pd.DataFrame(columns=column_names)

    def create(self, df: pd.DataFrame) -> str:
        """
        Create new jobs (CREATE movement type -28).

        Args:
            df (pd.DataFrame): DataFrame containing job data for creation

        Returns:
            str: Success message

        Raises:
            Exception: If validation fails
        """
        try:
            # Set movement_type to CREATE for all records
            df['movement_type'] = '-28'
            validated_df = self.meta4.validate(df=df, schema=JobSchema)

            # Append validated DataFrame to batch_df
            self.batch_df = pd.concat([self.batch_df, validated_df], ignore_index=True)

            return {"success": True, "message": "Jobs created successfully"}
        except Exception as e:
            raise Exception(f"Failed to create jobs: {e}")

    def update(self, df: pd.DataFrame) -> str:
        """
        Update existing jobs (UPDATE movement type -29).

        Args:
            df (pd.DataFrame): DataFrame containing job data for update

        Returns:
            str: Success message

        Raises:
            Exception: If validation fails
        """
        try:
            # Set movement_type to UPDATE for all records
            df['movement_type'] = '-29'
            validated_df = self.meta4.validate(df=df, schema=JobSchema)

            # Append validated DataFrame to batch_df
            self.batch_df = pd.concat([self.batch_df, validated_df], ignore_index=True)

            return {"success": True, "message": "Jobs updated successfully"}
        except Exception as e:
            raise Exception(f"Failed to update jobs: {e}")

    def delete(self, df: pd.DataFrame) -> str:
        """
        Delete jobs (DELETE movement type -29).

        Args:
            df (pd.DataFrame): DataFrame containing job data for deletion

        Returns:
            str: Success message

        Raises:
            Exception: If validation fails
        """
        try:
            # Set movement_type to DELETE for all records
            df['movement_type'] = '-29'
            validated_df = self.meta4.validate(df=df, schema=JobSchema)

            # Append validated DataFrame to batch_df
            self.batch_df = pd.concat([self.batch_df, validated_df], ignore_index=True)

            return {"success": True, "message": "Jobs deleted successfully"}
        except Exception as e:
            raise Exception(f"Failed to delete jobs: {e}")

    def export(self) -> str:
        """
        Export job data to CSV with validation (generic export).

        Args:
            df (pd.DataFrame): DataFrame containing job data to validate and export

        Returns:
            str: Path to the generated CSV file

        Raises:
            Exception: If validation or export fails
        """
        return self.meta4.export(df=self.batch_df, filename="job_import.csv")

    def get_batch_df(self) -> pd.DataFrame:
        """
        Get the current batch DataFrame containing all validated job records.

        Returns:
            pd.DataFrame: The batch DataFrame with all validated records
        """
        return self.batch_df

    def clear_batch_df(self):
        """
        Clear the batch DataFrame.
        """
        schema_fields = JobSchema.model_fields
        column_names = [field.alias or name for name, field in schema_fields.items()]
        self.batch_df = pd.DataFrame(columns=column_names)
