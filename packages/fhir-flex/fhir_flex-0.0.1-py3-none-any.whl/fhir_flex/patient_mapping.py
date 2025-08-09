def fhir_patient_to_simple_json(fhir_obj):
    """
    Extracts key patient info from a FHIR Patient resource dict and returns a simplified dict.
    Args:
        fhir_obj (dict): FHIR Patient resource as a dict.
    Returns:
        dict: Simplified patient info.
    """
    try:
        result = {
            "fhirId": fhir_obj.get("id"),
            "active": fhir_obj.get("active"),
            "firstName": None,
            "lastName": None,
            "gender": fhir_obj.get("gender"),
            "birthDate": fhir_obj.get("birthDate"),
        }
        # Extract first name and last name from the first name entry
        names = fhir_obj.get("name", [])
        if names and isinstance(names, list):
            first_name_entry = names[0]
            given = first_name_entry.get("given", [])
            if given and isinstance(given, list):
                result["firstName"] = given[0]
            result["lastName"] = first_name_entry.get("family")
        return result
    except Exception as e:
        raise ValueError(f"Invalid FHIR Patient object: {e}")


def fhir_patient_to_detailed_json(fhir_obj):
    """
    Maps a FHIR Patient resource dict to the detailed target output format as described by the user.
    Args:
        fhir_obj (dict): FHIR Patient resource as a dict.
    Returns:
        dict: Patient info in the target format.
    """
    # Helper functions
    def get_extension_value(ext_list, url, value_type):
        for ext in ext_list:
            if ext.get("url") == url:
                return ext.get(value_type)
        return None

    def get_extension_value_string(ext_list, url):
        for ext in ext_list:
            if ext.get("url") == url:
                return ext.get("valueString")
        return None

    def get_extension_value_code(ext_list, url):
        for ext in ext_list:
            if ext.get("url") == url:
                return ext.get("valueCode")
        return None

    def get_extension_value_reference(ext_list, url):
        for ext in ext_list:
            if ext.get("url") == url:
                return ext.get("valueReference")
        return None

    def get_nested_extension_value(ext_list, url, nested_url, value_type):
        for ext in ext_list:
            if ext.get("url") == url:
                for sub_ext in ext.get("extension", []):
                    if sub_ext.get("url") == nested_url:
                        return sub_ext.get(value_type)
        return None

    # Name fields
    names = fhir_obj.get("name", [])
    first_name = middle_name = last_name = None
    if names:
        name_entry = names[0]
        given = name_entry.get("given", [])
        if given:
            first_name = given[0]
            if len(given) > 1:
                middle_name = given[1]
        last_name = name_entry.get("family")

    # Address fields
    addresses = fhir_obj.get("address", [])
    address_line_1 = address_line_2 = city = state = country = zip_code = None
    if addresses:
        address = addresses[0]
        lines = address.get("line", [])
        if lines:
            address_line_1 = lines[0]
            if len(lines) > 1:
                address_line_2 = lines[1]
        city = address.get("city")
        state = address.get("state")
        country = address.get("country")
        zip_code = address.get("postalCode")

    # Telecom fields
    telecom = fhir_obj.get("telecom", [])
    phone = secondary_phone = home_phone = work_phone = ""
    email = ""
    for t in telecom:
        if t.get("system") == "phone":
            if t.get("use") == "home":
                home_phone = t.get("value", "")
            elif t.get("use") == "work":
                work_phone = t.get("value", "")
            elif t.get("use") == "mobile":
                secondary_phone = t.get("value", "")
            elif not phone:
                phone = t.get("value", "")
        elif t.get("system") == "email":
            email = t.get("value", "")

    # Gender
    gender = fhir_obj.get("gender")
    gender = gender.capitalize() if gender else None

    # Date of birth
    date_of_birth = fhir_obj.get("birthDate")

    # SSN (not present in FHIR, set as None)
    ssn = None

    # Language
    language = None
    if fhir_obj.get("communication"):
        comm = fhir_obj["communication"][0]
        lang = comm.get("language", {})
        language = lang.get("coding", [{}])[0].get("code") or lang.get("text")

    # Race and Ethnicity
    extensions = fhir_obj.get("extension", [])
    race = get_nested_extension_value(extensions, "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race", "text", "valueString")
    ethnicity = get_nested_extension_value(extensions, "http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity", "text", "valueString")

    # Marital status
    marital_status = fhir_obj.get("maritalStatus", {}).get("text")

    # Consent (not directly available, set as True if any telecom present)
    is_consent_to_message = bool(telecom)
    is_consent_to_call = bool(telecom)
    is_consent_to_email = bool(email)

    # MRN (use first identifier value)
    mrn = None
    identifiers = fhir_obj.get("identifier", [])
    if identifiers:
        mrn = identifiers[0].get("value")

    # Status
    status = "active" if fhir_obj.get("active") else "inactive"

    # Registration date (not present, set as None)
    registration_date = None

    # Output dict
    output = {
        "id": None,
        "address_line_1": address_line_1,
        "address_line_2": address_line_2,
        "country": country,
        "state": state,
        "city": city,
        "zip": zip_code,
        "first_name": first_name,
        "middle_name": middle_name,
        "last_name": last_name,
        "gender": gender,
        "date_of_birth": date_of_birth,
        "ssn": ssn,
        "phone": phone,
        "secondary_phone": secondary_phone,
        "home_phone": home_phone,
        "work_phone": work_phone,
        "phone_note": None,
        "pos": None,
        "risk_level": "",
        "monthly_goal_minutes": 20,
        "risk_score": None,
        "email": email,
        "language": language,
        "race": race,
        "ethnicity": ethnicity,
        "marital_status": marital_status,
        "is_consent_to_message": is_consent_to_message,
        "is_consent_to_call": is_consent_to_call,
        "is_consent_to_email": is_consent_to_email,
        "notes": "",
        "expected_outcomes": None,
        "is_ccm_eligible": False,
        "is_pcm_eligible": False,
        "is_bhi_eligible": False,
        "is_rpm_eligible": False,
        "is_tcm_eligible": False,
        "is_awv_eligible": False,
        "is_mdpcp_eligible": False,
        "is_heart_eligible": False,
        "is_apcm_eligible": False,
        "last_call_at": None,
        "last_call_status": None,
        "mrn": mrn,
        "ehr_id": None,
        "active_status": fhir_obj.get("active", True),
        "active_status_updated_at": None,
        "active_status_updated_note": None,
        "status": status,
        "status_updated_at": None,
        "updated_on": None,
        "updated_note": None,
        "invite_status": "not invited",
        "invited_at": None,
        "referring_provider": None,
        "registration_date": registration_date,
        "mbi": None,
        "attributed_prior_quarter": False,
        "cms_risk_score": None,
        "cms_risk_tier": None,
        "smmg_risk_tier": None,
        "adi_score": None,
        "adi_quintile": None,
        "risk_stratification_bool": False,
        "risk_stratification_date": None,
        "risk_stratification_freq": None,
        "mdpcp_careplan_bool": False,
        "mdpcp_careplan_date": None,
        "mdpcp_careplan_freq": None,
        "timezone": "US/Eastern",
        "is_deleted": False,
        "deleted_reason": None,
        "deleted_at": None,
        "recovered_reason": None,
        "recovered_at": None,
        "code": None,
        "auth_generated_at": None,
        "auth_updated_at": None,
        "preferred_communication_channel": "email",
        "is_ehr_imported": False,
        "ehr_name": None,
        "is_transferred": False,
        "transferred_at": None,
        "disable_call_recording": False,
        "blueprint_patient_id": None,
        "goals_minutes_for_program": {
            "ccm": 20,
            "rpm": 20,
            "bhi": 20,
            "awv": 20
        },
        "next_outreach_due_date": None,
        "next_psychiatric_scheduled_visit": None,
        "department_id": None,
        "vital_cards": None,
        "provider_group": 6,
        "user": None,
        "active_status_updated_by": None,
        "updated_by": None,
        "primary_care_manager": None,
        "secondary_care_manager": None,
        "primary_physician": None,
        "biller": None,
        "additional_careteam_member": None,
        "created_by": 7,
        "deleted_by": None,
        "recovered_by": None,
        "auth_generated_by": None,
        "auth_updated_by": None,
        "transferred_to": None,
        "transferred_from": None,
        "transferred_by": None,
        "old_patient": None,
        "new_patient": None,
        "flags": [],
        "devices": [],
        "care_managers": [],
        "cm_name": None,
        "ph_name": None,
        "scm_name": None
    }
    return output 