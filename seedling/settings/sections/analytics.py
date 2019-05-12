from environs import Env

env = Env()
env.read_env()

GOOGLE_ANALYTICS_PROPERTY_ID = env.str('GOOGLE_ANALYTICS_PROPERTY_ID', None)

# Protect the privacy of our users
ANALYTICAL_AUTO_IDENTIFY = False
