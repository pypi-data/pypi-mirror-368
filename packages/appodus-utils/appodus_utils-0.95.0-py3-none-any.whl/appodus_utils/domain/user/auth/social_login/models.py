import enum


class SocialAuthPlatform(str, enum.Enum):
    APPLE = "apple"
    FACEBOOK = "facebook"
    GOOGLE = "google"
