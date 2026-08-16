import time

import streamlit as st

from services.intake_ai import (
    analyse_message,
    generate_follow_up_questions,
    update_incident
)

from services.investigation import run_investigation
from services.summary import generate_summary

st.set_page_config(
    page_title="AI Incident Intake Assistant",
    page_icon="🤖",
    layout="wide"
)

st.title("AI Incident Intake Assistant")

DISPLAY_NAMES = {
    "merchant": "Merchant",
    "payment_method": "Payment Method",
    "incident_type": "Incident Type",
    "country": "Country",
    "incident_start_time": "Incident Start Time",
    "transaction_ids": "Transaction IDs",
    "error_message": "Error Message",
}

st.subheader("Merchant Message")

merchant_message = st.text_area(
    label="",
    value="""Hi,

Our Pix payments have stopped working since this morning.
Customers cannot complete purchases.

Regards,
ABC Store""",
    height=200,
    disabled=True,
    label_visibility="collapsed"
)

# ----------------------------------------------------
# Session state
# ----------------------------------------------------

for key in [
    "analysis_complete",
    "follow_up_generated",
    "incident_ready",
    "investigation_complete"
]:
    if key not in st.session_state:
        st.session_state[key] = False

if "summary_generated" not in st.session_state:
    st.session_state.summary_generated=False
if "ticket_created" not in st.session_state:
    st.session_state.ticket_created=False

# ----------------------------------------------------
# Analyze
# ----------------------------------------------------

if st.button("Analyze", type="primary"):
    st.session_state.analysis_complete = True

if st.session_state.analysis_complete:

    result = analyse_message(merchant_message)

    st.success("AI analysis completed.")

    st.subheader("Extracted Information")

    st.markdown(f"**Merchant:** {result['merchant']}")
    st.markdown(f"**Payment Method:** {result['payment_method']}")
    st.markdown(f"**Incident Type:** {result['incident_type']}")

    st.subheader("Missing Information")
    
    st.info(
        "The AI needs additional information before the incident can be created."
    )
    
    for field in result["missing_fields"]:
        st.markdown(f"- {DISPLAY_NAMES.get(field, field)}")
    
    with st.expander("View Structured JSON"):
        st.json(result)
    
    # ----------------------------------------------------

    if not st.session_state.follow_up_generated:

        if st.button("Generate Follow-up Questions"):
            st.session_state.follow_up_generated = True
            st.rerun()

    if st.session_state.follow_up_generated:

        follow_up = generate_follow_up_questions(result)

        st.subheader("AI Follow-up Message")

        st.info(follow_up)

        st.subheader("Merchant Reply")

        merchant_reply = st.text_area(
            label="",
            value="""Hi,

The issue started around 10:15 UTC.

Country: Brazil.

Affected transaction IDs:

TX123456
TX123457

Customers receive:

Gateway Timeout

Regards,
ABC Store""",
            height=220,
            disabled=True,
            label_visibility="collapsed"
        )

        # ----------------------------------------------------

        if not st.session_state.incident_ready:

            if st.button("Process Reply", type="primary"):
                st.session_state.incident_ready = True
                st.rerun()

        if st.session_state.incident_ready:

            with st.spinner("Analyzing merchant reply..."):
                incident = update_incident(
                    result,
                    merchant_reply
                )

            st.success("Merchant reply analyzed.")

            st.subheader("Updated Incident Information")

            st.markdown(f"**Merchant:** {incident['merchant']}")
            st.markdown(f"**Payment Method:** {incident['payment_method']}")
            st.markdown(f"**Incident Type:** {incident['incident_type']}")
            st.markdown(f"**Country:** {incident['country']}")
            st.markdown(f"**Incident Start Time:** {incident['incident_start_time']}")

            transaction_ids = incident.get("transaction_ids", [])

            if transaction_ids:
                st.markdown(
                    f"**Transaction IDs:** {', '.join(transaction_ids)}"
                )
            else:
                st.markdown("**Transaction IDs:**")

            st.markdown(f"**Error Message:** {incident['error_message']}")

            if incident["missing_fields"]:
                st.subheader("Missing Information")

                for field in incident["missing_fields"]:
                    st.markdown(f"- {DISPLAY_NAMES.get(field, field)}")
            else:
                st.success("✅ All required information has been collected.")

            with st.expander(
                    "View Updated JSON",
                    expanded=True
            ):
                display_incident = incident.copy()
                display_incident.pop("missing_fields", None)

                st.json(display_incident)

            # ----------------------------------------------------
            # Investigation
            # ----------------------------------------------------

            if not st.session_state.investigation_complete:

                if st.button("Run Investigation", type="primary"):

                    st.subheader("Investigation Progress")

                    current_step = st.empty()

                    for step in run_investigation(incident):

                        # Показываем текущую проверку
                        current_step.info(step["running"])

                        time.sleep(1)

                        # Убираем строку "Checking..."
                        current_step.empty()

                        # Добавляем завершённую проверку.
                        # Эти строки НЕ исчезнут.
                        st.success(step["completed"])

                        time.sleep(0.3)

                    st.session_state.investigation_complete = True

            if st.session_state.investigation_complete:

                st.success("Investigation completed.")

                st.divider()

                if not st.session_state.summary_generated:
                    if st.button("Generate Summary"):
                        st.session_state.summary_generated=True
                        st.rerun()

                if st.session_state.summary_generated:
                    summary=generate_summary()

                    st.subheader("Investigation Summary")
                    for item in summary["summary"]:
                        st.markdown(f"- {item}")

                    st.subheader("Recommendation")
                    st.info(summary["recommendation"])

                    if not st.session_state.ticket_created:
                        if st.button("Create Incident Ticket"):
                            st.session_state.ticket_created=True
                            st.rerun()

                    if st.session_state.ticket_created:
                        st.success("Incident ticket created successfully.")