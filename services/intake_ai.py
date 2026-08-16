import json

from services.openai_client import client


def analyse_message(message):

    prompt = f"""
Analyze the following merchant incident report.

Extract the following information if available:

- merchant
- payment_method
- incident_type
- country
- incident_start_time
- transaction_ids
- error_message

If a field cannot be determined from the merchant message, leave it empty and add its name to the "missing_fields" array.

Use exactly the same field names in "missing_fields".

Return ONLY a valid JSON object in the following format:

{{
  "merchant": "",
  "payment_method": "",
  "incident_type": "",
  "country": "",
  "incident_start_time": "",
  "transaction_ids": [],
  "error_message": "",
  "missing_fields": []
}}

Merchant message:

{message}
"""

    response = client.responses.create(
        model="gpt-5.6",
        input=prompt
    )

    return json.loads(response.output_text)


def generate_follow_up_questions(result):

    prompt = f"""
A merchant reported a payment issue.

Based on the following incident information, write a short and professional email asking only for the missing information.

Incident information:

{json.dumps(result, indent=2)}

Return only the email.
"""

    response = client.responses.create(
        model="gpt-5.6",
        input=prompt
    )

    return response.output_text


def update_incident(existing_incident, merchant_reply):

    prompt = f"""
You are updating an existing payment incident.

You are given:

1. Current incident information in JSON format.
2. A follow-up reply from the merchant.

Update the incident using the merchant reply.

Rules:

- Keep all existing values unless new information is provided.
- Fill previously empty fields whenever possible.
- Remove completed fields from "missing_fields".
- Return ONLY the updated JSON.

Current incident:

{json.dumps(existing_incident, indent=2)}

Merchant reply:

{merchant_reply}
"""

    response = client.responses.create(
        model="gpt-5.6",
        input=prompt
    )

    return json.loads(response.output_text)