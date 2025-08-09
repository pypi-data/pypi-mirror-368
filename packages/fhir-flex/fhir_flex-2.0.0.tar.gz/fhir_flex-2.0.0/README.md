# fhir_simple

A library to simplify FHIR Patient objects to basic JSON.

## Usage

```python
from fhir_simple import fhir_patient_to_simple_json

fhir_patient = { ... }  # your FHIR Patient dict
simple = fhir_patient_to_simple_json(fhir_patient)
print(simple)
```

## Output Example

```
{
  "fhirId": "...",
  "active": true,
  "firstName": "...",
  "lastName": "...",
  "gender": "...",
  "birthDate": "..."
}
```


