from enum import Enum


class BuildingBlockType(Enum):
    AGGREGATE_ROOT = "Aggregate Root"
    ENTITY = "Entity"
    VALUE_OBJECT = "Value Object"
    DOMAIN_SERVICE = "Domain Service"
    REPOSITORY = "Repository"
    DOMAIN_EVENT = "Domain Event"
    PORT = "Port"

    ACTION = "Action"
    COMMAND = "Command"
    DOMAIN_EVENT_LISTENER = "Domain Event Listener"
    INTEGRATION_EVENT_LISTENER = "Integration Event Listener"

    INFRASTRUCTURE_SERVICE = "Infrastructure Service"
    ADAPTER = "Adapter"
