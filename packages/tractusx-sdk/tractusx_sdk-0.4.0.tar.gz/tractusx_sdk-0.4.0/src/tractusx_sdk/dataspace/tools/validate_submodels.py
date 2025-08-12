#################################################################################
# Eclipse Tractus-X - Software Development KIT
#
# Copyright (c) 2025 Contributors to the Eclipse Foundation
#
# See the NOTICE file(s) distributed with this work for additional
# information regarding copyright ownership.
#
# This program and the accompanying materials are made available under the
# terms of the Apache License, Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the
# License for the specific language govern in permissions and limitations
# under the License.
#
# SPDX-License-Identifier: Apache-2.0
#################################################################################

from typing import Optional

from requests import HTTPError, get
import jsonschema


## Test Orchestrator of Eclipse Tractus-X SDK Services
## License: Apache License, Version 2.0
## Source: https://github.com/eclipse-tractusx/tractusx-sdk-services/blob/cfd73933ad7871891bee9f117b32643bc9abad40/test-orchestrator/test_orchestrator/utils.py#L176-L217

@staticmethod
def submodel_schema_finder(
        semantic_id,
        link_core: Optional[str] = 'https://raw.githubusercontent.com/eclipse-tractusx/sldt-semantic-models/main/'):
    """
    Function to facilitate the validation of the submodel output by retrieving the correct schema
    based on the semantic_id provided by the user
    """

    split_string = semantic_id.split(':')

    if len(split_string) < 4:
        raise HTTPError(f"422 Client Error: The semanticID provided does not follow the correct structure. subprotocolBody: {semantic_id}")

    loc_elements = split_string[3].split('#')
    schema_link = link_core + split_string[2] + '/' + loc_elements[0] + '/gen/' + loc_elements[1] + '-schema.json'

    # Now we can use the link to pull in the correct schema.
    response = get(schema_link)

    if response.status_code != 200:
        raise HTTPError(f"422 Client Error: Failed to obtain the required schema. schema link: {schema_link}")

    try:
        schema = response.json()
    except Exception:
        raise HTTPError(f"422 Client Error: The schema obtained is not a valid json. schema link: {schema_link}")

    return {'status': 'ok',
            'message': 'Submodel validation schema retrieved successfully',
            'schema': schema}

@staticmethod
def json_validator(schema, json_to_validate, validation_type = 'jsonschema'):
    """
    Validates a JSON object against a given schema.

    This function uses the specified validation type to check whether a JSON object
    conforms to a given schema. Currently, only 'jsonschema' validation is supported.
    Validation errors are recorded with details about the specific violations.

    :param schema: The JSON schema object to validate against.
    :param json_to_validate: The JSON object to be validated.
    :param validation_type: The type of validation to perform. Default is 'jsonschema'.
    :raises HTTPError: Raised if validation errors are found.
    :return: A dictionary indicating the status and message if validation passes successfully.
    """

    error_records = []

    if validation_type == 'jsonschema':
        validator = jsonschema.Draft7Validator(schema)

        for error in validator.iter_errors(json_to_validate):
            error_records.append({
                "path": ".".join(str(p) for p in error.path) if error.path else "root",
                "message": error.message,
                "validator": error.validator,
                "expected": error.schema.get("type", "N/A"),  
                "invalid_value": error.instance  
            })

        if error_records:
            raise HTTPError(f"422 Client Error: Validation error - {len(error_records)} validation errors found: {error_records}")

    return {"status": "ok",
            "message": "Congratulations, your JSON file passed the validation test"}
