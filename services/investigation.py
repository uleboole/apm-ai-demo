def run_investigation(incident: dict) -> list:
    """
    Simulates a technical investigation workflow.

    Later each item will be replaced by a real
    service call (Transaction API, Grafana, etc.).
    """

    return [
        {
            "running": "Checking Transaction API...",
            "completed": "✅ Transaction API — 2 failed transactions found"
        },
        {
            "running": "Checking Grafana...",
            "completed": "✅ Grafana — elevated error rate detected"
        },
        {
            "running": "Checking Provider Status...",
            "completed": "✅ Provider Status — PIX provider status: Degraded"
        },
        {
            "running": "Searching similar incidents...",
            "completed": "✅ Similar Incidents — 3 matching incidents found"
        }
    ]