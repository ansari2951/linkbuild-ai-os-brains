
AGENTS = {
    "publisher_research": {
        "name": "Publisher Research Brain",
        "department": "publisher",
        "capabilities": [
            "find publishers",
            "website research",
            "niche research"
        ],
        "status": "connected"
    },
    "publisher_outreach": {
        "name": "Publisher Outreach Brain",
        "department": "publisher",
        "capabilities": [
            "publisher emails",
            "publisher outreach"
        ],
        "status": "connected"
    },
    "publisher_deals": {
        "name": "Publisher Deal Brain",
        "department": "publisher",
        "capabilities": [
            "negotiation",
            "publisher deals"
        ],
        "status": "connected"
    },
    "client_research": {
        "name": "Client Research Brain",
        "department": "client",
        "capabilities": [
            "find clients",
            "lead research"
        ],
        "status": "connected"
    },
    "client_outreach": {
        "name": "Client Outreach Brain",
        "department": "client",
        "capabilities": [
            "client emails",
            "cold outreach"
        ],
        "status": "connected"
    },
    "email_intelligence": {
        "name": "Email Intelligence Brain",
        "department": "email",
        "capabilities": [
            "email replies",
            "inbox analysis"
        ],
        "status": "connected"
    }
}


def list_agents():
    return AGENTS


def get_agent(agent_id):
    return AGENTS.get(agent_id)


def get_agents_by_department(department):
    return {
        agent_id: agent
        for agent_id, agent in AGENTS.items()
        if agent["department"] == department
    }


def get_agent_count():
    return len(AGENTS)
