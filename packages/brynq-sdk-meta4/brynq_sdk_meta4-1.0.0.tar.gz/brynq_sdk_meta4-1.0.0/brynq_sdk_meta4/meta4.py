import os
import csv
from typing import List, Optional, Literal
import pandas as pd
from brynq_sdk_ftp import SFTP
from brynq_sdk_brynq import BrynQ
from brynq_sdk_functions import Functions
import pydantic
from .employees import Employees
from .cost_centers import CostCenters
from .jobs import Jobs

class Meta4(BrynQ):
    """
    Meta4 HR system client for BrynQ integrations.
    Focuses on schema validation and CSV export functionality.
    """

    def __init__(self, system_type: Optional[Literal['source', 'target']] = None, output_path:str="outputs", debug=False):
        """
        Initialize Meta4 client.
        """
        super().__init__()
        self.debug = debug

        self.output_path = output_path
        # SFTP client as a composition attribute
        self.sftp = SFTP()
        credentials = self.interfaces.credentials.get(system="meta-4", system_type=system_type)
        credentials = credentials.get('data', credentials)

        self.sftp._set_credentials(credentials)

        # Initialize entity classes
        self.employees = Employees(self)
        self.cost_centers = CostCenters(self)
        self.jobs = Jobs(self)

    def validate(self, df: pd.DataFrame, schema: pydantic.BaseModel) -> pd.DataFrame:
        """
        Validate data against schema and return validated DataFrame.
        """
        try:
                data_list = df.to_dict('records')

                valid_data = []
                invalid_data = []
                for data_item in data_list:
                    try:
                        validated_item = schema(**data_item)
                        valid_data.append(validated_item.model_dump(by_alias=True, mode="json"))
                    except Exception as validation_error:
                        invalid_data.append({
                            'data': data_item,
                            'error': str(validation_error)
                        })

                # Print invalid data count
                if invalid_data:
                    print(f" {len(invalid_data)} lines of {schema.__name__} data validation failed:")

                # Convert to DataFrame
                df = pd.DataFrame(valid_data)
                return df
        except Exception as e:
            raise Exception(f"Failed to validate data: {e}")

    def export(
      self,
        df: pd.DataFrame,
        filename: str
    ) -> dict:
        """
        Validate data against schema and export to CSV file.

        Args:
            schema_class: Pydantic schema class (e.g., EmployeeSchema, CostCenterSchema, JobSchema)
            df: DataFrame containing data to validate and export

        Returns:
            dict: Dictionary containing filepath, valid count, invalid count, and invalid data list

        Raises:
            ValidationError: If data validation fails
            Exception: If file writing fails
        """
        try:
            os.makedirs(self.output_path, exist_ok=True)


            # Export to CSV
            df.to_csv(
                f"{self.output_path}/{filename}",
                index=False,
                encoding="utf-8-sig",
                sep=";",
                quotechar='"',
                quoting=csv.QUOTE_MINIMAL
            )
            return {
                'filepath': f"{self.output_path}/{filename}",
            }

        except Exception as e:
            raise Exception(f"Failed to export data for {filename}: {e}")

    def upload(self, upload_path: str="/") -> List[str]:
        """
        Upload all CSV files from the output directory to the specified remote path.

        This method scans the output directory for CSV files and uploads each one
        to the remote server via SFTP. Files are uploaded to different directories
        based on their filename:
        - employee_import.csv -> ENTRADA folder
        - Other files -> SALIDA folder

        Args:
            upload_path (str): Remote directory path where CSV files will be uploaded.
                             Must be a valid directory path on the remote server.

        Returns:
            List[str]: List of successfully uploaded remote file paths.
                      Each path includes the remote directory and filename.
        Raises:
            Exception: For any other upload-related errors.
        """
        try:

            # Get list of CSV files in output directory
            csv_files = [f for f in os.listdir(self.output_path) if f.endswith('.csv')]
            uploaded_files = []

            # Upload each CSV file
            for csv_file in csv_files:
                try:
                    local_filepath = os.path.join(self.output_path, csv_file)

                    # Determine upload directory based on filename
                    if csv_file == "employee_import.csv":
                        upload_dir = "ENTRADA/EMPLEADOS"
                    else:
                        upload_dir = "SALIDA"

                    remote_filepath = os.path.join(upload_path, upload_dir, csv_file).replace('\\', '/')

                    # Upload file using SFTP attribute
                    self.sftp.upload_file(
                        local_filepath=local_filepath,
                        remote_filepath=remote_filepath
                    )

                    uploaded_files.append(remote_filepath)

                except Exception as file_error:
                    print(f"Failed to upload {csv_file}: {file_error}")
                    # Continue with other files even if one fails
                    continue

            if not uploaded_files:
                raise Exception("No files were successfully uploaded")

            return f"The files successfully uploaded: {', '.join(uploaded_files)}"

        except Exception as e:
            raise Exception(f"Upload failed with unexpected error: {e}")
