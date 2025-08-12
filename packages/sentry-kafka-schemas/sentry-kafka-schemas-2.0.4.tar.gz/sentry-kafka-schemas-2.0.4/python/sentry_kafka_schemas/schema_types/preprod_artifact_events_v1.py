from typing import Required, TypedDict


class PreprodArtifactEvents(TypedDict, total=False):
    """
    preprod_artifact_events.

    Preprod artifact events
    """

    artifact_id: Required[str]
    """ Required property """

    project_id: Required[str]
    """ Required property """

    organization_id: Required[str]
    """ Required property """

