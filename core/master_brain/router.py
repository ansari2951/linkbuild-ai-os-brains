ROUTES = {
    "publisher_research": [
        "find publisher", "find website", "publisher research",
        "niche research", "websites"
    ],
    "publisher_outreach": [
        "publisher email", "contact publisher", "publisher outreach"
    ],
    "publisher_deals": [
        "negotiate", "publisher deal", "publisher price"
    ],
    "client_research": [
        "find client", "find lead", "client research",
        "prospect research"
    ],
    "client_outreach": [
        "client outreach", "cold email", "contact client"
    ],
    "email_intelligence": [
        "check replies", "email replies", "check inbox",
        "inbox analysis"
    ]
}


def route_task(command):
    command = command.lower().strip()

    matches = []

    for agent_id, keywords in ROUTES.items():
        for keyword in keywords:
            if keyword in command:
                matches.append((len(keyword), agent_id))

    if not matches:
        return None

    matches.sort(reverse=True)
    return matches[0][1]
