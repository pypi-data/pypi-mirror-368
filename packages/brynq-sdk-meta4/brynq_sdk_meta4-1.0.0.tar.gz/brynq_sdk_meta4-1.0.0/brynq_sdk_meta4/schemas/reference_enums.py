from enum import Enum
from typing import Dict, Any


class MovementType(str, Enum):
    """Movement types for employee data"""
    ALTA = "1"  # New Hire
    BAJA = "2"  # Terminate
    MODIFICACION = "3"  # Modification


class DocumentType(str, Enum):
    """Document types for employee identification"""
    DNI = "1"  # National Identity Document
    NIE = "6"  # Foreigner Identity Number


class GenderType(str, Enum):
    """Gender types"""
    MALE = "1"  # Male
    FEMALE = "2"  # Female


class MaritalStatusType(str, Enum):
    """Marital status types"""
    SINGLE = "01"  # Single
    MARRIED = "02"  # Married
    WIDOWED = "03"  # Widowed
    DIVORCED = "04"  # Divorced
    COMMON_LAW = "05"  # Common-law partnership
    SEPARATED = "06"  # Separated
    OTHER = "07"  # Others


class StreetType(str, Enum):
    """Street types for addresses"""
    ACERA = "AC"  # Sidewalk
    ALDEA = "AD"  # Village
    ALAMEDA = "AL"  # Avenue
    AMPLIACION = "AM"  # Extension
    ANGOSTA = "AN"  # Narrow
    APARTAMENTOS = "AP"  # Apartments
    ACEQUIA = "AQ"  # Ditch
    APARTADO_CORREOS = "AS"  # Post office box
    ATAJO = "AT"  # Shortcut
    AVENIDA = "AV"  # Avenue
    BAJADA = "BA"  # Descent
    BARRANCO = "BC"  # Ravine
    BARRIADA = "BD"  # Neighborhood
    BOULEVARD = "BL"  # Boulevard
    BARRIO = "BO"  # District
    CALLEJA = "CA"  # Alley
    CALLEJUELA = "CE"  # Small street
    CHALET = "CH"  # Chalet
    CALLEJON = "CJ"  # Alley
    CALLE = "CL"  # Street
    CAMINO = "CM"  # Road
    COSTANILLA = "CN"  # Slope
    COLONIA = "CO"  # Colony
    COOPERATIVA = "CP"  # Cooperative
    CARRETERA = "CR"  # Highway
    CASERIO = "CS"  # Hamlet
    CUESTA = "CU"  # Slope
    CALZADA = "CZ"  # Roadway
    ESCALA = "EA"  # Scale
    EDIFICIO = "ED"  # Building
    ESCALINATA = "EL"  # Staircase
    ESCALERA = "ES"  # Stairs
    ESTRADA = "ET"  # Road
    GLORIETA = "GL"  # Roundabout
    GRUPO = "GR"  # Group
    CORRAL = "KO"  # Corral
    LUGAR = "LG"  # Place
    LLANO = "LL"  # Plain
    MERCADO = "MC"  # Market
    MUNICIPIO = "MN"  # Municipality
    MONTANA = "MO"  # Mountain
    MANZANA = "MZ"  # Block
    PASEO_ALTO = "PA"  # High promenade
    POBLADO = "PB"  # Village
    PARTICULAR = "PC"  # Private
    PASADIZO = "PD"  # Passage
    PLAZOLETA = "PE"  # Small square
    POLIGONO = "PG"  # Polygon
    PASILLO = "PI"  # Corridor
    PASAJE = "PJ"  # Passage
    PLACETA = "PL"  # Small square
    PROLONGACION = "PN"  # Extension
    PASEO_BAJO = "PO"  # Low promenade
    PASEO = "PP"  # Promenade
    PARQUE = "PQ"  # Park
    PORTALES = "PR"  # Portals
    PASO = "PS"  # Step
    PATIO = "PT"  # Patio
    PLAZUELA = "PU"  # Small square
    PRIVADA = "PV"  # Private
    PLAZA = "PZ"  # Square
    RAMAL = "RA"  # Branch
    RAMBLA = "RB"  # Rambla
    RINCONADA = "RC"  # Corner
    RONDA = "RD"  # Round
    RESIDENCIA = "RE"  # Residence
    RESIDENCIAL = "RL"  # Residential
    RINCON = "RN"  # Corner
    RAMPA = "RP"  # Ramp
    RIBERA = "RR"  # Shore
    SECTOR_SECCION = "SC"  # Sector, Section
    SENDA = "SD"  # Path
    PASSEIG = "SP"  # Promenade (Catalan)
    SENDERO = "SR"  # Trail
    SUBIDA = "SU"  # Ascent
    TRANSVERSAL = "TL"  # Transversal
    TORRE = "TO"  # Tower
    TRAVESIA = "TR"  # Cross street
    TRASERA = "TS"  # Back
    TORRENTE = "TT"  # Stream
    URBANIZACION = "UR"  # Urbanization
    VIA = "VI"  # Way
    VILLAS = "VL"  # Villas
    VIVIENDAS = "VV"  # Dwellings
    SIN_DATOS_DOMICILIARIOS = "XX"  # Without residential data
    ZONA = "ZO"  # Zone
    OTROS = "ZZ"  # Others


class HoursType(str, Enum):
    """Hours types"""
    WEEKLY = "1"  # Weekly
    MONTHLY = "2"  # Monthly
    ANNUAL = "3"  # Annual


class PartTimeType(str, Enum):
    """Part-time schedule types"""
    REGULAR = "R"  # Regular
    IRREGULAR = "I"  # Irregular


class SSNumberType(str, Enum):
    """With/Without SS Number"""
    WITHOUT_SS = "0"  # Without SS Number
    WITH_SS = "1"  # With SS Number


class YesNoType(str, Enum):
    """Yes/No types"""
    YES = "S"  # Yes
    NO = "N"  # No


class SalaryType(str, Enum):
    """Salary types"""
    DAILY = "0"  # Daily
    MONTHLY = "1"  # Monthly


class AdjustmentType(str, Enum):
    """Adjustment types"""
    WITHOUT_ADJUSTMENT = "0"  # Without gross adjustment
    WITH_ADJUSTMENT = "1"  # With gross adjustment


class PaymentType(str, Enum):
    """Payment types"""
    CHECK = "2"  # Check
    BANK_TRANSFER = "4"  # Bank transfer


class IRPFType(str, Enum):
    """IRPF types"""
    ALAVA = "ALA"
    NO_RESIDENT_UE_EEE = "EUE"  # Non-resident EU/EEA
    EXPATRIATES = "EXPA"  # Expatriates
    FOREIGNER = "EXT"  # Foreigner
    GUIPUZCOA = "GUI"
    NATIONAL = "NAC"  # National
    NAVARRA = "NAV"
    CROSS_BORDER_FORAL_MOD_296 = "TRAF"  # Cross-border Foral Mod 296
    CROSS_BORDER_TCOMUN_MOD_296 = "TRAN"  # Cross-border TCOMUN Mod 296
    VIZCAYA = "VIZ"


class IRPFStatusType(str, Enum):
    """IRPF status types"""
    SINGLE_WIDOWED_DIVORCED_SEPARATED_WITH_MINORS = "1"  # Single, Widowed, Divorced or Legally Separated with minors in charge
    MARRIED_NOT_SEPARATED_WITH_DEPENDENT_SPOUSE = "2"  # Married and not separated with dependent spouse
    OTHER_SITUATIONS_OR_DOES_NOT_WISH = "3"  # Other situations, or does not wish to


class DisabilityHRType(str, Enum):
    """Disability HR types"""
    FROM_33_TO_BELOW_65 = "M_33_65"  # From 33% and below 65%
    FROM_33_TO_BELOW_65_WITH_HELP = "M_33_65_A"  # From 33% and below 65% with help
    EQUAL_OR_GREATER_THAN_65 = "M_65"  # Equal to or greater than 65%


class ManagementType(str, Enum):
    """Management types"""
    UNICA = "UNICA"  # Unique


class PerceptionKeyType(str, Enum):
    """Perception key types"""
    A = "A"


# Termination reason types
# Note: This enum is related to UnemploymentCauseType through TERMINATION_REASON_TO_UNEMPLOYMENT_CAUSE mapping
class TerminationReasonType(str, Enum):
    """Termination reason types - Related to UnemploymentCauseType via TERMINATION_REASON_TO_UNEMPLOYMENT_CAUSE mapping"""
    BORRADO_PERSONAL = "000"  # Borrado de personal
    MOTIVOS_ECONOMICOS = "001"  # Motivos Económicos
    DESACUERDO_POLITICA_EMPRESARIAL = "002"  # Desacuerdo con la Política Empresarial
    DESCONTENTO_AMBIENTE = "003"  # Descontento con el ambiente
    DESPIDO = "004"  # Despido
    JUBILACION = "005"  # Jubilación
    BAJA_VOLUNTARIA = "006"  # Baja Voluntaria
    INDEMNIZACION_ESPECIAL_ERE_EXTINTIVO = "007"  # Indemnización Especial ERE Extintivo
    BAJA_VOLUNTARIA_NO_RECONTRATAR = "008"  # Baja Voluntaria No Recontratar
    TERMINACION_SIN_FINIQUITO = "009"  # Terminación sin finiquito
    FIN_CONTRATO = "010"  # Fin Contrato
    FIN_CONTRATO_CON_INDEMNIZACION = "011"  # Fin Contrato con Indemnización
    SUSPENSION_EMPLEO_SUELDO = "012"  # Suspensión de Empleo y sueldo
    INVALIDEZ = "013"  # Invalidez
    EXCEDENCIA_FORZOSA = "014"  # Excedencia forzosa
    EXTINCION_PUESTO_TRABAJO = "015"  # Extinción Puesto Trabajo
    CAMBIO_CONVENIO = "017"  # Cambio de Convenio
    DESPIDO_DIRECTIVO = "024"  # Despido Directivo
    EXCEDENCIA_ART_31 = "031"  # Excedencia Art. 31
    FIN_CONTRATO_COMISION_TERMINACION = "050"  # Fin del contrato - Comisión de terminación del servicio
    ACUERDO_REVOCADO = "051"  # Acuerdo Revocado, basado en un motivo que permite gastos colec
    BAJA_DESPIDO_DISCIPLINARIO_INDIVIDUAL = "053"  # Baja por despido disciplinario individual
    BAJA_FUSION_ABSORCION_EMPRESA = "055"  # Baja por fusión/absorción de la empresa
    BAJA_SUSPENSION_TEMPORAL_ERE = "069"  # Baja por suspensión temporal de ERE
    EXCEDENCIA_CUIDADO_FAMILIAR = "073"  # Excedencia Cuidado Familiar
    SUSPENSION_SERVICIO_TEMPORAL = "074"  # Suspensión de servicio temporal
    BAJA_DESPIDO_COLECTIVO = "077"  # Baja por Despido Colectivo
    SUSPENSION_VIOLENCIA_GENERO = "080"  # Suspensión por violencia de género
    CESE_PERIODO_PRUEBA_TRABAJADOR = "090"  # Cese en periodo de prueba a instancia del trabajador
    BAJA_DESPIDO_CAUSAS_OBJETIVAS_EMPRESA = "091"  # Baja despido por causas objetivas (empresa)
    BAJA_DESPIDO_CAUSAS_OBJETIVAS_TRABAJADOR = "092"  # Baja despido causas objetivas (trabajador)
    BAJA_PASE_INACTIVIDAD_FIJOS_DISCONTINUOS = "094"  # Baja por pase a inactividad fijos discontinuos
    SUBROGACION_CERTIFICADO_EMPRESA = "096"  # Subrogación (con certificado de empresa)
    CESE_TRASLADO_CENTRO_TRABAJO = "097"  # Cese por Traslado de Centro de Trabajo
    CAMBIO_EMPRESA = "098"  # Cambio de Empresa
    BAJA_MODIFICACION_SUSTANCIAL_CONDICIONES = "099"  # Baja por modificación sustancial de las condiciones de trabajo
    IMPORTACION_DATOS_BAJA = "100"  # Importación de datos con baja
    INCORPORACION_PLANTILLA = "101"  # Por incorporación plantilla
    FALLECIMIENTO = "111"  # Fallecimiento
    NO_SUPERACION_PERIODO_PRUEBA = "112"  # No superación período de prueba
    DESISTIMIENTO = "13"  # Desistimiento
    CAMBIO_FUNCIONES = "15"  # Cambio de funciones
    ERE_PARCIAL = "17"  # ERE Parcial
    DESPIDO_SIN_PREAVISO = "20"  # Despido sin preaviso
    BAJA_VOL_PTE_COMISIONES = "200"  # Baja vol pte comisiones
    BAJA_NO_VOL_PTE_COMISIONES = "201"  # Baja No Vol pte comisiones
    BAJA_VOL_PTE_PAGO = "202"  # Baja Vol pte pago
    BAJA_NO_VOL_PTE_PAGO = "203"  # Baja No vol pte pago
    BAJA_FIN_BECA = "204"  # Baja por fin de beca
    CAMBIO_DEVENGO_PAGAS_EXTRAS = "300"  # Cambio devengo pagas extras
    EXCEDENCIA_VOLUNTARIA = "333"  # Excedencia Voluntaria
    EXCEDENCIA_ESPECIAL = "334"  # Excedencia Especial
    EXCEDENCIA_FALLECIMIENTO_CONYUGE_HIJO_MENOR = "335"  # Excedencia fallecimiento de cónyuge con hijo menor a cargo
    EXCEDENCIA_FORZOSA_CARGO_PUBLICO = "336"  # Excedencia forzosa. Cargo público.
    EXCEDENCIA_TRAMITES_ADOPCION_INTERNACIONAL = "337"  # Excedencia trámites adopción internacional. Gestiones en país
    BAJA_VOLUNTARIA_TRABAJADOR = "51"  # Baja voluntaria del trabajador
    BAJA_DESPIDO_DISCIPLINARIO_PROCEDENTE = "53"  # Baja por Despido disciplinario Procedente
    BAJA_AGOTAMIENTO_IT = "65"  # Baja por Agotamiento IT
    EXCEDENCIA_CUIDADO_HIJOS_SIN_LIQUIDACION = "68"  # Excedencia cuidado de hijos (sin liquidación)
    EXCEDENCIA_CUIDADO_HIJOS_CON_LIQUIDACION = "69"  # Excedencia cuidado de hijos (con liquidación)
    MUTUO_ACUERDO = "700"  # Mutuo acuerdo
    FIN_EXPATRIACION = "701"  # Fin expatriación
    FIN_MISION = "702"  # Fin misión
    FIN_COMISION_SERVICIOS = "703"  # Fin comisión de servicios
    BAJA_INCENTIVADA = "704"  # Baja incentivada
    PREJUBILACION = "705"  # Prejubilación
    INICIO_EXPATRIACION = "706"  # Inicio Expatriacion
    TERMINACION_EMPLEADO_EVENTUAL = "777"  # Terminación de empleado eventual
    CAMBIO_PERIODO_GL_SIN_LIQUIDACION = "81"  # Cambio periodo por GL (sin liquidación)
    BAJA_DIMISION = "82"  # Baja por Dimision
    BAJA_EXTINCION_CONTRATO_PRUEBAS = "85"  # Baja por extinción contrato en pruebas
    BAJA_SIN_LIQUIDACION_NUEVO_PERIODO = "86"  # Baja sin liquidación Nuevo Periodo
    PERMISO_SIN_SUELDO = "87"  # Permiso sin sueldo
    CAMBIO_CONTRATO = "88"  # Cambio de contrato
    DESPIDO_SIN_INDEMNIZACION = "888"  # Despido sin Indemnización
    SUBROGACION = "889"  # Subrogación
    SUBROGACION_BAJA_SEGURIDAD_SOCIAL = "890"  # Subrogación con Baja en Seguridad Social
    CAMBIO_CENTRO_TRABAJO_SIN_LIQUIDACION = "98"  # Cambio Centro Trabajo sin Liquidacion
    FIN_INTERINIDAD = "987"  # Fin Interinidad
    ANULACION_ALTA_PREVIA = "988"  # Anulación Alta Previa
    INCAPACIDAD = "99"  # Incapacidad
    OTRAS_CAUSAS_BAJA = "991"  # Otras Causas de Baja
    BAJA_PERIODOS_FUERA_PLAZO = "992"  # Baja para periodos fuera de plazo
    ERE_EXTINTIVO = "999"  # ERE Extintivo


# Contract types
class ContractType(str, Enum):
    """Contract types"""
    WITHOUT_CONTRACT = "0"  # SIN CONTRATO
    TEMPORARY_EMPLOYMENT_AGENCY = "1"  # ETT
    INTERN_STUDENT = "2"  # BECARIO / ALUMNO
    RETIRED = "3"  # JUBILADO
    SURPLUS = "4"  # EXCEDENTES
    SUBSIDIZED_INTERN = "5"  # BECARIO BONIFICADO
    ADVISOR = "6"  # CONSEJERO
    CHINA_AGREEMENT = "7"  # CONVENIO CHINA
    REGULAR_INDEFINITE_FULL_TIME = "1000"  # ORDINARIO INDEFINIDO TP COMPLETO
    INDEFINITE_FULL_TIME_OVER_45 = "1002"  # INDEFINIDO TP COMPL. MAYORES 45
    REGULAR_TEMPORARY_FULL_TIME = "2000"  # ORDINARIO TEMPORAL TP COMPLETO
    REGULAR_INDEFINITE_PART_TIME = "3000"  # ORDINARIO INDEFINIDO TP PARCIAL
    REGULAR_TEMPORARY_PART_TIME = "4000"  # ORDINARIO TEMPORAL TP PARCIAL


# Labor relationship types
class LaborRelationshipType(str, Enum):
    """Labor relationship types"""
    HIGH_MANAGEMENT_PERSONNEL = "100"  # Personal de alta dirección
    PRISONERS_LEARNING_TRAINING = "301"  # Penados en Instituciones Penitenciarias. Aprendizaje/Formación
    PRISONERS_WORK_ACTIVITY = "302"  # Penados en Instituciones Penitenciarias. Actividad Laboral
    PRISONERS_COMMUNITY_BENEFIT = "303"  # Penados en Instituciones Penitenciarias. Beneficio Comunidad
    PRISONERS_MINORS = "304"  # Penados en Instituciones Penitenciarias. Menores
    STEVEDORES = "396"  # Estibadores
    PROFESSIONAL_ATHLETES = "409"  # Deportistas profesionales
    COMMERCIAL_REPRESENTATIVES = "500"  # Representantes de comercio
    ONCE_COUPON_SELLERS = "501"  # Representantes de comercio -vendedores del cupón de la ONCE-
    DISABLED_SPECIAL_EMPLOYMENT_CENTERS = "600"  # Minusválidos en Centros Especiales de Empleo
    DISABLED_LABOR_ENCLAVE = "601"  # Minusválido procedente enclave laboral
    DISABLED_NATIONAL_ORGANIZATION_BLIND = "602"  # Discapacitado Organización Nacional de Ciegos
    PORT_STEVEDORES = "700"  # Estibadores portuarios
    ARTISTS_PUBLIC_SHOWS = "800"  # Artistas en espectáculos públicos
    LAWYERS_LAW_FIRM = "900"  # Abogados en despacho de abogados
    ADVISOR_ADMINISTRATOR_SMC = "951"  # Consejero-administrador SMC / Situación laboral asimilada a cuenta ajena
    ADVISOR_ADMIN_SMC_LAB_SITUATION = "952"  # CONSEJERO-ADMINIST.SMC./S.LAB.ASIMIL.C/A
    RESEARCHERS_SPANISH_SCIENCE_TECHNOLOGY = "9901"  # Investigadores del Sistema Español de Ciencia y Tecnología
    INTERIM_RESIDENT_DOCTORS = "9902"  # Médicos Interinos Residentes
    PUBLIC_UNIVERSITY_ASSISTANT_PROFESSOR = "9903"  # Universidad Pública -Profesor Ayudante
    PUBLIC_UNIVERSITY_ASSISTANT_DOCTOR_PROFESSOR = "9904"  # Universidad Pública -Profesor Ayudante Doctor
    PUBLIC_UNIVERSITY_COLLABORATING_PROFESSOR = "9905"  # Universidad Pública -Profesor Colaborador
    PUBLIC_UNIVERSITY_CONTRACTED_DOCTOR_PROFESSOR = "9906"  # Universidad Pública -Profesor Contratado Doctor
    PUBLIC_UNIVERSITY_ASSOCIATE_PROFESSOR = "9907"  # Universidad Pública -Profesor Asociado
    PUBLIC_UNIVERSITY_VISITING_PROFESSOR = "9908"  # Universidad Pública -Profesor Visitante
    RESEARCH_STAFF_TRAINING_SCHOLARSHIP = "9909"  # Personal investigador en formación - Beca
    RESEARCH_STAFF_TRAINING_INTERNSHIP_CONTRACT = "9910"  # Personal investigador en formación - Contrato prácticas
    STUDENTS_WORKERS_WORKSHOP_SCHOOL_PROGRAMS = "9911"  # Alumnos - Trabajadores en programas de escuela taller
    STUDENTS_WORKERS_TRADE_HOUSE_PROGRAMS = "9912"  # Alumnos - Trabajadores en programas de casas de oficios
    STUDENTS_WORKERS_EMPLOYMENT_WORKSHOP_PROGRAMS = "9913"  # Alumnos - Trabajadores en programas de talleres de empleo
    DISABILITY_PENSIONER_SS = "9914"  # Pensionista de incapacidad S.S.
    DISABILITY_PENSIONER_PASSIVE_CLASSES = "9915"  # Pensionista de incapacidad clases pasivas
    RD_I_RESEARCH_STAFF = "9916"  # Personal investigador I+D+I
    TRAINING_CONTRACTS_EXTENSION_AFTER_2010 = "9918"  # Contratos de Formación – Prorroga posterior 18-06-2010
    NON_SUBSIDIZED_TRAINING_CONTRACT_AFTER_2011 = "9920"  # Contrato de formación no bonificados. posterior 18.06.2011
    PREDOCTORAL_CONTRACT = "9921"  # Contrato predoctoral
    PARTICIPANTS_TRAINING_PROGRAMS = "9922"  # Participantes en programas para la formación
    NON_LABOR_INTERNSHIPS_COMPANIES = "9923"  # Prácticas no laborales en empresas
    LABOR_SOCIETY_PARTNER = "9924"  # Socio Sociedad Laboral
    NON_PARTNER_LABOR_SOCIETY = "9925"  # No socio Sociedad Laboral
    EXTERNAL_ACADEMIC_INTERNSHIP = "9927"  # PRACTIC.ACAD.EXTERNA
    EXTERNAL_CURRICULAR_INTERNSHIPS = "9928"  # Prácticas curriculares externas
    CT_ALTERNATING_TRAINING_PROFESSIONALITY_CERTIFICATE_LEVEL_3 = "9935"  # CT FORMACION ALTERNANCIA - CERTIFICADO PROFESIONALIDAD NIVEL 3
    CT_ALTERNATING_TRAINING_UNIVERSITY_FP_STUDIES = "9936"  # CT FORMACIÓN ALTERNANCIA - ESTUDIOS UNIVERSIDAD/FP
    PAID_TRAINING_INTERNSHIPS_DA52LGSS = "9939"  # PRÁCTICAS FORM.REMUNERADAS DA52LGSS


# Substitution cause types
class SubstitutionCauseType(str, Enum):
    """Substitution cause types"""
    NULL_SUBSTITUTION_CAUSE = "0"  # Causa de sustitución nula (valor 0 para el AFI)
    SUBSTITUTION_LEAVE_FAMILY_CARE = "1"  # Sustitución por excedencia por cuidado de familiares
    REST_BIRTH_CARE_MINOR_PREGNANCY_LACTATION_RISK = "2"  # Descanso nacimiento cuidado menor- Riesgo embarazo/Lactancia
    SUBSTITUTION_EARLY_RETIREE_64_YEARS = "3"  # Sustitución jubilado anticipadamente a los 64 años
    DISABLED_PERSON_SUBSTITUTION = "4"  # Sustitución minusválido
    DISABLED_PERSON_SUBSTITUTION_SICK_LEAVE = "5"  # Sustitución minusválido en situación de IT
    GENDER_VIOLENCE_VICTIMS = "6"  # Víctimas violencia de género
    COVERAGE_VACANCY_REDUCTION_PERMANENT_EMPLOYMENT = "7"  # Cobertura vacante disminución empleo fijo
    TEMPORARY_COVERAGE_JOB_POSITION_SELECTION_PROCESS = "8"  # Cobertura temporal de puesto de trabajo durante el proceso de selección
    SEXUAL_VIOLENCE_VICTIM_SUBSTITUTION = "9"  # Sustitución víctima violencia sexual
    REST_BIRTH_CARE_MINOR_RISK_SUBSTITUTE = "10"  # Descanso nacimiento cuidado menor/ Riesgo-sustituto


# Unemployment cause types
# Note: This enum is related to TerminationReasonType through TERMINATION_REASON_TO_UNEMPLOYMENT_CAUSE mapping
class UnemploymentCauseType(str, Enum):
    """Unemployment cause types - Related to TerminationReasonType via TERMINATION_REASON_TO_UNEMPLOYMENT_CAUSE mapping"""
    UNKNOWN = "00"  # Desconocida
    WORKER_DISMISSAL = "01"  # Despido del trabajador
    OBJECTIVE_CAUSES_DISMISSAL = "02"  # Despido por causas objetivas
    PERMANENT_TOTAL_DISABILITY_CESSATION = "06"  # Cese por declaración de invalidez permanente total del trabajador
    EMPLOYER_TRIAL_PERIOD_CESSATION = "07"  # Cese en período de prueba a instancia del empresario
    WORKER_TRIAL_PERIOD_CESSATION = "09"  # Cese en período de prueba a instancia del trabajador
    TEMPORARY_CONTRACT_END = "11"  # Fin de contrato temporal
    TRANSFER_SUBSTANTIAL_MODIFICATION = "14"  # Traslado o modificación sustancial de las condiciones de trabajo
    FIXED_DISCONTINUOUS_ACTIVITY_END = "15"  # Fin o interrupción de la actividad de los trabajadores fijos-discontinuos
    ERE_CONTRACT_EXTINCTION = "16"  # Extinción del contrato autorizada en E.R.E.
    ERE_CONTRACT_SUSPENSION = "17"  # Suspensión del contrato autorizada en E.R.E. o por auto judicial o constatada por la autoridad laboral en cooperativas
    ERE_TEMPORARY_HOURS_REDUCTION = "18"  # Reducción temporal de jornada autorizada en E.R.E. o por auto judicial o constatada  por la autoridad laboral en cooperativas
    GENDER_VIOLENCE_VOLUNTARY_SUSPENSION = "19"  # Suspensión o extinción voluntaria del contrato en caso de víctimas de violencia de género
    VOLUNTARY_WORKER_RESIGNATION = "21"  # Baja voluntaria del trabajador
    DEATH = "23"  # Fallecimiento
    LEAVE_OF_ABSENCE = "26"  # Excedencia
    OBJECTIVE_CAUSES_DISMISSAL_INCOMPETENCE = "30"  # DESPIDO POR CAUSAS OBJETIVAS.INEPTITUD,FALTA DE ADAPTACION Y ASISTENCIA AL TRABAJO
    WORKER_RESOLUTION_SUBSTANTIAL_MODIFICATION = "31"  # RESOLUCIÓN DEL TRABAJADOR POR MODIFICACIÓN SUSTANCIAL DE LAS CONDICIONES DE TRABAJO
    IT_EXHAUSTION_RESIGNATION = "65"  # Baja por agotamiento I.T.
    OTHER_SUSPENSION_CAUSES = "74"  # Otras causas de suspensión
    RETIREMENT = "88"  # JUBILACION


# Reduction reason types
class ReductionReasonType(str, Enum):
    """Reduction reason types"""
    CARE_OF_MINOR = "001"  # Care of minor
    CARE_OF_DISABLED = "002"  # Care of disabled person
    CARE_OF_FAMILY_MEMBER = "003"  # Care of family member
    BREASTFEEDING_CO_RESPONSIBILITY = "004"  # Breastfeeding co-responsibility
    GENDER_VIOLENCE = "005"  # Gender violence
    PREMATURE_CHILD_BIRTH = "006"  # Premature child birth
    CARE_OF_MINOR_WITH_SERIOUS_ILLNESS = "007"  # Care of minor with serious illness
    CARE_OF_MINOR_WITH_SERIOUS_ILLNESS_PLUS_OTHER_REDUCTION = "008"  # Care of minor with serious illness + other reduction
    PARTIAL_SCHEDULE_REDUCTION_COVID = "009"  # Partial schedule reduction COVID
    TOTAL_SCHEDULE_REDUCTION_COVID_19 = "010"  # Total schedule reduction COVID 19


# Termination reason mapping
TERMINATION_REASONS: Dict[str, str] = {
    "000": "Borrado de personal",
    "001": "Motivos Económicos",
    "002": "Desacuerdo con la Política Empresarial",
    "003": "Descontento con el ambiente",
    "004": "Despido",
    "005": "Jubilación",
    "006": "Baja Voluntaria",
    "007": "Indemnización Especial ERE Extintivo",
    "008": "Baja Voluntaria No Recontratar",
    "009": "Terminación sin finiquito",
    "010": "Fin Contrato",
    "011": "Fin Contrato con Indemnización",
    "012": "Suspensión de Empleo y sueldo",
    "013": "Invalidez",
    "014": "Excedencia forzosa",
    "015": "Extinción Puesto Trabajo",
    "017": "Cambio de Convenio",
    "024": "Despido Directivo",
    "031": "Excedencia Art. 31",
    "050": "Fin del contrato - Comisión de terminación del servicio",
    "051": "Acuerdo Revocado, basado en un motivo que permite gastos colec",
    "053": "Baja por despido disciplinario individual",
    "055": "Baja por fusión/absorción de la empresa",
    "069": "Baja por suspensión temporal de ERE",
    "073": "Excedencia Cuidado Familiar",
    "074": "Suspensión de servicio temporal",
    "077": "Baja por Despido Colectivo",
    "080": "Suspensión por violencia de género",
    "090": "Cese en periodo de prueba a instancia del trabajador",
    "091": "Baja despido por causas objetivas (empresa)",
    "092": "Baja despido causas objetivas (trabajador)",
    "094": "Baja por pase a inactividad fijos discontinuos",
    "096": "Subrogación (con certificado de empresa)",
    "097": "Cese por Traslado de Centro de Trabajo",
    "098": "Cambio de Empresa",
    "099": "Baja por modificación sustancial de las condiciones de trabajo",
    "100": "Importación de datos con baja",
    "101": "Por incorporación plantilla",
    "111": "Fallecimiento",
    "112": "No superación período de prueba",
    "13": "Desistimiento",
    "15": "Cambio de funciones",
    "17": "ERE Parcial",
    "20": "Despido sin preaviso",
    "200": "Baja vol pte comisiones",
    "201": "Baja No Vol pte comisiones",
    "202": "Baja Vol pte pago",
    "203": "Baja No vol pte pago",
    "204": "Baja por fin de beca",
    "300": "Cambio devengo pagas extras",
    "333": "Excedencia Voluntaria",
    "334": "Excedencia Especial",
    "335": "Excedencia fallecimiento de cónyuge con hijo menor a cargo",
    "336": "Excedencia forzosa. Cargo público.",
    "337": "Excedencia trámites adopción internacional. Gestiones en país",
    "51": "Baja voluntaria del trabajador",
    "53": "Baja por Despido disciplinario Procedente",
    "65": "Baja por Agotamiento IT",
    "68": "Excedencia cuidado de hijos (sin liquidación)",
    "69": "Excedencia cuidado de hijos (con liquidación)",
    "700": "Mutuo acuerdo",
    "701": "Fin expatriación",
    "702": "Fin misión",
    "703": "Fin comisión de servicios",
    "704": "Baja incentivada",
    "705": "Prejubilación",
    "706": "Inicio Expatriacion",
    "777": "Terminación de empleado eventual",
    "81": "Cambio periodo por GL (sin liquidación)",
    "82": "Baja por Dimision",
    "85": "Baja por extinción contrato en pruebas",
    "86": "Baja sin liquidación Nuevo Periodo",
    "87": "Permiso sin sueldo",
    "88": "Cambio de contrato",
    "888": "Despido sin Indemnización",
    "889": "Subrogación",
    "890": "Subrogación con Baja en Seguridad Social",
    "98": "Cambio Centro Trabajo sin Liquidacion",
    "987": "Fin Interinidad",
    "988": "Anulación Alta Previa",
    "99": "Incapacidad",
    "991": "Otras Causas de Baja",
    "992": "Baja para periodos fuera de plazo",
    "999": "ERE Extintivo"
}


# Unemployment cause mapping
CAUSE_OF_UNEMPLOYMENT: Dict[str, str] = {
    "00": "Desconocida",
    "01": "Despido del trabajador",
    "02": "Despido por causas objetivas",
    "06": "Cese por declaración de invalidez permanente total del trabajador",
    "07": "Cese en período de prueba a instancia del empresario",
    "09": "Cese en período de prueba a instancia del trabajador",
    "11": "Fin de contrato temporal",
    "14": "Traslado o modificación sustancial de las condiciones de trabajo",
    "15": "Fin o interrupción de la actividad de los trabajadores fijos-discontinuos",
    "16": "Extinción del contrato autorizada en E.R.E.",
    "17": "Suspensión del contrato autorizada en E.R.E. o por auto judicial o constatada por la autoridad laboral en cooperativas",
    "18": "Reducción temporal de jornada autorizada en E.R.E. o por auto judicial o constatada  por la autoridad laboral en cooperativas",
    "19": "Suspensión o extinción voluntaria del contrato en caso de víctimas de violencia de género",
    "21": "Baja voluntaria del trabajador",
    "23": "Fallecimiento",
    "26": "Excedencia",
    "30": "DESPIDO POR CAUSAS OBJETIVAS.INEPTITUD,FALTA DE ADAPTACION Y ASISTENCIA AL TRABAJO",
    "31": "RESOLUCIÓN DEL TRABAJADOR POR MODIFICACIÓN SUSTANCIAL DE LAS CONDICIONES DE TRABAJO",
    "65": "Baja por agotamiento I.T.",
    "74": "Otras causas de suspensión",
    "88": "JUBILACION"
}


# Termination reason to unemployment cause mapping
TERMINATION_REASON_TO_UNEMPLOYMENT_CAUSE: Dict[str, str] = {
    "000": "00",
    "001": "02",
    "002": "21",
    "003": "21",
    "004": "01",
    "005": "88",
    "006": "21",
    "007": "16",
    "008": "21",
    "009": "14",
    "010": "11",
    "011": "11",
    "012": "74",
    "013": "06",
    "014": "26",
    "015": "02",
    "017": "00",
    "024": "01",
    "031": "26",
    "050": "11",
    "051": "11",
    "053": "01",
    "055": "00",
    "069": "17",
    "073": "26",
    "074": "74",
    "077": "01",
    "080": "19",
    "090": "09",
    "091": "02",
    "092": "30",
    "094": "15",
    "096": "11",
    "097": "14",
    "098": "14",
    "099": "31",
    "100": "00",
    "101": "14",
    "111": "23",
    "112": "07",
    "13": "21",
    "15": "14",
    "17": "18",
    "20": "01",
    "200": "21",
    "201": "01",
    "202": "21",
    "203": "01",
    "204": "00",
    "300": "00",
    "333": "26",
    "334": "26",
    "335": "26",
    "336": "26",
    "337": "26",
    "51": "21",
    "53": "01",
    "65": "65",
    "68": "26",
    "69": "26",
    "700": "01",
    "701": "14",
    "702": "14",
    "703": "14",
    "704": "01",
    "705": "88",
    "706": "74",
    "777": "11",
    "81": "00",
    "82": "21",
    "85": "07",
    "86": "00",
    "87": "26",
    "88": "14",
    "888": "01",
    "889": "14",
    "890": "74",
    "98": "14",
    "987": "11",
    "988": "00",
    "99": "65",
    "991": "14",
    "992": "00",
    "999": "16"
}
