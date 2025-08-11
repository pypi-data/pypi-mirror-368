"""IoT Pre-Provisioning Hook event types for AWS Lambda."""


from typing import Dict, TypedDict


class IoTPreProvisioningHookEvent(TypedDict):
    """Event sent by AWS IoT Core before provisioning a device.

    Args:
        claimCertificateId (str): The ID of the claim certificate used in the provisioning request.
        certificateId (str): The ID of the certificate that will be created.
        certificatePem (str): The PEM-encoded certificate that will be created.
        templateArn (str): The ARN of the provisioning template being used.
        clientId (str): The client ID from the provisioning request.
        parameters (Dict[str, str]): Parameters passed in the provisioning request.

    Reference:
        https://docs.aws.amazon.com/iot/latest/developerguide/pre-provisioning-hook.html
    """
    claimCertificateId: str
    certificateId: str
    certificatePem: str
    templateArn: str
    clientId: str
    parameters: Dict[str, str]
