class CloudFrontException(Exception):
    pass


class CloudFrontCreateDistributionException(CloudFrontException):
    pass


class CloudFrontGetDistributionException(CloudFrontException):
    pass


class CloudFrontUpdateDistributionException(CloudFrontException):
    pass


class CloudFrontDeleteDistributionException(CloudFrontException):
    pass


class CloudFrontCreateInvalidationException(CloudFrontException):
    pass


class CloudFrontCreateOriginAccessControlException(CloudFrontException):
    pass


class CloudFrontDeleteOriginAccessControlException(CloudFrontException):
    pass
