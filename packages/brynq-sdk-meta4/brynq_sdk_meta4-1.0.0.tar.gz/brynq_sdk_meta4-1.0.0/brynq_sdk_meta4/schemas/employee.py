from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, Literal
from datetime import datetime
from .reference_enums import (
    MovementType,
    DocumentType,
    GenderType,
    MaritalStatusType,
    StreetType,
    HoursType,
    PartTimeType,
    SSNumberType,
    YesNoType,
    SalaryType,
    AdjustmentType,
    PaymentType,
    IRPFType,
    IRPFStatusType,
    DisabilityHRType,
    ManagementType,
    PerceptionKeyType,
    ReductionReasonType,
    TerminationReasonType,
    UnemploymentCauseType,
    ContractType,
    LaborRelationshipType,
    SubstitutionCauseType
)


class EmployeeSchema(BaseModel):
    """
    Pydantic schema for Meta4 Employee data.
    Based on EQU_Interfaz_Empleados v.0 specification.
    """
    # Movement and Dates
    movement_type: MovementType = Field(description="Tipo de movimiento", example=MovementType.ALTA, alias="TIPO DE MOVIMIENTO")
    effective_date: datetime = Field(description="Fecha efectividad", example="2024-01-01", alias="FECHA EFECTIVIDAD")
    termination_date: Optional[datetime] = Field(None, description="Fecha de baja", example="2024-12-31", alias="FECHA DE BAJA")
    termination_reason: Optional[TerminationReasonType] = Field(None, description="Motivo de baja", example=TerminationReasonType.MOTIVOS_ECONOMICOS, alias="MOTIVO DE BAJA")
    unemployment_cause: Optional[UnemploymentCauseType] = Field(None, description="Causa desempleo", example=UnemploymentCauseType.WORKER_DISMISSAL, alias="CAUSA DESEMPLEO")
    vacation_end_date: Optional[datetime] = Field(None, description="Fecha fin vacaciones", example="2024-08-31", alias="FECHA FIN VACACIONES")

    # Personal Information
    person_id: Optional[str] = Field(None, description="ID Persona", example="EMP001", alias="ID PERSONA")
    first_surname: Optional[str] = Field(None, description="Apellido primero", example="García", alias="APELLIDO PRIMERO")
    second_surname: Optional[str] = Field(None, description="Apellido segundo", example="López", alias="APELLIDO SEGUNDO")
    employee_name: Optional[str] = Field(None, description="Nombre empleado", example="Juan Carlos", alias="NOMBRE EMPLEADO")
    document_type: Optional[DocumentType] = Field(None, description="Tipo documento", example=DocumentType.DNI, alias="TIPO DOCUMENTO")
    document_number: Optional[str] = Field(None, description="Número documento", example="12345678A", alias="NÚM. DOCUMENTO")
    document_country: Optional[str] = Field(None, description="País emisor documento", example="724", alias="PAÍS EMISOR DOCUMENTO")
    birth_date: Optional[datetime] = Field(None, description="Fecha de nacimiento", example="1985-03-15", alias="FECHA DE NACIMIENTO")
    nationality: Optional[str] = Field(None, description="Nacionalidad", example="724", alias="NACIONALIDAD")
    birth_country: Optional[str] = Field(None, description="País nacimiento", example="724", alias="PAÍS NACIMIENTO")
    birth_province: Optional[str] = Field(None, description="Provincia nacimiento", example="", alias="PROVINCIA NACIMIENTO")
    birth_community: Optional[str] = Field(None, description="Comunidad nacimiento", example="", alias="COMUNIDAD NACIMIENTO")
    gender: Optional[GenderType] = Field(None, description="Sexo", example=GenderType.MALE, alias="SEXO")
    marital_status: Optional[MaritalStatusType] = Field(None, description="Estado civil", example=MaritalStatusType.SINGLE, alias="ESTADO CIVIL")
    phone: Optional[str] = Field(None, description="Teléfono", example="912345678", alias="TELÉFONO")
    mobile_phone: Optional[str] = Field(None, description="Teléfono móvil", example="612345678", alias="TELEF. MÓVIL")
    email: Optional[str] = Field(None, description="Correo electrónico", example="juan.garcia@empresa.com", alias="CORREO ELECTRÓNICO")

    # Address Information
    location_type: Optional[Literal["1"]] = Field(None, description="Tipo localización", example="1", alias="TIPO LOCALIZACIÓN")
    street_type: Optional[StreetType] = Field(None, description="Tipo vía", example=StreetType.CALLE, alias="TIPO VÍA")
    send_mail: Optional[Literal["0"]] = Field(None, description="Enviar correo", example="0", alias="ENVIAR CORREO")
    employee_address: Optional[str] = Field(None, description="Dirección del empleado", example="Calle Mayor", alias="DIRECCIÓN DEL EMPLEADO")
    street_number: Optional[int] = Field(None, description="Número", example=123, alias="NÚMERO")
    building: Optional[str] = Field(None, description="Bloque", example="A", alias="BLOQUE")
    staircase: Optional[str] = Field(None, description="Escalera", example="1", alias="ESCALERA")
    floor: Optional[str] = Field(None, description="Piso", example="2", alias="PISO")
    door: Optional[str] = Field(None, description="Puerta", example="A", alias="PUERTA")
    country: Optional[str] = Field(None, description="País", example="", alias="PAÍS")
    city: Optional[str] = Field(None, description="Población", example="", alias="POBLACIÓN")
    province: Optional[str] = Field(None, description="Provincia", example="", alias="PROVINCIA")
    community: Optional[str] = Field(None, description="Comunidad", example="", alias="COMUNIDAD")
    postal_code: Optional[str] = Field(None, description="Código postal", example="28001", alias="CÓDIGO POSTAL")

    # Employment Information
    company: Optional[str] = Field(None, description="Empresa", example="EMPRESA001", alias="EMPRESA")
    job: Optional[str] = Field(None, description="Puesto", example="ANALISTA", alias="PUESTO")
    position: Optional[str] = Field(None, description="Posición", example="", alias="POSICION")
    organizational_unit: Optional[str] = Field(None, description="Unidad organizativa", example="IT", alias="UNIDAD ORGANIZATIVA")
    work_location: Optional[str] = Field(None, description="Lugar trabajo", example="MADRID", alias="LUGAR TRABAJO")
    cost_center: Optional[str] = Field(None, description="Centro de costo", example="CC001", alias="CENTRO DE COSTO")
    start_reason: Optional[Literal["001"]] = Field(None, description="Motivo inicio", example="001", alias="MOTIVO INICIO")
    employee_type: Optional[str] = Field(None, description="Tipo empleado", example="FIJO", alias="TIPO EMPLEADO")
    probation_end_date: Optional[datetime] = Field(None, description="Fin periodo prueba", example="2024-03-31", alias="FIN PERIODO PRUEBA")
    expected_end_date: Optional[datetime] = Field(None, description="Finalización prevista", example="2024-12-31", alias="FINALIZACIÓN PREVISTA")
    duration: Optional[int] = Field(None, description="Duración", example=12, alias="DURACIÓN")

    # Social Security Information
    has_ss_number: Optional[SSNumberType] = Field(None, description="Con/sin num. S.S.", example=SSNumberType.WITH_SS, alias="CON/SIN NUM. S.S.")
    ss_province: Optional[str] = Field(None, description="Núm S.S. (provincia)", example="28", alias="NÚM S.S. (PROVINCIA)")
    ss_number: Optional[str] = Field(None, description="Núm S.S. (número)", example="12345678", alias="NÚM S.S. (NÚMERO)")
    ss_check_digit: Optional[str] = Field(None, description="Núm S.S. (D.C.)", example="12", alias="NÚM S.S. (D.C.)")
    ss_header: Optional[str] = Field(None, description="Cabecera TC1", example="TC1", alias="CABECERA TC1")
    tariff_group: Optional[str] = Field(None, description="Grupo de tarifa", example="01", alias="GRUPO DE TARIFA")
    occupation: Optional[str] = Field(None, description="Ocupación", example="", alias="OCUPACIÓN")
    ss_agreement: Optional[str] = Field(None, description="Convenio S.S.", example="", alias="CONVENIO S.S.")
    multi_employee_number: Optional[str] = Field(None, description="Número pluriempleado", example="", alias="NÚMERO PLURIEMPLEADO")
    legal_contract: Optional[str] = Field(None, description="Contrato legal", example="", alias="CONTRATO LEGAL")
    internal_contract: Optional[ContractType] = Field(None, description="Contrato interno", example=ContractType.REGULAR_INDEFINITE_FULL_TIME, alias="CONTRATO INTERNO")
    contract_end_date: Optional[datetime] = Field(None, description="Fecha fin contrato", example="2024-12-31", alias="FECHA FIN CONTRATO")
    labor_relationship: Optional[LaborRelationshipType] = Field(None, description="Relación laboral", example=LaborRelationshipType.HIGH_MANAGEMENT_PERSONNEL, alias="RELACIÓN LABORAL")
    part_time_percentage: Optional[float] = Field(None, ge=0, le=100, description="% Jornada parcial", example=50.0, alias="% JORNADA PARCIAL")
    hours_type: Optional[HoursType] = Field(None, description="Tipo horas", example=HoursType.WEEKLY, alias="TIPO HORAS")
    hours_number: Optional[int] = Field(None, description="Número horas", example=40, alias="NÚMERO HORAS")
    part_time_type: Optional[PartTimeType] = Field(None, description="Tipo jornada parcial", example=PartTimeType.REGULAR, alias="TIPO JORNADA PARCIAL")
    work_days_weekly: Optional[str] = Field(None, description="Días trabajo semanales", example="5", alias="DÍAS TRABAJO SEMANALES")

    # Reduction Information
    reduction_percentage: Optional[str] = Field(None, description="% Reducción", example="25", alias="% REDUCCIÓN")
    reduction_reason: Optional[ReductionReasonType] = Field(None, description="Motivo reducción", example=ReductionReasonType.CARE_OF_MINOR, alias="MOTIVO REDUCCIÓN")
    substitution_cause: Optional[SubstitutionCauseType] = Field(None, description="Causa sustitución", example=SubstitutionCauseType.SUBSTITUTION_LEAVE_FAMILY_CARE, alias="CAUSA SUSTITUCIÓN")
    substituted_ss_province: Optional[str] = Field(None, description="Núm S.S. del sustituido (provincia)", example="", alias="NÚM S.S. DEL SUSTITUIDO (PROVINCIA)")
    substituted_ss_number: Optional[str] = Field(None, description="Núm S.S. del sustituido (número)", example="", alias="NÚM S.S. DEL SUSTITUIDO (NÚMERO)")
    substituted_ss_check_digit: Optional[str] = Field(None, description="Núm S.S. del sustituido (D.C.)", example="", alias="NÚM S.S. DEL SUSTITUIDO (D.C.)")
    disability_percentage: Optional[float] = Field(None, ge=0, le=100, description="% Minusvalía", example=33.0, alias="% MINUSVALÍA")
    old_contract_start: Optional[datetime] = Field(None, description="Inicio antiguo contrato", example="2020-01-01", alias="INICIO ANTIGUO CONTRATO")
    woman_maternity_24_months: Optional[YesNoType] = Field(None, description="Mujer mater. 24 meses", example=YesNoType.NO, alias="MUJER MATER. 24 MESES")
    woman_underrepresented: Optional[YesNoType] = Field(None, description="Mujer subrepresentada", example=YesNoType.NO, alias="MUJER SUBREPRESENTADA")
    probation_days: Optional[int] = Field(None, description="Días de prueba", example=30, alias="DÍAS DE PRUEBA")
    additional_clause: Optional[str] = Field(None, description="Cláusula adicional", example="SC", alias="CLÁUSULA ADICIONAL")
    adjustment_type: Optional[AdjustmentType] = Field(None, description="Tipo de ajuste", example=AdjustmentType.WITH_ADJUSTMENT, alias="TIPO DE AJUSTE")
    agreement: Optional[str] = Field(None, description="Convenio", example="CONV001", alias="CONVENIO")
    category: Optional[str] = Field(None, description="Categoría", example="TECNICO", alias="CATEGORÍA")
    annual_gross: Optional[float] = Field(None, ge=0, description="Bruto anual", example=30000.0, alias="BRUTO ANUAL")
    salary_type: Optional[SalaryType] = Field(None, description="Tipo salario", example=SalaryType.MONTHLY, alias="TIPO SALARIO")
    seniority_date: Optional[datetime] = Field(None, description="Fecha antigüedad", example="2020-01-01", alias="FECHA ANTIGÜEDAD")
    extras_date: Optional[datetime] = Field(None, description="Fecha extras", example="2024-01-01", alias="FECHA EXTRAS")
    union: Optional[str] = Field(None, description="Sindicato", example="", alias="SINDICATO")
    irpf_type: Optional[IRPFType] = Field(None, description="Tipo IRPF", example=IRPFType.NATIONAL, alias="TIPO IRPF")
    irpf_status: Optional[IRPFStatusType] = Field(None, description="Estado IRPF", example=IRPFStatusType.SINGLE_WIDOWED_DIVORCED_SEPARATED_WITH_MINORS, alias="ESTADO IRPF")
    disability_hr: Optional[DisabilityHRType] = Field(None, description="Minusvalía RH", example="", alias="MINUSVALÍA RH")
    payment_type: Optional[PaymentType] = Field(None, description="Tipo pago", example=PaymentType.BANK_TRANSFER, alias="TIPO PAGO")
    company_bank: Optional[str] = Field(None, description="Banco empresa", example="BANK001", alias="BANCO EMPRESA")
    bank_branch: Optional[str] = Field(None, description="Banco + sucursal", example="BRANCH001", alias="BANCO + SUCURSAL")
    account_number: Optional[str] = Field(None, description="Núm. cuenta", example="12345678901234567890", alias="NÚM. CUENTA")
    check_digit: Optional[str] = Field(None, description="D.C.", example="12", alias="D.C.")
    activity_type: Optional[str] = Field(None, description="Tipo actividad", example="ACT001", alias="TIPO ACTIVIDAD")
    producer_type: Optional[str] = Field(None, description="Tipo productor", example="", alias="TIPO PRODUCTOR")
    management_type: Optional[ManagementType] = Field(None, description="Tipo gestión", example=ManagementType.UNICA, alias="TIPO GESTION")
    professional_group: Optional[str] = Field(None, description="Grupo profesional", example="", alias="GRUPO PROFESIONAL")
    professional_level: Optional[str] = Field(None, description="Nivel profesional", example="", alias="NIVEL PROFESIONAL")
    project: Optional[str] = Field(None, description="Proyecto", example="", alias="PROYECTO")
    team: Optional[str] = Field(None, description="Equipo", example="", alias="EQUIPO")
    product: Optional[str] = Field(None, description="Producto", example="", alias="PRODUCTO")
    function: Optional[str] = Field(None, description="Función", example="", alias="FUNCION")
    organizational_subgroup: Optional[str] = Field(None, description="Subgrupo organizativo", example="", alias="SUBGRUPO ORGANIZATIVO")
    department: Optional[str] = Field(None, description="Departamento", example="", alias="DEPARTAMENTO")
    region: Optional[str] = Field(None, description="Región", example="", alias="REGION")
    country_region: Optional[str] = Field(None, description="País", example="", alias="PAIS")
    territory: Optional[str] = Field(None, description="Territorio", example="", alias="TERRITORIO")
    perception_key: Optional[PerceptionKeyType] = Field(None, description="Clave percepción", example=PerceptionKeyType.A, alias="CLAVE PERCEPCIÓN")
    external_employee_id: Optional[str] = Field(None, description="ID empleado externo", example="", alias="ID EMPLEADO EXTERNO")

    # -------- DATETIME PARSE --------
    @field_validator(
        "effective_date", "termination_date", "vacation_end_date",
        "birth_date", "probation_end_date", "expected_end_date",
        "old_contract_start", "seniority_date", "extras_date",
        mode="before"
    )
    def parse_dd_mm_yyyy(cls, v):
        if v in (None, "") or isinstance(v, datetime):
            return v
        return datetime.strptime(v, "%d/%m/%Y")

    # -------- MOVEMENT TYPE VALIDATION --------
    @model_validator(mode='after')
    def validate_movement_requirements(self):
        """
        Validate mandatory fields based on movement type.
        """
        if self.movement_type == MovementType.MODIFICACION:
            # For MODIFICACION (3), only effective_date and person_id are mandatory
            mandatory_fields_modificacion = [
                'effective_date', 'person_id'
            ]

            for field_name in mandatory_fields_modificacion:
                field_value = getattr(self, field_name, None)
                if field_value is None or field_value == "":
                    raise ValueError(f"{field_name} is mandatory for MODIFICACION movement")

        elif self.movement_type == MovementType.BAJA:
            # For BAJA (2), termination_date and termination_reason are mandatory
            mandatory_fields_baja = [
                'effective_date', 'termination_date', 'termination_reason',
                'unemployment_cause', 'person_id'
            ]

            for field_name in mandatory_fields_baja:
                field_value = getattr(self, field_name, None)
                if field_value is None or field_value == "":
                    raise ValueError(f"{field_name} is mandatory for BAJA movement")

        elif self.movement_type == MovementType.ALTA:
            # For ALTA (1), all basic employee information is mandatory
            mandatory_fields_alta = [
                'effective_date', 'person_id', 'first_surname', 'second_surname',
                'employee_name', 'document_type', 'document_number', 'birth_date',
                'nationality', 'birth_country', 'gender', 'location_type', 'street_type',
                'employee_address', 'street_number', 'postal_code', 'company', 'job',
                'organizational_unit', 'work_location', 'cost_center', 'start_reason',
                'employee_type', 'has_ss_number', 'ss_province', 'ss_number',
                'ss_check_digit', 'internal_contract', 'reduction_percentage',
                'reduction_reason', 'additional_clause', 'adjustment_type', 'agreement',
                'category', 'salary_type', 'irpf_type', 'irpf_status', 'payment_type',
                'company_bank', 'bank_branch', 'account_number', 'check_digit',
                'management_type', 'perception_key'
            ]

            for field_name in mandatory_fields_alta:
                field_value = getattr(self, field_name, None)
                if field_value is None or field_value == "":
                    raise ValueError(f"{field_name} is mandatory for ALTA movement")

        return self

    class Config:
        json_encoders = {datetime: lambda d: d.strftime("%d/%m/%Y")}
        allow_population_by_field_name = True
        populate_by_name = True
