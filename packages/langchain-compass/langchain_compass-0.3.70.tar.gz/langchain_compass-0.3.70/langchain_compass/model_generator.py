import warnings
from typing import Any

# # Read the OpenAPI JSON file
# with open('../openapi.json', 'r', encoding='utf-8') as f:
#     openapi_content = f.read()
from datamodel_code_generator import (
    DataModelType,
    InputFileType,
    OpenAPIScope,
    generate,
)
from datamodel_code_generator.model import PythonVersion


def models_from_openapi(openapi_content: str, path: Any) -> None:
    # tmp_file = tempfile.NamedTemporaryFile(delete=False)
    # path = Path(tmp_file.name)

    # Generate Python code (as a string)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        generate(
            input_=openapi_content,
            output=path,
            use_default_kwarg=True,
            apply_default_values_for_required_fields=True,
            additional_imports=["numpy"],
            output_model_type=DataModelType.PydanticV2BaseModel,
            input_file_type=InputFileType.OpenAPI,
            openapi_scopes=[OpenAPIScope.Schemas],
            target_python_version=PythonVersion.PY_311,  # Change to your Python version
        )
