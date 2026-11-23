
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
        "status": "registered"
    },
    "publisher_deals": {
        "name": "Publisher Deal Brain",
        "department": "publisher",
        "capabilities": [
            "negotiation",
            "publisher deals"
        ],
        "status": "registered"
    },
    "client_research": {
        "name": "Client Research Brain",
        "department": "client",
        "capabilities": [
            "find clients",
            "lead research"
        ],
        "status": "registered"
    },
    "client_outreach": {
        "name": "Client Outreach Brain",
        "department": "client",
        "capabilities": [
            "client emails",
            "cold outreach"
        ],
        "status": "registered"
    },
    "email_intelligence": {
        "name": "Email Intelligence Brain",
        "department": "email",
        "capabilities": [
            "email replies",
            "inbox analysis"
        ],
        "status": "registered"
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
