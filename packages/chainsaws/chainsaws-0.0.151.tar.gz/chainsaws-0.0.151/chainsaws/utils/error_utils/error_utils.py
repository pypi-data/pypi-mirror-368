"""Error handling utilities for external error monitoring and reporting."""

import pprint
import traceback
from typing import Any, Final
from datetime import datetime

# Constant for max payload length for error message
MAX_PAYLOAD_LENGTH: Final[int] = 1000


def make_error_description(event: dict[str, Any]) -> str:
    # 에러 발생시 설명을
    tb = traceback.format_exc()
    source_ip = event.get('requestContext', {}).get(
        'identity', {}).get('sourceIp', 'unknown')
    request_id = event.get('requestContext', {}).get('requestId', 'unknown')

    request_payload_str = pprint.pformat(event, indent=1)
    if len(request_payload_str) > MAX_PAYLOAD_LENGTH:
        request_payload_str = request_payload_str[:MAX_PAYLOAD_LENGTH]
        request_payload_str += '... \n*See more to query via AWS Cloudwatch, Copy & Paste bellow!*'
        request_payload_str += '```fields @timestamp, @message\n' +\
                               f' | filter requestContext.requestId = "{request_id}"\n' +\
            ' | sort @timestamp desc\n' +\
            ' | limit 20```\n'

    description = f'>*{datetime.now()}*\n' \
        f'>*source_ip*: {source_ip}\n' \
        f'>*request_id*: {request_id}\n\n' \
        f'>*Request(1000글자):*\n{request_payload_str}\n\n' \
        f'>*Error*:\n```{tb}```\n\n'

    return description


if __name__ == "__main__":
    pass
    # sample_event = {
    #     "requestContext": {
    #         "requestId": "test-request-id",
    #         "identity": {
    #             "sourceIp": "127.0.0.1",
    #             "userAgent": "Mozilla/5.0",
    #         },
    #     },
    #     "body": "test body",
    # }

    # error = AppError(
    #     code="S00005",
    #     message="Invalid S3 Query Command",
    #     details={"query": "SELECT * FROM invalid_table"},
    # )

    # print(make_error_description(sample_event, error))
